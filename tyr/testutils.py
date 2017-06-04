import os
import random
import subprocess
import shutil
import string
from ConfigParser import SafeConfigParser

from tyr import resources
from tyr import events

parser = SafeConfigParser()

class compilers(object):
    """
    Each method in the compiler class is meant to
    emulate a different compiler. New methods can
    be added here to support new languages

    """
    @staticmethod
    def gcc(path, inputList, outputList, libsList):
        # compiler name
        c = resources.strings.COMPILER_C
        err = ""
        # Execute the compiler
        for i in range(len(inputList)):
            cmd = c + " -o " + os.path.join(path, outputList[i]) + " " + os.path.join(path, inputList[i])
            cmd = cmd.split(" ")
            ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            err += ret
        return err

    @staticmethod
    def gpp(path, inputList, outputList, libsList):
        # compiler name
        c = resources.strings.COMPILER_CPP
        err = ""
        # Execute the compiler
        for i in range(len(inputList)):
            cmd = c + " -o " + os.path.join(path, outputList[i]) + " " + os.path.join(path, inputList[i])
            for j in range(len(libsList)):
                cmd += " --" + libsList[j]
            cmd = cmd.split(" ")
            try:
                ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                err += ret
            except subprocess.CalledProcessError as cpe:
                err += cpe.output
        return err

class controller(object):

    def __init__(self, target):
        self.target = target

    def __gen_id(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    def __mkdir_target(self):
        id_test = 'test_' + self.__gen_id()
        target_new = os.path.join(self.target, id_test)
        os.mkdir(target_new)
        return target_new

    def __create_isolated_directory(self, unit):
        t = os.path.join(self.target, unit)
        self.target = self.__mkdir_target()
        self.target = os.path.join(self.target)
        os.rename(t, self.target)

    def __build(self, unit, language, inputList, outputList, libsList):
        """
        Compile all source in the test directory

        """
        inputList = inputList.split(",")
        outputList = outputList.split(",")
        libsList = libsList.split(",")

        # Set up isolated directory (modifies attribute 'target')
        self.__create_isolated_directory(unit)

        # Call the compiler
        err = ""
        if language == resources.strings.LANG_C:
            err = compilers.gcc(self.target, inputList, outputList, libsList)
        elif language == resources.strings.LANG_CPP:
            err = compilers.gpp(self.target, inputList, outputList, libsList)
        else:
            print resources.strings.ERR_NO_LANG + language
        return err

    def __test(self, unit, cmdList):
        """
        Run the specified tests

        """
        cmdList = cmdList.split(",")
        # Run the tests
        for i in range(len(cmdList)):
            cmd = os.path.join(self.target, cmdList[i])
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
        self.path_testing = path_testing
        self.testconf = os.path.join(self.path_testing, os.path.basename(testconf))
        parser.read(self.testconf)
        self.controller = controller(path_testing)

    def run(self, do_compile, do_exec):
        output = ""
        if do_compile:
            print resources.strings.TEST_BUILD
            err = self.controller.build_test(self.testconf)
            if err:
                print resources.strings.ERR_BUILD_FAILED, err
                ebf = events.event_build_fail(err)
                ebf.trigger()
                do_exec = False

        if do_exec:
            print resources.strings.TEST_EXEC
            output = self.controller.exec_test(self.testconf)
            etd = events.event_test_done(output)
            etd.trigger()
