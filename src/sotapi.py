"""Stackexchange api interface """
import gzip
import json
import logging
import random
import time
import urllib.request as ur
import urllib.error
import datetime
from urllib.parse import quote

def sleep(min_time, max_time):
    time.sleep(random.randint(min_time, max_time))


def get_data(prefix, page_number=1, from_date=datetime.datetime(2008, 7, 28), to_date=datetime.datetime.now()):
    url = "http://api.stackexchange.com/2.2/{prefix}?" \
                  "page={page_num}&pagesize=100&" \
                  "fromdate={fromdate}&" \
                  "todate={todate}&" \
                  "site=stackoverflow&"\
                  "key={key}&"  \
                  "filter=!6JvKMTZy8(80_".format(prefix=quote(prefix),
                                                 key="gytnic74fozY)jD39pQSzg((",
                                                 page_num=page_number,
                                                 fromdate=int(from_date.timestamp()),
                                                 todate=int(to_date.timestamp()))
    logging.info('Fetching: ' + url)
    while True:
        try:
            resp = ur.urlopen(url)
            break
        except urllib.error.URLError as e:
            if e.errno != 110:  # Connection - timeout. Ignore it and try again
                raise
            else:
                sleep(3, 7)
    data = gzip.decompress(resp.read())
    data = json.loads(data.decode())
    return data


def get_tag_synonyms(tag):
    return get_data(prefix='tags/'+tag+'/synonyms')

if __name__ == "__main__":
    pass