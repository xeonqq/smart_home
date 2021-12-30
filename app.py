"""

A small Test application to show how to use Flask-MQTT.

"""

import json
import os
import pathlib
import urllib

import eventlet
import paho.mqtt.client as mqtt
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from utils import extract_filename, time_str_to_object, time_object_to_str

eventlet.monkey_patch()

app = Flask(__name__)

socketio = SocketIO(app)
bootstrap = Bootstrap(app)
client = None

SWITCH_POWER_TOPIC = "cmnd/sonoff-socket/POWER"
SWITCH_POWER_STATE_TOPIC = "stat/sonoff-socket/POWER"

datebase_file = "site.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(datebase_file)
db = SQLAlchemy(app)


class SwitchDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    switched_on = db.Column(db.Boolean, nullable=False, default=False)
    power_on_schedule = db.Column(db.Time, nullable=True)
    power_off_schedule = db.Column(db.Time, nullable=True)

    def __repr__(self):
        return f"Device('{self.name}', '{self.switched_on}', on at '{self.power_on_schedule}', off at '{self.power_off_schedule}')"


@app.route('/')
def index():
    get_device("Sonoff").power_off_schedule
    schedule = {
        'on': time_object_to_str(get_device("Sonoff").power_on_schedule),
        'off': time_object_to_str(get_device("Sonoff").power_off_schedule)
    }
    return render_template('index.html', schedule=schedule)


@app.route('/download')
def download():
    return render_template('download.html')


@socketio.on('off')
def handle_off():
    client.publish(SWITCH_POWER_TOPIC, 'OFF')
    get_device("Sonoff").switched_on = False
    db.session.commit()


@socketio.on('on')
def handle_on():
    client.publish(SWITCH_POWER_TOPIC, 'ON')
    get_device("Sonoff").switched_on = True
    db.session.commit()


@socketio.on('update_schedule')
def handle_update_schedule(json_str):
    data = json.loads(json_str)
    get_device("Sonoff").power_on_schedule = time_str_to_object(data['power_on_schedule'])
    get_device("Sonoff").power_off_schedule = time_str_to_object(data['power_off_schedule'])
    db.session.commit()

    print(get_device("Sonoff"))
    # return redirect(url_for('/'))


@socketio.on('cancel_download')
def handle_cancel_download():
    pass


@socketio.on('download')
def handle_download(json_str):
    data = json.loads(json_str)
    filename = extract_filename(data['url'])
    disk_location = pathlib.Path(data['disk_location'])

    disk_location.mkdir(parents=True, exist_ok=True)
    file_path = disk_location.joinpath(filename)

    msg = dict(
        msg="Downloading at: {}".format(str(file_path))
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

    urllib.request.urlretrieve(data['url'], str(file_path), show_progress)


def on_connect(client, userdata, flags, rc):
    client.subscribe(SWITCH_POWER_STATE_TOPIC)


def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('message', data=data)


def init_database(database_file):
    if not os.path.isfile(database_file):
        db.create_all()
        device = SwitchDevice(name="Sonoff")
        db.session.add(device)
        db.session.commit()


def get_device(name):
    return SwitchDevice.query.filter_by(name=name).first()


if __name__ == '__main__':
    client = mqtt.Client("Mqtt-controller", clean_session=True)
    client.on_connect = on_connect
    client.on_message = handle_mqtt_message
    mqtt_broker = "0.0.0.0"  # "192.168.0.15"
    client.connect(mqtt_broker)
    client.loop_start()
    init_database(datebase_file)

    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
