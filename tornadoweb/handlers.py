"""tornado handlers"""
import logging
from tornado import template
import psycopg2
import tornado.web
from config import config
import json


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
            self.redirect("/tech#"+str(tech_id))
            return
        except ValueError:
            pass
        cur = self.db_connection.cursor()
        cur.execute("select id, info::json from techs")
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
        cur.execute("select id, info::json from techs")
        self.write(page_template.generate(techs=cur.fetchall()))


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
        cur = self.db_connection.cursor()
        a = ','.join((str(x) for x in tids))
        cur.execute("select id, info::json from techs where id in (" + a + ')')
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
                res[k] = [{'date': d, 'value': (v-minmax_dict[k]['min'])/(minmax_dict[k]['max']-minmax_dict[k]['min'])}
                          for d, v in res[k].items()]
                if not average:
                    average = {d['date']: [d['value']] for d in res[k]}
                else:
                    [average[d['date']].append(d['value']) for d in res[k]]  # inline for loop
            res['average'] = [{'date': d, 'value': (sum(v)/len(v))} for d, v in average.items()]
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(result))

