""" Merge tag lists
"""
import pickle

__author__ = 'user'

if __name__ == '__main__':
    w_tags = pickle.load(open("wkp_tags.pkl", 'rb'))
    i_tags = pickle.load(open("itj_tags.pkl", 'rb'))

    w_tags = set([xw for _, x in w_tags for xw in x.split(' ')])

    names = [x for x in i_tags if x in w_tags]
    print( sorted(names))
    print(len(names))

    s_tags = pickle.load(open("sot_tags.pkl", 'rb'))
    s_tags = sorted(s_tags, key=lambda x: x['count'], reverse=True)

    a = list(set([x['name'] for x in s_tags[:150]]))
    a.sort()
    print(a)
    #pickle.dump(a, open('top50.pkl', 'wb'))
    print()
    print(len(s_tags))