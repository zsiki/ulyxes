#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.. module:: imagereader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

import os
import glob
import datetime
import time
import numpy as np
import cv2
from reader import Reader

try:
    #from picamera.array import PiRGBArray
    from picamera import PiCamera
except ModuleNotFoundError:
    pass

try:
    from picamera2 import Picamera2
except ModuleNotFoundError:
    pass

class ImageReader(Reader):
    """ Read images from folder(s) or video file or web camera or pi camera

        :param srcname: camera id/video file/list of image names with wildcard"
        :param name: name of reader
        :param filt: not used yet
        :param fps: frame/sec for video file
    """
    CAMERA = 0
    VIDEO = 1
    IMAGE = 2
    PICAM = 3
    PICAM2 = 4

    def __init__(self, srcname, name=None, filt=None, fps=None,
                 width=None, height=None):
        """ Constructor """
        super().__init__(name, filt)
        self.fps = fps
        self.srcname = srcname
        self.ind = 0    # image index
        self.start = datetime.datetime.now()
        self.dt = None
        self.source = None
        self.typ = None
        if isinstance(srcname, list):
            self.typ = self.IMAGE
            self.source = []
            for s in srcname:
                self.source += glob.glob(s) # extend wildcards and remove non-existent files
            if len(self.source) > 0:
                self.source.sort()
            else:
                self.source = None
        elif isinstance(srcname, str) and \
                srcname.lower()[-4:] in ("h264", ".mp4", ".avi", "webm", ".mkv"):
            self.typ = self.VIDEO
            if os.path.exists(srcname):
                self.source = cv2.VideoCapture(srcname)
                if fps is None:
                    self.fps = self.source.get(cv2.CAP_PROP_FPS)
                self.dt = datetime.timedelta(0, 1.0 / self.fps)
                self.start = datetime.datetime.fromtimestamp(os.path.getmtime(srcname))
                self.width = self.source.get(cv2.CAP_PROP_FRAME_WIDTH)
                self.height = self.source.get(cv2.CAP_PROP_FRAME_HEIGHT)
        elif srcname in ("0", "1", "2", "3"):
            # camera source
            self.typ = self.CAMERA
            self.source = cv2.VideoCapture(int(srcname)) # open camera stream
            if fps:
                self.source.set(cv2.CAP_PROP_FPS, fps)
            if width:
                self.source.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            if height:
                self.source.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.fps = self.source.get(cv2.CAP_PROP_FPS)
            self.width = self.source.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.source.get(cv2.CAP_PROP_FRAME_HEIGHT)

        elif srcname.lower() == 'picam':
            self.typ = self.PICAM
            self.source = PiCamera()
            if width is None or height is None:
                self.width = 640
                self.height = 480
            else:
                self.width = width
                self.height = height
            self.source.resolution = (self.width, self.height)
            if fps is not None:
                self.source.framerate = fps
            time.sleep(0.1)	# wait for camera initialization
        elif srcname.lower() == "picam2":
            self.typ = self.PICAM2
            self.source = Picamera2()
            if width is None or height is None:
                self.width = 640
                self.height = 480
            else:
                self.width = width
                self.height = height
            config = self.source.create_preview_configuration(main={"size": (self.width, self.height)})
            self.source.configure(config)
            self.source.start()
            time.sleep(0.1)
        self.act = self.start

    def __del__(self):
        """ release video """
        if self.typ in (self.CAMERA, self.VIDEO):
            try:
                self.source.release()
            except Exception:
                pass
        elif self.typ in (self.PICAM, self.PICAM2):
            try:
                self.source.close()
            except Exception:
                pass

    def GetNext(self):
        """ Get next image """
        frame = None
        t = None
        if self.typ == self.IMAGE:
            if self.source is not None and len(self.source):
                fn = self.source.pop(0)
                self.srcname = fn
                frame = cv2.imread(fn)
                t = datetime.datetime.fromtimestamp(os.path.getmtime(fn))
        elif self.typ == self.PICAM:
            frame = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.source.capture(frame, format="rgb")
            t = datetime.datetime.now()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)	# change to opencv BGR
        elif self.typ == self.PICAM2:
            frame = self.source.capture_array()
            t = datetime.datetime.now()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)	# change to opencv BGR
        else:
            ret, frame = self.source.read()
            if ret:
                if self.typ == self.CAMERA:
                    t = datetime.datetime.now()
                else:
                    # get timestamp from video
                    tt = self.source.get(cv2.CAP_PROP_POS_MSEC)
                    if tt > 0:
                        self.act = self.start + datetime.timedelta(milliseconds=tt)
                    t = self.act
                    self.act += self.dt
        self.ind += 1
        return frame, t

if __name__ == "__main__":
    ir0 = ImageReader('picam')
    img, t = ir0.GetNext()
    print(img.shape, t)
    ir1 = ImageReader("/home/siki/tmp/3_20191207_105813_00*.png")
    img, t = ir1.GetNext()
    print(ir1.ind, ir1.srcname, t)
    img, t = ir1.GetNext()
    print(ir1.ind, ir1.srcname, t)
    img, t = ir1.GetNext()
    print(ir1.ind, ir1.srcname, t)
    img, t = ir1.GetNext()
    print(ir1.ind, ir1.srcname, t)
    img, t = ir1.GetNext()
    print(ir1.ind, ir1.srcname, t)
    img, t = ir1.GetNext()
    print(ir1.ind, ir1.srcname, t)
    ir2 = ImageReader('/media/siki/Extreme SSD/munka/tanszek/uszomu/1207/video/3_20191207_105813.h264', fps=2)
    img, t = ir2.GetNext()
    print(ir2.ind, ir2.srcname, t)
    img, t = ir2.GetNext()
    print(ir2.ind, ir2.srcname, t)
    img, t = ir2.GetNext()
    print(ir2.ind, ir2.srcname, t)
    img, t = ir2.GetNext()
    print(ir2.ind, ir2.srcname, t)
    img, t = ir2.GetNext()
    print(ir2.ind, ir2.srcname, t)
    img, t = ir2.GetNext()
    print(ir2.ind, ir2.srcname, t)
    ir3 = ImageReader("0")
    img, t = ir3.GetNext()
    print(ir3.ind, ir3.srcname, t)
    img, t = ir3.GetNext()
    print(ir3.ind, ir3.srcname, t)
    img, t = ir3.GetNext()
    print(ir3.ind, ir3.srcname, t)
    img, t = ir3.GetNext()
    print(ir3.ind, ir3.srcname, t)
    img, t = ir3.GetNext()
    print(ir3.ind, ir3.srcname, t)
