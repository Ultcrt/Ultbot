import time

import openai
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from nonebot.internal.params import ArgStr
from nonebot.rule import regex

from .private_config import bot_id, api_key

request_time_gap = 10

openai.api_key = api_key

two_step_chat = on_message(rule=regex(r"(^你好~$)|(^你好～$)"))

max_tokens = 4097

prompt_ratio = 0.75

min_tokens = 1024

tokens_per_word = 3

session_info_dist = dict()


@two_step_chat.handle()
async def chat(bot: Bot, event: Event):
    if session_info_dist.get(str(event.get_session_id())) is None:
        session_info_dist[str(event.get_session_id())] = {
            "message_history": [],
            "identifier": len(session_info_dist) % 222,
            "last_request_time": 0
        }

    await bot.send(
        event,
        Message(
            "你好，%s。在之后的对话中，我将以[CQ:face,id=%s]标识我们的对话捏\n"
            "想要聊什么呢？我只会等你2min哦\n"
            "如果不想聊天了，要和我说“再见~”捏" % (
                str(event.get_user_id()),
                session_info_dist[str(event.get_session_id())]["identifier"]
            )
        )
    )


@two_step_chat.got("prompt")
async def got_prompt(bot: Bot, event: Event, prompt: str = ArgStr()):
    identifier_cq_code = "[CQ:face,id=%s]\n" % session_info_dist[str(event.get_session_id())]["identifier"]

    current_request_time = time.time()

    if prompt == "再见~" or prompt == "再见～":
        await two_step_chat.finish(Message(identifier_cq_code + "拜拜~"))

    if current_request_time - session_info_dist[str(event.get_session_id())]["last_request_time"] > request_time_gap:
        session_info_dist[str(event.get_session_id())]["last_request_time"] = current_request_time

        await bot.send(event, message=Message(identifier_cq_code + (await request(prompt, event))))

        # Reject会终止当前事件，并等待下个事件，从新执行当前依赖
        await two_step_chat.reject()
    else:
        await two_step_chat.reject(Message(identifier_cq_code + get_waiting_reject_prompt(event)))


async def request(prompt, event: Event):
    try:
        session_info_dist[str(event.get_session_id())]["message_history"].append(prompt)

        completions = await openai.Completion.acreate(
            engine="text-davinci-003",
            prompt="\n".join(session_info_dist[str(event.get_session_id())]["message_history"]) + "\n",
            max_tokens=max(min_tokens, max_tokens - len(
                "\n".join(session_info_dist[str(event.get_session_id())]["message_history"])
            ) * tokens_per_word),
            n=1,
            stop=None,
            temperature=0.9,
            timeout=request_time_gap
        )

        answer = str(completions.choices[0].text).strip()

        session_info_dist[str(event.get_session_id())]["message_history"].append(answer)

        return answer
    except Exception as e:
        if str(e).find("Please reduce your prompt") != -1:
            session_info_dist[str(event.get_session_id())]["message_history"].pop()
            session_info_dist[str(event.get_session_id())]["message_history"] = \
                session_info_dist[str(event.get_session_id())]["message_history"][-6:]

            if len(
                    "\n".join(session_info_dist[str(event.get_session_id())]["message_history"])
            ) * tokens_per_word > max_tokens:
                session_info_dist[str(event.get_session_id())]["message_history"] = []
                return "我被泥头车创了，记忆全丢失了，请重新提问捏~（其实是字数超出限制啦，将会把记忆清空）"
            else:
                return "我被泥头车创了，记忆丢失了捏，请重新提问捏~（其实是字数超出限制啦，将会把记忆删除到只剩最近三条问答）"
        else:
            return "这个不太会捏~（其实是报错啦）：\n" + str(e)


def get_waiting_reject_prompt(event: Event):
    current_request_time = time.time()
    return "我知道你很急，但是你先别急。再等{:.2f}秒".format(
        request_time_gap - (current_request_time - session_info_dist[str(event.get_session_id())]["last_request_time"])
    )
