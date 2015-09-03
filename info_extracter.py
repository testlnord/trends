#!/usr/bin/env python3
from core.updaters.google import GoogleUpdater
from core.updaters.sot import SotUpdater
from core.updaters.wiki import WikiUpdater
from core.updaters.itj import ItjUpdater

import psycopg2
from core.config import config

import sys


def get_id_by_name(tech_name):
    conn = psycopg2.connect(database=config["db_name"],
                            user=config["db_user"],
                            password=config["db_pass"])

    #cur =


def get_name_by_id(tech_id):
    conn = psycopg2.connect(database=config["db_name"],
                            user=config["db_user"],
                            password=config["db_pass"])

    cur = conn.cursor()
    cur.execute("select info::JSON->>'name' from techs where id = %s", (tech_id,))
    return cur.fetchone()[0]


def main():
    if len(sys.argv) != 2:
        print("Usage: info_extracter.py <TECH_NAME|TECH_ID>")
        return

    tech_id = None
    try:
        tech_id = int(sys.argv[1])
    except ValueError:
        print("TECH_NAME funct doesn't work. Use TECH_ID instead.")
        return
        #tech_id = get_id_by_name(sys.argv[1])

    tech_name = get_name_by_id(tech_id)

    print("Keywords for technology: {} (id={})".format(tech_name, tech_id))
    print("Google: ", GoogleUpdater().getWordsForTech(tech_id))
    print("Wiki: ", WikiUpdater().getWordsForTech(tech_id))
    print("SO: ", SotUpdater().getWordsForTech(tech_id))
    print("Itj: ", ItjUpdater().getWordsForTech(tech_id))


if __name__ == "__main__":
    main()