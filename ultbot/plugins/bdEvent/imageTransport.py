import os
from PIL import Image


# 由于CQ码不支持其他路径的图片，使用此函数将图片复制到'/data/image/'中
def image_to_coolq_file(source_image_path, target_file_name):
    # 左侧获取Ultbot文件夹的绝对位置
    source_path = os.getcwd() + source_image_path.split('.', 1)[1]
    target_path = os.getcwd().split('script')[0] + 'data/image/' + target_file_name
    s_img = Image.open(source_path)
    w, h = s_img.size
    t_img = s_img.resize((int(w/2), int(h/2)), Image.ANTIALIAS)
    t_img.save(target_path)
