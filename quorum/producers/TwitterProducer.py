import os
import json
import datetime
from time import sleep
from tweepy import API, OAuthHandler, Cursor, TweepError
from kafka import KafkaConsumer
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from quorum.producers.SeleniumProducer import SeleniumProducers
from quorum.utils.file_utils import create_dir
from quorum.utils.kafka_utils import (produce_iterator, terminate_producer, 
                                      signal_msg, produce_element, generate_topic)


class TwitterProducer(SeleniumProducers):
    """
    TwitterProducer.api
    TwitterProducer.get_tweet_ids(screen_name, produceTopic, start, end, 
                                  topics=[], day_step=2, tweet_lim=3200, 
                                  no_rt=True)
    TwitterProducer.ids_to_tweets(consumeTopic, produceTopic)
    TwitterProducer.get_tweets(self, screen_name, start, end, topics=[], 
                               day_step=2, tweet_lim=3200,  no_rt=True)
    """

    def __init__(self, virtuald=True, driver='firefox'):
        super().__init__(virtuald, driver) 
        self.api = self._twitter_client()


    def _twitter_client(self):
        from quorum.config.config import TWITTER
        auth = OAuthHandler(TWITTER["CONSUMER_KEY"], TWITTER["CONSUMER_SECRET"])
        auth.set_access_token(TWITTER["ACCESS_TOKEN"], TWITTER["ACCESS_SECRET"])
        api = API(auth, wait_on_rate_limit=True,  wait_on_rate_limit_notify=True,
                  compression=True)
        return api


    def twitter_url(self, screen_name='', no_rt=True, start='', end='', hashtag='', topics=[]):                                         
        # join url parts                                                            
        union = '%20'                                                               
        union_topic = '%20OR%20'                                                    
        url = ['https://twitter.com/search?f=tweets&q=']                            
        if hashtag:                                                                 
            url.append('%23' + hashtag.strip('#') + '%20')                          
        if topics:                                                                  
            url.append( union_topic.join(topics) )                                  
        if screen_name:                                                             
            url.append( 'from%3A' + screen_name )                                   
        if start:                                                                   
            url.append( 'since%3A' + start.strftime('%Y-%m-%d') )                   
        if end and hashtag:                                                         
            url.append( '%20until%3A' + end.strftime('%Y-%m-%d') )                  
        else:                                                                       
            url.append( 'until%3A' + end.strftime('%Y-%m-%d') )                     
        if no_rt:                                                                   
            url.append( '&src=typd' )                                               
        else:                                                                       
            url.append( 'include%3Aretweet&src=typd' )                              
        if hashtag:                                                                 
            return ''.join( url )                                                   
        else:                                                                       
            return union.join( url )

    
    def get_tweet_ids(self, screen_name, produceTopic, start, end, topics=[], 
                      day_step=2, tweet_lim=3200, no_rt=True,
                      terminate_kafkaTopic=False):
        self.start_driver()

        totalTweets = 0
        end_date = start
        while start<=end and (totalTweets<=tweet_lim or 0>tweet_lim):
            end_date += datetime.timedelta(days=day_step)
            url = self.twitter_url(screen_name=screen_name, no_rt=no_rt, 
                                   start=start, end=end_date, topics=topics)
            try:
                self.driver.get(url)

                self._found_tweets = self._scroll_and_get_tweets()
                totalTweets += self._save_tweetIds(produceTopic, tweet_lim) 
                
                start = end_date
            except NoSuchElementException as e:
                sleep(1*60)
                continue
            except TimeoutException:
                sleep(1*60)
                continue
        if terminate_kafkaTopic:
            terminate_producer(produceTopic)
        self.terminate_driver()
        return totalTweets


    def _scroll_and_get_tweets(self): 
        found_tweets = self.driver.find_elements_by_css_selector('li.js-stream-item')
        increment = 10
        while len(found_tweets) >= increment:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(1)
            found_tweets = self.driver.find_elements_by_css_selector('li.js-stream-item')
            increment += 10
        return found_tweets


    def _save_tweetIds(self, produceTopic, tweet_lim): 
        ids = []
        for tweet in self._found_tweets: 
            try:
                tweet_id = tweet.get_attribute('data-item-id')
                ids.append(tweet_id)

            except StaleElementReferenceException as e:
                continue
        if ids:
            produce_iterator(produceTopic, set(ids))
        return len(ids)


    def ids_to_tweets(self, consumeTopic, produceTopic):
        consumer = KafkaConsumer(consumeTopic, auto_offset_reset='earliest',
                                 enable_auto_commit=False)  
        for msg in consumer:
            if msg.value.decode('utf-8')==signal_msg:
                break
            try:
                tweet = self.api.get_status(msg.value.decode('utf-8'))    
                produce_element(produceTopic, json.dumps(tweet._json))
            except TweepError as e:
                print(e)
                sleep(15*60)
        terminate_producer(produceTopic)


    def get_tweets(self, screen_name, start, end, idsTopic='', tweetsTopic='', 
                   topics=[], day_step=2, tweet_lim=3200,  no_rt=True):
        if not idsTopic and not tweetsTopic:
            idsTopic = generate_topic() 
            tweetsTopic = generate_topic()                                              
            
        tweets = self.get_tweet_ids(screen_name, idsTopic, start, end, 
                                    topics=topics, day_step=day_step, 
                                    tweet_lim=3200, no_rt=no_rt)                      
        self.ids_to_tweets(idsTopic, tweetsTopic) 
        return tweetsTopic, tweets
