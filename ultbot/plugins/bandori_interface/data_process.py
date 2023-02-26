from .image_crawler import card_image_crawler, banner_image_crawler
from .image_transport import image_to_coolq_file
import time
import json

from .json_crawler import json_crawler

characters = {}

skills = {}

eventTypes = {
    'versus': '对邦',
    'story': '协力',
    'mission_live': '任务',
    'challenge': 'CP',
    'live_try': '试炼',
    'festival': '5v5',
    'medley': '共演'
}


def event_process(json_dict):
    if len(characters) == 0:
        fetch_characters_dict()

    banner_image_crawler('../bandori_data/images/events/', json_dict, 1)
    # 将图片移动到'/data/images/'
    image_to_coolq_file('../bandori_data/images/events/' + json_dict['bannerAssetBundleName'] + '.png', 'tmp.png')
    # 生成奖励成员字符串
    new_members_string = ''
    url_path = 'https://bestdori.com/api/cards/'
    for each in json_dict['rewardCards']:
        tmp = json_crawler(url_path + str(each) + '.json', wait_time=1)
        new_members_string += '★' + str(tmp['rarity']) + ' ' + \
                              tmp['attribute'] + ' ' + characters[tmp['characterId']] + '(' + \
                              str(each) + ')\n'
    # 生成加成成员字符串
    characters_string = ''
    for each_characters in json_dict['characters']:
        characters_string += characters[int(each_characters['characterId'])] + \
                             '(' + str(each_characters['percent']) + '%)\n'
    result = '%s\n'\
             '[CQ:image,file=tmp.png]\n'\
             '活动类型：\n%s\n\n'\
             '加成属性：\n%s(%d%%)\n\n'\
             '加成成员：\n' \
             '%s\n'\
             '奖励成员：\n'\
             '%s\n'\
             '持续时间：\n'\
             '%s\n'\
             '至\n%s'\
             % (json_dict['eventName'][0],
                eventTypes.get(json_dict['eventType'], "未知种类"),
                json_dict['attributes'][0]['attribute'], json_dict['attributes'][0]['percent'],
                characters_string,
                new_members_string,
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(json_dict['startAt'][0])/1000)),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(json_dict['endAt'][0])/1000)))
    return result


def card_process(json_dict):
    if len(characters) == 0:
        fetch_characters_dict()
    if len(skills) == 0:
        fetch_skills_dict()
    # 将图片移动到'/data/images/'
    # 部分其他服独占卡牌的图片不做处理（爬取时储存为错误格式图片，显示效果为换行）
    card_image_crawler(json_dict, 1)
    result = ''
    image_to_coolq_file('../bandori_data/images/cards/' +
                        json_dict['resourceSetName'] + '/card_normal.png', 'cn.png')
    result += '%s\n[CQ:image,file=cn.png]\n' % (json_dict['prefix'][0], )
    # 检查是否可以特训
    if json_dict['rarity'] >= 3:
        image_to_coolq_file('../bandori_data/images/cards/' +
                            json_dict['resourceSetName'] + '/card_after_training.png', 'cat.png')
        result += '[CQ:image,file=cat.png]\n'
    result += '人物：★%d %s\n'\
              '属性：%s\n'\
              '技能：\n%s'\
              % (json_dict['rarity'], characters[json_dict['characterId']],
                 json_dict['attribute'],
                 skills[json_dict['skillId']],
                 )
    return result


def gacha_process(json_dict):
    banner_image_crawler('../bandori_data/images/gacha/', json_dict, 1)
    # 将图片移动到'/data/images/'
    # 判断是否存在bannerAssetBundleName（部分台湾卡池和飞机池不存在此属性,活动和卡牌不存在此问题）
    image_name_cq = '[CQ:image,file=tmp.png]'
    try:
        image_to_coolq_file('../bandori_data/images/gacha/' +
                            json_dict['bannerAssetBundleName'] + '.png', 'tmp.png')
    # 飞机池会报错KeyError，其他服卡池会报错KeyError或FileNotFoundError
    # 把飞机池和其他服池图片都设置为飞机池(其他服池会在之后利用TypeError再分支处理)
    except (KeyError, FileNotFoundError):
        image_to_coolq_file('../bandori_data/images/gacha/' +
                            'gacha_flight.png', 'tmp.png')
    # 非日服卡池抛出TypeError
    try:
        # 记录PICKUP卡牌ID并返回，以便发送卡池信息时可以利用id和card_process发送发牌详细信息
        pick_up_cards_id = []
        all_cards_in_gacha = json_dict['details'][0]
        for key in all_cards_in_gacha:
            if all_cards_in_gacha[key]['pickup']:
                pick_up_cards_id.append(str(key))
        result = '%s\n' \
                 '%s\n' \
                 '卡池类型：\n%s\n' \
                 '持续时间：\n' \
                 '%s\n' \
                 '至\n%s' \
                 % (json_dict['gachaName'][0],
                    image_name_cq,
                    json_dict['type'],
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(json_dict['publishedAt'][0]) / 1000)),
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(json_dict['closedAt'][0]) / 1000)))
        if len(pick_up_cards_id) > 0:
            result += '\n活动卡牌(PICK UP)如下:'
        return result, pick_up_cards_id
    except TypeError:
        return '其他服独有卡池，不进行记录', []


def fetch_characters_dict():
    url_path = "https://bestdori.com/api/characters/main.2.json"
    all_json = json_crawler(url_path, wait_time=1)
    for key, val in all_json.items():
        valid_name = val["characterName"][3] if val["characterName"][3] is not None else val["characterName"][0]
        characters.update({int(key): valid_name})


def fetch_skills_dict():
    url_path = "https://bestdori.com/api/skills/all.10.json"
    all_json = json_crawler(url_path, wait_time=1)
    for key, val in all_json.items():
        valid_description = val["description"][3] if val["description"][3] is not None else val["description"][0]
        if val.get("onceEffect") is not None:
            formatted_description = valid_description.format(
                str(val["onceEffect"]["onceEffectValue"]), str(val["duration"])
            )
        else:
            formatted_description = valid_description.format(str(val["duration"]))
        skills.update({int(key): formatted_description})

