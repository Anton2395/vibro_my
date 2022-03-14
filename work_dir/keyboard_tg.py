import json


def keyboard_start_mailing():
    keyboard = {"keyboard": [["Подписаться"]],
                "one_time_keyboard": False,
                "resize_keyboard": True}
    keyboard = json.dumps(keyboard)
    return keyboard


def keyboard_stop_mailing():
    keyboard = {"keyboard": [["Отписаться"]],
                "one_time_keyboard": False,
                "resize_keyboard": True}
    keyboard = json.dumps(keyboard)
    return keyboard
