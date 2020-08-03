# -*- coding: utf-8 -*-


"""300Black Anneal8tor main"""

import micropython
import uasyncio
import ulogging as logging
import utime as time
from machine import Pin
from models import Config

micropython.alloc_emergency_exception_buf(100)


class Black:
    BOOTING = 'Booting'
    CALIBRATING = 'Calibrating'
    ERROR = 'Error'
    READY = 'Ready'
    ACTIVE = 'Active'
    PAUSED = 'Paused'
    ANNEAL_DELAY = 3500

    def __init__(self, motor, switch_pin=34):
        self.log = logging.getLogger('anneal8tor.black')
        self._slot_disp = 0
        self._motor = motor
        self._switch = Pin(switch_pin, Pin.IN)
        self._switch_count = 0
        self._switch_irq_began = None
        self._switch.irq(trigger=Pin.IRQ_FALLING, handler=self._handle_switch_irq)
        self._status = self.BOOTING
        self._error = None
        self._rehydate()

    def _rehydate(self):
        try:
            store = Config.get_id('black.slot_displacement')
        except KeyError:
            return
        else:
            if any(store):
                hydrated = store[0].value
                self._slot_disp = int(hydrated)
                self._switch_count = 0
                self.log.info('rehydrating calibrated slot displacement: ' + hydrated)
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
        self.log.debug('limit switch triggered: %s' % str(self._switch_count))

    def clear_error(self):
        self._error = None

    def calibrate_motor(self):
        self.log.info('starting motor calibration')
        self._status = self.CALIBRATING
        calibrated = False
        while not calibrated:
            self._motor.move_to(self._motor.position + 1)
            if self._switch_count >= 1:
                self.log.info('motor position found: %s' % self._motor.position)
                self._slot_disp = self._motor.position
                Config.create(key='black.slot_displacement', value=str(self._slot_disp))
                self._switch_count = 0
                self._motor.set_home()
                self._status = self.READY
                calibrated = True
        
    def _handle_switch_irq(self, *args):
        if not self._switch_irq_began:
            self._inc_switch_count()
            return
        diff_s = time.ticks_diff(time.ticks_ms(), self._switch_irq_began)
        if diff_s > 500:
            self._inc_switch_count()


    def move_by_slot(self, slot=1):
        self._motor.move_to(self._motor.position + self._slot_disp*slot)

    def move_home(self):
        return self._motor.move_to(0)

    def set_power(self, enabled=False):
        self._error = None
        status = self.ACTIVE if enabled else self.PAUSED
        self._status = status
        if enabled:
            self.move_home()

    async def do_anneal(self):
        while 1:
            if self.is_running:
                cur_count = int(self._switch_count)
                self.move_by_slot(1)
                # TRIGGER ANNIE VIA SERIAL HERE
                await uasyncio.sleep_ms(self.ANNEAL_DELAY)
                if cur_count >= self._switch_count:
                    self._status = self.ERROR
                    self._error = 'No shell detected! Are there any left?'
                    self.log.error(self._error)
                    self.log.error('Current count: %s | Total: %s' % (cur_count, self._switch_count))
            else:
                # sleep for ~5 seconds if not enabled
                await uasyncio.sleep_ms(self.ANNEAL_DELAY*3)
