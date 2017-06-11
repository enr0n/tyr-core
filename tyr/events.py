import sys
from pydispatch import dispatcher

from tyr import resources


class event_queue_test(object):

    def __init__(self, testconf):
        self.testconf = testconf

    def trigger(self):
        dispatcher.send(signal=resources.signals.SIG_INIT_TEST, sender=self)


class event_test_done(object):

    def __init__(self, output):
        self.output = output

    def trigger(self):
        dispatcher.send(signal=resources.signals.SIG_TEST_DONE, sender=self)


class event_build_fail(object):

    def __init__(self, err):
        self.err = err

    def trigger(self):
        dispatcher.send(signal=resources.signals.SIG_BUILD_FAIL, sender=self)
