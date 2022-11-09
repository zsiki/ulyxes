#!/usr/bin/env python

"""
.. module:: localiface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>

"""
import re
import logging
from iface import Iface

class LocalIface(Iface):
    """ This local interface stands for using PyAPI without any instrument.
        A file is used to read data instread of instrument.
        It is mainly for developing or testing.
        rand mode can be used with GeoCom commands only, if more lines with
        identical codes are in the input file, they are used sequentially

        :param name: name of the interface (str), default 'Local'
        :param fname: name of the file the data read from
        :param mode: seq/rand, seq=read the input sequentially (e.g. NMEA GNSS), rand=get line with given key (e.g. leica totalstation)
    """
    def __init__(self, name='Local', fname='None', mode='seq'):
        """ Constructor
        """
        super().__init__(name)
        self.mode = mode
        self.fp = None
        self.data = {}
        self.index = {}
        try:
            self.fp = open(fname, 'r')
        except Exception:
            self.state = self.IF_FILE
            logging.error(" error opening file")
            return
        if mode == 'rand':
            # load whole file
            for line in self.fp:
                code, ans = line.split('|')
                if code not in self.data:
                    self.data[code] = []
                    self.index[code] = 0
                self.data[code].append(ans)

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except Exception:
            pass

    def Send(self, msg):
        """ Return answer from the file instead of instrument

            :param msg: message to send
            :returns: message specific answer
        """
        if self.mode == 'rand':
            code = re.split(':|,', msg)[1]
            if code in self.data:
                i = self.index[code]
                if i < len(self.data[code]):
                    self.index[code] += 1
                else:
                    i = 0
                return self.data[code][i]
            return None
        if self.mode == 'seq':
            return self.GetLine()
        return None

    def GetLine(self):
        """ Return next line from sequental file

            :returns: next line from the file
        """
        w = self.fp.readline().strip()
        if len(w) == 0:
            self.state = self.IF_EOF
            logging.warning('End of file')
        return w

if __name__ == "__main__":
    a = LocalIface(fname="/home/siki/tmp/tca1800.geocom", mode='rand')
    #a = LocalIface('test', '/home/siki/meresfeldolgozas/nmea1.txt')
