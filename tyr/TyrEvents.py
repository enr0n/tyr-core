import sys
from pydispatch import dispatcher
# Tyr imports
from TyrResources import Signals

class EventQueueTest(object):

    def __init__(self, testconf):
        self.testconf = testconf

    def trigger(self):
        dispatcher.send(signal=Signals.SIG_INIT_TEST, sender=self)

class EventTestDone(object):

    def __init__(self, output):
        self.output = output

    def trigger(self):
        dispatcher.send(signal=Signals.SIG_TEST_DONE, sender=self)

class EventBuildFail(object):

    def __init__(self, err):
        self.err = err

    def trigger(self):
        dispatcher.send(signal=Signals.SIG_BUILD_FAIL, sender=self)
