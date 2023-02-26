from nonebot import on_message
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.exception import NetworkError
from nonebot.rule import regex

from .private_config import supervisor_id

transport = on_message(rule=regex(r"\[CQ:at,qq=" + supervisor_id + "\]"))


@transport.handle()
async def at_mes_transport(bot: Bot, event: Event):
    try:
        await bot.call_api("send_private_msg",
                           user_id=supervisor_id,
                           message='From ' + str(event.get_user_id())
                                   + ':\n\n' + str(event.get_message())
                           )

    except NetworkError:
        pass
