import time

import openai
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.internal.params import ArgStr
from nonebot.rule import regex
from .private_config import bot_id, api_key, mongo_host, mongo_port
from pymongo import MongoClient

# OpenAI API settings
openai.api_key = api_key
request_time_gap = 0       # Seconds
system_default_prompt = {"role": "system", "content": "你是一个可爱阳光的二次元美少女"}

# Mongodb settings
mongo_client = MongoClient(host=mongo_host, port=mongo_port)
mongo_db = mongo_client["UltBot"]
mongo_col = mongo_db["chatbot"]

user_info_caches = dict()

two_step_chat = on_message(rule=regex(r"(^你好~$)|(^你好～$)"))


@two_step_chat.handle()
async def chat(bot: Bot, event: MessageEvent):
    user_info = mongo_col.find_one(
        get_session_id_filter(event),
        {
            "messages": 1,
            "identifier": 1,
            "tokens_consumed": 1
        }
    )

    if user_info is None:
        # No user info, insert into mongo
        user_info = {
            "session_id": str(event.get_session_id()),
            "messages": [],
            "identifier": mongo_col.estimated_document_count() % 222,
            "tokens_consumed": 0
        }

        mongo_col.insert_one(user_info)

        user_info.pop("session_id")

    user_info.update({
        "last_request_time": 0,
        "last_tokens_consumed": user_info["tokens_consumed"]
    })

    user_info_caches[str(event.get_session_id())] = user_info

    print(user_info_caches)

    await bot.send(
        event,
        Message(
            "你好，%s（%s）。在之后的对话中，我将以[CQ:face,id=%s]标识我们的对话捏\n"
            "想要聊什么呢？我只会等你2min哦\n"
            "如果不想聊天了，要和我说“再见~”捏\n"
            "如果想和我下次继续聊下去，那就和我说“等我下~”捏" % (
                str(event.sender.nickname),
                str(event.user_id),
                user_info_caches[str(event.get_session_id())]["identifier"]
            )
        )
    )


@two_step_chat.got("prompt")
async def got_prompt(bot: Bot, event: MessageEvent, prompt: str = ArgStr()):
    identifier_cq_code = "[CQ:face,id=%s]\n" % user_info_caches[str(event.get_session_id())]["identifier"]

    current_request_time = time.time()

    if prompt == "再见~" or prompt == "再见～":
        mongo_col.update_one(
            get_session_id_filter(event),
            {
                "$set": {"messages": []}
            }
        )
        await two_step_chat.finish(Message(identifier_cq_code + "拜拜~（本次对话供消耗了{0}个token）".format(
            get_tokens_consumed_in_session(event)
        )))

    if prompt == "等我下~" or prompt == "等我下～":
        mongo_col.update_one(
            get_session_id_filter(event),
            {
                "$set": {"messages": user_info_caches[str(event.get_session_id())]["messages"]}
            }
        )
        await two_step_chat.finish(Message(identifier_cq_code + "等你捏~（本次对话供消耗了{0}个token）".format(
            get_tokens_consumed_in_session(event)
        )))

    if current_request_time - user_info_caches[str(event.get_session_id())]["last_request_time"] > request_time_gap:
        user_info_caches[str(event.get_session_id())]["last_request_time"] = current_request_time

        await bot.send(event, message=Message(identifier_cq_code + (await request(prompt, event))))

        # Reject会终止当前事件，并等待下个事件，从新执行当前依赖
        await two_step_chat.reject()
    else:
        await two_step_chat.reject(Message(identifier_cq_code + get_waiting_reject_prompt(event)))


async def request(prompt, event: MessageEvent):
    try:
        current_messages = [system_default_prompt]
        current_messages.extend(user_info_caches[str(event.get_session_id())]["messages"])
        current_messages.append({
            "role": "user",
            "content": prompt
        })

        completions = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=current_messages
        )

        # Record tokens consumed by user
        user_info_caches[str(event.get_session_id())]["tokens_consumed"] += int(completions.usage.total_tokens)

        mongo_col.update_one(
            get_session_id_filter(event),
            {
                "$set": {
                    "tokens_consumed": user_info_caches[str(event.get_session_id())]["tokens_consumed"]
                }
            }
        )

        answer = str(completions.choices[0].message.content).strip()

        user_info_caches[str(event.get_session_id())]["messages"].append({
            "role": "user",
            "content": prompt
        })

        user_info_caches[str(event.get_session_id())]["messages"].append({
            "role": "assistant",
            "content": answer
        })

        return answer
    except Exception as e:
        if str(e).find("Please reduce your prompt") != -1:
            return "太长不看捏~（其实是提问+回复的字数超出限制啦，请缩短提问长度）"
        else:
            return "这个不太会捏~（其实是报错啦）：\n" + str(e)


def get_waiting_reject_prompt(event: MessageEvent):
    current_request_time = time.time()
    return "我知道你很急，但是你先别急。再等{:.2f}秒".format(
        request_time_gap - (current_request_time - user_info_caches[str(event.get_session_id())]["last_request_time"])
    )


def get_session_id_filter(event: MessageEvent):
    return {'session_id': str(event.get_session_id())}


def get_tokens_consumed_in_session(event: MessageEvent):
    return user_info_caches[str(event.get_session_id())]["tokens_consumed"] - \
           user_info_caches[str(event.get_session_id())]["last_tokens_consumed"]
