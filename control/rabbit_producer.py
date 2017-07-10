# _*_ coding: utf-8 _*_

import json
import pika

from util.config import AUTHENTICATE, RABBITMQ
from util.config import PRIORI, EXCHANGE, EXCHANGE_TYPE
from util.info import UserData


class RabbitMQProducer(object):
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.conn = None
        self.channel = None
        self.reconnect()

    def connect(self):
        credit = pika.PlainCredentials(AUTHENTICATE.get("user"), AUTHENTICATE.get("password"))
        params = pika.ConnectionParameters(RABBITMQ.get("host"), RABBITMQ.get("port"), '/', credit)
        return pika.BlockingConnection(params)

    def reconnect(self):
        self.conn = self.connect()
        self.channel = self.conn.channel()
        self.channel.exchange_declare(exchange=EXCHANGE, exchange_type=EXCHANGE_TYPE)

    def publish_message(self, message):
        self.channel.basic_publish(exchange=EXCHANGE,
                                   routing_key=self.queue_name,
                                   body=message,
                                   properties=pika.BasicProperties(delivery_mode=2,))

    def run(self, message):
        message = json.dumps(message).encode(encoding="utf-8") if isinstance(message, (list, dict)) else message
        print("message: ", message)
        try:
            self.publish_message(message)
            print("publish")
        except pika.exceptions:
            self.reconnect()
            self.publish_message(message)
            print("publish2")

    def close(self):
        if self.conn:
            self.conn.close()


class ProduceService(RabbitMQProducer):
    def __init__(self, queue_name):
        RabbitMQProducer.__init__(self, queue_name)

    def produce(self, message):
        RabbitMQProducer.run(self, message)
        self.close()


if __name__ == "__main__":
    name = PRIORI
    import os, time
    path = '../data/data.txt'
    for line in open(path, encoding='utf-8'):
        array = line.split('\t')
        if array[2] == '' or array[4] == '\n':
            message = [(array[0], array[1]), (array[0], array[3])]
        else:
            message = [(array[0], array[1]), (array[0], array[3]),
                       (array[0], array[2]), (array[0], array[4].strip())]

        for i in message:
            data = UserData(i)
            text = {"param": data.set_request()}
            producer = ProduceService(name)
            producer.produce(text)
        time.sleep(60)
