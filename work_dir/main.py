import threading
import time
import datetime as _dt

from app import run_flask
from back_work_thread import Shetchik



if __name__ == "__main__":
    name = "Thread #schet"
    my = Shetchik(name)
    my.start()
    my_flask = threading.Thread(target=run_flask)
    my_flask.start()
    while True:
        if not my.is_alive():
            print(_dt.datetime.now(), "----------- restart back")
            with open("logs.log", 'a') as file:
                file.write(_dt.datetime.now(), "restart back writer to db")
            my.tirmenate()
            my.start()
            time.sleep(1)
        if not my_flask.is_alive():
            print(_dt.datetime.now(), "----------- restart flask")
            with open("logs.log", 'a') as file:
                file.write(_dt.datetime.now(), "restart flask")
            my_flask.tirmenate()
            my_flask.start()
            time.sleep(1)

