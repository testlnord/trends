import logging
from itertools import zip_longest

import core.crawlers.indeed_crawler
import tornado
from tornado import template

from tornadoweb.config import config

class IndeedHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        self.template_loader = template.Loader(config["template_dir"])
        self.logger.info("Indeed handler created logger")

        try:
            self.indeed_crawler = core.crawlers.indeed_crawler.IndeedCrawler()
            self.logger.info("Indeed handler created crawler")
        except:
            import traceback
            self.logger.error(traceback.format_exc())

    def get(self, slug):
        try:
            page_template = self.template_loader.load('indeed.html')
            self.write(page_template.generate(slug=slug))
        except Exception as e:
            import traceback
            self.logger.warning(traceback.format_exc())
            raise e

    def post(self, slug):
        try:
            data = self.indeed_crawler.get_data(slug)
            response = self.to_csv(data)
            self.set_header("Content-Type", "text/csv")
            self.set_header("Content-Disposition", "attachment")
            self.write(response)

        except:
            self.write("Smth happens\n<br>\n")
            import traceback
            self.write(traceback.format_exc())

    @staticmethod
    def to_csv(result):

        #make header
        response = ['date,value']
        #make body

        response += ['{},{}'.format(str(l[0].strftime("%Y-%m-%d")), str(l[1])) for l in result]

        return '\n'.join(response)