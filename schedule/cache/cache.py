# _*_ coding:utf-8 _*_

from time import sleep
from threading import Thread

from control.mysql import CacheClient, DataClient, DownloadClient
from control.rabbit_producer import ProduceService
from util.config import MIDDLE, LAGBEHIND, DOWNLOADBRW, DOWNLOADHTML


def schedule(db, table):
    cache = CacheClient(db, table.lower())
    while True:
        param = cache.fetch_and_delete()
        if param:
            producer = ProduceService(table)
            producer.produce(param)
        sleep(10)


def trigger(db, table):
    data = DataClient(db, table)
    while True:
        param = data.fetch_and_update()
        if param:
            producer = ProduceService(LAGBEHIND)
            producer.produce(param)
        sleep(10)


def download(db, table, mode):
    load = DownloadClient(db, table)
    while True:
        param = load.fetch_and_delete(mode)
        if param:
            if mode == 0:
                producer = ProduceService(DOWNLOADBRW)
            else:
                producer = ProduceService(DOWNLOADHTML)
            producer.produce(param)
        sleep(10)


if __name__ == '__main__':
    for i in range(2):
        p = Thread(target=schedule, args=("info", MIDDLE,))
        p.start()

    for i in range(1):
        p = Thread(target=trigger, args=("info", "message",))
        p.start()

    for i in range(2):
        p = Thread(target=download, args=("info", "download", i,))
        p.start()

