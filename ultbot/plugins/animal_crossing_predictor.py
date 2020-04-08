import nonebot
from datetime import datetime
import json
import pathlib
from nonebot.typing import Context_T
import re
import pytz

# bot = nonebot.get_bot()


#@bot.on_message('private')
async def price_submit(ctx: Context_T):
    # 获得价格数据
    flag = re.match(r"^(t)(\d{1,3})$", ctx['raw_message'])
    cur_price = 0
    if flag is None:
        # 格式错误，不响应
        return
    # 格式正确则读取并继续程序
    cur_price = int(flag.group(2))
    # 更新本地数据
    price_history = data_update(cur_price, ctx)
    # 计算结果
    calculate(price_history)


def data_update(cur_price, ctx: Context_T):
    # 查看是否存在用户记录
    price_history = {}
    path = pathlib.Path('./animal_crossing_data/' + ctx['user_id'] + '.json')
    # 存在则读取
    if path.is_file():
        with open(path, 'r', encoding='utf-8') as f:
            price_history = json.load(f)
    # 获取当前时间
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    key = ''
    # 周日不分上下午
    if now.weekday() == 6:
        key = str(now.weekday() + 1)
    else:
        key = str(now.weekday() + 1)+now.strftime('%p')
    # 更新价格信息, weekday返回0~6, 加1便于理解
    price_history.update({key: cur_price})
    # 写入json文件
    with open(path, "w", encoding='utf-8') as f:
        json.dump(price_history, f)
    return price_history


def calculate(price_history):
    


if __name__ == '__main__':
    price_history = {}
    now = datetime.now()
    price_history.update({str(now.weekday() + 1) + now.strftime('%p'): 22})
    print(price_history)


