""" Show trend plots

scan parsed data and show plots
"""

import pickle
import datetime
import calendar
import matplotlib.pyplot as plt
import pandas as pnd
import numpy as np
import rpy2.robjects as robj
__author__ = 'user'

spline = robj.r["smooth.spline"]

def main():
    names = pickle.load(open('../top_names.pkl', 'rb'))
    prsrs = ['google', 'itjobs', 'sot', 'wiki']
    colors = {'google': 'r', 'itjobs': 'g', 'sot': 'b', 'wiki': 'y'}
    plot_num = 0
    for name in names:
        datas = []
        srcs = []
        for prsr in prsrs:
            try:
                datas.append(pickle.load(open('../data/'+prsr+'/'+name+'/data', 'rb')))
                srcs.append(prsr)
            except FileNotFoundError:
                pass

        if datas:
            print(name)
            plt.figure(figsize=(14, 6))

            for idx, data in enumerate(datas):
                x, y = zip(*data)
                plt.plot(x, y, colors[srcs[idx]]+',')

                sp = spline([calendar.timegm(xv.timetuple()) for xv in x], list(y))
                plt.plot([datetime.datetime.fromtimestamp(x).date() for x in sp.rx(1)[0]], sp.rx(2)[0],
                         colors[srcs[idx]], lw=3, label=srcs[idx])

            plt.grid(True)
            plt.legend()
            plt.savefig("img_{0}.png".format(name), dpi=100)
            plt.close()
            plot_num += 1


if __name__ == '__main__':
    main()