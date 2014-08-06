"""parse google trends info to adequate data"""
__author__ = 'arkady'

import urllib.request as ur
import re
import datetime

from src.parsers.parser import Parser


class GoogleParser(Parser):

    """parser of google trends"""

    init_dir = "data/google"

    def get_response(self, query):
        query = '%20'.join(query.split(' '))
        url = "http://www.google.com/trends/fetchComponent?q="+query+"&cid=TIMESERIES_GRAPH_0&export=3"
        user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = ur.Request(url, headers=headers)
        self.sleep(120, 600)
        response = ur.urlopen(req)
        data = response.read().decode("utf-8")
        return data

    def get_raw_data(self, response):
        data = response[response.index('rows')+7:-5]
        data_extractor = re.compile('\{\"c\":\[\{\"v\":new Date\(([\d]*),([\d]*),([\d]*)[^\}]*\},\{\"v\":([\.\d]*)')
        result = []

        for match in data_extractor.finditer(data):
            date = datetime.date(int(match.group(1)), int(match.group(2))+1, int(match.group(3)))
            result.append((date, float(match.group(4))))

        return result






