import json
import tornado.ioloop
import tornado.web
from tornado import template
import psycopg2
from tornado.escape import json_encode


class MainHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader("templates")
        self.db_connection = psycopg2.connect(database='new.db', user='user', password='')

    def get(self):
        cur = self.db_connection.cursor()
        cur.execute("select id, info::json from techs")
        template = self.template_loader.load('index.html')
        self.write(template.generate(techs=cur.fetchall()))

class AjaxHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader("templates")
        self.db_connection = psycopg2.connect(database='new.db', user='user', password='')

    def get(self, slug):
        try:
            tid = int(slug)
        except ValueError:
            self.write("{}")  # todo redirect or 404 error
            return
        cur = self.db_connection.cursor()
        cur.execute("select source, to_char(time, 'YYYY MM DD'), value from reports_1 where tech_id = %s", (tid,))
        res = {}
        for rec in cur.fetchall():
            if rec[0] not in res:
                res[rec[0]] = []
            res[rec[0]].append({'date': rec[1], 'val': rec[2]})

        cur.execute("select to_char(time, 'YYYY MM DD'), value from reports_2 where tech_id = %s", (tid,))
        res['total'] = sorted(({'date': d, 'val': v} for d, v in cur.fetchall()), key=lambda x:x['date'])

        min_dates = []
        max_dates = []
        for k in res:
            min_dates.append(min(res[k], key=lambda x: x['date'])['date'])
            max_dates.append(max(res[k], key=lambda x: x['date'])['date'])
        max_min_date = max(min_dates)
        min_max_date = min(max_dates)

        for k in res:
            res[k] = {v['date']: v['val'] for v in res[k] if min_max_date >= v['date'] >= max_min_date}

        captions = ["date"]+list(res.keys())
        csv_lines = ['\t'.join(captions)]

        for date in sorted(res['total'].keys()):
            words = [date]
            for caption in captions[1:]:
                try:
                    words.append(str(res[caption][date]))
                except KeyError:
                    words.append("0")
            csv_lines.append('\t'.join(words))

        self.write('\n'.join(csv_lines))

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/tech/([^/]+)", AjaxHandler)
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
