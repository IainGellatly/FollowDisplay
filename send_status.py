# Send Status
#
# Version 1.0
# 08-Apr-2026
#
# Send hardware status message to server via web socket.

import asyncio
import psutil
import json
import time
from logging_mgr import log
from config import *

async def send_status(ws, dm, dc_event):
    log.info('starting send_status')
    stat_int = OPS.SEND_STATUS_INTERVAL
    platform = await dm.get('platform')
    while not dc_event.is_set():
        log.info('sending status')
        try:
            cpu_temp = round(
                psutil.sensors_temperatures(fahrenheit=True)
                ['cpu_thermal'][0].current, 2) \
                if platform == 'posix' else 0
            mem = psutil.virtual_memory()
            net = psutil.net_io_counters()
            stats_msg = {
                'msg_type': 'send_status',
                'cpu_temp': cpu_temp,
                'display_count': await dm.get('display_count'),
                'up_time': time.time() - psutil.boot_time(),
                'mem_percent': mem.percent,
                'mem_available': mem.available,
                'net_bytes_sent': net.bytes_sent,
                'net_bytes_recv': net.bytes_recv,
                'net_error_in': net.errin,
                'net_error_out': net.errout,
                'net_drop_in': net.dropin,
                'net_drop_out': net.dropout,
            }
            await ws.send(json.dumps(stats_msg))

        except Exception as err:
            log.error(f'send_status error: {err}')
            dc_event.set()
            break

        try:
            await asyncio.wait_for(dc_event.wait(), timeout=stat_int)

        except asyncio.TimeoutError:
            pass

# end of file