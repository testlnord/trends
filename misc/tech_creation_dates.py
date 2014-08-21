"""Attempt to get creation dates of technologies from wikipedia articles."""
import json
from bs4 import BeautifulSoup
import datetime
import psycopg2
import urllib.request as ureq
import csv

def get_date_from_all(strings):
    formats = ["%Y-%m-%d", "%Y-%m", "%Y", "%B %d, %Y", "%B %Y", "%B, %Y"]
    date = None
    for f in formats:
        for s in strings:
            try:
                date = datetime.datetime.strptime(s, f)
                break
            except:
                pass
        if date is not None:
            break
    return date

def main():
    conn = psycopg2.connect(database="new.db", user="user")
    tech_cur = conn.cursor()
    tech_cur.execute("select info::json->>'name', id from techs")
    wiki_conf = json.load(open("/home/user/Dropbox/trends/src_conf/wiki.json"))['techs']
    csv_writer = csv.writer(open("tech_dates.csv",'w'))
    for tech_name, tech_id in tech_cur:
        wiki_link = wiki_conf[str(tech_id)]['pages'][-1]
        url = "http://en.wikipedia.org/wiki/" + wiki_link.replace(" ", "_")
        resp = ureq.urlopen(url)
        page = resp.read().decode()

        soup = BeautifulSoup(page)

        try:
            date_string = list(soup.find(class_ = 'infobox').find_all('th', text=['Appeared in', 'Initial release', 'Introduced'])[0].find_next_sibling().strings)
        except (KeyError, IndexError, AttributeError):
            date_string = None
        if date_string is None:
            print("==============Not found:", tech_name, "link:", url)
        else:
            date_date = get_date_from_all(date_string)
            if date_date is None:
                print("***************Can't parse", tech_name, '\t', date_string, "link:", url)
            else:
                csv_writer.writerow([tech_id, tech_name, date_date])




if __name__ == "__main__":
    print(__file__)
    main()
