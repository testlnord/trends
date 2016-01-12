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


class EditFormHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_loader = template.Loader(config["template_dir"])
        self.db_connection = psycopg2.connect(database=config['db_name'],
                                              user=config['db_user'],
                                              password=config['db_pass'])
        self.logger = logging.getLogger(__name__)
        self.logger.info("Handler initialized")

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.write(traceback.format_exc())
        else:
            super().write_error(status_code, **kwargs)

    @staticmethod
    def stringify(*params):
        return " ".join(str(p) for p in params)

    def get(self, tech_id=None):
        try:
            tech_id, tech_name = self._check_tech_id(tech_id)
            if tech_id is None or tech_name is None:
                return

            wiki_pages = WikiUpdater().get_words_for_tech(tech_id)
            sot_tag = SotUpdater().get_words_for_tech(tech_id)
            google_name = GoogleUpdater().get_words_for_tech(tech_id)
            github_repo = GitStarsUpdater().get_words_for_tech(tech_id)
            itj_page = ItjUpdater().get_words_for_tech(tech_id)

            page_template = self.template_loader.load('tech_edit.html')
            self.write(
                page_template.generate(tech_id=tech_id, tech_name=tech_name, wiki_all=wiki_pages, sot_tag=sot_tag,
                                       google_name=google_name, github_repo=github_repo, itj_name=itj_page))
        except:
            self.write(self.stringify(tech_id, tech_name, wiki_pages, sot_tag, google_name, github_repo, itj_page))
            self.write(traceback.format_exc())
            #raise

    def _check_tech_id(self, tech_id):
        if tech_id is None:
            self.write_error("Attempt to edit tech wo tech_id")
            self.send_error(400)
            return None, None

        try:
            tech_id = int(tech_id)
        except ValueError:
            self.write("dsal'k'ldfs'l'lk'lkd sa dfsal'kdf sgal'kdfga  lkdf  l'kdf a' rgw ;lk ra'lakj")
            return None, None
            # self.write_error("Bad tech_id: %s", tech_id)
            # self.send_error(404)

        tech_name = self._get_tech_name(tech_id)
        if tech_name is None:
            self.write(
                "oiadjg o4q3hj[t084hkjnteghjg'3rbjlkgjb4l3,4bg;4l34lq3 bhl4 brl34 bhjq34uig34i uhqlif uhgh ad uih;lkbar")
            # self.write_error("Can't find tech with tech_id: %s", tech_id)
            # self.send_error(404)

        return tech_id, tech_name

    def _get_tech_name(self, tech_id):
        cur = self.db_connection.cursor()
        cur.execute("select name from techs where id = %s", (tech_id,))
        query_results = cur.fetchall()
        if not query_results:
            return None
        else:
            return query_results[0][0]

    def post(self, tech_id_addr=None):
        try:
            tech_id_addr, tech_name = self._check_tech_id(tech_id_addr)
            if tech_id_addr is None or tech_name is None:
                return

            self.write("<html><body><div>")
            tech_id = self.get_argument("tech_id", "")
            if tech_id != str(tech_id_addr):
                self.logger.error("tech_ids in addr and request differs")
                self.send_error(409)
                return

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
            if tech_name:
                cur.execute("update techs set name = %s where id = %s", (tech_name, tech_id))
                self.db_connection.commit()
            
            if wiki_pages:
                wiki_pages = wiki_pages.split(",")
                WikiUpdater().add_new_tech(tech_id, wiki_pages)
                self.write("wiki updated\n<br/>")
            if sot_tag:
                SotUpdater().add_new_tech(tech_id, sot_tag)
                self.write("sot updatd\n<br/>")
            if google_name:
                GoogleUpdater().add_new_tech(tech_id, google_name)
                self.write("google updated\n<br/>")
            if itj_page:
                ItjUpdater().add_new_tech(tech_id, itj_page)
                self.write("Itj upd \n<br/>")
            if github_repo:
                GitStarsUpdater().add_new_tech(tech_id, github_repo)
                self.write("Gitstars upd\n<br/>")

            self.write("Inserted successfully")
            self.write('<a href="/tech#{}">View tech {}</a>'.format(tech_id, tech_name))
            self.write("</div></body></html>")
        except Exception:
            self.logger.error("An error occured.\n%s", traceback.format_exc())
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
