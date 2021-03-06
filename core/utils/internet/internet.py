"""Some urllib wrappers"""
import random
import urllib.request as ur
import urllib.parse
import urllib.error
import time
import re
from ...config import config
from http.client import BadStatusLine

__author__ = 'user'



# i need this function sometimes
quote = urllib.parse.quote
unquote = urllib.parse.unquote


def sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))


def get_from_url(url, min_delay=1, max_delay=3, binary=False, force_wait=False, max_attempts=10):
    """ urlopen wrapper
    Getting data for specified url, reads it from response and decoded it if binary set to False.
    If http error occurred it sleeps for random time and then tries again.
    :param url: url to open
    :param min_delay: min time to sleep
    :param max_delay: max time to sleep
    :param binary: data will not be decoded if binary specified
    :param force_wait: it will sleep not only after errors but before first request to.
    It's useful when you getting data in loop and don't want to DDOS destination server.
    :param max_attempts: number of attempts to get data if error occurred
    :return: string with read data if binary=True or bytes if binary=False
    :raise: reraised HTTPError exception after max attempts
    """
    req = ur.Request(url, headers=config['headers'])
    if force_wait:
        sleep(min_delay, max_delay)

    attempts = 0
    while True:
        try:
            response = ur.urlopen(req)
            break
        except (urllib.error.HTTPError, BadStatusLine):
            attempts += 1
            if attempts < max_attempts:
                sleep(min_delay, max_delay)
            else:
                raise

    data = response.read()
    if binary:
        return data
    else:
        return data.decode()


def is_valid_url(url: str) -> bool:
    """ URL validity checker
    Based on django URL-checking expression got from http://stackoverflow.com/questions/7160737/
    :param url: URL to check
    :return: True for valid URL, False otherwise
    """
    return bool(is_valid_url.url_re.match(url))

is_valid_url.url_re = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  #domain...
    r'localhost|'  #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


if __name__ == "__main__":
    pass