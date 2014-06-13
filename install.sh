#!/bin/sh
apt-get install rabbitmq-server
apt-get install python-pip git-core
pip install -e git+https://github.com/pika/pika.git@v0.5.2#egg=pika-v0.5.2
