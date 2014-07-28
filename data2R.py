"""converts all raw data to format readable by R`s zoo lib

string example:
23 Feb 2005|43.72

R reading command:
data <- read.zoo("demo1.txt", sep = "|", format="%d %b %Y")
"""

import os
import pickle

data_dirs = ['wiki', 'sot', 'google', 'itjobs']


def convert():
    for data_dir in data_dirs:
        data_dir = os.path.join('data', data_dir)
        for tech_dir in os.listdir(data_dir):
            data_file = os.path.join(data_dir, tech_dir, 'raw_data')
            if os.path.exists(data_file):
                data = pickle.load(open(data_file, 'rb'))
                data_d = {}
                for d, v in data:
                    if d not in data_d.keys():
                        data_d[d] = []
                    data_d[d].append(v)

                with open(os.path.join(data_dir, tech_dir, 'r_data.txt'), 'w') as r_out:
                    for date in data_d:
                        r_out.write("{:%d %b %Y}|{:f}\n".format(date, max(data_d[date])))


if __name__ == '__main__':
    convert()