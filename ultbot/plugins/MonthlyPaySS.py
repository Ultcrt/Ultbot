from datetime import datetime
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError

@nonebot.scheduler.scheduled_job('cron',day=4,hour=12)
async def _():
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    try:
        await bot.send_group_msg(group_id=912732378,
                                 message='[CQ:at,qq=all]\n'+
                                         '[CQ:image,file=4.81-yuan.jpg]\n'+
                                         f'收款日期:{now.year}.{now.month}.{now.day}')
    except CQHttpError:
        pass    
