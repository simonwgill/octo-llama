#!/bin/sh
echo $1 > /var/lib/rabbitmq/.erlang.cookie
echo $1 > $HOME/.erlang.cookie

if [ -n "$2" ];
then rabbitmqctl stop_app;
rabbitmqctl join_cluster --ram rabbit@$2;
fi
rabbitmq-plugins enable rabbitmq_management

service rabbitmq-server restart
