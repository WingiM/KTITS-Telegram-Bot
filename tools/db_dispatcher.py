import os
import sqlite3
import json
from dotenv import load_dotenv
from telegram import Bot

load_dotenv('.env')


def set_default_timetables(file):
    """Устанавливает стандартные расписания по дням недели"""
    file = json.load(file)
    groups = file['groups']
    connection = sqlite3.connect('db/timetables.db')
    cur = connection.cursor()

    for group, weekdays in groups.items():
        for weekday, schedule in weekdays.items():
            if not cur.execute("""SELECT * FROM default_timetables_students WHERE "group" = ? AND weekday = ?""",
                               (group, weekday)).fetchall():
                cur.execute("""INSERT INTO default_timetables_students("group", weekday, schedule) VALUES (?, ?, ?)""",
                            (group, weekday, schedule))
                continue
            cur.execute("""UPDATE default_timetables_students SET schedule = ? WHERE weekday = ? AND "group" = ?""",
                        (schedule, weekday, group))
    connection.commit()


def mailing(text):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    bot = Bot(os.getenv('BOT_TOKEN'))
    for i in cursor.execute("""SELECT chat_id FROM users""").fetchall():
        bot.sendMessage(chat_id=i[0], text=text)

