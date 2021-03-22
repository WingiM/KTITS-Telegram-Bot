import sqlite3
import json

connection = sqlite3.connect('../db/timetables.db')


def set_default_timetables(file):
    """Устанавливает стандартные расписания по дням недели"""
    file = json.load(file)
    groups = file['groups']
    teachers = file['teachers']
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

    for teacher, weekdays in teachers.items():
        for weekday, schedule in weekdays.items():
            if not cur.execute("""SELECT * FROM default_timetables_teachers WHERE weekday = ? AND teacher_name = ?""",
                               (weekday, teacher)).fetchall():
                cur.execute(
                    """INSERT INTO default_timetables_teachers(teacher_name, weekday, schedule) VALUES (?, ?, ?)""",
                    (teacher, weekday, schedule))
                continue
            cur.execute("""UPDATE default_timetables_teachers SET schedule = ? WHERE teacher_name = ? AND weekday = ?""",
                        (schedule, teacher, weekday))

    connection.commit()


set_default_timetables(open('../test.json', encoding='utf8'))

