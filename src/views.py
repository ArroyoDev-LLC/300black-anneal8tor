# -*- coding: utf-8 -*-

"""300Black Views"""

import machine
import picoweb
import uasyncio
import ulogging as logging

from app import app
from models import Config

Log = logging.getLogger("anneal8tor.views")


def json_response(resp, **data):
    """Make json response."""
    yield from picoweb.start_response(resp, "application/json")
    yield from picoweb.jsonify(resp, data)


@app.route("/update_config")
def update_config(req, resp):
    """Update configuration variables."""
    req.parse_qs()
    ssid = req.form.get("ssid", None)
    power = req.form.get("power", None)
    if ssid:
        Log.info("wifi config update inbound: " + ssid)
        Config.create(key="wifi.ssid", value=ssid)
        Config.create(key="wifi.passwd", value=req.form.get("pass", ""))
        Log.info("config saved! rebooting...")
        machine.reset()
    if power:
        Log.info("power toggle update inbound: %s" % power)
        app.black.set_power(enabled=int(power))
        yield from json_response(resp, power=power)


@app.route("/events")
def events(req, resp):
    Log.info("Event source %s connected." % resp)
    yield from resp.awrite("HTTP/1.0 200 OK\r\n")
    yield from resp.awrite("Content-Type: text/event-stream\r\n")
    yield from resp.awrite("\r\n")
    app.events_sink.add(resp)
    return False


@app.route("/move_slot")
def move_slot(req, resp):
    loop = uasyncio.get_event_loop()
    req.parse_qs()
    step = int(req.form["step"])
    if step == 0:
        loop.call_soon(lambda: loop.create_task(app.black.move_home()))
    else:
        loop.call_soon(lambda: loop.create_task(app.black.move_by_slot(step)))
    yield from json_response(resp, position=app.black.motor.position)


@app.route("/set_pos")
def set_pos(req, resp):
    req.parse_qs()
    new_pos = req.form["pos"]
    app.black.motor.move_to(int(new_pos))
    yield from json_response(resp, position=app.black.motor.position)


@app.route("/calibrate")
def calibrate(req, resp):
    loop = uasyncio.get_event_loop()
    loop.create_task(app.black.calibrate_motor())
    yield from json_response(resp, position=app.black.motor.position)


@app.route("/")
def index(req, resp):
    try:
        ssid = Config.get_id("wifi.ssid")[0].value
    except KeyError:
        ssid = "300black Anneal8tor (AP)"
    yield from picoweb.start_response(resp)
    yield from app.render_template(resp, "index.tpl", ("ON", ssid))
