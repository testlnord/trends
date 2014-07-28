""" getting and parsing trends right from stackoverlfow """
import gzip
import json
import os
import pickle
import random
import time
__author__ = 'arkady'



import urllib.request as ur
import re
import datetime
from parsers.parser import Parser
from urllib.parse import quote
import selenium.webdriver


class SOTParser(Parser):
    init_dir = "data/sot_old"
    start_week = datetime.datetime(2008, 7, 28)
    end_week = datetime.datetime(2012, 7, 16)
    #start_week = datetime.datetime(2012, 7, 16)
    #end_week = datetime.datetime.now()

    def __init__(self):
        super(SOTParser).__init__()
        self.token = "adsf"
        # profile = selenium.webdriver.FirefoxProfile("/home/user/.mozilla/firefox/tmmwba0i.default/")
        # driver = selenium.webdriver.Firefox(firefox_profile=profile)
        #
        # driver.get("https://stackexchange.com/oauth/dialog?"
        #            "client_id=3330&"
        #            "scope=no_expiry&"
        #            "redirect_uri=https://stackexchange.com/oauth/login_success"
        #            "")
        # input("Press `enter` to continue.")
        # url = driver.current_url
        # print(url)
        # if "login_success" not in url:
        #     raise PermissionError("Auth failed")
        # match = re.search("access_token=(.*)", url)
        # self.token = match.group(1)


    def get_response(self, query):
        tag = query.replace(" ", "-")
        result = []
        week = self.start_week
        next_week = week + datetime.timedelta(days=7)
        print(tag)
        while next_week < self.end_week:
            url = "http://api.stackexchange.com/2.2/questions?" \
                  "fromdate={0}&" \
                  "todate={1}&" \
                  "key={3}&" \
                  "order=desc&sort=activity&site=stackoverflow&filter=!)V)MSZJYs)y".format(
                  int(week.timestamp()), int(next_week.timestamp()), quote(self.token), quote("gytnic74fozY)jD39pQSzg((")
                  )
            if not tag == "t":
                url += "&tagged={0}".format(quote(tag))
            print(' ', url)
            req = ur.Request(url)
            try:
                resp = ur.urlopen(req)
            except url
            data = resp.read()
            data = gzip.decompress(data)

            result.append((week, json.loads(data.decode())))
            print(' ', result[-1])
            #pickle.dump(result, open("total.pkl", 'wb'))
            time.sleep(random.randint(1, 7))

            week = next_week
            next_week = week + datetime.timedelta(weeks=1)

        return result

    def get_raw_data(self, response):
        total_resp = os.path.join(self.init_dir, "t/response")  # "parsers/total.pkl"
        totals = pickle.load(open(total_resp, "rb"))
        result = []
        total_idx = 0
        for date, v in response:
            while date < totals[total_idx][0]:
                total_idx += 1
            v = v["total"]
            v_t = totals[total_idx][1]["total"]
            result.append((date.date(), v/v_t))
        return result



