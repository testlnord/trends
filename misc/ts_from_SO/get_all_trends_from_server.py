import psycopg2
import requests

def main():
    conn = psycopg2.connect(database="trendsdb",
                            user="updater",
                            password="pass111"
                            )
    cur = conn.cursor()
    cur.execute("select id, name from techs")
    for row in cur:
        id, name = row
        get_remote_trend(id, name)
    pass

def get_only_remote():
    for row in get_remote_id_name(-1):
        id, name = row
        get_remote_trend(id, name)



def get_max_local_id():
    local_conn = psycopg2.connect(database="trendsdb",
                                         user="updater",
                                         password="pass111"
                                         )
    cur = local_conn.cursor()
    cur.execute("select max(id) from techs")
    max_local_id = cur.fetchone()[0]
    return max_local_id

def get_remote_id_name(max_id):
    remote_conn = psycopg2.connect(database="trendsdb",
                                  user="updater",
                                  password="upd210!!!",
                                  host='research-trends.labs.intellij.net'
                                )
    cur = remote_conn.cursor()
    cur.execute("select id, name from techs where id > %s", (max_id,))
    return cur

def get_remote_trend(id, name):
    trend = requests.get("http://research-trends.labs.intellij.net/csv/raw,wiki,{}.csv".format(id))
    out_file = open("tmp/" + name.replace(" ", "_") + ".csv", 'w')
    out_file.write(trend.text)


if __name__ == "__main__":
    get_only_remote()