"""

A small Test application to show how to use Flask-MQTT.

"""
import eventlet
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

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


@socketio.on('off')
def handle_off():
    client.publish(SWITCH_POWER_TOPIC, 'OFF')


@socketio.on('on')
def handle_on():
    client.publish(SWITCH_POWER_TOPIC, 'ON')


def on_connect(client, userdata, flags, rc):
    client.subscribe(SWITCH_POWER_STATE_TOPIC)


def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('mqtt_message', data=data)


if __name__ == '__main__':
    client = mqtt.Client("Mqtt-controller", clean_session=True)
    client.on_connect = on_connect
    client.on_message = handle_mqtt_message
    mqtt_broker = "192.168.0.32"
    client.connect(mqtt_broker)
    client.loop_start()

    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
