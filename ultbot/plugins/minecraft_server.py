import os
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event, NetworkError
from nonebot.adapters.onebot.v11.bot import Bot

from .private_config import supervisor_id

mcsr = on_command("mcsreboot")


@mcsr.handle()
async def mcsreboot(bot: Bot, event: Event):
    try:
        await bot.call_api("send_private_msg",
                           user_id=supervisor_id,
                           message=event.get_user_id() + ' tried to reboot MCS.')
    except NetworkError:
        pass
    result = os.popen('ps -ef | grep start_mcs.sh')
    try:
        await bot.send(event, '服务器重启中，请等待1min左右')
    except NetworkError:
        pass
    # 检测服务器是否正在运行
    for string in result:
        # 如果已经运行则kill后再启动
        if '/home/kenken/start_mcs.sh' in string:
            process_id = list(filter(None, string.split(' ')))[1]
            os.system('kill -9 %s' % process_id)
    os.system('bash /home/kenken/start_mcs.sh')
    result.close()


mcsi = on_command("mcsinfo")


@mcsi.handle()
async def mcsinfo(bot: Bot, event: Event):
    result = os.popen('netstat  -anp  |grep 25565').read()
    if result:
        try:
            await bot.send(event, 'Minecraft服务端运行中')
        except NetworkError:
            pass
    else:
        try:
            await bot.send(event, 'Minecraft服务端目前停止运行')
        except NetworkError:
            pass
    try:
        await bot.send(event, '如果无法访问服务器，可以尝试输入‘/mcsreboot’重启Minecraft服务端\n'
                              '警告：请核实服务器内是否有其他玩家再进行重启\n'
                              '注意：重启指令的使用者将上报至管理员')
    except NetworkError:
        pass
