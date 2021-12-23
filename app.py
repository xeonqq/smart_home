"""

A small Test application to show how to use Flask-MQTT.

"""
import json
import urllib

import eventlet
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

from utils import extract_filename

eventlet.monkey_patch()

app = Flask(__name__)

socketio = SocketIO(app)
bootstrap = Bootstrap(app)
client = None

SWITCH_POWER_TOPIC = "cmnd/sonoff-socket/POWER"
SWITCH_POWER_STATE_TOPIC = "stat/sonoff-socket/POWER"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download')
def download():
    return render_template('download.html')


@socketio.on('off')
def handle_off():
    client.publish(SWITCH_POWER_TOPIC, 'OFF')


@socketio.on('on')
def handle_on():
    client.publish(SWITCH_POWER_TOPIC, 'ON')


@socketio.on('download')
def handle_download(json_str):
    print(json_str)
    data = json.loads(json_str)
    filename = extract_filename(data['url'])

    msg = dict(
        msg="Downloaded at: {}".format(filename)
    )
    socketio.emit('message', data=msg)

    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        socketio.emit('download_progress', data=dict(
            downloaded=downloaded,
            total_size=total_size
        ))
        if downloaded >= total_size:
            socketio.emit('download_finish')

        # print("Downlading: {}MB/{}MB, {}%".format(downloaded / 1e6, total_size / 1e6, downloaded / total_size))

    urllib.request.urlretrieve(data['url'], filename, show_progress)


def on_connect(client, userdata, flags, rc):
    client.subscribe(SWITCH_POWER_STATE_TOPIC)


def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('message', data=data)


if __name__ == '__main__':
    client = mqtt.Client("Mqtt-controller", clean_session=True)
    client.on_connect = on_connect
    client.on_message = handle_mqtt_message
    mqtt_broker = '0.0.0.0'  # "192.168.0.28"
    client.connect(mqtt_broker)
    client.loop_start()

    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
