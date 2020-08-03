# -*- coding: utf-8 -*-

"""Black app"""

import picoweb
import models
from black import Black
from motor import Motor

STEP_PIN = 25
DIR_PIN = 26
EN_PIN = 27


class BlackApp(picoweb.WebApp):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.black = None
        self.events_sink = set()

    def init(self):
        models.db.connect()
        models.Config.create_table(False)
        motor = Motor(DIR_PIN, STEP_PIN, EN_PIN)
        self.black = Black(motor)
        super().init()


app = BlackApp(None)
