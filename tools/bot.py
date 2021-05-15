import os
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
    update.message.reply_text(f'Здравствуй, {update.message.from_user["first_name"]}!')
    if not link_checker(update, context):
        update.message.reply_text('Ваш аккаунт не привязан к системе! Используйте /link, чтобы привязаться')


def link(update, context):
    if link_checker(update, context):
        update.message.reply_text('Ваш аккаунт уже привязан к системе!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        'Пожалуйста, введите ваш номер группы', reply_markup=key)
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
    update.message.reply_text('Теперь вы можете использовать команду /get для того, чтобы получить расписание\n'
                              'Чтобы отвязаться можете использовать /unlink')
    return ConversationHandler.END


def unlink(update, context):
    if link_checker(update, context):
        connection = sqlite3.connect('db/timetables.db')
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM users WHERE chat_id =  ?""", (update.message.from_user['id'],))
        connection.commit()
        update.message.reply_text('Успешно отвязали ваш аккаунт', reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Ваш аккаунт и так не привязан ни к одной из групп',
                                  reply_markup=ReplyKeyboardRemove())


def linkt(update, context):
    if link_checker_t(update, context):
        update.message.reply_text('Ваш аккаунт уже привязан к системе', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    markup = [['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        'Пожалуйста, введите вашу фамилию и инициалы с точками через пробел (Садыкова Н.А.)', reply_markup=key)
    return 1


def linkert(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if not cursor.execute("""SELECT * FROM teachers WHERE name = ?""", (message,)).fetchone():
        update.message.reply_text('Такой фамилии и инициалов в базе данных нет.')
        return 1
    chat_id = update.message.chat['id']
    if cursor.execute("""SELECT * FROM teacher_users WHERE chat_id = ?""", (chat_id,)).fetchone():
        update.message.reply_text('Ваш аккаунт уже привязан к системе!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    cursor.execute("""INSERT INTO teacher_users VALUES (?, ?)""", (chat_id, message))
    connection.commit()
    update.message.reply_text('Вы успешно подключили ваш аккаунт!', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Теперь вы можете использовать команду /gett для того, чтобы получить расписание\n'
                              'Чтобы отвязаться можете использовать /unlinkt')
    return ConversationHandler.END


def unlinkt(update, context):
    if link_checker_t(update, context):
        connection = sqlite3.connect('db/timetables.db')
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM teacher_users WHERE chat_id =  ?""", (update.message.from_user['id'],))
        connection.commit()
        update.message.reply_text('Успешно отвязали ваш аккаунт', reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text('Ваш аккаунт и так не привязан', reply_markup=ReplyKeyboardRemove())


def get(update, context):
    if not link_checker(update, context):
        update.message.reply_text('Ваш аккаунт не привязан к системе! Используйте /link, чтобы привязаться')
        return ConversationHandler.END
    markup = [['Понедельник', 'Четверг'], ['Вторник', "Пятница"], ["Среда", "Суббота"], ['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=False)
    update.message.reply_text('Выберите день недели', reply_markup=key)
    return 1


def get_timetable(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    if message.lower() not in [i.lower() for i in list(WEEKDAYS.keys())]:
        update.message.reply_text('Это не день недели!')
        return 1
    if message.lower() == 'воскресенье':
        update.message.reply_text('В воскресенье мы не учимся')
        return 1
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    weekday = WEEKDAYS[message]
    group = cursor.execute("""SELECT "group" FROM users 
    WHERE chat_id = ?""", (update.message.from_user['id'],)).fetchone()[0]
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


def gett(update, context):
    if not link_checker_t(update, context):
        update.message.reply_text('Ваш аккаунт не привязан к системе! Используйте /linkt, чтобы привязаться')
        return ConversationHandler.END
    markup = [['Понедельник', 'Четверг'], ['Вторник', "Пятница"], ["Среда", "Суббота"], ['Выйти']]
    key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=False)
    update.message.reply_text('Выберите день недели', reply_markup=key)
    return 1


def get_timetablet(update, context):
    message = update.message.text
    if message.lower() == 'выйти':
        return leave(update, context)
    if message.lower() not in [i.lower() for i in list(WEEKDAYS.keys())]:
        update.message.reply_text('Это не день недели!')
        return 1
    if message.lower() == 'воскресенье':
        update.message.reply_text('В воскресенье мы не учимся')
        return 1
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    weekday = WEEKDAYS[message]
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


def link_checker(update, _):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if not cursor.execute("""SELECT "group" FROM users WHERE chat_id = ?""",
                          (update.message.from_user['id'],)).fetchone():
        return False
    return True


def link_checker_t(update, _):
    connection = sqlite3.connect('db/timetables.db')
    cursor = connection.cursor()
    if not cursor.execute("""SELECT name FROM teacher_users WHERE chat_id = ?""",
                          (update.message.from_user['id'],)).fetchone():
        return False
    return True


def leave(update, _):
    update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('unlink', unlink))
    dispatcher.add_handler(CommandHandler('unlinkt', unlinkt))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('link', link)],
        states={
            1: [MessageHandler(Filters.text, linker)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('linkt', linkt)],
        states={
            1: [MessageHandler(Filters.text, linkert)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('get', get)],
        states={
            1: [MessageHandler(Filters.text, get_timetable)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))

    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler('gett', gett)],
        states={
            1: [MessageHandler(Filters.text, get_timetablet)]
        },
        fallbacks=[CommandHandler('exit', leave)]
    ))
    print('Bot successfully started')
    updater.start_polling()
    updater.idle()
