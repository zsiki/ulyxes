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

    def __init__(self, srcname, name=None, filt=None, fps=None):
        """ Constructor """
        super(ImageReader, self).__init__(name, filt)
        self.fps = fps
        self.srcname = srcname
        self.ind = 0    # image index
        self.act = datetime.datetime.now()
        self.dt = None
        self.source = None
        if srcname in ("0", "1", "2", "3"):
            # camera source
            self.typ = self.CAMERA
            self.source = cv2.VideoCapture(int(srcname)) # open camera stream
        elif srcname.lower() == 'picam':
            self.typ = self.PICAM
            self.source = PiCamera()
            self.width = 1632	# TODO should be input parameter
            self.height = 1216
            #self.width = 640
            #self.height = 480
            self.source.resolution = (self.width, self.height)
            time.sleep(0.1)	# wait for camera initialization
        elif isinstance(srcname, str) and \
                srcname.lower()[-4:] in ("h264", ".mp4", ".avi", "webm"):
            self.typ = self.VIDEO
            if os.path.exists(srcname):
                self.source = cv2.VideoCapture(srcname)
                if fps is None:
                    self.fps = self.source.get(cv2.CAP_PROP_FPS)
                self.dt = datetime.timedelta(0, 1.0 / self.fps)
                self.act = datetime.datetime.fromtimestamp(os.path.getmtime(srcname))
        else:
            if isinstance(srcname, str):
                srcname = [srcname]   # make list
            self.typ = self.IMAGE
            self.source = []
            for s in srcname:
                self.source += glob.glob(s) # extend wildcards and remove non-existent files
            if len(self.source) > 0:
                self.source.sort()
            else:
                self.source = None

    def __del__(self):
        """ release video """
        if self.typ in (self.CAMERA, self.VIDEO):
            try:
                self.source.release()
            except Exception:
                pass
        elif self.typ == self.PICAM:
            try:
                self.source.close()
            except Exception:
                pass

    def GetNext(self):
        """ Get next image """
        frame = None
        t = None
        if self.typ == self.IMAGE:
            if len(self.source):
                fn = self.source.pop(0)
                self.srcname = fn
                frame = cv2.imread(fn)
                t = datetime.datetime.fromtimestamp(os.path.getmtime(fn))
        elif self.typ == self.PICAM:
            frame = np.empty((self.height, self.width, 3), dtype=np.uint8)
            self.source.capture(frame, format="rgb")
            cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)	# change to opencv BGR
            t = datetime.datetime.now()
        else:
            ret, frame = self.source.read()
            if ret:
                if self.typ == self.CAMERA:
                    t = datetime.datetime.now()
                else:
                    self.act += self.dt
                    t = self.act
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
