# Communications Manager
#
# Version 1.0
# 08-Apr-2026
#
# Manage web socket client communications with server.

import asyncio, websockets, time
from jose import jwt
from send_heartbeat import send_heartbeat
from send_status import send_status
from request_config import request_config
from receive_response import receive_response
from logging_mgr import log
from config import *

class WebSocketClient:

    def __init__(self, dm, status):
        log.info('initializing web socket client')
        self.dm = dm
        self.status = status

    async def token(self):
        log.info('creating display token')
        jw_token_data = {
            "display_id": BASE.DISPLAY_ID,
            "page_id": BASE.PAGE_ID,
            "exp": int(time.time()) + COMM.TOKEN_LIFETIME_SEC
        }
        jw_token = jwt.encode(
            jw_token_data, BASE.JWT_SECRET, algorithm="HS256")
        return jw_token

    async def run(self):
        log.info('running web socket client')
        retry_int = COMM.CONNECT_RETRY_INTERVAL
        ws_host = COMM.WS_HOST
        token = await self.token()
        ws_url = f'wss://{ws_host}/ws?token={token}'
        while True:
            if await self.dm.get('wifi_connected') == 'True':
                try:
                    await self.status.put({'event': 'ws_connecting'})
                    async with websockets.connect(
                            ws_url,
                            ping_interval=COMM.PING_INTERVAL_SEC,
                            ping_timeout=COMM.PING_TIMEOUT_SEC,
                            close_timeout=COMM.CLOSE_TIMEOUT_SEC
                    ) as ws:
                        await self.status.put({'event': 'ws_connected'})
                        disconn_event = asyncio.Event()
                        tasks = [
                            asyncio.create_task(
                                send_heartbeat(
                                    ws, self.dm, self.status, disconn_event
                                )
                            ),
                            asyncio.create_task(
                                send_status(
                                    ws, self.dm, disconn_event
                                )
                            ),
                            asyncio.create_task(
                                request_config(
                                    ws, self.dm, disconn_event
                                )
                            ),
                            asyncio.create_task(
                                receive_response(
                                    ws, self.dm, self.status, disconn_event
                                )
                            )
                        ]
                        _, pending = await asyncio.wait(
                            tasks,
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        disconn_event.set()
                        for task in pending:
                            task.cancel()

                        await asyncio.gather(
                            *pending,
                            return_exceptions=True
                        )

                except Exception as err:
                    log.error(f'websocket client error: {err}')
                    await self.status.put({'event': 'ws_disconnected'})

            await asyncio.sleep(retry_int)
            log.info('websocket client connect retry')

# end of file