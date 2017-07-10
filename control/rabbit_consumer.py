# _*_ coding: utf-8 _*_

import pika
import json
from time import sleep

from proxy.core.proxymanager import ProxyManager
from util.config import AUTHENTICATE, RABBITMQ, VALID_PROXY, QUEUE
from util.config import PRIORI_CPUTIME, MIDDLE_CPUTIME, LAGBEHIND_CPUTIME
from util.config import PRIORI, MIDDLE, LAGBEHIND
from util.config import EXCHANGE, EXCHANGE_TYPE
from util.info import GoogleScholarHeader
from core.crawl import GoogleScholarCrawl


class RabbitMQConsumer(object):
    def __init__(self, queue_name, q):
        self.conn = None
        self.channel = None
        self._closing = False
        self._consumer_tag = None
        self.queue_name = queue_name
        self.header = GoogleScholarHeader(q)
        self.db = ProxyManager(VALID_PROXY)

    def connect(self):
        credit = pika.PlainCredentials(AUTHENTICATE.get("user"), AUTHENTICATE.get("password"))
        params = pika.ConnectionParameters(RABBITMQ.get("host"), RABBITMQ.get("port"), '/', credit)
        return pika.SelectConnection(params, self.on_connection_open, stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        self.conn.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self.channel = None
        if self._closing:
            self.conn = self.conn.ioloop.stop()
        else:
            self.conn.add_timeout(5, self.reconnect)

    def reconnect(self):
        self.conn.ioloop.stop()
        if not self._closing:
            self.conn = self.connect()
            self.conn.ioloop.start()

    def open_channel(self):
        self.conn.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(EXCHANGE)

    def add_on_channel_close_callback(self):
        self.channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        self.conn.close()

    def setup_exchange(self, exchange_name):
        self.channel.exchange_declare(self.on_exchange_declareok, EXCHANGE, EXCHANGE_TYPE)

    def on_exchange_declareok(self, unused_frame):
        self.channel.queue_declare(self.on_queue_declareok, queue=self.queue_name, durable=True)

    def on_queue_declareok(self, method_frame):
        self.channel.queue_bind(self.on_bindok, self.queue_name, EXCHANGE, self.queue_name)

    def on_bindok(self, unused_frame):
        self.start_consuming()

    def start_consuming(self):
        self.add_on_cancel_callback()
        self._consumer_tag = self.channel.basic_consume(self.on_message, self.queue_name, no_ack=False)

    def add_on_cancel_callback(self):
        self.channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        if self.channel:
            self.channel.close()

    def on_message(self, ch, method, properties, body):
        param = json.loads(body.decode("utf-8"))
        param["proxy"] = self.db.get()
        param["header"] = self.header.get_header()
        crawler = GoogleScholarCrawl(param)
        crawler.get()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def stop_consuming(self):
        if self.channel:
            self.channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self):
        if self.channel:
            self.channel.close()

    def run(self):
        self.conn = self.connect()
        self.conn.ioloop.start()

    def stop(self):
        self._closing = True
        self.stop_consuming()
        self.conn.ioloop.start()

    def close_connection(self):
        if self.conn:
            self.conn.close()


class ConsumeService(RabbitMQConsumer):
    def __init__(self, queue_name, agent_queue):
        RabbitMQConsumer.__init__(self, queue_name, agent_queue)

    def consume(self):
        RabbitMQConsumer.run(self)


if __name__ == "__main__":
    name = PRIORI
    consumer = ConsumeService(name, QUEUE)
    consumer.consume()
