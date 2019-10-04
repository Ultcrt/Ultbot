import shutil
import os


# 由于CQ码不支持其他路径的图片，使用此函数将图片复制到'/data/image/'中
def image_to_coolq_file(source_image_path, target_file_name):
    # 左侧获取Ultbot文件夹的绝对位置
    source_path = os.getcwd() + source_image_path.split('.', 1)[1]
    target_path = os.getcwd().split('script')[0] + 'data/image/' + target_file_name
    shutil.copy(source_path, target_path)

