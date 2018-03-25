#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: csvreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

from filereader import FileReader

class CsvReader(FileReader):
    """ Class to read csv file, first line must contain field names

            :param name: name of reader (str), default None
            :param fname: name of input file
            :param separator: field separator, default ;
            :param filt: list of fields to use, default None (use all)
    """

    def __init__(self, name = None, fname = None, separator = ';', filt = None):
        """ Constructor
        """
        super(CsvReader, self).__init__(name, fname, filt)        
        self.separator = separator
        self.filt = filt
        # get field names from header line
        self.fields = []
        if self.state == self.RD_OK:
            self.fields = [
                x.strip() for x in self.GetLine().split(self.separator)]

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except:
            pass

    def GetNext(self):
        """ Get fields in dictionary from next line
        """
        w = [x.strip() for x in self.GetLine().split(self.separator)]
        res = {}
        if len(w) == 0 or w[0] == '':
            return None
        for i in range(len(w)):
            if self.filt is None or self.fields[i] in self.filt:
                res[self.fields[i]] = w[i]
        return res

if __name__ == '__main__':
    cr = CsvReader('test', 'test.csv')
    if cr.state == cr.RD_OK:
        print (cr.Load())
    else:
        print("File not found")
