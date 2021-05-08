#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: csvreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

from filereader import FileReader

class CsvReader(FileReader):
    """ Class to read csv file, first line must contain field names

            :param name: name of reader (str), default None
            :param fname: name of input file
            :param separator: field separator, default ;
            :param filt: list of fields to use, default None (use all)
            :param fields: list of field names for columns in CSV if not in the first line
    """

    def __init__(self, name=None, fname=None, separator=';', filt=None, fields=None):
        """ Constructor
        """
        super(CsvReader, self).__init__(name, fname, filt)
        self.separator = separator
        self.filt = filt
        if fields is None:
            # get field names from header line
            self.fields = []
            if self.state == self.RD_OK:
                self.fields = [
                    x.strip() for x in self.GetLine().split(self.separator)]
        else:
            self.fields = fields

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except Exception:
            pass

    def GetNext(self):
        """ Get fields in dictionary from next line
        """
        buf = self.GetLine()
        if self.state != self.RD_OK:
            return None
        w = [x.strip() for x in buf.split(self.separator)]
        if len(w) == 0:
            return None         # empty line
        res = {}
        for i, item in enumerate(w):
            if self.filt is None or self.fields[i] in self.filt:
                res[self.fields[i]] = item
        return res

if __name__ == '__main__':
    cr = CsvReader('test', '../data/elev_1056.csv', separator=',',
                   fields=['psz', 'dt', 'east', 'north', 'elev', 'code'])
    if cr.state == cr.RD_OK:
        print(cr.Load())
    else:
        print("File not found")
