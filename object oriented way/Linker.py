import sqlite3
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler


class Linker:
    @staticmethod
    def leave(update, _):
        update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    @staticmethod
    def check_link(update, _):
        connection = sqlite3.connect('timetables.sqlite')
        cursor = connection.cursor()
        if not cursor.execute("""SELECT "group" FROM users WHERE user_id = ?""",
                              (update.message.from_user['id'],)).fetchone():
            return False
        username = cursor.execute("""SELECT username FROM users WHERE user_id = ?""",
                                  (update.message.from_user['id'],)).fetchone()
        if username[0] != update.message.from_user['username']:
            cursor.execute("""UPDATE users SET username = ? WHERE user_id = ?""",
                           (update.message.from_user['username'], update.message.from_user['id']))
            connection.commit()
        return True

    @staticmethod
    def check_teacher_link(update, _):
        connection = sqlite3.connect('timetables.sqlite')
        cursor = connection.cursor()
        if not cursor.execute("""SELECT name FROM teacher_users WHERE chat_id = ?""",
                              (update.message.from_user['id'],)).fetchone():
            return False
        return True

    def start_user_linking(self, update, context):
        if self.check_link(update, context):
            update.message.reply_text('Ваш аккаунт уже привязан к системе!', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        markup = [['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(
            'Пожалуйста, введите ваш номер группы', reply_markup=key)
        return 1

    def link_user(self, update, context):
        message = update.message.text
        if message.lower() == 'выйти':
            return self.leave(update, context)
        if not message.isdigit():
            update.message.reply_text('Вы ввели не номер группы!')
            return 1
        connection = sqlite3.connect('timetables.sqlite')
        cursor = connection.cursor()
        if not cursor.execute("""SELECT * FROM groups WHERE number = ?""", (message,)).fetchone():
            update.message.reply_text('Такой группы не существует!')
            return 1
        chat_id = update.message.from_user['id']
        username = update.message.from_user['username']
        if cursor.execute("""SELECT * FROM users WHERE user_id = ?""", (chat_id,)).fetchone():
            update.message.reply_text('Ваш аккаунт уже привязан к системе!', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        cursor.execute("""INSERT INTO users VALUES (?, ?, ?)""", (chat_id, message, username))
        connection.commit()
        update.message.reply_text('Вы успешно подключили ваш аккаунт!', reply_markup=ReplyKeyboardRemove())
        update.message.reply_text('Теперь вы можете использовать команду /get для того, чтобы получить расписание\n'
                                  'Чтобы отвязаться можете использовать /unlink')
        return ConversationHandler.END

    def start_teacher_linking(self, update, context):
        if self.check_teacher_link(update, context):
            update.message.reply_text('Ваш аккаунт уже привязан к системе', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        markup = [['Выйти']]
        key = ReplyKeyboardMarkup(markup, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(
            'Пожалуйста, введите вашу фамилию и инициалы с точками через пробел (Садыкова Н.А.)', reply_markup=key)
        return 1

    def link_teacher(self, update, context):
        message = update.message.text
        if message.lower() == 'выйти':
            return self.leave(update, context)
        connection = sqlite3.connect('timetables.sqlite')
        cursor = connection.cursor()
        if not cursor.execute("""SELECT * FROM teachers WHERE name = ?""", (message,)).fetchone():
            update.message.reply_text('Такой фамилии и инициалов в базе данных нет.')
            return 1
        chat_id = update.message.from_user['id']
        if cursor.execute("""SELECT * FROM teacher_users WHERE chat_id = ?""", (chat_id,)).fetchone():
            update.message.reply_text('Ваш аккаунт уже привязан к системе!', reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        cursor.execute("""INSERT INTO teacher_users VALUES (?, ?)""", (chat_id, message))
        connection.commit()
        update.message.reply_text('Вы успешно подключили ваш аккаунт!', reply_markup=ReplyKeyboardRemove())
        update.message.reply_text('Теперь вы можете использовать команду /gett для того, чтобы получить расписание\n'
                                  'Чтобы отвязаться можете использовать /unlinkt')
        return ConversationHandler.END

    def unlink_user(self, update, context):
        if self.check_link(update, context):
            connection = sqlite3.connect('timetables.sqlite')
            cursor = connection.cursor()
            cursor.execute("""DELETE FROM users WHERE user_id =  ?""", (update.message.from_user['id'],))
            connection.commit()
            update.message.reply_text('Успешно отвязали ваш аккаунт', reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text('Ваш аккаунт и так не привязан ни к одной из групп',
                                      reply_markup=ReplyKeyboardRemove())

    def unlink_teacher(self, update, context):
        if self.check_teacher_link(update, context):
            connection = sqlite3.connect('timetables.sqlite')
            cursor = connection.cursor()
            cursor.execute("""DELETE FROM teacher_users WHERE chat_id =  ?""", (update.message.from_user['id'],))
            connection.commit()
            update.message.reply_text('Успешно отвязали ваш аккаунт', reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text('Ваш аккаунт и так не привязан', reply_markup=ReplyKeyboardRemove())
