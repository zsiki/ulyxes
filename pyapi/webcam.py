#!/usr/bin/env python
"""
.. module:: measureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>. This module depends on OpenCV
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""

#TODO move to interface!

import cv

class VideoMeasureUnit(MeasureUnit):
    """ Read from video stream or video file
    """
    def __init__(self, name = 'webcam', typ = 'video', source = 0):
        """ Constructor

            :param name: name of measure unit
            :param typ: type of measure unit
            :param source: id of device or file name
        """
        super(VideoMeasureUnit).__init__(name, typ)
        if type(source) is int:
            # video device source
            self.video = cv.CaptureFromCAM(source)
            # TODO error handlig
        else:
            # video device source TODO
            pass

    def __del__(self):
        """ Destructor
        """
        self.video.release()
        
    def Measure(self):
        """ Get a frame from video stream/file

for i in range(10):
    img = cv.QueryFrame(video)
    cv.SaveImage(str(i)+".png", img)
video.release()
