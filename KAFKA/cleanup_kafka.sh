#!/bin/bash

KAFKA_HOME=/home/alarcj/Documents/datasci/quorum/KAFKA

topics=($(${KAFKA_HOME}/bin/kafka-topics.sh --list --zookeeper localhost:2181))
for topic in ${topics[@]}; do
	$KAFKA_HOME/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic $topic 
done
