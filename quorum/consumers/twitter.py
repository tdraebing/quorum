import datetime
from nltk.probability import FreqDist 
from nltk.tokenize import TweetTokenizer
from quorum.consumers.general import get_url_domain 

def convert_tweet_date(jsonTweet):
    """ Convert the datetime format of a tweet. 
    
    """
    informat = '%a %b %d %H:%M:%S %z %Y'                
    outformat = '%Y-%m-%d %H:%M:%S %Z'
    date = datetime.datetime.strptime(jsonTweet['created_at'], informat)
    return date.strftime(outformat)


def get_tweet_urls(jsonTweet, unshorten=True):
    urls = []
    for url in jsonTweet['entities']['urls']:
        if unshorten:
            url = get_url_domain(url)
        urls.append(url['expanded_url'])


def Tweet_freq_dist(tweet):
    tokenizer =  TweetTokenizer()
    return FreqDist(tokenizer.tokenize(tweet)) 
