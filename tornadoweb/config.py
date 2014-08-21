"""Web server configuration """

import os
import jsmin
import json

current_path = os.path.dirname(__file__)
config_path = os.path.join(current_path, "config.json")

config = json.loads(jsmin.jsmin(open(config_path).read()))