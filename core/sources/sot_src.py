""" """
import datetime
from .sourcemanager import source_decorator
from ..dbis import sotdbi
from ..crawlers import sot_crawler
from ..link_makers import sotlm
from .errors import UnknownTechnology


@source_decorator
class SotSrc():
    earliest_data_available = datetime.datetime(2008, 7, 28)

    def __init__(self):
        self.dbi = sotdbi.SotDBI()
        self.crawler = sot_crawler.SotCrawler()
        self.link_maker = sotlm.SotLinkMaker()

    def get_series(self, tech_name, start_date=None, end_date=None):
        name_id = self.dbi.get_tag(tech_name)
        if not name_id:
            raise UnknownTechnology(tech_name)

            # for page, page_id in pages:
            # todo move refresh to scheduler
            # last_date = self.dbi.get_last_date(page)
            # if last_date < datetime.datetime.now() - datetime.timedelta(days=config['wiki']['refresh_time']):
            # fresh_data = self.crawler.get_data(page, date_from=last_date)
            #     self.dbi.add_series_data(fresh_data, page_id=page_id)

        return self.dbi.get_series_data(tech_name, start_date, end_date)

    def add_tech(self, tech_name):
        tag = self.link_maker.make_links(tech_name)
        tag_id = self.dbi.add_tag(tag, tech_name)

        data = self.crawler.get_data(tag, self.earliest_data_available,
                                     date_to=self.earliest_data_available + datetime.timedelta(weeks=10))
        self.dbi.add_series_data(data, tag_id)


if __name__ == "__main__":
    pass