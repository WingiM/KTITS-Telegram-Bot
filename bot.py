import os
from telegram.ext import Updater
from dotenv import load_dotenv


load_dotenv('.env')


def main():
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


