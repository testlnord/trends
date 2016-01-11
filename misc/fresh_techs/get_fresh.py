import requests
import psycopg2
from bs4 import BeautifulSoup
import csv

def main():
    conn = psycopg2.connect(database='trendsdb',
                            user='updater',
                            password='pass111')
    cur = conn.cursor()
    cur.execute("select tech_id, settings from source_settings where source = 'wiki'")
    dates = {}
    for i, row in enumerate(cur):
        tech_id, settings = row
        page = settings['pages'][0]
        wiki_url = 'https://en.wikipedia.org/wiki/' + page
        print(page)
        response = requests.get(wiki_url)
        soup = BeautifulSoup(response.text, "html.parser")
        info_table = soup.find_all('table', class_='infobox vevent')
        if info_table:
            info_table = info_table[0]
            for row in info_table.find_all('tr'):
                if 'Initial release' in str(row) or 'First appeared' in str(row):
                    print(row.td.text.split('<')[0])
                    dates[tech_id] = (row.td.text.split('<')[0], page)
                    break
            else:
                print("_-----------------------------------------------------------------------------------")
                print(info_table)
                print("========================================================================================================")


    with open("dates.csv", 'w') as dates_file:
        dates_csv = csv.DictWriter(dates_file, ['id', 'date', 'name'])
        dates_csv.writeheader()
        for tid in dates:
            dates_csv.writerow({'id':tid, 'date':dates[tid][0], 'name': dates[tid][1]})

if __name__ == "__main__":
    main()