""" """
from html.parser import HTMLParser
import logging
import re

from core.utils.internet import google_search
from .link_maker import LinkMaker
from ..utils.internet.internet import unquote

class SotLinkMaker(LinkMaker):
    def __init__(self):
        self.so_tag_link_pattern = re.compile('http://stackoverflow.com/tags/(.*)/info')

    def make_links(self, tech_name):
        sot_res = google_search.google_search(tech_name, cse_name='sot')
        if 'items' not in sot_res:
            logging.warning("Nothing googled for stackoverflow, query: %s", tech_name)
            logging.debug("Google response: %s", sot_res)
            raise KeyError("Nothing found in stackoverflow")

        sot_tag = None
        for item in sot_res['items']:
            search = self.so_tag_link_pattern.search(item['link'])
            if search:
                sot_tag = unquote(search.group(1))
                logging.debug("SO founded link: %s", item['link'])
                logging.info("SO founded tag: %s", sot_tag)
                break

        return sot_tag

if __name__ == "__main__":
    pass