# _*_ coding: utf-8 _*_

import pymysql

from util.config import MYSQL, MIDDLE, LAGBEHIND
from util.utils import create_id, current_time


class MySQLClient(object):
    def __init__(self, data_base, table_name):
        self.conn = pymysql.connect(host=MYSQL.get("host"), port=3306,
                                    user=MYSQL.get("user"), passwd=MYSQL.get("password"),
                                    db=data_base, charset='utf8')
        self.table = table_name
        self.cur = self.conn.cursor()

    def insert(self, param):
        sql_list = ["insert into", self.table, "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"]
        sql = ' '.join(sql_list)
        self.cur.execute(sql, param)
        self.conn.commit()

    def update(self, key, param):
        sql = 'update %s set %s = "%s" where id = "%s"' % (self.table, key, param[1], param[0])
        self.cur.execute(sql)
        self.conn.commit()

    def find(self, title, author, journal, param):
        sql = 'select id from %s where %s = "%s" and %s = "%s" and %s = "%s"' % (self.table, title, param[0],  author,
                                                                                 param[1], journal, param[2])
        count = self.cur.execute(sql)
        return True if count > 0 else False

    def delete(self, id):
        sql = 'delete from %s where id = "%s"' % (self.table, id)
        self.cur.execute(sql)
        self.conn.commit()

    def get_id(self, title, author, journal, param):
        flag = self.find(title, author, journal, param)
        if flag:
            ret = self.cur.fetchone()
            return ret[0]
        else:
            return None

    def close(self):
        self.conn.close()


class CacheClient(MySQLClient):
    def __init__(self, data_base, table_name):
        MySQLClient.__init__(self, data_base, table_name)
        self.delta = 2

    def insert(self, param):
        params = (create_id(), param.get('q'), param.get('hl'),
                  param.get('oq'), param.get('start'), current_time())
        sql_list = ["insert into", self.table, "values(%s, %s, %s, %s, %s, %s)"]
        sql = ' '.join(sql_list)
        self.cur.execute(sql, params)
        self.conn.commit()

    def find(self, start, q, oq, param):
        params = (param.get('start', 0), param.get('q', ''), param.get('oq', ''))
        sql = 'select id from %s where %s = "%s" and %s = "%s" and %s = "%s"' % (self.table, start, params[0],
                                                                                 q, params[1], oq, params[2])
        count = self.cur.execute(sql)
        return True if count > 0 else False

    def fetch_and_delete(self):
        sql = 'select * from %s where timestamp < date_sub(now(), interval %s hour)' % (self.table, self.delta)
        count = self.cur.execute(sql)
        if count > 0:
            ret = self.cur.fetchone()
            uid = ret[0]
            param = {"q": ret[1], "hl": ret[2], "oq": ret[3], "start": ret[4], "as_sdt": 0}
            self.delete(uid)
            return param
        else:
            return None


class DataClient(MySQLClient):
    def __init__(self, data_base, table_name):
        MySQLClient.__init__(self, data_base, table_name)
        self.delta = 4

    def insert(self, param):
        params = (create_id(), param.get('q'), param.get('hl'),
                  param.get('oq'), param.get('start'), current_time())
        sql_list = ["insert into", self.table, "values(%s, %s, %s, %s, %s, %s)"]
        sql = ' '.join(sql_list)
        self.cur.execute(sql, params)
        self.conn.commit()

    def find(self, start, q, oq, param):
        params = (param.get('start', 0), param.get('q', ''), param.get('oq', ''))
        sql = 'select id from %s where %s = "%s" and %s = "%s" and %s = "%s"' % (self.table, start, params[0],
                                                                                 q, params[1], oq, params[2])
        count = self.cur.execute(sql)
        return True if count > 0 else False

    def update(self, id):
        sql = 'update %s set timestamp = "%s" where id = "%s"' % (self.table, current_time(), id)
        self.cur.execute(sql)
        self.conn.commit()

    def fetch_and_update(self):
        sql = 'select * from %s where timestamp < date_sub(now(), interval %s hour) order by timestamp asc limit 1' % (self.table, self.delta)
        count = self.cur.execute(sql)
        if count > 0:
            ret = self.cur.fetchone()
            uid = ret[0]
            param = {"q": ret[1], "hl": ret[2], "oq": ret[3], "start": ret[4], "as_sdt": 0}
            self.update(uid)
            return param
        else:
            return None


class DownloadClient(MySQLClient):
    def __init__(self, data_base, table_name):
        MySQLClient.__init__(self, data_base, table_name)

    def insert(self, param, mode):
        params = (param.get('id'), param.get('title'), param.get('url'), param.get('author'),
                  param.get('journal'), mode, current_time())
        sql_list = ["insert into", self.table, "values(%s, %s, %s, %s, %s, %s, %s)"]
        sql = ' '.join(sql_list)
        self.cur.execute(sql, params)
        self.conn.commit()

    def find(self, title, url, param, mode):
        params = (param.get('title'), param.get('url'))
        sql = 'select id from %s where %s = "%s" and %s = "%s" and mode = "%s"' % (self.table, title, params[0], url, params[1], mode)
        count = self.cur.execute(sql)
        return True if count > 0 else False

    def fetch_and_delete(self, mode):
        sql = 'select * from %s where mode = "%s" order by timestamp asc limit 1' % (self.table, mode)
        count = self.cur.execute(sql)
        if count > 0:
            ret = self.cur.fetchone()
            uid = ret[0]
            self.delete(uid)

            value = {"id": uid, "title": ret[1], "url": ret[2],
                     "author": ret[3], "journal": ret[4]}
            return value
        else:
            return None


if __name__ == "__main__":
    cache = DownloadClient("info", "download")
    while True:
        param = cache.fetch_and_delete(1)
        if param:
            print("param ： ", param)

