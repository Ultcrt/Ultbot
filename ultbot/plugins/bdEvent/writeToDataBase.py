import json
import mysql.connector
from .imageCrawler import card_image_crawler, banner_image_crawler

# 所有数据库中的数据仅作为引索使用


def gacha_to_db(file_name_without_path, user_info):
    # 保存图片
    json_file_path = './bandori_data/json/gacha/' + file_name_without_path
    with open(json_file_path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    banner_image_crawler('./bandori_data/image/gacha/', tmp)
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    start_tmp = tmp['publishedAt'][0]
    end_tmp = tmp['closedAt'][0]
    # 检查卡池是否不存在于日服(数据库的检索只支持日服时间,目前只有台湾扭蛋卡池比较奇葩)
    if start_tmp is None:
        return
    cursor = cntr.cursor()
    # 检测活动数据是否已经存在,利用传入活动名称不存在于数据表时，返回list长度为0
    cursor.execute('SELECT jsonFileName FROM gacha WHERE jsonFileName = %s', (file_name_without_path,))
    guarantee = cursor.fetchall()
    if len(guarantee):
        cursor.execute('UPDATE gacha SET gachaName = %s, type = %s,'
                       'publishedAt = %s, closedAt = %s WHERE jsonFileName = %s',
                       (str(tmp['gachaName']), tmp['type'], start_tmp, end_tmp,
                        file_name_without_path))
    else:
        cursor.execute('INSERT INTO'
                       ' gacha (gachaName, type, publishedAt, closedAt,'
                       ' jsonFileName) VALUES (%s, %s, %s, %s, %s)',
                       (str(tmp['gachaName']), tmp['type'], start_tmp, end_tmp,
                        file_name_without_path))
    cntr.commit()
    cursor.close()
    cntr.close()


def card_to_db(file_name_without_path, user_info):
    # 保存图片
    json_file_path = './bandori_data/json/cards/' + file_name_without_path
    with open(json_file_path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    card_image_crawler(tmp)
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    # 检测活动数据是否已经存在,利用传入活动名称不存在于数据表时，返回list长度为0
    cursor.execute('SELECT jsonFileName FROM cards WHERE jsonFileName = %s', (file_name_without_path,))
    guarantee = cursor.fetchall()
    if len(guarantee):
        cursor.execute('UPDATE cards SET characterId = %s, rarity = %s,'
                       'attribute = %s, prefix = %s, skillId = %s WHERE jsonFileName = %s',
                       (tmp['characterId'], tmp['rarity'], tmp['attribute'], str(tmp['prefix']),
                        tmp['skillId'], file_name_without_path))
    else:
        cursor.execute('INSERT INTO'
                       ' cards (characterId, rarity, attribute, prefix,'
                       ' skillId, jsonFileName) VALUES (%s, %s, %s, %s, %s, %s)',
                       (tmp['characterId'], tmp['rarity'], tmp['attribute'], str(tmp['prefix']),
                        tmp['skillId'], file_name_without_path))
    cntr.commit()
    cursor.close()
    cntr.close()


def event_to_db(file_name_without_path, user_info):
    # 保存图片
    json_file_path = './bandori_data/json/events/' + file_name_without_path
    with open(json_file_path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    banner_image_crawler('./bandori_data/image/events/', tmp)
    attributes_tmp = tmp['attributes'][0]['attribute']
    characters_tmp = ''
    for each_one in tmp['characters']:
        characters_tmp += str(each_one['characterId']) + ';'
    start_tmp = tmp['startAt'][0]
    end_tmp = tmp['endAt'][0]
    cntr = mysql.connector.connect(host=user_info['host'],
                                   user=user_info['user'],
                                   password=user_info['password'],
                                   database=user_info['db_name'],
                                   auth_plugin='mysql_native_password')
    cursor = cntr.cursor()
    # 检测活动数据是否已经存在,利用传入活动名称不存在于数据表时，返回list长度为0
    cursor.execute('SELECT jsonFileName FROM events WHERE jsonFileName = %s', (file_name_without_path,))
    guarantee = cursor.fetchall()
    if len(guarantee):
        cursor.execute('UPDATE events SET eventName = %s, eventType = %s,'
                       'attributes = %s, characters = %s, startAt = %s,'
                       'endAt = %s WHERE jsonFileName = %s',
                       (str(tmp['eventName']), tmp['eventType'], attributes_tmp, characters_tmp,
                        start_tmp, end_tmp, file_name_without_path))
    else:
        cursor.execute('INSERT INTO'
                       ' events (eventName, eventType, attributes, characters,'
                       ' startAt, endAt, jsonFileName) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (str(tmp['eventName']), tmp['eventType'], attributes_tmp, characters_tmp,
                        start_tmp, end_tmp, file_name_without_path))
    cntr.commit()
    cursor.close()
    cntr.close()
