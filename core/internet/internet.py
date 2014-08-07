"""Some urllib wrappers"""
import random
import urllib.request as ur
import urllib.parse
import urllib.error
import time
from ..config import config

__author__ = 'user'



# i need this function sometimes
quote = urllib.parse.quote


def sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))


def get_from_url(url, min_delay=1, max_delay=3):
    req = ur.Request(url, headers=config['headers'])
    while True:
        try:
            response = ur.urlopen(req)
            break
        except urllib.error.HTTPError:
            sleep(min_delay, max_delay)
    data = response.read().decode()
    return data


if __name__ == "__main__":
    pass