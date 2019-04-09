# -*- coding: utf-8 -*-
import pika
import kerberos


class BaseRabbitMQ(object):
    """
    Базовый класс для соединения с RabbitMQ сервером содержит функции:
    connect: для соединения с сервером
    get_settings: для получения настроек из словаря настроек
    """

    def __init__(self, conf_dict):
        """
        пример файла ..exmaple.conf
        :param conf_dict: словарь с настроечными данными
        connect to rabbitmq
        NOTE: prefetch is set to 1 here for test to keep the number of threads created
        to a reasonable amount. We can to test with different prefetch values
        to find which one provides the best performance and usability for your solution

        :return: None (void)
        """
        self.conf_dict = conf_dict
        self.params = pika.ConnectionParameters(
            host=self.get_settings('RABBITMQ_HOST'),
            port=self.get_settings('RABBITMQ_PORT'),
            credentials=pika.credentials.PlainCredentials(self.principal, self.token),
            heartbeat_interval=int(self.get_settings('HEARTBEAT_INTERVAL')),
            blocked_connection_timeout=int(self.get_settings('BLOCKED_CONNECTION_TIMEOUT')),
        )
        self.connection = pika.BlockingConnection(
            parameters=self.params,
        )
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(
            queue=self.get_settings('QUEUE_NAME'),
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
        self.channel.basic_qos(prefetch_count=1)

    def __enter__(self):
        """
        Необходимые "магические методы" для реалзации функционала with
        Использование:
        with RabbitMQSender() as sender_obj:
            # use sender_obj (используем объект тут)
        :return:
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Необходимые "магические методы" для реалзации функционала with
        :param exc_type:
        :param exc_value:
        :param traceback:
        :return:
        """
        self.connection.close()

    def get_settings(self, setting):
        if type(self.conf_dict) is not dict:
            raise AttributeError('conf_dict must be a dict.')
        try:
            prop = self.conf_dict[setting]
        except KeyError:
            raise SettingIsNoneException()
        return prop

    @property
    def principal(self):
        """
        не будет участвовать в аутентификации поэтому может быть любым
        :return: principal пользователя
        """
        if int(self.get_settings('USE_GSS_API')):
            return self.get_settings('PRINCIPAL')
        else:
            return self.get_settings('RABBIT_COMMON_USER')

    @property
    def token(self):
        """
        для передачи в поле пароль GSS токена
        :return: GSSAPI token (либо пароль в тестовой среде)
        """
        if int(self.get_settings('USE_GSS_API')):
            result, context = kerberos.authGSSClientInit(self.get_settings('RABBITMQ_SPS'),
                                                         gssflags=kerberos.GSS_C_SEQUENCE_FLAG,
                                                         principal=self.get_settings('PRINCIPAL'))
            _result = kerberos.authGSSClientStep(context, '')
            return kerberos.authGSSClientResponse(context)
        else:
            return self.get_settings('RABBIT_COMMON_PASSWORD')


class SettingIsNoneException(Exception):
    def __init___(self, *args):
        Exception.__init__(self, "Can`t find {0} in provided config dictionary".format(*args))
