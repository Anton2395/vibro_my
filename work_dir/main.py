import threading
import time
import datetime as _dt
import multiprocessing as mp
from app import run_flask
# from back_work_thread import Shetchik
from back_work_snap import StartProcessOpcForConnectToPLC
from back_work_modbus import ConnectModProcess, data


if __name__ == "__main__":
    name = "Thread #schet"
    # my = Shetchik(name)
    status_connec = mp.Value('i', 0)
    my = StartProcessOpcForConnectToPLC(status=status_connec)
    my.start()

    status_connec_mod = mp.Value('i', 0)
    stop_point_mod = mp.Value('i', 0)
    # test_mod = ConnectModProcess(name_connect='datchik', ip='185.6.25.165', port=501, status=status_connec_mod,
    #                              stop_point=stop_point_mod, values=data)
    # test_mod.start()
    my_flask = threading.Thread(target=run_flask)
    my_flask.start()
    while True:
        if not my.is_alive():
            print(_dt.datetime.now(), "----------- restart back")
            with open("logs.log", 'a') as file:
                file.write(_dt.datetime.now(), "restart back writer to db|||| snap")
            my.tirmenate()
            my.start()
            time.sleep(1)
        # if not test_mod.is_alive():
        #     print(_dt.datetime.now(), "----------- restart back")
        #     with open("logs.log", 'a') as file:
        #         file.write(_dt.datetime.now(), "restart back writer to db|||| mod")
        #     test_mod.terminate()
        #     test_mod.start()
        #     time.sleep(1)
        if not my_flask.is_alive():
            print(_dt.datetime.now(), "----------- restart flask")
            with open("logs.log", 'a') as file:
                file.write(_dt.datetime.now(), "restart flask")
            my_flask.tirmenate()
            my_flask.start()
            time.sleep(1)

