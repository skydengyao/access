# _*_ coding: utf-8 _*_

import json
import redis

from util.utils import set_expire


class RedisSet(object):
    def __init__(self, name, pool):
        self.name = name  # 集合名，不含重复的信息
        self.conn = redis.Redis(connection_pool=pool)

    def get(self):
        return self.conn.srandmember(name=self.name).decode('utf-8')

    def put(self, value):
        value = json.dumps(value) if isinstance(value, (list, dict)) else value
        self.conn.sadd(self.name, value)  # 集合中插入值

    def delete(self, value):
        value = json.dumps(value) if isinstance(value, (list, dict)) else value
        self.conn.srem(self.name, value)  # 集合中删除值


class RedisHset(object):
    def __init__(self, name, pool):
        self.name = name  # 哈希字段名
        self.conn = redis.Redis(connection_pool=pool)

    def get(self):
        return self.conn.hgetall(self.name)

    def put(self, param):
        p = self.conn.pipeline()
        for key, value in param.items():
            p.hset(self.name, key, value)
        p.expireat(self.name, set_expire())
        p.execute()

    def delete(self):
        keys = self.conn.hkeys(self.name)
        self.conn.hdel(self.name, keys)

