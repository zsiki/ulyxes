#!/usr/bin/env python

"""
.. module:: localiface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>

"""
import re
import logging
from iface import Iface

class LocalIface(Iface):
    """ This local interface stands for using PyAPI without any instrument. 
        A file is used to read data instread of instrument.
        It is mainly for developing or testing

            :param name: name of the interface (str), default 'Local'
            :param fname: name of the file the data read from
            :param mode: seq/rand, seq=read the input sequentially (e.g. NMEA GNSS), rand=get line with given key (e.g. leica totalstation)
    """
    def __init__(self, name = 'Local', fname = 'None', mode='seq'):
        """ Constructor
        """
        super(LocalIface, self).__init__(name)
        self.mode = mode
        self.fp = None
        self.data = {}
        try:
            self.fp = open(fname, 'r')
        except:
            self.state = self.IF_FILE
            logging.error(" error opening file")
            return
        if mode == 'rand':
            # load whole file
            for line in self.fp:
                code, ans = line.split('|')
                self.data[code] = ans

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except:
            pass

    def Send(self, msg):
        """ Return answer from the file instead of instrument

            :param msg: message to send
            :returns: message specific answer
        """
        if self.mode == 'rand':
            code = re.split(':|,', msg)[1]
            if code in self.data:
                return self.data[code]
            else:
                return None
        elif self.mode == 'seq':
            return self.GetLine()
        else:
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
    a = LocalIface('test', '/home/siki/meresfeldolgozas/nmea1.txt')
    print (a.GetName())
    print (a.GetState())
    print (a.GetLine())
