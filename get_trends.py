""" Get trend info by parsers
"""

import pickle


__author__ = 'user'


#import parsers.itjobs
#import parsers.google
#import parsers.sotrends
import core.parsers.wiki

def main():
    hot = pickle.load(open('top_names.pkl', 'rb'))
    #hot = ['c++', 'c', 'c#']
    #gp = parsers.google.GoogleParser()
    # ip = parsers.itjobs.ItjobsParser()
    sp = core.parsers.sotrends2.SOTParser()
    wp = core.parsers.wiki.WikiParser()
    for i, name in enumerate(hot):
        if i > 50:
            break
        try:
            wp.parse(name)
        except KeyError as e:
            print(e)
        # except Exception as e:
        #     print(e)
        #     pass
        # try:
        #     gp.parse(name)
        # except Exception as e:
        #     print(e)
        #     pass
        # try:
        #     sp.parse(name)
        # except:
        #     pass
        # try:
        #     ip.parse(name)
        # except:
        #     pass
        print(i, end=":  ")
        print(name)
        #time.sleep(random.randint(10, 200))


if __name__ == '__main__':
    main()
