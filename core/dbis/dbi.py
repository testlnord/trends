"""Abstract DBI class """

import sqlite3
from ..config import config

__author__ = 'user'

class DBI:
    def __init__(self):
        self.conn = sqlite3.connect(config['dbpath'])
        self._create_tables()
        pass

    def _create_tables(self):
        table_creation = "create table if not exists {table_name} ({column_def})"
        for table, schema in self._table_schemas.items():
            columns = ', '.join(k+' '+v for k, v in schema.items())
            self.conn.execute(table_creation.format(table_name=table, column_def=columns))
        self.conn.commit()

if __name__ == "__main__":
    pass