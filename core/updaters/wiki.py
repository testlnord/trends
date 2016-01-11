"""Wiki specified updater """
import json
import datetime
import re
from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..utils.internet import internet
from ..config import config, project_root


class WikiUpdater(DataUpdater):
    def __init__(self):
        super().__init__('wiki', __name__)
        self.logger.info("Wiki updater initialized.")

    def add_new_tech(self, tech_id, pages):
        start_date = self.settings['earliest_date'] if 'earliest_date' in self.settings \
            else datetime.date(2000, 1, 1).strftime(config['date_format'])
        self.settings[str(tech_id)] = {
            "pages": pages
        }
        self.last_dates[str(tech_id)] = start_date
        self.commit_settings()

    def get_data(self, tech_id):
        last_date = self.last_dates[tech_id]
        page_datas = []
        for page in self.settings[tech_id]['pages']:
            self.logger.debug("Getting data for page %s", page)
            page_datas.append(self.get_page_data(page, last_date))

        self.logger.debug("Merging data.")
        tech_data = self.merge_data(page_datas)
        return tech_data

    def update_db_data(self, data, tech_id):
        min_date = min(data, key=lambda x: x[0])[0]
        max_date = max(data, key=lambda x: x[0])[0]

        self.logger.debug("Updating values in database")
        cur = self.connection.cursor()
        cur.execute("delete from rawdata where source = 'wiki' and tech_id = %s and time >= %s",
                    (tech_id, min_date))
        cur.executemany("insert into rawdata(source, tech_id, time, value) values(%s, %s, %s, %s)",
                        (('wiki', tech_id, d, v) for d, v in data))
        self.connection.commit()

    def get_page_data(self, page_name, from_date):
        page_name = page_name.replace(" ", "_")
        month = datetime.date(from_date.year, from_date.month, 1)
        today = datetime.datetime.today().date()
        result = []

        date_pattern = re.compile('(\d*)-(\d\d)-(\d\d)')
        while month < today:
            self.logger.debug("Getting data for date: %s", month.strftime("%Y-%m"))

            url = "http://stats.grok.se/json/en/" + month.strftime("%Y%m") + "/" + internet.quote(page_name)
            data = internet.get_from_url(url)

            for day, value in json.loads(data)['daily_views'].items():
                date_parsed = date_pattern.match(day)
                if date_parsed:
                    # I have to make 1st day of month and then add days,
                    # cause response contains dates like '2012-02-31'
                    # which is '2012-03-02' really
                    date = datetime.date(int(date_parsed.group(1)), int(date_parsed.group(2)), 1)
                    date += datetime.timedelta(days=(int(date_parsed.group(3)) - 1))
                    result.append((date, value))

            month = datetime.date(month.year + int(month.month / 12), month.month % 12 + 1, 1)  # add a month
        return result

    def merge_data(self, data_for_all_pages):
        all_page_dicts = [dict(l) for l in data_for_all_pages]
        dates = set(all_page_dicts[0])
        for page_dict in all_page_dicts[1:]:
            dates.update(set(page_dict))

        result = []
        for date in dates:
            value = 0
            for page_dict in all_page_dicts:
                try:
                    value += page_dict[date]
                except KeyError:
                    pass
            result.append((date, value))
        return sorted(result, key=lambda x: x[0])

    def get_words_for_tech(self, tech_id: int):
        try:
            tech_data = self.settings[tech_id]
            return tech_data["pages"]
        except KeyError as e:
            print(e)
            return None

    @staticmethod
    def _words_to_link(links):
        if links is None:
            return None
        return ["https://en.wikipedia.org/wiki/"+link for link in links]
