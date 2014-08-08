"""Crawls data from stackoverflow"""
import datetime
import gzip
import json
import logging
import re
from ..config import config
from ..utils.internet import internet


__author__ = 'user'


class SotCrawler:
    @staticmethod
    def get_data(tag, date_from, date_to=datetime.datetime.now().date()) -> list:
        tag = internet.quote(tag.replace(" ", "-"))
        result = []
        week = date_from
        next_week = week + datetime.timedelta(weeks=1)
        while next_week < date_to:
            url = "http://api.stackexchange.com/2.2/questions?" \
                  "fromdate={0}&" \
                  "todate={1}&" \
                  "key={2}&" \
                  "order=desc&sort=activity&site=stackoverflow&filter=!)V)MSZJYs)y".format(
                  int(week.timestamp()), int(next_week.timestamp()), internet.quote(config["sources"]["so"]["apikey"])
                  )
            url += "&tagged={0}".format(tag)
            logging.debug("Generated url fo SO: " + url)
            data = internet.get_from_url(url, 3, 7, binary=True)
            data = gzip.decompress(data)
            response = json.loads(data.decode())
            count = response["total"]

            result.append((week, count))
            print(' ', result[-1])

            internet.sleep(1, 2)

            week = next_week
            next_week = week + datetime.timedelta(weeks=1)

        return result

if __name__ == "__main__":
    pass