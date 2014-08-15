""" Move data from pkl files to database

Need only during development.
"""
import gzip
import json
import os
import pickle
from psycopg2._json import Json
from core.config import config
import psycopg2
import csv
import datetime
from core.link_makers.itjlm import ItjLinkMaker


def migrate_data():
    conn = psycopg2.connect(database=config["db_name"], user=config["db_user"], password=config["db_pass"])
    cur = conn.cursor()

    # create tables
    cur.execute(open("core/db/create.sql").read())
    conn.commit()

    # add sources
    cur.execute("insert into sources(name, config) values(%s, %s)", ('wiki', Json({'refresh_time': 'week'})))
    cur.execute("insert into sources(name, config) values(%s, %s)", ('itj', Json({'refresh_time': 'month'})))
    cur.execute("insert into sources(name, config) values(%s, %s)", ('sot', Json({'refresh_time': 'week'})))
    cur.execute("insert into sources(name, config) values(%s, %s)", ('google', Json({'refresh_time': 'month'})))

    # add techs
    techs = pickle.load(open("top_names.pkl", 'rb'))
    tech_ids = {}
    for tech in techs:
        cur.execute("insert into techs(info) values (%s) returning id", (Json({'name': tech}),))
        tid = cur.fetchone()
        tech_ids[tech] = tid[0]
    conn.commit()

    # add wiki data
    for tech, tid in tech_ids.items():
        data_path = os.path.join("data", "wiki2", tech, "raw_data")
        if os.path.exists(data_path):
            data = pickle.load(open(data_path, 'rb'))
            cur.executemany("insert into rawdata(source, tech_id, time, value) values(%s, %s, %s, %s)",
                            (('wiki', tid, d, v) for (d, v) in data))
    conn.commit()

    # add sot data
    for tech, tid in tech_ids.items():
        data_path = os.path.join("data", "sot_my", tech, "response")
        if os.path.exists(data_path):
            data = pickle.load(open(data_path, 'rb'))
            cur.executemany("insert into rawdata(source, tech_id, time, value) values(%s, %s, %s, %s)",
                            (('sot', tid, d, v['total']) for (d, v) in data))
    conn.commit()

    # add itj data
    for tech, tid in tech_ids.items():
        data_path = os.path.join("data", "itjobs", tech, "raw_data")
        if os.path.exists(data_path):
            data = pickle.load(open(data_path, 'rb'))
            cur.executemany("insert into rawdata(source, tech_id, time, value) values(%s, %s, %s, %s)",
                            (('itj', tid, d, round(v * 1000)) for (d, v) in data))
    conn.commit()

    # add google data
    data_path_1 = os.path.join("data", "gcsv")
    data_path_2 = "/home/user/Dropbox/google_trends/google-trends-csv-downloader/data"
    csv_files = [os.path.join(data_path_1, file) for file in os.listdir(data_path_1) if file.endswith(".xml")]
    csv_files += [os.path.join(data_path_2, file, "2004-present/0-5-31.csv") for file in os.listdir(data_path_2)
                  if os.path.exists(os.path.join(data_path_2, file, "2004-present/0-5-31.csv"))]
    for file in csv_files:
        with open(file) as opened_file:
            reader = csv.reader(opened_file, delimiter=',')
            start = False
            result = []
            name = ''
            for row in reader:
                if row and row[0] == 'Week':
                    start = True
                    name = row[1]
                    if name not in techs:  # ignore result if u don`t need it
                        break
                    continue
                if start and not row:
                    break
                if start:
                    d = datetime.datetime.strptime(row[0][:10], '%Y-%m-%d')
                    if datetime.datetime.now() - datetime.timedelta(weeks=1) < d:
                        break
                    v = int(row[1])
                    result.append((d.date(), v))

            if name and result:
                cur.executemany("insert into rawdata(source, tech_id, time, value) values(%s, %s, %s, %s)",
                                (('google', tech_ids[name], d, v) for (d, v) in result))
    conn.commit()


def migrate_sot_settings(conn):
    # sot settings
    with open("src_conf/sot.json", 'w') as sot_file:
        data = {'refresh_time': 'week',
                'earliest_date': datetime.datetime(2008, 7, 28).strftime("%Y-%m-%d"),
                'apikey': "gytnic74fozY)jD39pQSzg((",
                'techs': {}
        }
        cur_techs = conn.cursor()
        cur_techs.execute("select * from techs")
        cur_date = conn.cursor()
        for tid, name in cur_techs:
            name = name['name']
            cur_date.execute("select max(time) from rawdata where source='sot' and tech_id=%s", (tid,))
            date = cur_date.fetchone()
            if date[0] is None:
                date = data['earliest_date']
            else:
                date = date[0].strftime("%Y-%m-%d")
            data['techs'][tid] = {'tag': [name.replace(' ', '-')], 'last_date': date}
        json.dump(data, sot_file)


def migrate_wiki_settings(conn):
    # wiki settings
    with open("src_conf/wiki.json", 'w') as wiki_file:
        pages_dict = pickle.load(open("core/parsers/total_names.pkl", 'rb'))
        data = {'refresh_time': 'week',
                'earliest_date': datetime.datetime(2007, 12, 1).strftime("%Y-%m-%d"),
                'techs': {}
        }
        cur_techs = conn.cursor()
        cur_techs.execute("select * from techs")
        cur_date = conn.cursor()
        for tid, name in cur_techs:
            name = name['name']
            cur_date.execute("select max(time) from rawdata where source='wiki' and tech_id=%s", (tid,))
            date = cur_date.fetchone()
            if date[0] is None:
                date = data['earliest_date']
            else:
                date = date[0].strftime("%Y-%m-%d")
            data['techs'][tid] = {'pages': pages_dict[name.replace(' ', '-')], 'last_date': date}
        json.dump(data, wiki_file)


def migrate_google_settings(conn):
    with open("src_conf/google.json", 'w') as google_file:
        pages_dict = pickle.load(open("core/parsers/total_names.pkl", 'rb'))
        data = {'refresh_time': 'month',
                'techs': {},
                'proxies': json.load(open("proxies.json"))['proxies']
        }
        old_enough_date = datetime.datetime(2004, 1, 1).strftime("%Y-%m-%d")

        cur_techs = conn.cursor()
        cur_techs.execute("select * from techs")
        cur_date = conn.cursor()
        for tid, name in cur_techs:
            name = name['name']
            cur_date.execute("select max(time) from rawdata where source='google' and tech_id=%s", (tid,))
            date = cur_date.fetchone()
            if date[0] is None:
                date = old_enough_date
            else:
                date = date[0].strftime("%Y-%m-%d")
            data['techs'][tid] = {'name': [name], 'last_date': date}
        json.dump(data, google_file)


def migrate_itj_settings(conn):
    # itj settings
    linkmaker = ItjLinkMaker()
    with open("src_conf/itj.json", 'w') as itj_file:
        pages_dict = pickle.load(open("core/parsers/total_names.pkl", 'rb'))
        data = {'refresh_time': 'month',
                'techs': {}
        }
        old_enough_date = datetime.datetime(2004, 1, 1).strftime("%Y-%m-%d")
        cur_techs = conn.cursor()
        cur_techs.execute("select * from techs")
        cur_date = conn.cursor()
        for tid, name in cur_techs:
            name = name['name']
            try:
                link = linkmaker.make_links(name)
            except KeyError:
                link = ""
            print(name, link)

            cur_date.execute("select max(time) from rawdata where source='itj' and tech_id=%s", (tid,))
            date = cur_date.fetchone()
            if date[0] is None:
                date = old_enough_date
            else:
                date = date[0].strftime("%Y-%m-%d")
            data['techs'][tid] = {'link': [link], 'last_date': date}
        json.dump(data, itj_file)


def migrate_so_users_settings(conn):
    conf = json.load(open("src_conf/so_users.json"))
    for tid, tech in conf['techs'].items():
        tech['last_date'] = conf['earliest_date']
        conf['techs'][tid] = tech
    json.dump(conf, open("src_conf/so_users.json", 'w'))

def migrate_settings():
    """
    Maybe it will be settings later. For now it just json with source specific data.
    :return: Nothing
    """
    conn = psycopg2.connect(database=config['db_name'], user=config["db_user"], password=config["db_pass"])
    # migrate_sot_settings(conn)
    # migrate_wiki_settings(conn)
    # migrate_google_settings(conn)
    # migrate_itj_settings(conn)
    migrate_so_users_settings(conn)


if __name__ == "__main__":
    migrate_settings()
    # from core.utils.internet.internet import get_from_url
    # from core.utils.internet.internet import quote
    # sot = json.load(open("src_conf/sot.json"))
    # for tech in sot["techs"].values():
    #     tag = tech['tag'][0]
    #     url = "http://api.stackexchange.com/2.2/tags?order=desc" \
    #           "&min={0}&max={0}&sort=name&site=stackoverflow&key={1}".format(
    #         quote(tag), config["sources"]["so"]["apikey"])
    #     data = get_from_url(url, min_delay=2, max_delay=5, binary=True, force_wait=True)
    #     data = gzip.decompress(data)
    #     resp = json.loads(data.decode())
    #     print(len(resp['items']), tech)
