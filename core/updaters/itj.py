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
            "last_date": datetime.date(2000, 1, 1).strftime(config['date_format']),
            "link": [link]
        }
        self.commit_settings()

    def update_data(self):
        threshold_date = get_threshold_date(self.settings['refresh_time']).strftime(config['date_format'])
        self.logger.info("Updating itj data from date %s", threshold_date)
        dirty = False
        for tech_id, tech_info in self.settings['techs'].items():
            if tech_info['last_date'] < threshold_date:
                pic_name = tech_info['link'][0]
                self.logger.debug("Getting data for %s image.", pic_name)
                try:
                    data = self.crawler.get_data(pic_name)

                    if data:
                        max_date = max(data, key=lambda x: x[0])[0]
                        self.logger.debug("Updating database")
                        cur = self.connection.cursor()
                        cur.execute("delete from rawdata where source='itj' and tech_id = %s", (tech_id,))
                        # multiply values by factor 1000, to save percents in integer field
                        cur.executemany("insert into rawdata(source, tech_id, time, value) values (%s, %s, %s, %s)",
                                        (('itj', tech_id, d, v*1000) for d, v in data))
                        self.connection.commit()
                        dirty = True

                        self.logger.debug("Updating settings")
                        self.settings['techs'][tech_id]['last_date'] = max_date.strftime(config['date_format'])
                        self.commit_settings()
                except:
                    self.logger.warning("Failed to update tech %s with pic %s", tech_id, pic_name, exc_info=True)
        return dirty

    def getWordsForTech(self, tech_id: int):
        try:
            tech_data = self.settings['techs'][str(tech_id)]
            return tech_data["link"]
        except KeyError as e:
            print(e)
            return "---"
