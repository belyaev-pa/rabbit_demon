# -*- coding: utf-8 -*-


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


class UnsupportedCommandException(Exception):
    def __init___(self, *args):
        Exception.__init__(self, "Can`t find {0} in provided command".format(*args))
