import traceback
import tornado
from tornado import template
import psycopg2
import tornado.web

from tornadoweb.config import config
from core.updaters.gitstars import GitStarsUpdater
from core.updaters.google import GoogleUpdater
from core.updaters.itj import ItjUpdater
from core.updaters.wiki import WikiUpdater
from core.updaters.sot import SotUpdater
from core.updaters.parent import DataUpdater

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

    def get(self, slug):
        try:
            tech_id = None
            try:
                tech_id = int(slug)
            except ValueError:
                self.write_error(404)
                return

            info = {'tech_id': tech_id,
                    'description': ''}
            cur = self.db_connection.cursor()
            cur.execute("select name, info::JSON from techs where id = %s", (tech_id,))
            res = cur.fetchall()
            if res and len(res) == 1:
                name, info_json = res[0]
                info['name'] = name
                if 'description' in info_json:
                    info['description'] = info_json['description']

            updaters = [SotUpdater, WikiUpdater, GitStarsUpdater, ItjUpdater, GoogleUpdater]
            info['sources'] = []
            for updater in updaters:
                upd = updater()
                """:type : DataUpdater"""
                links = upd.get_links(tech_id)
                if links:
                    info['sources'].append({'name' : upd.source_name,
                                            'links': links})


            self.render('info.html', **info)
        except:
            self.write(traceback.format_exc())