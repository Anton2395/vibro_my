from threading import Thread

import requests

import models as _models

class Mailing(Thread):
    """
    A threading example
    """
    r = ''

    def __init__(self, name, text):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = name
        self.text = text

    def run(self):
        """Запуск потока"""
        with _models.get_db as db:
            users = db.query(_models.User).filter(_models.User.mailing==1)
        # users = user.query.filter_by(mailing=1).all()
        URL = 'https://api.telegram.org/bot1929071630:AAGd6557EvdeWtOs2bhc_dd_eVVGzx7XGOY/'
        for user in users:
            url = URL + 'sendMessage'
            answer = {'chat_id': user.chat_id,
                      'parse_mode': 'HTML',
                      'disable_web_page_preview': True,
                      'text': self.text,
                      'reply_markup': ''
                      }
            r = requests.post(url, json=answer)
        return r.json()