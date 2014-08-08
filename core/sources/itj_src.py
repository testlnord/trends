"""IT jobs watch source manager """
import datetime
from .sourcemanager import source_decorator
from ..dbis import itjdbi
from ..crawlers import itj_crawler
from ..link_makers import itjlm
from .errors import UnknownTechnology

# todo uncomment
#@source_decorator
class ItjSrc():
    def __init__(self):
        self.dbi = itjdbi.ItjDBI()
        self.crawler = itj_crawler.ItjCrawler()
        self.link_maker = itjlm.ItjLinkMaker()

    def get_series(self, tech_name, start_date=None, end_date=None):
        name_id = self.dbi.get_name_id(tech_name)
        if not name_id:
            raise UnknownTechnology(tech_name)

        # for page, page_id in pages:
            # todo move refresh to scheduler
            # last_date = self.dbi.get_last_date(page)
            # if last_date < datetime.datetime.now() - datetime.timedelta(days=config['wiki']['refresh_time']):
            #     fresh_data = self.crawler.get_data(page, date_from=last_date)
            #     self.dbi.add_series_data(fresh_data, page_id=page_id)

        return self.dbi.get_series_data(tech_name, start_date, end_date)

    def add_tech(self, tech_name):
        name = self.link_maker.make_links(tech_name)
        self.dbi.add_name(name, tech_name)

        data = self.crawler.get_data(name)
        self.dbi.add_series_data(data, tech_name)

if __name__ == "__main__":
    pass