"""Parent updater for all other updaters """
import json
import logging
import datetime
import psycopg2
from core.config import config
from core.utils.stuff import get_threshold_date


class DataUpdater:
    def __init__(self, source_name, logger_name):
        try:
            self.connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                               password=config['db_pass'])
        except:
            self.logger.error("Couldn't connect to database")
            raise

        self.last_dates = {}
        self.settings = {}
        self.source_config = {}

        self.source_name = source_name
        self.open_settings()
        self.logger = logging.getLogger(logger_name)

    def add_new_tech(self, tech_id, info):
        raise NotImplemented

    def update_data(self):
        raise NotImplemented

    def open_settings(self):
        cur = self.connection.cursor()
        cur.execute("select tech_id, settings, last_update_date from source_settings "
                    "where source = %s ORDER by last_update_date ASC",
                    (self.source_name,))

        for row in cur.fetchall():
            self.settings[row[0]] = row[1]
            self.last_dates[row[0]] = row[2]

        cur.execute("select config from sources where name = %s", (self.source_name,))
        self.source_config = cur.fetchone()[0]

    def commit_settings(self):
        self.logger.debug("commiting settings")
        cur = self.connection.cursor()
        for tech_id in self.last_dates:
            cur.execute("update source_settings set (settings, last_update_date) = (%s, %s) "
                        "where source = %s AND tech_id = %s",
                        (json.dumps(self.settings[tech_id]), self.last_dates[tech_id],
                         self.source_name, tech_id))
            if cur.rowcount == 0:
                cur.execute("insert into source_settings (tech_id, source, settings, last_update_date) "
                            "values (%s, %s, %s, %s)",
                            (tech_id,
                             self.source_name,
                             json.dumps(self.settings[tech_id]),
                             self.last_dates[tech_id]))
        cur.execute("update sources set config = %s where name = %s", (json.dumps(self.source_config),
                                                                       self.source_name))
        self.connection.commit()


    def update_data(self):
        """Updates data for all technologies

        Lurking for outdated techs and downloads fresh data for them.
        :return: dirty flag. True if some data was updated.
        """

        time_threshold = get_threshold_date(self.source_config['refresh_time'])
        dirty = False
        for tech_id in self.settings:
            if self.last_dates[tech_id] < time_threshold.date():
                self.logger.info("Updating tech: %s", tech_id)
                try:
                    data = self.get_data(tech_id)
                except:
                    import traceback
                    self.logger.warning("Can't get data.")
                    self.logger.warning(traceback.format_exc())
                    continue

                if not data:
                    self.logger.info("No data for query %s", tech_id)
                else:
                    self.update_db_data(data, tech_id)
                    dirty = True
                    # We should update date for every tech.
                    self.logger.debug("Updating last_date property")
                    self.last_dates[tech_id] = datetime.date.today().strftime(config['date_format'])
                    self.commit_settings()

        return dirty

    def get_data(self, tech_id):
        raise NotImplemented

    def update_db_data(self, data, tech_id):
        raise NotImplemented

    def get_words_for_tech(self, tech_id: int):
        raise NotImplemented

    def get_links(self, tech_id: int):
        return self._words_to_link(self.get_words_for_tech(tech_id))

    @staticmethod
    def _words_to_link(param):
        raise NotImplemented
