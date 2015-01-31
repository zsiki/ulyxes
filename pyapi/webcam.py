#!/usr/bin/env python
"""
.. module:: webcam.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

from instrument import Instrument

class WebCam(Instrument):
    """ WebCam or video device
    """

    def __init__(self, name, measureUnit, measureInterf, writerUnit = None):
        """ Constructor

            :param name: name of instrument
            :param measureUnit: measure unit part of instrument 
            :param measureInterf: interface to measure unit
            :param writerUnit: store data
        """
        # call super class init
        super(WebCam, self).__init__(name, measureUnit, measureInterf, writerUnit)

    def GetImage(self):
        """ Get next image from stream
        """
        img = self.measureInterf.GetImage()
        if img is not None and self.writerUnit is not None:
            self.writerUnit.WriteData(img)
        return img

if __name__ == "__main__":
    from videointerface import *
    from videomeasureunit import *
    from imagewriter import *
    mu = VideoMeasureUnit()
    iface = VideoInterface(source=0)
    wrt = ImageWriter("test", "tmp")
    wc = WebCam('test', mu, iface, wrt)
    wc.GetImage()
