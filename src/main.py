# main.py

import gc

import network
import uasyncio
import ulogging as logging
import utime as time
import views
from app import app
from models import Config

Log = logging.getLogger('anneal8tor')

def connect_wifi(ssid, passwd):
    wifi = network.WLAN(network.STA_IF)
    if wifi.isconnected():
        Log.info('Connected to wifi: %s' % ssid)
        return 
    Log.info('Connecting to: %s' % ssid)
    wifi.active(True)
    wifi.connect(ssid, passwd)
    while not wifi.isconnected():
        Log.info('connecting...')
        time.sleep(1)
    Log.info('Wifi connected!')
    return

def get_wifi():
    wifi = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    if any(Config.scan()):
        try:
            Log.info('wifi configuration found!')
            ssid = Config.get_id('wifi.ssid')[0].value
            passwd = Config.get_id('wifi.passwd')[0].value
            if not wifi.isconnected():
                connect_wifi(ssid, passwd)
            Log.info('WLAN: %s' % wifi.ifconfig()[0])
            return
        except Exception as e:
            Log.warning('failed to connect to wifi!')
            Log.error(e)
            Log.warning('recreating config table!')
            Config.create_table(True)
    Log.warning('no wifi config found! Going into AP mode.')
    ap = network.WLAN(network.AP_IF)
    ap.config(essid='300Black Anneal8tor')
    ap.active(True)
    Log.info('WLAN: %s %s %s %s' % wifi.ifconfig())
    return


async def push_event(ev):
    to_del = set()
    for resp in app.events_sink:
        try:
            await resp.awrite("data: %s\n\n" % ev)
        except OSError as e:
            Log.warning("Event source %r disconnected (%r)" % (resp, e))
            await resp.aclose()
            to_del.add(resp)
    for resp in to_del:
        app.events_sink.remove(resp)

async def push_status():
    while 1:
        await push_event("pos:%s" % app.black.motor.position)
        await push_event("state:%s" % app.black.status)
        await push_event("count:%s" % app.black.count)
        if app.black.error:
            await push_event("error:%s" % app.black.error)
            app.black.clear_error()
        await uasyncio.sleep(1)


def main():
    gc.collect()
    logging.basicConfig(level=logging.DEBUG)
    gc.collect()
    app._load_template('index.tpl')
    gc.collect()
    loop = uasyncio.get_event_loop()
    loop.create_task(push_status())
    loop.call_soon(get_wifi)
    loop.call_soon(lambda: loop.create_task(app.black.do_anneal()))
    app.run(host='0.0.0.0', debug=True)


if __name__ == '__main__':
    main()
