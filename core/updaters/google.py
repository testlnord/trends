"""Google specific updater """
import csv
from io import StringIO
import datetime
import googletrendscsvdownloader.pyGoogleTrendsCsvDownloader as gcd
from ..config import config, project_root
from ..utils.stuff import get_threshold_date
from .parent import DataUpdater


class OutOfProxies(Exception):
    pass


class GoogleUpdater(DataUpdater):


    def __init__(self):
        super().__init__('google', __name__)

        self.proxy_iter = iter(self.source_config["proxies"])
        self.make_google_connection()

        self.logger.info("Google updater initialized.")

    def add_new_tech(self, tech_id:int, name:str):
        # todo move common code to parent
        self.settings[tech_id] = {
            "name": [name]
        }
        self.last_dates[tech_id] = self.get_earliest_date()
        self.commit_settings()

    def next_proxy(self):
        try:
            proxy = next(self.proxy_iter)
            while not proxy['user']:
                self.logger.warning("For proxy %s user not specified. Check config.", proxy['proxy'])
                proxy = next(self.proxy_iter)
            return proxy
        except StopIteration:
            self.logger.error("Google parser is out of proxies")
            raise OutOfProxies("Google parser is out of proxies")

    def make_google_connection(self):
        proxy = self.next_proxy()
        while True:
            # repeat connection attempts
            try:
                self.trends_downloader = gcd.pyGoogleTrendsCsvDownloader(proxy['user'], proxy['pass'], proxy['proxy'])
                break
            except ValueError:
                self.logger.warning("Google authentication failed for user: %s", proxy['user'])

    def update_db_data(self, data, tech_id):
        cur = self.connection.cursor()
        self.logger.debug("Deleting old data...")
        cur.execute("delete from rawdata where tech_id = %s and source = 'google'", (tech_id,))
        self.logger.debug("Inserting new data...")
        cur.executemany("insert into rawdata(tech_id, source, time, value) values(%s, %s, %s, %s)",
                        ((tech_id, 'google', d, v) for d, v in data))
        self.connection.commit()

    def get_data(self, tech_id):
        try:
            self.logger.debug("Getting data...")
            csv_data = self.trends_downloader.get_csv_data(q=self.settings[tech_id]['name'][0],
                                                           cat=self.source_config["trend_category"])
            return self.parse_csv(csv_data)
        except gcd.QuotaExceededException:
            self.logger.info("Google quota exceeded.")
            self.make_google_connection()
        return None


    @staticmethod
    def parse_csv(csv_data):
        reader_file = StringIO(csv_data.decode())
        reader = csv.reader(reader_file, delimiter=',')
        start = False
        result = []
        for row in reader:
            if row and row[0] == 'Week':
                start = True
                continue
            if start and not row:
                break
            if start:
                d = datetime.datetime.strptime(row[0][:10], config['date_format'])
                if datetime.datetime.now() - datetime.timedelta(weeks=1) < d:
                    break
                v = int(row[1])
                result.append((d.date(), v))
        return result

    def get_words_for_tech(self, tech_id: int):
        try:
            tech_data = self.settings[tech_id]
            return tech_data["name"][0]
        except KeyError as e:
            print(e)
            return None

    @staticmethod
    def _words_to_link(word):
        if word is None:
            return None
        return ["https://www.google.com/trends/explore#cmpt=q&q={}&cat=0-5-31".format(word)]
