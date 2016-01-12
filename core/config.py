""" Loads configuration from config.json file

config.json contains comments. It's out of standard and cannot be parsed
by json lib directly. So I piped it though jsmin as 'Douglas Crockford' has advised.
https://plus.google.com/+DouglasCrockfordEsq/posts/RK8qyGVaGSr
"""
import json
import logging, logging.config, logging.handlers
import os
from jsmin import jsmin
from os import path
import aadict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

local_config_path = path.join(project_root, 'local.config.json')
config_path = path.join(project_root, 'config.json')

config = json.loads(jsmin(open(config_path).read()))
if path.exists(local_config_path):
    config.update(json.loads(jsmin(open(local_config_path).read())))

config = aadict.aadict.d2ar(config)

class BufferingSMTPHandler(logging.handlers.BufferingHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, subject, capacity, mailport=None, mailpassword=None):
        logging.handlers.BufferingHandler.__init__(self, capacity)
        self.mailhost = mailhost
        self.mailport = mailport
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        if not isinstance(toaddrs, str):
            ','.join(self.toaddrs)
        self.mailpassword = mailpassword
        self.subject = subject
        self.setFormatter(logging.Formatter("%(asctime)s %(levelname)-5s %(message)s"))

    def flush(self):
        if len(self.buffer) > 0:
            try:
                import smtplib
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP_SSL(self.mailhost, port)
                if self.mailpassword:
                    smtp.login(self.fromaddr, self.mailpassword)
                msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (self.fromaddr, self.toaddrs, self.subject)
                for record in self.buffer:
                    s = self.format(record)
                    msg = msg + s + "\r\n"
                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
                smtp.quit()
            except:
                import traceback
                print(traceback.format_exc())
                self.handleError(None)  # no particular record
            self.buffer = []

def init_logging():
    logging.config.dictConfig(config['logging'])


# todo make settings checking