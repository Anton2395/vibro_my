import datetime
import struct
import threading
import time
from multiprocessing import Process

import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
import psycopg2

data = [{
    'name': '44',
    'slave_id': 1,
    'func': 3,
    'start_reg_adr': 0,
    'size': 4,
    'value_list': [
        {
            'name': 'axel',
            'type_table': 'float',
            'type_val': 'float',
            'start': 0,
            'signed': False,
            'big_or_little_endian': False,
            'byte_swap': True,
            'min_time_check': 1000,
            'max_time_check': 1,
            'if_change': False,
            'divide': False,
            'divide_num': 1,
            'bit': 0
        },
        {
            'name': 'temp',
            'type_table': 'float',
            'type_val': 'float',
            'start': 2,
            'signed': False,
            'big_or_little_endian': False,
            'byte_swap': True,
            'min_time_check': 1000,
            'max_time_check': 1,
            'if_change': True,
            'divide': False,
            'divide_num': 1,
            'bit': 0
        }
    ]
}]


def createConnection():
    return psycopg2.connect(dbname="db1", user="mvlab", password="z1x2c3", host="10.0.0.2")


class ConnectModProcess(Process):
    def __init__(self, name_connect: str, ip: str, port: int, status: object, stop_point: object, values: list = []):
        # slot:int, rack:int, values:list=[]):
        """Класс процесса для подключения к ПЛК по адресу address, с портом port (по умолчанию 102) и получения заданных
        значений из блока данных db в промежутке с start_address_db по start_address_db+offset_db
        (offset_db - количество забираемых byte из блока). После получения данных разбирает bytearray по
        списку values_list.

        :param ip: ip адрес ПЛК
        :param rack:  линейка ПЛК (смотри в Step7 или Tia POrtal)
        :param slot: номер слота ПЛК (смотри в Step7 или Tia POrtal)
        :param values: список значений которые взять из ПЛК
        :param port: номер порта (по умолчанию 102)
        :param name_connect: префикс названия таблиц для подключения
        :param status: статус соединения(передаётся Value из multiprocessing)

        """
        self.name_connect = name_connect
        self.ip = ip
        self.status = status
        self.stop_point = stop_point
        # self.rack = rack
        # self.slot = slot
        self.port = port
        self.values_list = values
        self.bytearray_data = []
        self.values = {}
        self._conn = createConnection()
        self._c = self._conn.cursor()

        self.master = modbus_tcp.TcpMaster(
            host=ip,
            port=port,
            timeout_in_sec=1
        )
        try:
            self.master._do_open()
            self.status.value = True
        except ConnectionResetError:
            self.status.value = False
        except TimeoutError:
            self.status.value = False
        super(ConnectModProcess, self).__init__()

    def __create_table_if_not_exist(self):
        """Создание таблиц для хранения данных (если их нету)"""
        for area in self.values_list:
            for value in area['value_list']:
                if value["type_table"] == 'int':
                    type_sql = 'INT'
                if value["type_table"] == 'float':
                    type_sql = 'REAL'
                if value["type_table"] == 'double':
                    type_sql = 'BIGINT'
                if value["type_table"] == 'bool':
                    type_sql = 'INT'
                value['table_name'] = self.name_connect + "_" + area["name"] + "_" + value["name"]
                self._c.execute(f'''CREATE TABLE IF NOT EXISTS {value['table_name']}
                                    (key serial primary key,
                                    now_time TIMESTAMP  WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                                    value {type_sql})''')
                self._conn.commit()
                self.set_old_value(value["table_name"])

    def set_old_value(self, table_name):
        self._c.execute(f'''
                        SELECT value, now_time
                            FROM {table_name}
                            ORDER BY now_time DESC
                            LIMIT 1
                        ''')
        val = self._c.fetchone()
        if val:
            self.values[table_name] = val[0]
            self.values["time_" + table_name] = val[1].replace(tzinfo=None)
        print(f'create and set table mvlab_{table_name}')

    def __get_data(self, area):
        """
        Получение данных с устройства
        """

        try:
            if area["func"] == 3:
                self.bytearray_data = self.master.execute(area["slave_id"], cst.READ_HOLDING_REGISTERS,
                                                          area['start_reg_adr'], area['size'])
                return True
            elif area["func"] == 4:
                self.bytearray_data = self.master.execute(area["slave_id"], cst.READ_INPUT_REGISTERS,
                                                          area['start_reg_adr'], area['size'])
                return True
            else:
                return False
        except Exception as e:
            print("Can't get data from PLC. Text error: ", self.name_connect)
            print(e)
            self.master._do_open()
            return False

    def __parse_bytearray(self, value):
        type_val = value['type_val']
        start = value['start']
        if type_val == 'int':
            end = start + 1
            temp_result = self.bytearray_data[start:end][0]
            result = self._convert_to_int(value, temp_result)
        elif type_val == 'float':
            end = start + 2
            temp_result = self.bytearray_data[start:end]
            result = self._convert_to_float(value, temp_result)
        elif type_val == 'double':
            end = start + 2
            temp_result = self.bytearray_data[start:end]
            result = self._convert_to_double(value, temp_result)
        elif type_val == 'bool':
            end = start + 2
            temp_result = self.bytearray_data[start:end]
            bits_mask_decimal = self._convert_to_double(value, temp_result)
            result = self._convert_to_bool(bits_mask_decimal, value['bit'])
        else:
            print('Bad choice type value')
            result = False
        return result

    def _convert_to_int(self, value: dict, data):
        if value['byte_swap']:
            convert = struct.pack('>H', data)
        else:
            convert = struct.pack('H', data)
        if value['signed']:
            result = struct.unpack('h', convert)[0]
        else:
            result = struct.unpack('H', convert)[0]
        if value['divide']:
            result = result / value['divide_num']
        return result

    def _convert_to_float(self, value: dict, data):
        if value['byte_swap']:
            convert_to_byte = struct.pack('>H', data[1]) + struct.pack('>H', data[0])
        else:
            convert_to_byte = struct.pack('HH', data[1], data[0])
        if value['big_or_little_endian']:
            result = struct.unpack('f', convert_to_byte)[0]
        else:
            result = struct.unpack('>f', convert_to_byte)[0]
        if value['divide']:
            result = result / value['divide_num']
        return result

    def _convert_to_double(self, value: dict, data):
        if value['byte_swap']:
            convert = struct.pack('>H', data[1]) + struct.pack('>H', data[0])
        else:
            convert = struct.pack('HH', data[1], data[0])
        if value['signed']:
            if value['big_or_little_endian']:
                result = struct.unpack('<l', convert)[0]
            else:
                result = struct.unpack('>l', convert)[0]
        else:
            if value['big_or_little_endian']:
                result = struct.unpack('<L', convert)[0]
            else:
                result = struct.unpack('>L', convert)[0]
        if value['divide']:
            result = result / value['divide_num']
        return result

    def _convert_to_bool(self, data, bit):
        bit_mask = f"{data:032b}"[::-1]
        result = int(bit_mask[bit])
        return result

    def __thread_for_write_data(self, value_param):
        """

        """
        value = self.__parse_bytearray(value_param)
        now = datetime.datetime.now()
        min_time_check = value_param["min_time_check"] / 1000

        if value_param['if_change'] and not value_param["table_name"] in self.values:
            self.values[value_param["table_name"]] = value
            self.values["time_" + value_param["table_name"]] = now
            self.__write_to_db(value_param["table_name"], value)

        if value_param['if_change'] and value_param["table_name"] in self.values and "time_" + value_param[
            "table_name"] in self.values:
            if value != self.values[value_param["table_name"]]:
                if (now - self.values['time_' + value_param['table_name']]).seconds >= min_time_check:
                    self.values[value_param["table_name"]] = value
                    self.values["time_" + value_param["table_name"]] = now
                    self.__write_to_db(value_param["table_name"], value)

        if not value_param['if_change'] and not "time_" + value_param["table_name"] in self.values:
            self.values["time_" + value_param["table_name"]] = now
            self.__write_to_db(value_param["table_name"], value)

        if not value_param['if_change'] and "time_" + value_param["table_name"] in self.values:
            if (now - self.values['time_' + value_param['table_name']]).seconds >= min_time_check:
                self.values["time_" + value_param["table_name"]] = now
                self.__write_to_db(value_param["table_name"], value)

    def __write_to_db(self, tablename, value):
        """Запись распаршеных данных в БД"""
        self._c.execute(
            f'''INSERT INTO {tablename} (value) VALUES ({value});''')

    def run(self):
        self.__create_table_if_not_exist()  # создание таблиц если их нет
        while True:
            try:
                if self.stop_point.value:
                    break
                for area in self.values_list:
                    if (not self.__get_data(area)):
                        self.status.value = False
                    else:
                        threads = list()
                        for value in area["value_list"]:
                            data_get_process = threading.Thread(target=self.__thread_for_write_data, args=(value,))
                            threads.append(data_get_process)
                            while threading.active_count() > 250:
                                time.sleep(0.01)
                            data_get_process.start()
                        self.status.value = True
                    for thread in threads:
                        thread.join()
                    self._conn.commit()
            except Exception as e:
                self.status.value = False
        self.stop_point.value = False