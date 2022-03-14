import time
import datetime as _dt
import traceback
from threading import Thread

import service as _service


class Shetchik(Thread):
    def __init__(self, name):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = name

    def run(self):
        while True:
            try:
                _service.downlod_and_add_to_db()
                print(_dt.datetime.now(), "   //////   write db done")
                time.sleep(20)
            except Exception as e:
                print(_dt.datetime.now(), "   //////   write db error")
                print(traceback.format_exc())
                print(e)
                with open("logs.log", 'a') as file:
                    file.write(f"{_dt.datetime.now()} ---------------------------------------------------------------------\n")
                    file.write(traceback.format_exc())
                    file.write(e)
                time.sleep(20)