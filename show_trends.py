"""Show trend plots

scan parsed data and show plots
"""
import pickle
import matplotlib.pyplot as plt
import pandas as pnd
import numpy as np
__author__ = 'user'


def main():
    names = pickle.load(open('top_names.pkl', 'rb'))
    prsrs = ['google', 'itjobs', 'sot', 'wiki']

    colors = {'google':'r', 'itjobs':'g', 'sot':'b', 'wiki':'y'}
    plot_num = 0
    for name in names:
        datas = []
        srcs = []
        for prsr in prsrs:
            try:
                datas.append(pickle.load(open('data/'+prsr+'/'+name+'/data', 'rb')))
                srcs.append(prsr)
            except FileNotFoundError:
                pass

        # fig = plt.figure()
        # fig.text(.1,.1,name)
        if len(datas) > 1  and 'wiki' in srcs:
            splot = plt.subplot(5, 4, plot_num)
            splot.set_xticklabels([])
            splot.set_xticks([])
            splot.yaxis.set_visible(False)
            plot_num += 1
            for idx, data in enumerate(datas):
                x, y = zip(*data)
                plt.plot(x, y, colors[srcs[idx]]+',', label=srcs[idx])

                int_size = int(len(x)/7)
                rm = pnd.rolling_mean(pnd.Series(y), int_size)
                plt.plot(np.array(x) - (x[int(int_size/2)] - x[0]), rm, colors[srcs[idx]])

            plt.xlabel(name)
            #plt.legend()
        if plot_num == 20:
            break

    plt.show()



if __name__ == '__main__':
    main()