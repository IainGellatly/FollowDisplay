# Wi-Fi Manager
#
# Version 1.0
# 08-Apr-2026
#
# Monitor status of Wi-Fi connection and report changes.

import asyncio
import psutil
from logging_mgr import log
from config import *

async def wifi_manager(dm, status):
    log.info('starting wifi_manager')
    platform = BASE.PLATFORM
    nic = 'wlan0' if platform == 'posix' else 'Wi-Fi'
    wifi_int = COMM.WIFI_CHECK_INTERVAL
    connected = False
    await dm.set('wifi_connected', 'False')
    await status.put({'event': 'wifi_disconnected'})
    while True:
        try:
            curr_conn = psutil.net_if_stats()[nic].isup
            if curr_conn != connected:
                connected = curr_conn
                wifi_val = 'True' if connected else 'False'
                event_val = ('wifi_connected' if connected
                             else 'wifi_disconnected')
                await dm.set('wifi_connected', wifi_val)
                await status.put({'event': event_val})
                log.info(f'wifi connected: {wifi_val}')

        except Exception as err:
            log.error(f'wifi_manager error: {err}')
            await status.put({'event': 'wifi_error'})

        await asyncio.sleep(wifi_int)

# end of file
