import os
import sqlite3
import json
from dotenv import load_dotenv
from telegram import Bot

load_dotenv('.env')


def set_default_timetables(schedules:dict):
    """Устанавливает стандартные расписания по дням недели"""
    connection = sqlite3.connect('db/timetables.db')
    cur = connection.cursor()
    cur.execute("""DELETE FROM groups""")

    for group, weekday_schedules in schedules.items():
        cur.execute("""INSERT INTO groups VALUES (?)""", (group, ))
        for weekday, schedule in weekday_schedules.items():
            if cur.execute("""SELECT * FROM default_timetables_students WHERE weekday = ? AND "group" = ?""", (weekday, group)).fetchone():
                cur.execute("""UPDATE default_timetables_students SET schedule = ? 
                WHERE weekday = ? AND "group" = ?""", (schedule, weekday, group))
            else:
                cur.execute("""INSERT INTO default_timetables_students("group", weekday, schedule) VALUES (?, ?, ?)""", (group, weekday, schedule))
    connection.commit()


def mailing(text):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    bot = Bot(os.getenv('BOT_TOKEN'))
    for i in cursor.execute("""SELECT chat_id FROM users""").fetchall():
        bot.sendMessage(chat_id=i[0], text=text)

