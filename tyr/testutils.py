import os
import random
import subprocess
from ConfigParser import SafeConfigParser

from tyr import resources
from tyr import events

parser = SafeConfigParser()

class controller(object):

    def __init__(self, path_srvr):
        self.path_srvr = path_srvr

    def __build(self, unit, language, inputList, outputList, libsList):
        """
        Compile all source in the test directory

        """
        inputList = inputList.split(",")
        outputList = outputList.split(",")
        libsList = libsList.split(",")

        path = os.path.join(self.path_srvr, unit)

        # Call the compiler
        err = ""
        if language == resources.strings.LANG_C:
            err = TyrCompiler.gcc(path, inputList, outputList, libsList)
        elif language == resources.strings.LANG_CPP:
            err = TyrCompiler.gpp(path, inputList, outputList, libsList)
        elif language == resources.strings.LANG_PYTHON:
            err = TyrCompiler.python(path, inputList)
        elif language == resources.strings.LANG_JAVA:
            err = TyrCompiler.java(path, inputList)
        else:
            print resources.strings.ERR_NO_LANG + language
        return err

    def __test(self, unit, cmdList):
        """
        Run the specified tests

        """
        path = os.path.join(self.path_srvr, unit)
        cmdList = cmdList.split(",")
        # Run the tests
        for i in range(len(cmdList)):
            cmd = os.path.join(path, cmdList[i])
            cmd = cmd.split(" ")
            ret = subprocess.check_output(cmd)
        return ret

    def build_test(self, testconf):
        """
        Build the test based on
        testconf

        """
        parser.read(testconf)
        testdir = parser.get(resources.strings.CONF_FILES, resources.strings.CONF_DIR)
        language = parser.get(resources.strings.CONF_BUILD, resources.strings.CONF_LANG)
        inputs = parser.get(resources.strings.CONF_BUILD, resources.strings.CONF_INPUT)
        outputs = parser.get(resources.strings.CONF_BUILD, resources.strings.CONF_OUTPUT)
        libs = parser.get(resources.strings.CONF_BUILD, resources.strings.CONF_LIBS)
        return self.__build(testdir, language, inputs, outputs, libs)

    def exec_test(self, testconf):
        """
        Execute the test based on
        testconf

        """
        parser.read(testconf)
        testdir = parser.get(resources.strings.CONF_FILES, resources.strings.CONF_DIR)
        cmdList = parser.get(resources.strings.CONF_TEST, resources.strings.CONF_EXEC)
        return self.__test(testdir, cmdList)

class test_unit(object):

    def __init__(self, testconf, path_testing):
        self.testconf = os.path.join(path_testing, os.path.basename(testconf))
        parser.read(self.testconf)
        self.controller = controller(path_testing)

    def run(self, do_compile, do_exec):
        output = ""
        if do_compile:
            print resources.strings.TEST_BUILD
            err = self.controller.build_test(self.testconf)
            if err:
                print resources.strings.ERR_BUILD_FAILED, err
                ebf = events.EventBuildFail(err)
                ebf.trigger()
                do_exec = False

        if do_exec:
            print resources.strings.TEST_EXEC
            output = self.controller.exec_test(self.testconf)
            etd = events.EventTestDone(output)
            etd.trigger()
