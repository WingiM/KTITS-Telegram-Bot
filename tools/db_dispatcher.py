import datetime
import os
import sqlite3
from dotenv import load_dotenv
from telegram import Bot

load_dotenv('.env')


def set_default_timetables(schedules: dict):
    connection = sqlite3.connect('db/timetables.db')
    cur = connection.cursor()
    cur.execute("""DELETE FROM groups""")

    for group, weekday_schedules in schedules.items():
        cur.execute("""INSERT INTO groups VALUES (?)""", (group,))
        for weekday, schedule in weekday_schedules.items():
            if cur.execute("""SELECT * FROM default_timetables_students WHERE weekday = ? AND "group" = ?""",
                           (weekday, group)).fetchone():
                cur.execute("""UPDATE default_timetables_students SET schedule = ? 
                WHERE weekday = ? AND "group" = ?""", (schedule, weekday, group))
            else:
                cur.execute("""INSERT INTO default_timetables_students("group", weekday, schedule) VALUES (?, ?, ?)""",
                            (group, weekday, schedule))
    connection.commit()


def set_default_timetables_teachers(schedules: dict):
    connection = sqlite3.connect('db/timetables.db')
    cur = connection.cursor()
    cur.execute("""DELETE FROM teachers""")

    for name, weekday_schedules in schedules.items():
        cur.execute("""INSERT INTO teachers VALUES (?)""", (name,))
        for weekday, schedule in weekday_schedules.items():
            schedule = '\n'.join(sorted(schedule, key=lambda x: int(x.split(':')[0][1:])))
            if cur.execute("""SELECT * FROM default_timetables_teachers WHERE weekday = ? AND name = ?""",
                           (weekday, name)).fetchone():
                cur.execute("""UPDATE default_timetables_teachers SET schedule = ? WHERE weekday = ? AND name = ?""",
                            (schedule, weekday, name))
            else:
                cur.execute("""INSERT INTO default_timetables_teachers(name, weekday, schedule) VALUES (?, ?, ?)""",
                            (name, weekday, schedule))
    connection.commit()


def check_temporary_timetables():
    connection = sqlite3.connect('db/timetables.db')
    cur = connection.cursor()
    dates = cur.execute("""SELECT DISTINCT date FROM temporary_timetables_students""").fetchall()
    closest_date = list(map(lambda x: datetime.date(*map(int, x[0].split('-'))), dates))
    try:
        if (max(closest_date) - datetime.date.today()).days < 0:
            cur.execute("""DELETE FROM temporary_timetables_students""")
            cur.execute("""DELETE FROM temporary_timetables_teachers""")
        connection.commit()
    except ValueError:
        return


def set_temporary_timetables_students(schedules: dict, dates: list):
    connection = sqlite3.connect('db/timetables.db')
    cur = connection.cursor()

    for group, weekday_schedules in schedules.items():
        for weekday, schedule in weekday_schedules.items():
            if cur.execute("""SELECT * FROM temporary_timetables_students WHERE weekday = ? AND "group" = ?""",
                           (weekday, group)).fetchone():
                cur.execute(
                    """UPDATE temporary_timetables_students SET schedule = ?, date = ? 
                    WHERE weekday = ? AND "group" = ?""", (schedule, dates[weekday], weekday, group))
            else:
                cur.execute(
                    """INSERT INTO temporary_timetables_students(weekday, date, schedule, "group") 
                    VALUES (?, ?, ?, ?)""", (weekday, dates[weekday], schedule, group))
    connection.commit()


def set_temporary_timetables_teachers(schedules: dict, dates: list):
    connection = sqlite3.connect('db/timetables.db')
    cur = connection.cursor()

    for name, weekday_schedules in schedules.items():
        for weekday, schedule in weekday_schedules.items():
            schedule = '\n'.join(sorted(schedule, key=lambda x: int(x.split(':')[0][1:])))
            if cur.execute("""SELECT * FROM temporary_timetables_teachers WHERE weekday = ? AND name = ?""",
                           (weekday, name)).fetchone():
                cur.execute(
                    """UPDATE temporary_timetables_teachers SET schedule = ?, date = ? 
                    WHERE weekday = ? AND name = ?""", (schedule, dates[weekday], weekday, name))
            else:
                cur.execute(
                    """INSERT INTO temporary_timetables_teachers(name, weekday, date, schedule) VALUES (?, ?, ?, ?)""",
                    (name, weekday, dates[weekday], schedule))
    connection.commit()


# def notify():
#     bot = Bot(os.getenv("BOT_TOKEN"))
#     connection = sqlite3.connect('db/timetables.db')
#     cursor = connection.cursor()
#     users = cursor.execute("""SELECT chat_id FROM users""").fetchall() + cursor.execute(
#         """SELECT chat_id FROM teacher_users""").fetchall()
#     for user in users:
#         bot.sendMessage(chat_id=user[0], text="ВНИМАНИЕ!!!\nПоявилось запланированное изменение в расписании.")
