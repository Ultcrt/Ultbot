from datetime import datetime
import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
from .crawler import crawler


@nonebot.scheduler.scheduled_job('cron', day_of_week='tue', hour=15)
async def _():
    crawler()

