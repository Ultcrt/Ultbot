from nonebot import on_natural_language, NLPSession
from aiocqhttp.exceptions import Error as CQHttpError

@on_natural_language(keywords={'给鸭鸭塞口球'}, only_to_me = False)
async def _(session:NLPSession):
	bot = session.bot
	try:
		await bot.set_group_ban(group_id=912732378,user_id=952363797)
	except CQHttpError:
		pass
