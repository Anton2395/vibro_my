import requests

from flask import jsonify

import models as _models
import keyboard_tg as _kb

from mailing_th import Mailing



URL = 'https://api.telegram.org/bot1929071630:AAGd6557EvdeWtOs2bhc_dd_eVVGzx7XGOY/'


def send_message(chat_id, text, keyboard):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id,
              'parse_mode': 'HTML',
              'disable_web_page_preview': True,
              'text': text,
              'reply_markup': keyboard
              }
    r = requests.post(url, json=answer)
    return r.json()

async def send_mailing(text):
    name = "Thread #schet"
    my_thread = Mailing(name, text)
    my_thread.start()



def pars_message(data):
    if 'message' in data:
        message = {'chat_id': data['message']['chat']['id'],
                   'username': data['message']['from']['username'],
                   'text': data['message']['text'],
                   'callback': False
        }
    elif 'callback_query' in data:
        message = {'chat_id': data['callback_query']['message']['chat']['id'],
                   'username': data['callback_query']['from']['username'],
                   'text': data['callback_query']['data'],
                   'callback': True
                   }
    else:
         message = {
             "text": ""
         }
    return message



def add_user_tg(chat_id: int, username: str):
    db = _models.SessionLocal()
    user = db.query(_models.User).filter(_models.User.chat_id==chat_id).first()
    if not user:
        user = _models.User(chat_id=chat_id, username=username)
        db.add(user)
        db.commit()
    else:
        user.username = username
        db.commit()
    db.close()


def update_subscription(chat_id, subscription):
    db = _models.SessionLocal()
    user = db.query(_models.User).filter(_models.User.chat_id==chat_id).first()
    user.mailing = subscription
    db.commit()
    db.close()


def routing_tg(message, response):
    if message['text'] == '':
        return jsonify()
    if not message['callback']:
        if 'voice' in message:
            return jsonify(response)
        elif 'sticker' in message:
            return jsonify(response)
        elif 'photo' in message:
            return jsonify(response)
        elif 'video' in message:
            return jsonify(response)
        else:
            if message['text'] == '/start':
                add_user_tg(chat_id=message['chat_id'],
                            username=message['username'])
                send_message(chat_id=message['chat_id'],
                             text='Привет',
                             keyboard=_kb.keyboard_start_mailing())
            elif message['text'] == 'Подписаться':
                print("DONE")
                update_subscription(chat_id=message['chat_id'], subscription=1)
                print("change done")
                send_message(chat_id=message['chat_id'],
                             text= 'Ты успешно подписался',
                             keyboard=_kb.keyboard_stop_mailing())
            elif message['text'] == 'Отписаться':
                update_subscription(chat_id=message['chat_id'], subscription=0)
                send_message(chat_id=message['chat_id'],
                             text='Ты успешно отписался',
                             keyboard=_kb.keyboard_start_mailing())
            else:
                return jsonify()
    return jsonify(response)