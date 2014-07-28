__author__ = 'arkady'

""" normalize data and draw graphs """

import datetime
import time
import matplotlib.pyplot


def normalize(data):
    data = [ (x,y) for x, y in sorted(data, key=(lambda v: v[0]))]
    min_val = min(data, key=(lambda v: v[1]))[1]
    max_val = max(data, key=(lambda v: v[1]))[1]
    return [ (x, float(y - min_val)/(max_val - min_val)) for x, y in data]


def date_to_float(data):
    return [ (float(time.mktime(x.timetuple())), y) for x, y in data]


def plot(data, name):
    plot_impl(date_to_float(normalize(data)), name)

def plot_impl(data, name):
    matplotlib.pyplot.plot([x for x, _ in data], [y for _, y in data], 'b', label=name)
    matplotlib.pyplot.grid(True)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.savefig("{0}.png".format(name))
    print("plot {0} is ready".format(name))
    matplotlib.pyplot.close()