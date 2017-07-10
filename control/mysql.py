# _*_ coding: utf-8 _*_

import pymysql

from util.config import MYSQL
from util.utils import create_id


class MySQLClient(object):
    def __init__(self, data_base, table_name):
        self.conn = pymysql.connect(host=MYSQL.get("host"), port=3306,
                                    user=MYSQL.get("user"), passwd=MYSQL.get("password"),
                                    db=data_base,
                                    charset='utf8')
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

    def delete(self, param):
        sql = 'delete from %s where id = "%s"' % (self.table, param)
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


class MessageClient(MySQLClient):
    def __init__(self, data_base, table_name):
        MySQLClient.__init__(self, data_base, table_name)

    def insert(self, param):
        params = (create_id(), param.get('q'), param.get('hl'), param.get('oq'), param.get('start'))
        sql_list = ["insert into", self.table, "values(%s, %s, %s, %s, %s)"]
        sql = ' '.join(sql_list)
        self.cur.execute(sql, params)
        self.conn.commit()

    def find(self, start, q, oq, param):
        params = (param.get('start', 0), param.get('q', ''), param.get('oq', ''))
        sql = 'select id from %s where %s = "%s" and %s = "%s" and %s = "%s"' % (self.table, start, params[0],
                                                                                 q, params[1], oq, params[2])
        count = self.cur.execute(sql)
        return True if count > 0 else False


if __name__ == "__main__":
    mc = MySQLClient("info", "paper")
    # mc.insert((1, "hello", "url", "author", "jou", 2012, "press", "snap", 100, "path"))
    # mc.update("path", (1, "come here now"))
    # mc.delete(1)
    mc.find("title", "author", "journal", ("hello", "author", "jou"))
