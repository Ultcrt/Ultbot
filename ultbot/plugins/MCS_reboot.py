import os
import nonebot
from nonebot import on_command, CommandSession
from aiocqhttp.exceptions import Error as CQHttpError

bot = nonebot.get_bot()


@on_command('mcsreboot',only_to_me=False)
async def mcsreboot(session: CommandSession):
    try:
        await bot.senf_private_msg(user_id=326090231,
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
        if 'java -Xmx1536M -Xms1536M -jar server.jar nogui' in string:
            process_id = list(filter(None, string.split(' ')))[1]
            os.system('kill -9 %s' % process_id)
    os.system('cd /opt/mcs/; '
              'nohup java -Xmx1536M -Xms1536M -jar server.jar nogui >/opt/mcs/mcs.log &')

