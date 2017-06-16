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


def list_of_dicts_to_dict(dictionary):                                          
    new_dict = {}                                                               
    key_name = 'entities'                                                       
    counter=1                                                                   
    for item in dictionary:                                                     
        name = key_name+str(counter)                                            
        new_dict[name] = item                                                   
        counter+=1                                                              
    return new_dict  


def flatten_dict(d, parent_key='', sep='__'):                                        
    items = []                                                                  
    for k, v in d.items(): 
        new_key = parent_key + sep + k if parent_key else k                     
        if isinstance(v, collections.MutableMapping):                           
            items.extend(flatten_dict(v, new_key, sep=sep).items())                 
        else:                                                                   
            items.append((new_key, v))                                          
    return dict(items)
