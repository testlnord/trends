"""Wiki specified updater """
import json
import logging
import psycopg2
from ..config import config


class WikiUpdater:
    setting_path = "../src_conf/wiki.json"

    def __init__(self):
        self.settings = json.load(open(self.setting_path))
        self.logger = logging.getLogger(__name__)
        try:
            self.connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                               password=config['db_pass'])
        except:
            self.logger.error("Couldn't connect to database")
            raise
        self.logger.info("Wiki updater initialized.")