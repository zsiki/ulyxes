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
import os
import cv
import logging
from writer import Writer

class ImageWriter(Writer):
    """ write images to single files to a directory
    """

    def __init__(self, name, dirName, counter = 0):
        """ Constructor

            :param name: name for writer
            :param dirname: output directory name
        """
        super(ImageWriter, self).__init__(name)
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

    def WriteData(self, data):
        """ write image to file

            :param data: image to write
        """
        if data is None:
            logging.warning(" empty image not written")
            return
        name = os.path.join(self.dirName, str(self.counter) + '.png')
        try:
            cv.SaveImage(name, data)
            self.counter += 1
        except:
            logging.warning(" cannot write image to file")

if __name__ == "__main__":
    pass
