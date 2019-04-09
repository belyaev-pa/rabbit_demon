# -*- coding: utf-8 -*-
import pika
import json
import datetime
from pika import exceptions
from base_rabbit_connector import BaseRabbitMQ


class RabbitMQSender(BaseRabbitMQ):

    def __init__(self, conf_dict, msg, queue_name):
        """
        необходимые настройки в conf_dict
        REPLY_TO = "reply_queue" название очереди
        RABBITMQ_HOST = '10.128.152.30' (ip адрес rabbit`a должно быть выставлено ansibl`ом)
        RABBITMQ_PORT = 5672 (порт работы рабита default = 5672)
        HEARTBEAT_INTERVAL = 600 (интервал серцебиения раббита)
        BLOCKED_CONNECTION_TIMEOUT = 300 (интервал остановки соединения клентом)
        :param conf_dict: словарь с настройками
        :param msg: словарь сообщения
        :param queue_name: название очереди в которую необходимо положить сообщение
        """
        self.msg = msg
        self.queue_name = queue_name
        if type(self.msg) is not dict:
            raise AttributeError('conf_dict must be a dict.')
        super(RabbitMQSender, self).__init__(conf_dict)

    def send(self):
        self.make_message()
        self.rabbit_put()

    def make_message(self):
        """
        формируем json
        :return:
        """
        self.message = json.dumps(self.msg, sort_keys=False, default=str)

    def rabbit_put(self):
        """send message must be called after connect()"""
        self.queue = self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=self.message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
