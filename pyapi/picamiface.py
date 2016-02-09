#!/usr/bin/env python
"""
.. module:: picamiface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""

from picamera.array import PiRGBArray
from picamera import PiCamera
import logging
from iface import Iface

class PiCamIface(Iface):
    """ Read from raspberry pi camera.

            :param name: name of interface (str), default 'picam'
            :param source: id of device, dummy not used yet, default = 0
    """
    def __init__(self, name = 'picam', source = 0):
        """ Constructor
        """
        super(PiCamIface, self).__init__(name)
        self.source = source
        self.video = None
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera)

    def __del__(self):
        """ Destructor
        """
        self.camera.close()

    def GetImage(self):
        """ Get image from stream

            :returns: an image or None
        """
        if self.state == self.IF_OK:
            self.camera.capture(self.rawCapture, format="bgr")
            img = self.rawCapture.array
            if img is None:
                self.state = self.IF_EOF
                logging.warning(" eof on video source")
            return img
        return None

if __name__ == "__main__":
    stream = PiCamIface()
    if stream.state != stream.IF_OK:
        print ("error opening video stream")
    else:
        im = stream.GetImage()
        print (type(im))
        print (len(im))
