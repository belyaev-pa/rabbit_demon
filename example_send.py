from rabbit_tools import rabbit_send, parse_conf


if __name__ == "__main__":
    conf_file_path = '/home/pavel/PycharmProjects/rabbit_demon/example.conf'
    conf_dict = parse_conf(conf_file_path)
    queue_name = 'aaaabbbb'
    msg = dict(
        field1=1,
        field2=2,
        field3={'user':'guest', 'password':'12345678'},
    )
    rabbit_send(conf_dict, msg, queue_name)