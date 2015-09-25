"""Crawls data from stackoverflow"""
import datetime
import gzip
import json
import logging
from ..utils.internet import internet


__author__ = 'user'


class OutOfApiQuotaException(Exception):
    pass


class SotCrawler:

    def __init__(self, apikey):
        self.apikey = apikey
        self.logger = logging.getLogger(__name__)

    def get_data(self, tag, date_from, date_to=None) -> list:
        if date_to is None:
            date_to = datetime.datetime.today()
        try:
            date_from.hour
        except:
            date_from = datetime.datetime.fromordinal(date_from.toordinal())
        #date_from -= datetime.timedelta(days=-date_from.weekday())  # getting monday date

        tag = internet.quote(tag.replace(" ", "-"))
        result = []
        week = date_from
        next_week = week + datetime.timedelta(weeks=1)
        while next_week < date_to:
            url = "http://api.stackexchange.com/2.2/questions?" \
                  "fromdate={0}&" \
                  "todate={1}&" \
                  "key={2}&" \
                  "order=desc&sort=activity&site=stackoverflow&filter=!GeF-5sJS7jmzL".format(
                  int(week.timestamp()), int(next_week.timestamp()), internet.quote(self.apikey)
                  )
            if tag:
                url += "&tagged={0}".format(tag)
            self.logger.debug("Generated url fo SO: " + url)
            data = internet.get_from_url(url, 1, 4, binary=True, force_wait=True)
            data = gzip.decompress(data)
            response = json.loads(data.decode())
            self.logger.debug("Response: %s", data.decode())
            count = response["total"]
            if response["quota_remaining"] < 10:
                self.logger.warning("Stackoveflow crawler is out of quota.")
                raise OutOfApiQuotaException
            result.append((week, count))
            self.logger.debug('Data portion last line: %s',  str(result[-1]))

            internet.sleep(1, 2)

            week = next_week
            next_week = week + datetime.timedelta(weeks=1)

        return result

if __name__ == "__main__":
    pass