import jaydebeapi
import pickle
conn = jaydebeapi.connect('net.sourceforge.jtds.jdbc.Driver',
                          ['jdbc:jtds:sqlserver://jetstat.labs.intellij.net:1433;databaseName=StackOverflowStatistic',
                           'so_write',
                           'dmitrykalashnikov'],
                          ['/home/user/.PyCharm40/config/jdbc-drivers/jtds-1.2.5.jar'])

cur = conn.cursor()
cur.execute("select id, tagname from tags")
tags_dict = {row[1]: int(row[0]) for row in cur.fetchall()}

print("Tags created...")
cur.execute("select id, tags from posts")
all_posts = {}
print("Tags from posts selected")
post = cur.fetchone()
while post:
    post_id = int(post[0])
    print("post id: ", post_id)
    post_tags = post[1]
    if post_tags:
        post_tags = post_tags[1:-1].split("><")
        try:
            post_tags_ids = [tags_dict[t] for t in post_tags]
            ins_cur = conn.cursor()
            for tag_id in post_tags_ids:
                ins_cur.execute("insert into posttags(postid, tagid) values ({},{})".format(post_id, tag_id))
            #
            # conn.commit()
        except KeyError as e:
            print("Tag not found")
            print(post_tags)
            print(e)


    post = cur.fetchone()


