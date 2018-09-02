#!/usr/bin/env python
"""
.. module:: camera.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor::  Bence Turak <bence.turak@gmail.com>
"""

import sys
#sys.path.append('../ulyxes/pyapi/')
import os
import cv2
from instrument import Instrument
from camcalibparams import CamCalibParams
from tcpiface import TCPIface

try:
    import picamera
except:
    pass

class Camera(Instrument):
    ''' Class for handle different camera unit

        :param name: name of instrument
        :param measureUnit: measure unit part of instrument
        :param measureIface: interface to physical unit
        :param writerUnit: store data, default None
    '''

    def __init__(self, name, measureUnit, measureIface = None, writerUnit = None):
        '''contructor
        '''
        super(Camera, self).__init__(name, measureUnit, measureIface, writerUnit)

        self.measureUnit = measureUnit
    def TakePhoto(self, pic, resolution = (480,720)):
        '''taking photo method

            :param name: name of image file
            :param resolution: resolution of picture (tuple)
        '''
        msg = self.measureUnit.TakePhotoMsg(pic, resolution)
        if isinstance(msg, str):
            return self._process(msg, pic)
        else:
            return msg
    def StartCameraView(self):
        '''Start Camera View method
        '''
        msg = self.measureUnit.StartCameraViewMsg()

        if msg['ret'] != 0:
            return self._process(msg)
        else:
            return msg['ret']

    def StopCameraView(self):
        '''Stop Camera View method
        '''

        msg = self.measureUnit.StopCameraViewMsg()

        if msg['ret'] != 0:
            return self._process(msg)
        else:
            return msg['ret']

    def GetContrast(self, mask = None):
        '''take picture and get contarst

            :returns: contrast of taken picture
        '''

        msg = self.measureUnit.GetContrastMsg(mask)

        if msg['ret'] != 0:
            return self._process(msg)
        else:
            return msg['contrast']
