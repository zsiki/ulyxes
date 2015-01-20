#!/usr/bin/env python
"""
.. module:: leicadnaunit.py

   :platform: Unix, Windows
      :synopsis: Ulyxes - an open source project to drive total stations and
             publish observation results.
            GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

  .. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokbme@gmail.com>
"""

from measureunit import MeasureUnit
import re

class LeicaDnaUnit(MeasureUnit):
    """ Leica DNA measure unit
    """
    MEASURE = "GET/M/WI32/WI330"
    TEMPERATURE = "GET/M/WI95"
    SETAUTOOFF = "SET/95/"
    GETAUTOOFF = "CONF/95"
    unitDiv = [1000.0, 1000.0 / 0.3048, 10000.0, 10000.0 / 0.3048, 100000.0]

    def __init__(self, name = 'Leica level', typ = 'Level'):
        """ Construnctor for leica dna unit

            :param name: name of measure unit
            :param typ: type of measure unit
        """
        # call super class init
        super(LeicaDnaUnit, self).__init__(name, typ)

    def Result(self, msg, ans):
        """ process result of a measurement

            :param msg: message sent
            :param ans: answer to message
            :returns: observation results (dictionary)
        """
        m = re.search("^@[EW]([0-9]+)$")
        res = {}
        if m is not None:
            res["error"] = int(m.group(0))
            return res    # error
        ansBuflist = re.split(' ', ans)
        if msg == self.MEASURE:
            for item in ansBuflist:
                if re.search("^32\.", item):
                    # distance
                    res["distance"] = float(item[7:]) / unitDiv[int(item[5])]
                elif re.search("^330", item):
                    # staff reading
                    res["staff"] = float(item[7:]) / unitDiv[int(item[5])]
        elif msg == self.TEMPERATURE:
            for item in ansBuflist:
                if re.search("^95", item):
                    # temperature
                    res["temperature"] = float(item[7:]) / unitDiv[int(item[5])]
        elif msg == self.SETAUTOOFF:
            if len(ans):
                res["error"] = ans
        elif msg == self.GETAUTOOFF:
            if len(ans):
                res["error"] = ans
        return res

    def MeasureMsg(self):
        """ Start measure message
        
            :returns: measure message
        """
        return self.MEASURE

    def TemperatureMsg(self):
        """ Get temperature message
        
            :returns: temperature message
        """
        return self.TEMPERATURE
    
    def SetAutoOffMsg(self, par):
        """ Set auto off message

            :param par: 0/1/2 Off/On/Sleep mode
            :return: auto off message
        """
        return "{0}{1:d}".format(self.SETAUTOOFF, par) 

    def GetAutoOffMsg(self):
        """ Get auto off message

            :returns: get auto off message
        """
        return self.GETAUTOOFF
