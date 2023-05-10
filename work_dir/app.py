from flask import Flask, request, render_template, jsonify
# from flask_cors import CORS
from pytz import timezone
import models as _models
import service_telegram as _tel_bot
import service as _service
from service_for_graf import generate_column, get_table_name
import json
import datetime

app = Flask(__name__)
# CORS(app)
tz = timezone('Europe/Minsk')

@app.route("/data", methods=['POST'])
async def pars():
    data = request.get_json()
    mac = data['MAC']
    Axel_time = data['Axel_time']
    Axel = data['Axel']
    Temp_time = data['Temp_time']
    Temp = data['Temp']
    # count = 0
    Axel = [float(item) for item in Axel]
    max_value = max(Axel)
    db = _models.SessionLocal()
    if mac == '4C:75:25:36:34:3F':
        if max_value > 4:
            await _tel_bot.send_mailing(text='1 датчик значение: {value}'.format(value=max_value))
        for index, (time, value) in enumerate(zip(Axel_time, Axel)):
            if index%2 == 0:
                data_to_db = _models.Datchik_1_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
        for index, (time, value) in enumerate(zip(Temp_time, Temp)):
            if index%2 == 0:    
                data_to_db = _models.Datchik_1_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
    elif mac == '58:BF:25:DB:3A:78':
        if max_value > 4:
            await _tel_bot.send_mailing(text='2 датчик значение: {value}'.format(value=max_value))
        for index, (time, value) in enumerate(zip(Axel_time, Axel)):
            if index%2 == 0:
                data_to_db = _models.Datchik_2_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
        for index, (time, value) in enumerate(zip(Temp_time, Temp)):
            if index%2 == 0:
                data_to_db = _models.Datchik_2_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
    elif mac == '58:BF:25:DA:D8:03':
        if max_value > 4:
            await _tel_bot.send_mailing(text='3 датчик значение: {value}'.format(value=max_value))
        for index, (time, value) in enumerate(zip(Axel_time, Axel)):
            if index%2==0:
                data_to_db = _models.Datchik_3_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
        for index, (time, value) in enumerate(zip(Temp_time, Temp)):
            if index%2 == 0:
                data_to_db = _models.Datchik_3_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
    elif mac == '58:BF:25:DB:4D:C8':
        if max_value > 4:
            await _tel_bot.send_mailing(text='4 датчик значение: {value}'.format(value=max_value))
        for index, (time, value) in enumerate(zip(Axel_time, Axel)):
            if index%2 == 0:
                data_to_db = _models.Datchik_4_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
        for index, (time, value) in enumerate(zip(Temp_time, Temp)):
            if index%2 == 0:
                data_to_db = _models.Datchik_4_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
    db.close()
    return 'ok', 200, {'Content-Type': 'text'}


@app.route("/get_data_1", methods=['POST', 'GET'])
def chart_1():
    data = _service.get_data(id=0)
    return data


@app.route("/get_data_2", methods=['POST', 'GET'])
def chart_2():
    data = _service.get_data(id=1)
    return data


@app.route("/get_data_3", methods=['POST', 'GET'])
def chart_3():
    data = _service.get_data(id=2)
    return data


@app.route("/get_data_4", methods=['POST', 'GET'])
def chart_4():
    data = _service.get_data(id=3)
    return data


@app.route("/get_data_5", methods=['POST', 'GET'])
def chart_5():
    # data = _service.get_data(id=4)
    # print(type(_service.get_data_from_datchik()[0]))
    data = json.dumps(_service.get_data_from_datchik(5))
    return data


@app.route("/add_data", methods=['POST', 'GET'])
def add_data():
    last_id_1 = request.values.get('last_id_1')
    last_id_2 = request.values.get('last_id_2')
    last_id_3 = request.values.get('last_id_3')
    last_id_4 = request.values.get('last_id_4')
    last_id_5 = request.values.get('last_id_5')
    data = _service.update_data(last_id_1=last_id_1,
                       last_id_2=last_id_2,
                       last_id_3=last_id_3,
                       last_id_4=last_id_4,
                       last_id_5=last_id_5)
    return data, 200, {'Content-Type': 'text'}


@app.route("/", methods=['GET'])
def main():
    # data = get_data(3)
    return render_template('index_1.html')


@app.route("/chart", methods=['GET'])
def main_chart():
    return render_template('index_chart.html')


@app.route("/all_line", methods=['GET'])
def all_line_chart():
    return render_template('test_all_chart.html')


@app.route("/get_point/<number>", methods=['GET'])
def get_point(number):
    data = json.dumps(_service.get_data_from_datchik(number))
    return data


@app.route("/tg", methods=['POST'])
def pull_json_tg():
    message = _tel_bot.pars_message(request.get_json())
    _tel_bot.routing_tg(message=message, response=request.get_json())
    return jsonify(request.get_json())


@app.route("/new", methods=['GET'])
def main_page():
    conn = _models.createConnection()
    return render_template('new_index.html')


@app.route("/get_full_data_from", methods=['GET'])
def main_page12():
    conn = _models.createConnection()
    curs = conn.cursor()
    curs.execute("""SELECT axel_time, axel FROM datchik_5_axel WHERE id % 500 = 0 order by axel_time""")
    data = curs.fetchall()
    conn.close()
    return json.dumps(data)


@app.route("/get_test/<start>/<end>", methods=['GET'])
def period_test(start=None, end=None):
    start_int = int(start)
    end_int = int(end)
    conn = _models.createConnection()
    curs = conn.cursor()
    curs.execute(f"""SELECT count(*) FROM datchik_5_axel where axel_time>={start_int} and axel_time<={end_int}""")
    count = curs.fetchone()[0]
    if count > 30000:
        curs.execute(f"""SELECT axel_time, axel FROM datchik_5_axel WHERE axel_time>={start_int} and axel_time<={end_int} and id % {round(count/3000)} = 0 order by axel_time""")
    else:
        curs.execute(f"""SELECT axel_time, axel FROM datchik_5_axel WHERE axel_time>={start_int} and axel_time<={end_int} order by axel_time""")
    data = curs.fetchall()
    conn.close()
    return json.dumps(data)


@app.route("/get_one_line/<point>", methods=['GET'])
def get_start_points(point):
    conn = _models.createConnection()
    curs = conn.cursor()
    table_name = get_table_name(point)
    columns, order_param = generate_column(table_name)
    if table_name:
        curs.execute(f""" SELECT count(*) from {table_name}""")
        count = curs.fetchone()[0]
        if count > 3000:
            curs.execute(f"""SELECT {columns} FROM {table_name} WHERE id % {round(count/3000)} = 0 order by {order_param}""")
        else:
            curs.execute(f"""SELECT {columns} FROM {table_name} order by {order_param}""")
        data = curs.fetchall()
        conn.close()
        return json.dumps(data)
    else:
        conn.close()
        return 'bad request'


@app.route("/get_one_line/<point>/<start>/<end>", methods=['GET'])
def get_duration_points(point, start, end):
    start_int = int(start)
    end_int = int(end)
    conn = _models.createConnection()
    curs = conn.cursor()
    table_name = get_table_name(point)
    columns, order_param = generate_column(table_name)
    if table_name and order_param != 'now_time':
        curs.execute(f""" SELECT count(*) from {table_name} WHERE {order_param}>={start_int} and {order_param}<={end_int}""")
        count = curs.fetchone()[0]
        if count > 3000:
            curs.execute(f"""SELECT {columns} FROM {table_name} WHERE {order_param}>={start_int} and {order_param}<={end_int} and id % {round(count/3000)} = 0 order by {order_param}""")
        else:
            curs.execute(f"""SELECT {columns} FROM {table_name} WHERE {order_param}>={start_int} and {order_param}<={end_int} order by {order_param}""")
        data = curs.fetchall()
        conn.close()
        return json.dumps(data)
    elif table_name and order_param == 'now_time':
        new_start = tz.localize(datetime.datetime.fromtimestamp(start_int/1000))
        new_end = tz.localize(datetime.datetime.fromtimestamp(end_int/1000))
        curs.execute(f""" SELECT count(*) from {table_name} WHERE {order_param}>='{new_start}' and {order_param}<='{new_end}'""")
        count = curs.fetchone()[0]
        if count > 3000:
            curs.execute(f"""SELECT {columns} FROM {table_name} WHERE {order_param}>='{new_start}' and {order_param}<='{new_end}' and id % {round(count/3000)} = 0 order by {order_param}""")
        else:
            curs.execute(f"""SELECT {columns} FROM {table_name} WHERE {order_param}>='{new_start}' and {order_param}<='{new_end}' order by {order_param}""")
        data = curs.fetchall()
        conn.close()
        return json.dumps(data)
    else:
        conn.close()
        return 'bad request'

@app.route("/control_line", methods=['GET'])
def page_with_control_line():
    return render_template('index_with_control_line.html')


def run_flask():
#     app.run(host="0.0.0.0", debug=True)
    app.run(host="0.0.0.0")

# run_flask()

