"""attempt to renorm data"""
__author__ = 'user'


import pickle
import os
import numpy
import draw

if __name__ == '__main__':

    tags = pickle.load(open('imp_data_bckp/sot_tags216.pkl', 'rb'))
    datas = []
    for tag in tags:
        file = os.path.join('sot', tag['name'], 'raw_data')
        if os.path.exists(file):
            datas.append(tag)
            datas[-1]['data'] = pickle.load(open(file, 'rb'))
    #XAXAXAXA!!!
    #Sorting tags by popularity median, and take median
    parrot = [x for x in sorted(datas, key=lambda v: numpy.median(list(zip(*(v['data'])))[1]), reverse=True)][int(len(datas)/2)]

    parrot['n_data'] = draw.normalize(parrot['data'])
    print(parrot['n_data'])



