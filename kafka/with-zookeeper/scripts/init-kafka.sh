#!/bin/bash

if [ -z "$ZOOKEEPER_CONNECT" ]; then
    echo '[SYSTEM] $ZOOKEEPER_CONNECT must be defined!'
    exit 1
fi


if [ -z "$KAFKA_BROKER_ID" ]; then
    echo '[SYSTEM] $KAFKA_BROKER_ID will be parsed from hostname'
    KAFKA_BROKER_ID=$(hostname | grep -Eo '[0-9]+')
fi

if [ -z "$KAFKA_PORT" ]; then
    echo '[SYSTEM] $KAFKA_PORT will be set to default 9092, due to not defined'
    KAFKA_PORT=9092
fi

tee -a $KAFKA_CONF_DIR/server.properties << EOF

# followings are added from the init-kafka.sh:

listeners=PLAINTEXT://:$KAFKA_PORT
advertised.listeners=PLAINTEXT://$(hostname):$KAFKA_PORT
broker.id=$KAFKA_BROKER_ID
log.dirs=/data/kafka/logs
zookeeper.connect=$ZOOKEEPER_CONNECT
EOF

kafka-server-start.sh $KAFKA_CONF_DIR/server.properties
