""" get and parse data about article page visits from wikipedia """

import json
import os
import pickle
import re
import urllib.request as ur
import urllib.error
import datetime
import sqlite3
import urllib.parse as urlp

from numpy import median
import rpy2.robjects

from src.parsers.parser import Parser


rpy2.robjects.r.library('pracma')
def outlinerMAD(vals):
    df = rpy2.robjects.IntVector(vals)
    d = rpy2.robjects.r.hampel(df, 10)
    return list(d[0])

class WikiParser(Parser):
    init_dir = "data/wiki2"
    wiki_links = None

    def init_conn(self, path):
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY ASC, page_name TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS pdata (pid INTEGER, pdata BLOB)")
        conn.commit()
        return conn

    def select_again(self, query, properties=None):
        """ Useless method

        Creepy stuff happens. All my selects runs just with second try. First they all fall
        with "Error binding parameter 0 - probably unsupported type" error
        :param query: SQL query
        :param properties: tuple with params (if any)
        :return: what sqlite3.connection.execute() returns
        """
        tries = 0
        max_tries = 5
        while True:
            try:
                if properties is None:
                    r = self.conn.execute(query)
                else:
                    r = self.conn.execute(query, properties)
                return r
            except sqlite3.InterfaceError as e:
                tries += 1
                if tries > max_tries:
                    raise
                print(e)

    def get_response(self, query):
        if self.wiki_links is None:
            self.wiki_links = pickle.load(open('parsers/total_names.pkl', 'rb'))
        try:
            links = self.wiki_links[query.replace(' ', '-')]
        except KeyError:
            links = [query.replace(' ', '_')]

        resp_dir = os.path.join(self.init_dir, query, "respd")
        if not os.path.exists(resp_dir):
            os.mkdir(resp_dir)
        self.conn = self.init_conn(os.path.join(resp_dir, "res.db"))

        for link in links:
            print(link)
            if list(self.select_again("select * from pages where page_name=?", (link,))):
                continue
            # get data
            data_blob = pickle.dumps(self.get_part_response(link))
            # insert data
            self.conn.execute("insert into pages(page_name) values(?)", (link,))
            self.conn.commit()
            r = self.select_again("select * from pages where page_name=?", (link,))
            id = next(r)[0]
            self.conn.execute("insert into pdata values(?, ?)", (id, data_blob))
            self.conn.commit()



        # sum all views
        data_parts = []
        for link in links:
            pdata_cur = self.select_again("select pdata from pdata inner join pages on pid = id where page_name = ?",
                                      (link,))
            pdata = next(pdata_cur)[0]
            dict_list = [json.loads(json_str)['daily_views'] for json_str in pickle.loads(pdata)]
            data_part = {}
            for d in dict_list:
                for k in d:
                    if k in data_part.keys():
                        data_part[k] = max(data_part[k], d[k])
                    else:
                        data_part[k] = d[k]
            data_parts.append(data_part)

        result = {}
        for date in data_parts[0]:
            sum = 0
            for part in data_parts:
                sum += part[date]
            result[date] = sum

        return result

    def get_part_response(self, wiki_name):
        wiki_name = wiki_name.replace(" ", "_")

        user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
        headers = {'User-Agent': user_agent}

        month = datetime.date(2007, 12, 1)
        result = []
        while month <= datetime.datetime.now().date():
            url = "http://stats.grok.se/json/en/" + month.strftime("%Y%m") + "/" + urlp.quote(wiki_name)
            req = ur.Request(url, headers=headers)
            while True:
                try:
                    response = ur.urlopen(req)
                    month = datetime.date(month.year + int(month.month / 12), month.month % 12 + 1, 1)  # add a month
                    break
                except urllib.error.HTTPError:
                    self.sleep(1, 3)
            data = response.read().decode("utf-8")
            result.append(data)
            print(month)

            #self.sleep(1, 3)
        return result

    def get_raw_data(self, response):

        result = []
        date_expr = re.compile('(\d*)-(\d\d)-(\d\d)')
        for k in response:
            date_parsed = date_expr.match(k)
            if date_parsed:
                # I have to make 1st day of month and then add days,
                # cause response contains dates like '2012-02-31'
                # which are '2012-03-02' really
                date = datetime.date(int(date_parsed.group(1)), int(date_parsed.group(2)), 1)
                date += datetime.timedelta(days=(int(date_parsed.group(3)) - 1))
                result.append((date, response[k]))
        return result

    def get_data(self, raw_data):
        raw_data = sorted(raw_data, key=lambda x: x[1])
        vals = [x for d, x in raw_data]
        pred_z = 0
        for idx, v in enumerate(vals):
            if v > 1:
                pred_z = idx
                break
        vals = vals[pred_z:]
        med = median(vals)
        mad = median([abs(x - med) for x in vals])
        #vals = [x if med - 4 * mad < x < med + 4 * mad else None for x in vals]
        try:
            vals = outlinerMAD(vals)
            #
            # df = pandas.DataFrame([0] + vals)
            # df = df.interpolate()
            # vals = list(df[0])[1:]
            data = [(d, vals[idx - pred_z]) if idx > pred_z else (d, 0) for idx, (d, _) in enumerate(raw_data)]
        except TypeError:
            data = raw_data
        return super().get_data(data)


if __name__ == '__main__':
    wp = WikiParser()
    wp.parse_fresh("azure")