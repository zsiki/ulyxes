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
        self.p0 = None    # sealevel pressure not set
        self.LoadCalibration()

    def LoadCalibration(self):
        # TODO read calibration data from sensor
        #self.measureUnit.cal_AC1 = self.measureIface.Send(('readS16BE', BMP180_CAL_AC1))['data']
        pass

    def GetPressure(self, withTemp = 1):
        """ Get pressure from sensor

            :param withTemp: measure temperature also for fresh correction value (B5 sotred in measure unit)
            :returns: pressure in Pascals
        """
        if withTemp:
            self.GetTemp()
        msg = self.measureUnit.GetPressureMsg()
        return self._process(msg)

    def GetTemp(self):
        """ Get temperature from sensor

            :returns: temperature in centigrades
        """
        msg = self.measureUnit.GetTempMsg()
        return self._process(msg)

    def SetSealevel(self, altitude, pressure = None):
        """ calculate sealevel pressure from known elevation and pressure

            :param altitude: known elevation (float) meters
            :param pressure: know pressure at elevation, default None means get the pressure from sensor
        """
        if pressure is None:
            pressure = self.GetPressure()['pressure']
        self.p0 = pressure / pow(1.0 - altitude / 44330.0, 5.255)

    def GetAltitude(self):
        """ calculate altitude from sealevel pressure

            :returns: altitude
        """
        if self.p0 is None:
            return None    # no reference pressure
        pressure = self.GetPressure()['pressure']
        return 44330.0 * (1.0 - pow(pressure / self.p0, (1.0 / 5.255)))

if __name__ == "__main__":
    from bmp180measureunit import BMP180MeasureUnit
    from i2ciface import I2CIface
    from echowriter import EchoWriter
    mu = BMP180MeasureUnit()
    i2c = I2CIface(None, 0x77)
    ew = EchoWriter()
    bmp = BMP180('BMP180', mu, i2c, ew)
    bmp.GetTemp()
    bmp.GetPressure()
    bmp.SetSealevel(105.0)
    print bmp.GetAltitude()
