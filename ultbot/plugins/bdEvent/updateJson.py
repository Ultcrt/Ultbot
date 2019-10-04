import os
from .jsonCrawler import json_crawler
from .timeCounter import time_counter
import json
from .writeToDataBase import event_to_db, gacha_to_db, card_to_db
from .privateConfig import user_info


def new_json_fetch(json_file_type):
    # 不加/是为了便于处理all.5.json
    local_path = './bandori_data/json/' + json_file_type
    url_path = 'https://bestdori.com/api/' + json_file_type + '/'
    # 获取最新的all.5.json以得到序号信息（dict）
    # 保存到./bandori_data/json/下，否则会影响排序
    json_crawler(url_path + 'all.5.json', local_path + '.json')
    with open(local_path + '.json', 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    local_path += '/'
    json_dir = os.listdir(local_path)
    # 排序后获取最大的json文件序号
    # 之前使用的排序方法：
    # json_dir.sort(key=lambda x: int(x[:-5]))
    # tmp = sorted(tmp, key=lambda x: int(x))
    # 记录下载的json序号，以便录入数据库和通知用户
    result = []
    for key in tmp:
        # dict中存在本地不存在的json文件信息则下载
        if key + '.json' not in json_dir:
            # 等待0.3秒
            time_counter(0.3)
            json_crawler(url_path + key + '.json', local_path + key + '.json')
            result.append(key + '.json')
        # 当遇到小于等于最大序号的key时直接跳出（已存在）
        else:
            break
    if json_file_type == 'events':
        for each in result:
            event_to_db(each, user_info)
    elif json_file_type == 'cards':
        for each in result:
            card_to_db(each, user_info)
    elif json_file_type == 'gacha':
        for each in result:
            gacha_to_db(each, user_info)
    return result


def complete_json_update(json_file_type):
    # 不加/是为了便于处理all.5.json
    local_path = './bandori_data/json/' + json_file_type
    url_path = 'https://bestdori.com/api/' + json_file_type + '/'
    # 获取最新的all.5.json以得到序号信息（dict）
    # 保存到./bandori_data/json/下，否则会影响排序
    json_crawler(url_path + 'all.5.json', local_path + '.json')
    with open(local_path + '.json', 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    local_path += '/'
    for key in tmp:
        # 等待0.1秒
        time_counter(0.1)
        json_crawler(url_path + key + '.json', local_path + key + '.json')
    if json_file_type == 'events':
        for each in tmp:
            event_to_db(each + '.json', user_info)
    elif json_file_type == 'cards':
        for each in tmp:
            card_to_db(each + '.json', user_info)
    elif json_file_type == 'gacha':
        for each in tmp:
            gacha_to_db(each + '.json', user_info)
