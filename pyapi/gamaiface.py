#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: gamaiface
    :platform: Linux, Windows
    :synopsis: interface modul to GNU Gama

.. moduleauthor::Zoltan Siki <siki@agt.bme.hu>
"""
import os
import math
import tempfile
from PyQt4.QtCore import QFile
from PyQt4.QtXml import QDomDocument, QXmlSimpleReader, QXmlInputSource
#from angle import Angle

class GamaIface(object):
    """ Interface class to GNU Gama
    """
    def __init__(self, gama_path, dimension=3, probability=0.95, stdev_angle=1, stdev_dist=1, stdev_dist1=1.5):
        """ Initialize a new GamaIface instance.

            :param dimension: dimension of network (int), 1/2/3
            :param probability: porbability for statistical tests (float)
            :param stdev_angle: standard deviation for directions in cc (float)
            :param stdev_dist: base standard deviation for distances mm (float)
            :param stdev_dist1: standard deviation for distances mm/km (float)
        """
        self.dimension = dimension
        self.probability = probability
        self.stdev_angle = stdev_angle
        self.stdev_dist = stdev_dist
        self.stdev_dist1 = stdev_dist1
        self.points = []
        self.observations = []
        if not os.path.isfile(gama_path):
            # TODO log error
            print "gama not found"
            pass
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

    def adjust(self):
        """ Export data to GNU Gama xml, adjust the network and read result

            :returns: result list of adjusment from GNU Gama
        """
        # fix = 0 free network
        fix = sum([1 for p, s in self.points if s == 'FIX'])
        adj = sum([1 for p, s in self.points if s == 'ADJ'])
        if adj == 0 or len(self.observations) == 0:
            # no unknowns or observations
            return None
        
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
        parameters.setAttribute('update-constrained-coordinates', 'yes')
        network.appendChild(parameters)
        points_observations = doc.createElement('points-observations')
        points_observations.setAttribute('distance-stdev', str(self.stdev_dist) + ' ' + str(self.stdev_dist1)) 
        points_observations.setAttribute('direction-stdev', str(self.stdev_angle))
        points_observations.setAttribute('angle-stdev', str(math.sqrt(self.stdev_angle * 2)))
        points_observations.setAttribute('zenith-angle-stdev', str(self.stdev_angle))
        network.appendChild(points_observations)
        for p, s in self.points:
            if self.dimension == 1:
                tmp = doc.createElement('point')
                tmp.setAttribute('id', p['id'])
                if p['elev'] is not None:
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
                if p['east'] is not None and p['north'] is not None:
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
                if p['east'] is not None and p['north'] is not None:
                    tmp.setAttribute('y', str(p['east']))
                    tmp.setAttribute('x', str(p['north']))
                if p['elev'] is not None:
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
                        print o['distance']
                        tmp.setAttribute('val', str(o['distance']))
                        tmp.setAttribute('from_dh', str(ih))
                        tmp.setAttribute('to_dh', str(th))
                        sta.appendChild(tmp)
                    if 'v' in o:
                        tmp = doc.createElement('direction')
                        tmp.setAttribute('to', o['id'])
                        tmp.setAttribute('val', str(o['hz'].GetAngle('GON')))
                        tmp.setAttribute('from_dh', str(ih))
                        tmp.setAttribute('to_dh', str(th))
                        sta.appendChild(tmp)                      
                else:
                    # unknown dimension
                    return None
        #print doc.toprettyxml(indent="  ")
        # generate temp file name
        f = tempfile.NamedTemporaryFile()
        tmp_name = f.name
        f.close()
        f = open(tmp_name + '.xml', 'w')
        f.write(doc.toByteArray())
        f.close()
       
        # run gama-local
        if self.gama_path is None:
            return None
#        status = call([str(self.gama_path), str(tmp_name) + '.xml', '--text',
#            str(tmp_name) + '.txt', '--xml', str(tmp_name) + 'out.xml'])
        print self.gama_path + ' ' + tmp_name + '.xml --text ' + tmp_name + '.txt --xml' + tmp_name + 'out.xml'
        status = os.system(self.gama_path + ' ' + tmp_name + '.xml --text ' +
            tmp_name + '.txt --xml ' + tmp_name + 'out.xml')
        if status != 0:
            return None
        
        xmlParser = QXmlSimpleReader()
        xmlFile = QFile(tmp_name + 'out.xml')
        xmlInputSource = QXmlInputSource(xmlFile)
        doc.setContent(xmlInputSource, xmlParser)
        
        # get adjusted coordinates
        res = []
        adj_nodes = doc.elementsByTagName('adjusted')
        if adj_nodes.count() < 1:
            return res
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
                # TODO return ajusted coordinates
                res.append(p)
        xmlFile.close()
        # remove input xml and output xml
        os.remove(tmp_name + '.xml')
        os.remove(tmp_name + '.txt')
        os.remove(tmp_name + 'out.xml')
        
        return res

if __name__ == "__main__":
    """
        unit test
    """
    import sys
    import os
    from georeader import GeoReader

    fname = "/home/siki/GeoEasy/data/freestation.geo"
    gama_path = '/home/siki/GeoEasy/gama-local'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    if fname[-4:] != '.geo' and fname[-4:] != '.coo':
        fname += '.geo'
    if not os.path.isfile(fname):
        print "File not found: " + fname
        exit(-1)
    fn = fname[:-4] # remove extension
    g = GamaIface(gama_path, 3, 0.95, 1, 1, 1.5)
    coo = GeoReader(fname = fn + '.coo')
    while True:
        w = coo.GetNext()
        if w is None or len(w) == 0:
            break
        if 'id' in w:
            if w['id'] == '1':
                g.add_point(w, 'ADJ')
            else:
                g.add_point(w, 'FIX')
    obs = GeoReader(fname = fn + '.geo')
    while True:
        w = obs.GetNext()
        if w is None or len(w) == 0:
            break
        print w
        if 'station' in w or ('id' in w and 'hz' in w and 'v' in w and 'distance' in w):
            g.add_observation(w)
    res = g.adjust()
    print res
