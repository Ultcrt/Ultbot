import nonebot
from aiocqhttp.exceptions import Error as CQHttpError
from .htmlProcess import crawler, get_event_url
from .privateConfig import weibo_cookie, user_info
from .dataProcess import data_process
from .write_to_db import write_to_db
from jieba import posseg
import jieba
from nonebot import on_command, CommandSession, on_natural_language, NLPSession, IntentCommand
import mysql.connector
import re


@nonebot.scheduler.scheduled_job('cron', day_of_week='tue', hour=15)
async def bd_new_event_process():
    # 邦邦微博主页储存在tmp_root，活动详情储存在tmp_detail
    tmp_root = 'tmp_root.html'
    tmp_detail = 'tmp_detail.html'
    root_url = 'https://weibo.cn/u/6314659177'

    # 爬取主页
    crawler(root_url, weibo_cookie, tmp_root)
    # 获取活动详情页url
    detail_url = get_event_url(tmp_root)
    # 爬取活动详情页，爬取失败返回None
    if detail_url:
        raise ValueError
    else:
        crawler(detail_url, weibo_cookie, tmp_detail)

    # 获取活动信息
    event_info = data_process(tmp_detail)

    # 写入数据库
    write_to_db(event_info, user_info)

    # 转发活动信息
    bot = nonebot.get_bot()
    bonus_members_lined = event_info[3].replace(';', '\n')
    new_rank_four_lined = event_info[4].replace(';', '\n')
    try:
        await bot.send_group_msg(group_id=912732378,
                                 message='本周邦邦活动：\n%s\n\n'
                                         '活动类型：\n%s\n\n'
                                         '加成属性：\n%s\n\n'
                                         '加成成员：\n%s\n'
                                         '新增★4成员：\n%s\n'
                                         '持续时间：\n%s\n'
                                         '至\n%s' % (event_info[0], event_info[1], event_info[2], bonus_members_lined,
                                                    new_rank_four_lined, event_info[5], event_info[6],))
    except CQHttpError:
        pass


@on_command('findall_events', only_to_me=False)
async def findall_events(session: CommandSession):
    elem = session.state['event_elem']
    # 两边添加%并配合LIKE可以不严格匹配
    detail = '%' + session.get('detail', prompt='请输入需要匹配的字符串：') + '%'
    # 规范化日期格式
    if elem == 'start_time' or elem == 'end_time':
        detail = re.sub(re.compile(r'[./]'), '-', detail)
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    # 使用 '%s LIKE %s',(elem, detail) 无法正常识别elem，这是由于mysql中%s会自动补充''
    command = 'SELECT * FROM event WHERE %s LIKE \'%s\'' % (elem, detail)
    cursor.execute(command)
    result = cursor.fetchall()
    if not result:
        await session.send('未找到指定活动')
    else:
        await session.send('活动信息如下：')
        counter = 1
        for n in result:
            bonus_members_lined = n[4].replace(';', '\n')
            new_rank_four_lined = n[5].replace(';', '\n')
            await session.send('搜索结果%d：\n%s\n\n'
                               '活动类型：\n%s\n\n'
                               '加成属性：\n%s\n\n'
                               '加成成员：\n%s\n'
                               '新增★4成员：\n%s\n'
                               '持续时间：\n%s\n'
                               '至\n%s' % (counter, n[1], n[2], n[3], bonus_members_lined,
                                          new_rank_four_lined, n[6], n[7],))
            counter += 1
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
            session.state['detail'] = stripped_arg_list[1]
        elif length == 1:
            session.state['event_elem'] = stripped_arg_list[0]
        # 没有任何参数输入则给出指南
        else:
            session.finish('使用指南：\n/findall_events [搜索对象] [匹配字符]'
                           '\ne.g.\n/findall_events event_name 小兔子脱逃中！')
    # session.get提示输入后再次执行指令
    else:
        # session.get提示输入后若用户输入无效字符则终止指令执行
        if not stripped_arg:
            session.finish('参数无效，指令已终止')
        # session.get提示输入后用户输入有效
        else:
            session.state['detail'] = stripped_arg_list[0]
    return


@on_natural_language(keywords={'邦邦', 'bang dream', }, only_to_me=False)
async def _(session: NLPSession):
    # 读取邦邦字典
    jieba.load_userdict('bd_dict.txt')
    # 确保有效词汇只生效一次
    find_once = True
    event_elem_once = True
    # 活动属性名称dict
    event_dict = {
        'lack_confidence': 'lack_confidence',
        '活动名': 'event_name',
        '活动类型': 'event_type',
        '加成属性': 'bonus_type',
        '加成成员': 'bonus_members',
        '新增成员': 'new_rank_four_members',
        '开始日期': 'start_time',
        '结束日期': 'end_time',
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





