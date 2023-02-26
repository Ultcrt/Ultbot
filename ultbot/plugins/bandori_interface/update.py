from .json_crawler import json_crawler
import json


def new_fetch(json_file_type):
    # 不加/是为了便于处理all.5.json
    local_path = '../bandori_data/records.json'
    url_path = 'https://bestdori.com/api/' + json_file_type + '/'

    # 获取最新的all.5.json以得到ID信息，通过其间接检查更新，无需保存
    all_json = json_crawler(url_path + 'all.5.json', wait_time=1)
    with open(local_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    # 记录下载的json序号
    results = []
    for key in all_json.keys():
        # dict中存在本地不存在的json文件信息则下载
        if key not in records[json_file_type]:
            detail_json = json_crawler(url_path + key + '.json', wait_time=1)
            # 更新records
            records[json_file_type].append(key)
            # 保证json下载与数据库写入同时进行，避免了两者不同步的问题
            results.append(detail_json)

    # 如果发生更新则写入json
    if len(results) > 0:
        with open(local_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=4)

    return results
