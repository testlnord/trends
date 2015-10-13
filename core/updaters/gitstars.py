"""StackOverflow specific updater """
import datetime

from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..config import config, project_root
from ..crawlers import gitstars_crawler


class GitStarsUpdater(DataUpdater):
    def __init__(self):
        super().__init__('gitstars', __name__)
        self.crawler = gitstars_crawler.GitStarsCrawler()

    def add_new_tech(self, tech_id, repo_name):
        start_date = self.source_config['earliest_date'] if 'earliest_date' in self.source_config \
            else datetime.date(2001, 1, 1).strftime(config['date_format'])
        self.settings[str(tech_id)] = {
            "repo": [repo_name]
        }
        self.last_dates[str(tech_id)] = start_date
        self.commit_settings()

    def get_data(self, tech_id):
        repo = self.settings[tech_id]['repo'][0]
        self.logger.debug("Getting data for repo: %s", repo)
        data = self.crawler.get_data(repo)
        return [(d, 1) for d in data]

    def update_db_data(self, data, tech_id):
        self.logger.debug("Updating database")
        cur = self.connection.cursor()
        cur.execute("delete from rawdata where source='gitstars' and tech_id = %s",
                    (tech_id,))
        cur.executemany("insert into rawdata(source, tech_id, time, value) values (%s, %s, %s, %s)",
                        (('gitstars', tech_id, d, v) for d, v in data))
        self.connection.commit()

    def get_words_for_tech(self, tech_id: int):
        try:
            tech_data = self.settings[tech_id]
            return tech_data["repo"]
        except KeyError as e:
            print(e)
            return ""

    def _group_by_days(self, dt_list: list) -> list:
        if not dt_list:
            return []
        dates_counts = {}
        for dt in dt_list:
            if dt.date() not in dates_counts:
                dates_counts[dt.date()] = [dt]
            else:
                dates_counts[dt.date()].append(dt)
        cur_date = min(dates_counts)
        """:type : datetime.date"""
        max_date = max(dates_counts)
        """:type : datetime.date"""
        result = []
        while cur_date != max_date:
            if cur_date in dates_counts:
                result.append((cur_date, len(dates_counts[cur_date])))
            else:
                result.append((cur_date, 0))
            cur_date += datetime.timedelta(days=1)

        return result
