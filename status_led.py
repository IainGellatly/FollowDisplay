# Status LED
#
# Version 1.0
# 08-Apr-2026
#
# Tri-color LED shows status of display Wi-Fi connection, server connection
# and system error alert.

import asyncio
from logging_mgr import log
from config import *

async def status_led(dm, status):
    platform = BASE.PLATFORM
    if platform == 'posix':
        log.info('starting status_led with leds')
        import RPi.GPIO as GPIO
        event_code_color = {
            'heartbeat_error': (1, 0, 0),
            'wifi_error': (1, 0, 0),
            'comm_error': (1, 0, 0),
            'wifi_disconnected': (1, 1, 0),
            'wifi_connected': (0, 1, 0),
            'ws_disconnected': (0, 1, 1),
            'ws_connecting': (0, 0, 1),
            'ws_connected': (1, 0, 1),
            'count_received': (1, 1, 1),
            'heartbeat_ok': (1, 1, 1),
            'received_ok': (1, 1, 1)
        }
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HW.STATUS_LED_RED_PIN, GPIO.OUT)
        GPIO.setup(HW.STATUS_LED_GREEN_PIN, GPIO.OUT)
        GPIO.setup(HW.STATUS_LED_BLUE_PIN, GPIO.OUT)
        GPIO.output(HW.STATUS_LED_RED_PIN, 1)
        GPIO.output(HW.STATUS_LED_GREEN_PIN, 0)
        GPIO.output(HW.STATUS_LED_BLUE_PIN, 0)

    else:
        log.info('starting status_led logging only')

    while True:
        try:
            event_msg = await status.get()
            event_code = event_msg.get('event')
            log.info(f'status_led event: {event_code}')
            if platform == 'posix':
                event_color = event_code_color.get(event_code)
                GPIO.output(HW.STATUS_LED_RED_PIN, event_color[0])
                GPIO.output(HW.STATUS_LED_GREEN_PIN, event_color[1])
                GPIO.output(HW.STATUS_LED_BLUE_PIN, event_color[2])

        except Exception as err:
            log.error(f'status_led error: {err}')

# end of file
