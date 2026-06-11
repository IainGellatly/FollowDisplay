# Receive Response
#
# Version 1.0
# 08-Apr-2026
#
# Receive and process messages from server via web socket.

import asyncio
import json
from logging_mgr import log
from config import *

async def receive_response(ws, dm, status, dc_event):
    log.info('starting receive_response')
    try:
        async for msg in ws:
            try:
                log.info(f'received msg: {msg}')
                await status.put({'event': 'received_ok'})
                msg = json.loads(msg)
                match msg.get('msg_type'):
                    case 'confirm_heartbeat':
                        log.info('heartbeat confirmed')
                        await status.put({'event': 'heartbeat_ok'})

                    case 'status_received':
                        log.info('status received')

                    case 'config_response':
                        log.info('config received')
                        schedule = json.dumps(msg.get('run_schedule')).strip('"')
                        await dm.set('run_schedule', schedule)

                    case 'display_update':
                        log.info('display count received')
                        display_count = msg.get('display_count')
                        await dm.set('display_count', display_count)
                        await status.put({'event': 'count_received'})

                    case _:
                        log.error(f'receive_response unknown msg: {msg}')
                        await status.put({'event': 'comm_error'})

            except Exception as err:
                log.error(f'receive_response error: {err} msg: {msg}')
                await status.put({'event': 'comm_error'})

    except Exception as err:
        log.error(f'receive_response connection lost: {err}')
        dc_event.set()

    dc_event.set()

# end of file