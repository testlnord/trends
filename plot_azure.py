from parsers import sotrends, google, wiki_edits

__author__ = 'arkady'

import matplotlib.pyplot
import pickle
import numpy
import draw

if __name__ == "__main__":
    wiki_az = pickle.load(open("itjobs/azure sql database/data", 'rb'))
    wiki_az = draw.date_to_float(wiki_az)
    google_az = pickle.load(open("google/azure/data", 'rb'))
    google_az = draw.date_to_float(google_az)
    sot_az = pickle.load(open("sot/azure/data", 'rb'))
    sot_az = draw.date_to_float(sot_az)


    matplotlib.pyplot.figure(figsize=(13.24, 7.72))

    matplotlib.pyplot.plot([x for x, _ in wiki_az], [y for _, y in wiki_az], 'bo', label="wiki")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in wiki_az], [y for _, y in wiki_az], 5))
    matplotlib.pyplot.plot([x for x, _ in wiki_az], fit([x for x, _ in wiki_az]), 'b')

    matplotlib.pyplot.plot([x for x, _ in google_az], [y for _, y in google_az], 'r^', label="google")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in google_az], [y for _, y in google_az], 5))
    matplotlib.pyplot.plot([x for x, _ in google_az], fit([x for x, _ in google_az]), 'r')

    matplotlib.pyplot.plot([x for x, _ in sot_az], [y for _, y in sot_az], 'gv', label="SOt")
    fit = numpy.poly1d(numpy.polyfit([x for x, _ in sot_az], [y for _, y in sot_az], 5))
    matplotlib.pyplot.plot([x for x, _ in sot_az], fit([x for x, _ in sot_az]), 'g')

    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.savefig("{0}.png".format("azure"), dpi=100)
    print("plot {0} is ready".format("azure"))
    matplotlib.pyplot.close()
