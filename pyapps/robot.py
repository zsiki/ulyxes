#!/usr/bin/env python
"""
.. module:: robot.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to measure a serie of points

    :param argv[1]: input file with directions
    :param argv[2]: output file with observations default stdout
    :param argv[3]: sensor tcra1103/1100/tca1800/1800/tps1201/1200, default 1200
    :param argv[4]: serial port, default COM1
    :param argv[5]: number of retry if target not found, default 3
    :param argv[6]: delay between retries default 0
    :param argv[7]: name of met sensor BMP180/webmet, default None
    :param argv[8]: address of met sensor, i2c addres for BMP180 or internet address of webmet service
    :param argv[9]: parameters for webmet sensor

Input file is a GeoEasy geo file or a dmp (can be created by filemaker.py).
Sample geo::

    {2 S2} {3 0.0}                                    # station id & istrumnt h.
    {5 2} {7 6.283145} {8 1.120836} {4 PR0} {112 2}  # target id, hz, v, code,
    {5 T1} {7 2.022707} {8 1.542995} {4 RL} {112 2} # number of faces
    {5 3} {7 3.001701} {8 1.611722} {4 OR} {112 2}
    {5 T2} {7 3.006678} {8 1.550763} {4 ATR1} {112 2}
    {5 4} {7 3.145645} {8 1.610680} {4 PR2} {112 2}
    {5 1} {7 6.002123} {8 1.172376} {4 PR} {112 2}
    {5 9} {7 6.235123} {8 1.178538} {4 RLA} {112 2}

Sample dmp::

    station; id; hz; v; code;faces
    S2;2;6.283145;1.120836;PR0;2
    S2;T1;2.022707;1.542995;RL;2
    S2;3;3.001701;1.611722;OR;2
    S2;T2;3.006678;1.550763;ATR1;2
    S2;4;3.145645;1.610680;PR2;2
    S2;1;6.002123;1.172376;PR;2

Codes describe target type::

    ATRn - prism and automatic targeting, n referes to prism type 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini
    PRn - prism, n referes to prism type 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini, manual targeting
    RL - refrectorless observation, manual targeting
    RLA - reflectorless observation (automatic)
    OR - do not measure distance (orientation), manual targeting

    In case of PR/RL/OR the program stops and the user have to aim at the target
"""
import sys
import time
import re
import math
import logging

sys.path.append('../pyapi/')

from angle import Angle, PI2
from serialiface import SerialIface
from csvwriter import CsvWriter
from georeader import GeoReader
from geowriter import GeoWriter
from georeader import GeoReader
from csvreader import CsvReader
from httpwriter import HttpWriter
from totalstation import TotalStation

logging.getLogger().setLevel(logging.WARNING)

class Robot(object):
    """ manage robotic observations

        :param ifname: input file name .py/.geo/.dmp file
        :param ofname: output file name .csv or an URL
    """

    def __init__(self, ifname, ofname = 'stdout', stationtype = '1100',
        port = '/dev/ttyUSB0', maxtry = 3, delaytry = 0):
        """ initialize
        """
        if ifname[-3:] == '.py':  # configuration file given
            exec 'from ' + ifname[:-3] + ' import *'
        if ofname[-4:] == '.dmp' or ofname[-4:] == '.csv' or ofname == 'stdout':
            # dmp/csv file or console output
            if ofname[-4:] == '.dmp' or ofname[-4:] == '.csv':
                ofname1 = ofname[:-4] + '.dmp'
                ofname2 = ofname[:-4] + '.csv'
            else:
                ofname1 = ofname2 = ofname
            self.dmp_wrt = CsvWriter(angle = 'DMS', dist = '.4f', \
                filt = ['station', 'id','hz','v','distance', 'datetime'], \
                fname = ofname1, mode = 'a', sep = ';')
            self.coo_wrt = CsvWriter(dist = '.4f', \
                filt = ['id', 'east', 'north', 'elev', 'datetime'], \
                fname = ofname2, mode = 'a', sep = ';')
        elif ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
            # geo/coo file output
            if ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
                ofname1 = ofname[:-4] + '.geo'
                ofname2 = ofname[:-4] + '.coo'
            self.dmp_wrt = GeoWriter(angle = 'RAD', dist = '.4f', \
                filt = ['station', 'id','hz','v','distance', 'datetime'], \
                fname = ofname1, mode = 'a')
            self.coo_wrt = GeoWriter(dist = '.4f', \
                filt = ['id', 'east', 'north', 'elev', 'datetime'], \
                fname = ofname2, mode = 'a')
        elif ofname[:5] == 'http:' or ofname[:6] == 'https:':
            # http output
            ofname1 = ofname2 = ofname
            self.dmp_wrt = HttpWriter(angle = 'RAD', dist = '.4f', \
                filt = ['station', 'id','hz','v','distance', 'datetime'], \
                url = ofname1, mode = 'POST')
            self.coo_wrt = HttpWriter(angle = 'RAD', dist = '.4f', \
                filt = ['id', 'east', 'north', 'elev', 'datetime'], \
                url = ofname2, mode = 'POST')
        if re.search('120[0-9]$', stationtype):
            from leicatps1200 import LeicaTPS1200
            mu = LeicaTPS1200()
        elif re.search('110[0-9]$', stationtype):
            from leicatcra1100 import LeicaTCRA1100
            mu = LeicaTCRA1100()
        elif re.search('180[0-9]$', stationtype):
            from leicatca1800 import LeicaTCA1800
            mu = LeicaTCA1800()
        elif re.search('550[0-9]$', stationtype):
            from trimble5500 import Trimble5500
            mu = Trimble5500()

        iface = SerialIface("rs-232", port)
        self.ts = TotalStation(stationtype, mu, iface)
        if maxtry < 1:
            maxtry = 1
            logging.warning("maxtry changed to 1")
        self.maxtry = maxtry # number of retry if failed
        if delaytry < 0:
            delaytry = 0
            logging.warning("delaytry changed to 0")
        self.delaytry = delaytry # delay between retries
        self.directions, self.max_faces = self.load(ifname)
        if ifname[-4:] == '.geo':
            self.coordinates, _ = self.load(ifname[:-4] + '.coo')
        else:
            self.coordinates, _ = self.load(ifname[:-4] + '.csv')
        self.station = '???'  # TODO
        if 'station' in self.directions[0]:
            self.station = self.directions[0]['station']
        self.ih = 0
        if 'ih' in self.directions[0]:
            self.ih = self.directions[0]['ih']
        self.station_east = self.station_north = self.station_elev = 0
        for coo in self.coordinates:
            if coo['id'] == self.station:
                self.station_east = coo['east']
                self.station_north = coo['north']
                self.station_elev = coo['elev']
                break

    def load(self, ifn):
        """ load observation or coordinate data from file

            :param ifn: name of input file
            :returns: observation list and max faces to measure
        """
        # load input data set
        if ifn[-4:] in ('.geo', '.coo'):
            g = GeoReader(fname = ifn)
        else:
            g = CsvReader(fname = ifn)
        directions = []
        max_faces = 0
        while 1:
            w = g.GetNext()
            if w is None or len(w) == 0:
                break
            if not 'code' in w:
                w['code'] = 'ATR'
            if not 'faces' in w:
                # default to 1 face
                w['faces'] = 1
            if max_faces < w['faces']:
                max_faces = w['faces']
            directions.append(w)
        return (directions, max_faces)

    def polar(self, obs):
        """ calculate coordinates for target

            :param obs: observed angles and distance
            :returns: (east, north, elev)
        """
        east = self.station_east + obs['distance'] * math.sin(obs['v'].GetAngle()) * math.sin(obs['hz'].GetAngle())
        north = self.station_north + obs['distance'] * math.sin(obs['v'].GetAngle()) * math.cos(obs['hz'].GetAngle())
        elev = self.station_elev + self.ih + obs['distance'] * math.cos(obs['v'].GetAngle())
        return (east, north, elev)

    def run(self):
        """ run an observation serie
        """
        # wake up instrument
        self.ts.GetATR()
        target_msg = "Target on %s point(%s) in face %d and press enter or press 's' to skip the point"
        n = 0  # number of faces measured fo far
        while n < self.max_faces:
            if n % 2 == 0:   # face left
                i1 = 1
                i2 = len(self.directions)
                step = 1
            else:            # face right
                i1 = len(self.directions) - 1
                i2 = 0
                step = -1

            for i in range(i1, i2, step):
                if self.directions[i]['faces'] > n:
                    pn = self.directions[i]['id']
                    hz = self.directions[i]['hz'].GetAngle()
                    v = self.directions[i]['v'].GetAngle()
                    if step < 0:
                        # change angles to face right
                        hz = hz - math.pi if hz > math.pi else hz + math.pi 
                        v = PI2 - v
                    j = 0   # try count
                    ans = ''
                    while j < self.maxtry:
                        res = {}
                        if self.directions[i]['code'][0:3] == 'ATR':
                            if j == 0: # first try set target
                                self.ts.SetATR(1)
                                self.ts.SetEDMMode('STANDARD')
                                if len(self.directions[i]['code']) > 3:
                                    self.ts.SetPrismType(int(self.directions[i]['code'][3:]))
                            res = self.ts.Move(Angle(hz), Angle(v), 1)
                            if not 'errorCode' in res:
                                res = self.ts.Measure()
                        elif self.directions[i]['code'][0:2] == 'PR':
                            if j == 0:
                                # prism type: 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini
                                self.ts.SetATR(0)
                                self.ts.SetEDMMode('STANDARD')
                                if len(self.directions[i]['code']) > 2:
                                    self.ts.SetPrismType(int(self.directions[i]['code'][2:]))
                            res = self.ts.Move(Angle(hz), Angle(v), 0)
                            # wait for user to target on point
                            ans = raw_input(target_msg % (pn, self.directions[i]['code'], n % 2 + 1))
                            if ans == 's':
                                j = self.maxtry
                                break
                            res = self.ts.Measure()
                        elif self.directions[i]['code'] == 'RL':
                            self.ts.SetATR(0)
                            self.ts.SetEDMMode('RLSTANDARD')
                            self.ts.Move(Angle(hz), Angle(v), 0)
                            # wait for user to target on point
                            ans = raw_input(target_msg % (pn, self.directions[i]['code'], n % 2 + 1))
                            if ans == 's':
                                j = self.maxtry
                                break
                            res = self.ts.Measure()
                        elif self.directions[i]['code'] == 'RLA':
                            if j == 0:
                                self.ts.SetATR(0)
                                self.ts.SetEDMMode('RLSTANDARD')
                            res = self.ts.Move(Angle(hz), Angle(v), 0)
                            if not 'errorCode' in res:
                                res = self.ts.Measure()
                        elif self.directions[i]['code'] == 'OR':
                            res = self.ts.Move(Angle(hz), Angle(v), 0)
                            # wait for user to target on point
                            ans = raw_input(target_msg % (pn, self.directions[i]['code'], n % 2 + 1))
                            if ans == 's':
                                j = self.maxtry
                                break
                        else:
                            # unknown code skip
                            j = self.maxtry
                            break
                        if 'errorCode' in res:
                            j += 1
                            time.sleep(self.delaytry)
                            continue
                        if self.directions[i]['code'] == 'OR':
                            obs = self.ts.GetAngles()
                        else:
                            obs = self.ts.GetMeasure()
                        if self.ts.measureIface.state != self.ts.measureIface.IF_OK or 'errorCode' in obs:
                            self.ts.measureIface.state = self.ts.measureIface.IF_OK
                            j += 1
                            continue
                        else:
                            break   # observation OK
                    if j >= self.maxtry:
                        logging.error("Cannot measure point %s" % pn)
                        continue
                    obs['id'] = pn
                    obs['station'] = self.directions[0]['station']
                    self.dmp_wrt.WriteData(obs)
                    coo = {}
                    if self.directions[i]['code'] != 'OR':
                        coo['id'] = pn
                        coo['east'], coo['north'], coo['elev'] = self.polar(obs)
                        self.coo_wrt.WriteData(coo)
            n = n + 1
        # rotate back to first point
        self.ts.Move(self.directions[1]['hz'], self.directions[1]['v'], 0)

if __name__ == "__main__":

    import os.path
    from bmp180measureunit import BMP180MeasureUnit
    from i2ciface import I2CIface
    from bmp180 import BMP180
    from webmetmeasureunit import WebMetMeasureUnit
    from webiface import WebIface
    from webmet import WebMet

    if len(sys.argv) > 1:
        ifn = sys.argv[1]
        if not os.path.isfile(ifn):
            print ("Input file doesn't exists:" + ifn)
            exit(-1)
    else:
        print ("Usage: robot.py input_file [output_file] [sensor] [serial_port] [max_try] [delay_try] [BMP180|webmet] [met_addr] [met_par]")
        print ("  or   robot.py config_file.py")
        exit(-1)
    # output file
    if len(sys.argv) > 2:
        ofn = sys.argv[2]
    else:
        ofn = 'stdout'
        #ofn = 'http://192.168.1.108/monitoring/get.php'
        #ofn = 'http://192.168.7.145/monitoring/get.php'
    if not ofn[-4:] in ['.dmp', '.csv', '.geo', '.coo'] and ofn != 'stdout' and ofn[:4] != 'http':
        print "Unknown output type"
        exit(1)
    if len(sys.argv) > 3:
        st = sys.argv[3]
    else:
        st = '1100'
    if len(sys.argv) > 4:
        p = sys.argv[4]
    else:
        p = '/dev/ttyUSB0'
    max_try = 3
    if len(sys.argv) > 5:
        max_try = int(sys.argv[5])
    delay_try = 0
    if len(sys.argv) > 6:
        delay_try = int(sys.argv[6])
    met = None
    if len(sys.argv) > 7 and sys.argv[7].upper() in ["BMP180", "WEBMET"]:
        met = sys.argv[7].upper()
    met_addr = None
    if len(sys.argv) > 8:
        met_addr = sys.argv[8]
    met_par = None
    if len(sys.argv) > 9:
        met_par = sys.argv[9]

    r = Robot(ifn, ofn, st, p, delay_try)
    if r.ts.measureIface.state != r.ts.measureIface.IF_OK:
        exit(-1)   # no serial communication available
    r.ts.GetATR()               # wake up instrument
    # met sensor
    if not met is None:
        atm = r.ts.GetAtmCorr()     # get current settings from ts
        if met == 'BMP180':
            # bmp180 sensor
            bmp_mu = BMP180MeasureUnit()
            i2c = I2CIface(None, 0x77)   # TODO error handling if no sensor
            bmp = BMP180('BMP180', bmp_mu, i2c)
            pres = float(bmp.GetPressure()['pressure'])
            temp = float(bmp.GetTemp()['temp'])
            wet = None    # wet temperature unknown
        else:
            # met data from the net
            wi = WebIface("demo", "http://api.openweathermap.org/data/2.5/weather", "json")
            web_mu = WebMetMeasureUnit(msg="q=budapest&appid=13152b0308b85a39cc9a161e241ec2cf")
            web = WebMet('WebMet', web_mu, wi)
            data = web.GetPressure()
            pres = data['pressure']
            temp = data['temp']
            humi = data['humidity']
            wet = web.GetWetTemp(temp, humi)
        r.ts.SetAtmCorr(float(atm['lambda']), pres, temp, wet)
    r.run()
