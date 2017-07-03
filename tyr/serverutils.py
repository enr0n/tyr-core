import os
import sys
import socket
import Queue
import logging
import logging.handlers
import ConfigParser
from threading import Thread
from pydispatch import dispatcher

from tyr import resources
from tyr import events
from tyr import testutils

log = logging.getLogger('server-utils')
log.setLevel(logging.DEBUG)
log.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

class test_queue(object):
    """ queue for builds and tests """

    def __init__(self, q_size, path_testing):
        log.info(resources.strings.Q_INIT)

        self.q_size = q_size
        self.test_queue = Queue.Queue(maxsize=q_size)
        self.path_testing = path_testing
        dispatcher.connect(self._recv_test,
                           signal=resources.signals.SIG_INIT_TEST,
                           sender=dispatcher.Any)

    def _recv_test(self, sender):
        """ handle test received signal """
        if type(sender) is events.event_queue_test:
            log.info(resources.strings.Q_RECV + sender.test_id)
            self.test_queue.put(sender.test_id)
        else:
            log.error(resources.strings.ERR_UNEXPECTED_OBJECT, sender)

    def _worker(self):
        """ queue worker """
        while True:
            next_test = self.test_queue.get()
            try:
                log.info(resources.strings.WORKER_INIT + next_test)
                t = testutils.test_unit(next_test, self.path_testing)
                t.run(True, True)
                self.test_queue.task_done()
            except:
                eue = events.event_uncaught_exception(next_test)
                eue.trigger()

    def start_daemon(self):
        """ start the worker """
        t = Thread(target=self._worker)
        t.daemon = True
        t.start()

class q_server(object):

    def __init__(self):

        # Dictionary for test's socket
        self.conns = {}

        self.srvr_conf = resources.strings.FS_SRVR_CONF
        # Setup the server
        self._config_server()

        # Setup event handlers
        dispatcher.connect(self._send_output,
                           signal=resources.signals.SIG_TEST_DONE,
                           sender=dispatcher.Any)

        dispatcher.connect(self._send_error,
                           signal=resources.signals.SIG_BUILD_FAIL,
                           sender=dispatcher.Any)

        dispatcher.connect(self._notify_exception,
                           signal=resources.signals.SIG_UNCAUGHT_EXCEP,
                           sender=dispatcher.Any)

    def _config_server(self):
        """ get settings from config """

        # Check for server config
        if not os.path.isfile(self.srvr_conf):
            log.error(resources.strings.ERR_NO_CONF)
            sys.stderr.write(resources.strings.ERR_NO_CONF)
            sys.exit(-1)

        # Parse the config file
        parser = ConfigParser.SafeConfigParser()
        try:
            parser.read(self.srvr_conf)
            self.addr = parser.get(resources.strings.CONF_HOST,
                                   resources.strings.CONF_ADDR)

            self.port = int(parser.get(resources.strings.CONF_HOST,
                                       resources.strings.CONF_PORT))

            self.q_size = int(parser.get(resources.strings.CONF_QUEUE,
                                         resources.strings.CONF_QSIZE))

            self.max_conns = int(parser.get(resources.strings.CONF_DATA,
                                            resources.strings.CONF_MAX_CONNS))

            self.buf_size = int(parser.get(resources.strings.CONF_DATA,
                                           resources.strings.CONF_BUF_SIZE))

            self.path_testing = parser.get(resources.strings.CONF_TESTING,
                                           resources.strings.CONF_PATH)

        except ConfigParser.NoSectionError as nse:
            log.error(str(nse))
            sys.stderr.write(str(nse)+'\n')
            sys.exit(-1)

        except ConfigParser.NoOptionError as noe:
            log.error(str(noe))
            sys.stderr.write(str(noe)+'\n')
            sys.exit(-1)

    def _notify_exception(self, sender):
        """ notify client of unhandled exception """
        if type(sender) is events.event_uncaught_exception:
            log.info(sender.err)
            self.conns[sender.test_id].sendall(sender.err)

            # Remove connection from dictionary
            del self.conns[sender.test_id]
        else:
            log.error(resources.strings.ERR_UNEXPECTED_OBJECT, sender)

    def _send_output(self, sender):
        """ send output to client """
        if type(sender) is events.event_test_done:
            log.info(resources.strings.TEST_SEND_OUT)
            self.conns[sender.test_id].sendall(sender.output)

            # Remove connection from dictionary
            del self.conns[sender.test_id]
        else:
            log.error(resources.strings.ERR_UNEXPECTED_OBJECT, sender)
            sys.exit(-1)

    def _send_error(self, sender):
        """ send error to client """
        if type(sender) is events.event_build_fail:
            log.info(resources.strings.TEST_SEND_ERR)
            self.conns[sender.test_id].sendall(sender.err)

            # Remove connection froms dictionary
            del self.conns[sender.test_id]
        else:
            log.error(resources.strings.ERR_UNEXPECTED_OBJECT, sender)
            sys.exit(-1)

    def _create_sock(self):
        """ create socket """
        self.tsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _bind_socket(self):
        """ bind socket """
        try:
            log.debug('Binding socket: ' +
                         str(self.addr) + ':' + str(self.port))
            self.tsocket.bind((self.addr, self.port))

        except socket.error as msg:
            log.error(resources.strings.ERR_SOCK_BIND + str(msg[0]))
            sys.exit(-1)

    def _init_queue(self):
        """ create test queue """
        tq = test_queue(self.q_size, self.path_testing)
        tq.start_daemon()

    def _socket_listen(self):
        """ listen for connections """
        try:
            self.tsocket.listen(self.max_conns)
            while True:
                conn, addr = self.tsocket.accept()

                test_id = conn.recv(self.buf_size)
                self.conns[test_id] = conn

                log.info(resources.strings.TEST_RECV_CONF + test_id)

                eqt = events.event_queue_test(test_id)
                eqt.trigger()

        except KeyboardInterrupt:
            log.info(resources.strings.EXCEP_KB_INT)
            self.tsocket.close()
            sys.exit(-1)

        finally:
            self.tsocket.close()

    def start(self):
        """ convenience method to start server """
        self._create_sock()
        self._bind_socket()
        self._init_queue()
        self._socket_listen()
