from bs4 import BeautifulSoup


with open('tmp.html', 'r', encoding="utf-8") as f:
    tmp = f.read()
soup = BeautifulSoup(tmp, 'lxml')
blog_ini = soup.find_all('div', class_='c')
for n in blog_ini:
    content = n.find('span', class_='ctt')
    try:
        print(content.text)
    except AttributeError as e:
        pass
