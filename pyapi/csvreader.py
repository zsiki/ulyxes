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
            :param filter: list of fields to use, default None (use all)
    """

    def __init__(self, name = None, fname = None, separator = ';', filter = None):
        """ Constructor
        """
        super(CsvReader, self).__init__(name, fname)        
        self.separator = separator
        self.filter = filter
        # get field name from header line
        self.fields = [x.strip() for x in self.GetLine().split(self.separator)]

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except:
            pass

    def GetNext(self):
        """ Get fields in adictionary from next line considering filter
        """
        w = [x.strip() for x in self.GetLine().split(self.separator)]
        res = {}
        for i in range(len(self.fields)):
            if self.filter is None or self.fields[i] in self.filter:
                res[self.fields[i]] = w[i]
        return res

if __name__ == '__main__':
    cr = CsvReader('test', 'test.csv')
    print (cr.GetNext())
