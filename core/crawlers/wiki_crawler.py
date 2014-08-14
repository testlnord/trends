"""Crawls data from en.wikipedia"""
import datetime
import json
import logging
import re

from ..utils.internet import internet


__author__ = 'user'


class WikiCrawler:
    @staticmethod
    def get_data(page_name, date_from, date_to=None) -> list:
        if date_to is None:
            date_to = datetime.date.today()

        page_name = page_name.replace(" ", "_")
        logging.info("Getting wikipedia data for page: %s", page_name)
        month = datetime.date(date_from.year, date_from.month, 1)
        result = []

        date_pattern = re.compile('(\d*)-(\d\d)-(\d\d)')
        while month < date_to:
            logging.debug("Getting data for date: %s", month.strftime("%Y-%m"))

            url = "http://stats.grok.se/json/en/" + month.strftime("%Y%m") + "/" + internet.quote(page_name)
            data = internet.get_from_url(url)

            for day, value in json.loads(data)['daily_views'].items():
                date_parsed = date_pattern.match(day)
                if date_parsed:
                    # I have to make 1st day of month and then add days,
                    # cause response contains dates like '2012-02-31'
                    # which is '2012-03-02' really
                    date = datetime.date(int(date_parsed.group(1)), int(date_parsed.group(2)), 1)
                    date += datetime.timedelta(days=(int(date_parsed.group(3)) - 1))
                    if date >= date_from:
                        result.append((date, value))

            month = datetime.date(month.year + int(month.month / 12), month.month % 12 + 1, 1)  # add a month
        return result


if __name__ == "__main__":
    pass