#!/usr/bin/env python
"""
.. module:: videointeface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>. This module depends on OpenCV.
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""

import cv
import logging
import os.path
from interface import Interface

class VideoInterface(Interface):
    """ Read from video stream or video file
    """
    def __init__(self, name = 'webcam', source = 0):
        """ Constructor

            :param name: name of interface
            :param source: id of device or file name, default = 0
        """
        super(VideoInterface, self).__init__(name)
        self.source = source
        self.video = None
        if type(source) is int:
            # video device source
            self.video = cv.CaptureFromCAM(source)
            # try to read stream
            if cv.QueryFrame(self.video) is None:
                self.state = self.IF_SOURCE
                logging.error(" error opening video camera")
        elif type(source) is str:
            # video file source
            if os.path.exists(name) and os.path.isfile(name):
                self.video = cv.CaptureFromFile(name)
            else:
                self.state = self.IF_FILE
                logging.error(" error opening video file")
        else:
            self.state = self.IF_SOURCE
            logging.error(" error opening video source")

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
        print self.state
        if self.state == self.IF_OK:
            img = cv.QueryFrame(self.video)
            if img is None:
                self.state = self.IF_READ
                logging.error(" error reading video source")
            return img
        return None

if __name__ == "__main__":
    stream = VideoInterface("webcam", 0)
    if stream.state != stream.IF_OK:
        print "error opening video stream"
    else:
        img = stream.GetImage()
        print type(img)
        print cv.GetSize(img)
