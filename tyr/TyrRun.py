import os
import random
import subprocess
from subprocess import call
from TyrResources import Strings
from TyrCompiler import TyrCompiler

class RunTest(object):

    def __init__(self, path_srvr):
        self.path_srvr = path_srvr

    def build(self, unit, language, inputList, outputList, libsList):
        """
        Compile all source in the test directory

        """
        inputList = inputList.split(",")
        outputList = outputList.split(",")
        libsList = libsList.split(",")

        path = os.path.join(self.path_srvr, unit)

        # Call the compiler
        err = ""
        if language == Strings.LANG_C:
            err = TyrCompiler.gcc(path, inputList, outputList, libsList)
        elif language == Strings.LANG_CPP:
            err = TyrCompiler.gpp(path, inputList, outputList, libsList)
        elif language == Strings.LANG_PYTHON:
            err = TyrCompiler.python(path, inputList)
        elif language == Strings.LANG_JAVA:
            err = TyrCompiler.java(path, inputList)
        else:
            print Strings.ERR_NO_LANG + language
        return err

    def test(self, unit, cmdList):
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
