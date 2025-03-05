#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: gamaiface.py
    :platform: Linux, Windows
    :synopsis: interface modul to GNU Gama
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor::Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

import sys
import os
import math
import re
import tempfile
import logging
# for XML
import xml.etree.ElementTree as ET

class GamaIface():
    """ Interface class to GNU Gama
    """
    def __init__(self, gama_path, dimension=3, probability=0.95, stdev_angle=1,
                 stdev_dist=1, stdev_dist1=1.5):
        """ Initialize a new GamaIface instance.

            :param gama_path: path to gama-local program
            :param dimension: dimension of network (int), 1/2/3
            :param probability: porbability for statistical tests (0.9/0.95/0.997) (float)
            :param stdev_angle: standard deviation for directions in cc (float)
            :param stdev_dist: base standard deviation for distances mm (float)
            :param stdev_dist1: standard deviation for distances mm/km (float)
        """
        self.dimension = dimension
        # limit probability to 90/95/99.7%
        if probability < 0.925:
            self.probability = 0.9
            self.krit = 1.64
        elif probability < 0.975:
            self.probability = 0.95
            self.krit = 1.96
        else:
            self.probability = 0.997
            self.krit = 2.97
        self.stdev_angle = stdev_angle
        self.stdev_dist = stdev_dist
        self.stdev_dist1 = stdev_dist1
        self.points = []
        self.observations = []
        if not (gama_path.startswith('/') or gama_path.startswith('.')):
            # search path for file
            path = os.getenv('PATH')
            for p in path.split(':'):
                if os.path.isfile(os.path.join(p, gama_path):
                    gama_path = os.path.join(p, gama_path)
                    break
        if not os.path.isfile(gama_path):
            logging.error("GNU gama not found")
            gama_path = None
        self.gama_path = gama_path

    def add_point(self, point, state='ADJ'):
        """ Add point to adjustment

            :param point: point to ad network (dic)
            :param state: FIX or ADJ (str)
        """
        if [point, "ADJ"] in self.points or [point, "FIX"] in self.points:
            # avoid duplicated points
            return
        self.points.append([point, state])

    def add_observation(self, obs):
        """ Add observation to adjustment

            :param obs: observation to add (dic)
        """
        self.observations.append(obs)

    def remove_last_observation(self, st=False):
        """ remove last observation or station data

            :param st: False remove single observation, True remove station (Bool)
        """
        if len(self.observations) > 0:
            if st:
                o = self.observations.pop()
                while len(self.observations) > 0  and o.station is None:
                    o = self.observations.pop()
            else:
                self.observations.pop()

    def remove_observation(self, fr, to):
        """ Remove a polar observation
            TODO it erases hz, v and distance
            TODO it removes first occurance
        """
        for o in self.observations:
            if 'station' in o:
                st = o['station']
            elif st == fr and to == o['id']:
                oo = o
                break
        self.observations.remove(oo)

    def adjust(self):
        """ Export data to GNU Gama xml, adjust the network and read result

            :returns: result list of adjusment and blunder from GNU Gama
        """
        # gama-local OK?
        if self.gama_path is None:
            logging.error("GNU gama path is None")
            return (None, None)
        # fix = 0 free network
        fix = sum([1 for p, s in self.points if s == 'FIX'])
        adj = sum([1 for p, s in self.points if s == 'ADJ'])
        if adj == 0 or len(self.observations) < 2:
            # no unknowns or observations
            logging.error("GNU gama no unknowns or not enough observations")
            return (None, None)

        gama_local = ET.Element('gama-local', {'version': '2.0'})
        comment = ET.Comment('Gama XML created by Ulyxes')
        gama_local.append(comment)
        network = ET.SubElement(gama_local, 'network',
            {'axes-xy': 'ne', 'angles': 'left-handed'})
        description = ET.SubElement(network, 'description')
        if self.dimension == 1:
            description.text = 'GNU Gama 1D network'
        elif self.dimension == 2:
            description.text = 'GNU Gama 2D network'
        elif self.dimension == 3:
            description.text = 'GNU Gama 3D network'
        parameters = ET.SubElement(network, 'parameters',
            {'sigma-apr': '1', 'conf-pr': str(self.probability),
            'tol-abs': '1000', 'sigma-act': 'aposteriori'})
            #'update-constrained-coordinates': 'yes'}) gama 2.10!
        points_observations = ET.SubElement(network, 'points-observations',
            {'distance-stdev': str(self.stdev_dist)+' '+str(self.stdev_dist1),
            'direction-stdev': str(self.stdev_angle / 3600.0 * 10000.0),
            'angle-stdev': str(math.sqrt(2)*self.stdev_angle/3600.0*10000),
            'zenith-angle-stdev': str(self.stdev_angle/3600.0*10000.0)})
        for p, s in self.points:
            attr = {}
            if self.dimension == 1:
                attr['id'] = p['id']
                if 'elev' in p and p['elev'] is not None:
                    attr['z'] = str(p['elev'])
                if s == 'FIX':
                    attr['fix'] = 'z'
                else:
                    if fix == 0:
                        attr['adj'] = 'Z'
                    else:
                        attr['adj'] = 'z'
                tmp = ET.SubElement(points_observations, 'point', attr)
            elif self.dimension == 2:
                attr['id'] = p['id']
                if 'east' in p and 'north' in p and \
                    p['east'] is not None and p['north'] is not None:
                    attr['y'] = str(p['east'])
                    attr['x'] = str(p['north'])
                if s == 'FIX':
                    attr['fix'] = 'xy'
                else:
                    if fix == 0:
                        # free network
                        attr['adj'] = 'XY'
                    else:
                        attr['adj'] = 'xy'
                tmp = ET.SubElement(points_observations, 'point', attr)
            elif self.dimension == 3:
                attr['id'] = p['id']
                if 'east' in p and 'north' in p and \
                    p['east'] is not None and p['north'] is not None:
                    attr['y'] = str(p['east'])
                    attr['x'] = str(p['north'])
                if 'elev' in p and p['elev'] is not None:
                    attr['z'] = str(p['elev'])
                if s == 'FIX':
                    attr['fix'] = 'xyz'
                else:
                    if fix == 0:
                        attr['adj'] = 'XYZ'
                    else:
                        attr['adj'] = 'xyz'
                tmp = ET.SubElement(points_observations, 'point', attr)
        for o in self.observations:
            if 'station' in o:
                # station record
                attr = {}
                attr['from'] = o['station']
                # instrument height
                ih = 0
                if 'ih' in o:
                    ih = o['ih']
                sta = ET.SubElement(points_observations, 'obs', attr)
            else:
                # observation
                th = 0
                if 'th' in o:
                    th = o['th']
                if self.dimension == 2:
                    # horizontal network
                    if 'hz' in o:
                        attr = {}
                        attr['to'] = o['id']
                        attr['val'] = str(o['hz'].GetAngle('GON'))
                        tmp = ET.SubElement(sta, 'direction', attr)
                    if 'distance' in o and 'v' in o:
                        # horizontal distance
                        attr = {}
                        hd = math.sin(o['v'].GetAngle()) * o['distance']
                        attr['to'] = o['id']
                        attr['val'] = str(hd)
                        tmp = ET.SubElement(sta, 'direction', attr)
                elif self.dimension == 1:
                    # elevations only
                    pass
                elif self.dimension == 3:
                    # 3d
                    if 'hz' in o:
                        attr = {}
                        attr['to'] = o['id']
                        attr['val'] = str(o['hz'].GetAngle('GON'))
                        tmp = ET.SubElement(sta, 'direction', attr)
                    if 'distance' in o:
                        attr = {}
                        attr['to'] = o['id']
                        attr['val'] = str(o['distance'])
                        attr['from_dh'] = str(ih)
                        attr['to_dh'] = str(th)
                        tmp = ET.SubElement(sta, 's-distance', attr)
                    if 'v' in o:
                        attr = {}
                        attr['to'] = o['id']
                        attr['val'] = str(o['v'].GetAngle('GON'))
                        attr['from_dh'] = str(ih)
                        attr['to_dh'] = str(th)
                        tmp = ET.SubElement(sta, 'z-angle', attr)
                else:
                    # unknown dimension
                    logging.error("GNU gama unknown dimension")
                    return (None, None)
        # generate temp file name
        with tempfile.NamedTemporaryFile() as f:
            tmp_name = f.name
        w = ET.tostring(gama_local).decode('utf-8')
        with open(tmp_name + '.xml', 'w') as f:
            f.write(w)

        # run gama-local
        status = os.system(self.gama_path + ' ' + tmp_name + '.xml --text ' +
                           tmp_name + '.txt --xml ' + tmp_name + 'out.xml ' +
                           '--cov-band 0')
        if status != 0:
            logging.error("GNU gama failed")
            return (None, None)

        doc = ET.parse(tmp_name + 'out.xml')
        root = doc.getroot()

        if not root.tag.endswith("gama-local-adjustment"):
            #return res
            print("***")
        root_tag = re.sub('gama-local-adjustment$', '', root.tag)
        p = {}  # the single adjusted point from result
        blunder = {'std-residual': 0}
        for child in root:
            if root_tag + "coordinates" == child.tag:
                for gchild in child:
                    if root_tag + "adjusted" == gchild.tag:
                        for ggchild in gchild:
                            if root_tag + "point" == ggchild.tag:
                                for pdata in ggchild:
                                    if root_tag + "id" == pdata.tag:
                                        p['id'] = pdata.text
                                    elif root_tag + "y" == pdata.tag:
                                        p['east'] = float(pdata.text)
                                    elif root_tag + "x" == pdata.tag:
                                        p['north'] = float(pdata.text)
                                    elif root_tag + "z" == pdata.tag:
                                        p['elev'] = float(pdata.text)
                    if root_tag + "orientation-shifts" == gchild.tag:
                        for ggchild in gchild:
                            if root_tag + "orientation" == ggchild.tag:
                                for pdata in ggchild:
                                    if root_tag + "approx" == pdata.tag:
                                        p['approx_ori'] = float(pdata.text)
                                    if root_tag + "adj" == pdata.tag:
                                        p['ori'] = float(pdata.text)
                    if root_tag + "cov-mat" == gchild.tag:
                        i = 0
                        idx = ['std_east', 'std_north', 'std_elev', 'std_ori']
                        for ggchild in gchild:
                            if root_tag + "flt" == ggchild.tag:
                                p[idx[i]] = math.sqrt(float(ggchild.text))
                                i += 1
            if root_tag + "observations" == child.tag:
                for gchild in child:
                    o = {'std-residual': 0}
                    if gchild.tag in (root_tag + "direction",
                                      root_tag + "slope-distance",
                                      root_tag + "zenith-angle"):
                        o["type"] = re.sub('^' + root_tag, '', gchild.tag)
                        for ggchild in gchild:
                            if root_tag + "from" == ggchild.tag:
                                o["from"] = ggchild.text
                            if root_tag + "to" == ggchild.tag:
                                o["to"] = ggchild.text
                            if root_tag + "f" == ggchild.tag:
                                o["f"] = float(ggchild.text)
                            if root_tag + "std-residual" == ggchild.tag:
                                o["std-residual"] = float(ggchild.text)
                    if o['std-residual'] > self.krit and \
                       o['std-residual'] > blunder['std-residual'] and \
                       o['f'] > 10:     # extra observations ratio
                        blunder = o

        # remove input xml and output xml
        os.remove(tmp_name + '.xml')
        os.remove(tmp_name + '.txt')
        os.remove(tmp_name + 'out.xml')

        return (p, blunder)

if __name__ == "__main__":
    # unit test
    from georeader import GeoReader

    fname = "/home/siki/GeoEasy_old/data/freestation.geo"
    gama_path = '/home/siki/GeoEasy/src/gama-local'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    if fname[-4:] != '.geo' and fname[-4:] != '.coo':
        fname += '.geo'
    if not os.path.isfile(fname):
        print("File not found: " + fname)
        sys.exit(-1)
    fn = fname[:-4] # remove extension
    g = GamaIface(gama_path, 3, 0.95, 1, 1, 1.5)
    # load coordinates
    coo = GeoReader(fname=fn + '.coo')
    while True:
        w = coo.GetNext()
        if w is None or len(w) == 0:
            break
        if 'id' in w:
            if w['id'] == '1':
                g.add_point(w, 'ADJ')
            else:
                g.add_point(w, 'FIX')
    obs = GeoReader(fname=fn + '.geo')
    # load observations
    while True:
        w = obs.GetNext()
        if w is None or len(w) == 0:
            break
        if 'station' in w or \
            ('id' in w and 'hz' in w and 'v' in w and 'distance' in w):
            g.add_observation(w)
    res = {}
    while True:
        last_res = res
        p, blunder = g.adjust()
        print(p, blunder)
        if p is not None:
            #print(p)
            pass
        else:
            print("None")
        if blunder is not None:
            print(blunder)
        else:
            print("None")
        if p is None  or 'east' not in p or \
           'north' not in p or 'elev' not in p:
            print("adjustment failed")
            break
        if blunder is not None and blunder['std-residual'] < 1.0:
            print("blunders removed")
            break
        print(f"{blunder['from']} - {blunder['to']} observation removed")
        g.remove_observation(blunder['from'], blunder['to'])
