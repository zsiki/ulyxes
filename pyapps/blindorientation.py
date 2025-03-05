#!/usr/bin/env python
"""
.. module:: blindorientation.py

.. moduleauthor:: Zoltan Siki

Get orientation for totalstation. Command line parameters::

    argv[1]: input coordinate file

"""
import sys
import re
import math
import logging
import os.path

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from angle import Angle, PI2
from totalstation import TotalStation

class Orientation(object):
    """ find prism and orientation from coordinate list

        :param observations: list of observation
        :param ts: totalstation
        :param dist_tol: distance tolerance, default 0.1 m
    """

    def __init__(self, observations, ts, dist_tol=0.1):
        """ initialize
        """
        self.dist_tol = dist_tol
        self.step = 3.0 / 180.0 * math.pi   # 3 arc deg
        self.observations = observations
        self.ts = ts

    def FindPoint(self, obs):
        """ Find point from observation (distance and zenith)
            compering slope distances and heigth differences

            :param obs: observation data
            :returns: bearing to actual instrument direction
        """
        if 'distance' not in obs or 'v' not in obs:
            return None
        d_elev = obs['distance'] * math.cos(obs['v'].GetAngle())
        min_o = None
        mind = 1e10
        # find nearest point
        for o in self.observations:
            if 'distance' in o and 'v' in o:
                d_elev1 = o['distance'] * math.cos(o['v'].GetAngle())
                dd = abs(o['distance'] - obs['distance'])
                de = abs(d_elev1 - d_elev)
                if dd < self.dist_tol and de < self.dist_tol:
                    ddd = math.sqrt(dd * dd + de * de)
                    if mind > ddd:
                        mind = ddd
                        min_o = o
        if min_o:
            return min_o['hz']
        return None

    def Search(self):
        """ Search for a prism

            :returns: dictionary on error with errorCode
        """
        self.ts.GetATR()    # wake up instrument
        dhz = 0 # relative direction from start position
        # find min/max zenith angles
        min_v = math.pi
        max_v = 0
        for obs in self.observations:
            if 'v' in obs:
                if min_v > obs['v'].GetAngle():
                    min_v = obs['v'].GetAngle()
                if max_v < obs['v'].GetAngle():
                    max_v = obs['v'].GetAngle()

        self.ts.SetATR(1)
        self.ts.SetEDMMode('STANDARD')
        ans = self.ts.GetAngles()
        if not 'v' in ans:
            logging.fatal("Check communication line")
            sys.exit(1)
        # move from safe position to first direction
        if ans['v'].GetAngle('DEG') > 160 and ans['v'].GetAngle('DEG') < 200:
            ans = self.ts.Move(self.observations[1]['hz'], \
                self.observations[1]['v'], 0)
        # instrument targeting on prism?
        ans = self.ts.MoveRel(Angle(0), Angle(0), 1)
        if 'errorCode' in ans:
            # try powersearch clockwise
            if 'POWERSEARCH' in self.ts.measureUnit.GetCapabilities():
                # set telescope into the middle in vertical direction
                angles = self.ts.GetAngles()
                self.ts.Move(angles['hz'], Angle((min_v + max_v) / 2.0))
                # repeat power search to skip false prisms
                for i in range(len(self.observations)):
                    ans = self.ts.PowerSearch(1)
                    if 'errorCode' not in ans:
                        self.ts.Measure()
                        obs = self.ts.GetMeasure()
                        w = self.FindPoint(obs)
                        if w is not None:
                            ans = self.ts.SetOri(w)
                            return ans
                    self.ts.MoveRel(Angle(3, 'DEG'), Angle(0))  # move from previous prism
                return {'errCode': 998}    # power search failed stop
            # try to rotate to the second, third, ... point
            i = 2
            while 'errorCode' in ans and i < len(self.observations):
                ans = self.ts.Move(self.observations[i]['hz'], \
                    self.observations[i]['v'], 1)
                i += 1
        if 'errorCode' not in ans:
            self.ts.Measure()
            obs = self.ts.GetMeasure()
            w = self.FindPoint(obs)
            if w is not None:
                ans = self.ts.SetOri(w)
                return ans
        # try blind find
        angles = self.ts.GetAngles()
        if 'errorCode' in angles:
            logging.error("Cannot measure angles")
            return angles
        if 'hz' not in angles:
            logging.error("No Hz got from instrument")
            angles['errorCode'] = 999
            return angles
        act_hz = angles['hz'].GetAngle()
        while dhz < PI2:
            act_v = min_v
            while act_v <= max_v:
                ans = self.ts.Move(Angle(act_hz), Angle(act_v), 1)
                if 'errorCode' not in ans:
                    self.ts.Measure()
                    obs = self.ts.GetMeasure()
                    w = self.FindPoint(obs)
                    if w is not None:
                        ans = self.ts.SetOri(w)
                        return ans
                act_v += self.step
            act_hz += self.step
            if act_hz > 2 * math.pi:
                act_hz -= 2* math.pi
            dhz += self.step
        return {'errCode': -999}

if __name__ == '__main__':
    from serialiface import SerialIface
    from georeader import GeoReader
    from csvreader import CsvReader
    from filegen import ObsGen

    logging.getLogger().setLevel(logging.WARNING)
    if len(sys.argv) > 2:
        ifname = sys.argv[1]
        station = sys.argv[2]
    else:
        #ifname = 'test.geo'
        print("Usage: blindorientation.py coo_file station_name instrument_height totalstation port")
        sys.exit(-1)
    _, ext = os.path.splitext(ifname)
    if ext == '.coo':
        g = GeoReader(fname=ifname)
    elif ext in ('.csv', 'txt'):
        g = CsvReader(fname=ifname, fields=['id', 'east', 'north', 'elev'],
                      numeric=['east', 'north', 'elev']) # csv coordinates
    else:
        print("Invalid input file")
        exit()
    if g.state == g.RD_OPEN:
        sys.exit(2)
    coords = g.Load()
    ih = 0.0
    if len(sys.argv) > 3:
        ih = float(sys.argv[3])
    # generate observations
    og = ObsGen(coords, station, ih)
    obs = og.run()
    stationtype = '1100'
    if len(sys.argv) > 4:
        stationtype = sys.argv[4]
    port = '/dev/ttyUSB0'
    if len(sys.argv) > 5:
        port = sys.argv[5]
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
    ts = TotalStation(stationtype, mu, iface)
    o = Orientation(obs, ts)
    print(o.Search())
