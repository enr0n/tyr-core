import os
import sys
from ConfigParser import SafeConfigParser
from TyrRun import RunTest
from TyrResources import Strings
from TyrEvents import EventTestDone
from TyrEvents import EventBuildFail

parser = SafeConfigParser()

class TestControl(object):
    """
    TestControl is a class of static helper methods
    for a TestUnit to interface with a Loki instance

    Methods:
        buildTest - builds the source code

        execTest - executes the test units test cases
    """
    @staticmethod
    def buildTest(tester, testconf):
        parser.read(testconf)
        testdir = parser.get(Strings.CONF_FILES, Strings.CONF_DIR)
        language = parser.get(Strings.CONF_BUILD, Strings.CONF_LANG)
        inputs = parser.get(Strings.CONF_BUILD, Strings.CONF_INPUT)
        outputs = parser.get(Strings.CONF_BUILD, Strings.CONF_OUTPUT)
        libs = parser.get(Strings.CONF_BUILD, Strings.CONF_LIBS)
        return tester.build(testdir, language, inputs, outputs, libs)

    @staticmethod
    def execTest(tester, testconf):
        parser.read(testconf)
        testdir = parser.get(Strings.CONF_FILES, Strings.CONF_DIR)
        cmdList = parser.get(Strings.CONF_TEST, Strings.CONF_EXEC)
        return tester.test(testdir, cmdList)

class TestUnit(object):
    """
    TestUnit is an instance of a tyr test

    Methods:
        run - run the test unit

    """
    def __init__(self, testconf, path_testing):
        self.testconf = os.path.join(path_testing, os.path.basename(testconf))
        parser.read(self.testconf)
        self.tester = RunTest(path_testing)

    def run(self, do_compile, do_exec):
        output = ""
        if do_compile:
            print Strings.TEST_BUILD
            err = TestControl.buildTest(self.tester, self.testconf)
            if err:
                print Strings.ERR_BUILD_FAILED, err
                ebf = EventBuildFail(err)
                ebf.trigger()
                do_exec = False

        if do_exec:
            print Strings.TEST_EXEC
            output = TestControl.execTest(self.tester, self.testconf)
            etd = EventTestDone(output)
            etd.trigger()
