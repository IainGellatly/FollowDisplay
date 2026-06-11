# Request Configuration
#
# Version 1.0
# 08-Apr-2026
#
# Request display configuration from server.

import asyncio
import json
from logging_mgr import log
from config import *

async def request_config(ws, dm, dc_event):
    log.info('starting request_config')
    config_int = OPS.REQUEST_CONFIG_INTERVAL
    while not dc_event.is_set():
        log.info('requesting config')
        try:
            await ws.send(json.dumps({'msg_type': 'request_config'}))

        except Exception as err:
            log.error(f'request_config error: {err}')
            dc_event.set()
            break

        try:
            await asyncio.wait_for(dc_event.wait(), timeout=config_int)

        except asyncio.TimeoutError:
            pass

# end of file