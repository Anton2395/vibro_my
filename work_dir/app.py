from flask import Flask, request, render_template, jsonify

import models as _models
import service_telegram as _tel_bot
import service as _service
import json

app = Flask(__name__)

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
    with _models.get_db() as db:
        if mac == '4C:75:25:36:34:3F':
            if max_value > 0.1:
                await _tel_bot.send_mailing(text='1 датчик значение: {value}'.format(value=max_value))
            for time, value in zip(Axel_time, Axel):
                data_to_db = _models.Datchik_1_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
            for time, value in zip(Temp_time, Temp):
                data_to_db = _models.Datchik_1_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
        elif mac == '58:BF:25:DB:3A:78':
            if max_value > 0.1:
                await _tel_bot.send_mailing(text='2 датчик значение: {value}'.format(value=max_value))
            for time, value in zip(Axel_time, Axel):
                data_to_db = _models.Datchik_2_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
            for time, value in zip(Temp_time, Temp):
                data_to_db = _models.Datchik_2_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
        elif mac == '58:BF:25:DA:D8:03':
            if max_value > 0.1:
                await _tel_bot.send_mailing(text='3 датчик значение: {value}'.format(value=max_value))
            for time, value in zip(Axel_time, Axel):
                data_to_db = _models.Datchik_3_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
            for time, value in zip(Temp_time, Temp):
                data_to_db = _models.Datchik_3_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
        elif mac == '58:BF:25:DB:4D:C8':
            if max_value > 0.1:
                await _tel_bot.send_mailing(text='4 датчик значение: {value}'.format(value=max_value))
            for time, value in zip(Axel_time, Axel):
                data_to_db = _models.Datchik_4_axel(
                    axel_time = float(time),
                    axel = float(value)
                )
                db.add(data_to_db)
                db.commit()
            for time, value in zip(Temp_time, Temp):
                data_to_db = _models.Datchik_4_temp(
                    temp_time=time,
                    temp=value
                )
                db.add(data_to_db)
                db.commit()
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
    data = _service.get_data(id=4)
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


@app.route("/tg", methods=['POST'])
def pull_json_tg():
    message = _tel_bot.pars_message(request.get_json())
    _tel_bot.routing_tg(message=message, response=request.get_json())
    return jsonify(request.get_json())


def run_flask():
    app.run(host="0.0.0.0")

