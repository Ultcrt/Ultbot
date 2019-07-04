from nonebot import on_natural_language, NLPSession

@on_natural_language(keywords={'给鸭鸭塞口球'}, only_to_me = False)
async def _(session:NLPSession):
	bot = session.bot
	info = await bot.set_group_ban(group_id=912732378,user_id=952363797)
