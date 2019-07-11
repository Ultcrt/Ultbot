import os
from nonebot import on_command, CommandSession, permission as perm
from aiocqhttp.exceptions import Error as CQHttpError


@on_command('rcl', only_to_me=False, permission=perm.SUPERUSER)
async def rcl(session: CommandSession):
    cl = session.state['cl']
    if not cl:
        try:
            await session.send('Nothing to do.')
        except CQHttpError:
            pass
    else:
        result = os.popen(cl)
        temp = ''
        for string in result:
            temp += string
        try:
            await session.send(temp)
        except CQHttpError:
            pass


@rcl.args_parser
async def _(session: CommandSession):
    session.state['cl'] = session.current_arg_text.strip()
