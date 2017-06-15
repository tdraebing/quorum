import os
import string
import random
import subprocess
from kafka import KafkaProducer, KafkaConsumer

signal_msg = 'live with more freedom than anyone else in the world!'


def produce_element(topic, element):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send(topic, element.encode('utf-8'))
    producer.flush() 

def produce_iterator(topic, iterator):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    for i in iterator:
        future = producer.send(topic, i.encode('utf-8'))
    producer.flush()

def terminate_producer(topic):
    produce_element(topic, signal_msg)

def generate_id(length=6):                                                        
    choices = string.ascii_lowercase + string.ascii_uppercase + string.digits   
    return ''.join(random.choices(choices, k=length))                           
                                                                                
def generate_n_ids(n, length=6, ids=[]):                                                  
    ids = set(ids)                                                                 
    while len(ids)!=n and n>0:                                                  
        ids.add(generate_id(length))                                            
    return list(ids)                                                            

def existing_topics():
    work_path = os.getcwd()                                                     
    kafka_path = work_path+'/KAFKA/kafka_2.11-0.10.2.0'
    list_topics = [
        kafka_path+'/bin/kafka-topics.sh', '--list', '--zookeeper', 'localhost:2181'
    ]
    topics = subprocess.run(list_topics, stdout=subprocess.PIPE)
    return topics.stdout.decode('utf-8').split('\n')

def generate_topic():                                                           
    existing = existing_topics()                                         
    while True:
        new_topic = generate_id()                                               
        if new_topic not in existing:
            create_kafka_topics([new_topic])                                        
            return new_topic

def create_kafka_topics(topics):   
    work_path = os.getcwd()                                                     
    kafka_path = work_path+'/KAFKA/kafka_2.11-0.10.2.0'                                                                                                     
    create_topic = '/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic '
    for topic in topics:                                                        
        subprocess.call(kafka_path + create_topic + topic, shell=True)
