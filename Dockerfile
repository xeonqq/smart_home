FROM balenalib/rpi-debian-python:3.7.4

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc g++ python3-dev


COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /usr/src/app

ENTRYPOINT [ "python", "./app.py" ]
