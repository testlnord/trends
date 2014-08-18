"""Normalizes all data and generates reports """
import logging

import psycopg2
from ..config import config
from . import statmodule

logger = logging.getLogger(__name__)


def normalize():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, info::json from techs")
    for tech_id, tech_info in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("delete from reports_2 where tech_id = %s", (tech_id,))
        data_cur.execute("insert into reports_2(tech_id, time, value)  "
                         "select tech_id, time, avg(value) as vavg from reports_1 "
                         "where tech_id = %s group by tech_id, time", (tech_id,))
        connection.commit()

    pass


def normalize_google():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, info::json from techs")
    for tech_id, tech_info in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='google' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in google for tech %s", tech_info['name'])
            continue
        data = data[:-1]
        data = statmodule.freq_month(data)
        data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'google' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('google', tech_id, d, v) for d, v in data))
        connection.commit()


def normalize_wiki():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, info::json from techs")
    for tech_id, tech_info in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='wiki' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in wiki for tech %s", tech_info['name'])
            continue
        data = data[:-1]
        data = statmodule.freq_month(data)
        data = statmodule.sort_ts(data)
        data = statmodule.median_filter(data)
        data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'wiki' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('wiki', tech_id, d, v) for d, v in data))
        connection.commit()


def normalize_itj():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, info::json from techs")
    for tech_id, tech_info in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='itj' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in itj for tech %s", tech_info['name'])
            continue

        data = data[:-1]
        data = statmodule.freq_month(data)
        data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'itj' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('itj', tech_id, d, v) for d, v in data))
        connection.commit()
    pass


def normalize_sot():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, info::json from techs")
    for tech_id, tech_info in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='sot' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in sot for tech %s", tech_info['name'])
            continue

        data = data[:-1]
        data = statmodule.freq_month(data)
        data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'sot' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('sot', tech_id, d, v) for d, v in data))
        connection.commit()
    pass


def normalize_sousers():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, info::json from techs")
    for tech_id, tech_info in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='sousers' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in sousers for tech %s", tech_info['name'])
            continue

        data = data[:-1]
        data = statmodule.freq_month(data)
        data = statmodule.divergence(data)
        data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'sousers' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('sousers', tech_id, d, v) for d, v in data))
        connection.commit()
    pass