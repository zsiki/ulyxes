#!/usr/bin/env python
"""
.. module:: writer.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

class Writer(object):
    """ Base class for different writer (virtual)
    """
    WR_OK = 0
    WR_OPEN = -1
    WR_WRITE = -2

    def __init__(self, name = 'None'):
        """ Constructor

            :param name: name of writer
        """
        self.name = name
        self.state = self.WR_OK

    def GetName(self):
        """ Get the name of the interface being used.
        """
        return self.name

    def GetState(self):
        """ Get the state of the interface being used.
        """
        return self.state

    def ClearState(self):
        """ Clear the state of the interface being used.
        """
        self.state = self.WR_OK
