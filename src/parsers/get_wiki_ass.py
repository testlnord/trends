"""Gets associated pages (backlinks) to wiki page """
import json
import pickle
import random
import time

__author__ = 'user'
import urllib.request as ur
import urllib.error

def sleep(min_time, max_time):
    time.sleep(random.randint(min_time, max_time))


def get(name):
    """ Gets back links for page

    :param name: page title
    :return: list of back links titles
    """

    url = "http://en.wikipedia.org/w/api.php?action=query&" \
          "list=backlinks&" \
          "blfilterredir=redirects&" \
          "bltitle={0}&" \
          "bllimit=max&" \
          "format=json&" \
          "maxlag=5".format(name)

    sleep(1, 7)
    resp = ur.urlopen(url)
    data = resp.read().decode()
    data = json.loads(data)

    backlinks = []
    for bl in data["query"]["backlinks"]:
        backlinks.append(bl["title"])
    return backlinks


total_file_name = "total_names.pkl"


def main():
    wiki_names = pickle.load(open("wiki_names.pkl", 'rb'))

    total_names = {} #pickle.load(open(total_file_name, 'rb'))
    for name in wiki_names:
        wiki_name = wiki_names[name]
        wiki_name = wiki_name[wiki_name.rindex("/")+1:]
        print(name, ": ", wiki_name, end=' ')
        links = get(wiki_name)
        total_names[name] = links + [wiki_name]
        print(len(links), " link(s) added.")
        pickle.dump(total_names, open(total_file_name, 'wb'))

if __name__ == "__main__":
    main()