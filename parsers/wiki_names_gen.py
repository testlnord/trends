""" Take links to wikipedia from tab separated string of technology tags
"""

lst = open("wiki_names_raw.txt").readlines()
lst = [tuple(v for v in x.split('\t')) for x in lst]
lst = {x[0]: x[3] for x in lst if x[0]}

import pickle
pickle.dump(lst, open('wiki_names.pkl', 'wb'))