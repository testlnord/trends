""" getting and parsing trends right from stackoverlfow """
import gzip
import json
import os
import pickle

__author__ = 'arkady'



import urllib.request as ur
import urllib.error
import datetime
from core.parsers.parser import Parser
from urllib.parse import quote


class SOTParser(Parser):
    init_dir = "data/sot_my"
    start_week = datetime.datetime(2008, 7, 28)
    end_week = datetime.datetime.now()

    def __init__(self):
        super(SOTParser).__init__()
        self.total = dict(pickle.load(open(os.path.join(self.init_dir, "t/response"), 'rb')))

    def get_response(self, query):
        tag = quote(query.replace(" ", "-"))
        result = []
        week = self.start_week
        next_week = week + datetime.timedelta(days=7)
        print(tag)
        while next_week < self.end_week:
            url = "http://api.stackexchange.com/2.2/questions?" \
                  "fromdate={0}&" \
                  "todate={1}&" \
                  "key={2}&" \
                  "order=desc&sort=activity&site=stackoverflow&filter=!)V)MSZJYs)y".format(
                  int(week.timestamp()), int(next_week.timestamp()), quote("gytnic74fozY)jD39pQSzg((")
                  )
            if not tag == "t":
                url += "&tagged={0}".format(tag)
            print(' ', url)
            req = ur.Request(url)
            print(req.get_full_url())
            while True:
                try:
                    resp = ur.urlopen(req)
                    break
                except urllib.error.URLError as e:
                    if e.errno != 110:  # Connection - timeout. Ignore it and try again
                        raise
                    else:
                        self.sleep(3, 7)

            data = resp.read()
            data = gzip.decompress(data)

            result.append((week, json.loads(data.decode())))
            print(' ', result[-1])
            self.sleep(1, 3)

            week = next_week
            next_week = week + datetime.timedelta(weeks=1)

        return result

    def get_raw_data(self, response):
        result = []
        total_idx = 0
        for date, v in response:
            # while date < self.total[date]:
            #     total_idx += 1
            v = v["total"]
            try:
                v_t = self.total[date]["total"]
                result.append((date.date(), v/v_t))
            except KeyError:
                pass # ignore missing data, will interpolate later
        return result


