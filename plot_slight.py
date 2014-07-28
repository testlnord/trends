from parsers import sotrends, google, wiki_edits

__author__ = 'arkady'

import matplotlib.pyplot
import pickle
import numpy
import draw

if __name__ == "__main__":
    wiki_sl = pickle.load(open("wiki/Microsoft_Silverlight/data", 'rb'))
    wiki_sl = draw.date_to_float(wiki_sl)
    google_sl = pickle.load(open("google/silverlight/data", 'rb'))
    google_sl = draw.date_to_float(google_sl)
    sot_sl = pickle.load(open("sot/silverlight/data", 'rb'))
    sot_sl = draw.date_to_float(sot_sl)


    matplotlib.pyplot.figure(figsize=(13.24, 7.72))

    matplotlib.pyplot.plot([x for x, _ in wiki_sl], [y for _, y in wiki_sl], 'bo', label="wiki")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in wiki_sl], [y for _, y in wiki_sl], 5))
    matplotlib.pyplot.plot([x for x, _ in wiki_sl], fit([x for x, _ in wiki_sl]), 'b')

    matplotlib.pyplot.plot([x for x, _ in google_sl], [y for _, y in google_sl], 'r^', label="google")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in google_sl], [y for _, y in google_sl], 5))
    matplotlib.pyplot.plot([x for x, _ in google_sl], fit([x for x, _ in google_sl]), 'r')

    matplotlib.pyplot.plot([x for x, _ in sot_sl], [y for _, y in sot_sl], 'gv', label="SOt")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in sot_sl], [y for _, y in sot_sl], 5))
    matplotlib.pyplot.plot([x for x, _ in sot_sl], fit([x for x, _ in sot_sl]), 'g')

    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.savefig("{0}.png".format("silverlight"), dpi=100)
    print("plot {0} is ready".format("sl"))
    matplotlib.pyplot.close()
