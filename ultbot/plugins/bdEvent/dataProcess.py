import pytz
from datetime import datetime
from bs4 import BeautifulSoup
import re


# 获取活动信息
def data_process(html_file_name):
    with open(html_file_name, 'r', encoding="utf-8") as f:
        tmp = f.read()

    # 获取活动详情文本
    soup = BeautifulSoup(tmp, 'lxml')
    event_text = soup.find(text=re.compile(r'(亲爱的各位)|(各位亲爱的)BanG Dreamer')).parent.text

    # 获取活动名
    try:
        event_name_raw = re.search(re.compile(r'游戏内将开启「.+?」活动'), event_text).group(0)
        event_name_with_quotes = re.search(re.compile(r'「.+?」'), event_name_raw).group(0)
        event_name = list(filter(None, re.split(re.compile(r'[「」]'), event_name_with_quotes)))[0]
    except AttributeError:
        event_name = 'ERROR'

    # 获取活动类型
    try:
        if re.search(re.compile(r'挑战演出'), event_text) is not None:
            event_type = 'CP'
        else:
            event_type = '协力'

    except AttributeError:
        event_type = 'ERROR'

    # 获取活动加成属性
    try:
        bonus_type_raw = re.search(re.compile(r'将.{4,8}?属性的成员编入乐队'), event_text).group(0)
        bonus_type = re.search(re.compile(r'(HAPPY)|(PURE)|(POWERFUL)|(COOL)'), bonus_type_raw).group(0)
    except AttributeError:
        bonus_type = 'ERROR'

    # 获取活动加成成员
    try:
        bonus_members_raw = \
            re.search(
                re.compile(r'(将.{5,20}?的成员（.{3,50}?）编入乐队)|(将.{3,50}?这几位成员编入乐队)'
                           r'|(将特定角色（.{3,50}?）编入乐队)'),
                event_text).group(0)
        # 获取成员名列表
        bonus_members_list = list(filter(
            None,
            re.split(re.compile(r'[将（米歇尔）这的成员编入乐队、几位特定角色]'), bonus_members_raw)))
        # 获取成员名（乐队名）字符串
        bonus_members = ''
        for each_member in bonus_members_list:
            bonus_members += (each_member + ';')
    except TabError:
        bonus_members = 'ERROR'

    # 获取新增4星成员
    try:
        # 获取新增成员名列表
        new_rank_four_members_list = re.findall(r'★4.+?\[.+?\]', event_text)
        # 获取新增成员名字符串
        new_rank_four_members = ''
        for each_member in new_rank_four_members_list:
            new_rank_four_members += (each_member + ';')
    except AttributeError:
        new_rank_four_members = 'ERROR'

    # 获取活动开始、结束时间
    cur_datetime = datetime.now(pytz.timezone('Asia/Shanghai'))
    cur_year = cur_datetime.strftime("%Y")
    try:
        datetime_text = re.search(
            re.compile(r'活动举办时间：\d{1,2}月\d{1,2}日维护后~\d{1,2}月\d{1,2}日\d{1,2}:\d{1,2}'), event_text).group(0)
        datetime_list = re.findall(re.compile(r'\d{1,2}'), datetime_text)
        # 填补0
        counter = 0
        while counter <= 5:
            if len(datetime_list[counter]) == 1:
                datetime_list[counter] = '0' + datetime_list[counter]
            counter += 1
        start_datetime = cur_year + '-' + datetime_list[0] + '-' + datetime_list[1] + ' 15:00:00'
        end_datetime = cur_year + '-' + datetime_list[2] + '-' + datetime_list[3] + ' ' + datetime_list[4] + ':' \
                                + datetime_list[5] + ':00'
    except AttributeError:
        # 区别于数据库时间默认值
        start_datetime = '1111-11-11 11:11:11'
        end_datetime = '1111-11-11 11:11:11'

    # 活动信息储存在dict中
    event_info = [
        event_name,
        event_type,
        bonus_type,
        bonus_members,
        new_rank_four_members,
        start_datetime,
        end_datetime,
    ]

    return event_info



