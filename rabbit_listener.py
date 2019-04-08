# -*- coding: utf-8 -*-
import threading
import functools
import datetime
import syslog
import traceback
from pika import exceptions
from base_rabbit_connector import BaseRabbitMQ


class RabbitMQListener(BaseRabbitMQ):

    def __init__(self, conf_dict):
        """
        конструктор демона
        :param pidfile: путь к pid файлу, обязательный агрумент
        :param stdin: путь к файлу для хранения stdin, по умолчанию никуда не сохраняет
        :param stdout: путь к файлу для хранения stdout, по умолчанию никуда не сохраняет
        :param stderr: путь к файлу для хранения stderr, по умолчанию никуда не сохраняет
        """
        # self.stdin = stdin
        # self.stdout = stdout
        # self.stderr = stderr
        # self.pidfile = pidfile
        super(RabbitMQListener, self).__init__(conf_dict)
        # адекватная передача ссылки на функцию-обработчик сообщения
        self.handler_link = self.get_settings('HANDLER_LINK')

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Необходимые "магические методы" для реалзации функционала with
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return:
        """
        syslog.openlog(self.get_settings('LOG_NAME'))
        syslog.syslog(syslog.LOG_INFO, '{} Exiting...{}'.format(datetime.datetime.now(), traceback.format_exc(limit=2)))
        self.channel.stop_consuming()
        self.connection.close()
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()

    def run(self):
        while True:
            self.threads = []
            on_message_callback = functools.partial(self.on_message)
            self.channel.basic_consume(on_message_callback,
                                       queue=self.get_settings('QUEUE_NAME'))
            self.channel.start_consuming()

    def ack_message(self, ch, delivery_tag):
        """
        функция возврата ack для RabbitMQ + пишем лог файл, если вернули акк
        очищаем лог файл, если нет пишем в лог файл об этом и ждем тоже
        сообщение снова, что бы продолжить писать в него
        Note that `channel` must be the same pika channel instance via which
        the message being ACKed was retrieved (AMQP protocol constraint).
        """
        if self.channel.is_open:
            self.channel.basic_ack(self.delivery_tag)
            # erasing log file:
            open(self.get_settings('TMP_LOG_PATH'), 'w').close()
        else:
            with open(self.get_settings('TMP_LOG_PATH'), 'a') as log_file:
                log_file.write("{} cannot return ack to rabbit channel is closed".format(datetime.datetime.now()))


    def do_work(self, conn, ch, delivery_tag, body):
        """
        функция выполнения работы
        # thread_id = threading.get_ident()
        # fmt1 = 'Thread id: {} Delivery tag: {} Message body: {}'
        # LOGGER.info(fmt1.format(thread_id, delivery_tag, body))
        # Sleeping to simulate 10 seconds of work (we need to code work here)
        """
        # time.sleep(10)
        # необходимо переработать вызов класса воркера тут как указан ов to_do в __init__
        self.handler_link(body)
        # if self.ab_sb == 'ab':
        #     work.AgentJobHandler(body, self.get_settings('TMP_LOG_PATH'))
        # elif self.ab_sb == 'sb':
        #     work.SBJobHandler(body, self.get_settings('TMP_LOG_PATH'))
        callback = functools.partial(self.ack_message, ch, delivery_tag)
        self.connection.add_callback_threadsafe(callback)

    def on_message(self, ch, method_frame, header_frame, body):
        """
        функция выполняемая при получении сообщения
        формирует поток обработки сообщения, при этом поддерживая
        соединения с RabbitMQ
        example from https://github.com/pika/pika/blob/master/examples/basic_consumer_threaded.py
        :param method_frame: метод (мета параметры используемые rabbitmq)
        :param header_frame: заголовки пакета AMQP
        :param body: сообщение
        :return: void
        """
        self.delivery_tag = method_frame.delivery_tag
        thr = threading.Thread(target=self.do_work, args=(self.connection, ch, self.delivery_tag, body))
        thr.start()
        self.threads.append(thr)

