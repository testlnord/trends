"""tornado handlers
Handlers for all tech data
"""
import logging
import sys
import traceback
from tornado import template
import psycopg2
import tornado.web

from tornadoweb.config import config
import json
from itertools import zip_longest


class MainHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.info("init main handler")
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def get(self):
        self.redirect("/tech#1")
        return
        tech_id = self.get_argument("tech_selector", '')
        try:
            tech_id = int(tech_id)
            self.redirect("/tech#" + str(tech_id))
            return
        except ValueError:
            pass
        cur = self.db_connection.cursor()
        cur.execute("SELECT id, info::JSON FROM techs")
        self.render('index.html', techs=cur.fetchall())


class TechsHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def get(self, *slug):
        if slug and len(slug) == 1:
            self.redirect('/tech#'+slug[0])

        cur = self.db_connection.cursor()
        cur.execute("SELECT id, name, info::JSON FROM techs")
        technologies = cur.fetchall()
        try:
            technologies = sorted(technologies, key=lambda x: x[1].lower())
            self.render('techs.html', techs=technologies,selectors_count=5)
        except Exception as e:
            t, e, tb = sys.exc_info()
            self.write(str(e))
            self.write("\n<br>\n")
            self.write(traceback.format_exc().replace('\n','\n<br>\n'))


def get_norm_data(connection, tids):
    # todo make nice filtration and summarizing
    cur = connection.cursor()
    a = ','.join((str(x) for x in tids))
    cur.execute("SELECT id, name, info::JSON FROM techs WHERE id IN (" + a + ')')
    result = {i: {'tech_name': name} for i, name, info in cur.fetchall()}
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
            #  I will remove filter. let's look what we will get
            # res[k] = {d: v for d, v in res[k] if min_max_date >= d >= max_min_date}
            res[k] = {d: v for d, v in res[k] if d >= max_min_date}
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
        average = {d:[] for k in res for d in res[k]}
        for k in res:
            if k == 'tech_name':
                continue
            res[k] = [
                {'date': d, 'value': (v/minmax_dict[k]['max'])} #(v - minmax_dict[k]['min']) / (minmax_dict[k]['max'] - minmax_dict[k]['min'])}
                for d, v in res[k].items()]
            if k == 'google' and len(res) > 1:
                continue
            if not average:
                average = {d['date']: [d['value']] for d in res[k]}
            else:
                [average[d['date']].append(d['value']) for d in res[k]]  # inline for loop
        res['average'] = [{'date': d, 'value': (sum(v)/len(v))} for d, v in average.items() if len(v)]
    return result


class CsvHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
                                              password=config['db_pass'])

    def get(self, slug):
        try:
            args = slug[:-4].split(',')
            if len(args) < 2:
                self.logger.warning("Bad csv request: %s", slug)
                self.write_error(406)
                return
            if args[0] == 'norm':
                try:
                    response = self.to_csv(self.norm_data(args[1:]))
                    self.set_header("Content-Type", "text/csv")
                    self.set_header("Content-Disposition", "attachment")
                    self.write(response)
                except ValueError:
                    self.logger.warning("Can't parse request: %s", slug)
                    self.write_error(406)
            elif args[0] == 'raw':
                try:
                    response = self.to_csv(self.raw_data(args[1:]))
                    self.set_header("Content-Type", "text/csv")
                    self.set_header("Content-Disposition", "attachment")
                    self.write(response)
                except (ValueError, KeyError):
                    self.logger.warning("Can't parse request: %s", slug)
                    self.write_error(406)
            else:
                self.logger.warning("Bad css request type (must be raw or norm): %s", slug)
                self.write_error(406)
                return
        except:
            self.write("Smt happens\n<br>\n")
            self.write(traceback.format_exc())

    def raw_data(self, args):
        if len(args) == 1 and args[0].isnumeric():
            query = "SELECT source AS name, time, value FROM rawdata WHERE tech_id = " + args[0]
        else:
            query = "SELECT name, time, value FROM rawdata " \
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
        response = [','.join("time,{}".format(x) for x in names)]
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
            try:
                tids = [int(x) for x in slug.split(',')]
            except ValueError:
                self.write_error(406)
                return
            result = get_norm_data(self.db_connection, tids)
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(result))
        except:
            self.write("Smth happens\n")
            self.write(traceback.format_exc())

