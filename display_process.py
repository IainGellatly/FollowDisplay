import pygame
import sys
import queue
import threading
import redis
import time
import subprocess
from config import *
from logging_mgr import log

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 480
SCREEN_TITLE = "Odometer Wheel Test"
DIGIT_HEIGHT = 480
NUM_DIGITS = 5
DIGIT_SPACING = 410
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_CHANNEL = "display_count"

# --- SOUND FILES ---
WHEEL_SOUND_FILE = "running_gear.ogg"
BELL_SOUND_FILE = "double_bell.WAV"
VOLUME_SOUND_FILE = 'volume_bell.WAV'

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.FULLSCREEN)
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()
FONT = pygame.font.Font("copperplate_gothic_bold140_75.ttf", 420)
DIGIT_SURFACES = {}

for digit in "0123456789":
    DIGIT_SURFACES[digit] = FONT.render(
        digit,
        True,
        (255, 255, 255)
    )

# --- LOAD SOUNDS ---
wheel_sound = pygame.mixer.Sound(WHEEL_SOUND_FILE)
bell_sound = pygame.mixer.Sound(BELL_SOUND_FILE)
volume_sound = pygame.mixer.Sound(VOLUME_SOUND_FILE)
pygame.mixer.set_num_channels(8)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


# ------------------ WHEEL ------------------ #
class WheelColumn:

    def __init__(self, x):
        self.x = x
        self.current_offset = 0.0
        self.start_offset = 0.0
        self.target_offset = 0.0
        self.timer = 0.0
        self.duration = 1.0
        self.delay = 0.0
        self.state = "idle"

    def is_animating(self):
        return self.state in ("waiting", "rolling")

    def ease_out_quad(self, t):
        return 1 - (1 - t) * (1 - t)

    def start_roll(self, target_digit, delay, duration):
        self.start_offset = self.current_offset
        current_digit = (
            int(self.current_offset / DIGIT_HEIGHT)
            % 10
        )
        delta_digits = (
            target_digit - current_digit
        ) % 10
        total_digits = delta_digits + 10
        self.target_offset = (
            self.start_offset +
            total_digits * DIGIT_HEIGHT
        )
        self.timer = 0
        self.duration = duration
        self.delay = delay
        self.state = "waiting"

    def snap_to_digit(self, target_digit):
        self.current_offset = (
            target_digit * DIGIT_HEIGHT
        )
        self.state = "idle"

    def update(self, delta_time):
        if self.state == "waiting":
            self.timer += delta_time
            if self.timer >= self.delay:
                self.timer = 0
                self.state = "rolling"

        elif self.state == "rolling":
            self.timer += delta_time
            t = min(self.timer / self.duration, 1.0)
            eased = self.ease_out_quad(t)
            self.current_offset = (
                self.start_offset +
                (self.target_offset - self.start_offset) * eased
            )
            if t >= 1.0:
                self.current_offset = self.target_offset
                self.state = "idle"

    def draw(self, screen):
        center_y = SCREEN_HEIGHT // 2
        wheel_pos = self.current_offset /DIGIT_HEIGHT
        base_index = int(wheel_pos)
        frac = wheel_pos - base_index
        for offset in range(-1, 3):
            digit_num = (base_index + offset) % 10
            digit = str(digit_num)
            y = center_y + (offset - frac) * DIGIT_HEIGHT
            surface = DIGIT_SURFACES[digit]
            rect = surface.get_rect(center=(self.x, y))
            screen.blit(surface, rect)


# ---------------- DISPLAY ---------------- #
class OdometerDisplay:
    def __init__(self):
        self.columns = []
        start_x = SCREEN_WIDTH // 2 - ((NUM_DIGITS - 1) * DIGIT_SPACING) // 2
        for i in range(NUM_DIGITS):
            x = start_x + i * DIGIT_SPACING
            self.columns.append(WheelColumn(x))

    def is_animating(self):
        return any(col.is_animating() for col in self.columns)

    def set_value(self, value, animate=True):
        digits = f"{value:05d}"

        for i, col in enumerate(self.columns):
            target_digit = int(digits[i])
            if animate:
                delay = i * 0.18
                duration = 5 + i * 0.8
                col.start_roll(target_digit, delay, duration)

            else:
                col.snap_to_digit(target_digit)

    def update(self, delta_time):
        for col in self.columns:
            col.update(delta_time)

    def draw(self, screen):
        for col in self.columns:
            col.draw(screen)


# ----------- CONTROL KNOBS ------------- #
def control_knobs(volume_queue):

    def sample_knob(knob, num_samp):
        total = 0
        num_samp = 1 if num_samp < 1 else num_samp
        for samp in range(num_samp):
            total += knob.value
        avg = total / num_samp

        return avg

    bright_set = -1.0
    volume_set = -1.0
    samples = OPS.ADC_NUM_SAMPLES
    min_step = OPS.ADC_MIN_STEP
    check_int = OPS.ADC_CHECK_INTERVAL
    platform = BASE.PLATFORM
    if platform == 'posix':
        log.info('starting control_knobs with knobs')
        from gpiozero import MCP3002
        bright_knob = MCP3002(
            channel=OPS.ADC_BRIGHT_CHANNEL,
            clock_pin=HW.ADC_CLOCK_PIN,
            mosi_pin=HW.ADC_MOSI_PIN,
            miso_pin=HW.ADC_MISO_PIN,
            select_pin=HW.ADC_SELECT_PIN)
        volume_knob = MCP3002(
            channel=OPS.ADC_VOLUME_CHANNEL,
            clock_pin=HW.ADC_CLOCK_PIN,
            mosi_pin=HW.ADC_MOSI_PIN,
            miso_pin=HW.ADC_MISO_PIN,
            select_pin=HW.ADC_SELECT_PIN)

    else:
        log.info('starting control_knobs fixed settings')

    while True:
        try:
            if platform == 'posix':
                new_bright_set = sample_knob(bright_knob, samples)
                new_volume_set = sample_knob(volume_knob, samples)

            else:
                new_bright_set = 1.00
                new_volume_set = 0.50

            if abs(new_volume_set - volume_set) >= min_step:
                volume_set = new_volume_set
                volume_queue.put(volume_set)

            if abs(new_bright_set - bright_set) >= min_step:
                bright_set = new_bright_set
                bright_level = int(bright_set * bright_set * 255)
                redis_client.set('brightness', bright_level)
                bright_cmd = f'./set_bright.sh {bright_level}'
                subprocess.call(bright_cmd, shell=True)

        except Exception as err:
            log.error(f'control_knob error: {err}')

        time.sleep(check_int)


# ---------------- MAIN ---------------- #
def main():
    odometer = OdometerDisplay()
    value = 12345
    odometer.set_value(value, animate=False)
    volume_queue = queue.Queue()

    # restore threads
    threading.Thread(target=control_knobs, args=(volume_queue,), daemon=True).start()

    # --- SOUND STATE ---
    volume = 1.0
    bell_pending = False
    volume_bell_pending = False
    wheel_playing = False
    post_stop_timer = 0
    ACTIVE_FPS = 60
    IDLE_FPS = 2
    running = True
    dirty = True
    while running:
        # --- Determine state BEFORE ticking ---
        animating = odometer.is_animating()
        if animating:
            target_fps = ACTIVE_FPS
        else:
            target_fps = IDLE_FPS

        delta_time = clock.tick(target_fps) / 1000.0
        # --- EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- VOLUME CONTROL ---
        try:
            while True:
                volume = volume_queue.get_nowait()
                wheel_sound.set_volume(volume)
                bell_sound.set_volume(volume)
                volume_bell_pending = True

        except queue.Empty:
            pass

        if volume_bell_pending and not animating:

            if not bell_sound.get_num_channels():
                bell_sound.play()
                volume_bell_pending = False

        # --- SOUND LOGIC ---
        if animating and not wheel_playing:
            wheel_sound.play(loops=-1)
            wheel_playing = True

        if not animating and wheel_playing:
            wheel_sound.stop()
            wheel_playing = False
            post_stop_timer = 0
            bell_pending = True

        if bell_pending:
            post_stop_timer += delta_time
            if post_stop_timer >= 0.5:
                bell_sound.play()
                bell_pending = False

        # --- UPDATE LOGIC ---
        odometer.update(delta_time)
        if animating:
            dirty = True

        # --- DRAW ONLY IF NEEDED ---
        if dirty:
            screen.fill((0, 0, 0))
            odometer.draw(screen)
            pygame.display.flip()
            dirty = False

        # --- CHECK NEW COUNT ---
        if not animating:
            current_value = int(redis_client.get('display_count'))
            if current_value > value:
                odometer.set_value(current_value, True)
                dirty = True
                log.info(f'main: new display_count={value} higher')

            elif current_value < value:
                odometer.set_value(current_value, False)
                dirty = True
                log.info(f'main: new display_count={value} lower')

            value = current_value

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

# end of file