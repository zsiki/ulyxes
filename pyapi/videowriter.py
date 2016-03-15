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
import cv2
import logging
from writer import Writer

class VideoWriter(Writer):
    """ write images to video file

            :param name: name for writer
            :param fname: output file name
            :param codec: video compression
            :param fps: frame per sec (int), default 10
            :param size: image size (int, int), default (640, 480)
    """
    codecs = { 'JPEG': cv2.cv.CV_FOURCC('J', 'P', 'E', 'G'),
               'MJPG': cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'),
               'FLV1': cv2.cv.CV_FOURCC('F', 'L', 'V', '1'),
               'PIM1': cv2.cv.CV_FOURCC('P', 'I', 'M', '1') }

    def __init__(self, name, fname, codec, fps = 10, size = (640, 480)):
        """ Constructor
        """
        super(VideoWriter, self).__init__(name)
        self.state = self.WR_OK
        if codec is None:
            codec = self.codecs['JPEG']
        self.wp = cv2.cv.CreateVideoWriter(fname, codec, fps, size)
        if self.wp is None:
            self.state = self.WR_OPEN
            logging.error("cannot open video file %s", fname)

    def __del__(self):
        """ Destructor
        """
        try:
            self.wp.release()
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
            cv2.cv.WriteFrame(self.wp, data)
        except:
            logging.warning(" cannot write image to video file")

if __name__ == "__main__":
    from webcam import WebCam
    from videoiface import VideoIface
    from videomeasureunit import VideoMeasureUnit
    vw = VideoWriter("vw", "video_file", None)
    mu = VideoMeasureUnit()
    vi = VideoIface()
    cam = WebCam('x', mu, vi, vw)

