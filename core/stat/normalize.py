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
    techs_cur.execute("select id, name from techs")
    for tech_id, tech_name in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='google' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in google for tech %s", tech_name)
            continue
        data = statmodule.freq_month(data)
        #data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'google' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('google', tech_id, d, v) for d, v in data))
        connection.commit()


def normalize_wiki():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, name from techs")
    for tech_id, tech_name in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='wiki' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in wiki for tech %s", tech_name)
            continue
        data = statmodule.outliers_filter(data)
        data = statmodule.freq_month(data)
        data = statmodule.sort_ts(data)

        #data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'wiki' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('wiki', tech_id, d, v) for d, v in data))
        connection.commit()


def normalize_itj():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, name from techs")
    for tech_id, tech_name in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='itj' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in itj for tech %s", tech_name)
            continue

        data = statmodule.freq_month(data)
        #data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'itj' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('itj', tech_id, d, v) for d, v in data))
        connection.commit()
    pass


def normalize_sot():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    total_cur = connection.cursor()
    total_cur.execute("select time, value from rawdata where source = 'sot' and tech_id=103")  # total id
    total_data = {d: v for d, v in statmodule.freq_month(total_cur.fetchall())}
    techs_cur = connection.cursor()
    techs_cur.execute("select id, name from techs")
    for tech_id, tech_name in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='sot' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in sot for tech %s", tech_name)
            continue

        #data = data[:-1]
        data = statmodule.freq_month(data)
        data = [(d, v / total_data[d] if d in total_data else 0) for d, v in data]
        #data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'sot' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('sot', tech_id, d, v) for d, v in data))
        connection.commit()
    pass

def normalize_gitstars():
    connection = psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_pass'])
    techs_cur = connection.cursor()
    techs_cur.execute("select id, name from techs")
    for tech_id, tech_name in techs_cur:
        data_cur = connection.cursor()
        data_cur.execute("select time, value from rawdata where source ='gitstars' and tech_id=%s", (tech_id,))

        data = data_cur.fetchall()
        if not data:
            logger.debug("No data in getstars for tech %s", tech_name)
            continue

        data = statmodule.freq_month(data, month_average=False)
        #data = statmodule.normalize_series(data)
        data_cur.execute("delete from reports_1 where source = 'gitstars' and tech_id = %s", (tech_id, ))
        data_cur.executemany("insert into reports_1(source, tech_id, time, value) values(%s, %s, %s, %s)",
                             (('gitstars', tech_id, d, v) for d, v in data))
        connection.commit()
    pass




