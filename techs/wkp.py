import pickle
import time

__author__ = 'user'

import urllib.request as ur
import http.client
import gzip
from html.parser import HTMLParser
from collections import deque

class WikiTechsParser(HTMLParser):
    state = ''
    state_depth = 0
    pages = []
    cats = []
    depth = 0

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        if ('id', 'mw-subcategories') in attrs:
            self.state_depth = self.depth
            self.state = 'subcats'
        elif ('id', 'mw-pages') in attrs:
            self.state_depth = self.depth
            self.state = 'pages'
        elif self.state == 'subcats' and tag == 'a':
            self.cats.append(dict(attrs)['href'])
        elif self.state == 'pages' and tag == 'a':
            attrs = dict(attrs)
            try:
                self.pages.append((attrs['href'], attrs['title']))
            except KeyError:
                pass  # it`s ok here, i need just <a>s with href

    def handle_endtag(self, tag):
        self.depth -= 1
        if self.state_depth > self.depth:
            self.state = ''
            self.state_depth = 0

    def refresh(self):
        self.state = ''
        self.pages = []
        self.cats = []
        self.depth = 0

def main():

    result_filename = 'wkp_tags.pkl'
    result = pickle.load(open(result_filename, 'rb'))
    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/35.0.1916.153 Safari/537.36",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "en-US,en;q=0.8",
        }
    url_list = pickle.load(open('to_visit', 'rb'))
    visited_urls = pickle.load(open('visited', 'rb'))
    parser = WikiTechsParser()
    while url_list:
        url = url_list.popleft()
        if url in visited_urls:
            continue

        req = ur.Request("http://en.wikipedia.org" + url, headers=headers)
        try:
            response = ur.urlopen(req)
        except http.client.BadStatusLine:
            url_list.append(url)
            time.sleep(10)
            continue

        data = response.read()
        html_data = gzip.decompress(data).decode()

        parser.feed(html_data)

        url_list.extend(parser.cats)
        result.extend(parser.pages)
        parser.refresh()

        time.sleep(30)

        print(url)
        visited_urls.add(url)
        pickle.dump(result, open(result_filename, 'wb'))
        pickle.dump(url_list, open('to_visit', 'wb'))
        pickle.dump(visited_urls, open('visited', 'wb'))

if __name__ == '__main__':
    pass
