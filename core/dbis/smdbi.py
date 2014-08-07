"""Source manager database interface """
from .dbi import DBI

class SourmManagerDBI(DBI):
    _table_schemas = {
        'techs': {
            'id': 'INTEGER PRIMARY KEY ASC',
            'tech_name': 'TEXT UNIQUE'
        }
    }

    def __init__(self):
        super().__init__()

    def get_tech(self, tech_name):
        cursor = self.conn.execute("SELECT * from techs where tech_name = ?", (tech_name, ))
        return cursor.fetchone()

    def add_tech(self, tech_name):
        print("added tech")
        self.conn.execute("INSERT into techs (tech_name) values(?)", (tech_name,))
        self.conn.commit()

if __name__ == "__main__":
    pass