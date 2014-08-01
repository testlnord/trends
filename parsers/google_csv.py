"""Module uses ability to download csv files from google trends
"""
from io import StringIO
import pickle
import random
import time
import urllib
import datetime
import selenium.common

import selenium.webdriver as webdriver

#import contextlib
#import os
#import lxml.html as LH

__author__ = 'user'


from parsers.parser import Parser
import csv
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GoogleCsvParser(Parser):

    init_dir = "data/gcsv"
    browser = None

    def get_raw_data(self, response):
        reader_file = StringIO(response.decode())
        reader = csv.reader(reader_file, delimiter=',')
        start = False
        result = []
        for row in reader:
            if row and row[0] == 'Week':
                start = True
                continue
            if start and not row:
                break
            if start:
                d = datetime.datetime.strptime(row[0][:10], '%Y-%m-%d')
                if datetime.datetime.now() - datetime.timedelta(weeks=1) < d:
                    break
                v = int(row[1])
                result.append((d.date(), v))
        return result



if __name__ == '__main__':
    pass





