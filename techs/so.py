""" Get list of tags from StackOverflow
"""
import pickle
import time

__author__ = 'user'

import urllib.request as ur
import json
import gzip

def main():

    result_filename = 'sot_tags.pkl'
    result = pickle.load(open(result_filename, 'rb'))

    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/35.0.1916.153 Safari/537.36",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "en-US,en;q=0.8",
        }
    url = "http://api.stackexchange.com/2.2/tags?site=stackoverflow&pagesize=100"
    req = ur.Request(url+"&page=216", headers=headers)
    response = ur.urlopen(req)

    data = response.read()
    json_data = gzip.decompress(data).decode()
    raw = json.loads(json_data)
    result.extend(raw["items"])
    page_number = 217

    while raw["has_more"]:
        print(page_number)

        pickle.dump(result, open(result_filename, 'wb'))

        time.sleep(180)

        req = ur.Request(url+"&page="+str(page_number), headers=headers)
        response = ur.urlopen(req)
        data = response.read()
        json_data = gzip.decompress(data).decode()
        raw = json.loads(json_data)
        result.extend(raw["items"])

        page_number += 1

    pickle.dump(result, open(result_filename, 'wb'))


if __name__ == '__main__':
    main()