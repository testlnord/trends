"""Module uses ability to download csv files from google trends
"""
from io import StringIO
import urllib
import urllib.request
import datetime

#import contextlib
#import os
#import lxml.html as LH

__author__ = 'user'


from core.parsers.parser import Parser
import csv


class GoogleCsvParser(Parser):

    init_dir = "data/gcsv"
    browser = None

    def get_raw_data(self, response):
        reader_file = StringIO(response.decode())
        reader = csv.reader(reader_file, delimiter=',')
        start = False
        result = []
        for row in reader:
            if row and row[0] == 'Week':
                start = True
                continue
            if start and not row:
                break
            if start:
                d = datetime.datetime.strptime(row[0][:10], '%Y-%m-%d')
                if datetime.datetime.now() - datetime.timedelta(weeks=1) < d:
                    break
                v = int(row[1])
                result.append((d.date(), v))
        return result



if __name__ == '__main__':

    # This time, rather than install the OpenerDirector, we use it directly:

    proxy = 'http://117.59.217.236:81'
    proxy_dict = {'http': proxy}
    proxy_handler = urllib.request.ProxyHandler(proxy_dict)
    opener = urllib.request.build_opener(proxy_handler)
    resp = opener.open('http://google.com/trends')
    data = resp.read().decode()
    print(data)
    pass





