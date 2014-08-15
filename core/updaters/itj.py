""" Itjobs specific updater"""

from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..config import config, project_root
from ..crawlers.itj_crawler import ItjCrawler


class ItjUpdater(DataUpdater):
    setting_path = project_root+"/src_conf/itj.json"

    def __init__(self):
        super().__init__(self.setting_path)

        self.crawler = ItjCrawler()

    def update_data(self):
        threshold_date = get_threshold_date(self.settings['refresh_time']).strftime(config['date_format'])
        self.logger.info("Updating itj data from date %s", threshold_date)
        dirty = False
        for tech_id, tech_info in self.settings['techs'].items():
            if tech_info['last_date'] < threshold_date:
                pic_name = tech_info['link'][0]
                self.logger.debug("Getting data for %s image.", pic_name)
                
                data = self.crawler.get_data(pic_name)

                if data:
                    max_date = max(data, key=lambda x: x[0])[0]
                    self.logger.debug("Updating database")
                    cur = self.connection.cursor()
                    cur.execute("delete from rawdata where source='itj' and tech_id = %s", (tech_id,))
                    cur.executemany("insert into rawdata(source, tech_id, time, value) values (%s, %s, %s, %s)",
                                    (('itj', tech_id, d, v) for d, v in data))
                    self.connection.commit()
                    dirty = True

                    self.logger.debug("Updating settings")
                    self.settings['techs'][tech_id]['last_date'] = max_date.strftime(config['date_format'])
                    self.commit_settings()

        return dirty
