import paho.mqtt.client as mqtt
import time


class Switch(object):
    def __init__(self):
        self._state = "OFF"

    def set_state(self, state):
        self._state = state

    @property
    def state(self):
        return self._state


class Controller(object):
    def __init__(self):
        self._client = mqtt.Client("controller")
        host = "raspberrypi.local"
        self._client.connect(host)
        self._switch_power_topic = "cmnd/sonoff-socket/POWER"
        self._switch_power_state_topic = "stat/sonoff-socket/POWER"
        self._switch_on_msg = "ON"
        self._switch_off_msg = "OFF"
        self._client.subscribe(self._switch_power_state_topic)
        self._client.on_message = self.on_message
        self._switch = Switch()
        self._callback_map = {self._switch_power_state_topic: self._switch_power_state_topic_cb}

    def get_switch(self):
        return self._switch

    def _switch_power_state_topic_cb(self, payload):
        self._switch.set_state(payload)

    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode("utf-8"))
        self._callback_map.get(message.topic, lambda _: None)(payload)

    def switch_on(self):
        self._client.publish(self._switch_power_topic, self._switch_on_msg)

    def switch_off(self):
        self._client.publish(self._switch_power_topic, self._switch_off_msg)

    def start(self):
        self._client.loop_start()

    def stop(self):
        self._client.loop_stop()


if __name__ == "__main__":
    controller = Controller()
    controller.switch_on()
    controller.start()
    time.sleep(4)
    controller.stop()
