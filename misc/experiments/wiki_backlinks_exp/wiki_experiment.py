""" Wiki assotiations experiment

I try to get data about all pages which redirects to "azure" page
"""
import pickle

import matplotlib.pyplot as plt

from experiments.wiki_backlinks_exp.wiki import WikiParser


ass = ["Windows Strata", "Windows Cloud", "Windows azure_", "Windows Azure Fabric Controller",
       "Microsoft Windows Azure", "Azure Services Platform", "Windows Azure", "Microsoft azure", "Microsoft_Azure"]


def main():
    wp = WikiParser()
    print("Getting data")
    for a in ass:
        print(' ', a)
        wp.parse(a)

    print('Plotting data')
    for a in ass:
        print(' ', a)
        data = pickle.load(open("data/wiki/{0}/raw_data".format(a), 'rb'))
        data = list(zip(*data))
        plt.plot(data[0], data[1], marker='.', ms=2, linestyle='None', label=a)
        plt.plot()
    plt.legend()
    plt.savefig("wiki_exp.png", dpi=100)
    plt.close()

if __name__ == "__main__":
    main()
