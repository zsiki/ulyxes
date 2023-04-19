#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: confreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""
import os
import logging
from jsonreader import JSONReader

class ConfReader(JSONReader):
    """ Class to read json configuration file

            :param name: name of reader (str), default None
            :param fname: name of input file
            :param pars: a dictionary for parameter validation e.g. {key : {}}, valid keys for individual config parameters are: required (True/False), type (int/float/str/list)
    """

    def __init__(self, name=None, fname=None, pars=None):
        """ Constructor
        """
        super().__init__(name, fname)
        self.pars = pars

    def Check(self):
        """ Validate config values and send warning/error to log

            :returns: OK/WARNING/FATAL, msg_lst
        """
        # check for required pars and
        # set default values for missing parameters
        msg_lst = []
        for par in self.pars:
            if self.pars[par]['required'] and par not in self.json:
                msg_lst.append(f"missing required parameter: {par}")
                return 'FATAL', msg_lst
            if 'default' in self.pars[par] and par not in self.json:
                self.json[par] = self.pars[par]['default']
        for par in self.json:
            if par not in self.pars:
                msg_lst.append(f"unknown parameter: {par}")
                continue
            # type checking
            pardef = self.pars[par]
            if self.json[par] is None and pardef['default'] is None:
                # do not check type for None if it is the default
                continue
            if 'type' in pardef:
                if pardef['type'] == 'int' and type(self.json[par]) is not int:
                    msg_lst.append(f"type mismatch parameter: {par}")
                    return 'FATAL', msg_lst
                if pardef['type'] == 'float' and \
                    type(self.json[par]) is not int and \
                    type(self.json[par]) is not float:
                    msg_lst.append(f"type mismatch parameter: {par}")
                    return 'FATAL', msg_lst
                if pardef['type'] == 'list' and \
                    type(self.json[par]) is not list:
                    msg_lst.append(f"type mismatch parameter: {par}")
                    return 'FATAL', msg_lst
                if pardef['type'] == 'file' and \
                    type(self.json[par]) is str and \
                    not os.path.isfile(self.json[par]):
                    msg_lst.append(f"parameter type mismatch or file does not exist: {self.json[par]}")
                    return 'FATAL', msg_lst
                # check set for valid values
                if 'set' in pardef and \
                    self.json[par] not in pardef['set']:
                    msg_lst.append(f"invalid value: {par}")
                    return 'FATAL', msg_lst
        # TODO complex rules e.g. no fix but gama_path given
        if len(msg_lst) > 0:
            return 'WARNING', msg_lst
        return 'OK', msg_lst

if __name__ == '__main__':
    from sys import argv

    CONFIG_PARS = {
        'log_file': {'required' : True, 'type': 'file'},
        'log_level': {'required' : True, 'type': 'int',
                      'set':[logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]},
        'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
        'station_type': {'required' : True, 'type': 'str', 'set': ['1200', '1800', '1100']},
        'station_id': {'required' : True, 'type': 'str'},
        'station_height': {'required': False, 'default': 0, 'type': 'float'},
        'station_coo_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'orientation_limit': {'required': False, 'default': 0.1, 'type': 'float'},
        'faces': {'required': False, 'default': 1, 'type': 'int'},
        'face_coo_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'face_dir_limit': {'required': False, 'default': 0.0029, 'type': 'float'},
        'face_dist_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'directfaces': {'required': False, 'default': 1, 'type': 'int'},
        'avg_faces': {'required': False, 'default': 1, 'type': 'int'},
        'fix_list': {'required': False, 'type': 'list'},
        'mon_list': {'required': False, 'type': 'list'},
        'max_try': {'required': False, 'type': 'int', 'default': 3},
        'delay_try': {'required': False, 'type': 'float', 'default': 0},
        'dir_limit': {'required': False, 'type': 'float', 'default': 0.015},
        'port': {'required' : True, 'type': 'str'},
        'coo_rd': {'required' : True},
        'coo_wr': {'required' : True},
        'obs_wr': {'required': False},
        'met_wr': {'required': False},
        'inf_wr': {'required': False},
        'avg_wr': {'required': False, 'type': 'int', 'default': 1},
        'decimals': {'required': False, 'type': 'int', 'default': 4},
        'gama_path': {'required': False, 'type': 'file'},
        'stdev_angle': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist1': {'required': False, 'type': 'float', 'default': 1.5},
        'dimension': {'required': False, 'type': 'int', 'default': 3},
        'probability': {'required': False, 'type': 'float', 'default': 0.95},
        'blunders': {'required': False, 'type': 'int', 'default': 1},
        'ts_off': {'required': False, 'type': 'int', 'default': 0},
        'met': {'required': False, 'set': ['WEBMET', 'BMP180', 'SENSEHAT']},
        'met_addr': {'required': False},
        'met_par': {'required': False},
        '__comment__': {'required': False, 'type': 'str'}
    }
    FN = '../test/redey.json' if len(argv) < 2 else argv[1]
    JR = ConfReader('test', FN, CONFIG_PARS)
    if JR.state == JR.RD_OK:
        print(JR.Load())
        print(JR.Check())
    else:
        print("config file?")
