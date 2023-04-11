import json
import datetime as _dt
import traceback

from sqlalchemy import asc
import requests
import pytz

import models as _models


def median(f):
    # Creating buffer
    if not hasattr(median, "buffer"):
        median.buffer = [f] * 3

    # Move buffer to actually values ( [0, 1, 2] -> [1, 2, 3] )
    median.buffer = median.buffer[1:]
    median.buffer.append(f)

    # Calculation median
    a = median.buffer[0]
    b = median.buffer[1]
    c = median.buffer[2]
    middle = max(a, c) if (max(a, b) == max(b, c)) else max(b, min(a, c))

    return middle


def easy_mean(f, s_k=0.1, max_k=0.9, d=1.5):
    # Creating static variable
    if not hasattr(easy_mean, "fit"):
        easy_mean.fit = f

    # Adaptive ratio
    k = s_k if (abs(f - easy_mean.fit) < d) else max_k

    # Calculation easy mean
    easy_mean.fit += (f - easy_mean.fit) * k

    return easy_mean.fit


def get_data(id):
    if id == 0:
        table = _models.Datchik_1_axel
    elif id == 1:
        table = _models.Datchik_2_axel
    elif id == 2:
        table = _models.Datchik_3_axel
    elif id == 3:
        table = _models.Datchik_4_axel
    elif id == 4:
        table = _models.Datchik_5_axel
    db = _models.SessionLocal()
    data_array = db.query(table).order_by(asc(table.axel_time))
    json_data = {
        "data": [],
        "time": [],
        "name": f"datchik_{id+1}",
        "i": id
    }
    if data_array:
        for data in data_array:
            json_data['data'].append(data.axel)
            json_data['time'].append(data.axel_time)
            json_data['length'] = data.id
    db.close()
    return json_data

def get_data_from_datchik(number):
    conn = _models.createConnection()
    curs = conn.cursor()
    if number == 5 or number == '5':
        curs.execute(f"SELECT axel_time, axel FROM datchik_{number}_axel where (current_timestamp - to_timestamp(axel_time/1000)) < interval '1 month' order by axel_time;")
        answer = curs.fetchall()
    elif number == 3 or number == '3':
        curs.execute(f"SELECT axel_time, axel/16 FROM datchik_{number}_axel where (current_timestamp - to_timestamp(axel_time/1000)) < interval '1 month' order by axel_time;")
        answer = curs.fetchall()
    elif number == 4 or number == '4':
        curs.execute(f"SELECT axel_time, axel/30 FROM datchik_{number}_axel where (current_timestamp - to_timestamp(axel_time/1000)) < interval '1 month' order by axel_time;")
        answer = curs.fetchall()
    elif number == 99 or number == '99':
        curs.execute(f"SELECT axel_time, axel/16 FROM datchik_3_axel where (current_timestamp - to_timestamp(axel_time/1000)) < interval '1 month' order by axel_time;")
        x = []
        y = []
        for time, value in curs.fetchall():
            x.append(time)
            y.append(value)
        x_new = []
        y_new = []
        for index, (time, val) in enumerate(zip(x, y)):
            # print(index, "-", time, val)
            if index >= 3:
                x_new.append(time)
            # else:
                # delta_x = val - y[index-1]
                # y_new.append(y[index-1]+(delta_x*0.5))
                y_new.append((y[index]+y[index-1]+y[index-2]+y[index-3])/4)
        answer = []
        for i in zip(x_new, y_new):
            answer.append(i)
    # answer = []
    if number == '44':
        curs.execute(
            f"SELECT ceil(date_part('epoch', now_time)*1000), value/15 FROM datchik_{number}_axel where (current_timestamp - now_time) < interval '1 month' order by now_time;")
        answer = []
        for time, value in curs.fetchall():
            answer.append((time, easy_mean(median(value))))
    conn.close()
    return answer
    

def update_data(last_id_1, last_id_2, last_id_3, last_id_4, last_id_5):
    db = _models.SessionLocal()
    if last_id_1 != "undefined":
        data_datchik_1 = db.query(_models.Datchik_1_axel).filter(_models.Datchik_1_axel.id>int(last_id_1)).order_by(asc(_models.Datchik_1_axel.axel_time))
    else:
        data_datchik_1 = db.query(_models.Datchik_1_axel).all()
    if last_id_2 != "undefined":
        data_datchik_2 = db.query(_models.Datchik_2_axel).filter(_models.Datchik_2_axel.id>int(last_id_2)).order_by(asc(_models.Datchik_2_axel.axel_time))
    else:
        data_datchik_2 = db.query(_models.Datchik_2_axel).all()
    if last_id_3 != "undefined":
        data_datchik_3 = db.query(_models.Datchik_3_axel).filter(_models.Datchik_3_axel.id>int(last_id_3)).order_by(asc(_models.Datchik_3_axel.axel_time))
    else:
        data_datchik_3 = db.query(_models.Datchik_3_axel).all()
    if last_id_4 != "undefined":
        data_datchik_4 = db.query(_models.Datchik_4_axel).filter(_models.Datchik_4_axel.id>int(last_id_4)).order_by(asc(_models.Datchik_4_axel.axel_time))
    else:
        data_datchik_4 = db.query(_models.Datchik_4_axel).all()
    if last_id_1 != "undefined":
        data_datchik_5 = db.query(_models.Datchik_5_axel).filter(_models.Datchik_5_axel.id>int(last_id_5)).order_by(asc(_models.Datchik_5_axel.axel_time))
    else:
        data_datchik_5 = db.query(_models.Datchik_5_axel).all()
    db.close()
    json_data = {
        "datchik_1_axel": {
            "data": [],
            "time": [],
            "length": 0,
            "name": "datchik_1",
            "i": 0
        },
        "datchik_2_axel": {
            "data": [],
            "time": [],
            "length": 0,
            "name": "datchik_2",
            "i": 1
        },
        "datchik_3_axel": {
            "data": [],
            "time": [],
            "length": 0,
            "name": "datchik_3",
            "i": 2
        },
        "datchik_4_axel": {
            "data": [],
            "time": [],
            "length": 0,
            "name": "datchik_4",
            "i": 3
        },
        "datchik_5_axel": {
            "data": [],
            "time": [],
            "length": 0,
            "name": "datchik_5",
            "i": 4
        },
    }
    for data in data_datchik_1:
        json_data['datchik_1_axel']['data'].append(data.axel)
        json_data['datchik_1_axel']['time'].append(data.axel_time)
        last_id_1 = data.id
    json_data['datchik_1_axel']['length'] = last_id_1
    for data in data_datchik_2:
        json_data['datchik_2_axel']['data'].append(data.axel)
        json_data['datchik_2_axel']['time'].append(data.axel_time)
        last_id_2 = data.id
    json_data['datchik_2_axel']['length'] = last_id_2
    for data in data_datchik_3:
        json_data['datchik_3_axel']['data'].append(data.axel)
        json_data['datchik_3_axel']['time'].append(data.axel_time)
        last_id_3 = data.id
    json_data['datchik_3_axel']['length'] = last_id_3
    for data in data_datchik_4:
        json_data['datchik_4_axel']['data'].append(data.axel)
        json_data['datchik_4_axel']['time'].append(data.axel_time)
        last_id_4 = data.id
    json_data['datchik_4_axel']['length'] = last_id_4
    for data in data_datchik_5:
        json_data['datchik_5_axel']['data'].append(data.axel)
        json_data['datchik_5_axel']['time'].append(data.axel_time)
        last_id_5 = data.id
    json_data['datchik_5_axel']['length'] = last_id_5
    return json_data

def downlod_and_add_to_db():
    data_json = requests.get("http://185.6.25.165/awp/index.json")
    data = json.loads(data_json.content)
    db = _models.SessionLocal()
    for time_no_format_str, mm, temp in zip(data["time"], data["mm"], data["temp"]):
        time_format_str = time_no_format_str.replace(" ", "")
        try:
            time_no_tz = _dt.datetime.strptime(time_format_str, '%Y-%m-%dT%H:%M:%S')
            my_tz = pytz.timezone("Europe/Minsk")
            time = my_tz.localize(time_no_tz)
            axel_db = _models.Datchik_5_axel(axel_time=int(time.timestamp())*1000, axel=round(mm, 2))
            temp_db = _models.Datchik_5_temp(temp_time=int(time.timestamp())*1000, temp=round(temp, 2))
            db.add(axel_db)
            db.commit()
            db.add(temp_db)
            db.commit()
        except Exception as e:
            print(_dt.datetime.now(), "   //////   write db error")
            with open("logs.log", 'a') as file:
                file.write(f"{_dt.datetime.now()} ---------------------------------------------------------------------\n")
                file.write(traceback.format_exc())
                if type(e) == str:
                    file.write(e)
    db.close()

        