#!/bin/sh

echo deb http://www.rabbitmq.com/debian/ testing main > /etc/apt/sources.list.d/rabbit.list
echo deb http://www.apache.org/dist/cassandra/debian 11x main > /etc/apt/sources.list.d/cassandra.list
echo deb-src http://www.apache.org/dist/cassandra/debian 11x main >> /etc/apt/sources.list.d/cassandra.list

gpg --keyserver pgp.mit.edu --recv-keys F758CE318D77295D
gpg --export --armor F758CE318D77295D | apt-key add -

gpg --keyserver pgp.mit.edu --recv-keys 2B5C1B00
gpg --export --armor 2B5C1B00 | apt-key add -

wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
apt-key add rabbitmq-signing-key-public.asc

apt-get update
apt-get install rabbitmq-server -y
apt-get install cassandra -y
apt-get install python-pip git-core gcc -y
pip install -e git+https://github.com/pika/pika.git@v0.5.2#egg=pika-v0.5.2
pip install pycassa
pip install twython
