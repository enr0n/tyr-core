import sys
import Queue
from threading import Thread
from pydispatch import dispatcher
from TyrTest import TestUnit
from TyrEvents import EventQueueTest
from TyrResources import Strings
from TyrResources import Signals

class TestQueue(object):

    def __init__(self, q_size, path_testing):
        self.q_size = q_size
        self.test_queue = Queue.Queue(maxsize=q_size)
        self.path_testing = path_testing
        dispatcher.connect(self.__receiveTest, signal=Signals.SIG_INIT_TEST, sender=dispatcher.Any)

    def __receiveTest(self, sender):
        if type(sender) is EventQueueTest:
            self.test_queue.put(sender.testconf)
        else:
            print Strings.ERR_UNEXPECTED_OBJECT, sender

    def __worker(self):
        while True:
            next_test = self.test_queue.get()
            t = TestUnit(next_test, self.path_testing)
            # TODO:these need to be parameterized
            t.run(True, True)
            self.test_queue.task_done()

    def start_daemon(self):
        t = Thread(target=self.__worker)
        t.daemon = True
        t.start()
