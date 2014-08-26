"""tornado handlers"""
import logging
from tornado import template
import psycopg2
import tornado.web
from config import config
import json
from itertools import zip_longest


class MainHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def get(self):
        tech_id = self.get_argument("tech_selector", '')
        try:
            tech_id = int(tech_id)
            self.redirect("/tech#" + str(tech_id))
            return
        except ValueError:
            pass
        cur = self.db_connection.cursor()
        cur.execute("SELECT id, info::JSON FROM techs")
        page_template = self.template_loader.load('index.html')
        self.write(page_template.generate(techs=cur.fetchall()))


class TechsHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def get(self):
        page_template = self.template_loader.load('techs.html')
        cur = self.db_connection.cursor()
        cur.execute("SELECT id, info::JSON FROM techs")
        self.write(page_template.generate(techs=cur.fetchall()))


def get_norm_data(connection, tids):
    cur = connection.cursor()
    a = ','.join((str(x) for x in tids))
    cur.execute("SELECT id, info::JSON FROM techs WHERE id IN (" + a + ')')
    result = {i: {'tech_name': info['name']} for i, info in cur.fetchall()}
    for tid in tids:
        res = {}
        cur.execute("select source, to_char(time, 'YYYY MM DD'), value from reports_1 where tech_id = %s", (tid,))

        for rec in cur.fetchall():
            if rec[0] not in res:
                res[rec[0]] = []
            res[rec[0]].append((rec[1], rec[2]))

        min_dates = []
        max_dates = []
        for k in res:
            min_dates.append(min(res[k], key=lambda x: x[0])[0])
            max_dates.append(max(res[k], key=lambda x: x[0])[0])
        max_min_date = max(min_dates)
        min_max_date = min(max_dates)
        for k in res:
            res[k] = {d: v for d, v in res[k] if min_max_date >= d >= max_min_date}
        result[tid].update(res)
    # renorm values
    # get min and max for each of source in selected techs
    minmax_dict = {}
    for res in result.values():
        for k in res:
            if k == 'tech_name':
                continue
            if k not in minmax_dict:
                minmax_dict[k] = {'min': min(res[k].values()), 'max': max(res[k].values())}

            else:
                minmax_dict[k] = {'min': min(minmax_dict[k]['min'], min(res[k].values())),
                                  'max': max(minmax_dict[k]['max'], max(res[k].values()))}
    # normalize values with new min and max
    for res in result.values():
        average = {}
        for k in res:
            if k == 'tech_name':
                continue
            res[k] = [
                {'date': d, 'value': (v - minmax_dict[k]['min']) / (minmax_dict[k]['max'] - minmax_dict[k]['min'])}
                for d, v in res[k].items()]
            if k == 'google' and len(res) > 2:
                continue
            if not average:
                average = {d['date']: [d['value']] for d in res[k]}
            else:
                [average[d['date']].append(d['value']) for d in res[k]]  # inline for loop
        res['average'] = [{'date': d, 'value': (sum(v)/len(v))} for d, v in average.items()]
    return result


class CsvHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def get(self, slug):
        args = slug[:-4].split(',')
        if len(args) < 2:
            self.logger.warning("Bad csv request: %s", slug)
            self.write_error(406)
            return
        self.set_header("Content-Type", "text/csv")
        self.set_header("Content-Disposition", "attachment")
        if args[0] == 'norm':
            try:
                self.write(self.to_csv(self.norm_data(args[1:])))
            except ValueError:
                self.logger.warning("Can't parse request: %s", slug)
                self.write_error(406)
        elif args[0] == 'raw':
            try:
                self.write(self.to_csv(self.raw_data(args[1:])))
            except (ValueError, KeyError):
                self.logger.warning("Can't parse request: %s", slug)
                self.write_error(406)
        else:
            self.logger.warning("Bad css request type (must be raw or norm): %s", slug)
            self.write_error(406)
            return

    def raw_data(self, args):
        if len(args) == 1 and args[0].isnumeric():
            query = "SELECT source AS name, time, value FROM rawdata WHERE tech_id = " + args[0]
        else:
            query = "SELECT info::JSON->>'name' AS name, time, value FROM rawdata " \
                    "inner JOIN techs ON tech_id = id " \
                    "WHERE  tech_id IN (" + ','.join(args[1:]) + ") AND source = '" + args[0] + "'"
        self.logger.debug("Selecting query: %s", query)
        cur = self.db_connection.cursor()
        cur.execute(query)
        res = {}
        for name, t, v in cur.fetchall():
            if name not in res:
                res[name] = []
            res[name].append((t.strftime("%Y %m %d"), v))
        return res

    @staticmethod
    def to_csv(result):
        names = list(result)
        #make header
        response = [','.join("time, {}".format(x) for x in names)]
        #make body
        for line in zip_longest(*[sorted(result[name], key=lambda x: x[0]) for name in names], fillvalue=("NA", "NA")):
            response.append(','.join(str(pair[0]) + ',' + str(pair[1]) for pair in line))
        return '\n'.join(response)

    def norm_data(self, args):
        if len(args) == 1 and args[0].isnumeric():
            tids = [int(args[0])]
            per_source_report = False
        else:
            tids = [int(arg) for arg in args[1:]]
            per_source_report = True
        result = get_norm_data(self.db_connection, tids)
        self.logger.debug(result)
        if per_source_report:
            result = {result[k]['tech_name']: result[k][args[0]] for k in result}
        else:
            result = {k: v for k, v in result[tids[0]].items() if k != 'tech_name'}

        for k in result:
            result[k] = ((d['date'], d['value']) for d in result[k])
        return result


class AjaxHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])


    def get(self, slug):
        try:
            tids = [int(x) for x in slug.split(',')]
        except ValueError:
            self.write_error(406)
            return
        result = get_norm_data(self.db_connection, tids)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(result))

