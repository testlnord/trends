import pickle
import time

__author__ = 'user'

import urllib.request as ur
import gzip
from html.parser import HTMLParser


class ItjTechsParser(HTMLParser):
    tech_name = False
    names_list = []
    next = None


    def handle_starttag(self, tag, attrs):
        if ('class', 'c2') in attrs:
            self.tech_name = True
        if ('class', 'next') in attrs:
            self.next = dict(attrs)['href']

    def handle_data(self, data):
        if self.tech_name:
            self.tech_name = False
            self.names_list.append(data)


def main():
    result = []
    result_filename = 'itj_tags.pkl'

    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/35.0.1916.153 Safari/537.36",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "en-US,en;q=0.8",
        }
    url = "http://www.itjobswatch.co.uk/default.aspx?page=1&sortby=1&orderby=0&q=&id=0&lid=2618"
    parser = ItjTechsParser()

    while url is not None:
        req = ur.Request(url, headers=headers)
        response = ur.urlopen(req)
        data = response.read()
        html_data = gzip.decompress(data).decode()
        parser.feed(html_data)

        result.extend(parser.names_list)
        parser.names_list = []
        url = "http://www.itjobswatch.co.uk" + parser.next
        parser.next = None

        f_res = open(result_filename, 'wb')
        pickle.dump(result, f_res)
        f_res.close()

        print(url)
        print(result[-1])

        time.sleep(30)


if __name__ == '__main__':
    tags = pickle.load(open("itj_tags.pkl", 'rb'))
    print(len(tags))
    print(tags)