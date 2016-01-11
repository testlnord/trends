from core.crawlers.wiki_crawler import WikiCrawler
import csv
import datetime
pages = ["IntelliJ", "JetBrains"]

with open("misc/jb_wiki_2.csv", 'w') as res_file:
    result = csv.DictWriter(res_file, ['time', 'value'])

    min_date = datetime.date(2015,1,1)
    by_page_data = []
    for page in pages:
        res = WikiCrawler.get_data(page, min_date)
        for line in res:
            result.writerow({'time':line[0], 'value':line[1]})


