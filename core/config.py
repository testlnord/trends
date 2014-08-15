""" Loads configuration from config.json file

config.json contains comments. It's out of standard and cannot be parsed
by json lib directly. So I piped it though jsmin as 'Douglas Crockford' has advised.
https://plus.google.com/+DouglasCrockfordEsq/posts/RK8qyGVaGSr
"""
import json
import logging.config
import os
from jsmin import jsmin
from os import path
import aadict

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config_path = path.join(project_root, 'config.json')
config = json.loads(jsmin(open(config_path).read()))

logging.config.dictConfig(config['logging'])

config = aadict.aadict.d2ar(config)

#todo make settings checking