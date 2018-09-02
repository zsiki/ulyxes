import sys
sys.path.append('ulyxes/pyapi')
sys.path.append('lib')
from totalstationrequesthandler import TotalStationRequestHandler
from leicatps1200 import LeicaTPS1200
from serialiface import SerialIface

import SocketServer
import threading


if __name__ == "__main__":

    #iface = SerialIface('test', '/dev/ttyUSB0')

    #mu = LeicaTPS1200()


    server = SocketServer.TCPServer(('192.168.1.102', 8081), TotalStationRequestHandler)

    server.serve_forever()

    #thread = threading.Thread(target=server.serve_forever)
    #thread.start()
