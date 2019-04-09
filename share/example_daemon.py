#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rabbit_tools import create_daemon, parse_conf
import sys



def message_handler(msg):
    """
    функция обработки сообщения
    :param msg:
    :return:
    """
    with open ('/home/pavel/example_rabbitmq.txt', 'a') as f:
        f.write(msg)


if __name__ == "__main__":
    conf_file_path = '/home/pavel/PycharmProjects/rabbit_daemon/example.conf'
    conf_dict = parse_conf(conf_file_path)
    conf_dict['HANDLER_LINK'] = message_handler
    create_daemon(sys.argv[1], conf_dict)
    sys.exit(0)
