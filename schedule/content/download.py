# _*_ coding: utf-8 _*_

from threading import Thread
from queue import Queue

from util.config import DOWNLOADPDF, DOWNLOADHTML, DOWNLOADNCBI, DOWNLOADDOI, DOWNLOADPMID
from control.download_consumer import DownloadConsume

QUEUE = Queue()


def schedule(data_base, table_name, queue_name, q):
    consumer = DownloadConsume(data_base, table_name, queue_name, q)
    consumer.consume()


if __name__ == "__main__":
    for i in range(3):
        p = Thread(target=schedule, args=("info", "paper", DOWNLOADPDF, QUEUE, ))
        p.start()

    for i in range(2):
        p = Thread(target=schedule, args=("info", "paper", DOWNLOADHTML, QUEUE, ))
        p.start()

    for i in range(2):
        p = Thread(target=schedule, args=("info", "paper", DOWNLOADDOI, QUEUE, ))
        p.start()

    for i in range(2):
        p = Thread(target=schedule, args=("info", "paper", DOWNLOADPMID, QUEUE, ))
        p.start()

    for i in range(1):
        p = Thread(target=schedule, args=("info", "paper", DOWNLOADNCBI, QUEUE, ))
        p.start()


