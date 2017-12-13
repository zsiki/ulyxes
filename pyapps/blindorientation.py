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


sys.path.append('../pyapi/')

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
        for o in self.observations:
            if 'distance' in o and 'v' in o:
                d_elev1 = o['distance'] * math.cos(o['v'].GetAngle())
                if abs(o['distance'] - obs['distance']) < self.dist_tol and \
                   abs(d_elev1 - d_elev) < self.dist_tol:
                    return o['hz']
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
        # move from safe position to first direction
        if ans['v'].GetAngle('DEG') > 160 and ans['v'].GetAngle('DEG') < 200:
            ans = self.ts.Move(self.observations[1]['hz'], \
                self.observations[1]['v'], 0)
        # instrument targeting on prism?
        ans = self.ts.MoveRel(Angle(0), Angle(0), 1)
        if 'errorCode' in ans:
            # try to rotate to the second, third, ... point
            i = 2
            while 'errorCode' in ans and i < len(self.observations):
                ans = self.ts.Move(self.observations[i]['hz'], \
                    self.observations[i]['v'], 1)
                i += 1
            if 'errorCode' in ans:
                # try powersearch clockwise
                if 'POWERSEARCH' in self.ts.measureUnit.GetCapabilities():
                    # set telescope into the middle in vertical direction
                    angles = self.ts.GetAngles()
                    self.ts.Move(angles['hz'], Angle((min_v + max_v) / 2.0))
                    # repeat power search to skip false prisms
                    for i in range(10):
                        ans = self.ts.PowerSearch(1)
                        if 'errorCode' not in ans:
                            self.ts.Measure()
                            obs = self.ts.GetMeasure()
                            w = self.FindPoint(obs)
                            if w is not None:
                                ans = self.ts.SetOri(w)
                                return ans
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

    logging.getLogger().setLevel(logging.WARNING)
    if len(sys.argv) > 1:
        ifname = sys.argv[1]
    else:
        #ifname = 'test.geo'
        print "Usage: blindorientation.py input_file totalstation port"
        sys.exit(-1)
    if ifname[-4:] != '.dmp' and ifname[-4:] != '.geo':
        ifname += '.geo'
    if ifname[-4:] == '.geo':
        g = GeoReader(fname=ifname)
    else:
        g = CsvReader(fname=ifname)
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
