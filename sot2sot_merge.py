""" merges data from sot and sot2 parsers """
import os
import pickle
import matplotlib.pyplot as plt
__author__ = 'user'


def main():
    sot_names = []
    sot_dir = "data/sot"
    for name in os.listdir(sot_dir):
        if os.path.exists(os.path.join(sot_dir, name, "raw_data")):
            sot_names.append(name)

    print(sot_names)

    sot2_names = []
    sot2_dir = "data/sot2"
    for name in os.listdir(sot2_dir):
        if os.path.exists(os.path.join(sot2_dir, name, "raw_data")):
            sot2_names.append(name)

    print(sot2_names)

    uniq_names = [n for n in sot_names if n not in sot2_names]
    uniq_names2 = [n for n in sot2_names if n not in sot_names]
    print(uniq_names)
    print(uniq_names2)

    uniq_names.extend(uniq_names2)

    names = filter(lambda n: n in sot_names,sot2_names)
    # plotting data to see mistakes
    for name in names:
        d1 = pickle.load(open(os.path.join(sot_dir, name, "raw_data"), 'rb'))
        d2 = pickle.load(open(os.path.join(sot2_dir, name, "raw_data"), 'rb'))
        d1 = list(zip(*d1))
        d2 = list(zip(*d2))
        plt.plot(d1[0], d1[1])
        plt.plot(d2[0], d2[1])
        plt.xlabel(name)
        plt.show(block=True)


def merge_old_and_new():
    pref1 = "data/sot2/"
    pref2 = "data/sot_old"
    pref_out = "data/sot_my"
    from parsers.sotrends2 import SOTParser
    SOTParser.init_dir = pref_out
    sp = SOTParser()

    for name in os.listdir(pref1):
        d1 = os.path.join(pref1, name, "response")
        d2 = os.path.join(pref2, name, "response")
        if os.path.exists(d1) and os.path.exists(d2):
            d1 = pickle.load(open(d1, 'rb'))
            d2 = pickle.load(open(d2, 'rb'))
            try:
                os.mkdir(os.path.join(pref_out, name))
            except FileExistsError:
                pass  # just ignore
            total_data = d2 + d1
            pickle.dump(total_data, open(os.path.join(pref_out, name, "response"), 'wb'))
            print(name)
            sp.parse(name)


if __name__ == "__main__":
    main()