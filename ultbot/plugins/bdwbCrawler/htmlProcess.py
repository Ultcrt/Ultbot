from bs4 import BeautifulSoup
import re


with open('tmp.html', 'r', encoding="utf-8") as f:
    tmp = f.read()
soup = BeautifulSoup(tmp, 'lxml')
first_sorted = soup.find_all('div', class_='c')
for n in first_sorted:
    if n.find(text=re.compile(r'游戏内将开启「.+」活动')) is not None:
        try:
            print(n.text)
        except AttributeError as e:
            pass
