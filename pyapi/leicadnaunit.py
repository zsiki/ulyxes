#!/usr/bin/env python
"""
    Leica DNA specific functions
    <p>Ulyxes - an open source project to drive total stations and
           publish observation results</p>
    <p>GPL v2.0 license</p>
    <p>Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu></p>
    @author Zoltan Siki
    @author Daniel Moka
    @version 1.1
"""

from measureunit import *

class LeicaDnaUnit(MeasureUnit):

    def __init__(self, name = 'Leica level', typ = 'Level'):
        # call super class init
        super(LeicaMeasureUnit, self).__init__(name, typ)

    def Result(self, msg, ans):
        pass

    def Measure(self):
        pass
