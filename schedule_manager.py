# Schedule Manager
#
# Version 1.0
# 08-Apr-2026
#
# Update display periodically according to schedule.

import asyncio
import subprocess
import json
from datetime import datetime
from logging_mgr import log
from config import *

async def schedule_manager(dm, status):
    log.info('starting schedule_manager')
    sch_int = OPS.UPDATE_SCHEDULE_INTERVAL
    platform = BASE.PLATFORM
    exist_sch = await dm.get('run_schedule')
    if not exist_sch:
        await dm.set('run_schedule', OPS.DEFAULT_SCHEDULE)

    op_mode = 'active'
    await dm.set('operation_mode', op_mode)
    while True:
        try:
            rs = await dm.get('run_schedule')
            sch = json.loads(rs)
            curr_time = datetime.now()
            week_day = curr_time.weekday()
            curr_hr = curr_time.hour
            is_oper = curr_hr in range(sch[week_day][0], sch[week_day][1])
            new_mode = 'active' if is_oper else 'sleeping'
            if new_mode != op_mode:
                log.info(f'new schedule mode={new_mode}')
                await dm.set('operation_mode', new_mode)
                if platform == 'posix':
                    if new_mode == 'sleeping':
                        disp_cmd = './set_bright.sh 0'

                    else:
                        bright = int(await dm.get('brightness'))
                        disp_cmd = f'./set_bright.sh {bright}'

                    subprocess.call(disp_cmd, shell=True)

                op_mode = new_mode

        except Exception as err:
            log.error(f'schedule_manager error: {err}')

        await asyncio.sleep(sch_int)

# end of file