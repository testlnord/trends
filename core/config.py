""" Loads configuration from config.json file

config.json contains comments. It's out of standard and cannot be parsed
by json lib directly. So I piped it though jsmin as 'Douglas Crockford' has advised.
https://plus.google.com/+DouglasCrockfordEsq/posts/RK8qyGVaGSr
"""
import json
from jsmin import jsmin
from os import path
config_path = path.join(path.dirname(path.abspath(__file__)), '..', 'config.json')
config = json.loads(jsmin(open(config_path).read()))

#todo try aadict