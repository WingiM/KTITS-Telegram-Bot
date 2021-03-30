import os
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters


bot = Bot(os.getenv("BOT_TOKEN"))


def start(update, context):
    update.message.reply_text('Здравствуйте!')
    if not link_checker(update, context):
        update.message.reply_text('Для привязки аккаунта используйте /link')


def link_checker(update, context):
    print(os.getcwd())
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    admins = cursor.execute("""SELECT * FROM users WHERE chat_id = ?""", (update.message.from_user['id'], )).fetchall()
    print(admins)
    if not cursor.execute("""SELECT chat_id FROM admin_users WHERE chat_id = ?""", (update.message.from_user["id"], )).fetchone():
        return False
    return True


def link(update, context):
    if link_checker(update, context):
        update.message.reply_text('Ваш аккаунт уже привязан')
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
        return 1
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO admin_users VALUES(?)""", (update.message.from_user['id'], ))
    update.message.reply_text('Успешно привязали аккаунт.\nИспользуйте /send для отправки сообщений группам')
    return ConversationHandler.END


def message_send(update, context):
    if not link_checker(update, context):
        update.message.reply_text('Ваш аккаунт не привязан')
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Введите номер группы, которой вы хотите отпраить сообщение\n"
                              "Например: 120", reply_markup=key)
    return 1


def select_group(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    if not check_group(message):
        update.message.reply_text("Вы ввели неправильный номер группы")
        return 1
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Введите сообщение группе", reply_markup=key)
    context.user_data['to_group'] = message
    return 2


def message_to_group(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    current_group = context.user_data['to_group']
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    users = cursor.execute("""SELECT chat_id FROM users WHERE "group" = ? """, (current_group, )).fetchall()
    for i in users:
        bot.sendMessage(chat_id=i[0], text="Учебная часть:\n" + message)
    update.message.reply_text(f'Успешно отправили сообщение группе {context.user_data["to_group"]}', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def check_group(group):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if cursor.execute(""" SELECT * FROM groups WHERE number = ?""", (group,)).fetchone():
        return True
    return False


def leave(update, context):
    update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv("ADMIN_BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('link', link)],
        states={
            1: [MessageHandler(Filters.text, linker)]
        },
        fallbacks=[]
    ))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('send', message_send)],
        states={
            1: [MessageHandler(Filters.text, select_group, pass_user_data=True)],
            2: [MessageHandler(Filters.text, message_to_group, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))

    updater.start_polling()
    updater.idle()
