import json
import pickle
import random
import re
from parsers.parser import Parser

__author__ = 'arkady'

"""get and parse data about article changes on wikipedia"""

import urllib.request as ur
import urllib.error
import html.parser
import datetime
import time


class WikiParser(Parser):
    init_dir = "data/wiki"
    wiki_links = None

    def get_response(self, query):
        if self.wiki_links is None:
            self.wiki_links = pickle.load(open('parsers/wiki_names.pkl', 'rb'))
        query = self.wiki_links[query.replace(' ', '-')]
        query = query[query.rindex('/'):]
        user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
        headers = {'User-Agent': user_agent}

        month = datetime.date(2007, 12, 1)
        result = []
        while month <= datetime.datetime.now().date():
            #print(month.strftime("%Y%m"))
            url = "http://stats.grok.se/json/en/" + month.strftime("%Y%m") + "/" + query
            req = ur.Request(url, headers=headers)
            try:
                response = ur.urlopen(req)
                month = datetime.date(month.year + int(month.month / 12), month.month % 12 + 1, 1)
            except urllib.error.HTTPError:
                time.sleep(random.randint(5, 10))
            data = response.read().decode("utf-8")
            result.append(data)
            time.sleep(random.randint(5, 10))
        return result

    def get_raw_data(self, response):

        result = []
        date_expr = re.compile('(\d*)-(\d\d)-(\d\d)')
        for line in response:
            d = json.loads(line)
            data = d['daily_views']
            for k in data:
                date_parsed = date_expr.match(k)
                if date_parsed:
                    date = datetime.date(int(date_parsed.group(1)), int(date_parsed.group(2)), 1)
                    date += datetime.timedelta(days=(int(date_parsed.group(3))-1))
                    result.append((date, data[k]))
        return result

if __name__ == '__main__':
    wp = WikiParser()
    wp.parse_fresh("azure")