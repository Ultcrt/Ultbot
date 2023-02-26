import os.path

import nonebot
import json

import time
from matplotlib.font_manager import FontProperties
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Event, Message
from nonebot.adapters.onebot.v11.bot import Bot
from .coingecko_api import exchange_list, get_exchange_rates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from .private_config import group_id, bot_id

scheduler = require('nonebot_plugin_apscheduler').scheduler

local_record_path = "./data/eth_data/records.json"

images_path = "W:/Program Files/go-http/data/images/"

plt_font = FontProperties(fname="./tools/sarasa-regular.ttc")

TIMES_ALL = 25920
TIMES_MONTHLY = 4320
TIMES_DAILY = 144

RECORD_SECOND_GAP = 600
RECORD_MINUTE_GAP = RECORD_SECOND_GAP / 60

# 半小时
DAILY_SECOND_GAP = 1800
# 半天
MONTHLY_SECOND_GAP = 43200
# 3天
ALL_SECOND_GAP = 259200


# ETH价格记录
@scheduler.scheduled_job('interval', start_date='2021-7-20 00:00:00', minutes=RECORD_MINUTE_GAP, misfire_grace_time=60)
async def eth_recorder():
    with open(local_record_path, "r") as f:
        records = json.load(f)

    json_resp = get_exchange_rates()

    btc_to_eth = json_resp["eth"]["value"]
    btc_to_usd = json_resp["usd"]["value"]
    btc_to_cny = json_resp["cny"]["value"]

    eth_to_usd = btc_to_usd / btc_to_eth
    eth_to_cny = btc_to_cny / btc_to_eth

    records.update({
        str(time.time()): {
            "usd": eth_to_usd,
            "cny": eth_to_cny
        }
    })

    # up to 180 days
    while len(records) > TIMES_ALL:
        records.pop(records.keys()[0])

    with open(local_record_path, "w") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)


# ETH价格群定时通知
@scheduler.scheduled_job('interval', start_date='2021-7-20 00:00:00', hours=3, misfire_grace_time=60)
async def eth_reminder(event=None):
    bot = nonebot.get_bots()[bot_id]

    with open(local_record_path, "r") as f:
        records = json.load(f)

    eth_to_cny = list(records.values())[-1]["cny"]
    eth_to_usd = list(records.values())[-1]["usd"]

    message_text = "以太坊汇率（%s）：\n以太坊兑人民币：%.3f\n以太坊兑美元：%.3f\n走势图生成中，请稍后" \
                   % (time.strftime("%H点%M分", time.localtime(float(list(records.keys())[-1]))),
                      eth_to_cny,
                      eth_to_usd)

    if event is None:
        await bot.call_api("send_group_msg",
                           group_id=group_id,
                           message=message_text)
    else:
        await bot.send(event, message_text)

    daily_prices = list(map(lambda x: x["cny"], list(records.values())[-TIMES_DAILY:]))
    monthly_prices = list(map(lambda x: x["cny"], list(records.values())[-TIMES_MONTHLY:]))
    all_prices = list(map(lambda x: x["cny"], list(records.values())))

    daily_dates = list(map(float, list(records.keys())[-TIMES_DAILY:]))
    monthly_dates = list(map(float, list(records.keys())[-TIMES_MONTHLY:]))
    all_dates = list(map(float, records.keys()))

    daily_date_labels = []
    monthly_date_labels = []
    all_date_labels = []

    daily_date_ticks = []
    monthly_date_ticks = []
    all_date_ticks = []

    present_timestamp = float(list(records.keys())[-1])

    current = present_timestamp
    for idx in range(TIMES_DAILY + int(DAILY_SECOND_GAP/RECORD_SECOND_GAP)):
        time_array = time.localtime(current)
        if (present_timestamp - current) % DAILY_SECOND_GAP == 0:
            daily_date_labels.insert(0, time.strftime("%d日 %H点%M分", time_array))
            daily_date_ticks.insert(0, current)
        current -= RECORD_SECOND_GAP

    current = present_timestamp
    for idx in range(TIMES_MONTHLY + int(MONTHLY_SECOND_GAP/RECORD_SECOND_GAP)):
        time_array = time.localtime(current)
        if (present_timestamp - current) % MONTHLY_SECOND_GAP == 0:
            monthly_date_labels.insert(0, time.strftime("%m月%d日 %H点", time_array))
            monthly_date_ticks.insert(0, current)
        current -= RECORD_SECOND_GAP

    current = present_timestamp
    for idx in range(TIMES_ALL + int(ALL_SECOND_GAP/RECORD_SECOND_GAP)):
        time_array = time.localtime(current)
        if (present_timestamp - current) % ALL_SECOND_GAP == 0:
            all_date_labels.insert(0, time.strftime("%Y年%m月%d日", time_array))
            all_date_ticks.insert(0, current)
        current -= RECORD_SECOND_GAP

    eth_history_plt_generate(daily_prices, daily_dates, daily_date_ticks, daily_date_labels, "eth_daily.jpg")
    eth_history_plt_generate(monthly_prices, monthly_dates, monthly_date_ticks, monthly_date_labels, "eth_monthly.jpg")
    eth_history_plt_generate(all_prices, all_dates, all_date_ticks, all_date_labels, "eth_all.jpg")

    message_chart = Message("以太坊汇率走势：\n"
                            "24h内：\n[CQ:image,file=eth_daily.jpg]\n"
                            "30天内：\n[CQ:image,file=eth_monthly.jpg]\n"
                            "180天内：\n[CQ:image,file=eth_all.jpg]")

    if event is None:
        await bot.call_api("send_group_msg",
                           group_id=group_id,
                           message=message_chart)
    else:
        await bot.send(event, message_chart)


exchange_cmd = on_command("exchange")


@exchange_cmd.handle()
async def exchange(bot: Bot, event: Event):
    stripped_arg = str(event.get_message()).strip()
    stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
    have_opt = False

    json_resp = get_exchange_rates()

    # 处理命令选项
    for arg in stripped_arg_list:
        if arg.startswith("-"):
            stripped_arg_list.remove(arg)
            have_opt = True
            if arg == "-l":
                await bot.send(event, exchange_list(json_resp))
                return
            elif arg == "-eth":
                await eth_reminder(event=event)
                return
            else:
                await bot.send(event, "'{opt}'选项不存在".format(opt=arg))

    # 长度需要在删除命令选项后获得
    length = len(stripped_arg_list)

    # 处理命令参数
    if length == 0:
        if not have_opt:
            await bot.send(
                event,
                "指令格式：\n/exchange [源币种] [目标币种] [金额]\n/exchange [源币种] [目标币种]\n/exchange [源币种]")
    elif length == 1:
        src_abbr = stripped_arg_list[0]
        if json_resp.get(src_abbr) is None:
            await bot.send(
                event,
                "币种'{abbr}'不存在，币种简写对照表可使用指令：/exchange -l获取".
                format(abbr=src_abbr))
        else:
            src_name = json_resp[src_abbr]["name"]

            btc_to_src = json_resp[src_abbr]["value"]
            btc_to_usd = json_resp["usd"]["value"]
            btc_to_cny = json_resp["cny"]["value"]

            target_to_usd = btc_to_usd / btc_to_src
            target_to_cny = btc_to_cny / btc_to_src

            await bot.send(
                event,
                "'{src}'兑人民币：{cny:.3f}\n'{src}'兑美元：{usd:.3f}".
                format(src=src_name, cny=target_to_cny, usd=target_to_usd))
    else:
        src_abbr = stripped_arg_list[0]
        dest_abbr = stripped_arg_list[1]

        none_str = ""
        if json_resp.get(src_abbr) is None:
            none_str += src_abbr
        if json_resp.get(dest_abbr) is None:
            none_str += "'与'" + dest_abbr

        if none_str != "":
            await bot.send(
                event,
                "币种'{abbr}'不存在，币种简写对照表可使用指令：/exchange -l获取".
                format(abbr=none_str))
        else:
            src_name = json_resp[src_abbr]["name"]
            dest_name = json_resp[dest_abbr]["name"]

            btc_to_src = json_resp[src_abbr]["value"]
            btc_to_dest = json_resp[dest_abbr]["value"]
            src_to_dest = btc_to_dest / btc_to_src

            if length == 2:
                await bot.send(
                    event,
                    "'{src}'兑'{dest}'：{rate:.3f}".
                    format(src=src_name, dest=dest_name, rate=src_to_dest))
            else:
                val_str = stripped_arg_list[2]
                if not val_str.isdigit():
                    await bot.send(event, "金额'{val}'非法".format(val=val_str))
                else:
                    val_float = float(val_str)
                    await bot.send(
                        event,
                        "'{src}'兑'{dest}'：{rate:.3f}\n换算结果：{res:.3f}".
                        format(src=src_name, dest=dest_name, rate=src_to_dest, res=val_float * src_to_dest))


def eth_history_plt_generate(prices, dates, date_ticks, date_labels, filename):
    plt.gcf().set_size_inches(36, 18)

    max_price = max(prices)
    min_price = min(prices)
    gap_price = max_price - min_price
    cur_price = prices[-1]

    plt.xlim(date_ticks[0], date_ticks[-1])
    plt.ylim(min_price - gap_price * 0.05, max_price + gap_price * 0.05)

    plt.gca().yaxis.set_major_formatter(mticker.FormatStrFormatter('%d 元'))
    plt.yticks(fontproperties=plt_font)
    plt.xticks(ticks=date_ticks, labels=date_labels, rotation=300, fontproperties=plt_font)

    plt.plot(dates, prices)

    plt.axhline(max_price, color='red', linestyle='--')
    plt.text(date_ticks[-1], max_price, "%0.3f" % max_price, color='red', size=20)
    plt.axhline(min_price, color='green', linestyle='--')
    plt.text(date_ticks[-1], min_price, "%0.3f" % min_price, color='green', size=20)
    plt.axhline(cur_price, color='orange', linestyle='--')
    plt.text(date_ticks[-1], cur_price, "%0.3f" % cur_price, color='orange', size=20)

    plt.savefig(images_path + filename, bbox_inches="tight", dpi=100)

    plt.cla()
