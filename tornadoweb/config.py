"""Web server configuration """

import os
import jsmin
import json
import logging.config

current_path = os.path.dirname(__file__)
local_config_path = os.path.join(current_path, 'local.config.json')
config_path = os.path.join(current_path, 'config.json')

config = json.loads(jsmin.jsmin(open(config_path).read()))
if os.path.exists(local_config_path):
    config.update(json.loads(jsmin.jsmin(open(local_config_path).read())))

config["current_dir"] = os.path.dirname(os.path.abspath(__file__))

if not "template_dir" in config:
    config["template_dir"] = os.path.join(config["current_dir"], "templates")

if not "staticfiles_dir" in config:
    config["staticfiles_dir"] = os.path.join(config["current_dir"], "images")
logging.config.dictConfig(config['logging'])