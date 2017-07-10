#  _*_ coding: utf-8 _*_

import json
from random import choice
from pymongo import MongoClient

DEFAULT_FIELD = 'proxy'


class MongoService(object):
    def __init__(self, name, host, port):
        self.name = name  # 数据表名
        self.client = MongoClient(host, port)
        self.db = self.client.proxy  # 默认数据库名

    def get_all(self):
        return [p[DEFAULT_FIELD] for p in self.db[self.name].find()]

    def find(self, value):
        ret = self.db[self.name].find({DEFAULT_FIELD: value.get(DEFAULT_FIELD)})
        size = ret.count()
        return True if size > 0 else False

    def get(self):
        proxy = self.get_all()
        return choice(proxy) if proxy else None  # 随机获取其中的一个值

    def get_by_timestamp(self):
        ret = self.db.find().sort({"timestamp": 1})
        return ret[0].get(DEFAULT_FIELD) if len(ret) > 0 else None

    def put(self, value):
        if self.db[self.name].find_one({DEFAULT_FIELD: value.get(DEFAULT_FIELD)}):
            pass
        else:
            self.db[self.name].insert(value)

    def update(self, value):
        self.db[self.name].update({DEFAULT_FIELD: value.get(DEFAULT_FIELD)},
                                  {"$set": {"count": value.get("count")}})

    def pop(self):
        value = self.get()
        if value:
            self.delete(value)  # 获取该值并删除此值
        return value

    def delete(self, value):
        self.db[self.name].remove({DEFAULT_FIELD: value.get(DEFAULT_FIELD)})

    def delete_all(self):
        self.db[self.name].remove()

    def clean(self):
        # 数据库与字段名相同是作者刻意为之
        self.client.drop_database('proxy')

    def get_status(self):
        value = self.get_all()
        return len(value)

    def set_inc_count(self, value, count):
        sum_count = 0
        data = self.db[self.name].find_one({DEFAULT_FIELD: value.get(DEFAULT_FIELD)})
        if data:
            sum_count = data.get("count", 0)
            self.delete(value)
            sum_count += count
            sum_count = 4 if sum_count >= 4 else sum_count  # 设置最大阈值为4，以防代理突然失效
            data["count"] = sum_count  # 调整引用计数值
            self.update(data)
        return sum_count


if __name__ == "__main__":
    db = MongoService("valid_proxy", "localhost", 27017)
    from time import sleep

    while True:
        print("proxy: ", db.get())
        sleep(10)
