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

    #todo Actualy merge data


if __name__ == "__main__":
    main()