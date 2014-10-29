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

class MeasureUnit(object):
    def __init__(self, name = 'None', type = 'None'):
        self.name = name
        self.type = type

    def GetName(self):
        return self.name

    def GetType(self):
        return self.type

    def Result(self, msg, ans):
        return None

    def Move(self, hz, v, units='RAD', atr=0):
        pass

if __name__ == "__main__":
    a = MeasureUnit()
    print a.GetName()
    print a.GetType()	
