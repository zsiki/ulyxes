#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: queuewriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Bence Turák <turak.bence@epito.bme.hu>
"""

from writer import Writer
import logging
import queue

class QueueWriter(Writer):

    def __init__(self, name=None, angle='GON', dist='.3f', \
                 dt='%Y-%m-%d %H:%M:%S', filt=None):
        '''Class to write queue

                :param name: name of writer (str), default None
                :param angle: angle unit to use (str), default GON
                :param dist: distance and coordinate format (str), default .3f
                :param dt: date/time format (str), dafault ansi
                :param filt: list of keys to output (list), deafult None
        '''
        super(Writer, self).__init__(name, angle, dist)
        self.q = queue.Queue()

    def WriteData(self, data):
        '''Write observation data to queue
                :param data: dictonary with observation data
        '''
        line = {}
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return

        data = self.ExtendData(data)
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                line[key] = val
        try:
            self.q.put(line)
        except:
            logging.error(" queue write failed")
            return -1

        return 0
