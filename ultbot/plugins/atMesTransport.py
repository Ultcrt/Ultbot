import nonebot
from nonebot.typing import Context_T
from aiocqhttp.exceptions import Error as CQHttpError
import re

bot = nonebot.get_bot()


@bot.on_message('group')
async def _(ctx: Context_T):
    if '[CQ:at,qq=326090231]' in ctx['raw_message']:
        try:
            await bot.send_private_msg(user_id=326090231,
                                       message='From'+ctx['user_id']
                                               +':\n'+ctx['raw_message'])

        except CQHttpError:
            pass
