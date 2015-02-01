#!/usr/bin/env python
"""
.. module:: videowriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""
import cv
import logging
from writer import Writer

class VideoWriter(Writer):
    """ write images to video file
    """
    codecs = { 'JPEG': cv.CV_FOURCC('J', 'P', 'E', 'G'),
               'MJPG': cv.CV_FOURCC('M', 'J', 'P', 'G'),
               'FLV1': cv.CV_FOURCC('F', 'L', 'V', '1'),
               'PIM1': cv.CV_FOURCC('P', 'I', 'M', '1') }

    def __init__(self, name, fname, codec, fps = 10, size = (640, 480)):
        """ Constructor

            :param name: name for writer
            :param fname: output file name
        """
        super(VideoWriter, self).__init__(name)
        self.state = self.WR_OK
        if codec is None:
            codec = self.codecs['JPEG']
        self.wp = cv.CreateVideoWriter(fname, codec, fps, size)
        if self.fp is None:
            self.state = self.WR_OPEN
            logging.error("cannot open video file %s", fname)

    def __del__(self):
        """ Destructor
        """
        try:
            # TODO no Release in cv, cv2 should be used
            #cv.cvReleaseVideoWriter(self.wp)
            pass
        except:
            pass

    def WriteData(self, data):
        """ write image to video file

            :param data: image to write
        """
        if data is None:
            logging.warning(" empty image not writen")
            return
        try:
            cv.WriteFrame(self.wp, data)
        except:
            logging.warning(" cannot write image to video file")

if __name__ == "__main__":
    from webcam import *
    from videointerface import *
    from videomeasureunit import *
    vw = VideoWriter("vw", "video_file", None)
    mu = VideoMeasureUnit()
    vi = VideoInterface()
    cam = WebCam('x', mu, vi, vw)

