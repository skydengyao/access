# _*_ coding: utf-8 _*_

from time import sleep
from time import time
from queue import Queue
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler

from util.config import PROXY_SERVICE, MINIMUM_SIZE
from util.config import RAW_PROXY, VALID_PROXY
from util.logger import Logger
from util.utils import verify_proxy_format, check_valid_proxy
from util.utils import dispatch_sleep_time
from proxy.core.getproxy import GetProxy
from proxy.core.proxymanager import ProxyManager

log = Logger(__name__, "proxy_schedule.log").getLogger()


class ProxySchedule(ProxyManager):
    def __init__(self, name=RAW_PROXY):
        ProxyManager.__init__(self, name)
        self.size = len(PROXY_SERVICE)

    def process(self, index):
        func_name = PROXY_SERVICE[index]
        for proxy in getattr(GetProxy, func_name)():
            proxy = proxy.strip()
            value = {"proxy": proxy}
            if verify_proxy_format(proxy) and not self.find(value):
                value["timestamp"] = int(time())
                value["count"] = 0
                self.put(value)


def spider(index, name=RAW_PROXY):
    schedule = ProxySchedule(name)
    schedule.process(index)


def spider_schedule(name=RAW_PROXY):
    size = len(PROXY_SERVICE)
    for index in range(size):
        p = Thread(target=spider, args=(index, name, ))
        p.start()


class UpdateSchedule(object):
    def __init__(self, valid_name=VALID_PROXY, raw_name=RAW_PROXY):
        self.valid_db = ProxyManager(valid_name)
        self.raw_db = ProxyManager(raw_name)

    def get_value(self):
        value = self.raw_db.get()
        if value:  # 随机取值,值可能为None
            value = {"proxy": value}
            self.raw_db.delete(value)
        return value

    def update_schedule(self):
        while True:
            value = self.get_value()
            if value:
                if check_valid_proxy(value) and not self.valid_db.find(value):
                    print("update proxy")
                    self.valid_db.put(value)
                else:
                    log.debug('valid Proxy for %s validation fail' % value.get("proxy"))
            sleep(dispatch_sleep_time())


def update(valid_name=VALID_PROXY, raw_name=RAW_PROXY):
    schedule = UpdateSchedule(valid_name, raw_name)
    schedule.update_schedule()


def update_proxy(valid_name=VALID_PROXY, raw_name=RAW_PROXY, number=20):
    for i in range(number):
        p = Thread(target=update, args=(valid_name, raw_name, ))
        p.start()


class ValidSchedule(ProxyManager):
    def __init__(self, name=VALID_PROXY):
        ProxyManager.__init__(self, name)

    def valid_schedule(self):
        while True:   # 实时调度
            value = self.get()
            if value:
                value = {"proxy": value}
                if check_valid_proxy(value):
                    count = self.set_inc_count(value, 1)
                else:
                    count = self.set_inc_count(value, -1)
                    log.debug('validProxy: {} validation fail'.format(value))

                if count <= -3:
                    self.delete(value)
            sleep(dispatch_sleep_time()*2)  # 降低频繁访问


def valid(name=VALID_PROXY):
    schedule = ValidSchedule(name)
    schedule.valid_schedule()


def valid_proxy(name=VALID_PROXY, number=20):
    for i in range(number):
        p = Thread(target=valid, args=(name,))
        p.start()


class StatusSchedule(ProxyManager):
    def __init__(self, q, name=VALID_PROXY):
        ProxyManager.__init__(self, name)
        self.size = 0   # 有效容积数
        self.q = q  # 队列用于通信

    def schedule(self):
        while True:
            self.size = self.status()
            if self.size <= MINIMUM_SIZE:
                if self.q.empty():  # 当队列数据被清空时, 再次向队列添加信号
                    self.q.put(self.size)
            sleep(dispatch_sleep_time()*5)


def status_proxy(q, name=VALID_PROXY):
    schedule = StatusSchedule(q, name)
    schedule.schedule()


def refresh(valid_name, raw_name, number=20):
    update_proxy(valid_name, raw_name, number=number)


# 间隔10分钟调度一次
def capacity_schedule(q, name=RAW_PROXY):
    if not q.empty():
        spider_schedule(name)
        q.get()  # 释放信号量


def crawl(q, name=RAW_PROXY):
    spider_schedule(name)
    schedule = BackgroundScheduler()
    schedule.add_job(func=capacity_schedule, args=(q, name, ), trigger='interval', minutes=10)
    schedule.start()


def validate(q, name=VALID_PROXY, number=20):
    valid_proxy(name, number=number)
    status_proxy(q, name)


if __name__ == "__main__":
    q_status = Queue()
    crawl(q_status, RAW_PROXY)
    refresh(VALID_PROXY, RAW_PROXY, 20)
    validate(q_status, VALID_PROXY, 10)
