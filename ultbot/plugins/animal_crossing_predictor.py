import nonebot
from datetime import datetime
from datetime import timedelta
import json
import pathlib
import os
from nonebot.typing import Context_T
import re
import pytz
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import prettytable
from PIL import Image, ImageDraw, ImageFont
from nonebot import on_command, CommandSession

bot = nonebot.get_bot()


@bot.on_message()
async def price_submit(ctx: Context_T):
    # 获得价格数据
    flag = re.match(r"^(t)(\d{1,3})$", ctx['raw_message'])
    if flag is None:
        # 格式错误，不响应
        return
    # 格式正确则读取并继续程序
    cur_price = int(flag.group(2))
    # 更新本地数据
    price_history = daily_update(cur_price, ctx['user_id'])
    # 将结果转化为字符串
    string = to_string(price_history)
    # 上传至网页并返回结果
    table = submit_to_web(string)
    # 生成图片
    await picture_process(table)
    # 发送图片
    if ctx['message_type'] == 'private':
        await bot.send_private_msg(user_id=ctx['user_id'], message='[CQ:image,file=tmp.png]')
    elif ctx['message_type'] == 'group':
        await bot.send_group_msg(group_id=ctx['group_id'], message='[CQ:image,file=tmp.png]')


@on_command('turnip', only_to_me=False)
async def update(session: CommandSession):
    user_id = session.event['user_id']
    path = get_path(user_id)
    price_history = read_json(path)
    command_lines = session.current_arg_text.split(' ')
    if len(command_lines) == 0:
        print('样例：/turnip del-1am,2am new-2am:0')
    for command in command_lines:
        args = command.split('-')
        param = args[1].split(',')
        if args[0] == 'del':
            for each in param:
                if each in price_history:
                    price_history.pop(each.upper())
        elif args[0] == 'new':
            for each in param:
                raw_item = each.split(':')
                item = {raw_item[0].upper(): int(raw_item[1])}
                price_history.update(item)
    # 将结果写入
    write_to_json(price_history, path)
    # 将结果转化为字符串
    string = to_string(price_history)
    # 上传至网页并返回结果
    table = submit_to_web(string)
    # 生成图片
    await picture_process(table)
    # 发送图片
    await session.send(message='[CQ:image,file=tmp.png]')


def get_path(user_id):
    # 获取当前时间
    now = datetime.now(pytz.timezone('Asia/Shanghai')).isocalendar()
    # 由于周日在大头菜计算中其实在下一周，因此在周日进行调用时应当指向下一周
    if now[2] == '7':
        now = (datetime.now(pytz.timezone('Asia/Shanghai'))+timedelta(days=1)).isocalendar()
    date_string = str(now[0]) + '-' + str(now[1])
    return pathlib.Path('./animal_crossing_data/' + str(user_id) + '-' + date_string + '.json')


def daily_update(cur_price, user_id):
    # 查看是否存在用户记录
    path = get_path(user_id)
    # 存在则读取
    price_history = read_json(path)
    # 获取当前星期
    calendar = datetime.now(pytz.timezone('Asia/Shanghai'))
    now = calendar.isocalendar()[2]
    ap = calendar.strftime('%p')
    key = ''
    # 周日不分上下午
    # 更新价格信息
    if now == 7:
        key = str(now)
    else:
        key = str(now)+ap
    price_history.update({key: cur_price})
    # 写入文件
    write_to_json(price_history, path)
    return price_history


def read_json(path):
    price_history = {}
    if path.is_file():
        with open(path, 'r', encoding='utf-8') as f:
            price_history = json.load(f)
    return price_history


def write_to_json(price_history: dict, path):
    with open(path, "w", encoding='utf-8') as f:
        json.dump(price_history, f)
    return price_history


def to_string(price_history):
    string = ''
    # 共7天，从星期一到日
    for i in range(1,8):
        key = str(i)
        # 周日在开头（不用判断i是否为7，data_update中确保只有7能单独作为key）
        if key in price_history:
            string = str(price_history[key]) + ' ' + string
        else:
            # 搜索i的上午
            if key + 'AM' in price_history:
                string += str(price_history[key+'AM'])+'/'
            else:
                string += '/'
            # 搜索i的下午
            if key + 'PM' in price_history:
                string += str(price_history[key+'PM'])+' '
            else:
                string += ' '
    return string


def submit_to_web(string: str):
    # 无GUI配置
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    # 打开网页
    url = 'https://www.tgbus.com/gametools/DWSYH_DTC/'
    browser = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)
    browser.get(url)
    # 获取输入框与确认按钮
    input_field = browser.find_element_by_xpath('//input[@name="inlineInput"]')
    button = browser.find_element_by_xpath('//input[@onclick="onInlinePredictionButtonClick()"]')
    # 输入数据并提交
    input_field.send_keys(string)
    button.click()
    # 获取结果
    soup = BeautifulSoup(browser.page_source, "html.parser")
    raw_body = soup.find('tbody', id='predictionTableBody')
    html_table = raw_body.parent
    raw_field = html_table.find('thead')
    # 删除多余field
    field_list = raw_field.find_all('tr')
    field_list[0].extract()
    field_list[2].extract()
    # 补充field
    tag = soup.new_tag('th')
    tag.string = '类型1'
    field_list[1].insert(0, tag)
    tag = soup.new_tag('th')
    tag.string = '类型2'
    field_list[1].insert(1, tag)
    tag = soup.new_tag('th')
    tag.string = '购入价格'
    field_list[1].insert(2, tag)
    # 修改row
    for row in raw_body.find_all('tr'):
        # th改为td
        error_elem_list = row.find_all('th')
        for elem in error_elem_list:
            elem.name = 'td'
        # 连续下跌没有type2, 需要补充一列空
        if len(error_elem_list) == 1:
            tag = soup.new_tag('td')
            tag.string = '-'
            row.insert(1, tag)
    # 表格构建
    table = prettytable.from_html(str(html_table))
    return table
    

async def picture_process(table):
    # 初始化图片对象及字体
    img = Image.new('RGB', (0, 0), (255, 255, 255, 255))
    font = ImageFont.truetype('./sarasa-fixed-cl-regular.ttf', 22)
    # 初始化画笔
    draw = ImageDraw.Draw(img)
    # 实际尺寸
    img_size = draw.multiline_textsize(str(table[0]), font=font)
    actual_img = img.resize(img_size)
    # 更新画笔
    draw = ImageDraw.Draw(actual_img)
    draw.multiline_text((0, 0), str(table[0]), font=font)
    # 保存图片
    target_path = os.getcwd().split('script')[0] + 'data/image/' + 'tmp.png'
    actual_img.save(target_path)

