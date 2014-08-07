""" Loads configuration from config.json file

config.json contains comments. It's out of standard and cannot be parsed
by json lib directly. So I piped it though jsmin as 'Douglas Crockford' has advised.
https://plus.google.com/+DouglasCrockfordEsq/posts/RK8qyGVaGSr
"""
import json
from jsmin import jsmin
settings = json.loads(jsmin(open('config.json').read()))