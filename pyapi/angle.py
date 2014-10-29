#!/usr/bin/python
import math
"""
This file contains common instrument, angle conversion functions
    <p>Ulyxes - an open source project to drive total stations and
           publish observation results</p>
    <p>GPL v2.0 license</p>
    <p>Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu></p>
    @author Zoltan Siki
    @author Daniel Moka
    @version 1.1
"""
RO = 180 * 60 * 60 / math.pi

class Angle(object):
    def __init__(self, value=0, unit='RAD'):
        self.SetAngle(value, unit)

    def GetAngle(self, out):
        if out == 'RAD':
            output = self.value
        elif out == 'DMS':
            output = self.__DMS()
        elif out == 'DEG':
            output = self.__Rad2Deg()
        elif out == 'GON':
            output = self.__Rad2Gon()
        elif out == 'NMEA':
            output = self.__Rad2DM()
        else:
            # to do : write error in log file
            print('The output format is unknown: try RAD,DEG,DMS,GON')
        return output

    def SetAngle(self, value, unit='RAD'):
        if unit == 'RAD':
            self.value = value
        elif unit == 'DMS':
            self.value = self.__DMS2Rad(value)
        elif unit == 'DEG':
            self.value = self.__Deg2Rad(value)
        elif unit == 'GON':
            self.value = self.__Gon2Rad(value)
        elif unit == 'NMEA':
            self.value = self.__DM2Rad(value)
        else:
            # unknown unit
            self.value = 0

    def __Deg2Rad(self, angle):
        return math.radians(angle)

    def __Gon2Rad(self, angle):
        return (angle / 200.0 * math.pi)

    def __DMS2Rad(self, dms):
        #degrees = numpy.sum(numpy.fromstring(dms,sep='-')*[1.0, 1/60.0, 1/3600.0])
	items = [float(item) for item in dms.split('-')]
        return math.radians(items[0] + items[1] / 60.0 + items[2] / 3600.0)

    def __DM2Rad(self, angle):
        "DDMM.nnnnnn NMEA angle to radian"
        w = angle / 100.0
        d = int(w)
	return math.radians(d + (w - d) * 100.0 / 60.0)

    def __Rad2Gon(self):
        return (self.value / math.pi * 200.0)

    def __Rad2Sec(self):
        return self.value * RO

    def __Rad2Deg(self):
        return math.degrees(self.value)

    def __DMS(self):
        secs = round(self.__Rad2Sec())
        min, sec = divmod(secs, 60)
        deg, min = divmod(min, 60)
        deg = int(deg)
	dms = "%d-%02d-%02d" % (deg, min, sec)
        return dms

    def __Rad2DM(self):
        w = self.value / math.pi * 180.0
	d = int(w)
	return d * 100 + (w - d) * 60

if __name__ == "__main__":
    a = Angle('359-59-59', 'DMS')
    print a.GetAngle('RAD')
    print a.GetAngle('DMS')
    print a.GetAngle('DEG')
    print a.GetAngle('GON')
    print a.GetAngle('NMEA')
    print Angle(a.GetAngle('RAD'), 'RAD').GetAngle('DMS')
    print Angle(a.GetAngle('DMS'), 'DMS').GetAngle('DMS')
    print Angle(a.GetAngle('DEG'), 'DEG').GetAngle('DMS')
    print Angle(a.GetAngle('GON'), 'GON').GetAngle('DMS')
    print Angle(a.GetAngle('NMEA'), 'NMEA').GetAngle('DMS')
