"""wikipedia source manager"""
import datetime

from .sourcemanager import source_decorator
from ..dbis import wikidbi
from ..crawlers import wiki_crawler
from ..link_makers import wikilm
from .errors import UnknownTechnology
from ..config import config


@source_decorator
class WikiSrc():
    earliest_date_available = datetime.date(2007, 12, 1)

    def __init__(self):
        self.dbi = wikidbi.WikiDBI()
        self.crawler = wiki_crawler.WikiCrawler()
        self.link_maker = wikilm.WikiLinkMaker()

    def get_series(self, tech_name, start_date=None, end_date=None):
        pages = self.dbi.get_pages(tech_name)
        if not pages:
            raise UnknownTechnology(tech_name)

        # for page, page_id in pages:
            # todo move refresh to scheduler
            # last_date = self.dbi.get_last_date(page)
            # if last_date < datetime.datetime.now() - datetime.timedelta(days=config['wiki']['refresh_time']):
            #     fresh_data = self.crawler.get_data(page, date_from=last_date)
            #     self.dbi.add_series_data(fresh_data, page_id=page_id)

        return self.dbi.get_series_data(tech_name, start_date, end_date)

    def add_tech(self, tech_name):
        pages = self.link_maker.make_links(tech_name)
        self.dbi.add_pages(pages, tech_name)
        for page in pages:
            page_data = self.crawler.get_data(page, self.earliest_date_available,
                                  self.earliest_date_available + datetime.timedelta(days=50))
            self.dbi.add_series_data(page_data, page_name=page)

    pass


if __name__ == "__main__":
    pass