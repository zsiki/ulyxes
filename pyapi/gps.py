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
from instrument import Instrument

class GPS(Instrument):
    def __init__(self, name, measureUnit, measureInterf):
        """ constructor for gps

            :param name: name of gps instrument
            :param measureUnit: reference to measure unit
            :param measureInterf: reference to measure interface
        """
    # call super class init
        super(GPS, self).__init__(name, measureUnit, measureInterf)

    def Measure():
        pass


if __name__ == '__main__':
    pass
