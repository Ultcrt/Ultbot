from time import sleep

import requests
import json

headers = {
    'accept': 'application/json, text/plain, */*',
    'referer': 'https://bestdori.com/info/events/',
    'sec-ch-ua': 'Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71',
}


def json_crawler(url, file_path=None, wait_time=0):
    tmp = requests.get(url, headers=headers, timeout=5)
    # 检测请求是否错误
    if tmp.status_code != 200:
        return
    sleep(wait_time)

    if file_path is not None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tmp.json(), f, ensure_ascii=False)

    return tmp.json()
