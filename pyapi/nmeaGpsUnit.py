#!/usr/bin/env python
"""
    Leica TCA1800/RTS1200 specific functions
    <p>Ulyxes - an open source project to drive total stations and
           publish observation results</p>
    <p>GPL v2.0 license</p>
    <p>Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu></p>
    @author Zoltan Siki
    @author Daniel Moka
    @version 1.1
"""

from angle import *
from measureunit import *

class NmeaGpsUnit(MeasureUnit):
    def __init__(self, name = 'Nmea Gps', type = '-'):
        # call super class init
        super(NmeaGpsUnit, self).__init__(name, type)

    def Result():
        pass

    def MeasureMsg():
        return "GET/M/WI32/WI330"

if __name__ == '__main__':
    main()
