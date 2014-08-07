"""Dbi for wiki source """
import datetime
import sqlite3
from ..config import config
from .dbi import DBI
__author__ = 'user'


class WikiDBI(DBI):
    _table_schemas = {
        'wiki_pages': {
            'id': 'INTEGER PRIMARY KEY ASC',
            'tid': 'INTEGER REFERENCES techs(id)',
            'page': 'TEXT'
        },
        'wiki_stat': {
            'date_from': 'DATETIME',
            'visits': 'INTEGER',
            'pid': 'INTEGER REFERENCES wiki_pages(id)'
        }
    }

    def __init__(self):
        super().__init__()

    def get_pages(self, tech_name):
        cursor = self.conn.execute("SELECT page, wiki_pages.id FROM wiki_pages INNER JOIN techs ON techs.id = tid "
                                   "WHERE tech_name = ?", (tech_name,))
        result = []
        for rec in cursor:
            result.append(rec)
        return result

    def get_last_date(self, page_name):
        cursor = self.conn.execute("select max(date_from) from wiki_stat inner join wiki_pages on wiki_pages.id = pid "
                                   "where page = ?", (page_name, ))
        result = cursor.fetchone()[0]
        return result

    def get_series_data(self, tech_name, date_from=None, date_to=None):
        query = "select date_from, visits from wiki_stat where pid = ?"
        if date_from is not None:
            assert isinstance(date_from, datetime.date), "date_from must be datetime.date object"
            query += ' and date_from > ' + date_from.strftime('%Y-%m-%d')
        if date_to is not None:
            assert isinstance(date_to, datetime.date), "date_to must be datetime.date object"
            query += ' and date_from < ' + date_to.strftime('%Y-%m-%d')

        pages = self.get_pages(tech_name)
        result = []

        for page, page_id in pages:
            cursor = self.conn.execute(query, (page_id,))
            result.append(list(cursor))
        return result

    def add_series_data(self, fresh_data, page_id=None, page_name=None):
        assert page_id is not None or page_name is not None, 'Page id or name must be specified'
        if page_id is None:
            page_id = self._get_page_id(page_name)
        self.conn.executemany("insert into wiki_stat (date_from, visits, pid) values (?, ?, ?)",
                              ((d, v, page_id) for d, v in fresh_data))
        self.conn.commit()

    def _get_page_id(self, page_name):
        cursor = self.conn.execute('select id from wiki_pages where page = ?', (page_name,))
        return cursor.fetchone()[0]

    def add_pages(self, pages, tech_name):
        cursor = self.conn.execute("select id from techs where tech_name = ?", (tech_name,))
        tech_id = cursor.fetchone()[0]
        self.conn.executemany("insert into wiki_pages (page, tid) values (?, ?)",
                              ((p, tech_id) for p in pages))
        self.conn.commit()

if __name__ == "__main__":
    pass