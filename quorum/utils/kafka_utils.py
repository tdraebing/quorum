import os
import string
import random
import subprocess
from kafka import KafkaProducer, KafkaConsumer

signal_msg = 'live with more freedom than anyone else in the world!'


def produce_element(topic, element):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send(topic, element.encode('utf-8'))

def produce_iterator(topic, iterator):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    for i in iterator:
        producer.send(topic, i.encode('utf-8'))

def terminate_producer(topic):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')                
    producer.send(topic, signal_msg.encode('utf-8'))

def generate_id(length=6):                                                        
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits   
    return ''.join(random.choices(choices, k=length))                           
                                                                                
def generate_n_ids(n, length=6, ids=[]):                                                  
    ids = set(ids)                                                                 
    while len(ids)!=n and n>0:                                                  
        ids.add(generate_id(length))                                            
    return list(ids)                                                            

def generate_topic():
    existing_topics = existing_topics()
    while True:
        new_topic = generate_id()
        if new_topic not in existing_topics:
            create_kafka_topics([topic])
            return new_topic


def existing_topics():
    work_path = os.getcwd()                                                     
    kafka_path = work_path+'/KAFKA/kafka_2.11-0.10.2.0'
    list_topics = '/bin/kafka-topics.sh --list --zookeeper localhost:2181'
    topics = subprocess.run(list_topics, stdout=subprocess.PIPE)
    return topics.stdout.decode('utf-8').split('\n')

def create_kafka_topics(topics):   
    work_path = os.getcwd()                                                     
    kafka_path = work_path+'/KAFKA/kafka_2.11-0.10.2.0'                                                                                                     
    create_topic = '/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic '
    for topic in topics:                                                        
        subprocess.call(kafka_path + create_topic + topic, shell=True)
