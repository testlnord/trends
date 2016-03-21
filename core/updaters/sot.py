"""StackOverflow specific updater """
import datetime

from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..config import config, project_root
from ..crawlers import sot_crawler


class SotUpdater(DataUpdater):

    def __init__(self):
        super().__init__('sot', __name__)
        self.crawler = sot_crawler.SotCrawler(self.source_config["apikey"])
        self.entity_name = 'tag'


    def get_data(self, tech_id):
        last_date = self.last_dates[tech_id] - datetime.timedelta(days=3)
        tag = self.settings[tech_id]['tag'][0]
        self.logger.debug("Getting data for tag: %s", tag)
        data = self.crawler.get_data(tag, last_date)
        return data

    def update_db_data(self, data, tech_id):
        max_date = max(data, key=lambda x: x[0])[0]
        min_date = min(data, key=lambda x: x[0])[0]

        self.logger.debug("Updating database")
        cur = self.connection.cursor()
        cur.execute("delete from rawdata where source='sot' and tech_id = %s and time >= %s",
                (tech_id, min_date))
        cur.executemany("insert into rawdata(source, tech_id, time, value) values (%s, %s, %s, %s)",
                    (('sot', tech_id, d, v) for d, v in data))
        self.connection.commit()

    def get_words_for_tech(self, tech_id: int):
        try:
            tech_data = self.settings[tech_id]
            return tech_data["tag"]
        except KeyError as e:
            print(e)
            return None

    @staticmethod
    def _words_to_link(tags):
        if tags is None:
            return None
        return ["http://stackoverflow.com/tags/{}/info".format(tag) for tag in tags]