import os
import datetime
from time import sleep
from tweepy import API, OAuthHandler, Cursor, TweepError
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from quorum.cpnsumers.SeleniumConsumers import SeleniumConsumers
from quorum.utils.file_utils import create_dir


class TwitterConsumer(SeleniumConsumers):

    def __init__(self, virtuald=True, driver='firefox'):
        super().__init__(virtuald, driver) 
        self.api = _twitter_client()


    def _twitter_client(self):
        from quorum.config.config import TWITTER
        auth = OAuthHandler(TWITTER["CONSUMER_KEY"], TWITTER["CONSUMER_SECRET"])
        auth.set_access_token(TWITTER["ACCESS_TOKEN"], TWITTER["ACCESS_SECRET"])
        api = API(auth, wait_on_rate_limit=True,  wait_on_rate_limit_notify=True,
                  compression=True)
        return api


    def twitter_url(self, screen_name='', no_rt=False, start='', end='', hashtag='', topics=[]):                                         
        # join url parts                                                            
        union = '%20'                                                               
        union_topic = '%20OR%20'                                                    
        
        # construct the various parts of the search url                             
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

    
    def get_all_user_tweets(self, screen_name, hashtag='', topics=[], start, end, 
                            day_step=2, tweet_lim=3200, no_rt=True, virtuald=False):
   
        self.start_driver()
        path = create_dir(urls=[screen_name], data_dir='data')                  
        checkpoint_filename = path +'/tweetIds_checkpoints_file.txt'
        ids_filename = path + '/tweetIds.jsonl'
        checkpoint_file, start = self.restart_crawl(checkpoint_filename)
        start = datetime.datetime.strptime(start[-1],"%Y-%m-%d %H:%M:%S")

        while start<=end:
            end_date += datetime.timedelta(days=day_step)
            url = twitter_url(screen_name=screen_name, no_rt=no_rt, start=start_date, 
                              end=end_date, topics=topics)
            try:
                self.driver.get(url)

                self._found_tweets = self._scroll_and_get_tweets()
                self._save_tweetIds(ids_filename)         
                
                checkpoint_file.write( '{}\n'.format(start) )
                start = end_date
            except NoSuchElementException as e:
                sleep(1*60)
                continue
            except TimeoutException:
                sleep(1*60)
                continue
        
        checkpoint_file.close()
        self.terminate_driver()
        return len(ids)


    def _scroll_and_get_tweets(self): 
        found_tweets = self.driver.find_elements_by_css_selector('li.js-stream-item')
        increment = 10
        while len(found_tweets) >= increment:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(1)
            found_tweets = self.driver.find_elements_by_css_selector('li.js-stream-item')
            increment += 10
        return found_tweets


    def _save_tweetIds(self, filename):
        ids = []
        with open(filename, 'a') as fout:
            for tweet in self._found_tweets:
                try:
                    tweet_id = tweet.get_attribute('data-item-id')
                    ids.append(tweet_id)

                    if len(ids) == tweet_lim:
                        fout.write(json.dumps(list(set(ids)))+'\n')
                        self.terminate_driver()
                        return len(ids)
                except StaleElementReferenceException as e:
                    continue
            if ids:
                fout.write(json.dumps(list(set(ids)))+'\n')
        return len(ids)


    def ids_to_tweets(self, path_to_ids):
        ids_file = path_to_ids + '/tweetIds.jsonl'
        ftweets = path_to_ids + '/tweets.jsonl'
        checkpoint_filename = path_to_ids + '/tweets_checkpoints_file.txt'
        checkpoint_file, checkpoints = self.restart_crawl(checkpoint_filename)

        with open(ids_file, 'r') as f, open(ftweets, 'a') as f_tweet:
            if checkpoints:
                f.seek(int(checkpoints[-1]))
            
            for line in iter(f.readline, ''):
                checkpoint_file.write('{}\n'.format(f.tell()))
                ids = json.loads(line)

                for tweetId in ids:
                    try:
                        tweet = self.api.get_status(tweetId)
                        f_tweet.write(json.dumps(tweet._json)+'\n')
                    except TweepError as e:
                        print(e)
                        time.sleep(60*15)

        checkpoint_file.close() 

