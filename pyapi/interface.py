#!/usr/bin/env python
"""
.. module:: interface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Siki Zoltan <siki@agt.bme.hu>, Moka Daniel <mokadaniel@citromail.hu>

"""

class Interface(object):
    """
    Base class for different interfaces
    """
    
    IF_OK = 0
    IF_OPEN = -1
    IF_WRITE = -2
    IF_TIMEOUT = -3
    IF_READ = -4
    IF_FILE = -5
    IF_SOURCE = -6

    def __init__(self, name = 'None'):
        self.name = name
        self.state = self.IF_OK

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
    a = Interface()
    print a.GetName()
    print a.GetState()
