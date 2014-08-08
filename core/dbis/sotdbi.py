"""Stackoverflow source dbi """
import logging

__author__ = 'user'

"""Dbi for wiki source """
import datetime
import sqlite3
from ..config import config
from .dbi import DBI
__author__ = 'user'


class SotDBI(DBI):
    _table_schemas = {
        'sot_tags': {
            'id': 'INTEGER PRIMARY KEY ASC',
            'tid': 'INTEGER REFERENCES techs(id)',
            'tag': 'TEXT'
        },
        'sot_stat': {
            'date_from': 'DATETIME',
            'questions': 'INTEGER',
            'tid': 'INTEGER REFERENCES sot_tags(id)'
        }
    }

    def __init__(self):
        super().__init__()

    def get_tag(self, tech_name):
        cursor = self.conn.execute("SELECT tag, sot_tags.id FROM sot_tags INNER JOIN techs ON techs.id = tid "
                                   "WHERE tech_name = ?", (tech_name,))
        return cursor.fetchone()

    def get_last_date(self, tag_id):
        cursor = self.conn.execute("select max(date_from) from sot_stat" /
                                   "where tid = ?", (tag_id, ))
        result = cursor.fetchone()[0]
        return result

    def get_series_data(self, tech_name, date_from=None, date_to=None):
        query = "select date_from, questions from sot_stat where tid = ?"
        if date_from is not None:
            assert isinstance(date_from, datetime.date), "date_from must be datetime.date object"
            query += ' and date_from > ' + date_from.strftime('%Y-%m-%d')
        if date_to is not None:
            assert isinstance(date_to, datetime.date), "date_to must be datetime.date object"
            query += ' and date_from < ' + date_to.strftime('%Y-%m-%d')

        try:
            tag_name, tag_id = self.get_tag(tech_name)
            logging.debug("Tag %s, id %s founded for technology %s ", tag_name, tag_id, tech_name)
        except TypeError:
            return None  # todo raise exception

        cursor = self.conn.execute(query, (tag_id,))
        return list(cursor)

    def add_series_data(self, fresh_data, tag_id):
        self.conn.executemany("insert into sot_stat (date_from, questions, tid) values (?, ?, ?)",
                              ((d, v, tag_id) for d, v in fresh_data))
        self.conn.commit()

    def add_tag(self, tag, tech_name):
        cursor = self.conn.execute("select id from techs where tech_name = ?", (tech_name,))
        tech_id = cursor.fetchone()[0]
        cur = self.conn.execute("insert into sot_tags (tag, tid) values (?, ?)",
                          (tag, tech_id))
        self.conn.commit()
        return cur.lastrowid

if __name__ == "__main__":
    pass