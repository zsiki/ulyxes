#import total
import sys
sys.path.append('../ulyxes/pyapi/')
sys.path.append('lib/')
from totalstation import TotalStation
from totalstationclient import TotalStationClient
from serialiface import SerialIface
from leicatcra1100 import LeicaTCRA1100
from leicatps1200 import LeicaTPS1200
from leicameasureunit import LeicaMeasureUnit
from stationcommands import StationCommands
from remotemeasureunit import RemoteMeasureUnit
from picameraunit import PiCameraUnit
from camerastation import CameraStation
import time
import cv2
import numpy as np


class CameraStationUnit(PiCameraUnit, LeicaTPS1200): pass


import SocketServer
import json

#iface = SerialIface('test', '/dev/ttyUSB0')
#ts = TotalStation('test', LeicaTPS1200(), iface)

class TotalStationRequestHandler(SocketServer.StreamRequestHandler):
    '''TCP request handler for total stations remote controll

    '''


    def handle(self):
        #mu = LeicaTPS1200()
        mu = CameraStationUnit()
        iface = SerialIface('test', '/dev/ttyUSB0')

        ts = CameraStation('test', mu, iface)
        #ts = TotalStation('test', mu, iface)

        while True:
            print('--------------')
            msg = self.request.recv(1024)

            print(msg)

            ans, file = RemoteMeasureUnit.execCmd(ts, msg)

            print(ans,'///')

            self.wfile.write(ans + b'\n')

            if file != None:
                print('???????')


                file.seek(0)
                l = 0
                aaa = file.read(1024)
                l += self.request.send(aaa)
                while aaa:
                    aaa = file.read(1024)
                    l += self.request.send(aaa)

                print('binary is sent')


    def setNewStation(self, station):
        if isinstance(station, TotalStation):
            self.server.stations.append(station)





    #def processRequest(self):
        #pass
