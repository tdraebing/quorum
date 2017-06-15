#!/bin/bash

KAFKA_HOME=/home/alarcj/Documents/datasci/quorum/KAFKA/kafka_2.11-0.10.2.0

topics=($(${KAFKA_HOME}/bin/kafka-topics.sh --list --zookeeper localhost:2181))
total=${#topics[*]}
for (( i=0; i<=$(( $total -1 )); i++ ))
do
	if [ ${topics[$i]} != "__consumer_offsets" ]; then 
		$KAFKA_HOME/bin/kafka-topics.sh --delete \
			--zookeeper localhost:2181 --topic ${topics[$i]}
	fi
done
