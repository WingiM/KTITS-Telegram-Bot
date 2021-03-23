from multiprocessing import Process
from tools import url_parser, bot

if __name__ == '__main__':
    p1 = Process(target=bot.main)
    p1.start()
    p2 = Process(target=url_parser.main)
    p2.start()
