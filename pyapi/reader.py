#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: reader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

class Reader(object):
    """ Base class for different readers (virtual)

            :param name: name of reader (str), default None
    """
    RD_OK = 0
    RD_OPEN = -1
    RD_READ = -2

    def __init__(self, name = None):
        """ Constructor
        """
        self.name = name
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
