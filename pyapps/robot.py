#!/usr/bin/env python
"""
.. module:: robot.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to measure a serie of points.
Command line parameters::

    argv[1]: input file with directions
    argv[2]: output file with observations default stdout
    argv[3]: sensor tcra1103/1100/tca1800/1800/tps1201/1200, default 1200
    argv[4]: serial port, default COM1
    argv[5]: number of retry if target not found, default 3
    argv[6]: delay between retries default 0
    argv[7]: name of met sensor BMP180/webmet, default None
    argv[8]: address of met sensor, i2c addres for BMP180 or internet address of webmet service
    argv[9]: parameters for webmet sensor

Input file is a GeoEasy geo file or a dmp (can be created by filemaker.py
or filegen.py).
Sample geo file::

    {2 S2} {3 0.0}                                   # station id & istrumnt h.
    {5 2} {7 6.283145} {8 1.120836} {4 PR0} {112 2}  # target id, hz, v, code,
    {5 T1} {7 2.022707} {8 1.542995} {4 RL} {112 2}  # number of faces
    {5 3} {7 3.001701} {8 1.611722} {4 OR} {112 2}
    {5 T2} {7 3.006678} {8 1.550763} {4 ATR1} {112 2}
    {5 4} {7 3.145645} {8 1.610680} {4 PR2} {112 2}
    {5 1} {7 6.002123} {8 1.172376} {4 PR} {112 2}
    {5 9} {7 6.235123} {8 1.178538} {4 RLA} {112 2}

    instead of code=4 you can define prism constant using code=20
    prism constant units are meter

Sample dmp file::

    station; id; hz; v; code;faces
    S2;2;6.283145;1.120836;PR0;2
    S2;T1;2.022707;1.542995;RL;2
    S2;3;3.001701;1.611722;OR;2
    S2;T2;3.006678;1.550763;ATR1;2
    S2;4;3.145645;1.610680;PR2;2
    S2;1;6.002123;1.172376;PR;2

Codes describe target type::

    ATRn - prism and automatic targeting, n referes to prism type 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini
    ATR-n - prims and automatictargeting but wait for a keypress to measure
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
import os.path

sys.path.append('../pyapi/')

if sys.version_info[0] > 2: # Python 3 compatibility
    raw_input = input

from angle import Angle, PI2
from serialiface import SerialIface
from csvwriter import CsvWriter
from georeader import GeoReader
from geowriter import GeoWriter
from csvreader import CsvReader
from httpwriter import HttpWriter
from totalstation import TotalStation

class Robot(object):
    """ manage robotic observations

        :param directions: observation directions, dictionary
        :param coordinates: station coordinate, dictionary
        :param ts: instrument, totalstation
        :param maxtry: max retry for a point, default 3
        :param delaytry: delay in seconds between retries, default 0
        :param dirLimit: max angle difference [radians], default 0.015 (5')
        :param distLimit: max slope distance difference [m], default 0.1 m
    """

    def __init__(self, directions, coordinates, ts, maxtry=3, delaytry=0,
                 dirLimit=0.015, distLimit=0.1):
        """ initialize
        """
        if maxtry < 1:
            maxtry = 1
            logging.warning("maxtry changed to 1")
        self.maxtry = maxtry # number of retry if failed
        if delaytry < 0:
            delaytry = 0
            logging.warning("delaytry changed to 0")
        self.delaytry = delaytry # delay between retries
        self.dirLimit = dirLimit
        self.distLimit = distLimit
        self.directions = directions
        self.coordinates = coordinates
        self.ts = ts
        self.max_faces = 0
        for w in self.directions:
            if 'code' not in w:
                w['code'] = 'ATR'
            if 'faces' not in w:
                # default to 1 face
                w['faces'] = 1
            if self.max_faces < w['faces']:
                self.max_faces = w['faces']
        self.station = '???'
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

    def polar(self, obs):
        """ calculate coordinates for target

            :param obs: observed angles and distance
            :returns: (east, north, elev)
        """
        east = self.station_east + obs['distance'] * \
            math.sin(obs['v'].GetAngle()) * math.sin(obs['hz'].GetAngle())
        north = self.station_north + obs['distance'] * \
            math.sin(obs['v'].GetAngle()) * math.cos(obs['hz'].GetAngle())
        elev = self.station_elev + self.ih + obs['distance'] * \
            math.cos(obs['v'].GetAngle())
        return (east, north, elev)

    def run(self):
        """ run an observation serie

            :returns: (obs_out, coo_out)
        """
        target_msg = "Target on point {}({}) in face {} and press Enter/s to measure/skip the point"
        target_msg1 = "Press Enter/b/s to measure/back/skip point {}({}) in face {}"
        wait = False
        n = 0  # number of faces measured fo far
        obs_out = []
        coo_out = []
        # write station record to output
        obs = {'station': self.directions[0]['station'], 'ih': self.ih}
        obs_out.append(obs)
        while n < self.max_faces:
            if n % 2 == 0:   # face left
                i1 = 1
                i2 = len(self.directions)
                step = 1
            else:            # face right
                i1 = len(self.directions) - 1
                i2 = 0
                step = -1
            i = i1
            while i != i2:
                if 'id' in self.directions[i] and \
                    self.directions[i]['faces'] > n:
                    # loop for directfaces
                    for k in range(self.directions[i]['directfaces']):
                        wait = False
                        pn = self.directions[i]['id']
                        hz = self.directions[i]['hz'].GetAngle()
                        v = self.directions[i]['v'].GetAngle()
                        distance = self.directions[i]['distance'] if 'distance' in self.directions[i] else None
                        if (n + k) % 2 == 1:
                            # change angles to face right
                            hz = hz - math.pi if hz > math.pi else hz + math.pi
                            v = PI2 - v
                        j = 0   # try count
                        while j < self.maxtry:
                            ww = ''
                            res = {}
                            code = self.directions[i]['code']
                            if code[0:3] == 'ATR':
                                if j == 0: # first try set target
                                    self.ts.SetATR(1)
                                    self.ts.SetEDMMode('STANDARD')
                                    if code[3:4] == '-':
                                        if k == 0:  #wait only in first face left
                                            wait = True
                                        code = code[0:3] + code[4:]
                                    if len(code) > 3:
                                        self.ts.SetPrismType(int(code[3:]))
                                    elif 'pc' in self.directions[i]:
                                        self.ts.SetPc(self.directions[i]['pc'])
                                res = self.ts.Move(Angle(hz), Angle(v), 1)
                                if 'errorCode' not in res:
                                    if wait:
                                        ww = raw_input(target_msg1.format(pn, self.directions[i]['code'], (n + k) % 2 + 1))
                                        if ww in ['b', 's']:
                                            break
                                    res = self.ts.Measure()
                            elif self.directions[i]['code'][0:2] == 'PR':
                                if j == 0:
                                    # prism type: 0/1/2/3/4/5/6/7
                                    # round/mini/tape/360/user1/user2/user3/360 mini
                                    self.ts.SetATR(0)
                                    self.ts.SetEDMMode('STANDARD')
                                    if len(self.directions[i]['code']) > 2:
                                        self.ts.SetPrismType(int(self.directions[i]['code'][2:]))
                                res = self.ts.Move(Angle(hz), Angle(v), 0)
                                if 'errorCode' not in res:
                                    # wait for user to target on point
                                    ww = raw_input(target_msg.format(pn, self.directions[i]['code'], (n + k) % 2 + 1))
                                    if ww == 's':
                                        break
                                    res = self.ts.Measure()
                            elif self.directions[i]['code'] == 'RL':
                                self.ts.SetATR(0)
                                self.ts.SetEDMMode('RLSTANDARD')
                                self.ts.Move(Angle(hz), Angle(v), 0)
                                if 'errorCode' not in res:
                                    # wait for user to target on point
                                    ww = raw_input(target_msg % (pn, self.directions[i]['code'], (n + k) % 2 + 1))
                                    if ww == 's':
                                        break
                                    res = self.ts.Measure()
                            elif self.directions[i]['code'] == 'RLA':
                                if j == 0:
                                    self.ts.SetATR(0)
                                    self.ts.SetEDMMode('RLSTANDARD')
                                res = self.ts.Move(Angle(hz), Angle(v), 0)
                                if 'errorCode' not in res:
                                    res = self.ts.Measure()
                            elif self.directions[i]['code'] == 'OR':
                                res = self.ts.Move(Angle(hz), Angle(v), 0)
                                if 'errorCode' not in res:
                                    # wait for user to target on point
                                    ww = raw_input(target_msg % (pn, self.directions[i]['code'], (n + k) % 2 + 1))
                                    if ww == 's':
                                        break
                            else:
                                # unknown code skip
                                logging.warning("Invalid code %s(%s)", pn, self.directions[i]['code'])
                                break
                            if 'errorCode' in res:
                                j += 1
                                time.sleep(self.delaytry)
                                continue
                            if self.directions[i]['code'] == 'OR':
                                obs = self.ts.GetAngles()
                            else:
                                obs = self.ts.GetMeasure()
                                # add inclination data to obs
                                w = self.ts.GetAngles()
                                if 'crossincline' in w and 'lengthincline' in w:
                                    obs['crossincline'] = w['crossincline']
                                    obs['lengthincline'] = w['lengthincline']
                            if self.ts.measureIface.state != self.ts.measureIface.IF_OK or 'errorCode' in obs:
                                self.ts.measureIface.state = self.ts.measureIface.IF_OK
                                j += 1
                                continue
                            else:
                                # check false direction
                                if abs(hz - obs['hz'].GetAngle()) > self.dirLimit or \
                                   abs(v - obs['v'].GetAngle()) > self.dirLimit or \
                                   'distance' in obs and distance is not None and \
                                   abs(obs['distance'] - distance) > self.distLimit:
                                    j += 1
                                    logging.warning("False direction %s", pn)
                                    continue    # try again
                                break   # observation OK
                        if j >= self.maxtry:
                            logging.error("Cannot measure point %s", pn)
                            continue
                        if ww in ['b', 's']:
                            break
                        obs['id'] = pn
                        obs['face'] = self.ts.FACE_RIGHT if step < 0 else self.ts.FACE_LEFT
                        obs_out.append(obs)
                        coo = {}
                        if self.directions[i]['code'] != 'OR':
                            coo['id'] = pn
                            coo['east'], coo['north'], coo['elev'] = self.polar(obs)
                            coo_out.append(coo)
                if ww == 'b':
                    i -= step
                    if i not in range(min(i1, i2), max(i1, i2)):
                        i = i1
                else:
                    i += step   # switch to next point
            n = n + 1
        # rotate back to first point
        self.ts.Move(self.directions[1]['hz'], self.directions[1]['v'], 0)
        return (obs_out, coo_out)

if __name__ == "__main__":
    #logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger().setLevel(logging.INFO)

    # process commandline parameters
    config = False
    # input observations
    if len(sys.argv) > 1:
        ifname = sys.argv[1]
        if not os.path.isfile(ifname):
            print("Input file doesn't exists: %s" % ifname)
            exit(-1)
        if ifname[-3:] == '.py':  # configuration file given
            exec('from ' + ifname[:-3] + ' import *')
            config = True
    else:
        print("Usage: robot.py input_file [output_file] [sensor] [serial_port] [max_try] [delay_try] [BMP180|webmet] [met_addr] [met_par]")
        print("  or   robot.py config_file.py")
        exit(-1)
    # output file
    if len(sys.argv) > 2:
        ofname = sys.argv[2]
    elif not config:
        ofname = 'stdout'
    if ofname[-4:] not in ['.dmp', '.csv', '.geo', '.coo'] and \
        ofname != 'stdout' and ofname[:4] != 'http':
        print("Unknown output type")
        exit(1)
    if len(sys.argv) > 3:
        stationtype = sys.argv[3]
    elif not config:
        stationtype = '1100'
    if len(sys.argv) > 4:
        port = sys.argv[4]
    elif not config:
        port = '/dev/ttyUSB0'
    if len(sys.argv) > 5:
        maxtry = int(sys.argv[5])
    elif not config:
        maxtry = 3
    if len(sys.argv) > 6:
        delaytry = int(sys.argv[6])
    elif not config:
        delaytry = 0
    if len(sys.argv) > 7 and sys.argv[7].upper() in ["BMP180", "WEBMET"]:
        met = sys.argv[7].upper()
    elif not config:
        met = None
    if len(sys.argv) > 8:
        met_addr = sys.argv[8]
    elif not config:
        met_addr = None
    if len(sys.argv) > 9:
        met_par = sys.argv[9]
    elif not config:
        met_par = None

    # load input data set
    coo_filt = ['id', 'east', 'north', 'elev', 'pc', 'code']
    if ifname[-4:] in ('.geo', '.coo'):
        g = GeoReader(fname=ifname[:-4] + '.geo')
        f = GeoReader(fname=ifname[:-4] + '.coo', filt=coo_filt)
    else:
        g = CsvReader(fname=ifname[:-4] + '.dmp')
        f = CsvReader(fname=ifname[:-4] + '.csv', filt=coo_filt)
    directions = g.Load()
    coordinates = f.Load()

    # writers
    if ofname[-4:] == '.dmp' or ofname[-4:] == '.csv' or ofname == 'stdout':
        # dmp/csv file or console output
        if ofname[-4:] == '.dmp' or ofname[-4:] == '.csv':
            ofname1 = ofname[:-4] + '.dmp'
            ofname2 = ofname[:-4] + '.csv'
        else:
            ofname1 = ofname2 = ofname
        dmp_wrt = CsvWriter(angle='DMS', dist='.4f', \
            filt=['station', 'id', 'hz', 'v', 'distance', 'datetime'], \
            fname=ofname1, mode='a', sep=';')
        coo_wrt = CsvWriter(dist='.4f', \
            filt=['id', 'east', 'north', 'elev', 'datetime'], \
            fname=ofname2, mode='a', sep=';')
    elif ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
        # geo/coo file output
        if ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
            ofname1 = ofname[:-4] + '.geo'
            ofname2 = ofname[:-4] + '.coo'
        dmp_wrt = GeoWriter(angle='RAD', dist='.4f', \
            filt=['station', 'ih', 'id', 'th', 'hz', 'v', 'distance', \
            'datetime'], fname=ofname1, mode='a')
        coo_wrt = GeoWriter(dist='.4f', \
            filt=['id', 'east', 'north', 'elev', 'datetime'], \
            fname=ofname2, mode='a')
    elif ofname[:5] == 'http:' or ofname[:6] == 'https:':
        # http output
        ofname1 = ofname2 = ofname
        dmp_wrt = HttpWriter(angle='RAD', dist='.4f', \
            filt=['station', 'id', 'hz', 'v', 'distance', 'datetime'], \
            url=ofname1, mode='POST')
        coo_wrt = HttpWriter(angle='RAD', dist='.4f', \
            filt=['id', 'east', 'north', 'elev', 'datetime'], \
            url=ofname2, mode='POST')
    # totalstation
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
    else:
        print("Invalid instrument type: " + stationtype)
        sys.exit()
    # interface to the totalstation
    iface = SerialIface("rs-232", port)
    ts = TotalStation(stationtype, mu, iface)
    if ts.measureIface.state != ts.measureIface.IF_OK:
        print("no serial communication")
        exit(-1)   # no serial communication available
    ts.GetATR()            # wake up instrument
    #ts.SwitchOn(1) TODO              # wake up instrument
    # met sensor
    if met is not None:
        atm = ts.GetAtmCorr()     # get current settings from ts
        if met == 'BMP180':
            from bmp180measureunit import BMP180MeasureUnit
            from i2ciface import I2CIface
            from bmp180 import BMP180
            # bmp180 sensor
            bmp_mu = BMP180MeasureUnit()
            i2c = I2CIface(None, 0x77)
            try:
                bmp = BMP180('BMP180', bmp_mu, i2c)
            except IOError:
                logging.error("BMP180 sensor not found")
                sys.exit(-1)
            pres = float(bmp.GetPressure()['pressure'])
            temp = float(bmp.GetTemp()['temp'])
            wet = None    # wet temperature unknown
        else:
            # met data from the net
            from webmetmeasureunit import WebMetMeasureUnit
            from webmet import WebMet
            from webiface import WebIface
            wi = WebIface("demo", "http://api.openweathermap.org/data/2.5/weather", "json")
            web_mu = WebMetMeasureUnit(msg="q=budapest&appid=13152b0308b85a39cc9a161e241ec2cf")
            web = WebMet('WebMet', web_mu, wi)
            data = web.GetPressure()
            pres = data['pressure']
            temp = data['temp']
            humi = data['humidity']
            wet = web.GetWetTemp(temp, humi)
        ts.SetAtmCorr(float(atm['lambda']), pres, temp, wet)
        logging.info("temperature: %f air pressure: %f wet termperature: %f",
                     temp, pres, wet)
    r = Robot(directions, coordinates, ts, maxtry, delaytry)
    obs_out, coo_out = r.run()
    for obs in obs_out:
        dmp_wrt.WriteData(obs)
    for coo in coo_out:
        coo_wrt.WriteData(coo)
