import requests
import os
from time import sleep

headers = {
    'accept': 'application/json, text/plain, */*',
    'referer': 'https://bestdori.com/info/events/',
    'sec-ch-ua': 'Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71',
}


# 图片不存在时会保存无法正常打开的图片
def card_image_crawler(json_dict, wait_time):
    # 默认根位置
    path = '../bandori_data/images/cards/'
    url = ''
    # 检测是否为独占
    if json_dict['prefix'][0] is not None:
        url = 'https://bestdori.com/assets/jp/characters/resourceset/'
    elif json_dict['prefix'][1] is not None:
        url = 'https://bestdori.com/assets/en/characters/resourceset/'
    elif json_dict['prefix'][2] is not None:
        url = 'https://bestdori.com/assets/tw/characters/resourceset/'
    elif json_dict['prefix'][3] is not None:
        url = 'https://bestdori.com/assets/cn/characters/resourceset/'
    # 特定卡面位置
    path += json_dict['resourceSetName'] + '/'
    url += json_dict['resourceSetName'] + '_rip/'
    # 不存在文件夹则创建
    if not os.path.exists(path):
        os.mkdir(path)
    # 判断是否可以特训
    if json_dict['rarity'] >= 3:
        # 判断是否已经储存，已有则跳过（卡面更新可能性极小所以不进行更新）
        if not os.path.exists(path + 'card_after_training.png'):
            # 特训后储存
            image = requests.get(url + 'card_after_training.png', headers=headers, timeout=5)
            sleep(wait_time)
            with open(path + 'card_after_training.png', 'wb') as f:
                f.write(image.content)
    # 特训前储存
    # 判断是否已经储存，已有则跳过（卡面更新可能性极小所以不进行更新）
    if not os.path.exists(path + 'card_normal.png'):
        image = requests.get(url + 'card_normal.png', headers=headers, timeout=5)
        sleep(wait_time)
        with open(path + 'card_normal.png', 'wb') as f:
            f.write(image.content)


# save_path是为了区分活动和卡池
def banner_image_crawler(save_path, json_dict, wait_time):
    # 默认根位置
    url = 'https://bestdori.com/assets/jp/homebanner_rip/'
    # 不检测是否为独占，由于封面信息只录入日服信息
    # 某些json可能不包含图片信息，因此捕获KeyError
    try:
        save_path += json_dict['bannerAssetBundleName'] + '.png'
        url += json_dict['bannerAssetBundleName'] + '.png'
    except KeyError:
        return
    # 不存在图片则继续，存在则结束录入（封面更新可能性极小所以不进行更新）
    if not os.path.exists(save_path):
        pass
    else:
        return
    # 图片保存
    image = requests.get(url, headers=headers, timeout=5)
    sleep(wait_time)
    with open(save_path, 'wb') as f:
        f.write(image.content)
