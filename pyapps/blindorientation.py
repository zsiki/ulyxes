#!/usr/bin/env python
"""
.. module:: blindorientation.py

.. moduleauthor:: Zoltan Siki

Get orientation for totalstation

    :param argv[1]: input coordinate file

    9042 get search area
    9043 set search area
    9040 get spiral
    9041 set spiral
    9047, 9048, 9052, 9051 power search
"""
import sys
import re
import math
import logging

logging.getLogger().setLevel(logging.WARNING)

sys.path.append('../pyapi/')

from angle import Angle, PI2
from totalstation import TotalStation

class Orientation(object):
    """ find prism and orientation from coordinate list

        :param observations: list of observation
        :param ts: totalstation
        :param dist_tol: distance tolerance, default 0.1 m
        :param ang_tol: zenith angle tolerance, default 0.000145 (10 arc min)
    """

    def __init__(self, observations, ts, dist_tol = 0.1, ang_tol = 0.00145):
        """ initialize
        """
        self.dist_tol = dist_tol
        self.ang_tol = ang_tol
        self.step = 3.0 / 180.0 * math.pi   # 3 arc deg
        self.observations = observations
        self.ts = ts

    def FindPoint(self, obs):
        """ Find point from observation (distance and zenith)

            :param obs: observation data
            :returns: orientation angle
        """
        for o in self.observations:
            if 'distance' in o and \
               abs(o['distance'] - obs['distance']) < self.dist_tol and \
               abs((o['v'] - obs['v']).GetAngle()) < self.ang_tol:
                return o['hz']
        return None

    def Search(self):
        """ Search for a prism
        
            :returns: True if orientation set
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
        # instrument targeting on prism?
        ans = self.ts.MoveRel(Angle(0), Angle(0), 1)
        if not 'errorCode' in ans:
            self.ts.Measure()
            obs = self.ts.GetMeasure()
            w = self.FindPoint(obs)
            if not w is None:
                self.ts.SetOri(w)
                return True
        # try to rotate to the second point
        ans = self.ts.Move(self.observations[1]['hz'], \
            self.observations[1]['v'], 1)
        if not 'errorCode' in ans:
            self.ts.Measure()
            obs = self.ts.GetMeasure()
            w = self.FindPoint(obs)
            if not w is None:
                self.ts.SetOri(w)
                return True
        # try blind find
        angles = self.ts.GetAngles()
        act_hz = angles['hz'].GetAngle()
        while dhz < PI2:
            act_v = min_v
            while act_v <= max_v:
                ans = self.ts.Move(Angle(act_hz), Angle(act_v), 1)
                if not 'errorCode' in ans:
                    self.ts.Measure()
                    obs = self.ts.GetMeasure()
                    w = self.FindPoint(obs)
                    if not w is None:
                        self.ts.SetOri(w)
                        return True
                act_v += self.step
            act_hz += self.step
            if act_hz > 2 * math.pi:
                act_hz -= 2* math.pi
            dhz += self.step
        return False

if __name__ == '__main__':
    from serialiface import SerialIface
    from georeader import GeoReader
    from csvreader import CsvReader

    if len(sys.argv) > 1:
        ifname = sys.argv[1]
    else:
        #ifname = 'test.geo'
        print "Usage: blindorientation.py input_file totalstation port"
        sys.exit(-1)
    if ifname[-4:] != '.dmp' and ifname[-4:] != '.geo':
        ifname += '.geo'
    if ifname[-4:] == '.geo':
        g = GeoReader(fname = ifname)
    else:
        g = CsvReader(fname = ifname)
    data = g.Load()
    stationtype = '1100'
    if len(sys.argv) > 2:
        stationtype = sys.argv[2]
    port = '/dev/ttyUSB0'
    if len(sys.argv) > 3:
        port = sys.argv[3]
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
    o = Orientation(data, ts)
    print o.Search()
