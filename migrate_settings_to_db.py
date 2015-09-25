import json
import logging
import datetime
import psycopg2
from core.config import config



def migrate_names(connection, logger):
    logger.info("migrating names")
    cur_sel = connection.cursor()
    cur_sel.execute("SELECT id, info FROM techs")
    for row in cur_sel.fetchall():
        r_id = int(row[0])
        r_info = row[1]
        r_name = r_info['name']
        del r_info['name']
        cur_upd = connection.cursor()
        cur_upd.execute("update techs set info = %s, name = %s where id = %s",
                        (json.dumps(r_info), r_name, r_id))


def create_name_field(connection, logger):
    logger.info("creating name field")
    cur = connection.cursor()
    cur.execute("ALTER TABLE techs ADD name VARCHAR(255);")


def create_settings_table(connection, logger):
    logger.info("creating tables for settings")
    cur = connection.cursor()
    cur.execute("""
    CREATE TABLE source_settings(
        tech_id INTEGER,
        source VARCHAR(10),
        settings JSON,
        last_update_date DATE
    );
    """)


def migrate_settings(connection, logger):
    logger.info("Migrate settings to database")
    sources = {
        'sot': 'src_conf/sot.json',
        'wiki': 'src_conf/wiki.json',
        'google': 'src_conf/google.json',
        'itj': 'src_conf/itj.json'
    }
    for source in sources:
        logger.info("Migrating settings for source {}".format(source))
        settings_dict = json.load(open(sources[source]))
        techs_dict = settings_dict['techs']
        del settings_dict['techs']
        cur_ins_settings = connection.cursor()
        cur_ins_settings.execute("update sources set config = %s where name = %s",
                                 (json.dumps(settings_dict), source))

        for tech_id in techs_dict:
            item_state = techs_dict[tech_id]
            # getting last date
            last_date = datetime.date(2001, 1, 1)
            if 'earliest_date' in settings_dict:
                try:
                    last_date = datetime.datetime.strptime(settings_dict['earliest_date'], config['date_format']).date()
                except ValueError as e:
                    logger.error("Wrong earliest date format for source = {}".format(source))
                    logger.error(str(e))
            try:
                last_date = item_state['last_date']
                del item_state['last_date']
                last_date = datetime.datetime.strptime(last_date, config['date_format']).date()
            except KeyError as e:
                logger.error("Can't get last date for tech_id={} and source={}".format(tech_id, source))
                logger.error(str(e))
            except ValueError as e:
                logger.error("Wrong date format for tech_id = {} and source = {}".format(tech_id, source))
                logger.error(str(e))

            cur_tech_ins = connection.cursor()
            cur_tech_ins.execute("insert into source_settings (tech_id, source, settings, last_update_date)"
                                 "values (%s, %s, %s, %s)", (int(tech_id), source, json.dumps(item_state), last_date))


def main():
    logger = logging.getLogger("migrate_settings")
    try:
        with psycopg2.connect(database=config['db_name'], user=config['db_user'],
                              password=config['db_pass']) as connection:
            create_name_field(connection, logger)
            migrate_names(connection, logger)
            create_settings_table(connection, logger)
            migrate_settings(connection, logger)
    except Exception as e:
        logger.error("Couldn't connect to database")
        logger.error(str(e))
        raise


if __name__ == "__main__":
    main()
