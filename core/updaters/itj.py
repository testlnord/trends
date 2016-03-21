""" Itjobs specific updater"""
import datetime
import sys

from core.updaters.parent import DataUpdater
from core.utils.stuff import get_threshold_date
from core.config import config, project_root
from core.crawlers.itj_crawler import ItjCrawler
import traceback

class ItjUpdater(DataUpdater):

    def __init__(self):
        super().__init__('itj', __name__)
        self.crawler = ItjCrawler()

    def add_new_tech(self, tech_id:int, link:str):
        self.logger.debug("adding or updating technology %s %s", tech_id, link)
        self.settings[tech_id] = {
            "link": [link]
        }
        self.last_dates[tech_id] = self.get_earliest_date()
        self.commit_settings()


    def get_data(self, tech_id):
        pic_name = self.settings[tech_id]['link'][0]
        self.logger.debug("Getting data for %s image.", pic_name)
        try:
            data = self.crawler.get_data(pic_name)
            return data
        except Exception as e:
            self.logger.error("Can't get data for image: %s\n%s\n%s", pic_name,
                              traceback.format_exc(), '\n'.join(traceback.format_tb(sys.exc_info()[2])))
            return None

    def update_db_data(self, data, tech_id):
        self.logger.debug("Updating database")
        cur = self.connection.cursor()
        cur.execute("delete from rawdata where source='itj' and tech_id = %s", (tech_id,))
        # multiply values by factor 1000, to save percents in integer field
        cur.executemany("insert into rawdata(source, tech_id, time, value) values (%s, %s, %s, %s)",
                        (('itj', tech_id, d, v*1000) for d, v in data))
        self.connection.commit()

    def get_words_for_tech(self, tech_id: int):
        try:
            tech_data = self.settings[tech_id]
            return tech_data["link"]
        except KeyError as e:
            print(e)
            return None

    @staticmethod
    def _words_to_link(links):
        if links is None:
            return None

        return ["http://www.itjobswatch.co.uk/jobs/uk/{}.do".format(link.replace('+', "%20")) for link in links]