import requests
from .cookies import weibo_cookie


def crawler():
    url = 'https://weibo.cn/u/6314659177'
    temp = requests.get(url, cookies=weibo_cookie)
    with open('tmp.html', 'w', encoding='utf-8') as f:
        f.write(temp.content.decode('utf-8', 'ignore'))


if __name__ == '__main__':
    crawler()
