import os
import nonebot
from nonebot import on_command, CommandSession
from aiocqhttp.exceptions import Error as CQHttpError


@on_command('ssping', only_to_me=False)
async def ssping(session: CommandSession):
    ip = '207.148.114.224'
    bot = nonebot.get_bot()
    await session.send('测试可能需要0到30s\n请耐心等待')
    temp = os.popen('ping -c 5 -w 6 %s' % ip)
    trigger = False
    for line in temp:
        if '100% packet loss' in line:
            trigger = True
    if trigger:
        try:
            await bot.send_private_msg(user_id=326090231,
                                       message='ss has been blocked.'
                                               '\nPlz fix it in time.')
            await bot.send_private_msg(user_id=1399677960,
                                       message='ss has been blocked.'
                                               '\nPlz fix it in time.')
            await session.send('ss死了\nUltbot已通知管理者')
        except CQHttpError:
            pass
    else:
        try:
            await session.send('ss工作正常，请检察个人网络状态')
        except CQHttpError:
            pass
    temp.close()
