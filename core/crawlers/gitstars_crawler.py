"""Crawls data from stackoverflow"""
import datetime
import gzip
import json
import logging
import re
import requests
from requests.auth import HTTPBasicAuth
from core.config import config
from ..utils.internet import internet


__author__ = 'user'


class OutOfApiQuotaException(Exception):
    pass


class GitStarsCrawler:

    def __init__(self):
        self.api_token = config["github_token"]
        self.api_user = config["github_user"]
        self.api_pass = config["github_pass"]
        self.logger = logging.getLogger(__name__)

    def get_data(self, reponame) -> list:
        url = "https://api.github.com/repos/{}/stargazers?per_page=100&page={}&access_token={}"
        resp = requests.get('https://api.github.com/user', auth=HTTPBasicAuth(self.api_user, self.api_pass))
        if int(resp.status_code) == 200:
            self.logger.debug("Authentication succeed")
        else:
            self.logger.warning("Authentication failed. Rate limits will be very small.\n"
                                "Status: %s\nMessage: %s", resp.status_code, resp.text)

        headers = {'Accept':'application/vnd.github.v3.star+json'}
        starred_at_times = []
        page = 1
        max_page = None
        waited_on_prev_step = False
        while True:
            url_cooked = url.format(reponame, page, self.api_token)
            self.logger.debug("Generated url fo gitstars: " + url_cooked)
            resp = requests.get(url_cooked, headers=headers)
            self.logger.debug("Headers: {}".format(str(sorted(resp.headers))))
            if max_page is None and 'link' in resp.headers:
                link = resp.headers['link']
                link = link.split(',')
                for l in link:
                    if l.strip().endswith('rel="last"'):
                        m = re.search("&page=(\d*)", l)
                        if m:
                            max_page = int(m.group(1))
                            self.logger.debug("Max page number: %s", (max_page,))
            # checking rate limits
            if 'x-ratelimit-remaining' in resp:
                self.logger.debug("Github api limit rate: %s", resp['x-ratelimit-remaining'])
                if resp["x-ratelimit-remaining"] < 10:
                    if not waited_on_prev_step:
                        self.logger.warning("Low api limit, going to sleep.")
                        internet.sleep(60, 90)
                        waited_on_prev_step = True
                        continue
                    else:
                        raise OutOfApiQuotaException()
            waited_on_prev_step = False

            # getting data
            gazers = resp.json()
            for gazer in gazers:
                # time example: 2014-01-02T18:58:22Z
                starred_at_times.append(datetime.datetime.strptime(gazer["starred_at"],
                                                                   '%Y-%m-%dT%H:%M:%SZ'))
            if starred_at_times:
                self.logger.debug('Got starring times to %s',  str(starred_at_times[-1]))
            else:
                self.logger.info('No stars')

            # I can make 5000 requests per hour
            # so if i sleep 1-2 seconds, I will make 60*60 = 3600 requests
            # that should be ok.
            internet.sleep(1, 2)

            page += 1
            if max_page is None or max_page <= page:
                break


        return starred_at_times

if __name__ == "__main__":
    pass