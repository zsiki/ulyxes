#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: filereader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""
import logging
from reader import Reader

class FileReader(Reader):
    """ Class to read file

            :param name: name of reader (str), default None
            :param fname: name of input file
            :param filt: obligatory fields for Load
    """

    def __init__(self, name = None, fname = None, filt = None):
        """ Constructor
        """
        super(FileReader, self).__init__(name, filt)        
        self.fp = None
        try:
            self.fp = open(fname, 'r')
        except IOError:
            self.state = self.RD_OPEN
            logging.error(" cannot open file %s", fname)

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except:
            pass

    def GetLine(self):
        """ Get next line from file
        """
        return self.fp.readline().lstrip('\r\n')

    def GetNext(self):
        return self.GetLine()

    def Rewind(self):
        """ Rewind file to start
        """
        if self.fp.tell():
            self.fp.seek(0)

if __name__ == '__main__':
    fr = FileReader('test', 'reader.py')
    if fr.state == fr.RD_OK:
        print(fr.Load())
    else:
        print('File not found')
