import time

import openai
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.internal.params import ArgStr
from nonebot.rule import regex

from .private_config import bot_id, api_key

request_time_gap = 10

last_request_time = 0

openai.api_key = api_key

two_step_chat = on_message(rule=regex(r"^你好~$"))

max_tokens = 4097

prompt_ratio = 0.75

min_tokens = 1024

message_history = ""

tokens_per_word = 3


@two_step_chat.handle()
async def chat(bot: Bot, event: Event):
    current_request_time = time.time()

    if current_request_time - last_request_time > request_time_gap:
        await bot.send(event, "你好，想要聊什么呢？\n我只会等你30秒哦\n如果不想聊天了，要和我说“再见~”捏")
    else:
        await two_step_chat.finish(get_waiting_reject_prompt())


@two_step_chat.got("prompt")
async def got_prompt(bot: Bot, event: Event, prompt: str = ArgStr()):
    global last_request_time
    global message_history

    current_request_time = time.time()

    if prompt == "再见~":
        message_history = ""
        await two_step_chat.finish("拜拜~")

    if current_request_time - last_request_time > request_time_gap:
        last_request_time = current_request_time

        await bot.send(event, message="让我想想")
        await bot.send(event, message=await request(prompt))

        # Reject会终止当前事件，并等待下个事件，从新执行当前依赖
        await two_step_chat.reject()
    else:
        await two_step_chat.reject(get_waiting_reject_prompt())


async def request(prompt):
    global message_history

    try:
        message_history += prompt + "\n"

        completions = await openai.Completion.acreate(
            engine="text-davinci-003",
            prompt=message_history,
            max_tokens=max(min_tokens, max_tokens - len(message_history) * tokens_per_word),
            n=1,
            stop=None,
            temperature=0.5,
            timeout=request_time_gap
        )

        answer = str(completions.choices[0].text).strip()

        message_history += answer + "\n"

        return str(completions.choices[0].text).strip()
    except Exception as e:
        if str(e).find("Please reduce your prompt"):
            message_history = ""
            return "我被泥头车创了，记忆全丢了捏~：\n" + str(e)
        else:
            return "这个不太会捏~：\n" + str(e)


def get_waiting_reject_prompt():
    current_request_time = time.time()
    return "我知道你很急，但是你先别急。再等{:.2f}秒".format(
        request_time_gap - (current_request_time - last_request_time)
    )
