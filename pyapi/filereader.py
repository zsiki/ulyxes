#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: filereader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""
import logging
import glob
from reader import Reader

class FileReader(Reader):
    """ Class to read file

            :param name: name of reader (str), default None
            :param fname: name of input file
            :param filt: obligatory fields for Load
    """

    def __init__(self, name=None, fname=None, filt=None):
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
        except Exception:
            pass

    @classmethod
    def extend_names(cls, name_list):
        """ extend wildcard characters from the command line on windows
            and remove non-existent files from list
        """
        names = []
        for name in name_list:
            names += glob.glob(name)
        return names

    def GetLine(self):
        """ Get next line from file

            :returns: next line from file or None in case of EOF
        """
        buf = self.fp.readline()
        if buf:
            buf = buf.strip('\r\n')
        else:
            buf = None
            self.state = self.RD_EOF
        return buf

    def GetNext(self):
        """ Get next line from file
        """
        return self.GetLine()

    def Rewind(self):
        """ Rewind file to start
        """
        if self.fp.tell():
            self.fp.seek(0)

if __name__ == '__main__':
    fr = FileReader('test', 'reader.py')
    if fr.state == fr.RD_OK:
        for line in fr.Load():
            print(line)
    else:
        print('File not found')
