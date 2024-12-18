#!/usr/bin/env python
"""
.. module:: imagewriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""
import os
import logging
import cv2
from writer import Writer

class ImageWriter(Writer):
    """ write images to single files to a directory, file names are ordinal
        numbers

            :param name: name for writer (str)
            :param dirname: output directory name (str)
            :param counter: id number for the first image (int), default 0
            :param itype: target image type, default png
    """

    def __init__(self, name, dirName, counter=1, itype='png'):
        """ Constructor
        """
        super().__init__(name)
        if itype[0] != '.':
            itype = '.' + itype
        if not itype in ('.bmp', '.jpg', '.png', '.tif', '.pbm'):
            logging.warning("unsupported image format, png is used")
            itype = '.png'
        self.itype = itype
        self.state = self.WR_OK
        self.dirName = None
        self.counter = counter
        if os.path.exists(dirName):
            if os.path.isdir(dirName):
                self.dirName = dirName
            else:
                logging.error(" not a directory")
        else:
            os.mkdir(dirName)
            self.dirName = dirName

    def WriteData(self, data, convert=None):
        """ write image to file

            :param data: image to write
            :param convert: conversion before write e.g. convert='gray'
            :return: name of image file
        """
        if data is None:
            logging.warning(" empty image not written")
            return None
        name = os.path.join(self.dirName, self.name + "{:05d}".format(self.counter) + self.itype)
        try:
            if convert == 'gray' and len(data.shape) == 3:
                cv2.imwrite(name, cv2.cvtColor(data, cv2.COLOR_BGR2GRAY))
            else:
                cv2.imwrite(name, data)
            self.counter += 1
        except Exception:
            logging.warning(" cannot write image to file")
        return name

if __name__ == "__main__":
    pass
