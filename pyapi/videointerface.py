#!/usr/bin/env python
"""
.. module:: videointeface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>. This module depends on OpenCV.
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""

import cv
import os.path
from interface import Interface

class VideoInterface(Interface):
    """ Read from video stream or video file
    """
    def __init__(self, name = 'webcam', source = 0):
        """ Constructor

            :param name: name of interface
            :param source: id of device or file name
        """
        super(VideoInterface, self).__init__(name)
        self.source = source
        self.video = None
        if type(source) is int:
            # video device source
            self.video = cv.CaptureFromCAM(source)
            # try to read stream
            if cv.QueryFrame(self.video) is None:
                self.state = self.ERR_SOURCE
        elif type(source) is str:
            # video file source
            if os.path.exists(name) and os.path.isfile(name):
                self.video = cv.CaptureFromFile(name)
            else:
                self.state = self.ERR_FILE

        else:
            self.state = ERR_SOURCE
            self.video = None
            self.state = self.ERR_OPEN

    def __del__(self):
        """ Destructor
        """
        if self.video is not None:
            try:
                self.video.release()
            except:
                pass

    def GetImage(self):
        """ Get image from stream

            :returns: an image or None
        """
        if self.state != self.IF_OK:
            img = cv.QueryFrame(self.video)
            if img is None:
                self.state = self.ERR_READ
            return img
        return None

if __name__ == "__main__":
    stream = VideoInterface("webcam", 1)
    img = stream.GetImage()
    print stream.state
    print img
    print cv.GetSize(img)
