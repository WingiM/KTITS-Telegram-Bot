import multiprocessing
from dotenv import load_dotenv
from tools import AdminBot, UserInteractionBot

if __name__ == '__main__':
    load_dotenv('.env')
    p1 = multiprocessing.Process(target=UserInteractionBot.main)
    p1.start()
    p2 = multiprocessing.Process(target=AdminBot.main)
    p2.start()
