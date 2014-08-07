""" get and parse data about article changes on wikipedia """

import urllib.request as ur
import html.parser
import datetime

from core.parsers.parser import Parser


class WikiParser(Parser):
    init_dir = "data/wiki"

    def get_response(self, query):
        url = "http://en.wikipedia.org/w/index.php?title="+query+"&dir=prev&limit=1000000&action=history"
        user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = ur.Request(url, headers=headers)
        response = ur.urlopen(req)
        data = response.read().decode("utf-8")
        return data

    class WikiDatesParser(html.parser.HTMLParser):
        date_link = False
        result = []

        def handle_starttag(self, tag, attrs):
            if tag == "a" and ("class", "mw-changeslist-date") in attrs:
                self.date_link = True

        def handle_endtag(self, tag):
            if self.date_link:
                self.date_link = False

        def handle_data(self, data):
            if self.date_link:
                self.result.append(datetime.datetime.strptime(data, "%H:%M, %d %B %Y"))

    @staticmethod
    def month_eq(date1, date2):
        return date1.year == date2.year and date1.month == date2.month

    def get_raw_data(self, response):
        parser = self.WikiDatesParser()
        parser.feed(response)
        result = []

        for d in parser.result:
            if result != [] and self.month_eq(result[-1][0], d):
                result[-1][1] += 1
            else:
                result.append([datetime.date(d.year, d.month, 1), 1])

        return result

if __name__ == '__main__':
    WikiParser.init_dir = '../' + WikiParser.init_dir
    wp = WikiParser()
    wp.parse("Microsoft_SharePoint")