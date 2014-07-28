__author__ = 'arkady'

""" getting and parsing trends from plot on http://hewgill.com/~greg/stackoverflow/stack_overflow/tags/"""

import urllib.request as ur
import re
import datetime
from parsers.parser import Parser


class SOTParser(Parser):
    init_dir = "data/sot"

    def get_response(self, query):
        query = query.replace(" ", "-")
        data = self.get_resp_impl(query)
        total = self.get_resp_impl("_total")
        return data + '\n' + total

    def get_raw_data(self, response):
        plot_pattern = re.compile("\[(\d*), (\d*)\]")

        response = response.splitlines()

        total = []
        for match in plot_pattern.finditer(response[1]):
            d = int(match.group(1))
            v = int(match.group(2))
            total.append((d, v))
        query = []
        for i, match in enumerate(plot_pattern.finditer(response[0])):
            d = int(match.group(1))
            v = int(match.group(2))
            query.append((d, v))

        result = []
        date = datetime.date(2008, 7, 28)
        q_idx = 0
        for d, v in total:
            if d < query[q_idx][0]:
                result.append((date, 0))
            else:
                result.append((date, query[q_idx][1]/v))
                q_idx += 1
            date += datetime.timedelta(weeks=1)
        return result

    def get_resp_impl(self, query):
        url = "http://hewgill.com/~greg/stackoverflow/stack_overflow/tags/"+query+".json"
        user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
        headers = {'User-Agent': user_agent}

        req = ur.Request(url, headers=headers)
        response = ur.urlopen(req)
        data = response.read().decode("utf-8")
        return data

