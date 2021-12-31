# Light weight smart home system

Many of the smart home systems (like openhab) is very bulky to install and they recommend to use at least RPi3 to run.
For simple use case, it is an overkill. On the other hand, I just want to make my idling RPi 1 useful.

It runs on RPi version 1 in docker, with python Flask
Currently just controlling one Sonoff swtich using MQTT, with support of scheduled power-on and off.

It contains also a simple http downloader for downloading files on RPi.
