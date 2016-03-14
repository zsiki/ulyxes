#!/usr/bin/env python
"""
.. module:: webcam.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

from instrument import Instrument

class WebCam(Instrument):
    """ WebCam or video device

            :param name: name of instrument
            :param measureUnit: measure unit part of instrument 
            :param measureIface: interface to measure unit
            :param writerUnit: store data, default None
    """

    def __init__(self, name, measureUnit, measureIface, writerUnit = None):
        """ Constructor
        """
        # call super class init
        super(WebCam, self).__init__(name, measureUnit, measureIface, writerUnit)

    def GetImage(self):
        """ Get next image from stream
        """
        img = self.measureIface.GetImage()
        if img is not None and self.writerUnit is not None:
            self.writerUnit.WriteData(img)
        return img

if __name__ == "__main__":
    from videoiface import VideoIface
    #from picamiface import PiCamIface
    from videomeasureunit import VideoMeasureUnit
    from imagewriter import ImageWriter
    mu = VideoMeasureUnit()
    iface = VideoIface(source=0)
    #iface = PiCamIface()
    wrt = ImageWriter("test", "tmp")
    wc = WebCam('test', mu, iface, wrt)
    for i in range(2):
        wc.GetImage()
