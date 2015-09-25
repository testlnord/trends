import tornado
from tornado import template
import psycopg2
import tornado.web

from tornadoweb.config import config


class TechSearchHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def post(self):
        tech_name = self.get_argument('tech_name', '')

        pass
    def get(self):
        page_template = self.template_loader.load('tech_search.html')
        cur = self.db_connection.cursor()
        cur.execute("SELECT id, name, info::JSON FROM techs")
        all_techs = cur.fetchall()
        cur.execute("SELECT name from sources")
        all_sources = cur.fetchall()

        self.write(page_template.generate(techs=cur.fetchall()))

class TechInfoHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def get(self):
        page_template = self.template_loader.load('techs_info.html')
        cur = self.db_connection.cursor()
        cur.execute("SELECT id, name, info::JSON FROM techs")
        all_techs = cur.fetchall()
        cur.execute("SELECT name from sources")
        all_sources = cur.fetchall()

        self.write(page_template.generate(techs=cur.fetchall()))