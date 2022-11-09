#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: reader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

class Reader():
    """ Base class for different readers (virtual)

            :param name: name of reader (str), default None
            :param filt: list of mandatory field names in input record to keep
    """
    RD_OK = 0
    RD_OPEN = -1
    RD_READ = -2
    RD_EOF = -3

    def __init__(self, name=None, filt=None):
        """ Constructor
        """
        self.name = name
        self.filt = filt
        self.state = self.RD_OK

    def GetName(self):
        """ Get the name of the interface being used.
        """
        return self.name

    def GetState(self):
        """ Get the state of the interface being used.
        """
        return self.state

    def ClearState(self):
        """ Clear the state of the reader being used.
        """
        self.state = self.RD_OK

    def GetNext(self):
        """ Dummy function implemented in descendant objects
        """
        return None

    def Rewind(self):
        """ Dummy function implemented in descendant objects
        """
        self.state = self.RD_OK

    def Filt(self, rec):
        """ check all filter fields are in record

            :param rec: record to check to self.filt
            :returns: Tue/False keep/drop record
        """
        if self.filt is None:
            return True
        for f in self.filt:
            if f not in rec:
                return False
        return True

    def Load(self):
        """ Load all records into a list

            :returns: list of data units/lines
        """
        res = []
        w = None
        #self.Rewind()
        while self.state == self.RD_OK:
            try:
                w = self.GetNext()
            except IOError:
                self.state = self.RD_READ
            if w is None:
                break
            if self.Filt(w):
                res.append(w)   # keep record passed filter
        return res
