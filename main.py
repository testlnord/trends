#!/usr/bin/env python3
from tornadoweb.config import config
import logging
import sys
import tornado.ioloop
import tornado.web
from tornadoweb.handlers import MainHandler, AjaxHandler, TechsHandler, CsvHandler
from tornadoweb.info_handlers import TechInfoHandler, TechSearchHandler
from tornadoweb.tech_add_handlers import AddFormHandler, AddFormAjaxHandler
from tornadoweb.feedback_handlers import ReceiveFeedbackHandler, ShowFeedbacksHandler
from tornadoweb.daemon3x import daemon


class TrendsWebServer(daemon):
    def run(self):
        logger = logging.getLogger(__name__)
        logger.info("Logging initialized. Creating application...")
        application = tornado.web.Application([
            (r'/images/(.*)', tornado.web.StaticFileHandler, {'path': config['staticfiles_dir']}),
            (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': config['staticfiles_css_dir']}),
            (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': config['staticfiles_js_dir']}),
            (r"/", MainHandler),
            (r"/tech", TechsHandler),
            (r"/json/([^/]+)", AjaxHandler),
            (r"/csv/([^/]+)", CsvHandler),
            (r"/feedback/send/([^/]+)", ReceiveFeedbackHandler),
            (r"/feedback5", ShowFeedbacksHandler),
            (r"/tech_info$", TechSearchHandler),
            (r"/tech_info([^/]+)", TechInfoHandler),
            (r"/tech_add/json/", AddFormAjaxHandler),
            (r"/tech_add", AddFormHandler)

        ])
        logger.info("Application created. Starting to listen port...")
        application.listen(config["port"])
        logger.info("Starting application...")
        # noinspection PyBroadException
        try:
            tornado.ioloop.IOLoop.instance().start()
        except:  # I don't know what can happen here
            logger.error("Application crashed.", exc_info=True)
            logger.info("Stopping daemon.")
            self.stop()

if __name__ == "__main__":
    my_daemon = TrendsWebServer('/tmp/trendsws.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            my_daemon.start()
        elif 'stop' == sys.argv[1]:
            my_daemon.stop()
        elif 'restart' == sys.argv[1]:
            my_daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
