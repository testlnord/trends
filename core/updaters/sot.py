"""StackOverflow specific updater """
import datetime

from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..config import config
from ..crawlers import sot_crawler


class SotUpdater(DataUpdater):
    setting_path = "../src_conf/sot.json"

    def __init__(self):
        super().__init__(self.setting_path)
        self.crawler = sot_crawler.SotCrawler(self.settings["apikey"])

    def update_data(self):
        threshold_date = get_threshold_date(self.settings['refresh_time']).strftime(config['date_format'])
        dirty = False
        for tech_id, tech in self.settings['techs'].items():
            if tech['last_date'] < threshold_date:
                last_date = datetime.datetime.strptime(tech['last_date'], config['date_format']) - \
                    datetime.timedelta(days=3)
                tag = tech['tag'][0]
                self.logger.debug("Getting data for tag: %s", tag)
                data = self.crawler.get_data(tag, last_date)

                if data:
                    max_date = max(data, key=lambda x: x[0])[0]
                    min_date = min(data, key=lambda x: x[0])[0]

                    self.logger.debug("Updating database")
                    cur = self.connection.cursor()
                    cur.execute("delete from rawdata where source='sot' and tech_id = %s and time >= %s",
                                (tech_id, min_date))
                    cur.executemany("insert into rawdata(source, tech_id, time, value) values (%s, %s, %s, %s)",
                                    (('sot', tech_id, d, v) for d, v in data))
                    self.connection.commit()
                    dirty = True

                    self.logger.debug("Updating settings")
                    self.settings['techs'][tech_id]['last_date'] = max_date.strftime(config['date_format'])
                    self.commit_settings()

        return dirty