import collections
import urllib.request


def get_url_domain(url):
    """ Get the domain for a url.
    
        Example:
            url = 'http://bit.ly/silly'
            returns 'www.google.com'
    """
    response = urllib.request.urlopen(url)
    return response.url.split('/')[2]


def flatten(d, parent_key='', sep='__'):                                        
    items = []                                                                  
    for k, v in d.items(): 
        new_key = parent_key + sep + k if parent_key else k                     
        if isinstance(v, collections.MutableMapping):                           
            items.extend(flatten(v, new_key, sep=sep).items())                  
        else:                                                                   
            items.append((new_key, v))                                          
    return dict(items)
