from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from Linker import Linker
from TimetablePasser import TimetablePasser


class UserInteractionBot(Updater):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linker = Linker()
        self.passer = TimetablePasser()

        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('unlink', self.linker.unlink_user))
        self.dispatcher.add_handler(CommandHandler('unlinkt', self.linker.unlink_teacher))
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('link', self.linker.start_user_linking)],
            states={
                1: [MessageHandler(Filters.text, self.linker.link_user)]
            },
            fallbacks=[]
        ))
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('linkt', self.linker.start_teacher_linking)],
            states={
                1: [MessageHandler(Filters.text, self.linker.link_teacher)]
            },
            fallbacks=[]
        ))
        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('get', self.passer.user_get)],
            states={
                1: [MessageHandler(Filters.text, self.passer.pass_timetable)]
            },
            fallbacks=[]
        ))

        self.dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('gett', self.passer.teacher_get)],
            states={
                1: [MessageHandler(Filters.text, self.passer.pass_timetable_teacher)]
            },
            fallbacks=[]
        ))

    @staticmethod
    def leave(update, _):
        update.message.reply_text('Хорошо, отменяем', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def execute(self):
        print("Bot successfully started")
        self.start_polling()
        self.idle()

    def start(self, update, context):
        update.message.reply_text(f'Здравствуй, {update.message.from_user["first_name"]}!')
        if not self.linker.check_link(update, context):
            update.message.reply_text('Ваш аккаунт не привязан к системе! Используйте /link, чтобы привязаться')
