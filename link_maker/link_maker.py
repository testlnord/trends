""" """

import pprint
import json
import sys

sys.path.append("/home/user/Dropbox/google-api-python-client")
sys.path.append("/home/user/Dropbox/oauth2client")
from googleapiclient.discovery import build


def google_wiki(query):
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAU1Gd-n7w9wzcF082rZYIJm65-o_s2tV0")
    res = service.cse().list(
        q=query,
        cx='004999571245303029695:vg9td7rxfom',  # wiki
        start=1
    ).execute()
    return res


def google_so(query):
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAU1Gd-n7w9wzcF082rZYIJm65-o_s2tV0")
    res = service.cse().list(
        q=query,
        cx='004999571245303029695:4-4ruya5u_y',  # stackoverflow tags
        start=1
    ).execute()
    return res


def google_itj(query):
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAU1Gd-n7w9wzcF082rZYIJm65-o_s2tV0")
    res = service.cse().list(
        q=query,
        cx='004999571245303029695:95bfezmqesy',  # everywhere
        siteSearch='itjobswatch.co.uk',
        start=1
    ).execute()
    return res


def main():
    pass


if __name__ == '__main__':
    main()