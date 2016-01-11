import jaydebeapi
import datetime
import itertools
import csv
from core.crawlers.sot_crawler import SotCrawler
from core.config import config
from core.updaters.sot import SotUpdater

SO_api_key = SotUpdater().settings["apikey"]

conn = jaydebeapi.connect('net.sourceforge.jtds.jdbc.Driver',
                          ['jdbc:jtds:sqlserver://jetstat.labs.intellij.net:1433;databaseName=StackOverflowStatistic',
                           'so_write',
                           'dmitrykalashnikov'],
                          ['/home/user/.PyCharm40/config/jdbc-drivers/jtds-1.2.5.jar'])

min_date = datetime.datetime(2008, 7, 31)
max_date = datetime.datetime(2015, 3, 1)
crawler = SotCrawler(SO_api_key)
print(crawler.get_data("", min_date))

print("FINISH")