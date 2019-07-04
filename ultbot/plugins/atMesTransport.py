import nonebot

bot = nonebot.get_bot()

@bot.on_message('group')
async def _(ctx:Context_T):
    
