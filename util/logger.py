# -*- coding:utf-8 -*-

import logging


class Logger(object):
    def __init__(self, name, log_name="crawler.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        fm = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)s] - %(message)s')

        fh.setFormatter(fm)
        ch.setFormatter(fm)

        if not self.logger.handlers:
            self.logger.addHandler(fh)

        self.logger.propagate = False
        # logger.addHandler(ch)

    def getLogger(self):
        return self.logger
