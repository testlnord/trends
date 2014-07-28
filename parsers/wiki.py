""" get and parse data about article page visits from wikipedia """

import json
import pickle
import re
from numpy import median
from parsers.parser import Parser
import urllib.request as ur
import urllib.error
import datetime
import pandas


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
            url = "http://stats.grok.se/json/en/" + month.strftime("%Y%m") + "/" + query
            req = ur.Request(url, headers=headers)
            try:
                response = ur.urlopen(req)
                month = datetime.date(month.year + int(month.month / 12), month.month % 12 + 1, 1)  # add a month
            except urllib.error.HTTPError:
                self.sleep(5, 10)
            data = response.read().decode("utf-8")
            result.append(data)
            self.sleep(5, 10)
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

    def get_data(self, raw_data):
        vals = [x for d, x in raw_data]
        med = median(vals)
        mad = median([abs(x - med) for x in vals])
        vals = [x if med - 3*mad < x < med + 3*mad else None for x in vals]
        try:
            df = pandas.DataFrame([0]+vals)
            df = df.interpolate()
            vals = list(df[0])[1:]
            data = [(d, vals[idx]) for idx, (d, _) in enumerate(raw_data)]
        except TypeError:
            data = raw_data
        print(data)
        return super().get_data(data)


if __name__ == '__main__':
    wp = WikiParser()
    wp.parse_fresh("azure")