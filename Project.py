import requests
from bs4 import BeautifulSoup
import sqlite3

url = ['https://olympteka.ru/olymp/game/profile/50.html',\
       'https://olympteka.ru/olymp/game/profile/48.html',\
       'https://olympteka.ru/olymp/game/profile/46.html',\
       'https://olympteka.ru/olymp/game/profile/33.html',\
       'https://olympteka.ru/olymp/game/profile/34.html',\
       'https://olympteka.ru/olymp/game/profile/31.html']

        #Сочи-зимняя Олимпиада 2014
        #Ванкувер-зимняя Олимпиада 2010
        #Турин-зимняя Олимпиада 2006
        #Москва_летние Олимпиада 1980
        #Лос Анджелесе-летняя Олимпиада 1984
        #Монреаль-летняя Олимпиада 1976
              
def parser(url):
    rowdata = []; inf = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    country = soup.find_all('font', itemprop="name")
    country = country[0].get_text()
    country = (country.split(':')[1])[1:]
    quotes = soup.find_all(class_ = "main-tb tb-medals")
    for quote in quotes:
        rowdata.append(quote.text)
    for i in rowdata:
        inf.append(i.split())
    print(1,inf)
    inf = inf[0]
    inf[0] = 'Место'
    if 'Северная' in inf:
        change = inf.index('Северная')
        inf[change] = str(inf[change - 1] + ' ' + inf[change])
        inf.pop(change - 1), inf.pop(change)
    if 'Южная' in inf:
        change = inf.index('Южная')
        inf[change - 1] = str(inf[change - 1] + ' ' + inf[change])
        inf.pop(change)
    if 'Новая' in inf:
        change = inf.index('Новая')
        inf[change] = str(inf[change] + ' ' + inf[change + 1])
        inf.pop(change + 1)
    if 'Тайвань' in inf:
        change = inf.index('Тайвань')
        inf.pop(change + 1)
        inf.pop(change + 1)
    if 'Бермудские' in inf:
        change = inf.index('Бермудские')
        inf[change] = str(inf[change] + ' ' + inf[change + 1])
        inf.pop(change + 1)
    if 'Тринидад' in inf:
        change = inf.index('Тринидад')
        inf[change] = str(inf[change] + ' ' + inf[change + 1] + ' ' + inf[change + 2])
        inf.pop(change + 1)
        inf.pop(change + 1)

    change = inf.index('Всего', 8)
    inf[change] = str(inf[change] + ' ' + inf[change + 1])
    inf[change + 1] = ' '

    inf = inf[0:-6]
    return inf, country

def create(olymp_name):
    con = sqlite3.connect("olymp.db")
    cur = con.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS '{olymp_name}' ("
                f"Место INT NOT NULL,"
                f"Страна TEXT NOT NULL,"
                f"Золото FLOAT NOT NULL,"
                f"Серебро FLOAT NOT NULL,"
                f"Бронза FLOAT NOT NULL"
                f")")
    con.commit()
    con.close()

def insert(inf, olymp_name):
    print(inf, olymp_name)
    for i in range(6, len(inf), 6):
        print(inf[i], inf[i + 1], inf[i + 2], inf[i + 3], inf[i + 4])
        con = sqlite3.connect("olymp.db")
        cur = con.cursor()
        cur.execute(f"INSERT INTO '{olymp_name}' ("
                    f"Место, Страна, Золото, Серебро, Бронза) VALUES (?, ?, ?, ?, ?);", [inf[i], inf[i + 1], inf[i + 2], \
                                                                                         inf[i + 3], inf[i + 4]])
        con.commit()
        con.close()

def count():
    first_country = ['', 0, 0, 0, 0]
    con = sqlite3.connect("olymp.db")
    cur = con.cursor()
    cur.execute("SELECT tbl_name FROM sqlite_master where type='table'")
    olymp_name = cur.fetchall()
    name = []
    for i in olymp_name:
        name.append(i[0])
    for j in name:
        cur.execute(f"SELECT count(*) from '{j}'")
        row_count = cur.fetchone()
        for i in range(row_count[0]-2, -1, -1):
            cur.execute(f"SELECT * FROM '{j}' ORDER BY Место LIMIT 1 OFFSET {i}")
            vtulka = cur.fetchall()
            vtulka = vtulka[0]
            cnt = vtulka[2]*7 + vtulka[3]*5 + vtulka[4]*4

            if cnt > first_country[1]:
                first_country = [vtulka[1], cnt, vtulka[2], vtulka[3], vtulka[4]]
            elif vtulka[2] > first_country[2]:
                first_country = [vtulka[1], cnt, vtulka[2], vtulka[3], vtulka[4]]

        print(f"{j}\nСтрана: {first_country[0]}\nОчки: {first_country[1]}\nЗолотые медали: {first_country[2]}\nСеребряные "
        f"медали: {first_country[3]}\nБронзовые медали: {first_country[4]}\n----------------------\n")

def max_medals():
    con = sqlite3.connect("olymp.db")
    cur = con.cursor()
    cur.execute("SELECT tbl_name FROM sqlite_master where type='table'")
    olymp_name = cur.fetchall()
    name = []
    for i in olymp_name:
        name.append(i[0])
    for j in name:
        print(f"{j}")
        for i in ['Золото', 'Серебро', 'Бронза']:
            cur.execute(f"SELECT Страна, {i} FROM '{j}' WHERE {i} in (SELECT MAX({i}) FROM '{j}')")
            inf = cur.fetchall()
            print(f"Самое большое количество медалей '{i}': {inf[0][0]} - {inf[0][1]}")
        print(f"----------------------\n")
mode = int(input('Выберете режим работы:\n1 - Создание таблицы и заполнение данных\n2 - Показать победителей\n3 - Максимальное количество медалей по категориям\n'))
if  mode == 1:
    for i in url:
        inf, olymp_name = parser(i)
        create(olymp_name)
        insert(inf, olymp_name)
elif mode == 2:
    count()
elif mode == 3:
    max_medals()
parser(url[1])
