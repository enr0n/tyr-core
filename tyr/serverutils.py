import sys
import socket
import Queue
from threading import Thread
from ConfigParser import SafeConfigParser
from pydispatch import dispatcher

from tyr import resources
from tyr import events
from tyr import testutils

class test_queue(object):

    def __init__(self, q_size, path_testing):
        self.q_size = q_size
        self.test_queue = Queue.Queue(maxsize=q_size)
        self.path_testing = path_testing
        dispatcher.connect(self.__recv_test, signal=resources.signals.SIG_INIT_TEST, sender=dispatcher.Any)

    def __recv_test(self, sender):
        if type(sender) is events.event_queue_test:
            self.test_queue.put(sender.testconf)
        else:
            print resources.strings.ERR_UNEXPECTED_OBJECT, sender

    def __worker(self):
        while True:
            next_test = self.test_queue.get()
            t = testutils.test_unit(next_test, self.path_testing)
            t.run(True, True)
            self.test_queue.task_done()

    def start_daemon(self):
        t = Thread(target=self.__worker)
        t.daemon = True
        t.start()

class q_server(object):

    def __init__(self, srvr_conf):
        self.srvr_conf = srvr_conf
        # Setup the server
        parser = SafeConfigParser()
        parser.read(self.srvr_conf)
        self.addr = parser.get(resources.strings.CONF_HOST, resources.strings.CONF_ADDR)
        self.port = int(parser.get(resources.strings.CONF_HOST, resources.strings.CONF_PORT))
        self.q_size = int(parser.get(resources.strings.CONF_QUEUE, resources.strings.CONF_QSIZE))
        self.max_conns = int(parser.get(resources.strings.CONF_DATA, resources.strings.CONF_MAX_CONNS))
        self.buf_size = int(parser.get(resources.strings.CONF_DATA, resources.strings.CONF_BUF_SIZE))
        self.path_testing = parser.get(resources.strings.CONF_TESTING, resources.strings.CONF_PATH)
        dispatcher.connect(self.__send_output, signal=resources.signals.SIG_TEST_DONE, sender=dispatcher.Any)
        dispatcher.connect(self.__send_error, signal=resources.signals.SIG_BUILD_FAIL, sender=dispatcher.Any)

    def __send_output(self, sender):
        if type(sender) is events.event_test_done:
            self.conn.sendall(sender.output)
        else:
            print resources.strings.ERR_UNEXPECTED_OBJECT, sender
            sys.exit(-1)

    def __send_error(self, sender):
        if type(sender) is events.event_build_fail:
            self.conn.sendall(sender.err)
        else:
            print resources.strings.ERR_UNEXPECTED_OBJECT, sender
            sys.exit(-1)

    def __create(self):
        self.tsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __bind_socket(self):
        try:
            self.tsocket.bind((self.addr, self.port))

        except socket.error as msg:
            print resources.strings.ERR_SOCK_BIND + str(msg[0])
            sys.exit(-1)

    def __init_queue(self):
        tq = test_queue(self.q_size, self.path_testing)
        tq.start_daemon()

    def __socket_listen(self):
        try:
            self.tsocket.listen(self.max_conns)
            while True:
                self.conn, self.addr = self.tsocket.accept()
                testconf = self.conn.recv(self.buf_size)
                print resources.strings.TEST_RECV_CONF, testconf
                eqt = events.event_queue_test(testconf)
                eqt.trigger()

        except KeyboardInterrupt:
            print resources.strings.EXCEP_KB_INT
            self.tsocket.close()
            sys.exit(-1)

        finally:
            self.tsocket.close()

    def start(self):
        self.__create()
        self.__bind_socket()
        self.__init_queue()
        self.__socket_listen()
