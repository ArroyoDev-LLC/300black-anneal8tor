# -*- coding: utf-8 -*-

"""300Black Motor"""

import ulogging as logging
import utime as time
from machine import Timer
from models import Config
from nemastepper import Stepper


class Motor:
    MAX_ACCEL = 10000
    TIMER_FREQ = 10000
    TIMER_DELAY = 5

    def __init__(self, dir_pin, step_pin, en_pin):
        self._pos = 0
        self._state = 0
        self._speed = 0
        self._stepper = Stepper(dir_pin, step_pin, en_pin)
        self._stepper.MAX_ACCEL = self.MAX_ACCEL
        self._timer = Timer(1)
        self._timer.init(freq=self.TIMER_FREQ, callback=self._do_step)
        self.log = logging.getLogger("anneal8tor.motor")
        self._rehydate()

    def _rehydate(self):
        self.log.info("attempting to rehydrate motor...")
        try:
            store = Config.get_id("motor.position")
        except KeyError:
            return
        else:
            if any(store):
                hydrated = store[0].value
                self.log.info("rehydating motor position: " + hydrated)
                self._pos = int(hydrated)

    def _do_step(self, *args):
        self._stepper.do_step()

    @property
    def enabled(self):
        val = self._stepper.enable_pin.value()
        return val < 1

    @property
    def direction(self):
        return self._stepper.dir

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, value):
        try:
            val_exists = any(Config.get_id("motor.position"))
        except KeyError:
            val_exists = False
        self._pos = value
        if not val_exists:
            Config.create(key="motor.position", value=str(value))
            return self._pos
        Config.update({"key": "motor.position"}, value=str(value))
        return self._pos

    def _step(self, direction):
        self._stepper.set_speed(600 * direction)
        time.sleep_ms(self.TIMER_DELAY)
        self._stepper.set_speed(0)

    def move_to(self, pos):
        disp = self._pos - pos
        _dir = 1
        if disp >= 0:
            _dir = -1
        for i in range(abs(disp)):
            self._step(_dir)
        self.position = pos

    def set_home(self):
        self._pos = 0
        Config.create(key="motor.position", value=str(0))
