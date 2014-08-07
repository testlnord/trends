""" script for getting total count of questions on stack overflow per week
"""
import gzip
import random

__author__ = 'user'

import datetime
import pickle
import urllib.request as ur
import time
import json


start_week = datetime.datetime(2012, 7, 16)


def main(start_week, end_week = datetime.datetime.now()):
    result = []
    week = start_week
    next_week = week + datetime.timedelta(days=7)
    while next_week < end_week:


        url = "http://api.stackexchange.com/2.2/questions?" \
              "fromdate={0}&todate={1}&order=desc&sort=activity&site=stackoverflow&filter=!)V)MSZJYs)y".format(
              int(week.timestamp()), int(next_week.timestamp())
              )
        print(url)
        req = ur.Request(url)
        resp = ur.urlopen(req)
        data = resp.read()
        data = gzip.decompress(data)

        result.append((week, json.loads(data.decode())))
        print(result[-1])
        pickle.dump(result, open("total.pkl", 'wb'))
        time.sleep(random.randint(10, 15))

        week = next_week
        next_week = week + datetime.timedelta(weeks=1)



if __name__ == "__main__":
    main(start_week)