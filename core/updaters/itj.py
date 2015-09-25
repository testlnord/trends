""" Itjobs specific updater"""
import datetime

from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..config import config, project_root
from ..crawlers.itj_crawler import ItjCrawler


class ItjUpdater(DataUpdater):
    setting_path = project_root+"/src_conf/itj.json"

    def __init__(self):
        super().__init__(self.setting_path, __name__)
        self.crawler = ItjCrawler()

    def add_new_tech(self, tech_id, link):
        self.settings['techs'][str(tech_id)] = {
            "link": [link]
        }
        self.last_dates[str(tech_id)] = datetime.date(2000, 1, 1).strftime(config['date_format'])
        self.commit_settings()


    def get_data(self, tech_id):
        pic_name = self.settings[tech_id]['link'][0]
        self.logger.debug("Getting data for %s image.", pic_name)
        data = self.crawler.get_data(pic_name)
        return data

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
            tech_data = self.settings['techs'][str(tech_id)]
            return tech_data["link"]
        except KeyError as e:
            print(e)
            return "---"
