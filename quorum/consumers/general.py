import urllib.request

def get_url_domain(url):
    """ Get the domain for a url.
    
        Example:
            url = 'http://bit.ly/silly'
            returns 'www.google.com'
    """
    response = urllib.request.urlopen(url)
    return response.url.split('/')[2]
