"""Parent updater for all other updaters """
import json
import logging
import psycopg2
from ..config import config

class DataUpdater:
    def __init__(self, setting_path, logger_name):
        self.setting_path =setting_path
        self.settings = self.open_settings()
        self.logger = logging.getLogger(logger_name)
        try:
            self.connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                               password=config['db_pass'])
        except:
            self.logger.error("Couldn't connect to database")
            raise

    def update_data(self):
        raise NotImplemented

    def open_settings(self):
        return json.load(open(self.setting_path))

    def commit_settings(self):
        json.dump(self.settings, open(self.setting_path, 'w'))
