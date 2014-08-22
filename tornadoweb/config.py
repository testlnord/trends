"""Web server configuration """

import os
import jsmin
import json
import logging.config

current_path = os.path.dirname(__file__)
config_path = os.path.join(current_path, "config.json")

config = json.loads(jsmin.jsmin(open(config_path).read()))

config["current_dir"] = os.path.dirname(os.path.abspath(__file__))

if not "template_dir" in config:
    config["template_dir"] = os.path.join(config["current_dir"], "templates")

logging.config.dictConfig(config['logging'])