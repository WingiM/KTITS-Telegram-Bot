import datetime
import schedule
from bs4 import BeautifulSoup
from requests import get
from tools import excel
from tools.db_dispatcher import *

URL = 'https://www.mck-ktits.ru/'


def parse():
    print(f'Начинаем парс {datetime.datetime.now()}')
    html = get(URL).content.decode('utf-8')
    parser = BeautifulSoup(html, 'html.parser')
    schedules = parser.find('div', class_='schedule__item schedule__class')
    href = schedules.find_all('a')
    for number, link in enumerate(href, start=1):
        response = get(URL + link.get('href').rstrip('/'))
        with open(f'workbooks/rasp{number}.xlsx', 'wb') as file:
            file.write(response.content)
    with open('db/log.txt', 'a') as file:
        file.write(str(datetime.datetime.now()) + '\n')

    groups_schedule, teachers_schedule = excel.main()
    set_default_timetables(groups_schedule)
    set_default_timetables_teachers(teachers_schedule)

    check_temporary_timetables()
    if temp_timetables := excel.main(temp=True):
        groups_schedule_temp, teachers_schedule_temp, dates = temp_timetables
        set_temporary_timetables_students(groups_schedule_temp, dates)
        set_temporary_timetables_teachers(teachers_schedule_temp, dates)

    print(f'Парс окончен {datetime.datetime.now()}')


def main():
    parse()
    print('URL parser successfully started')
    schedule.every(1).day.at("04:00").do(parse)

    while True:
        schedule.run_pending()
