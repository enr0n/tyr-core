import os
import random
import subprocess
import shutil
import string
import logging
import logging.handlers
from ConfigParser import SafeConfigParser

from tyr import resources
from tyr import events

parser = SafeConfigParser()

log = logging.getLogger('test-utils')
log.setLevel(logging.DEBUG)
log.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

class compilers(object):

    @staticmethod
    def gcc(path, inputList, outputList, libsList):
        """ call the gcc compiler """

        # compiler name
        c = resources.strings.COMPILER_C
        err = ''
        # Execute the compiler
        for i in range(len(inputList)):
            cmd = c + ' -o ' + \
                os.path.join(path, outputList[i]) + \
                ' ' + os.path.join(path, inputList[i])
            cmd = cmd.split(' ')
            ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            err += ret
        return err

    @staticmethod
    def gpp(path, inputList, outputList, libsList):
        """ call the gpp compiler """

        # compiler name
        c = resources.strings.COMPILER_CPP
        err = ''
        # Execute the compiler
        for i in range(len(inputList)):
            cmd = c + ' -o ' + \
                os.path.join(path, outputList[i]) + \
                ' ' + os.path.join(path, inputList[i])
            for j in range(len(libsList)):
                cmd += ' --' + libsList[j]
            cmd = cmd.split(' ')
            try:
                ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                err += ret
            except subprocess.CalledProcessError as cpe:
                err += cpe.output
        return err


class controller(object):

    def __create_isolated_dir(self):
        """ create an isolated directory for the build """
        log.debug('Creating isolated directory: ' + self.test_id)

        path = os.path.join(self.path_testing, self.test_id)
        os.mkdir(path)

        err = subprocess.check_call(
            ['tar', 'xf', path + '.tar.gz', '-C', path, '--strip-components', '1'])
        self.path_testing = path

    def __get_testconf(self):
        """ get the test/build configuration """
        log.debug(os.path.join(self.path_testing, 'tyr.toml'))
        return os.path.join(self.path_testing, 'tyr.toml')

    def __init__(self, path_testing, test_id):
        log.info(resources.strings.TEST_INIT + test_id)

        self.path_testing = path_testing
        self.test_id = test_id

        self.__create_isolated_dir()

        self.testconf = self.__get_testconf()

    def __build(self, language, inputList, outputList, libsList):
        """ build the source """
        log.info(resources.strings.TEST_BUILD + self.test_id)

        inputList = inputList.split(',')
        outputList = outputList.split(',')
        libsList = libsList.split(',')

        # Call the compiler
        err = ''
        if language == resources.strings.LANG_C:
            err = compilers.gcc(self.path_testing,
                                inputList, outputList, libsList)
        elif language == resources.strings.LANG_CPP:
            err = compilers.gpp(self.path_testing,
                                inputList, outputList, libsList)
        else:
            print resources.strings.ERR_NO_LANG + language
        return err

    def __test(self, cmdList):
        """ execute the tests """
        log.info(resources.strings.TEST_EXEC + self.test_id)

        cmdList = cmdList.split(',')
        # Run the tests
        for i in range(len(cmdList)):
            cmd = os.path.join(self.path_testing, cmdList[i])
            cmd = cmd.split(' ')
            ret = subprocess.check_output(cmd)
        return ret

    def clean(self):
        """ clean the directory """
        path = os.path.normpath(os.path.join(self.path_testing, '..'))
        shutil.rmtree(path)

    def build_test(self):
        """ call __build with conf """
        parser.read(self.testconf)
        language = parser.get(resources.strings.CONF_BUILD,
                              resources.strings.CONF_LANG)
        inputs = parser.get(resources.strings.CONF_BUILD,
                            resources.strings.CONF_INPUT)
        outputs = parser.get(resources.strings.CONF_BUILD,
                             resources.strings.CONF_OUTPUT)
        libs = parser.get(resources.strings.CONF_BUILD,
                          resources.strings.CONF_LIBS)
        return self.__build(language, inputs, outputs, libs)

    def exec_test(self):
        """ call __test with conf """
        parser.read(self.testconf)
        cmdList = parser.get(resources.strings.CONF_TEST,
                             resources.strings.CONF_EXEC)
        return self.__test(cmdList)


class test_unit(object):

    def __init__(self, test_id, path_testing):
        log.debug('init:' + test_id)
        self.controller = controller(path_testing, test_id)
        self.test_id = test_id

    def run(self, do_compile, do_exec):
        """ run the build/test """
        output = ""
        if do_compile:
            print resources.strings.TEST_BUILD
            err = self.controller.build_test()
            if err:
                print resources.strings.ERR_BUILD_FAILED, err
                ebf = events.event_build_fail(err, self.test_id)
                ebf.trigger()
                do_exec = False

        if do_exec:
            print resources.strings.TEST_EXEC
            output = self.controller.exec_test()
            etd = events.event_test_done(output, self.test_id)
            etd.trigger()
