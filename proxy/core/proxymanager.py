# _*_ coding: utf-8 _*_

from control.mongodb import MongoService
from util.config import MONGODB, VALID_PROXY


class ProxyManager(object):
    def __init__(self, table_name):
        self.db = MongoService(table_name, MONGODB.get("host"), MONGODB.get("port"),
                               MONGODB.get("user"), MONGODB.get("password"))

    def find(self, value):
        ret = self.db.find(value)
        return ret

    def put(self, value):
        self.db.put(value)

    def get(self):
        ret = self.db.get()
        return ret

    def get_all(self):
        ret = self.db.get_all()
        return ret

    def delete(self, proxy):
        self.db.delete(proxy)

    def status(self):
        ret = self.db.get_status()
        return ret

    def set_inc_count(self, value, count):
        sum_count = self.db.set_inc_count(value, count)
        return sum_count

    def get_status(self):
        valid_number = self.status()
        return valid_number


if __name__ == "__main__":
    manager = ProxyManager(VALID_PROXY)
    from time import sleep
    while True:
        print(manager.get())
        sleep(10)
