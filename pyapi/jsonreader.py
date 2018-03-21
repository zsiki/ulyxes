#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: jsonreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""
import json
from filereader import FileReader

class JSONReader(FileReader):
    """ Class to read file

            :param name: name of reader (str), default None
            :param fname: name of input file
            :param filt: obligatory fields for Load
    """
    # TODO filt ????
    def __init__(self, name = None, fname = None, filt = None):
        """ Constructor
        """
        super(JSONReader, self).__init__(name, fname, filt)        
        self.json = None

    def GetLine(self):
        """ Not available for JSON
        """
        raise ValueError('GetLine not available for JSON reader')

    def Load(self):
        """ Load full JSON file
        """
        c = ""
        for line in self.fp:
            c += line
        res = json.loads(c)
        self.json = res
        return res

if __name__ == '__main__':
    jr = JSONReader('test', '../pyapps/test.json')
    print(jr.Load())
