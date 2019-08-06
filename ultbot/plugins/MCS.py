import os
import nonebot
from nonebot import on_command, CommandSession
from aiocqhttp.exceptions import Error as CQHttpError

bot = nonebot.get_bot()


@on_command('mcsreboot', only_to_me=False)
async def mcsreboot(session: CommandSession):
    try:
        await bot.send_private_msg(user_id=326090231,
                                   message=str(session.ctx['user_id'])
                                   + ' tried to reboot MCS.')
    except CQHttpError:
        pass
    result = os.popen('ps -ef | grep server.jar')
    try:
        await session.send('服务器重启中，请等待1min左右')
    except CQHttpError:
        pass
    # 检测服务器是否正在运行
    for string in result:
        # 如果已经运行则kill后再启动
        if 'java -Xmx1536M -Xms1536M -jar server.jar nogui' in string:
            process_id = list(filter(None, string.split(' ')))[1]
            os.system('kill -9 %s' % process_id)
    os.system('cd /opt/mcs/; '
              'nohup java -Xmx1G -Xms1G -jar server.jar nogui >/opt/mcs/mcs.log &')
    result.close()


@on_command('mcsinfo', only_to_me=False)
async def mcsinfo(session: CommandSession):
    result = os.popen('netstat  -anp  |grep 25565').read()
    if result:
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
