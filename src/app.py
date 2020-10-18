# -*- coding: utf-8 -*-

"""Black app"""

import picoweb

import models
from black import Black
from motor import Motor

STEP_PIN = 25
DIR_PIN = 26
EN_PIN = 27

HALL_PIN = 33
SWITCH_PIN = 34


def get_black():
    models.db.connect()
    models.Config.create_table(False)
    motor = Motor(DIR_PIN, STEP_PIN, EN_PIN)
    black = Black(motor, switch_pin=SWITCH_PIN, hall_pin=HALL_PIN)
    return motor, black


class BlackApp(picoweb.WebApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.black = None
        self.events_sink = set()

    def init(self):
        _, black = get_black()
        self.black = black
        super().init()


app = BlackApp(None)
