import os
import json
import datetime
import dataset
from kafka import KafkaProducer, KafkaConsumer
from quorum.producers.TwitterProducer import TwitterProducer
from quorum.utils.kafka_utils import signal_msg, generate_topic, terminate_producer
from quorum.consumers.twitter import flatten_tweet
from time import sleep
from collections import Counter


def tweets_to_db(tweetsTopic, db_uri='sqlite:///mydatabase.db'):
    db = dataset.connect(db_uri)
    db.begin()
    consumer = KafkaConsumer(tweetsTopic, auto_offset_reset='earliest',
                             enable_auto_commit=False, consumer_timeout_ms=3000)
    ids = set()
    counter = 0
    for tweet in consumer:
        if tweet.value.decode('utf-8')==signal_msg:    
            break
        tweet = json.loads(tweet.value.decode('utf-8'))

        if not tweet['id'] in ids:
            ids.add(tweet['id'])
        else:
            continue
        print(counter) 
        try:
            db['tweets'].insert(flatten_tweet(tweet))
            db.commit()
            counter += 1
        except Exception as e:
            db.rollback()
            continue
    print('Obtained: {}'.format(counter))

if __name__=="__main__":
    idsTopic = generate_topic()                                         
    tweetsTopic = generate_topic()
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1)
    print(start, '\t', end)
    scraper = TwitterProducer(virtuald=True)

    Total = 0
    line_num = 0
    users = [line.strip().strip('\n') for line in open('somefilewithtwitterusernames', 'r')]
    users = set(users)
    for user in users:
        line_num += 1
        print('user: ', line_num)
        tweets = scraper.get_tweet_ids(user, idsTopic, start, end, 
                                       topics=[], day_step=1, 
                                       tweet_lim=-1, no_rt=True,
                                       terminate_kafkaTopic=False)
        Total += tweets
        print('Tweets: ', tweets)
    terminate_producer(idsTopic)
    print('Obtained: {}'.format(Total))
    scraper.ids_to_tweets(idsTopic, tweetsTopic)
    tweets_to_db(tweetsTopic, db_uri='sqlite:///mydatabase.db')
