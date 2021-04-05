import os
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

bot = Bot(os.getenv("BOT_TOKEN"))


def link_checker(update, _):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if not cursor.execute("""SELECT chat_id FROM admin_users WHERE chat_id = ?""",
                          (update.message.from_user["id"],)).fetchone():
        return False
    return True


def start(update, context):
    update.message.reply_text('Здравствуйте!')
    if not link_checker(update, context):
        update.message.reply_text('Для привязки аккаунта используйте команду /link или кнопку.')


def link(update, context):
    if link_checker(update, context):
        update.message.reply_text('Ваш аккаунт уже привязан', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
    update.message.reply_text('Пожалуйста, введите пароль учебной части', reply_markup=key)
    return 1


def linker(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    if message != os.getenv("ADMIN_PASSWORD"):
        update.message.reply_text('Пароль неверный')
        return 2
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO admin_users VALUES(?)""", (update.message.from_user['id'],))
    connection.commit()
    update.message.reply_text('Успешно привязали аккаунт.')
    return ConversationHandler.END


def message_groups(update, context):
    if not link_checker(update, context):
        update.message.reply_text('Ваш аккаунт не привязан! Используйте /link')
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
    update.message.reply_text('Укажите номер(а) групп(ы)\nНапример: 102 103 111 120', reply_markup=key)
    return 1


def select_groups(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    group_list = set(message.split())
    to_del = set()
    for group in group_list:
        if not check_group(group):
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


def send_to_groups(update, context):
    message = update.message.text
    photo_passed = False
    if message and message.lower() == 'выйти':
        return leave(update, context)
    try:
        file = update.message.photo[-1]
        newFile = Bot(os.getenv("ADMIN_BOT_TOKEN")).get_file(file_id=file.file_id)
        newFile.download(custom_path="image_temp/file.png")
        photo_passed = True
    except IndexError:
        pass
    groups_list = context.user_data['to_groups']
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    for group in groups_list:
        users = cursor.execute("""SELECT chat_id FROM users WHERE "group" = ? """, (group,)).fetchall()
        for user in users:
            if photo_passed:
                bot.sendPhoto(chat_id=user[0], photo=open("image_temp/file.png", 'rb'),
                              caption=("Учебная часть:\n" + update.message.caption)
                              if update.message.caption is not None else None)
            else:
                bot.sendMessage(chat_id=user[0], text="Учебная часть:\n" + message)
        update.message.reply_text(f'Успешно отправили сообщение группе {group}')
    update.message.reply_text("Рассылка закончена!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def message_courses(update, context):
    if not link_checker(update, context):
        update.message.reply_text('Ваш аккаунт не привязан! Используйте /link')
        return ConversationHandler.END
    markup = [['1 курс', "2 курс"], ['3 курс', '4 курс'], ["Всем"], ['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
    update.message.reply_text('Выберите курс', reply_markup=key)
    return 1


def select_courses(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
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


def send_to_courses(update, context):
    message = update.message.text
    photo_passed = False
    if message and message.lower() == 'выйти':
        return leave(update, context)
    try:
        file = update.message.photo[-1]
        newFile = Bot(os.getenv("ADMIN_BOT_TOKEN")).get_file(file_id=file.file_id)
        newFile.download(custom_path="image_temp/file.png")
        photo_passed = True
    except IndexError:
        pass
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    groups = context.user_data['to_course']
    for i in groups:
        users = cursor.execute("""SELECT chat_id FROM users WHERE "group" LIKE ? """,
                               (str(i) + "%",))
        for user in users:
            if photo_passed:
                bot.sendPhoto(chat_id=user[0], photo=open("image_temp/file.png", 'rb'),
                              caption=("Учебная часть:\n" + update.message.caption)
                              if update.message.caption is not None else None)
            else:
                bot.sendMessage(chat_id=user[0], text="Учебная часть:\n" + message)
        update.message.reply_text(f'Успешно отправили сообщение {str(i)} курсу',
                                  reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def check_group(group):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if cursor.execute(""" SELECT * FROM groups WHERE number = ?""", (group,)).fetchone():
        return True
    return False


def leave(update, _):
    update.message.reply_text('Хорошо, отменяем.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv("ADMIN_BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('link', link)],
        states={
            1: [MessageHandler(Filters.text, linker)]
        },
        fallbacks=[]
    ))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('groups', message_groups)],
        states={
            1: [MessageHandler(Filters.text, select_groups, pass_user_data=True)],
            2: [MessageHandler(Filters.text | Filters.photo, send_to_groups, pass_user_data=True)]
        },
        fallbacks=[]
    ))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('courses', message_courses)],
        states={
            1: [MessageHandler(Filters.text, select_courses, pass_user_data=True)],
            2: [MessageHandler(Filters.text | Filters.photo, send_to_courses, pass_user_data=True)]
        },
        fallbacks=[]
    ))

    print('Admin bot successfully started')
    updater.start_polling()
    updater.idle()
