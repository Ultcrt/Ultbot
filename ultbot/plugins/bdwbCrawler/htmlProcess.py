from bs4 import BeautifulSoup
import re
import requests


# 爬取网页
def crawler(url, cookie, html_file_name):
    tmp = requests.get(url, cookies=cookie)
    with open(html_file_name, 'w', encoding='utf-8') as f:
        f.write(tmp.content.decode('utf-8', 'ignore'))


# 获取活动详情url
def get_event_url(html_file_name):
    url_prefix = 'https://weibo.cn'
    with open(html_file_name, 'r', encoding="utf-8") as f:
        tmp = f.read()
    soup = BeautifulSoup(tmp, 'lxml')
    find_result = soup.find(text=re.compile(r'游戏内将开启「.+」活动'))
    if find_result is not None:
        entrance_ini = find_result.parent
        url_suffix = entrance_ini.find(text='全文').parent.attrs['href'].split('?')[0]
        entrance = url_prefix + url_suffix
        return entrance
    else:
        return None




