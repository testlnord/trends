"""Little user-tag-country experiment

I need data about badges, users with badges, user's countries
"""
import gzip
import json
import pickle
from urllib.parse import quote
import urllib.request as ur
import urllib.error
import time
import random
import datetime

from experiments.tag_experim import geo_data


def sleep(min_time, max_time):
    time.sleep(random.randint(min_time, max_time))


def get_badges():
    badges_file = "badges.pkl"
    result = {} #pickle.load(open(badges_file, 'rb'))

    tags = pickle.load(open("top_names.pkl", 'rb'))

    for tag in tags:
        if tag in result.keys():
            print("Present:", tag)
            continue

        print(tag)
        sleep(5, 10)
        url = "http://api.stackexchange.com/2.2/badges/tags?" \
              "order=desc&" \
              "min={0}&" \
              "max={0}&" \
              "key={1}&" \
              "sort=name&" \
              "inname={0}&" \
              "site=stackoverflow".format(quote(tag.replace(' ', '-')), quote("gytnic74fozY)jD39pQSzg(("))
        print(url)
        while True:
            try:
                resp = ur.urlopen(url)
                break
            except urllib.error.URLError as e:
                if e.errno != 110:  # Connection - timeout. Ignore it and try again
                    raise
                else:
                    sleep(3, 7)
        data = gzip.decompress(resp.read())
        print(data)
        data = json.loads(data.decode())

        result[tag] = data["items"]
        pickle.dump(result, open(badges_file, 'wb'))


def badges_100_iterator(badges_info):
    res = []
    bad_info = [x['badge_id'] for val in badges_info.values() for x in val]
    idx = 0
    while True:
        part = bad_info[idx: idx+100]
        idx += 100
        if len(part) < 100:
            break
        yield part
    if part:
        yield part
    raise StopIteration()


def get_users_with_badges():
    badges = pickle.load(open("badges.pkl", 'rb'))
    from_date = int(datetime.datetime(2008, 7, 28).timestamp())
    to_date = int(datetime.datetime.now().timestamp())
    result = [] #pickle.load(open("user_badges.pkl", 'rb'))

    for ids in list(badges_100_iterator(badges)):
        print(ids[0], '...', ids[-1])
        ids_str = ';'.join(map(str, ids))
        page_number = 1
        while True:
            print(' ', page_number, end=' ')
            sleep(1, 3)
            url = "http://api.stackexchange.com/2.2/badges/" \
                  "{idss}/recipients?" \
                  "page={page_num}&pagesize=100&" \
                  "fromdate={fromdate}&" \
                  "todate={todate}&" \
                  "site=stackoverflow&"\
                  "key={key}&"  \
                  "filter=!6JvKMTZy8(80_".format(key="gytnic74fozY)jD39pQSzg((",
                                                 idss=ids_str,
                                                 page_num=page_number,
                                                 fromdate=from_date,
                                                 todate=to_date)
            print(url)
            while True:
                try:
                    resp = ur.urlopen(url)
                    break
                except urllib.error.URLError as e:
                    if e.errno != 110:  # Connection - timeout. Ignore it and try again
                        raise
                    else:
                        sleep(3, 7)
            data = gzip.decompress(resp.read())
            data = json.loads(data.decode())
            result.append(data["items"])

            pickle.dump(result, open("user_badges.pkl", 'wb'))

            page_number += 1


            if not data["has_more"]:
                break


def get_user_ids():
    data = pickle.load(open("user_badges.pkl", 'rb'))
    user_ids = set()
    for data_page in data:
        for data_line in data_page:
            user_ids.add(data_line['user']['user_id'])
    return user_ids


def get_user_data():
    result = {}#pickle.load(open("user_data.pkl", 'rb'))
    user_ids = list(sorted(get_user_ids()))
    for idx in range(0, len(user_ids), 100):
        sub_ids = user_ids[idx: idx + 100]
        sub_ids = [x for x in sub_ids if x not in result.keys()]
        if not sub_ids:
            continue
        sleep(1, 3)
        print(sub_ids[0], sub_ids[-1])
        url = "http://api.stackexchange.com/2.2/users/" \
              "{ids}?" \
              "pagesize=100&" \
              "order=desc&" \
              "sort=reputation&" \
              "site=stackoverflow&" \
              "key={key}".format(ids=";".join(str(x) for x in sub_ids),
                                 key="gytnic74fozY)jD39pQSzg((")
        print(url)
        while True:
            try:
                resp = ur.urlopen(url)
                break
            except urllib.error.URLError as e:
                if e.errno != 110:  # Connection - timeout. Ignore it and try again
                    raise
                else:
                    sleep(3, 7)
        data = gzip.decompress(resp.read())
        page_data = json.loads(data.decode())

        if page_data['has_more']:
            print("MOAR!!!!")

        for item in page_data["items"]:
            result[item["user_id"]] = item

        pickle.dump(result, open('user_data.pkl', 'wb'))


def user_country():
    user_data = pickle.load(open("tag_experim/user_data.pkl", 'rb'))
    locs = {}
    noloc = 0
    bloc = 0
    for user_id in user_data:
        try:
            loc = user_data[user_id]['location']
            ctr = loc.split(', ')[-1]
        except KeyError:
            noloc += 1
            ctr = ''
            pass

        if ctr in geo_data.us_abbrs or ctr in geo_data.us_full:
            locs[user_id] = 'United States'
        elif ctr.lower() in geo_data.countries_dict:
            locs[user_id] = geo_data.countries_dict[ctr.lower()]
        else:
            locs[user_id] = ''
            if ctr:
                #print(ctr)
                bloc += 1
    print('Undef locations:', bloc, 'unspec locations:', noloc, 'of total:', len(user_data))
    return locs


def badges_users():
    badge_data = pickle.load(open("tag_experim/user_badges.pkl", 'rb'))
    badge_user = {}
    for page in badge_data:
        for rec in page:
            if rec['badge_id'] not in badge_user.keys():
                badge_user[rec['badge_id']] = []
            badge_user[rec['badge_id']].append(rec['user']['user_id'])
    return badge_user


def badges_ctr_cnt():
    user_ctr = user_country()
    bad_user = badges_users()
    bad_ctr_cnt = {}
    for badge in bad_user:
        bad_ctr_cnt[badge] = {}
        for user in bad_user[badge]:
            ctr = user_ctr[user]
            if ctr not in bad_ctr_cnt[badge].keys():
                bad_ctr_cnt[badge][ctr] = 0
            bad_ctr_cnt[badge][ctr] += 1

    return bad_ctr_cnt


points = {'gold': 1000, 'silver': 400, 'bronze': 100}


def tag_ctr():
    bad_ctr = badges_ctr_cnt()
    badges_file = "tag_experim/badges.pkl"
    badges_info = pickle.load(open(badges_file, 'rb'))
    tag_ctr_pts = {}
    for tag in badges_info:
        tag_ctr_pts[tag] = {}
        for badge in badges_info[tag]:
            bad_id = badge['badge_id']
            pts = points[badge['rank']]
            try:
                for ctr in bad_ctr[bad_id]:
                    if ctr not in tag_ctr_pts[tag]:
                        tag_ctr_pts[tag][ctr] = 0
                    tag_ctr_pts[tag][ctr] += bad_ctr[bad_id][ctr]
            except KeyError:
                print(bad_id)

    return tag_ctr_pts


def pprint(ctr_dict):
    # format:
    #          ['Greece', 1],
    keys = list(ctr_dict.keys())
    lines = []
    for k in keys[:-1]:
        lines.append('\t\t[\'' + k + '\', ' + str(ctr_dict[k]) + '],\n')
    lines.append('\t\t[\'' + keys[-1] + '\', ' + str(ctr_dict[keys[-1]])+ ']\n')
    return lines


def t(tag):
    return quote(tag).replace('%', '_').replace('.', 'dot')+'_'

if __name__ == "__main__":
    tcp = tag_ctr()

    with open("tag_experim/ctr_badges.html", 'w') as out_file:
        out_file.writelines(open('tag_experim/header.txt').readlines())
        for tag in tcp:
            out_file.write('\t' + t(tag) + ' = [' + '\n')
            out_file.writelines(pprint(tcp[tag]))
            out_file.write('\t];\n')
            out_file.write('\t' + t(tag) + 'data = f1(' + t(tag) + ');' + '\n')
            out_file.write('\n')
            out_file.write('\t' + t(tag) + 'data_cutted = f1(' + t(tag) + ');' + '\n')
            out_file.write('\n')
        out_file.writelines(open('tag_experim/body.txt').readlines())
        for tag in tcp:
            # <option value="java_data">Java</option>
            out_file.write('\t<option value="' + t(tag) + 'data">' + tag + "</option>" + '\n')
        out_file.writelines(open('tag_experim/footer.txt').readlines())