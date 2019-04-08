# -*- coding: utf-8 -*-
import base_demon
import ConfigParser
from demon import DaemonConfigurator, UnsupportedCommandException
from rabbit_sender import RabbitMQSender


def create_demon(command, conf_dict):
    """
    Функция создания и управлению демоном
    :param command: строка содержащая команду start, stop, restart
    :param conf_dict: словарь с настройками
    :return: void
    """
    daemon = base_demon.Demon(pidfile=conf_dict['PID_FILE_PATH'],
                              conf_dict=conf_dict,
                              log_name=conf_dict['LOG_NAME'])
    config = DaemonConfigurator(daemon)
    react_dict = config.get_reacts_for_demon()
    try:
        react_dict[command]()
    except KeyError:
        raise UnsupportedCommandException()



def parse_conf(conf_file_path):
    """
    Функция парсинга конфиг файла
    :param conf_file_path: путь до файла
    :return: сформированный словарь настроек
    """
    config = ConfigParser.ConfigParser()
    config.read(conf_file_path)
    conf_dict = dict(
        QUEUE_NAME=config.get('rabbitmq_server', 'QUEUE_NAME'),
        RABBITMQ_HOST=config.get('rabbitmq_server', 'RABBITMQ_HOST'),
        RABBITMQ_PORT=config.get('rabbitmq_server', 'RABBITMQ_PORT'),
        HEARTBEAT_INTERVAL=config.get('rabbitmq_server', 'HEARTBEAT_INTERVAL'),
        BLOCKED_CONNECTION_TIMEOUT=config.get('rabbitmq_server', 'BLOCKED_CONNECTION_TIMEOUT'),
        USE_GSS_API=config.get('daemon_auth', 'USE_GSS_API'),
        PRINCIPAL=config.get('daemon_auth', 'PRINCIPAL'),
        RABBIT_COMMON_USER=config.get('daemon_auth', 'RABBIT_COMMON_USER'),
        RABBIT_COMMON_PASSWORD=config.get('daemon_auth', 'RABBIT_COMMON_PASSWORD'),
        RABBITMQ_SPS=config.get('daemon_auth', 'RABBITMQ_SPS'),
        TMP_LOG_PATH=config.get('daemon_conf', 'TMP_LOG_PATH'),
        PID_FILE_PATH=config.get('daemon_conf', 'PID_FILE_PATH'),
        LOG_NAME=config.get('daemon_conf', 'LOG_NAME'),
    )
    return conf_dict


def rabbit_send(conf_dict, msg, queue_name):
    """
    Функция посылки сообщения в RabbitMQ
    :param conf_dict: словарь настроек
    :param msg: передаваемое сообщение (словарь)
    :param queue_name: название очереди - строка
    :return: void
    """
    with RabbitMQSender(conf_dict, msg, queue_name) as sender_obj:
        sender_obj.send()
