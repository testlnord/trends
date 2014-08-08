""" """
class LinkMaker:
    pass

import os
import pickle
from html.parser import HTMLParser
import re
import sys
from urllib.parse import unquote, quote
import urllib.request as ur

sys.path.append("/home/user/Dropbox/google-api-python-client")
sys.path.append("/home/user/Dropbox/oauth2client")
from googleapiclient.discovery import build
from core.sotapi import get_tag_synonyms



def google_wiki(query, page=0, related=None):
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAU1Gd-n7w9wzcF082rZYIJm65-o_s2tV0")
    res = service.cse().list(
        q=query,
        cx='004999571245303029695:vg9td7rxfom',  # wiki + keywords
        start=page * 10 + 1,
        relatedSite=related
    ).execute()
    return res


def google_so(query, page=0):
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAU1Gd-n7w9wzcF082rZYIJm65-o_s2tV0")
    res = service.cse().list(
        q=query,
        cx='004999571245303029695:4-4ruya5u_y',  # stackoverflow tags
        start=page * 10 + 1
    ).execute()
    return res


def google_itj(query, page=0):
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAU1Gd-n7w9wzcF082rZYIJm65-o_s2tV0")
    res = service.cse().list(
        q=query,
        cx='004999571245303029695:8dgxffq9eui',  # itjobswatch.co.uk/jobs/uk
        # cx='004999571245303029695:95bfezmqesy',  # everywhere
        # siteSearch='itjobswatch.co.uk',
        start=page * 10 + 1
    ).execute()
    return res




def get_itj_image_name(itj_link):
    class ItjPageParser(HTMLParser):
        read_image = False
        img_src = None

        def handle_starttag(self, tag, attrs):
            if tag == 'a' and ('id', 'demand_trend') in attrs:
                self.read_image = True
                return
            if self.read_image and tag == 'img':
                self.img_src = dict(attrs)['src']
                self.read_image = False

    resp = ur.urlopen(itj_link)
    page = resp.read().decode()
    ipp = ItjPageParser()
    ipp.feed(page)
    link = ipp.img_src
    name_search = re.search('aspx\?s=(.*)&', link)
    if not name_search:
        print(link)
        raise KeyError('bad link')
    return name_search.group(1)


def get_page_title(link):
    class PageTitleParser(HTMLParser):
        read_title = False
        title = None

        def handle_starttag(self, tag, attrs):
            if tag == 'title':
                self.read_title = True
                return

        def handle_data(self, data):
            if self.read_title:
                self.title = data
                self.read_title = False

    resp = ur.urlopen(link)
    page = resp.read().decode()
    ptp = PageTitleParser()
    ptp.feed(page)
    return ptp.title


def main(query):
    # getting ITJ image name
    print("===============itjobs=======================")

    itj_tag_link_pattern = re.compile('http://www.itjobswatch.co.uk/jobs/uk/(.*).do')
    itj_magic_word_pattern = re.compile('(.*) Jobs, Average Salary for (.*)')

    if os.path.exists(query + '_i.pkl'):
        itj_res = pickle.load(open(query + '_i.pkl', 'rb'))
    else:
        itj_res = search_itj(query)
        if not itj_res['items']:
            itj_res = google_itj(query)

        if 'items' not in itj_res:
            print(itj_res)
            raise KeyError("Nothing found in itjobs")
        pickle.dump(itj_res, open(query + '_i.pkl', 'wb'))
    itj_link = None
    itj_name = None
    itj_m_word = None
    for item in itj_res['items']:
        print(item['title'], item['link'])
    for item in itj_res['items']:
        search = itj_tag_link_pattern.search(item['link'])
        if search:
            itj_link = item['link']
            print(itj_link)
            try:
                page_title = get_page_title(item['link'])
                print(page_title)
                itj_m_word = itj_magic_word_pattern.search(page_title).group(2)
                if itj_m_word.endswith('Skills'):
                    itj_m_word = itj_m_word[:-7]
            except AttributeError:
                print(item)
                raise
            itj_name = get_itj_image_name(itj_link)
            break
        else:
            print(":(", item['title'], item['link'])

    print(itj_name)

    # getting SO tag
    print('==============stov=================')
    so_tag_link_pattern = re.compile('http://stackoverflow.com/tags/(.*)/info')

    if os.path.exists(query + '_s.pkl'):
        sot_res = pickle.load(open(query + '_s.pkl', 'rb'))
    else:
        sot_res = google_so(query)
        if 'items' not in sot_res:
            print(sot_res)
            raise KeyError("Nothing found in stackoverflow")
        pickle.dump(sot_res, open(query + '_s.pkl', 'wb'))
    sot_link = None
    sot_tag = None
    for item in sot_res['items']:
        search = so_tag_link_pattern.search(item['link'])
        if search:
            sot_tag = unquote(search.group(1))
            sot_link = item['link']
            break
    synonyms = [sot_tag]
    for item in get_tag_synonyms(sot_tag)['items']:
        synonyms.append(item['from_tag'])

    print(sot_tag)
    print(synonyms)

    # get wiki name
    print('===============wiki==============')
    wiki_name_pattern = re.compile('en\.wikipedia\.org/wiki/(.*)')
    # query_list = list(set([x.lower() for x in [query, sot_tag, itj_name, itj_m_word]]))
    # if len(query_list) < 2:
    # query_list =
    # w_query = ' '.join([x.replace('-', ' ') for x in synonyms])
    # w_query = ' '.join(query_list)
    # print(w_query)
    if os.path.exists(query + '_w.pkl'):
        wiki_res = pickle.load(open(query + '_w.pkl', 'rb'))
    else:
        wiki_res = google_wiki(query)
        if 'items' not in wiki_res:
            print(wiki_res)
            raise KeyError("Nothing found in wikipedia")
        pickle.dump(wiki_res, open(query + '_w.pkl', 'wb'))
    wiki_link = None
    wiki_name = None
    for item in wiki_res['items']:
        search = wiki_name_pattern.search(item['link'])
        if search:
            print(item['title'], item['link'])
            wiki_link = item['link']
            wiki_name = search.group(1)
            break
    for item in wiki_res['items']:
        print(item['link'])
    print(wiki_name)


if __name__ == '__main__':
    main('cassandra')