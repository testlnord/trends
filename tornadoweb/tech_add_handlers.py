import json
import traceback
from psycopg2.extras import Json
import tornado
from tornado import template
import psycopg2
import tornado.web
from tornadoweb.config import config
import core.link_makers.wikilm as wikilm
import core.utils.internet.internet
from tornado.escape import json_decode
from tornado.escape import json_encode

from core.updaters.google import GoogleUpdater
from core.updaters.wiki import WikiUpdater
from core.updaters.itj import ItjUpdater
from core.updaters.sot import SotUpdater
from core.updaters.gitstars import GitStarsUpdater

import logging


class AddFormHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'],
                                              user=config['db_user'],
                                              password=config['db_pass'])
        self.logger = logging.getLogger(__name__)

    def get(self):
        page_template = self.template_loader.load('tech_add.html')
        self.write(page_template.generate())

    def post(self):
        try:
            self.write("<html><body><div>")
            tech_name = self.get_argument("tech_name", "")
            wiki_pages = self.get_argument("wiki_all", "")
            google_name = self.get_argument("google_name", "")
            sot_tag = self.get_argument("sot_tag", "")
            itj_page = self.get_argument("itj_name", "")
            github_repo = self.get_argument("github_repo", '')

            self.write("tn: " + tech_name + "<br/>\n")
            self.write("wn: " + wiki_pages + "<br/>\n")
            self.write("gn: " + google_name + "<br/>\n")
            self.write("sn: " + sot_tag + "<br/>\n")
            self.write("in: " + itj_page + "<br/>\n")
            self.write("gs: " + github_repo + "<br/>\n")

            if not tech_name or (not wiki_pages and
                                     not google_name and
                                     not sot_tag and
                                     not itj_page and
                                     not github_repo):
                self.write("failed. Nothing to insert")
                return

            cur = self.db_connection.cursor()
            cur.execute("insert into techs(name, info) values(%s, '{}') returning id", (tech_name,))
            self.db_connection.commit()
            fb_id = cur.fetchone()[0]
            if wiki_pages:
                wiki_pages = wiki_pages.split(",")
                WikiUpdater().add_or_update_new_tech(fb_id, wiki_pages)
                self.write("wiki added\n<br/>\n")
            if sot_tag:
                SotUpdater().add_or_update_new_tech(fb_id, [sot_tag])
                self.write("sot added\n<br/>\n")
            if google_name:
                GoogleUpdater().add_or_update_new_tech(fb_id, [google_name])
                self.write("google added\n<br/>\n")
            if itj_page:
                ItjUpdater().add_or_update_new_tech(fb_id, [itj_page])
                self.write("Itj added \n<br/>\n")
            if github_repo:
                GitStarsUpdater().add_or_update_new_tech(fb_id, [github_repo])
                self.write("Gitstars added\n<br/>\n")

            self.write("Inserted successfully\n<br/>\n")
            self.write('<a href="/tech_add">Add one more tech</a>')
            self.write("</div></body></html>")
        except Exception:
            self.logger.error("An error occurred.\n%s", traceback.format_exc())
            raise

class AddFormAjaxHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # self.db_connection = psycopg2.connect(database=config['db_name'], user=config['db_user'],
        #                                       password=config['db_pass'])

    def get(self):
        self.write_error(401)

    def post(self):
        try:
            request = json_decode(self.request.body)
            req_type = ""
            if "type" in request.keys():
                req_type = request["type"]

            if not req_type:
                self.write_error(406)
                return

            if req_type == "wiki":
                wiki_link = ""
                if "link" in request.keys():
                    wiki_link = request["link"]

                if not core.utils.internet.internet.is_valid_url(wiki_link) or \
                        not wiki_link.startswith("https://en.wikipedia.org/wiki/"):
                    self.write_error(400)
                    return

                all_links = wikilm.WikiLinkMaker.make_links_from_link(wiki_link)
                self.set_header("Content-Type", "application/json")
                self.write(json_encode(all_links))

            else:
                self.set_header("Content-Type", "application/json")
                self.write(json_encode("Oops!"))
        except Exception as e:
            self.set_header("Content-Type", "application/json")
            self.write("Error: " + json_encode(str(e)))
