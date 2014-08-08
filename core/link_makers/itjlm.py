""" """
from html.parser import HTMLParser
import logging
import re

from core.utils.internet import google_search
from .link_maker import LinkMaker
from ..utils.internet.internet import get_from_url, quote
from ..utils.internet.internet import sleep


class ItjLinkMaker(LinkMaker):

    def make_links(self, tech_name):
        itj_tag_link_pattern = re.compile('http://www.itjobswatch.co.uk/jobs/uk/(.*).do')
        
        itj_res = ItjLinkMaker._search_itj(tech_name)
        if not itj_res['items']:
            logging.warning("Nothing found in itjobs website for request: %s.", tech_name)
            itj_res = google_search(tech_name, cse_name='itjobs')

        if 'items' not in itj_res:
            logging.warning("Nothing found in itjobs for request: %s. Last response: %s", tech_name, itj_res)
            raise KeyError()
        
        itj_name = None
        for item in itj_res['items']:
            search = itj_tag_link_pattern.search(item['link'])
            if search:
                itj_link = item['link']
                logging.info("Itjobs link found: %s", itj_link)
                itj_name = self._get_itj_image_name(itj_link)
                logging.info("Itjobs picture name: %s", itj_name)
                break
            
        return itj_name

    class ItjSearchParser(HTMLParser):
        result = []
        table_start = False
        read_link = False
        
        def handle_starttag(self, tag, attrs):
            if tag == 'table' and ('class', 'results') in attrs:
                self.table_start = True
            elif self.table_start and tag == 'td' and ('class', 'c2') in attrs:
                self.read_link = True
            elif self.read_link and tag == 'a':
                attrs = dict(attrs)
                self.result.append({'link': 'http://www.itjobswatch.co.uk' + attrs['href'], 'title': attrs['title']})
                self.read_link = False
    
    
    @staticmethod
    def _search_itj(tech_name):
        url = "http://www.itjobswatch.co.uk/default.aspx?page=1&sortby=0&orderby=0&q={0}&id=0&lid=2618".format(
                quote(tech_name.replace(' ', '+')))
        page = get_from_url(url)
        isp = ItjLinkMaker.ItjSearchParser()
        isp.feed(page)
        return {'items': isp.result}

    class ItjPageParser(HTMLParser):
        read_image = False
        img_src = None
    
        def handle_starttag(self, tag, attrs):
            if tag == 'a' and ('id', 'demand_trend') in attrs:
                self.read_image = True
                return
            if self.read_image and tag == 'img':
                self.img_src = dict(attrs)['src']
                self.read_image = False

    def _get_itj_image_name(self, itj_link):
        page = get_from_url(itj_link)
        ipp = ItjLinkMaker.ItjPageParser()
        ipp.feed(page)
        link = ipp.img_src
        logging.debug("Located image link: %s", link)
        name_search = re.search('aspx\?s=(.*)&', link)
        if not name_search:
            logging.warning("Can't locate itjobs image on page: %s", link)
            raise KeyError('bad link')
        return name_search.group(1)        


if __name__ == "__main__":
    pass