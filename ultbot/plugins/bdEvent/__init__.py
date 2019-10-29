import nonebot
import time
from aiocqhttp.exceptions import Error as CQHttpError
from .updateJson import new_json_fetch, complete_json_update
from .dataProcess import event_process, card_process, gacha_process
from jieba import posseg
import jieba
from nonebot import on_command, CommandSession, \
    on_natural_language, NLPSession, IntentCommand, permission as perm
import mysql.connector
import re
from .privateConfig import user_info
import json


# 在__init__.py使用装饰器才能正常调用
# 更新时根据日本时间每天14点（大陆时间13点）
# 每日更新只对新增的json进行更新
@nonebot.scheduler.scheduled_job('cron', hour=13)
async def data_daily_update():
    bot = nonebot.get_bot()
    # 卡牌更新
    result_cards = new_json_fetch('cards')
    # 活动更新
    result_events = new_json_fetch('events')
    # 卡池更新
    result_gacha = new_json_fetch('gacha')
    # 通知管理员
    try:
        await bot.send_private_msg(user_id='326090231', message='events' + str(result_events))
    except CQHttpError:
        pass
    # 存在更新则发布更新
    for unit in result_events:
        with open('./bandori_data/json/events/' + unit, 'r', encoding='utf-8') as f:
            update_json_tmp = json.load(f)
        msg = event_process(update_json_tmp)
        await bot.send_private_msg(user_id='326090231', message='本日活动更新：\n' + msg)
        await bot.send_group_msg(group_id=912732378,
                                 message='本日活动更新：\n' + msg)
    # 通知管理员
    try:
        await bot.send_private_msg(user_id='326090231', message='cards' + str(result_cards))
    except CQHttpError:
        pass
    # 存在更新则发布更新
    for unit in result_cards:
        with open('./bandori_data/json/cards/' + unit, 'r', encoding='utf-8') as f:
            update_json_tmp = json.load(f)
        msg = card_process(update_json_tmp)
        await bot.send_private_msg(user_id='326090231', message='本日卡牌更新：\n' + msg)
        await bot.send_group_msg(group_id=912732378,
                                 message='本日卡牌更新：\n' + msg)
    # 通知管理员
    try:
        await bot.send_private_msg(user_id='326090231', message='gacha' + str(result_gacha))
    except CQHttpError:
        pass
    # 存在更新则发布更新
    for unit in result_gacha:
        with open('./bandori_data/json/gacha/' + unit, 'r', encoding='utf-8') as f:
            update_json_tmp = json.load(f)
        msg, id_list = gacha_process(update_json_tmp)
        await bot.send_private_msg(user_id='326090231', message='本日卡池更新：\n' + msg)
        await bot.send_group_msg(group_id=912732378,
                                 message='本日卡池更新：\n' + msg)
        # PICKUP卡牌信息处理
        for each_id in id_list:
            with open('./bandori_data/json/cards/' + each_id, 'r', encoding='utf-8') as f_card:
                tmp_card = json.load(f_card)
            msg = card_process(tmp_card)
            await bot.send_private_msg(user_id='326090231', message=msg)
            await bot.send_group_msg(group_id=912732378,
                                     message=msg)


@on_command('findall_events', only_to_me=False)
async def findall_events(session: CommandSession):
    elem = session.state['event_elem']
    detail = session.get('detail', prompt='请输入需要匹配内容：')
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    if elem == 'date':
        # 规范化日期格式
        detail = re.sub(re.compile(r'[./]'), '-', detail)
        detail += ' 12:00:00'
        time_array = time.strptime(detail, '%Y-%m-%d %H:%M:%S')
        # 服务储存为ms，需要变换为秒
        time_stamp = int(time.mktime(time_array)) * 1000
        cursor.execute('SELECT * FROM events WHERE startAt < %s AND endAt > %s',
                       (time_stamp, time_stamp))
    else:
        # 两边添加%并配合LIKE可以模糊匹配
        detail = '%' + detail + '%'
        # cursor.execute中的%s会处理数据为相对应的类型
        # 因此并不能把列名作为%s的对象(会自动填补单引号，使其被识别为字符串而不是列名)
        # 因此需要借助中介command
        command = \
            "SELECT * FROM events WHERE %s LIKE '%s'" % (elem, detail)
        cursor.execute(command)
    result = cursor.fetchall()
    if not result:
        await session.send('未找到指定活动')
    else:
        await session.send('查询到%d个活动，信息如下（最多只显示5个）：' % (len(result)))
        counter = 1
        for n in result:
            # n[-1]即jsonFileName
            with open('./bandori_data/json/events/' + n[-1], 'r', encoding='utf-8') as f:
                tmp = json.load(f)
            result_string = event_process(tmp)
            await session.send('搜索结果%d：\n' % (counter,) + result_string)
            # 防止过多结果匹配
            counter += 1
            # 防止过多结果匹配
            if counter > 5:
                break
    cursor.close()
    cntr.close()


@findall_events.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
    length = len(stripped_arg_list)

    # 首次执行指令
    if session.is_first_run:
        if length == 2:
            session.state['event_elem'] = stripped_arg_list[0]
            session.state['detail'] = stripped_arg_list[1].replace("'", "\\'")
        elif length == 1:
            session.state['event_elem'] = stripped_arg_list[0]
        # 参数数目不正确则给出指南
        else:
            session.finish('使用指南：\n/findall_events [搜索对象] [匹配字符]'
                           '\n\ne.g.\n/findall_events event_name 小兔子脱逃中！\n\n'
                           '其中有效的[搜索对象]为：\n'
                           'eventName\n'
                           'eventType\n'
                           'attributes\n'
                           'bonus_members\n'
                           'new_rank_four_members\n'
                           'date')
    # session.get提示输入后再次执行指令
    else:
        # session.get提示输入后若用户输入无效字符则终止指令执行
        if not stripped_arg:
            session.finish('参数无效，指令已终止')
        # session.get提示输入后用户输入有效
        else:
            # 避免字符串中存在单引号时数据库报错
            session.state['detail'] = stripped_arg_list[0].replace("'", "\\'")
    return


@on_command('findall_cards', only_to_me=False)
async def findall_cards(session: CommandSession):
    elem = session.state['card_elem']
    detail = session.get('detail', prompt='请输入需要匹配的内容：')
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    if elem == 'info':
        # detail长度为3或4，分开讨论
        if len(detail) == 3:
            cursor.execute('SELECT * FROM cards '
                           'WHERE characterId = %s AND attribute = %s '
                           'AND rarity = %s',
                           (detail[0], detail[1], detail[2]))
        else:
            cursor.execute('SELECT * FROM cards '
                           'WHERE characterId = %s AND attribute = %s '
                           'AND rarity = %s AND skillId = %s',
                           (detail[0], detail[1], detail[2], detail[3]))
    else:
        # 两边添加%并配合LIKE可以模糊匹配
        detail = '%' + detail + '%'
        cursor.execute('SELECT * FROM cards WHERE prefix LIKE %s', (detail,))
    result = cursor.fetchall()
    if not result:
        await session.send('未找到指定卡牌')
    else:
        await session.send('查询到%d个卡牌，信息如下（最多只显示5个）：' % (len(result)))
        counter = 1
        for n in result:
            # n[-1]即jsonFileName（表中最后一列元素）
            with open('./bandori_data/json/cards/' + n[-1], 'r', encoding='utf-8') as f:
                tmp = json.load(f)
            result_string = card_process(tmp)
            await session.send('搜索结果%d：\n' % (counter,) + result_string)
            # 防止过多结果匹配
            counter += 1
            # 防止过多结果匹配
            if counter > 5:
                break
    cursor.close()
    cntr.close()


@findall_cards.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
    length = len(stripped_arg_list)

    # 首次执行指令
    if session.is_first_run:
        if length == 2:
            session.state['card_elem'] = stripped_arg_list[0]
            tmp_string = stripped_arg_list[1]
            # 搜索对象为info时进一步处理
            if session.state['card_elem'] == 'info':
                tmp_string = tmp_string.split(':')
                if len(tmp_string) != 3 and len(tmp_string) != 4:
                    session.finish('有效info参数为[成员ID:属性:稀有度:技能]')
            session.state['detail'] = tmp_string
        elif length == 1:
            session.state['card_elem'] = stripped_arg_list[0]
        # 参数数目不正确则给出指南
        else:
            session.finish('使用指南：\n/findall_cards [搜索对象] [匹配字符]'
                           '\n\ne.g.\n/findall_cards info 1:pure:4:1\n\n'
                           '其中有效的[搜索对象]为：\n'
                           'info [成员ID:属性:稀有度:技能](技能可以省略)\n'
                           'prefix'
                           )
    # session.get提示输入后再次执行指令
    else:
        # session.get提示输入后若用户输入无效字符则终止指令执行
        if not stripped_arg:
            session.finish('参数无效，指令已终止')
        # session.get提示输入后用户输入有效
        else:
            tmp_string = stripped_arg_list[0]
            # 搜索对象为info时进一步处理
            if session.state['card_elem'] == 'info':
                tmp_string = tmp_string.split(':')
                if len(tmp_string) != 3 or len(tmp_string) != 4:
                    session.finish('有效info参数为:[成员ID:属性:稀有度:技能]')
            session.state['detail'] = tmp_string
    return


@on_command('findall_gacha', only_to_me=False)
async def findall_gacha(session: CommandSession):
    elem = session.state['gacha_elem']
    detail = session.get('detail', prompt='请输入需要匹配内容：')
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    if elem == 'info':
        detail_date = detail[0]
        # 规范化日期格式：将.和/替换为-
        detail_date = re.sub(re.compile(r'[./]'), '-', detail_date)
        detail_date += ' 12:00:00'
        time_array = time.strptime(detail_date, '%Y-%m-%d %H:%M:%S')
        # 服务储存为ms，需要变换为秒
        time_stamp = int(time.mktime(time_array)) * 1000
        # 检测是否有类型限定
        if len(detail) == 1:
            cursor.execute('SELECT * FROM gacha WHERE publishedAt < %s AND closedAt > %s ',
                           (time_stamp, time_stamp))
        else:
            cursor.execute('SELECT * FROM gacha WHERE publishedAt < %s AND closedAt > %s '
                           'AND type = %s',
                           (time_stamp, time_stamp, detail[1]))
    else:
        # 两边添加%并配合LIKE可以模糊匹配
        detail = '%' + detail + '%'
        cursor.execute("SELECT * FROM gacha WHERE gachaName LIKE %s", (detail,))
    result = cursor.fetchall()
    if not result:
        await session.send('未找到指定卡池')
    else:
        await session.send('查询到%d个卡池，信息如下（最多只显示5个）：' % (len(result)))
        counter = 1
        for n in result:
            # n[-1]即jsonFileName
            with open('./bandori_data/json/gacha/' + n[-1], 'r', encoding='utf-8') as f:
                tmp = json.load(f)
            result_string, id_list = gacha_process(tmp)
            await session.send('搜索结果%d：\n' % (counter,) + result_string)
            # PICKUP卡牌信息处理
            for each_id in id_list:
                with open('./bandori_data/json/cards/' + each_id, 'r', encoding='utf-8') as f_card:
                    tmp_card = json.load(f_card)
                await session.send(card_process(tmp_card))
            # 防止过多结果匹配
            counter += 1
            # 防止过多结果匹配
            if counter > 5:
                break
    cursor.close()
    cntr.close()


@findall_gacha.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
    length = len(stripped_arg_list)

    # 首次执行指令
    if session.is_first_run:
        if length == 2:
            session.state['gacha_elem'] = stripped_arg_list[0]
            tmp_string = stripped_arg_list[1]
            # 搜索对象为info时进一步处理
            if session.state['gacha_elem'] == 'info':
                tmp_string = tmp_string.split(':')
                if len(tmp_string) != 1 and len(tmp_string) != 2:
                    session.finish('有效info参数为:[时间:类型<special/limited/permanent>]')
            session.state['detail'] = tmp_string
        elif length == 1:
            session.state['gacha_elem'] = stripped_arg_list[0]
        # 参数数目不正确则给出指南
        else:
            session.finish('使用指南：\n/findall_gacha [搜索对象] [匹配字符]'
                           '\n\ne.g.\n/findall_gacha gachaName Poppin\'Partyガチャ\n\n'
                           '其中有效的[搜索对象]为：\n'
                           'gachaName\n'
                           'info [时间:类型<special/limited/permanent>](类型可以省略)')
    # session.get提示输入后再次执行指令
    else:
        # session.get提示输入后若用户输入无效字符则终止指令执行
        if not stripped_arg:
            session.finish('参数无效，指令已终止')
        # session.get提示输入后用户输入有效
        else:
            tmp_string = stripped_arg_list[0]
            # 搜索对象为info时进一步处理
            if session.state['gacha_elem'] == 'info':
                tmp_string = tmp_string.split(':')
                if len(tmp_string) != 1 and len(tmp_string) != 2:
                    session.finish('有效info参数为:[时间:类型<special/limited/permanent>]')
            session.state['detail'] = tmp_string
    return


@on_command('find_json', only_to_me=False)
async def find_json(session: CommandSession):
    elem = session.state['elem']
    detail = session.get('detail', prompt='请输入需要匹配的序号：')
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    if elem == 'events':
        cursor.execute('SELECT * FROM events WHERE jsonFileName = %s', (detail,))
        result = cursor.fetchall()
        # 发送结果
        if not result:
            await session.send('未找到指定活动')
        else:
            with open('./bandori_data/json/events/' + result[0][-1], 'r', encoding='utf-8') as f:
                tmp = json.load(f)
            result_string = event_process(tmp)
            await session.send(result_string)
    elif elem == 'cards':
        cursor.execute('SELECT * FROM cards WHERE jsonFileName = %s', (detail,))
        result = cursor.fetchall()
        # 发送结果
        if not result:
            await session.send('未找到指定卡牌')
        else:
            with open('./bandori_data/json/cards/' + result[0][-1], 'r', encoding='utf-8') as f:
                tmp = json.load(f)
            result_string = card_process(tmp)
            await session.send(result_string)
    elif elem == 'gacha':
        cursor.execute('SELECT * FROM gacha WHERE jsonFileName = %s', (detail,))
        result = cursor.fetchall()
        # 发送结果
        if not result:
            await session.send('未找到指定卡池')
        else:
            with open('./bandori_data/json/gacha/' + result[0][-1], 'r', encoding='utf-8') as f:
                tmp = json.load(f)
            result_string, id_list = gacha_process(tmp)
            await session.send(result_string)
            # PICKUP卡牌信息处理
            for each_id in id_list:
                with open('./bandori_data/json/cards/' + each_id, 'r', encoding='utf-8') as f_card:
                    tmp_card = json.load(f_card)
                await session.send(card_process(tmp_card))
    cursor.close()
    cntr.close()


@find_json.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    stripped_arg_list = list(filter(None, stripped_arg.split(' ')))
    length = len(stripped_arg_list)

    # 首次执行指令
    if session.is_first_run:
        if length == 2:
            session.state['elem'] = stripped_arg_list[0]
            session.state['detail'] = stripped_arg_list[1] + '.json'
        elif length == 1:
            session.state['elem'] = stripped_arg_list[0]
        # 参数数目不正确则给出指南
        else:
            session.finish('使用指南：\n/find_json [搜索对象] [匹配字符]'
                           '\n\ne.g.\n/find_json events 1\n\n'
                           '其中有效的[搜索对象]为：\n'
                           'events\n'
                           'cards\n'
                           'gacha'
                           )
    # session.get提示输入后再次执行指令
    else:
        # session.get提示输入后若用户输入无效字符则终止指令执行
        if not stripped_arg:
            session.finish('参数无效，指令已终止')
        # session.get提示输入后用户输入有效
        else:
            session.state['detail'] = stripped_arg_list[0] + '.json'
    return


@on_natural_language(keywords={'邦邦', 'bang dream', }, only_to_me=False)
async def _(session: NLPSession):
    # 读取邦邦字典
    jieba.load_userdict('./bandori_data/bd_dict.txt')
    # 确保有效词汇只生效一次
    find_once = True
    event_elem_once = True
    # 活动属性名称dict
    event_dict = {
        'lack_confidence': 'lack_confidence',
        '活动名': 'eventName',
        '活动类型': 'eventType',
        '加成属性': 'attribute',
        '加成成员': 'characters',
        '日期': 'date',
    }
    confidence = 0.0
    stripped_msg = session.msg_text.strip()
    words = posseg.lcut(stripped_msg)
    intent_elem = 'lack_confidence'

    # 计算置信度
    for word in words:
        if word.flag == 'find':
            # 出现'搜索'增加置信度
            if find_once:
                confidence += 40.0
                find_once = False
        elif word.flag == 'bbnz':
            # 出现邦邦专名增加置信度
            if event_elem_once:
                confidence += 40.0
                event_elem_once = False
                intent_elem = word.word
    return IntentCommand(confidence, 'findall_events',
                         current_arg=event_dict[intent_elem])


@on_command('manual_fetch', only_to_me=False, permission=perm.SUPERUSER)
async def manual_fetch(session: CommandSession):
    try:
        await session.send('Processing...')
    except CQHttpError:
        pass
    await data_daily_update()
    try:
        await session.send('Done')
    except CQHttpError:
        pass


@on_command('all_json_update', only_to_me=False, permission=perm.SUPERUSER)
async def all_json_update(session: CommandSession):
    try:
        await session.send('Processing(Will take a long time)...')
    except CQHttpError:
        pass
    try:
        complete_json_update('events')
        complete_json_update('cards')
        complete_json_update('gacha')
    except Exception as e:
        await session.send(str(e))
    try:
        await session.send('Done')
    except CQHttpError:
        pass
