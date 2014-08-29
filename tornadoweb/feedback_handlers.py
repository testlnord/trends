"""Tornado handlers,
provides services for all feedback related stuff
"""
import logging
import datetime
import math
from tornado import template
from urllib.parse import urlencode, unquote
import psycopg2
import tornado.web
# noinspection PyUnresolvedReferences
from config import config
import json


class ReceiveFeedbackHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])
        self.logger = logging.getLogger(__name__)

    def get(self, slug):
        try:
            message = json.loads(slug)
            if 'text' not in message or 'author' not in message or 'ids' not in message:
                raise ValueError()
            tech_ids = (int(x) for x in message['ids'])
            message['author'] = unquote(message['author'])
            message['text'] = unquote(message['text'])
        except ValueError:
            self.logger.debug("Bad message received: %s", slug)
            self.write_error(406)
            return

        cur = self.db_connection.cursor()
        cur.execute("insert into feedback (message, time, author) values(%s, %s, %s) returning id",
                    (message['text'], datetime.datetime.now(), message['author']))
        fb_id = cur.fetchone()[0]
        cur.executemany("insert into feedback_techs(fb_id, tech_id) values(%s, %s)",
                        ((fb_id, tid) for tid in tech_ids))
        self.db_connection.commit()
        self.write('{"ok":"ok"}')


class ShowFeedbacksHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])
        self.logger = logging.getLogger(__name__)

    def get(self):
        cur = self.db_connection.cursor()
        cur.execute("SELECT id, info::JSON->>'name' FROM techs WHERE (info::JSON->>'visible') IS NULL")
        techs = cur.fetchall()

        query = "SELECT id, message, author, time, array_agg(ft.tech_id) AS tech_ids FROM feedback " \
                "INNER JOIN feedback_techs AS ft ON id = ft.fb_id "
        total_query = "SELECT count(DISTINCT id) FROM feedback INNER JOIN feedback_techs ON id = fb_id "
        where = []
        joins = []
        req_params = {}

        tech_ids = self.get_argument("ts", None, True)
        url_params = {}
        if tech_ids is not None:
            tech_ids = [int(x) for x in tech_ids.split(',')]
            joins.append(" inner join feedback_techs as ft2 on id= ft2.fb_id ")
            where.append("ft2.tech_id in (" + ','.join(str(x) for x in tech_ids) + ")")
            req_params['ts'] = tech_ids
            url_params['ts'] = ",".join(str(x) for x in tech_ids)

        date_from = self.get_argument("df", None, True)
        if date_from is not None:
            date_from = datetime.datetime.strptime(date_from, "%Y%m%d")
            where.append("time >= " + date_from.strftime("DATE '%Y %m %d'"))
            req_params["df"] = date_from
            url_params["df"] = date_from.strftime("%Y%m%d")

        date_to = self.get_argument("dt", None, True)
        if date_to is not None:
            date_to = datetime.datetime.strptime(date_to, "%Y%m%d")
            where.append("time <= " + date_to.strftime("DATE '%Y %m %d'"))
            req_params["dt"] = date_to
            url_params["dt"] = date_to.strftime("%Y%m%d")

        if joins:
            query += ''.join(joins)
            total_query += ''.join(joins)
        if where:
            query += "where " + " and ".join(where)
            total_query += "where " + " and ".join(where)
        query += " group by id, message, author, time order by time "

        my_url_no_page = "/feedback5?" + urlencode(url_params) + "&"

        # pagination
        page = int(self.get_argument("pg", 1, True))
        max_on_page = int(self.get_argument("mp", 10, True))
        req_params['pg'] = page
        req_params['mp'] = max_on_page

        query += " limit  {} offset  {} ".format(max_on_page, max_on_page * (page - 1))

        self.logger.info("Query: %s", query)
        self.logger.info("Total query: %s", total_query)
        cur.execute(total_query)
        page_count = math.ceil(cur.fetchone()[0] / max_on_page)

        cur.execute(query)

        page_template = self.template_loader.load('feedback.html')

        self.write(page_template.generate(techs=techs, messages=cur.fetchall(), pages=page_count,
                                          page=page, req_params=req_params, my_url=my_url_no_page))
