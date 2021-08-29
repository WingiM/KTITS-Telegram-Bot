import os
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters
from tools.Messenger import Messenger
from tools.Linker import Linker


def main():
    user_bot = AdminBot(os.getenv("ADMIN_BOT_TOKEN"), use_context=True)
    user_bot.execute()


class AdminBot(Updater):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linker = Linker()
        self.messenger = Messenger()

        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('link', self.linker.start_admin_linking)],
            states={
                1: [MessageHandler(Filters.text, self.linker.link_admin)]
            },
            fallbacks=[]
        ))
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('groups', self.messenger.start_group_messaging)],
            states={
                1: [MessageHandler(Filters.text, self.messenger.select_groups, pass_user_data=True)],
                2: [MessageHandler(Filters.text | Filters.photo, self.messenger.send_to_groups, pass_user_data=True)]
            },
            fallbacks=[]
        ))
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('courses', self.messenger.start_course_messaging)],
            states={
                1: [MessageHandler(Filters.text, self.messenger.select_courses, pass_user_data=True)],
                2: [MessageHandler(Filters.text | Filters.photo, self.messenger.send_to_courses, pass_user_data=True)]
            },
            fallbacks=[]
        ))

    def execute(self):
        print("Admin Bot successfully started")
        self.start_polling()
        self.idle()

    def start(self, update, context):
        update.message.reply_text('Здравствуйте!')
        if not self.linker.check_admin_link(update, context):
            update.message.reply_text('Для привязки аккаунта используйте команду /link или кнопку.')
