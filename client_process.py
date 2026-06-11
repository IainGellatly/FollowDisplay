# Client Process
#
# Version 1.0
# 08-Apr-2026
#
# Client display processing to manage web socket communications, wifi
# connection and status led.

import asyncio
import redis.asyncio as redis
from config import *
from logging_mgr import log
from comm_manager import WebSocketClient
from wifi_manager import wifi_manager
from status_led import status_led
from schedule_manager import schedule_manager

status_queue = asyncio.Queue()
data_mgr = redis.Redis(
    host=DB.REDIS_HOST,
    port=DB.REDIS_PORT,
    db=DB.REDIS_DB,
    decode_responses=True)

async def main():
    log.info(f'')
    log.info(f'**** initializing client process ****')
    log.info(f'VERSION = {BASE.VERSION}')
    log.info(f'DISPLAY_ID = {BASE.DISPLAY_ID}')
    log.info(f'PAGE_ID = {BASE.PAGE_ID}')
    log.info(f'PLATFORM = {BASE.PLATFORM}')
    log.info(f'WS_HOST = {COMM.WS_HOST}')
    log.info(f'WS_PORT = {COMM.WS_PORT}')
    log.info(f'')
    log.info('client_process startup')
    ws_client = WebSocketClient(data_mgr, status_queue)
    await asyncio.gather(
        wifi_manager(data_mgr, status_queue),
        status_led(data_mgr, status_queue),
        schedule_manager(data_mgr, status_queue),
        ws_client.run()
    )

if __name__ == "__main__":
    asyncio.run(main())

# end of file