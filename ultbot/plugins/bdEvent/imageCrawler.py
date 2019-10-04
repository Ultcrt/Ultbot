import requests
import os


# 图片不存在时会保存无法正常打开的图片
def card_image_crawler(json_dict):
    # 默认根位置
    path = './bandori_data/image/cards/'
    url = 'https://bestdori.com/assets/jp/characters/resourceset/'
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
            image = requests.get(url + 'card_after_training.png')
            with open(path + 'card_after_training.png', 'wb') as f:
                f.write(image.content)
    # 特训前储存
    # 判断是否已经储存，已有则跳过（卡面更新可能性极小所以不进行更新）
    if not os.path.exists(path + 'card_normal.png'):
        image = requests.get(url + 'card_normal.png')
        with open(path + 'card_normal.png', 'wb') as f:
            f.write(image.content)


# save_path是为了区分活动和卡池
def banner_image_crawler(save_path, json_dict):
    # 默认根位置
    url = 'https://bestdori.com/assets/jp/homebanner_rip/'
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
    image = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(image.content)
