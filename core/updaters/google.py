"""Google specific updater """
import csv
import json
from io import StringIO
import datetime
import logging
import psycopg2
import googletrendscsvdownloader.pyGoogleTrendsCsvDownloader as gcd
from ..config import config
from ..utils.stuff import get_threshold_date

class OutOfProxies(Exception):
    pass


class GoogleUpdater:
    setting_path = "../src_conf/google.json"

    def __init__(self):
        self.settings = json.load(open(self.setting_path))
        self.logger = logging.getLogger(__name__)

        self.proxy_iter = iter(self.settings["proxies"])
        self.make_google_connection()

        try:
            self.connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                               password=config['db_pass'])
        except:
            self.logger.error("Couldn't connect to database")
            raise

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
            #repeate connection attempts
            try:
                self.trends_downloader = gcd.pyGoogleTrendsCsvDownloader(proxy['user'], proxy['pass'], proxy['proxy'])
                break
            except ValueError:
                self.logger.warning("Google authentication failed for user: %s", proxy['user'])


    def update_data(self):
        """Updates data for all technologies

        Lurking for outdated techs and downloads fresh data for them.
        :return: dirty flag. True if some data was updated.
        """

        time_threshold = get_threshold_date(self.settings['refresh_time'])
        dirty = False
        for tech_id, tech in self.settings['techs'].items():
            if tech['last_date'] < time_threshold.strftime('%Y-%m-%d'):
                tech_name = tech['name'][0]
                self.logger.info("Updating tech: %s", tech_name)
                try:
                    self.logger.debug("Getting data...")
                    csv_data = self.trends_downloader.get_csv_data(q=tech_name, cat=self.settings["trend_category"])
                except gcd.QuotaExceededException:
                    self.logger.info("Google quota exceeded.")
                    self.make_google_connection()
                    continue

                data = self.parse_csv(csv_data)
                if not data:
                    pass
                    self.logger.warning("No data for query %s", tech_name)
                else:
                    cur = self.connection.cursor()
                    self.logger.debug("Deleting old data...")
                    cur.execute("delete from rawdata where tech_id = %s and source = 'google'", (tech_id,))
                    self.logger.debug("Inserting new data...")
                    cur.executemany("insert into rawdata(tech_id, source, time, value) values(%s, %s, %s, %s)",
                                    ((tech_id, 'google', d, v) for d, v in data))
                    self.connection.commit()

                    dirty = True
                    # We should update date for every tech.
                    self.logger.debug("Updating last_date property")
                    max_date = max(data, key=lambda x: x[0])[0]
                    self.settings['techs'][tech_id]['last_date'] = max_date.strftime('%Y-%m-%d')
                    self.commit_settings()

        return dirty

    def commit_settings(self):
        json.dump(self.settings, open(self.setting_path, 'w'))

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
                d = datetime.datetime.strptime(row[0][:10], '%Y-%m-%d')
                if datetime.datetime.now() - datetime.timedelta(weeks=1) < d:
                    break
                v = int(row[1])
                result.append((d.date(), v))
        return result