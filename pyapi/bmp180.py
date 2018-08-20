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

from webmet import WebMet

class BMP180(WebMet):
    """ BMP180/BMP085 air pressure sensor

            :param name: name of sensor (str)
            :param measureUnit: measure unit of the sensor (MeasureUnit)
            :param MeasureIface: interface to physical sensor (Iface)
            :param writerUnit: unit to save observed data (Writer), optional
    """
    def __init__(self, name, measureUnit, measureIface, writerUnit=None):
        """ constructor
        """
        super(BMP180, self).__init__(name, measureUnit, measureIface, writerUnit)
        self.LoadCalibration()

    def LoadCalibration(self):
        """ read calibration data from sensor

        """
        msg = self.measureUnit.LoadCalibrationMsg()
        return self._process(msg)

    def GetPressure(self, withTemp=1):
        """ Get pressure in hecto Pascals (hPa) from sensor

            :param withTemp: measure temperature also for fresh correction value (B5 stored in measure unit)
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

    def GetHumi(self):
        """ Get humidity from sensor

            :returns: None (no humidity available)
        """
        return None

if __name__ == "__main__":
    """ bmp180 demo logger
        command line parameters
        argv[1]: name of log file, default bmp180.log
        argv[2]: number of repeated observations, default 10
        argv[3]: delay between observations, default 30 sec
        argv[4]: elevation of start point, default 100
    """
    import time
    import sys
    from bmp180measureunit import BMP180MeasureUnit
    from i2ciface import I2CIface
    from filewriter import FileWriter
    if len(sys.argv) > 1:
        log = sys.argv[1]       # name of log file
    else:
        log = 'bmp180.log'      # default log file
    if len(sys.argv) > 2:
        n = int(sys.argv[2])    # number of observations
    else:
        n = 10                  # default single observation
    if len(sys.argv) > 3:
        delay = int(sys.argv[3]) # delay between observations (sec)
    else:
        delay = 30               # default delay 30 sec
    if len(sys.argv) > 4:
        elevation = float(sys.argv[4]) # elevation of start point
    else:
        elevation = 100                # default elevation for start point
    mu = BMP180MeasureUnit()
    i2c = I2CIface(None, 0x77)
    fw = FileWriter(fname='bmp180.log', filt=['elev', 'pressure', 'temp', 'datetime'])
    bmp = BMP180('BMP180', mu, i2c)
    bmp.LoadCalibration()
    bmp.SetSealevel(elevation)
    #bmp.GetTemp()
    for i in range(n):
        data = bmp.GetPressure()
        data['elev'] = bmp.GetAltitude()
        data['temp'] = bmp.GetTemp()['temp']
        fw.WriteData(data)
        print(data)
        time.sleep(delay)
