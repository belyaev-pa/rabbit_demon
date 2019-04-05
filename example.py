# -*- coding: utf-8 -*-
from demon import create_demon, parse_conf
import sys



def message_handler(msg):
    """
    функция обработки сообщения
    :param msg:
    :return:
    """
    print(msg)


if __name__ == "__main__":
    conf_file_path = '/path/to/conf/file'
    conf_dict = parse_conf(conf_file_path)
    conf_dict['HANDLER_LINK'] = message_handler
    create_demon(sys.argv[1], conf_dict)
    sys.exit(0)