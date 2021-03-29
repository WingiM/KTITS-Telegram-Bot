import os
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters


bot = Bot(os.getenv("BOT_TOKEN"))


def start(update, context):
    update.message.reply_text('Здравствуйте!')


def message_send(update, context):
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
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Введите сообщение группе", reply_markup=key)
    context.user_data['locality'] = message
    return 2


def message_to_group(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    current_group = context.user_data['locality']
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    users = cursor.execute("""SELECT chat_id FROM users WHERE "group" = ? """, (current_group, )).fetchall()
    for i in users:
        bot.sendMessage(chat_id=i[0], text=message)
    return ConversationHandler.END


def check_group(group):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if cursor.execute(""" SELECT * FROM groups WHERE number = ?""", (group,)).fetchone():
        return True
    else:
        return False


def leave(update, context):
    update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv("ADMIN_BOT_TOKEN"), use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('message_send', message_send)],
        states={
            1: [MessageHandler(Filters.text, select_group, pass_user_data=True, pass_chat_data=True)],
            2: [MessageHandler(Filters.text, message_to_group, pass_user_data=True, pass_chat_data=True)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))

    updater.start_polling()
    updater.idle()
