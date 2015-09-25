"""StackOverflow specific updater """
import datetime

from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..config import config, project_root
from ..crawlers import sot_crawler


class SotUpdater(DataUpdater):
    setting_path = project_root+"/src_conf/sot.json"

    def __init__(self):
        super().__init__(self.setting_path, __name__)
        self.crawler = sot_crawler.SotCrawler(self.source_config["apikey"])

    def add_new_tech(self, tech_id, tag):
        start_date = self.source_config['earliest_date'] if 'earliest_date' in self.source_config \
            else datetime.date(2001, 1, 1).strftime(config['date_format'])
        self.settings['techs'][str(tech_id)] = {
            "tag": [tag]
        }
        self.last_dates[str(tech_id)] = start_date
        self.commit_settings()

    def get_data(self, tech_id):
        last_date =  datetime.datetime.strptime(self.last_dates[tech_id], config['date_format']) - \
                        datetime.timedelta(days=3)
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
            tech_data = self.settings['techs'][str(tech_id)]
            return tech_data["tag"]
        except KeyError as e:
            print(e)
            return "---"
