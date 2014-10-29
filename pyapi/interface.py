#!/usr/bin/env python
"""
    <p>Ulyxes - an open source project to drive total stations and
           publish observation results</p>
    <p>GPL v2.0 license</p>
    <p>Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu></p>
    @author Zoltan Siki 
    @author Daniel Moka 
    @version 1.1   
"""

class Interface(object):
    "base class for all interfaces"
    IF_OK = 0
    ERR_OPEN = 1
    ERR_WRITE = 2
    ERR_TIMEOUT = 3
    ERR_READ = 4
    def __init__(self, name = 'None'):
        self.name = name
        self.state = self.IF_OK

    def GetName(self):
        return self.name

    def GetState(self):
        return self.state

    def ClearState(self):
        self.state = self.IF_OK

    def Send(self, msg):
        pass

if __name__ == "__main__":
    a = Interface()
    print a.GetName()
    print a.GetState()
