import psycopg2
import requests
from urllib.parse import urljoin
import time


def get_remote_id_name():
    remote_conn = psycopg2.connect(database="trendsdb",
                                  user="updater",
                                  password="upd210!!!",
                                  host='research-trends.labs.intellij.net'
                                )
    cur = remote_conn.cursor()
    cur.execute("select id, name from techs")
    return cur

def main():
    # connect to github
    from requests.auth import HTTPBasicAuth
    requests.get('https://api.github.com/user', auth=HTTPBasicAuth('testlnord', '123qazwsX'))
    with open("repos.csv", 'w') as repo_file:
        repo_file.write("id, name, repo, link\n")
        for t_id, t_name in get_remote_id_name():
            resp = requests.get('https://api.github.com/search/repositories?q='+t_name.replace(' ', '+'))
            repo_name = ""
            repo_link = ""
            if resp.status_code == 200:
                repo_name = resp.json()['items'][0]['full_name']
                repo_link = urljoin("https://github.com/", repo_name)
            else:
                print(resp.status_code)
                for h in resp.headers:
                    print(h, " : ", resp.headers[h])
            repo_file.write(", ".join([str(t_id), t_name, repo_name, repo_link]) + '\n')
            print(t_name, repo_link)

            time.sleep(6)
    pass

def add_repos():
    remote_conn = psycopg2.connect(database="trendsdb",
                                  user="updater",
                                  password="upd210!!!",
                                  host='research-trends.labs.intellij.net'
                                )
    cur = remote_conn.cursor()
    with open('repos.csv','r') as repo_file:
        repo_file.readline()  # ignore first line
        for line in repo_file.readlines():
            tid, name, repo, link = line.strip().split(',')
            if not tid:
                continue
            else:
                tid = int(tid)
                cur.execute("select settings from source_settings where source like 'gitstars' and tech_id = %s", (tid,))
                if not cur.fetchall():
                    cur.execute("insert into source_settings VALUES (%s, 'gitstars', %s, '2011-01-01')",
                                (tid, '{"repo":["'+repo.strip()+'"]}'))
    remote_conn.commit()

if __name__ == "__main__":
    add_repos()