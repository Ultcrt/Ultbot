import requests


def crawler():
    url = 'https://weibo.cn/u/6314659177'
    temp = requests.get(url, cookies=cookie)
    with open('tmp.html', 'w') as f:
        f.write(temp.content.decode('utf-8', 'ignore'))
