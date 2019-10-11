from .imageTransport import image_to_coolq_file
import time
import json

characters = {
    1: '戸山 香澄',
    2: '花園 たえ',
    3: '牛込 りみ',
    4: '山吹 沙綾',
    5: '市ヶ谷 有咲',
    6: '美竹 蘭',
    7: '青葉 モカ',
    8: '上原 ひまり',
    9: '宇田川 巴',
    10: '羽沢 つぐみ',
    11: '弦巻 こころ',
    12: '瀬田 薫',
    13: '北沢 はぐみ',
    14: '松原 花音',
    15: '奥沢 美咲',
    16: '丸山 彩',
    17: '氷川 日菜',
    18: '白鷺 千聖',
    19: '大和 麻弥',
    20: '若宮 イヴ',
    21: '湊 友希那',
    22: '氷川 紗夜',
    23: '今井 リサ',
    24: '宇田川 あこ',
    25: '白金 燐子',
}

eventTypes = {
    'versus': '对邦',
    'story': '协力',
    'mission_live': '任务',
    'challenge': 'CP',
    'live_try': '试炼',
}

skills = {
    1: '得分提升10%',
    2: '得分提升30%',
    3: '得分提升60%',
    4: '得分提升100%',
    5: '判定强化(中)&得分提升10%',
    6: '判定强化(大)&得分提升20%',
    7: '判定强化(特大)&得分提升40%',
    8: '生命回复(中)&得分提升10%',
    9: '生命回复(大)&得分提升20%',
    10: '生命回复(特大)&得分提升40%',
    11: '判定强化(中)&得分提升30%',
    12: '判定强化(大)&得分提升60%',
    13: '生命回复300&得分提升30%',
    14: '生命回复450&得分提升60%',
    15: '生命回复300&判定强化(中)',
    16: '生命回复450&判定强化(大)',
    17: '生命900以上则得分提升65%',
    18: '生命900以上则得分提升110%',
    20: '仅在PERFECT时得分提升115%',
    21: '生命600以上则得分提升40%否则生命回复450',
    22: '生命600以上则得分提升80%否则生命回复500',
    23: '无敌并且得分提升10%',
    24: '无敌并且得分提升30%',
    25: '评分低于GREAT之前得分提升65%',
    26: '评分低于GREAT之前得分提升110%',
}


def event_process(json_dict):
    # 将图片移动到'/data/image/'
    image_to_coolq_file('./bandori_data/image/events/' + json_dict['bannerAssetBundleName'] + '.png', 'tmp.png')
    # 生成奖励成员字符串
    new_members_string = ''
    for each in json_dict['rewardCards']:
        with open('./bandori_data/json/cards/' + str(each) + '.json', 'r', encoding='utf-8') as f:
            tmp = json.load(f)
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
                eventTypes[json_dict['eventType']],
                json_dict['attributes'][0]['attribute'], json_dict['attributes'][0]['percent'],
                characters_string,
                new_members_string,
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(json_dict['startAt'][0])/1000)),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(json_dict['endAt'][0])/1000)))
    return result


def card_process(json_dict):
    # 将图片移动到'/data/image/'
    # 部分其他服独占卡牌的图片不做处理（爬取时储存为错误格式图片，显示效果为换行）
    result = ''
    image_to_coolq_file('./bandori_data/image/cards/' +
                        json_dict['resourceSetName'] + '/card_normal.png', 'cn.png')
    result += '%s\n[CQ:image,file=cn.png]\n' % (json_dict['prefix'][0], )
    # 检查是否可以特训
    if json_dict['rarity'] >= 3:
        image_to_coolq_file('./bandori_data/image/cards/' +
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
    # 将图片移动到'/data/image/'
    # 判断是否存在bannerAssetBundleName（部分台湾卡池和飞机池不存在此属性,活动和卡牌不存在此问题）
    image_name_cq = '[CQ:image,file=tmp.png]'
    try:
        image_to_coolq_file('./bandori_data/image/gacha/' +
                            json_dict['bannerAssetBundleName'] + '.png', 'tmp.png')
    # 飞机池会报错KeyError，其他服卡池会报错KeyError或FileNotFoundError
    # 把飞机池和其他服池图片都设置为飞机池(其他服池会在之后利用TypeError再分支处理)
    except (KeyError, FileNotFoundError):
        image_to_coolq_file('./bandori_data/image/gacha/' +
                            'gacha_flight.png', 'tmp.png')
    # 非日服卡池抛出TypeError
    try:
        # 记录PICKUP卡牌ID并返回，以便发送卡池信息时可以利用id和card_process发送发牌详细信息
        pick_up_cards_id = []
        all_cards_in_gacha = json_dict['details'][0]
        for key in all_cards_in_gacha:
            if all_cards_in_gacha[key]['pickup']:
                pick_up_cards_id.append(str(key) + '.json')
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

