# -*- coding: utf-8 -*-
import sys
import os
import time
import atexit
import signal
import syslog
import datetime
import rabbit_listener


class Daemon:

    def __init__(self, pidfile, conf_dict, log_name,
                 stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        """
        конструктор демона
        :param pidfile: путь к pid файлу, обязательный агрумент
        :param stdin: путь к файлу для хранения stdin, по умолчанию никуда не сохраняет
        :param stdout: путь к файлу для хранения stdout, по умолчанию никуда не сохраняет
        :param stderr: путь к файлу для хранения stderr, по умолчанию никуда не сохраняет
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.conf_dict = conf_dict
        self.log_name = log_name
        syslog.openlog(self.log_name)
        syslog.syslog(syslog.LOG_INFO, '{} Initialising security agent daemon'.format(datetime.datetime.now()))

    def daemonize(self):
        """
        производит UNIX double-form магию,
        Stevens "Advanced Programming in the UNIX Environment"
        for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            syslog.syslog(syslog.LOG_INFO, '{} fork #1 failed: {}'.format(datetime.datetime.now(), e.errno))
            sys.exit("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            syslog.syslog(syslog.LOG_INFO, '{} fork #2 failed: {}'.format(datetime.datetime.now(), e.errno))
            sys.exit("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))

            # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        syslog.syslog(syslog.LOG_INFO, '{} writing pid file'.format(datetime.datetime.now()))
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        syslog.syslog(syslog.LOG_INFO, '{} deleting pid file...'.format(datetime.datetime.now()))
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            syslog.syslog(syslog.LOG_INFO, '{} {}'.format(datetime.datetime.now(), message))
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        syslog.syslog(syslog.LOG_INFO, '{} starting daemon process pid: {}'.format(datetime.datetime.now(), pid))
        self.daemonize()
        self.run()

    sigDict = {}

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            syslog.syslog(syslog.LOG_INFO, '{} {}'.format(datetime.datetime.now(), message))
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        syslog.syslog(syslog.LOG_INFO, '{} restarting daemon process'.format(datetime.datetime.now()))
        self.stop()
        self.start()

    def run(self):
        with rabbit_listener.RabbitMQListener(self.conf_dict) as listener_obj:
            listener_obj.run()
