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
    ERR_OPEN = -1
    ERR_WRITE = -2
    ERR_TIMEOUT = -3
    ERR_READ = -4

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

    def Send(self, msg):
        pass

if __name__ == "__main__":
    a = Interface()
    print a.GetName()
    print a.GetState()
