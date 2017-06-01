from tyr import resources
from tyr import serverutils

def main():

    print resources.strings.SRVR_START
    server = serverutils.q_server(resources.strings.FS_SRVR_CONF)
    server.start()
    print resources.strings.SRVR_INIT_DONE
