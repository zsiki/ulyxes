#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: bmp180.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2015 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

Based on BMP085.py created by Tony DiCola
"""

from instrument import Instrument
from bmp180measureunit import *

class BMP180(Instrument):
    """ BMP180/BMP085 air pressure sensor

            :param name: name of sensor (str)
            :param measureUnit: measure unit of the sensor (MeasureUnit)
            :param MeasureIface: interface to physical sensor (Iface)
            :param writerUnit: unit to save observed data (Writer), optional
    """
    def __init__(self, name, measureUnit, measureIface, writerUnit = None):
        """ constructor
        """
        super(BMP180, self).__init__(name, measureUnit, measureIface, writerUnit)
        self.LoadCalibration()

    def LoadCalibration(self):
        # TODO read calibration data from sensor
        #self.measureUnit.cal_AC1 = self.measureIface.Send(('readS16BE', BMP180_CAL_AC1))['data']
        pass

    def GetPressure(self):
        """ Get pressure from sensor

            :returns: pressure in Pascals
        """
        msg = self.measureUnit.GetPressureMsg()
        return self._process(msg)

    def GetTemp(self):
        """ Get temperature from sensor

            :returns: temperature in centigrades
        """
        msg = self.measureUnit.GetTempMsg()
        return self._process(msg)

if __name__ == "__main__":
    from bmp180measureunit import BMP180MeasureUnit
    from i2ciface import I2CIface
    from echowriter import EchoWriter
    mu = BMP180MeasureUnit()
    i2c = I2CIface(None, 0x77)
    ew = EchoWriter()
    bmp = BMP180('BMP180', mu, i2c, ew)
    #bmp = BMP180('BMP180', mu, i2c)
    print bmp.GetTemp()
    print bmp.GetPressure()
