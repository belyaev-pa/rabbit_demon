# -*- coding: utf-8 -*-
import sys
import base_demon
import ConfigParser


class ReactFunction:
    """
    Класс команд обрабатываемых агентом
    для добавления команды, необходимо добавить
    новую функцию в класс из консоли будет вызываться
    python ab_demon.py new_command
    """
    def __init__(self, _daemon):
        """
        конструктор
        :param _daemon: инстанс демона
        """
        self._daemon = _daemon

    def start(self):
        """
        команда для запуска демона
        :return: void
        """
        self._daemon.start()

    def stop(self):
        """
        команда для остановки демона
        :return: void
        """
        self._daemon.stop()

    def restart(self):
        """
        команда для рестарта демона
        :return:
        """
        self._daemon.restart()


class DaemonConfigurator:

    def __init__(self, _daemon):
        self._demon = _daemon

    def get_reacts_for_demon(self):
        """
        формирует словарь команд на основании класса ReactFunction
        :return: словарь методов
        """
        local_con = ReactFunction(self._demon)
        react_dict = {}
        for react in dir(local_con):
            if react[0:1] != '_':
                react_dict[react] = getattr(local_con, react)
        return react_dict


def create_demon(command, conf_dict):
    daemon = base_demon.Demon(pidfile=conf_dict['PID_FILE_PATH'],
                              conf_dict=conf_dict,
                              log_name=conf_dict['LOG_NAME'])
    config = DaemonConfigurator(daemon)
    react_dict = config.get_reacts_for_demon()
    try:
        react_dict[command]()
    except KeyError:
        raise UnsupportedCommandException()
    else:
        sys.exit(0)


def parse_conf(conf_file_path):
    config = ConfigParser.ConfigParser()
    config.read(conf_file_path)
    conf_dict = dict(
        QUEUE_NAME=config.get('rabbitmq_demon', 'QUEUE_NAME'),
        RABBITMQ_HOST=config.get('rabbitmq_demon', 'RABBITMQ_HOST'),
        RABBITMQ_PORT=config.get('rabbitmq_demon', 'RABBITMQ_PORT'),
        HEARTBEAT_INTERVAL=config.get('rabbitmq_demon', 'HEARTBEAT_INTERVAL'),
        BLOCKED_CONNECTION_TIMEOUT=config.get('rabbitmq_demon', 'BLOCKED_CONNECTION_TIMEOUT'),
        USE_GSS_API=config.get('rabbitmq_demon', 'USE_GSS_API'),
        PRINCIPAL=config.get('rabbitmq_demon', 'PRINCIPAL'),
        RABBIT_COMMON_USER=config.get('rabbitmq_demon', 'RABBIT_COMMON_USER'),
        RABBIT_COMMON_PASSWORD=config.get('rabbitmq_demon', 'RABBIT_COMMON_PASSWORD'),
        RABBITMQ_SPS=config.get('rabbitmq_demon', 'RABBITMQ_SPS'),
        TMP_LOG_PATH=config.get('rabbitmq_demon', 'TMP_LOG_PATH'),
        PID_FILE_PATH=config.get('rabbitmq_demon', 'PID_FILE_PATH'),
        LOG_NAME=config.get('rabbitmq_demon', 'LOG_NAME'),
    )
    return conf_dict


class UnsupportedCommandException(Exception):
    def __init___(self, *args):
        Exception.__init__(self, "Can`t find {0} in provided command".format(*args))
