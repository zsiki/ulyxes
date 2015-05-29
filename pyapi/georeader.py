#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: georeader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""
import re
from angle import Angle
from filereader import FileReader

class GeoReader(FileReader):
    """ Class to read GeoEasy geo and coo files

        :param name: name of reader (str), default None
        :param fname: name of input file
        :param filt: list of GeoEasy field codes to use, default None (use all)
    """
    codes = {2: 'station', 3: 'ih', 4: 'code', 5: 'pid', 6: 'th',
             7: 'hz', 8: 'v', 9: 'distance', 11: 'hd', 21: 'hz',
             37: 'north', 38: 'east', 39: 'elev', 62: 'pid', 112: 'faces'}

    def __init__(self, name = None, fname = None, filt = None):
        """ Constructor
        """
        super(GeoReader, self).__init__(name, fname)
        self.filt = filt

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except:
            pass

    def GetNext(self):
        """ Get fields in dictionary from next line considering filter

            :returns: values in dict, empty dict on EOF
        """
        res = {}
        w = self.GetLine().strip('\n\r')
        buf = re.split('[\{\}]', w)
        for ww in buf:
            if len(ww) > 2:
                www = ww.split(' ')
                key = int(www[0])
                if key in self.codes and \
                    (self.filt is None or key in self.filt):
                    if key in (7, 8, 21):   # angles
                        res[self.codes[key]] =  Angle(float(www[1]))
                    elif key in (3, 6, 9, 11, 37, 38, 39):
                        res[self.codes[key]] =  float(www[1]) # numeric
                    elif key == 112:
                        res[self.codes[key]] =  int(www[1]) # numeric
                    else:
                        res[self.codes[key]] =  ' '.join(www[1:])
        return res

if __name__ == "__main__":
    g = GeoReader(fname='/home/siki/GeoEasy/data/test1.geo')
    while 1:
        w = g.GetNext()
        if w is None or len(w) == 0:
            break
        print w
