# _*_ coding: utf-8 _*_

from time import sleep
from threading import Thread

from control.mysql import CacheClient, DataClient
from control.rabbit_producer import ProduceService
from util.utils import dispatch_sleep_time
from util.config import MIDDLE, LAGBEHIND


def schedule(db, table, mode):
    cache = CacheClient(db, table.lower(), mode)
    while True:
        param = cache.fetch_and_delete()
        if param:
            producer = ProduceService(table)
            producer.produce(param)
        sleep(dispatch_sleep_time()*3)


def trigger(db, table):
    data = DataClient(db, table)
    while True:
        param = data.fetch_and_update()
        if param:
            producer = ProduceService(LAGBEHIND)
            producer.produce(param)
        sleep(dispatch_sleep_time()*2)


if __name__ == '__main__':
    for i in range(3):
        p = Thread(target=schedule, args=("info", MIDDLE, 0, ))
        p.start()

    for i in range(2):
        p = Thread(target=schedule, args=("info", LAGBEHIND, 1, ))
        p.start()

    for i in range(4):
        p = Thread(target=trigger, args=("info", "message", ))
        p.start()
