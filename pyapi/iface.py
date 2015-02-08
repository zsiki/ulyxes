#!/usr/bin/env python
"""
.. module:: iface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>

"""

class Iface(object):
    """ Base class for different interfaces

        :param name: name of the interface (str) (default None)
    """
    
    IF_OK = 0
    IF_WRITE = -3
    IF_TIMEOUT = -4
    IF_READ = -5
    IF_FILE = -6
    IF_SOURCE = -7
    IF_ERROR = -8

    def __init__(self, name = None):
        """ Constructor
        """
        self.name = name
        self.state = self.IF_OK
        self.opened = False

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
        self.state = self.IF_OK

if __name__ == "__main__":
    a = Iface()
    print (a.GetName())
    print (a.GetState())
