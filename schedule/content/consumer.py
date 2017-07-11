# _*_ coding: utf-8 _*_

from threading import Thread
from queue import Queue

from util.config import PRIORI, MIDDLE, LAGBEHIND
from control.rabbit_consumer import ConsumeService

QUEUE = Queue()


def schedule(name, queue):
    consumer = ConsumeService(name, queue)
    consumer.consume()


if __name__ == "__main__":
    for i in range(3):
        p = Thread(target=schedule, args=(PRIORI, QUEUE,))
        p.start()

    for i in range(2):
        p = Thread(target=schedule, args=(MIDDLE, QUEUE,))
        p.start()

    for i in range(2):
        p = Thread(target=schedule, args=(LAGBEHIND, QUEUE,))
        p.start()
