#!/usr/bin/env python
"""
.. module:: picameraunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor::  Bence Turak <bence.turak@gmail.com>
"""
import sys
import cv2
import numpy as np
import os
#sys.path.append('../ulyxes/pyapi/')
from measureunit import MeasureUnit
try:
    import picamera
except Exception:
    pass
class PiCameraUnit(MeasureUnit):
    """ Picamera Unit for handle Picamera device

            :param name: name of measure unit (str), default None
            :param typ: type of measure unit (str), default None
    """

    def __init__(self, name = None, typ = None):
        """constructor
        """
        MeasureUnit.__init__(self, name, typ)
        self.cam = picamera.PiCamera()


    def TakePhotoMsg(self, pic, resolution = (720, 480)):
        """Take photo

            :param pic: writable binary file
            :param resolution: resolution of picture (tuple)
            :returns: dictionary contain picture in binary file
        """
        self.cam.resolution = resolution
        self.cam.capture(pic)
        return {'ret': {}, 'pic': pic}

    def StartCameraViewMsg(self):
        """Start camera preview

            :returns: empty dictionary
        """
        self.cam.start_preview()
        return {'ret': {}}

    def StopCameraViewMsg(self):
        """Stop camera preview

            :returns: empty dictionary
        """
        self.cam.stop_preview()
        return {'ret': {}}

    def GetContrastMsg(self, mask):
        """Get contrast of picture (beta)

            :param mask: picture mask
            :returns: contrast
        """
        picName = 'focus_pics/focusPic.png'
        self.TakePhotoMsg(picName)
        img = cv2.imread(picName)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean, dev = None, None
        if mask == None:
            size = gray.shape
            mask = np.zeros(gray.shape, dtype='uint8')
            cv2.rectangle(mask, (int(size[0]/2) - 10, int(size[1]/2) - 10), (int(size[0]/2) + 10, int(size[1]/2) + 10), 255, -1)

        mean, dev = cv2.meanStdDev(gray, mean, dev, mask)
        os.remove(picName)
        return {'ret': 0, 'contrast': dev[0][0]}

    def __del__(self):
        """destructor
        """
        self.cam.close()
