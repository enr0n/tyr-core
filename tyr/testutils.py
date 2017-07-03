import os
import random
import subprocess
import shutil
import string
import logging
import logging.handlers
import ConfigParser

from tyr import resources
from tyr import events

parser = ConfigParser.SafeConfigParser()

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
        for f_in, f_out in zip(inputList, outputList):
            cmd = c + ' -o ' + \
                os.path.join(path, f_out) + \
                ' ' + os.path.join(path, f_in)

            # Add libs to command
            for lib in libsList:
                cmd += ' --' + lib

            # Create list to pass to subprocess
            cmd = cmd.split(' ')
            try:
                ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                err += ret
            except subprocess.CalledProcessError as cpe:
                err += cpe.output
        return err

    @staticmethod
    def gpp(path, inputList, outputList, libsList):
        """ call the gpp compiler """

        # compiler name
        c = resources.strings.COMPILER_CPP
        err = ''
        # Execute the compiler
        for f_in, f_out in zip(inputList, outputList):
            cmd = c + ' -o ' + \
                os.path.join(path, f_out) + \
                ' ' + os.path.join(path, f_in)

            # Add libs to command
            for lib in libsList:
                cmd += ' --' + lib

            # Create list to pass to subprocess
            cmd = cmd.split(' ')
            try:
                ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                err += ret
            except subprocess.CalledProcessError as cpe:
                err += cpe.output
        return err


class controller(object):

    def _create_isolated_dir(self):
        """ create an isolated directory for the build """
        log.debug('Creating isolated directory: ' + self.test_id)

        path = os.path.join(self.path_testing, self.test_id)
        os.mkdir(path)

        err = subprocess.check_call(
            ['tar', 'xf', path + '.tar.gz', '-C', path, '--strip-components', '1'])
        self.path_testing = path

    def _get_testconf(self):
        """ get the test/build configuration """
        log.debug(os.path.join(self.path_testing, 'tyr.toml'))
        return os.path.join(self.path_testing, 'tyr.toml')

    def __init__(self, path_testing, test_id):
        log.info(resources.strings.TEST_INIT + test_id)

        self.path_testing = path_testing
        self.test_id = test_id

        self._create_isolated_dir()

        self.testconf = self._get_testconf()

    def _build(self, language, inputList, outputList, libsList):
        """ build the source """
        log.info(resources.strings.TEST_BUILD + self.test_id)

        inputList = inputList.split(',')
        outputList = outputList.split(',')
        if libsList:
            libsList = libsList.split(',')


        compiler = { resources.strings.LANG_C: compilers.gcc,
                     resources.strings.LANG_CPP: compilers.gpp }
        # Call the compiler
        err = ''
        try:
            err = compiler[language](self.path_testing,
                                     inputList,
                                     outputList,
                                     libsList)
        except KeyError:
            log.error(resources.strings.ERR_NO_LANG + language)
            err = resources.strings.ERR_NO_LANG + language

        return err

    def _test(self, cmdList):
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
        """ call _build with conf """
        try:
            parser.read(self.testconf)
            language = parser.get(resources.strings.CONF_BUILD,
                                  resources.strings.CONF_LANG)
            inputs = parser.get(resources.strings.CONF_BUILD,
                                resources.strings.CONF_INPUT)
            outputs = parser.get(resources.strings.CONF_BUILD,
                                 resources.strings.CONF_OUTPUT)
            libs = parser.get(resources.strings.CONF_BUILD,
                              resources.strings.CONF_LIBS)
            return self._build(language, inputs, outputs, libs)

        except ConfigParser.NoSectionError as nse:
            log.error(str(nse))
            return str(nse)

        except ConfigParser.NoOptionError as noe:
            log.error(str(noe))
            return str(noe)

    def exec_test(self):
        """ call _test with conf """
        try:
            parser.read(self.testconf)
            cmdList = parser.get(resources.strings.CONF_TEST,
                                 resources.strings.CONF_EXEC)
            return self._test(cmdList)

        except ConfigParser.NoSectionError as nse:
            log.error(str(nse))
            return str(nse)

        except ConfigParser.NoOptionError as noe:
            log.error(str(noe))
            return str(noe)

class test_unit(object):

    def __init__(self, test_id, path_testing):
        log.debug('init:' + test_id)
        self.controller = controller(path_testing, test_id)
        self.test_id = test_id

    def run(self, do_compile, do_exec):
        """ run the build/test """
        output = ""
        if do_compile:
            err = self.controller.build_test()
            if err:
                log.error(resources.strings.ERR_BUILD_FAILED + err)
                ebf = events.event_build_fail(err, self.test_id)
                ebf.trigger()
                do_exec = False

        if do_exec:
            log.info(resources.strings.TEST_EXEC)
            output = self.controller.exec_test()
            etd = events.event_test_done(output, self.test_id)
            etd.trigger()
