import requests
import json


def json_crawler(url, file_path):
    tmp = requests.get(url)
    # 检测网站文件是否存在(一般正常为200，不存在为404)
    if tmp.status_code == 404:
        return
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(tmp.json(), f, ensure_ascii=False)
