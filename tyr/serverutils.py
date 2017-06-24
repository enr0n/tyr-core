import sys
import socket
import Queue
import logging
import logging.handlers
from threading import Thread
from ConfigParser import SafeConfigParser
from pydispatch import dispatcher

from tyr import resources
from tyr import events
from tyr import testutils

log = logging.getLogger('')
log.setLevel(logging.DEBUG)
log.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

class test_queue(object):
    """ queue for builds and tests """

    def __init__(self, q_size, path_testing):
        log.info("Initializing test queue")

        self.q_size = q_size
        self.test_queue = Queue.Queue(maxsize=q_size)
        self.path_testing = path_testing
        dispatcher.connect(
            self.__recv_test, signal=resources.signals.SIG_INIT_TEST, sender=dispatcher.Any)

    def __recv_test(self, sender):
        """ handle test received signal """
        if type(sender) is events.event_queue_test:
            log.info("Received queue request: " + sender.testconf)
            self.test_queue.put(sender.testconf)
        else:
            log.error(resources.strings.ERR_UNEXPECTED_OBJECT, sender)

    def __worker(self):
        """ queue worker """
        while True:
            next_test = self.test_queue.get()
            log.info("worker: initializing test unit for: " + next_test)
            t = testutils.test_unit(next_test, self.path_testing)
            t.run(True, True)
            self.test_queue.task_done()

    def start_daemon(self):
        """ start the worker """
        t = Thread(target=self.__worker)
        t.daemon = True
        t.start()


class q_server(object):

    def __init__(self):
        log.info("Initializing server")

        self.srvr_conf = resources.strings.FS_SRVR_CONF
        # Setup the server
        parser = SafeConfigParser()
        parser.read(self.srvr_conf)
        self.addr = parser.get(resources.strings.CONF_HOST,
                               resources.strings.CONF_ADDR)

        self.port = int(parser.get(resources.strings.CONF_HOST,
                                   resources.strings.CONF_PORT))

        self.q_size = int(parser.get(
            resources.strings.CONF_QUEUE, resources.strings.CONF_QSIZE))

        self.max_conns = int(parser.get(
            resources.strings.CONF_DATA, resources.strings.CONF_MAX_CONNS))

        self.buf_size = int(parser.get(
            resources.strings.CONF_DATA, resources.strings.CONF_BUF_SIZE))

        self.path_testing = parser.get(
            resources.strings.CONF_TESTING, resources.strings.CONF_PATH)

        dispatcher.connect(
            self.__send_output, signal=resources.signals.SIG_TEST_DONE, sender=dispatcher.Any)

        dispatcher.connect(
            self.__send_error, signal=resources.signals.SIG_BUILD_FAIL, sender=dispatcher.Any)

    def __send_output(self, sender):
        """ send output to client """
        if type(sender) is events.event_test_done:
            log.info("Sending output to client")
            self.conn.sendall(sender.output)
        else:
            log.error(resources.strings.ERR_UNEXPECTED_OBJECT, sender)
            sys.exit(-1)

    def __send_error(self, sender):
        """ send error to client """
        if type(sender) is events.event_build_fail:
            log.info("Sending error report to client")
            self.conn.sendall(sender.err)
        else:
            log.error(resources.strings.ERR_UNEXPECTED_OBJECT, sender)
            sys.exit(-1)

    def __create(self):
        """ create socket """
        self.tsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __bind_socket(self):
        """ bind socket """
        try:
            log.info("Binding socket: " +
                         str(self.addr) + ":" + str(self.port))
            self.tsocket.bind((self.addr, self.port))

        except socket.error as msg:
            log.error(resources.strings.ERR_SOCK_BIND + str(msg[0]))
            sys.exit(-1)

    def __init_queue(self):
        """ create test queue """
        tq = test_queue(self.q_size, self.path_testing)
        tq.start_daemon()

    def __socket_listen(self):
        """ listen for connections """
        try:
            self.tsocket.listen(self.max_conns)
            while True:
                self.conn, self.addr = self.tsocket.accept()
                testconf = self.conn.recv(self.buf_size)
                log.info(resources.strings.TEST_RECV_CONF + testconf)
                eqt = events.event_queue_test(testconf)
                eqt.trigger()

        except KeyboardInterrupt:
            log.info(resources.strings.EXCEP_KB_INT)
            self.tsocket.close()
            sys.exit(-1)

        finally:
            self.tsocket.close()

    def start(self):
        """ convenience method to start server """
        self.__create()
        self.__bind_socket()
        self.__init_queue()
        self.__socket_listen()
