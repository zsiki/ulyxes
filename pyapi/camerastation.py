#!/usr/bin/env python
"""
.. module:: camerastation.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Bence Turak <bence.turak@gmail.com>
"""

import sys
#sys.path.append('ulyxes/pyapi/')
#sys.path.append('lib/')
from totalstation import TotalStation
#from serialiface import SerialIface
from camera import Camera
#from steppermotor import StepperMotor
from imgprocess import ImgProcess
import numpy as np
import os
import cv2
import recognition as rec
from angle import Angle
import math
import time


class CameraStation(TotalStation, Camera):
    '''CameraStation class for TotalStation combinated with camera

        :param name: name of instrument
        :param measureUnit: measure unit part of instrument
        :param measureIface: interface to physical unit
        :param writerUnit: store data, default None
    '''
    #constants
    #FOCUS_CLOSER = 1
    #FOCUS_FARTHER = 2

    def __init__(self, name, measureUnit, measureIface, writerUnit = None):
        '''constructor
        '''
        TotalStation.__init__(self, name, measureUnit, measureIface, writerUnit)
        Camera.__init__(self, name, measureUnit, measureIface, writerUnit)
        #StepperMotor.__init__(self, stepperMotorUnit, speed, halfSteps)


        self._affinParams = None

    def LoadAffinParams(self, file):
        """Load affin params to measure on pictures

            :param file: name of the params file (It have to be .npy file)
        """
        self._affinParams = np.load(file)

    def PicMes(self, photoName, targetType = None):
        '''Measure angles between the target and the optical axis
            :param photoName: name of the photo
            :param targetType: type of the target
            :returns: horizontal (hz) and vertical (v) correction angle in dictionary
        '''

        ok = False
        while not ok:
            print(photoName)
            file = open(photoName, 'w+b')
            print((int(self._affinParams[0,3]), int(self._affinParams[1,3])))

            ang = self.GetAngles()
            self.TakePhoto(file, (int(self._affinParams[0,3]), int(self._affinParams[1,3])))

            file.close()

            try:

                img = cv2.imread(photoName, 1)
                picCoord = rec.recogChessPattern(img)
                print(picCoord)
                ok = True
            except:
                pass

        img[int(picCoord[1]),:] = [0,255,255]
        img[:,int(picCoord[0])] = [0,255,255]

        cv2.imwrite(photoName, img)
        angles = {}
        angles['hz'] = Angle(1/math.sin(ang['v'].GetAngle('RAD'))*(self._affinParams[0,1]*(picCoord[0] - round(self._affinParams[0,0])) + self._affinParams[0,2]*(picCoord[1] - round(self._affinParams[1,0]))))
        angles['v'] = Angle(self._affinParams[1,1]*(picCoord[0] - round(self._affinParams[0,0])) + self._affinParams[1,2]*(picCoord[1] - round(self._affinParams[1,0])))

        return angles

    def GetAbsAngles(self, targetType = None):
        """Get absolute angles with automatical target recognition (not prism)

            :param targetType: type of target (None)
            :returns: corrected horinzontas (hz) and vertical (v) angles in dictionary. It contains the last correction angles too.

        """

        t = time.localtime()
        picName = str(t.tm_year) + '_' + str(t.tm_mon) + '_' + str(t.tm_mday) + '_' + str(t.tm_hour) + '_' + str(t.tm_min) + '_' + str(t.tm_sec) + '.png'

        corr = self.PicMes(picName)
        ang = self.GetAngles()

        angles = {}
        angles['hz'] = ang['hz'] - corr['hz']
        angles['v'] = ang['v'] - corr['v']
        angles['chz'] = corr['hz']
        angles['cv'] = corr['v']
        i = 0

        print('hz:', corr['hz'].GetAngle('SEC'))
        print('v:', corr['v'].GetAngle('SEC'))

        while abs(corr['hz'].GetAngle('SEC')) > 6 or abs(corr['v'].GetAngle('SEC')) > 6:



            self.Move(angles['hz'], angles['v'])

            corr = self.PicMes(picName)
            ang = self.GetAngles()
            print('hz:', corr['hz'].GetAngle('SEC'))
            print('v:', corr['v'].GetAngle('SEC'))
            angles = {}
            angles['hz'] = ang['hz'] - corr['hz']
            angles['v'] = ang['v'] - corr['v']
            angles['chz'] = corr['hz']
            angles['cv'] = corr['v']
            print(i)
            i += 1
        return angles

    def FollowTarget(self):
        """Following target (beta)

        """
        t = time.localtime()
        picName = str(t.tm_year) + '_' + str(t.tm_mon) + '_' + str(t.tm_mday) + '_' + str(t.tm_hour) + '_' + str(t.tm_min) + '_' + str(t.tm_sec) + '.png'

        i = 0

        while True:

            corr = self.PicMes(picName)
            ang = self.GetAngles()
            print('hz:', corr['hz'].GetAngle('SEC'))
            print('v:', corr['v'].GetAngle('SEC'))
            angles = {}
            angles['hz'] = ang['hz'] - corr['hz']
            angles['v'] = ang['v'] - corr['v']
            print(i)
            i += 1
            if abs(corr['hz'].GetAngle('SEC')) > 6 or abs(corr['v'].GetAngle('SEC')) > 6 :
                self.Move(angles['hz'], angles['v'])


        return angles

    def __del__(self):
        '''destructor
        '''
        pass
