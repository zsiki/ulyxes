#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: gamaiface.py
    :platform: Linux, Windows
    :synopsis: interface modul to GNU Gama

.. moduleauthor::Zoltan Siki <siki@agt.bme.hu>
"""

import os
import math
import tempfile
import logging
# for XML
from PyQt4.QtCore import QFile
from PyQt4.QtXml import QDomDocument, QXmlSimpleReader, QXmlInputSource

class GamaIface(object):
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
        if len(self.observations):
            if st:
                o = self.observations.pop()
                while len(self.observations) and o.station is None:
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

        doc = QDomDocument()
        doc.appendChild(doc.createComment('Gama XML created by Ulyxes'))
        gama_local = doc.createElement('gama-local')
        gama_local.setAttribute('version', '2.0')
        doc.appendChild(gama_local)
        network = doc.createElement('network')
        network.setAttribute('axes-xy', 'ne')
        network.setAttribute('angles', 'left-handed')
        gama_local.appendChild(network)
        description = doc.createElement('description')
        if self.dimension == 1:
            description.appendChild(doc.createTextNode('GNU Gama 1D network'))
        elif self.dimension == 2:
            description.appendChild(doc.createTextNode('GNU Gama 2D network'))
        elif self.dimension == 3:
            description.appendChild(doc.createTextNode('GNU Gama 3D network'))
        network.appendChild(description)
        parameters = doc.createElement('parameters')
        parameters.setAttribute('sigma-apr', '1')
        parameters.setAttribute('conf-pr', str(self.probability))
        parameters.setAttribute('tol-abs', '1000')
        parameters.setAttribute('sigma-act', 'aposteriori')
#        parameters.setAttribute('sigma-act', 'apriori')
        parameters.setAttribute('update-constrained-coordinates', 'yes')
        network.appendChild(parameters)
        points_observations = doc.createElement('points-observations')
        points_observations.setAttribute('distance-stdev', str(self.stdev_dist) + ' ' + str(self.stdev_dist1))
        points_observations.setAttribute('direction-stdev', str(self.stdev_angle / 3600.0 * 10000.0))
        points_observations.setAttribute('angle-stdev', str(math.sqrt(2) * self.stdev_angle / 3600.0 * 10000))
        points_observations.setAttribute('zenith-angle-stdev', str(self.stdev_angle / 3600.0 * 10000.0))
        network.appendChild(points_observations)
        for p, s in self.points:
            if self.dimension == 1:
                tmp = doc.createElement('point')
                tmp.setAttribute('id', p['id'])
                if 'elev' in p and p['elev'] is not None:
                    tmp.setAttribute('z', str(p['elev']))
                if s == 'FIX':
                    tmp.setAttribute('fix', 'z')
                else:
                    if fix == 0:
                        tmp.setAttribute('adj', 'Z')
                    else:
                        tmp.setAttribute('adj', 'z')
                points_observations.appendChild(tmp)
            elif self.dimension == 2:
                tmp = doc.createElement('point')
                tmp.setAttribute('id', p['id'])
                if 'east' in p and 'north' in p and \
                    p['east'] is not None and p['north'] is not None:
                    tmp.setAttribute('y', str(p['east']))
                    tmp.setAttribute('x', str(p['north']))
                if s == 'FIX':
                    tmp.setAttribute('fix', 'xy')
                else:
                    if fix == 0:
                        # free network
                        tmp.setAttribute('adj', 'XY')
                    else:
                        tmp.setAttribute('adj', 'xy')
                points_observations.appendChild(tmp)
            elif self.dimension == 3:
                tmp = doc.createElement('point')
                tmp.setAttribute('id', p['id'])
                if 'east' in p and 'north' in p and \
                    p['east'] is not None and p['north'] is not None:
                    tmp.setAttribute('y', str(p['east']))
                    tmp.setAttribute('x', str(p['north']))
                if 'elev' in p and p['elev'] is not None:
                    tmp.setAttribute('z', str(p['elev']))
                if s == 'FIX':
                    tmp.setAttribute('fix', 'xyz')
                else:
                    if fix == 0:
                        tmp.setAttribute('adj', 'XYZ')
                    else:
                        tmp.setAttribute('adj', 'xyz')
                points_observations.appendChild(tmp)
        for o in self.observations:
            if 'station' in o:
                # station record
                sta = doc.createElement('obs')
                sta.setAttribute('from', o['station'])
                # instrument height
                ih = 0
                if 'ih' in o:
                    ih = o['ih']
                points_observations.appendChild(sta)
            else:
                # observation
                th = 0
                if 'th' in o:
                    th = o['th']
                if self.dimension == 2:
                    # horizontal network
                    if 'hz' in o:
                        tmp = doc.createElement('direction')
                        tmp.setAttribute('to', o['id'])
                        tmp.setAttribute('val', str(o['hz'].GetAngle('GON')))
                        sta.appendChild(tmp)
                    if 'distance' in o and 'v' in o:
                        # horizontal distance
                        hd = math.sin(o['v'].GetAngle()) * o['distance']
                        tmp = doc.createElement('distance')
                        tmp.setAttribute('to', o['id'])
                        tmp.setAttribute('val', str(hd))
                        sta.appendChild(tmp)
                elif self.dimension == 1:
                    # elevations only
                    pass
                elif self.dimension == 3:
                    # 3d
                    if 'hz' in o:
                        tmp = doc.createElement('direction')
                        tmp.setAttribute('to', o['id'])
                        tmp.setAttribute('val', str(o['hz'].GetAngle('GON')))
                        sta.appendChild(tmp)
                    if 'distance' in o:
                        tmp = doc.createElement('s-distance')
                        tmp.setAttribute('to', o['id'])
                        tmp.setAttribute('val', str(o['distance']))
                        tmp.setAttribute('from_dh', str(ih))
                        tmp.setAttribute('to_dh', str(th))
                        sta.appendChild(tmp)
                    if 'v' in o:
                        tmp = doc.createElement('z-angle')
                        tmp.setAttribute('to', o['id'])
                        tmp.setAttribute('val', str(o['v'].GetAngle('GON')))
                        tmp.setAttribute('from_dh', str(ih))
                        tmp.setAttribute('to_dh', str(th))
                        sta.appendChild(tmp)
                else:
                    # unknown dimension
                    logging.error("GNU gama unknown dimension")
                    return (None, None)
        # generate temp file name
        f = tempfile.NamedTemporaryFile()
        tmp_name = f.name
        f.close()
        f = open(tmp_name + '.xml', 'w')
        f.write(doc.toByteArray())
        f.close()

        # run gama-local
        status = os.system(self.gama_path + ' ' + tmp_name + '.xml --text ' +
                           tmp_name + '.txt --xml ' + tmp_name + 'out.xml ' +
                           '--cov-band 0')
        if status != 0:
            logging.error("GNU gama failed")
            return (None, None)

        xmlParser = QXmlSimpleReader()
        xmlFile = QFile(tmp_name + 'out.xml')
        xmlInputSource = QXmlInputSource(xmlFile)
        doc = QDomDocument()
        doc.setContent(xmlInputSource, xmlParser)

        # get adjusted coordinates
        adj_nodes = doc.elementsByTagName('adjusted')
        if adj_nodes.count() < 1:
            logging.error("GNU gama no adjusted coordinates")
            return (None, None)
        res = []
        adj_node = adj_nodes.at(0)
        for i in range(len(adj_node.childNodes())):
            pp = adj_node.childNodes().at(i)
            if pp.nodeName() == 'point':
                p = {}
                for ii in range(len(pp.childNodes())):
                    ppp = pp.childNodes().at(ii)
                    if ppp.nodeName() == 'id':
                        p['id'] = str(ppp.firstChild().nodeValue())
                    elif ppp.nodeName() == 'Y' or ppp.nodeName() == 'y':
                        p['east'] = float(ppp.firstChild().nodeValue())
                    elif ppp.nodeName() == 'X' or ppp.nodeName() == 'x':
                        p['north'] = float(ppp.firstChild().nodeValue())
                    elif ppp.nodeName() == 'Z' or ppp.nodeName() == 'z':
                        p['elev'] = float(ppp.firstChild().nodeValue())
                res.append(p)

        adj_nodes = doc.elementsByTagName('orientation-shifts')
        if adj_nodes.count() < 1:
            logging.error("GNU gama no adjusted orientations")
            return (None, None)
        adj_node = adj_nodes.at(0)
        for i in range(len(adj_node.childNodes())):
            pp = adj_node.childNodes().at(i)
            if pp.nodeName() == 'orientation':
                for ii in range(len(pp.childNodes())):
                    ppp = pp.childNodes().at(ii)
                    if ppp.nodeName() == 'id':
                        pid = str(ppp.firstChild().nodeValue())
                        for p in res:
                            if p['id'] == pid:
                                break
                        else:
                            break
                    elif ppp.nodeName() == 'approx':
                        p['appr_ori'] = float(ppp.firstChild().nodeValue())
                    elif ppp.nodeName() == 'adj':
                        p['ori'] = float(ppp.firstChild().nodeValue())

        # std-dev
        # TODO usefull for one unknown point in 3D
        # TODO band must be 0
        adj_nodes = doc.elementsByTagName('cov-mat')
        if adj_nodes.count() < 1:
            logging.error("GNU gama no covariance matrix")
            return (None, None)
        adj_node = adj_nodes.at(0)
        ii = 0
        for i in range(len(adj_node.childNodes())):
            pp = adj_node.childNodes().at(i)
            if pp.nodeName() == 'flt':
                w = float(pp.firstChild().nodeValue())
                if ii == 0:
                    res[0]['std_east'] = math.sqrt(w)
                    ii += 1
                elif ii == 1:
                    res[0]['std_north'] = math.sqrt(w)
                    ii += 1
                elif ii == 2:
                    res[0]['std_elev'] = math.sqrt(w)
                    ii += 1
                elif ii == 3:
                    res[0]['std_ori'] = math.sqrt(w)
                    ii += 1
        adj_nodes = doc.elementsByTagName('observations')
        if adj_nodes.count() < 1:
            logging.error("GNU gama no adjusted observations")
            return (None, None)
        blunder = {'std-residual': 0}
        adj_node = adj_nodes.at(0)
        for i in range(len(adj_node.childNodes())):
            pp = adj_node.childNodes().at(i)
            if pp.nodeName() in ['direction', 'slope-distance', 'zenith-angle']:
                o = {'std-residual': 0}
                for ii in range(len(pp.childNodes())):
                    ppp = pp.childNodes().at(ii)
                    if ppp.nodeName() == 'from':
                        o['from'] = str(ppp.firstChild().nodeValue())
                    elif ppp.nodeName() == 'to':
                        o['to'] = str(ppp.firstChild().nodeValue())
                    elif ppp.nodeName() == 'f':
                        o['f'] = float(ppp.firstChild().nodeValue())
                    elif ppp.nodeName() == 'std-residual':
                        o['std-residual'] = float(ppp.firstChild().nodeValue())
                if o['std-residual'] > self.krit and \
                   o['std-residual'] > blunder['std-residual'] and \
                   o['f'] > 10:     # extra observations ratio
                    blunder = dict(o)
        xmlFile.close()
        # remove input xml and output xml
        os.remove(tmp_name + '.xml')
        os.remove(tmp_name + '.txt')
        os.remove(tmp_name + 'out.xml')

        return (res, blunder)

if __name__ == "__main__":
    """
        unit test
    """
    import sys
    from georeader import GeoReader

    fname = "/home/siki/GeoEasy/data/freestation.geo"
    gama_path = '/home/siki/GeoEasy/gama-local'
    #gama_path = 'gama-local'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    if fname[-4:] != '.geo' and fname[-4:] != '.coo':
        fname += '.geo'
    if not os.path.isfile(fname):
        print("File not found: " + fname)
        exit(-1)
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
        res, blunder = g.adjust()
        if res is not None:
            print(res[0])
        else:
            print("None")
        if blunder is not None:
            print(blunder)
        else:
            print("None")
        if res is None  or 'east' not in res[0] or \
           'north' not in res[0] or 'elev' not in res[0]:
            print("adjustment failed")
            break
        elif blunder is not None and blunder['std-residual'] < 1.0:
            print("blunders removed")
            break
        else:
            print("%s - %s observation removed" % (blunder['from'], blunder['to']))
            g.remove_observation(blunder['from'], blunder['to'])
