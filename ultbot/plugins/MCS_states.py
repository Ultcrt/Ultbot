import os
from nonebot import on_command, CommandSession
from aiocqhttp.exceptions import Error as CQHttpError


@on_command('mcsinfo', only_to_me=False)
async def mcsinfo(session: CommandSession):
    result = os.popen('netstat  -anp  |grep 25565').read()
    if 'LISTEN' not in result:
        try:
            await session.send('Minecraft服务端运行中')
        except CQHttpError:
            pass
    else:
        try:
            await session.send('Minecraft服务端目前停止运行')
        except CQHttpError:
            pass
    try:
        await session.send('如果无法访问服务器，可以尝试输入‘/mcsreboot’重启Minecraft服务端\n'
                           '警告：请核实服务器内是否有其他玩家再进行重启\n'
                           '注意：重启指令的使用者将上报至管理员')
    except CQHttpError:
        pass
