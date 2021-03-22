import os
import datetime
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from dotenv import load_dotenv

load_dotenv('.env')


def start(update, context):
    update.message.reply_text(f'Здравствуй, {update.message.from_user["username"]}!')


def daily_timetable_start(update, context):
    markup = [['Назад']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Укажите номер группы и дату в формате NNN ДД ММ ГГГГ', reply_markup=key)
    return 1


def get_daily_timetable(update, context):
    try:
        message = update.message.text
        if message == 'Назад':
            update.message.reply_text('Возвращаемся назад', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        message = message.split()
        if len(message) != 4:
            raise KeyError
        group, day, month, year = map(int, message)
        date = datetime.date(year, month, day)
        days_delta = (date - datetime.date.today()).days
        if days_delta < 0:
            update.message.reply_text('Не могу вернуться в прошлое', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        if days_delta > 7:
            update.message.reply_text('Дальше недели не вижу', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        weekday = date.weekday()
        if weekday == 6:
            update.message.reply_text('В воскресенье не учимся', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        connection = sqlite3.connect('db/timetables.db')
        cursor = connection.cursor()
        schedule = cursor.execute("""SELECT schedule FROM default_timetables_students 
                                    WHERE "group" = ? AND weekday = ?""", (group, weekday)).fetchone()
        update.message.reply_text(schedule, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    except (KeyError, ValueError):
        update.message.reply_text('Некорректный запрос', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


def leave(update, context):
    update.message.reply_text('Ок')
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('day', daily_timetable_start)],
        states={
            1: [MessageHandler(Filters.text, get_daily_timetable)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
