import os
import random
import subprocess
import tarfile
from TyrResources import Strings
from subprocess import call

class TyrCompiler(object):
    """
    Each method in the compiler class is meant to
    emulate a different compiler. New methods can
    be added here to support new languages

    """
    @staticmethod
    def gcc(path, inputList, outputList, libsList):
        # compiler name
        c = Strings.COMPILER_C
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
        c = Strings.COMPILER_CPP
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
    @staticmethod
    def python(path, inputList):
        # compiler name
        c = Strings.COMPILER_PYTHON
        err = 0
        # Execute the compiler
        for i in range(len(inputList)):
            cmd = c + " " + os.path.join(path, inputList[i])
            cmd = cmd.split(" ")
            ret = subprocess.call(cmd)
            err += ret
        return err

    @staticmethod
    def java(path, inputList):
        #compiler name
        c = Strings.COMPILER_JAVA
        err = 0
        # Execute the compiler
        for i in range(len(inputList)):
            # Change the directory so that jvm can find
            # the other classes
            cmd = "cd " + path + " && " + c + " " + os.path.join(path, inputList[i])
            cmd = cmd.split(" ")
            ret = subprocess.call(cmd)
            err += ret
        return err
