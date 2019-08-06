import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from .htmlProcess import crawler
from .privateConfig import weibo_cookie


@nonebot.scheduler.scheduled_job('cron', day_of_week='tue', hour=15)
async def _():
    url = 'https://weibo.cn/u/6314659177'
    crawler(url, weibo_cookie, 'tmp_1.html')

