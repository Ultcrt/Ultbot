import nonebot
from nonebot.typing import Context_T
from aiocqhttp.exceptions import Error as CQHttpError


bot = nonebot.get_bot()


@bot.on_message('group')
async def at_mes_transport(ctx: Context_T):
    if '[CQ:at,qq=326090231]' in ctx['raw_message']:
        try:
            await bot.send_private_msg(user_id=326090231,
                                       message='From '+str(ctx['user_id'])
                                       + ':\n\n' + ctx['raw_message'])

        except CQHttpError:
            pass
