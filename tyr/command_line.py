from tyr import resources
from tyr import serverutils

def main():

    print resources.strings.SRVR_START
    server = serverutils.q_server()
    server.start()
