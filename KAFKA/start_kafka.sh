#!/bin/bash

KAFKA_HOME=/home/alarcj/Documents/datasci/quorum/KAFKA/kafka_2.11-0.10.2.0
export KAFKA_HEAP_OPTS="-Xmx100M -Xms100M"

nohup $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties > /dev/null 2>&1 &
sleep 3
nohup $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties > /dev/null 2>&1 &

