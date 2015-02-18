#!/usr/bin/env python
"""
.. module:: videoiface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""

import cv
import logging
import os.path
from iface import Iface

class VideoIface(Iface):
    """ Read from video stream or video file. This class depends on OpenCV.

            :param name: name of interface (str), default 'webcam'
            :param source: id of device or file name (int/str), default = 0
    """
    def __init__(self, name = 'webcam', source = 0):
        """ Constructor
        """
        super(VideoIface, self).__init__(name)
        self.source = source
        self.video = None
        if type(source) is int:
            # video device source
            self.video = cv.CaptureFromCAM(source)
            # try to read stream
            if cv.QueryFrame(self.video) is None:
                self.state = self.IF_SOURCE
                logging.error(" error opening video camera")
            else:
                self.opened = True
        elif type(source) is str:
            # video file source
            if os.path.exists(source) and os.path.isfile(source):
                self.video = cv.CaptureFromFile(source)
                self.opened = True
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
        if self.state == self.IF_OK:
            img = cv.QueryFrame(self.video)
            if img is None:
                self.state = self.IF_READ
                logging.error(" error reading video source")
            return img
        return None

if __name__ == "__main__":
    stream = VideoIface("webcam", 0)
    if stream.state != stream.IF_OK:
        print ("error opening video stream")
    else:
        im = stream.GetImage()
        print (type(im))
        print (cv.GetSize(im))
