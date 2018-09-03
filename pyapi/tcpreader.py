#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: tcpreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Bence Turak <bence.turak@gmail.com>
"""
import logging
from reader import Reader

class TCPReader(Reader):

    def __init__(name, iface, binary=False):
        super(TCPReader, self).__init__(name, iface, size = None)

        file = iface.GetLine(size)
