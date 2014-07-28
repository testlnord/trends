import scipy
from parsers import sotrends, google, wiki_edits

__author__ = 'arkady'

import matplotlib.pyplot as plt
import pickle
#import numpy as np
import draw
#import rpy2.robjects as r
import unittest
#from scipy import signal
#import pandas as pd


import parsers.sotrends2 as sot2

def make_plot():
    wiki_sl = pickle.load(open("data/itjobs/html/raw_data", 'rb'))
    wiki_slf = draw.date_to_float(wiki_sl)
    google_sl = pickle.load(open("data/google/html/data", 'rb'))
    google_slf = draw.date_to_float(google_sl)
    sot_sl = pickle.load(open("data/sot/.net/raw_data", 'rb'))
    #sot_r_sl = pickle.load(open("data/sot/.net/response", 'rb'))
    sot2_sl = pickle.load(open("data/sot2/.net/raw_data", 'rb'))
    #sot2_tot = pickle.load(open("parsers/total.pkl", 'rb'))
    sot2_slf =  draw.date_to_float(sot2_sl)
    sot_slf = draw.date_to_float(sot_sl)




    plt.figure(figsize=(14, 6))

    plt.plot([x for x, _ in sot_sl], [y for _, y in sot_sl], 'b', label=".net old")
    plt.plot([x for x, _ in sot2_sl], [y for _, y in sot2_sl], 'r', label=".net new")
    # fit = numpy.poly1d(numpy.polyfit([x for x, _ in wiki_slf], [y for _, y in wiki_slf], 5))
    # plt.plot([x for x, _ in wiki_sl], fit([x for x, _ in wiki_slf]), 'b')
    #
    # plt.plot([x for x, _ in google_sl], [y for _, y in google_sl], 'r^', label="google")
    # fit = numpy.poly1d(numpy.polyfit([x for x, _ in google_slf], [y for _, y in google_slf], 5))
    # plt.plot([x for x, _ in google_sl], fit([x for x, _ in google_slf]), 'r')
    #
    # plt.plot([x for x, _ in sot_sl], [y for _, y in sot_sl], 'gv', label="SOt")
    # fit = numpy.poly1d(numpy.polyfit([x for x, _ in sot_slf], [y for _, y in sot_slf], 5))
    # plt.plot([x for x, _ in sot_sl], fit([x for x, _ in sot_slf]), 'g')

    plt.grid(True)
    plt.legend()
    plt.savefig("{0}.png".format("net"), dpi=100)
    print("plot {0} is ready".format("sl"))
    plt.close()


if __name__ == "__main__":
    # stl = r.r.stl
    # data = pickle.load(open("itjobs/html/raw_data", 'rb'))
    # x = [v for d, v in data]
    # fs = 1000
    # print(data)
    #
    # print(stl(data))
    import parsers.sotrends2 as sp2
    sp = sp2.SOTParser()
    sp.parse('t')

    pass