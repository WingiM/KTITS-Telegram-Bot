import os
import sqlite3
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
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
    update.message.reply_text(f'Здравствуй, {update.message.from_user["first_name"]}!')
    if not link_checker(update, context):
        update.message.reply_text('Ваш аккаунт не привязан к системе! Используйте /link, чтобы привязаться')


#
# def daily_student_timetable_start(update, context):
#     markup = [['Назад']]
#     key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
#     update.message.reply_text(
#         'Введите номер группы и день недели (120 Понедельник)\n\n'
#         'Либо номер группы и дату, для получения расписания с учетом временных изменений (120 23 03 2021)',
#         reply_markup=key)
#     return 1
#
#
# def get_daily_student_timetable(update, context):
#     try:
#         message = update.message.text
#         if message == 'Назад':
#             update.message.reply_text('Возвращаемся назад', reply_markup=ReplyKeyboardRemove())
#             return ConversationHandler.END
#         connection = sqlite3.connect('db/timetables.db')
#         cursor = connection.cursor()
#         message = message.split()
#         if len(message) == 2:
#             group = int(message[0])
#             weekday = WEEKDAYS[message[1].capitalize()]
#             schedule = cursor.execute("""SELECT schedule FROM default_timetables_students
#                                                     WHERE "group" = ? AND weekday = ?""", (group, weekday)).fetchone()
#             update.message.reply_text(schedule[0], reply_markup=ReplyKeyboardRemove())
#             return ConversationHandler.END
#         elif len(message) == 4:
#             group, day, month, year = map(int, message)
#             date = datetime.date(year, month, day)
#             schedule = cursor.execute("""SELECT schedule FROM temp_timetables_students
#                                         WHERE "group" = ? AND date = ?""", (group, date)).fetchone()
#             update.message.reply_text(schedule, reply_markup=ReplyKeyboardRemove())
#             return ConversationHandler.END
#         raise KeyError
#
#     except (KeyError, ValueError):
#         update.message.reply_text('Некорректный запрос', reply_markup=ReplyKeyboardRemove())
#         return ConversationHandler.END
#
#
# def daily_teacher_timetable_start(update, context):
#     markup = [['Назад']]
#     key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
#     update.message.reply_text(
#         'Введите вашу фамилию и инициалы и день недели (Садыкова Н.А. Понедельник)\n\n'
#         'Либо фамилию, инициалы и дату, для получения расписания '
#         'с учетом временных изменений (Садыкова Н.А. 23 03 2021)',
#         reply_markup=key)
#     return 1
#
#
# def get_daily_teacher_timetable(update, context):  # TODO: доделать
#     try:
#         message = update.message.text
#         if message == 'Назад':
#             update.message.reply_text('Возвращаемся назад', reply_markup=ReplyKeyboardRemove())
#             return ConversationHandler.END
#         connection = sqlite3.connect('db/timetables.db')
#         cursor = connection.cursor()
#         message = message.split()
#         if len(message) == 2:
#             group = int(message[0])
#             weekday = WEEKDAYS[message[1].capitalize()]
#             schedule = cursor.execute("""SELECT schedule FROM default_timetables_students
#                                                     WHERE "group" = ? AND weekday = ?""", (group, weekday)).fetchone()
#             update.message.reply_text(schedule[0], reply_markup=ReplyKeyboardRemove())
#             return ConversationHandler.END
#         elif len(message) == 4:
#             group, day, month, year = map(int, message)
#             date = datetime.date(year, month, day)
#             schedule = cursor.execute("""SELECT schedule FROM temp_timetables_students
#                                         WHERE "group" = ? AND date = ?""", (group, date)).fetchone()
#             update.message.reply_text(schedule, reply_markup=ReplyKeyboardRemove())
#             return ConversationHandler.END
#         raise KeyError
#
#     except (KeyError, ValueError):
#         update.message.reply_text('Некорректный запрос', reply_markup=ReplyKeyboardRemove())
#         return ConversationHandler.END


def link_checker(update, context):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if not cursor.execute("""SELECT "group" FROM users WHERE chat_id = ?""",
                          (update.message.from_user['id'],)).fetchone():
        return False
    return True


def link(update, context):
    send()
    if link_checker(update, context):
        update.message.reply_text('Ваш аккаунт уже привязан к системе!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        'Пожалуйста, введите ваш номер группы\nВНИМАНИЕ: сменить группу после этого вы не сможете', reply_markup=key)
    return 1


def linker(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    if not message.isdigit():
        update.message.reply_text('Вы ввели не номер группы!')
        return 1
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if not cursor.execute("""SELECT * FROM groups WHERE number = ?""", (message,)).fetchone():
        update.message.reply_text('Такой группы не существует!')
        return 1
    chat_id = update.message.chat['id']
    if cursor.execute("""SELECT * FROM users WHERE chat_id = ?""", (chat_id,)).fetchone():
        update.message.reply_text('Ваш аккаунт уже привязан к системе!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    cursor.execute("""INSERT INTO users VALUES (?, ?)""", (chat_id, message))
    connection.commit()
    update.message.reply_text('Вы успешно подключили ваш аккаунт!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def leave(update, context):
    update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def text_processing(update, context):
    pass


def main():
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('link', link)],
        states={
            1: [MessageHandler(Filters.text, linker)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))
    dispatcher.add_handler(MessageHandler(Filters.text, text_processing))
    # dispatcher.add_handler(ConversationHandler(
    #     entry_points=[CommandHandler('day', daily_student_timetable_start)],
    #     states={
    #         1: [MessageHandler(Filters.text, get_daily_student_timetable)]
    #     },
    #     fallbacks=[]
    # ))
    # dispatcher.add_handler(ConversationHandler(
    #     entry_points=[CommandHandler('dayt', daily_teacher_timetable_start)],
    #     states={
    #         1: [MessageHandler(Filters.text, get_daily_teacher_timetable)]
    #     },
    #     fallbacks=[]
    # ))

    print('Bot successfully started')
    updater.start_polling()
    updater.idle()
