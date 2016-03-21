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
        self.entity_name = 'repo'

    @staticmethod
    def is_valid_repository_name(reponame):
        import re
        f_match = re.fullmatch("[A-Za-z0-9_.-]*/[A-Za-z0-9_.-]*", reponame)
        return f_match is not None

    def get_data(self, tech_id):
        repo = self.settings[tech_id]['repo'][0]
        if not self.is_valid_repository_name(repo):
            self.logger.warning("Invalid repo name: %s", repo)
            return []
        self.logger.debug("Getting data for repo: %s", repo)
        try:
            data = self.crawler.get_data(repo)
        except Exception:
            import traceback
            self.logger.warning("Can't get data for repo: %s", repo)
            self.logger.warning(traceback.format_exc())
            return []
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
            return None

    @staticmethod
    def _words_to_link(repos_name):
        if repos_name is None:
            return None
        return ["https://github.com/" + repo_name for repo_name in repos_name]

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
