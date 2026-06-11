# Send Heartbeat
#
# Version 1.0
# 08-Apr-2026
#
# Send heartbeat message to server via web socket.

import asyncio
import json
from logging_mgr import log
from config import *

async def send_heartbeat(ws, dm, status, dc_event):
    log.info('starting send_heartbeat')
    heartbeat_int = OPS.SEND_HEARTBEAT_INTERVAL
    while not dc_event.is_set():
        log.info('sending heartbeat')
        try:
            await ws.send(json.dumps({'msg_type': 'send_heartbeat'}))

        except Exception as err:
            log.error(f'send_heartbeat error: {err}')
            await status.put({'event': 'heartbeat_error'})
            dc_event.set()
            break

        try:
            await asyncio.wait_for(dc_event.wait(), timeout=heartbeat_int)

        except asyncio.TimeoutError:
            pass

# end of file