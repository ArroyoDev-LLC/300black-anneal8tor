# -*- coding: utf-8 -*-


"""300Black Anneal8tor main"""

import machine
import micropython
import uasyncio
import ulogging as logging
import utime as time
from machine import Pin

from models import Config


class Black:
    BOOTING = "Booting"
    CALIBRATING = "Calibrating"
    ERROR = "Error"
    READY = "Ready"
    ACTIVE = "Active"
    PAUSED = "Paused"
    ANNEAL_DELAY = 3500

    def __init__(self, motor, switch_pin=34, hall_pin=33, relay_pin=32):
        self.log = logging.getLogger("anneal8tor.black")
        self._slot_disp = 0
        self._motor = motor
        self._switch = Pin(switch_pin, Pin.IN)
        self._hall = Pin(hall_pin, Pin.IN)
        self._relay = Pin(relay_pin, Pin.OUT, value=0)
        self._switch_count = 0
        self._switch_irq_began = None
        self._found_home_at = None
        self._status = self.BOOTING
        self._error = None
        self._calibrating = False
        self._rehydate()

    def _rehydate(self):
        try:
            store = Config.get_id("black.slot_displacement")
        except KeyError:
            return
        else:
            if any(store):
                hydrated = store[0].value
                self._slot_disp = float(hydrated)
                self._switch_count = 0
                self.log.info("rehydrating calibrated slot displacement: " + hydrated)
                self._status = self.READY

    @property
    def motor(self):
        return self._motor

    @property
    def status(self):
        return self._status

    @property
    def count(self):
        return self._switch_count

    @property
    def is_running(self):
        return self._status == self.ACTIVE

    @property
    def error(self):
        return self._error

    def _inc_switch_count(self):
        self._switch_irq_began = time.ticks_ms()
        self._switch_count += 1
        self.log.debug("limit switch triggered: %s" % str(self._switch_count))

    def clear_error(self):
        self._error = None

    def check_hall(self):
        if self._calibrating and self._hall.value() == 0:
            self._calibrating = False
            return
        return self._hall.value() == 0

    async def calibrate_motor(self):
        self.log.info("starting motor calibration")
        self._status = self.CALIBRATING
        self._calibrating = True
        while self._calibrating:
            self._motor.move_at_speed(150)
            self.check_hall()
            uasyncio.sleep_ms(1)
        self._motor.stop()
        self._status = self.READY

    def calc_step_value(self, *args):
        self._motor.stop()
        revolve_time = time.ticks_diff(time.ticks_ms(), self._found_home_at)
        step_time = revolve_time // 8
        # self._slot_disp = self._motor.position / 8
        self._slot_disp = step_time
        self.log.info("calc slot displacement: %s" % self._slot_disp)
        Config.create(key="black.slot_displacement", value=str(self._slot_disp))
        self._status = self.READY

    def _handle_switch_irq(self, *args):
        if not self._switch_irq_began:
            self._inc_switch_count()
            return
        diff_s = time.ticks_diff(time.ticks_ms(), self._switch_irq_began)
        if diff_s > 500:
            self._inc_switch_count()

    async def move_by_slot(self, slot=1):
        direct = 1
        if slot >= 1:
            direct = -1

        while self.check_hall():
            self._motor.move_at_speed(500, direction=direct)
            await uasyncio.sleep_ms(50)

        while not self.check_hall():
            self._motor.move_at_speed(500, direction=direct)
            await uasyncio.sleep_ms(50)

        self._motor.stop()

    async def move_home(self):
        await self.calibrate_motor()

    def set_power(self, enabled=False):
        self._error = None
        status = self.ACTIVE if enabled else self.PAUSED
        self._status = status

    async def _switch_annie_relay(self):
        self._relay.value(1)
        await uasyncio.sleep_ms(250)
        self._relay.value(0)

    async def do_anneal(self):
        while 1:
            if self.is_running:
                cur_count = int(self._switch_count)
                await self.move_by_slot(1)
                await uasyncio.sleep_ms(500)
                await self._switch_annie_relay()
                await uasyncio.sleep_ms(self.ANNEAL_DELAY)
                if cur_count >= self._switch_count:
                    self._status = self.ERROR
                    self._error = "No shell detected! Are there any left?"
                    self.log.error(self._error)
                    self.log.error(
                        "Current count: %s | Total: %s"
                        % (cur_count, self._switch_count)
                    )
            else:
                # sleep for ~5 seconds if not enabled
                await uasyncio.sleep_ms(self.ANNEAL_DELAY * 3)
