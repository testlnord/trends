"""ITJ source DBI """
import datetime
from .dbi import DBI


class ItjDBI(DBI):
    _table_schemas = {
        'itj_names': {
            'id': 'INTEGER PRIMARY KEY ASC',
            'name': 'TEXT UNIQUE',
            'tid': 'INTEGER REFERENCES techs(id)',
            'active': 'INTEGER'
        },
        'itj_stat': {
            'date_from': 'DATETIME',
            'value': 'REAL',
            'expid': 'INTEGER REFERENCES itj_export_dates(id)'
        },
        'itj_export_dates': {
            'nid': 'INTEGER REFERENCES itj_names(id)',
            'id': 'INTEGER PRIMARY KEY ASC',
            'export_date': 'DATETIME'
        }
    }

    def __init__(self):
        super().__init__()

    def get_series_data(self, tech_name, date_from=None, date_to=None):
        query = "select date_from, value from itj_stat where expid = ?"
        if date_from is not None:
            assert isinstance(date_from, datetime.date), "date_from must be datetime.date object"
            query += ' and date_from > ' + date_from.strftime('%Y-%m-%d')
        if date_to is not None:
            assert isinstance(date_to, datetime.date), "date_to must be datetime.date object"
            query += ' and date_from < ' + date_to.strftime('%Y-%m-%d')

        last_date_id, last_date = self.get_last_date_for_tech(tech_name)

        cursor = self.conn.execute(query, (last_date_id,))
        result = list(cursor)
        return result

    def get_last_date_for_tech(self, tech_name):
        cursor = self.conn.execute('SELECT ied.id, max(export_date) FROM itj_export_dates AS ied INNER JOIN '
                                   'itj_names ON nid = itj_names.id INNER JOIN '
                                   'techs ON techs.id = tid WHERE tech_name = ? GROUP BY ied.id', (tech_name,))
        return cursor.fetchone()

    def add_series_data(self, fresh_data, tech):
        name_id = self.get_name_id(tech)
        cursor = self.conn.execute("INSERT INTO itj_export_dates (nid, export_date) VALUES (?, ?)",
                                   (name_id, datetime.datetime.now()))
        expid = cursor.lastrowid

        self.conn.executemany("INSERT INTO itj_stat (date_from, value, expid) VALUES (?, ?, ?)",
                              ((d, v, expid) for d, v in fresh_data))
        self.conn.commit()

    def add_name(self, name, tech_name):
        cursor = self.conn.execute("select id from techs where tech_name = ?", (tech_name,))
        tech_id = cursor.fetchone()[0]
        self.conn.execute("insert into itj_names (name, tid, active) values (?, ?, ?)",
                          (name, tech_id, 1))
        self.conn.commit()

    def get_name_id(self, tech_name):
        cursor = self.conn.execute("SELECT itj_names.id FROM itj_names INNER JOIN techs ON techs.id = tid "
                                   "WHERE tech_name = ?", (tech_name,))
        name_id = cursor.fetchone()
        if name_id is not None:
            return name_id[0]
        else:
            return None


if __name__ == "__main__":
    pass