#!/usr/bin/env python
"""
.. module:: blindorientation.py

.. moduleauthor:: Zoltan Siki

Get coordinates of station using known prism nearby

    argv[1]: input coordinate file
    argv[2]: instrument height, default 0.00

"""

from math import pi, sin, cos, hypot
import numpy as np
from angle import Angle
from filegen import ObsGen
from freestation import Freestation

class AnyStation(object):
    """ calculate station coordinates having no information about 
        station coorcinates and target ids

        :param coords: target coordinates
        :param ts: total station instant
        :param ih: instrument height, default 0.00
    """

    def __init__(self, coords, ts, gama, ih=0.00, dist_tol=0.05):
        """ initialize
        """
        self.coords = coords
        self.ts = ts
        self.gama = gama
        self.ih = ih
        self.dist_tol = dist_tol

    def get_obs(self):
        """ search prism and collect observations

            :returns: observations to found prisms
        """
        obs = []
        act_angle = Angle(0.0)
        ans = self.ts.Move(act_angle, Angle(pi/2))
        last_angle = 0.0
        max = 8
        act = 0
        self.ts.SetEDMMode('STANDARD')
        while act < max:
            ans = self.ts.PowerSearch(1)
            if not 'errorCode' in ans:
                self.ts.Measure()
                o = self.ts.GetMeasure()
                act_angle = o['hz']
                if act_angle.GetAngle() < last_angle:
                    break
                obs.append(o)
                self.ts.Move(act_angle+Angle(3, 'DEG'), Angle(pi/2))  # move forward for next
            act += 1
        return obs

    def get_coords(self, obs):
        """ calculate relative coordinates from station at the origin

            :param obs: observations to points
        """
        rel_coords = []
        for o in obs:
            if 'distance' in o:
                coo = {}
                coo['east'] = o['distance'] * sin(o['v'].GetAngle()) * sin(o['hz'].GetAngle())
                coo['north'] = o['distance'] * sin(o['v'].GetAngle()) * cos(o['hz'].GetAngle())
                coo['elev'] = o['distance'] * cos(o['v'].GetAngle()) + self.ih
                rel_coords.append(coo)
        return rel_coords

    def dist_matrix(self, coords):
        """ calculate distances among points in all combination

            :param coords: input coordinates
            :returns: numpy array with distances
        """
        n = len(coords)
        dm = np.zeros((n, n))
        for i, i_item in enumerate(coords):
            for j, j_item in enumerate(coords):
                if i < j:
                    dm[i, j] = hypot(hypot(i_item['east'] - j_item['east'],
                                           i_item['north'] - j_item['north']),
                                     i_item['elev'] - j_item['elev'])
                else:
                    dm[i, j] = dm[j, i]
        return dm

    def find_dist(self, d, d_mat):
        """ find distances in matrix close to given

            :param d: given distance
            :param d_mat: distance matrix
            :returns: indices of close distances
        """
        n, m = d_mat.shape
        res = []
        for i in range(n):
            for j in range(i+1, m):
                if abs(d_mat[i, j] - d) <= self.dist_tol:
                    res.append((i,j))
        return res

    def highest_freq(self, lst):
        """ find highest frequency in list
        """
        freq = {}
        for item in lst:
            if item in freq:
                freq[item] += 1
            else:
                freq[item] = 1
        max_num = 0
        max_id = None
        for item, num in freq.items():
            if num > max_num:
                max_num = num
                max_id = item
        return max_id

    def run(self):
        """ power search for prism clockwise and calculate
            station coordinates from observations
        """
        if not 'POWERSEARCH' in self.ts.measureUnit.GetCapabilities():
            return None
        obs = self.get_obs()    # measure to prisms
        # -------------------- FOR TESTING -----------------
        #stn = [{'id': '103', 'east': 119.192, 'north': 130.038, 'elev': 120.000}]
        #og = ObsGen(stn + self.coords, '103', self.ih)
        #obs = og.run()[1:]
        # --------------------- END FOR TESTING ------------
        rel_coords = self.get_coords(obs)   # calculate relative coordinates to station
        d_abs = self.dist_matrix(self.coords)
        d_rel = self.dist_matrix(rel_coords)
        # compare distances to find point ids to observations
        n, m = d_rel.shape
        ids = [[] for i in range(n)]    # empty lists to posible point ids
        for i in range(n):
            for j in range(i+1, m):
                dist = d_rel[i, j]
                indices = self.find_dist(dist, d_abs)
                for ind in indices:
                    ids[i].append(self.coords[ind[0]]['id'])
                    ids[i].append(self.coords[ind[1]]['id'])
                    ids[j].append(self.coords[ind[0]]['id'])
                    ids[j].append(self.coords[ind[1]]['id'])
        # get point id by highest frequency in ids lists
        target_ids = [self.highest_freq(i) for i in ids]
        for i, o in enumerate(obs):
            if target_ids is not None:
                o['id'] = target_ids[i]
        obs = [o for o in obs if 'id' in o]
        # add station to obs
        obs = [{'station': 'STATION', 'ih': self.ih}] + obs
        # add station to coords
        coords = [{'id': 'STATION'}] + self.coords
        fs = Freestation(obs, coords, self.gama, 3)   ## TODO gama path, stddev
        return fs.Adjustment()

if __name__ == "__main__":
    from georeader import GeoReader
    from serialiface import SerialIface
    from leicatps1200 import LeicaTPS1200
    from totalstation import TotalStation
    g = GeoReader(fname="../data/test.coo")
    coords = g.Load()
    mu = LeicaTPS1200()
    iface = SerialIface("rs-232", '/dev/ttyUSB0')
    ts = TotalStation('1200', mu, iface)
    a_s = AnyStation(coords, ts, 'gama-local', 0.366, 0.05)
    w = a_s.run()
    print(w)
