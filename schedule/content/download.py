# _*_ coding:utf-8 _*_

from threading import Thread
from queue import Queue

from util.config import DOWNLOADPDF, DOWNLOADHTML
from control.download_consumer import DownloadConsume

QUEUE = Queue()


def schedule(data_base, table_name, queue_name, q, number=0):
    consumer = DownloadConsume(data_base, table_name, queue_name, q, number)
    consumer.consume()


if __name__ == "__main__":
    for i in range(2):
        p = Thread(target=schedule, args=("info", "paper", DOWNLOADPDF, QUEUE, i,))
        p.start()

    for i in range(1):
        p = Thread(target=schedule, args=("info", "paper", DOWNLOADHTML, QUEUE, i,))
        p.start()