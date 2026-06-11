# Configuration
#
# 08-Apr-2026
#
# Configuration constants for in-store display.

class BASE:
    DISPLAY_ID = 10001
    PAGE_ID = 1001
    ROOT_DIR = '/home/admin/client'
    LOG_FILE = 'client_display.log'
    VERSION = '1.0.0'
    PLATFORM = 'posix'
    JWT_SECRET= 'super-secret-key'

class COMM:
    WS_HOST = 'followeb.site'
    WS_PORT = 8000
    PING_INTERVAL_SEC = 20
    PING_TIMEOUT_SEC = 60
    CLOSE_TIMEOUT_SEC = 10
    TOKEN_LIFETIME_SEC = 86400
    WIFI_CHECK_INTERVAL = 5
    CONNECT_RETRY_INTERVAL = 10

class DB:
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0

class OPS:
    SEND_HEARTBEAT_INTERVAL = 15
    SEND_STATUS_INTERVAL = 45
    REQUEST_CONFIG_INTERVAL = 60
    UPDATE_SCHEDULE_INTERVAL = 75
    STATUS_LED_INTERVAL = 1
    ADC_CHECK_INTERVAL = 0.05
    ADC_NUM_SAMPLES = 4
    ADC_MIN_STEP = 0.004
    ADC_BRIGHT_GAMMA = 2.2
    ADC_BRIGHT_CHANNEL = 0
    ADC_VOLUME_CHANNEL = 1
    STATUS_LED_BRIGHTNESS = 0.50
    BOOT_DISPLAY_COUNT = 12345
    BOOT_END_DELAY = 10
    MAX_PLAY_BELL = 3
    BELL_PAUSE = 1.2
    SOUND_FREQ = 48000
    BELL_SOUND_FILE = 'double_bell.wav'
    WHEEL_SOUND_FILE = 'running_wheel.wav'
    VOLUME_SOUND_FILE = 'bell_volume.wav'
    DEFAULT_SCHEDULE = '[[0,23],[0,23],[0,23],[0,23],[0,23],[0,23],[0,23]]'

class HW:
    STATUS_LED_RED_PIN = 16
    STATUS_LED_GREEN_PIN = 20
    STATUS_LED_BLUE_PIN = 21
    ADC_CLOCK_PIN = 11
    ADC_MOSI_PIN = 10
    ADC_MISO_PIN = 9
    ADC_SELECT_PIN = 22

class DISP:
    MAX_DISPLAY_COUNT = 99999
    NUM_DIGITS = 5
    FRAME_RATE = 60
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 480
    DIGIT_HEIGHT = 480
    DIGIT_SPACING = 410
    FULL_SCREEN = True

# end of file
