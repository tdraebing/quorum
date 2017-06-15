#!/bin/bash


sudo apt-get update -y && sudo apt-get upgrade -y

# Install Oracle JDK 8 using the Webupd8 team PPA repo
sudo add-apt-repository -y ppa:webupd8team/java 
sudo apt-get update -y && sudo apt-get install -y oracle-java8-installer 

# Install Zookeeper open source service for maintaining configuration
# information, providing distributed synchronization, naming and providing
# group services.
sudo apt-get install -y zookeeperd


# Download Kafka
curl http://apache.spinellicreations.com/kafka/0.10.2.0/kafka_2.11-0.10.2.0.tgz | tar xz
cd kafka_2.11-0.10.2.0

