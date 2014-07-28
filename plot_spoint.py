from parsers import sotrends, google, wiki_edits

__author__ = 'arkady'

import matplotlib.pyplot
import pickle
import numpy
import draw

if __name__ == "__main__":
    wiki_sp = pickle.load(open("wiki/Microsoft_SharePoint/data", 'rb'))
    wiki_sp = draw.date_to_float(wiki_sp)
    google_sp = pickle.load(open("google/sharepoint/data", 'rb'))
    google_sp = draw.date_to_float(google_sp)
    sot_sp = pickle.load(open("sot/sharepoint/data", 'rb'))
    sot_sp = draw.date_to_float(sot_sp)


    matplotlib.pyplot.figure(figsize=(13.24, 7.72))

    matplotlib.pyplot.plot([x for x, _ in wiki_sp], [y for _, y in wiki_sp], 'bo', label="wiki")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in wiki_sp], [y for _, y in wiki_sp], 5))
    matplotlib.pyplot.plot([x for x, _ in wiki_sp], fit([x for x, _ in wiki_sp]), 'b')

    matplotlib.pyplot.plot([x for x, _ in google_sp], [y for _, y in google_sp], 'r^', label="google")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in google_sp], [y for _, y in google_sp], 5))
    matplotlib.pyplot.plot([x for x, _ in google_sp], fit([x for x, _ in google_sp]), 'r')

    matplotlib.pyplot.plot([x for x, _ in sot_sp], [y for _, y in sot_sp], 'gv', label="SOt")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in sot_sp], [y for _, y in sot_sp], 5))
    matplotlib.pyplot.plot([x for x, _ in sot_sp], fit([x for x, _ in sot_sp]), 'g')

    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.savefig("{0}.png".format("sharepoint"), dpi=100)
    print("plot {0} is ready".format("sp"))
    matplotlib.pyplot.close()
