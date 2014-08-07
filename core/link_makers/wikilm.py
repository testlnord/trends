""" Finds wikipedia pages for search term"""
import json
import re

from .link_maker import LinkMaker
from ..internet import google_search
from ..internet.internet import get_from_url
from ..internet.internet import sleep

class WikiLinkMaker(LinkMaker):
    @staticmethod
    def make_links(tech_name):
        page = WikiLinkMaker._get_wiki_page(tech_name)
        back_links = WikiLinkMaker._get_back_links(page)
        return [page] + back_links

    @staticmethod
    def _get_back_links(page):
        url = "http://en.wikipedia.org/w/api.php?action=query&" \
              "list=backlinks&" \
              "blfilterredir=redirects&" \
              "bltitle={0}&" \
              "bllimit=max&" \
              "format=json&" \
              "maxlag=5".format(page)

        for i in range(10):  # max attempts
            data = get_from_url(url)
            data = json.loads(data)
            if 'error' in data:
                sleep(7, 10)
                continue
            break

        backlinks = []
        for bl in data["query"]["backlinks"]:
            backlinks.append(bl["title"])
        return backlinks

    @staticmethod
    def _get_wiki_page(tech_name):
        wiki_name_pattern = re.compile('en\.wikipedia\.org/wiki/(.*)')
        wiki_name = None

        wiki_res = google_search.google_search(tech_name, cse_name='wiki')
        if 'items' not in wiki_res:
            print(wiki_res)
            raise KeyError("Nothing found in wikipedia")

        for item in wiki_res['items']:
            search = wiki_name_pattern.search(item['link'])
            if search:
                wiki_name = search.group(1)
                break

        return wiki_name

if __name__ == "__main__":
    pass