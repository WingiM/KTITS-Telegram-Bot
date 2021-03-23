import datetime

import schedule
from bs4 import BeautifulSoup
from requests import get

URL = 'https://www.mck-ktits.ru/'


def parse():
    html = get(URL).content.decode('utf-8')
    parser = BeautifulSoup(html, 'html.parser')
    schedules = parser.find('div', class_='schedule__item schedule__class')
    href = schedules.find_all('a')
    for number, link in enumerate(href, start=1):
        response = get(URL + link.get('href').rstrip('/'))
        with open(f'../workbooks/rasp{number}.xlsx', 'wb') as file:
            file.write(response.content)
    with open('../db/log.txt', 'a') as file:
        file.write(str(datetime.datetime.now()) + '\n')


def main():
    print('URL parser successfully started')
    schedule.every(1).day.at("00:00").do(parse)

    while True:
        schedule.run_pending()