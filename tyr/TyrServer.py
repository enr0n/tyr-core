import sys
import socket
from ConfigParser import SafeConfigParser
from pydispatch import dispatcher
# Tyr Imports
from TyrQueue import TestQueue
from TyrEvents import EventTestDone
from TyrEvents import EventQueueTest
from TyrEvents import EventBuildFail
from TyrResources import Strings
from TyrResources import Signals

class TyrServer(object):

    # Define attributes if needed
    def __init__(self, srvr_conf):
        self.srvr_conf = srvr_conf
        # Setup the server
        parser = SafeConfigParser()
        parser.read(self.srvr_conf)
        self.addr = parser.get(Strings.CONF_HOST, Strings.CONF_ADDR)
        self.port = int(parser.get(Strings.CONF_HOST, Strings.CONF_PORT))
        self.q_size = int(parser.get(Strings.CONF_QUEUE, Strings.CONF_QSIZE))
        self.max_conns = int(parser.get(Strings.CONF_DATA, Strings.CONF_MAX_CONNS))
        self.buf_size = int(parser.get(Strings.CONF_DATA, Strings.CONF_BUF_SIZE))
        self.path_testing = parser.get(Strings.CONF_TESTING, Strings.CONF_PATH)
        dispatcher.connect(self.__sendOutput, signal=Signals.SIG_TEST_DONE, sender=dispatcher.Any)
        dispatcher.connect(self.__sendError, signal=Signals.SIG_BUILD_FAIL, sender=dispatcher.Any)

    def __sendOutput(self, sender):
        if type(sender) is EventTestDone:
            self.conn.sendall(sender.output)
        else:
            print Strings.ERR_UNEXPECTED_OBJECT, sender
            sys.exit(-1)

    def __sendError(self, sender):
        if type(sender) is EventBuildFail:
            self.conn.sendall(sender.err)
        else:
            print Strings.ERR_UNEXPECTED_OBJECT, sender
            sys.exit(-1)

    def __create(self):
        self.tsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __bindSocket(self):
        try:
            self.tsocket.bind((self.addr, self.port))

        except socket.error as msg:
            print Strings.ERR_SOCK_BIND + str(msg[0])
            sys.exit(-1)

    def __socketListen(self):
        tq = TestQueue(self.q_size, self.path_testing)
        tq.start_daemon()
        try:
            self.tsocket.listen(self.max_conns)
            while True:
                self.conn, self.addr = self.tsocket.accept()
                testconf = self.conn.recv(self.buf_size)
                print Strings.TEST_RECV_CONF, testconf
                eqt = EventQueueTest(testconf)
                eqt.trigger()

        except KeyboardInterrupt:
            print Strings.EXCEP_KB_INT
            sys.exit(-1)

        finally:
            self.tsocket.close()

    def start(self):
        self.__create()
        self.__bindSocket()
        self.__socketListen()
