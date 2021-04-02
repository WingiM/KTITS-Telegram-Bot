import os
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

bot = Bot(os.getenv("BOT_TOKEN"))


def start(update, context):
    update.message.reply_text('Здравствуйте!')
    markup = [['Привязать аккаунт']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True)
    if not link_checker(update, context):
        update.message.reply_text('Для привязки аккаунта используйте команду /link или кнопку.', reply_markup=key)
        return 1
    else:
        markup = [['Отправить сообщение группе']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Ваш аккаунт уже привязан', reply_markup=key)
        return 3


def link_checker(update, _):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if not cursor.execute("""SELECT chat_id FROM admin_users WHERE chat_id = ?""",
                          (update.message.from_user["id"],)).fetchone():
        return False
    return True


def link(update, context):
    message = update.message.text
    if link_checker(update, context):
        markup = [['Отправить сообщение группе']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('Ваш аккаунт уже привязан', reply_markup=key)
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Пожалуйста, введите пароль учебной части', reply_markup=key)
    return 2


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
    markup = [['Отправить сообщение'], ['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Успешно привязали аккаунт.\nИспользуйте команду '
                              '/send или кнопку для отправки сообщений группам',
                              reply_markup=key)
    return ConversationHandler.END


def message_send(update, context):
    if not link_checker(update, context):
        update.message.reply_text('Ваш аккаунт не привязан')
        return ConversationHandler.END
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)

    if message.lower() != "отправить сообщение группе":
        print(message.lower())
        update.message.reply_text("Вы ввели что-то не так!", reply_markup=None)
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        "Пожалуйста, введите номера групп, которым хотите отправить сообщение\n"
        "Например: 120 121 220", reply_markup=key)
    return 4


def select_group(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    groups = set(message.split(" "))
    for group in groups:
        if not check_group(group):
            groups.remove(group)
            update.message.reply_text("Вы ввели неправильный номер группы.")
    context.user_data['to_group'] = groups
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Введите сообщение группе", reply_markup=key)
    return 5


def message_to_group(update: Update, context):
    message = update.message.text if update.message.text else ''
    photo_passed = False
    if message and message.lower() == 'выйти':
        return leave(update, context)

    try:
        # files = InputMediaPhoto(update.message.photo, update.message.photo)
        # print(files)
        file = update.message.photo[0]
        print(update.message.photo)
        newFile = Bot(os.getenv("ADMIN_BOT_TOKEN")).get_file(file_id=file.file_id)
        newFile.download(custom_path="image_temp/file.png")
        photo_passed = True
    except IndexError:
        pass
    current_groups = context.user_data['to_group']
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    for group in current_groups:
        users = cursor.execute("""SELECT chat_id FROM users WHERE "group" = ? """, (group,)).fetchall()
        for user in users:
            if photo_passed:
                bot.sendPhoto(chat_id=user[0], photo=open("image_temp/file.png", 'rb'),
                              caption=("Учебная часть:\n" + update.message.caption)
                              if update.message.caption is not None else None)
            else:
                bot.sendMessage(chat_id=user[0], text="Учебная часть:\n" + message)
        update.message.reply_text(f'Успешно отправили сообщение группе {group}', reply_markup=ReplyKeyboardRemove())
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
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(Filters.text, link)],
            2: [MessageHandler(Filters.text, linker)],
            3: [MessageHandler(Filters.text, message_send)],
            4: [MessageHandler(Filters.text, select_group, pass_user_data=True)],
            5: [MessageHandler(Filters.text | Filters.photo | Filters.group, message_to_group, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))
    # dispatcher.add_handler(ConversationHandler(
    #     entry_points=[CommandHandler('send', message_send)],
    #     states={
    #         1: [MessageHandler(Filters.text, select_group, pass_user_data=True)],
    #         2: [MessageHandler(Filters.text | Filters.photo | Filters.group, message_to_group, pass_user_data=True)]
    #     },
    #     fallbacks=[CommandHandler('exit', leave)]
    # ))
    print('Admin bot successfully started')
    updater.start_polling()
    updater.idle()
