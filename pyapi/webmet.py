#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: webmet.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010- Zoltan Siki <siki.zoltan@epito.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>

"""

import math
from instrument import Instrument

class WebMet(Instrument):
    """ Get meteorological data from the Internet

            :param name: name of sensor (str)
            :param measureUnit: measure unit of the sensor (MeasureUnit)
            :param MeasureIface: interface to physical sensor (Iface)
            :param writerUnit: unit to save observed data (Writer), optional
    """
    def __init__(self, name, measureUnit, measureIface, writerUnit=None):
        """ constructor
        """
        super().__init__(name, measureUnit, measureIface, writerUnit)
        self.p0 = None    # sealevel pressure not set

    def GetTemp(self):
        """ Get temperature from sensor

            :returns: temperature data as dict
        """
        msg = self.measureUnit.GetTempMsg()
        res = self._process(msg)
        if res is not None and 'temp' in res:
            res['temp'] = res['temp'] - 273.1
        return res

    def GetPressure(self, withTemp=0):
        """ Get pressure in HPa from sensor

            :param withTemp: dummy parameter for inherited classes
            :returns: temperature data as dict
        """
        return self.GetTemp()


    def GetHumi(self):
        """ Get humidity from sensor

            :returns: temperature data as dict
        """
        return self.GetTemp()

    def SetSealevel(self, altitude, pressure=None):
        """ calculate sealevel pressure from known elevation and pressure

            :param altitude: known elevation (float) meters
            :param pressure: know pressure at elevation, default None means get the pressure from sensor
        """
        if pressure is None:
            pressure = self.GetPressure(1)['pressure'] * 100.0
        self.p0 = pressure / pow(1.0 - altitude / 44330.0, 5.255)

    def GetAltitude(self):
        """ calculate altitude from sealevel pressure

            :returns: altitude
        """
        if self.p0 is None:
            return None    # no reference pressure
        pressure = self.GetPressure()['pressure'] * 100
        return 44330.0 * (1.0 - pow(pressure / self.p0, (1.0 / 5.255)))

    @staticmethod
    def GetWetTemp(temp, humi):
        """ Calculate wet temperature from humidity and temperature
            formula from http://journals.ametsoc.org/doi/pdf/10.1175/JAMC-D-11-0143.1

            :param temp: dry temperature
            :param humi: humidity as percent
        """
        wet = temp * math.atan(0.151977 * math.sqrt(humi + 8.313659)) + \
            math.atan(temp + humi) - math.atan(humi - 1.676331) + \
            0.00391838 * humi**(3.0/2.0) * math.atan(0.023101 * humi) - \
            4.686035
        return wet

if __name__ == "__main__":
    # webmet demo logger
    #    command line parameters
    #    argv[1]: your app id for http://api.openweathermap.org
    #    argv[2]: name of log file, default webmet.log
    #    argv[3]: number of repeated observations, default 10
    #    argv[4]: delay between observations, default 30 sec
    #    argv[5]: elevation of start point
    import time
    import sys
    from webmetmeasureunit import WebMetMeasureUnit
    from webiface import WebIface
    from filewriter import FileWriter
    n = len(sys.argv)
    if n < 2:
        print(f"{sys.argv[0]} app_id [log_file]  [repeat] [delay]")
        sys.exit()
    app_id = sys.argv[1]
    if len(sys.argv) > 2:
        log = sys.argv[2]       # name of log file
    else:
        log = 'webmet.log'      # default log file
    if len(sys.argv) > 3:
        n = int(sys.argv[3])    # number of observations
    else:
        n = 10                  # default single observation
    if len(sys.argv) > 4:
        delay = int(sys.argv[4]) # delay between observations (sec)
    else:
        delay = 30               # default delay 30 sec
    if len(sys.argv) > 5:
        elevation = float(sys.argv[5]) # elevation of start point
    else:
        elevation = 100                # default elevation for start point
    mu = WebMetMeasureUnit(msg="lat=47.463142&lon=19.070921&appid=" + app_id)
    wi = WebIface("demo", "http://api.openweathermap.org/data/2.5/weather", "json")
    fw = FileWriter(fname=log, filt=['pressure', 'temp', 'humidity', 'datetime'])
    web = WebMet('WebMet', mu, wi)
    for i in range(n):
        data = web.GetPressure()
        data['temp'] = web.GetTemp()['temp']
        fw.WriteData(data)
        print(data)
        time.sleep(delay)
