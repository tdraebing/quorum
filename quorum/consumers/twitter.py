import collections
import datetime
from nltk.probability import FreqDist 
from nltk.tokenize import TweetTokenizer
from quorum.consumers.general import get_url_domain, list_of_dicts_to_dict   


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


def flatten_tweet(d, parent_key='', sep='__'):                                   
    items = []                                                                  
    for k, v in d.items():                                                      
        new_key = parent_key + sep + k if parent_key else k                     
        if isinstance(v, collections.MutableMapping):                           
            items.extend(flatten_tweet(v, new_key, sep=sep).items())             
        elif isinstance(v, list):                                               
            v = list_of_dicts_to_dict(v)                                        
            items.extend(flatten_tweet(v, new_key, sep=sep).items())
        else:                                                                   
            items.append((new_key, v))                                          
    return dict(items)
