import datetime
from quorum.producers.TwitterProducer import TwitterProducer

if __name__=="__main__":
    start = datetime.datetime(2017, 6, 8)                                     
    end   = datetime.datetime.now()

    scraper = TwitterProducer(virtuald=False)
    scraper.get_all_user_tweets('jonathonmorgan', 
                                start, end, 
                                tweet_lim=3200, no_rt=True)

