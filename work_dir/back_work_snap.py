import datetime
import os
import struct
import threading
import time
from multiprocessing import Process
import multiprocessing as mp
import cprint
import snap7
from snap7.util import get_bool
import psycopg2
import json


def createConnection():
    return psycopg2.connect(dbname="db1", user="mvlab", password="z1x2c3", host="10.0.0.2")


class StartProcessOpcForConnectToPLC(Process):

    def __init__(self, status):
        """Класс процесса для подключения к ПЛК по адресу address, с портом port (по умолчанию 102) и получения заданных
        значений из блока данных db в промежутке с start_address_db по start_address_db+offset_db
        (offset_db - количество забираемых byte из блока). После получения данных разбирает bytearray по
        списку values_list.
        :param address: ip адрес ПЛК
        :param rack:  линейка ПЛК (смотри в Step7 или Tia POrtal)
        :param slot: номер слота ПЛК (смотри в Step7 или Tia POrtal)
        :param db: номер ДБ блока данных в ПЛК
        :param start_address_db: начальный адрес ДБ в ПЛК
        :param offset_db: количество читаемых байт в ДБ
        :param values_list: список значений которые нужно разобрать из bytearray в числовые
        :param port: номер порта (по умолчанию 102)
        :param name_connect: префикс названия таблиц для подключения
        """
        self.name_connect = "datchik"
        self.address = "185.6.25.165"
        self.status = status
        self.rack = 0
        self.slot = 1
        self.port = 102
        self.DB = 2
        self.start_address_DB = 0
        self.offset_DB = 8
        self.values_list = [{
            "name": "axel",
            "start": 0,
            "type": "real",
            "time_sleep": 2000,
            "if_change": True,
            "rewrite_time": 1
        },
        {
            "name": "temp",
            "start": 4,
            "type": "real",
            "time_sleep": 2000,
            "if_change": True,
            "rewrite_time": 1
        }
        ]
        self.bind = {}
        self.error_read_data = False
        self.last_error = ''
        self.bytearray_data = bytearray()
        self.values = {}
        self._conn = createConnection()
        self._c = self._conn.cursor()
        self.client = snap7.client.Client()
        self.client.set_connection_type(3)
        try:
            self.client.connect(self.address, self.rack, self.slot, tcpport=self.port)
        except:
            cprint.cprint.err("NotConnect to PLC")
        super(StartProcessOpcForConnectToPLC, self).__init__()

    def __get_db_data(self) -> bool:  # получение данных в байт формате
        """
        получение данных из ДБ блока в формате bytearray
        """
        try:
            self.bytearray_data = self.client.db_read(self.DB, self.start_address_DB, self.offset_DB)
            return True
        except Exception as e:
            self.last_error = str(e)
            self.error_read_data = True
            return False

    def __reconect_to_plc(self) -> bool:
        """пере подключение к плк в случае ошибки валидации данных"""
        cprint.cprint.warn("Connect to PLC %s" % self.address)
        self.client.destroy()
        try:
            self.client = snap7.client.Client()
            self.client.set_connection_type(3)
            self.client.connect(self.address, self.rack, self.slot, tcpport=self.port)
            cprint.cprint.info("Good connect to %s" % self.address)
            return True
        except:
            time.sleep(3)
            return False

    def __create_table_if_not_exist(self) -> None:
        """фнкция создания таблиц в БД"""
        
        self._c.execute('''CREATE TABLE IF NOT EXISTS datchik_5_temp \
                        (id serial primary key,temp_time BIGINT, \
                        temp REAL)''')
        self._conn.commit()
        self._c.execute('''CREATE TABLE IF NOT EXISTS datchik_5_axel \
                        (id serial primary key,axel_time BIGINT, \
                        axel REAL)''')
        self._conn.commit()

    def __parse_bytearray(self, data: dict) -> any:
        """разбор полученных данных с ПЛК"""
        type = data['type']
        start = data['start']
        if (type == 'int'):
            offset = 2
            end = int(start) + int(offset)
            result = self.disassemble_int(self.bytearray_data[int(start):int(end)])
            if data['divide']:
                if result > 65000:
                    result = 0
                else:
                    result = result / int(data['divide_number'])
        elif (type == 'real'):
            offset = 4
            end = int(start) + int(offset)
            result = self.disassemble_float(self.bytearray_data[int(start):int(end)])
        elif (type == 'double'):
            offset = 4
            end = int(start) + int(offset)
            result = self.disassemble_int(self.bytearray_data[int(start):int(end)])
        elif (type == 'bool'):
            if 'bit' in data['alarms']:
                bit = data['alarms']['bit']
                result = self.from_bytearray_to_bit(bit=bit, start=start)
            else:
                result = False
        else:
            result = False
        return result

    def __write_to_db(self, tablename, value):
        """Запись распаршеных данных в БД"""
        #ceil(extract(epoch from now()))
        if tablename == "temp":
            self._c.execute(
                '''INSERT INTO datchik_5_temp (temp_time, temp) VALUES (ceil(extract(epoch from now()))*1000, ''' + str(value) + ''');''')
        elif tablename == "axel":
            self._c.execute(
                '''INSERT INTO datchik_5_axel (axel_time, axel) VALUES (ceil(extract(epoch from now()))*1000, ''' + str(value) + ''');''')

    def _thread_for_write_data(self, d):
        value = self.__parse_bytearray(d)
        now = datetime.datetime.now()
        timeout_sec = d['time_sleep'] / 1000
        if 'if_change' in d and d['if_change'] and not d['name'] in self.values:
            cprint.cprint.info("create last value in %s " % d['name'])
            self.values[d['name']] = value
            self.__write_to_db(tablename=d['name'], value=value)
            self.values[f'write_time_{d["name"]}'] = datetime.datetime.now()
            # if 'alarms' in d:
            #     self.add_to_alarm_new(d)

        if 'if_change' in d and d['if_change'] and (self.values[d['name']] != value or ((now - self.values[f'write_time_{d["name"]}']).total_seconds() > d['rewrite_time']*60)):
            if (now - self.values[f'write_time_{d["name"]}']).total_seconds() > timeout_sec:
                self.values[d['name']] = value
                self.__write_to_db(tablename=d['name'], value=value)
                self.values[f'write_time_{d["name"]}'] = datetime.datetime.now()
                # if 'alarms' in d:
                #     self.add_to_alarm_new(d)

        if 'if_change' in d and not d['if_change']:

            if not f'write_time_{d["name"]}' in self.values:
                self.__write_to_db(tablename=d['name'], value=value)
                self.values[f'write_time_{d["name"]}'] = datetime.datetime.now()
            elif (now - self.values[f'write_time_{d["name"]}']).total_seconds() > timeout_sec:
                self.__write_to_db(tablename=d['name'], value=value)
                self.values[f'write_time_{d["name"]}'] = datetime.datetime.now()

    def run(self):
        self.__create_table_if_not_exist()  # создание таблиц если их нет
        while True:
            if (not self.__get_db_data()):
                self.__reconect_to_plc()
                self.status.value = 0
            else:
                threads = list()
                for d in self.values_list:
                    x = threading.Thread(target=self._thread_for_write_data, args=(d,))
                    threads.append(x)
                    while threading.active_count() > 250:
                        time.sleep(0.01)
                    x.start()
                for thread in threads:
                    thread.join()
                self._conn.commit()
                self.status.value = 1


    def disassemble_float(self, data) -> float:  # метод для преобразования данных в real
        val = struct.unpack('>f', data)
        return round(val[0], 1)

    def disassemble_double(self, data) -> int:  # метод для преобразования данных в bigint
        val = struct.unpack('>d', data)
        return val[0]

    def disassemble_int(self, data) -> int:  # метод для преобразования данных в int
        return int.from_bytes(data, "big", signed=True)

    def from_bytearray_to_bit(self, bit, start) -> int:
        value = int.from_bytes(self.bytearray_data[int(start):int(start) + 1], byteorder='little', signed=True)
        bits = bin(value)
        bits = bits.replace("0b", "")
        bits = bits[::-1]
        try:
            # result = bits[bit]
            result = get_bool(self.bytearray_data[int(start):int(start) + 1], 0, bit)
        except:
            result = 0
        return result


b = mp.Value('i', 0)
a = StartProcessOpcForConnectToPLC(status=b)
a.start()
