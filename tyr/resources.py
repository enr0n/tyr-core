class strings(object):
    """
    This class contains a collection of string literals
    used throughout tyr core

    """
    # Filesystem
    FS_SRVR_CONF = "/etc/tyr/conf"

    # Logging
    LOG_DATE = '%m/%d/%Y %I:%M:%S %p'
    LOG_FORMAT = '%(asctime)s %(levelname)s:%(message)s'

    # Compilers
    COMPILER_PYTHON = "python"
    COMPILER_C = "gcc"
    COMPILER_CPP = "g++"
    COMPILER_JAVA = "javac"

    # Languages
    LANG_PYTHON = "python"
    LANG_C = "c"
    LANG_CPP = "c++"
    LANG_JAVA = "java"

    # Server statuses
    SRVR_START = "Starting tyr server..."
    SRVR_INIT_DONE = "Server initialization complete."

    # Test statuses
    TEST_BUILD = "Building source."
    TEST_EXEC = "Executing tests."
    TEST_RECV_CONF = "Received test configuration "
    TEST_COMPLETE = "Test completed."

    # Error statuses
    ERR_NO_LANG = "Error: no language matches "
    ERR_DIR_NOT_FOUND = "Error: directory not found"
    ERR_OPT_ITER = "Error: iterations must be greater than 1"
    ERR_OPT_COMP_ONLY = "Error: compile only cannot be used with option -E"
    ERR_OPT_EXEC_ONLY = "Error: execute only cannot be used with option -C"
    ERR_SFTP = "Error: failed sending files to server"
    ERR_UNEXPECTED_OBJECT = "Error: received unexpected object: "
    ERR_SOCK_BIND = "Error: could not bind socket: "
    ERR_BUILD_FAILED = "Error: builed failed: "

    # Exceptions
    EXCEP_KB_INT = "User interrupted server"

    # Conf strings
    CONF_LOKI = "loki"
    CONF_ADDR = "address"
    CONF_USER = "username"
    CONF_RPATH = "remotepath"
    CONF_FILES = "files"
    CONF_DIR = "testdir"
    CONF_BUILD = "build"
    CONF_LANG = "language"
    CONF_INPUT = "input"
    CONF_OUTPUT = "output"
    CONF_TEST = "test"
    CONF_EXEC = "exec"
    CONF_LIBS = "libs"

    # Server conf strings
    CONF_HOST = "host"
    CONF_PORT = "port"
    CONF_QSIZE = "size"
    CONF_QUEUE = "queue"
    CONF_QMAX = "max_tests"
    CONF_TESTING = "testing"
    CONF_PATH = "path"
    CONF_DATA = "data"
    CONF_BUF_SIZE = "buf_size"
    CONF_MAX_CONNS = "max_conns"


class signals(object):

    SIG_INIT_TEST = "INIT_TEST"
    SIG_TEST_DONE = "TEST_DONE"
    SIG_BUILD_FAIL = "BUILD_FAIL"
