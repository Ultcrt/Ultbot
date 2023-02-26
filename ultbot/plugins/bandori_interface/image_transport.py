import os
from PIL import Image
import shutil


# 由于CQ码不支持其他路径的图片，使用此函数将图片复制到'/data/images/'中
def image_to_coolq_file(relative_source_image_path, target_file_name):
    # 左侧获取Ultbot文件夹的绝对位置
    # 切割一次，以删除'../bandori_data/'开头的..
    source_path = os.getcwd().split('script')[0] + relative_source_image_path.split('..', 1)[1]
    compression_path = source_path.split('.')[0] + '_s' + '.png'
    target_path = os.getcwd().split('script')[0] + 'data/images/' + target_file_name
    # 如果是服务器中不存在的图片，保存到本地的文件为垃圾文件
    # Image库将抛出OSError，因此只需要将该垃圾文件复制即可（酷q发送时会显示为空行）
    try:
        # 检测是否存在压缩后的图片
        if not os.path.exists(compression_path):
            # 不存在则压缩
            image_compression(source_path)
        shutil.copy(compression_path, target_path)
    except OSError:
        shutil.copy(source_path, target_path)


# 由于服务器网速有限，需要简单压缩图像
def image_compression(source_image_path):
    # 打开原始图像
    img = Image.open(source_image_path)
    # 获取尺寸
    w, h = img.size
    # 改变尺寸
    img = img.resize((int(w / 2), int(h / 2)), Image.ANTIALIAS)
    # 保存
    # 切割图片后缀并修改名称
    compression_path = source_image_path.split('.')[0] + '_s' + '.png'
    img.save(compression_path)
