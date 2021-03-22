import os
import datetime
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from dotenv import load_dotenv

load_dotenv('.env')
WEEKDAYS = {
    'Понедельник': 0,
    'Вторник': 1,
    'Среда': 2,
    'Четверг': 3,
    'Пятница': 4,
    'Суббота': 5,
    'Воскресенье': 6
}


def start(update, context):
    update.message.reply_text(f'Здравствуй, {update.message.from_user["username"]}!')


def daily_timetable_start(update, context):
    markup = [['Назад']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        'Введите номер группы и день недели (120 Понедельник)\n\n'
        'Либо номер группы и дату, для получения расписания с учетом временных изменений (120 23 03 2021)',
        reply_markup=key)
    return 1


def get_daily_timetable(update, context):
    try:
        message = update.message.text
        if message == 'Назад':
            update.message.reply_text('Возвращаемся назад', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        connection = sqlite3.connect('db/timetables.db')
        cursor = connection.cursor()
        message = message.split()
        if len(message) == 2:
            group = int(message[0])
            weekday = WEEKDAYS[message[1].capitalize()]
            schedule = cursor.execute("""SELECT schedule FROM default_timetables_students 
                                                    WHERE "group" = ? AND weekday = ?""", (group, weekday)).fetchone()
            update.message.reply_text(schedule[0], reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        elif len(message) == 4:
            group, day, month, year = map(int, message)
            date = datetime.date(year, month, day)
            schedule = cursor.execute("""SELECT schedule FROM temp_timetables_students 
                                        WHERE "group" = ? AND date = ?""", (group, date)).fetchone()
            update.message.reply_text(schedule, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        raise KeyError

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
