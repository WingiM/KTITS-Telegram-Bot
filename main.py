from multiprocessing import Process
from tools import scheduler, bot, admin_bot

if __name__ == '__main__':
    p1 = Process(target=bot.main)
    p1.start()
    p2 = Process(target=scheduler.main)
    p2.start()
    p3 = Process(target=admin_bot.main)
    p3.start()

