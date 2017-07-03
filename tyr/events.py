import sys
from pydispatch import dispatcher

from tyr import resources


class event_queue_test(object):

    def __init__(self, test_id):
        self.test_id = test_id

    def trigger(self):
        dispatcher.send(signal=resources.signals.SIG_INIT_TEST, sender=self)


class event_test_done(object):

    def __init__(self, output, test_id):
        self.output = output
        self.test_id = test_id

    def trigger(self):
        dispatcher.send(signal=resources.signals.SIG_TEST_DONE, sender=self)


class event_build_fail(object):

    def __init__(self, err, test_id):
        self.err = err
        self.test_id = test_id

    def trigger(self):
        dispatcher.send(signal=resources.signals.SIG_BUILD_FAIL, sender=self)

class event_uncaught_exception(object):

    def __init__(self, test_id):
        self.test_id = test_id
        self.err = (resources.strings.ERR_UNCAUGHT_EXCEP % self.test_id)

    def trigger(self):
        dispatcher.send(signal=resources.signals.SIG_UNCAUGHT_EXCEP, sender=self)
