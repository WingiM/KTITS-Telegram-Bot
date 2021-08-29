import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from tools.Linker import Linker
from tools.globals import WEEKDAYS


class TimetablePasser:
    @staticmethod
    def leave(update, _):
        update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def check_input(self, update, context) -> bool:
        message = update.message.text
        if message.lower() == 'выйти':
            return self.leave(update, context)
        if message.lower() not in [i.lower() for i in list(WEEKDAYS.keys())]:
            update.message.reply_text('Это не день недели!')
            return True
        if message.lower() == 'воскресенье':
            update.message.reply_text('В воскресенье мы не учимся')
            return True
        return False

    def user_get(self, update, context):
        if not Linker.check_link(update, context):
            update.message.reply_text('Ваш аккаунт не привязан к системе! Используйте /link, чтобы привязаться')
            return ConversationHandler.END
        markup = [['Понедельник', 'Четверг'], ['Вторник', "Пятница"], ["Среда", "Суббота"], ['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text('Выберите день недели', reply_markup=key)
        return 1

    def pass_timetable(self, update, context):
        if self.check_input(update, context):
            return 1
        message = update.message.text
        connection = sqlite3.connect('db/timetables.sqlite')
        cursor = connection.cursor()
        weekday = WEEKDAYS[message.capitalize()]
        group = cursor.execute("""SELECT "group" FROM users 
            WHERE user_id = ?""", (update.message.from_user['id'],)).fetchone()[0]
        try:
            timetable = cursor.execute(
                """SELECT date, schedule FROM temporary_timetables_students 
                WHERE "group" = ? AND weekday = ?""", (group, weekday)).fetchone()
            message = f'{message} {timetable[0]}'
            timetable = timetable[1]
            update.message.reply_text(message)
        except TypeError:
            timetable = cursor.execute("""SELECT schedule FROM default_timetables_students 
                WHERE "group" = ? AND weekday = ?""", (group, weekday)).fetchone()[0]
        update.message.reply_text(f'{timetable}')
        return 1

    def teacher_get(self, update, context):
        if not Linker.check_teacher_link(update, context):
            update.message.reply_text('Ваш аккаунт не привязан к системе! Используйте /linkt, чтобы привязаться')
            return ConversationHandler.END
        markup = [['Понедельник', 'Четверг'], ['Вторник', "Пятница"], ["Среда", "Суббота"], ['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text('Выберите день недели', reply_markup=key)
        return 1

    def pass_timetable_teacher(self, update, context):
        if self.check_input(update, context):
            return 1
        message = update.message.text
        connection = sqlite3.connect('db/timetables.sqlite')
        cursor = connection.cursor()
        weekday = WEEKDAYS[message.capitalize()]
        name = cursor.execute("""SELECT name FROM teacher_users 
                WHERE chat_id = ?""", (update.message.from_user['id'],)).fetchone()[0]
        try:
            timetable = cursor.execute(
                """SELECT date, schedule FROM temporary_timetables_teachers 
                WHERE name = ? AND weekday = ?""", (name, weekday)).fetchone()
            message = f'{message} {timetable[0]}'
            timetable = timetable[1]
            update.message.reply_text(message)
        except TypeError:
            timetable = cursor.execute("""SELECT schedule FROM default_timetables_teachers 
                WHERE name = ? AND weekday = ?""", (name, weekday)).fetchone()
            if not timetable:
                update.message.reply_text('Повезло! В этот день у вас нет пар!')
                return 1
            timetable = timetable[0]
        update.message.reply_text(f'{timetable}')
        return 1
