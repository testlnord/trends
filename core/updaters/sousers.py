"""StackOverflow users count updater """
import datetime

from .parent import DataUpdater
from ..utils.stuff import get_threshold_date
from ..config import config, project_root


class SoUsersUpdater(DataUpdater):
    setting_path = project_root+"/src_conf/so_users.json"

    def __init__(self):
        super().__init__(self.setting_path, __name__)
        self.logger.info("SO users updater initialized.")

    def update_data(self):
        threshold_date = get_threshold_date(self.settings['refresh_time']).strftime(config['date_format'])
        dirty = False
        for tech_id, tech in self.settings['techs'].items():
            if tech['last_date'] < threshold_date:
                last_date = datetime.datetime.strptime(tech['last_date'], config['date_format']) - \
                    datetime.timedelta(days=3)
                tag = tech['tag'][0]
                self.logger.debug("Getting data for tag: %s", tag)

                data = self.get_data_for_tag(tag, last_date)

                if data:
                    max_date = max(data, key=lambda x: x[0])[0]
                    min_date = min(data, key=lambda x: x[0])[0]

                    self.logger.debug("Updating database")
                    cur = self.connection.cursor()
                    cur.execute("delete from rawdata where source='sousers' and tech_id = %s and time >= %s",
                                (tech_id, min_date))
                    cur.executemany("insert into rawdata(source, tech_id, time, value) values (%s, %s, %s, %s)",
                                    (('sousers', tech_id, d, v) for d, v in data))
                    self.connection.commit()
                    dirty = True

                    self.logger.debug("Updating settings")
                    self.settings['techs'][tech_id]['last_date'] = max_date.strftime(config['date_format'])
                    self.commit_settings()

        return dirty

    def get_data_for_tag(self, tag, last_date):
        cur = self.connection.cursor()
        result = []
        month = datetime.date(last_date.year, last_date.month, 1)
        # this_month = datetime.date.today()
        # datetime.date(this_month.year, this_month.month, 1)
        this_month = datetime.date(2014, 5, 1)
        if tag:
            tag = '<'+tag+'>'
        tag = '%'+tag+'%'
        while month < this_month:
            cur.execute("""with user_pts as (
            with sh_posts as (select owneruserid as userid, to_char(creationdate, 'YYYY MM') as time, score from posts
            where posts.tags like %s )
            select sum(score) as pts, userid  from sh_posts inner join users on users.id = sh_posts.userid
            where time < %s group by userid )
            select count(userid) from user_pts where pts > 100; """, (tag, month.strftime('%Y %m')))
            val = cur.fetchone()[0]
            result.append((month, val))
            month = datetime.date(month.year + int(month.month/12), month.month % 12 + 1, 1)
        return result