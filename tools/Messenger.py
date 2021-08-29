import os
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, error
from telegram.ext import ConversationHandler
from tools.Linker import Linker


class Messenger:
    def __init__(self):
        self.bot = Bot(os.getenv("BOT_TOKEN"))

    @staticmethod
    def leave(update, _):
        update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    @staticmethod
    def check_group(group):
        connection = sqlite3.connect('db/timetables.sqlite')
        cursor = connection.cursor()
        if cursor.execute(""" SELECT * FROM groups WHERE number = ?""", (group,)).fetchone():
            return True
        return False

    def start_group_messaging(self, update, context):
        if not Linker.check_admin_link(update, context):
            update.message.reply_text('Ваш аккаунт не привязан! Используйте /link')
            return ConversationHandler.END
        markup = [['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
        update.message.reply_text('Укажите номер(а) групп(ы)\nНапример: 102 103 111 120', reply_markup=key)
        return 1

    def select_groups(self, update, context):
        message = update.message.text
        if message.lower() == 'выйти':
            return self.leave(update, context)
        group_list = set(message.split())
        to_del = set()
        for group in group_list:
            if not self.check_group(group):
                to_del.add(group)
                update.message.reply_text(f'Группы {group} не существует')
        group_list = group_list - to_del
        if not group_list:
            update.message.reply_text('Среди введенный групп нет ни одной верной, введите заново!')
            return 1
        context.user_data['to_groups'] = group_list
        markup = [['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
        update.message.reply_text('Введите сообщение, которое хотите отправить', reply_markup=key)
        return 2

    def send_to_groups(self, update, context):
        message = update.message.text
        photo_passed = False
        if message and message.lower() == 'выйти':
            return self.leave(update, context)
        try:
            file = update.message.photo[-1]
            newFile = Bot(os.getenv("ADMIN_BOT_TOKEN")).get_file(file_id=file.file_id)
            newFile.download(custom_path="../image_temp/file.png")
            photo_passed = True
        except IndexError:
            pass
        groups_list = context.user_data['to_groups']
        connection = sqlite3.connect('db/timetables.sqlite')
        cursor = connection.cursor()
        for group in groups_list:
            users = cursor.execute("""SELECT user_id FROM users WHERE "group" = ? """, (group,)).fetchall()
            for user in users:
                try:
                    if photo_passed:
                        self.bot.sendPhoto(chat_id=user[0], photo=open("../image_temp/file.png", 'rb'),
                                           caption=("Учебная часть:\n" + update.message.caption)
                                      if update.message.caption is not None else None)
                    else:
                        self.bot.sendMessage(chat_id=user[0], text="Учебная часть:\n" + message)
                except error.Unauthorized:
                    cursor.execute("""DELETE FROM users WHERE user_id = ?""", (user[0],))
            update.message.reply_text(f'Успешно отправили сообщение группе {group}')
        update.message.reply_text("Рассылка закончена!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def start_course_messaging(self, update, context):
        if not Linker.check_admin_link(update, context):
            update.message.reply_text('Ваш аккаунт не привязан! Используйте /link')
            return ConversationHandler.END
        markup = [['1 курс', "2 курс"], ['3 курс', '4 курс'], ["Всем"], ['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
        update.message.reply_text('Выберите курс', reply_markup=key)
        return 1

    def select_courses(self, update, context):
        message = update.message.text
        if message.lower() == 'выйти':
            return self.leave(update, context)
        course = [message.split()[0]]
        if message.lower() == "всем":
            course = range(1, 5)
        try:
            if int(course[0]) not in range(1, 5):
                update.message.reply_text('Вы что-то ввели не так')
                return 1
        except ValueError:
            update.message.reply_text('Вы что-то ввели не так')
            return 1
        context.user_data['to_course'] = course
        markup = [['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
        update.message.reply_text('Введите сообщение, которое хотите отправить', reply_markup=key)
        return 2

    def send_to_courses(self, update, context):
        message = update.message.text
        photo_passed = False
        if message and message.lower() == 'выйти':
            return self.leave(update, context)
        try:
            file = update.message.photo[-1]
            newFile = Bot(os.getenv("ADMIN_BOT_TOKEN")).get_file(file_id=file.file_id)
            newFile.download(custom_path="../image_temp/file.png")
            photo_passed = True
        except IndexError:
            pass
        connection = sqlite3.connect('db/timetables.sqlite')
        cursor = connection.cursor()
        groups = context.user_data['to_course']
        for i in groups:
            users = cursor.execute("""SELECT user_id FROM users WHERE "group" LIKE ? """,
                                   (str(i) + "%",))
            for user in users:
                try:
                    if photo_passed:
                        self.bot.sendPhoto(chat_id=user[0], photo=open("../image_temp/file.png", 'rb'),
                                           caption=("Учебная часть:\n" + update.message.caption)
                                      if update.message.caption is not None else None)
                    else:
                        self.bot.sendMessage(chat_id=user[0], text="Учебная часть:\n" + message)
                except error.Unauthorized:
                    cursor.execute("""DELETE FROM users WHERE user_id = ?""", (user[0],))
            update.message.reply_text(f'Успешно отправили сообщение {str(i)} курсу')
        update.message.reply_text("Рассылка закончена!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
