import jaydebeapi
import datetime
import itertools
import csv

conn = jaydebeapi.connect('net.sourceforge.jtds.jdbc.Driver',
                          ['jdbc:jtds:sqlserver://jetstat.labs.intellij.net:1433;databaseName=StackOverflowStatistic',
                           'so_write',
                           'dmitrykalashnikov'],
                          ['/home/user/.PyCharm40/config/jdbc-drivers/jtds-1.2.5.jar'])

min_date = datetime.date(2008, 7, 31)
max_date = datetime.date(2015, 3, 1)


def read_tags(tags_file):
    tags = []
    for line in tags_file:
        line = line.strip()
        if line and line[1] != '#':
            line = line.lower()
            tags.append(line)
    return tags

tag = []
with open("tags_list.txt", 'r') as tags_file:
    tags = read_tags(tags_file)

with open("all.csv", "w") as result_file:
    result = csv.DictWriter(result_file, ["time"] + tags)
    result.writeheader()
    cur_date = min_date
    cur = conn.cursor()
    while cur_date < max_date:
        next_date = cur_date + datetime.timedelta(days=7)

        query = "select count(p.id), t.tagname " \
                "from posts as p INNER JOIN posttags as pt on p.id = pt.postid " \
                "INNER JOIN tags as t on pt.tagid = t.id " \
                "where t.tagname in ({tags}) " \
                "and p.creationdate < '{max_date}' " \
                "and p.creationdate <= '{min_date}' " \
                "GROUP BY t.tagname;".format(tags=", ".join("'" +t+"'" for t in tags),
                                             max_date=next_date.strftime("%Y-%m-%d"),
                                             min_date=cur_date.strftime("%Y-%m-%d"))

        print("quering data for ", cur_date.strftime("%Y-%m-%d"))
        cur.execute(query)
        query_result = {"time": cur_date.strftime("%Y-%m-%d")}
        for row in cur.fetchall():
            query_result[row[1]] = row[0]

        result.writerow(query_result)

        cur_date = next_date
print("FINISH")