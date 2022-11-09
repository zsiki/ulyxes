#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: jsonreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""
import json
from filereader import FileReader

class JSONReader(FileReader):
    """ Class to read file

            :param name: name of reader (str), default None
            :param fname: name of input file
    """

    def __init__(self, name=None, fname=None):
        """ Constructor
        """
        super().__init__(name, fname)
        self.json = None

    def GetLine(self):
        """ Not available for JSON
        """
        raise ValueError('GetLine not available for JSON reader')

    def Load(self):
        """ Load full JSON file
        """
        #c = ""
        #for line in self.fp:
        #    c += line
        res = json.loads("".join(self.fp.readlines()))
        self.json = res
        return res

if __name__ == '__main__':
    jr = JSONReader('test', '../pyapps/test.json')
    print(jr.Load())
