

from tornado import template
import psycopg2
import tornado.web

from tornadoweb.config import config
import json
from itertools import zip_longest


class BaseApiV1Handler(tornado.web.RequestHandler):
    handlerName = "BaseApiV1Handler"
    def __init__(self, *args, **kwargs):
        import logging

        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.handlerName)
        self.logger.info("initializing  handler")
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def write_traceback(self):
        import sys
        import traceback
        trace_msg = traceback.format_exc()
        self.logger.error(trace_msg)
        self.write(trace_msg)

    def get(self, *args):
        raise NotImplemented


class TechSourcesHandler(BaseApiV1Handler):
    handlerName = "ApiV1TechSourceHandler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, tech_id):
        try:
            tech_id = int(tech_id)
            cur = self.db_connection.cursor()
            cur.execute('select source from source_settings where tech_id = %s', (tech_id,))
            sources = []
            for src in cur.fetchall():
                sources.append(src[0])
            if sources:
                sources.append('average')
                self.write(json.dumps(sources))
            else:
                self.write_error(404)
        except:
            self.write_traceback()
            self.write_error(404)


class TechListHandler(BaseApiV1Handler):
    handlerName = "ApiV1TechListHandler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self):
        try:
            cur = self.db_connection.cursor()
            cur.execute('select id, name from techs')
            techs = []
            for tid, t_name in cur.fetchall():
                techs.append({'id': tid,
                         'name': t_name})
            self.write(json.dumps(techs))
        except:
            self.write_error(404)
            self.write_traceback()


class SourcesListHandler(BaseApiV1Handler):
    handlerName = "ApiV1SourceListHandler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self):
        cur = self.db_connection.cursor()
        cur.execute('select sources.name from sources')
        sources = ['average']
        for s_name in cur.fetchall():
            sources.append(s_name[0])
        self.write(json.dumps(sources))


class TechTrendHandler(BaseApiV1Handler):
    handlerName = "ApiV1TechTrendHandler"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, tech_id, source):
        tech_id = int(tech_id)
        cur = self.db_connection.cursor()
        if source == 'average':
            cur.execute('select time, value from reports_2 where tech_id = %s', (tech_id,))
        else:
            cur.execute('select time, value from reports_1 where tech_id = %s and source = %s', (tech_id, source))
        result = []
        for time, value in cur.fetchall():
            result.append({'t':str(time), 'v':value})
        if result:
            self.write(json.dumps(result))
        else:
            self.write_error(404)