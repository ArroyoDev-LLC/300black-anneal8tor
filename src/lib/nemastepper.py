# -*- coding: utf-8 -*-

"""A4988 Stepper Driver Interface.

Adopted from: https://github.com/jeffmer/micropython-upybbot/blob/master/nemastepper.py

Modified to be compatible with esp32 / some enhancements.

"""

from machine import Pin


class Stepper:
    """
    Handles  A4988 hardware driver for bipolar stepper motors
    """

    def __init__(self, dir_pin, step_pin, enable_pin):
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.enable_pin = Pin(enable_pin, Pin.OUT)
        self.enable_pin.on()
        self.dir = 0
        self.pulserate = 100
        self.count = 0
        self.speed = 0
        self.MAX_ACCEL = (
            100  # equivallent to 100 x (periodicity of set_speed) usteps/sec/sec
        )

    def do_step(self):  # called by timer interrupt every 100us
        if self.dir == 0:
            return
        self.count = (self.count + 1) % self.pulserate
        if self.count == 0:
            self.step_pin.on()
            pass
            self.step_pin.off()

    def set_speed(self, speed):  # called periodically
        if (self.speed - speed) > self.MAX_ACCEL:
            self.speed -= self.MAX_ACCEL
        elif (self.speed - speed) < -self.MAX_ACCEL:
            self.speed += self.MAX_ACCEL
        else:
            self.speed = speed
        # set direction
        if self.speed > 0:
            self.dir = 1
            self.dir_pin.on()
            self.enable_pin.off()
        elif self.speed < 0:
            self.dir = -1
            self.dir_pin.off()
            self.enable_pin.off()
        else:
            self.enable_pin.value(1)
            self.dir = 0
        if abs(self.speed) > 0:
            self.pulserate = 10000 // abs(self.speed)

    def set_off(self):
        self.enable_pin.on()

    def set_power(self, enabled=True):
        value = 1 if enabled else 0
        self.enable_pin.value(value)

    def get_speed(self):
        return self.speed
