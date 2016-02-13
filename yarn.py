import urllib.request, urllib.error, urllib.parse
import random
from bs4 import BeautifulSoup

user_agents = [
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5',
    'Mozilla/5.0 (Windows; Windows NT 6.1; rv:2.0b2) Gecko/20100720 Firefox/4.0b2',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
    'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
]


def build_request(url, data=None):
    # proxy_support = urllib.request.ProxyHandler({'https': '127.0.0.1:9050'})
    # opener = urllib.request.build_opener(proxy_support)
    # urllib.request.install_opener(opener)
    if data is not None:
        data = urllib.parse.urlencode(data)
        print(data)
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            'User-Agent': random.choice(user_agents)
        }
    )
    return request


def get_page_html(url, data=None, decoding=None):
    try:
        html = urllib.request.urlopen(url=build_request(url, data))
    except urllib.error.HTTPError as e:
        # print('Error Code: {} returned on HTTP request'.format(e.code))
        raise urllib.error.HTTPError
    except Exception as e:
        # print('Exception raised: {}'.format(e))
        raise e
    else:
        # print('Decoding HTML to utf-8')
        if decoding is None:
            decoded_data = html.read()
            return decoded_data
        try:
            decoded_data = html.read().decode(decoding)
        except Exception as e:
            # print('Decoding exception: {}'.format(e))
            raise e
    return decoded_data


def soup_page(url, data=None, decoding=None):
    soup = ''
    try:
        if decoding is not None:
            html_data = get_page_html(url, data, decoding)
        else:
            html_data = get_page_html(url, data, None)
    except Exception as e:
        print('Exception: {}'.format(e))
    else:
        soup = BeautifulSoup(html_data, 'lxml')
    return soup
