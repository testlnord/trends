import csv
import re


reg_matcher = re.compile("\(datetime\.datetime\((\d*), (\d*), (\d*), 0, 0\), (\d*)\)")
with open("total.txt", 'r') as inf:

    lines = inf.readline()
    with open("total.csv", 'w') as outf:
        out_csv = csv.DictWriter(outf, ['date','val'])
        out_csv.writeheader()
        for match in reg_matcher.findall(lines):
            out_csv.writerow({'date': match[0]+'-' + match[1] + '-'+match[2],
                              'val': match[3]})
