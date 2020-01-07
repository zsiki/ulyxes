#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: webiface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2015 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen

import json
from iface import Iface

class WebIface(Iface):
    """Class for communicating web page using HTTP GET and json/txt output.

        :param name: name of interface (str)
        :param url: address to read from (str)
    """

    def __init__(self, name, url, fmt, timeout=15):
        """Create an instance of the web interface
        """
        super(WebIface, self).__init__(name)
        self.url = url
        self.fmt = fmt
        self.timeout = timeout

    def Send(self, msg):
        """ send message to web

            :param msg: parameters to url
            :returns: downloaded data
        """
        try:
            response = urlopen(self.url + '?' + msg, timeout=self.timeout)
        except:
            response = None
            data = None
        if response is not None:
            if self.fmt == 'json':
                data = json.load(response)
            else:
                data = response.read()
        return data

if __name__ == "__main__":
    w = WebIface("demo", "http://api.openweathermap.org/data/2.5/weather", "json")
    print(w.Send("q=budapest&appid=13152b0308b85a39cc9a161e241ec2cf"))
    w = WebIface("demo", "http://www.geod.bme.hu/on_line/etrs2eov/etrs2eov.php", "txt")
    print(w.Send("e=650000&n=240000&sfradio=single&format=TXT"))
