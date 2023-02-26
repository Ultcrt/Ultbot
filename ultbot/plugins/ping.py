from subprocess import PIPE, Popen
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.exception import NetworkError

ping = on_command("ping", priority=5)


@ping.handle()
async def ping_with_qq(bot: Bot, event: Event):
    try:
        ip = str(event.get_message()).strip()
        await bot.send(event, '测试可能需要0到30s\n请耐心等待')
        proc = Popen('ping -c 5 -w 6 %s' % ip, stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True)
        outs, errs = proc.communicate()

        if len(errs) != 0:
            await bot.send(event, "'ping %s'执行出错：\n" % ip + errs)
            return

        if '100% packet loss' in outs:
            await bot.send(event, '%s 无法正常访问' % ip)
        else:
            await bot.send(event, '%s 能够正常访问' % ip)
    except NetworkError:
        pass
