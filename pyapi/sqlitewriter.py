#!/usr/bin/env python
"""
.. module:: sqlitewriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

import os.path
import logging
import datetime
import sqlite3
from angle import Angle
from writer import Writer

class SqLiteWriter(Writer):
    """ Class to write observations/coordinates to a local sqlite database

            :param name: name of writer (str)
            :param angle: angle unit to use (str), DMS not supported
            :param dist: distance and coordinate format (str)
            :param dt: date/time format (str), default ansi
            :param filt: list of allowed keys (list)
            :param db: name of database file (str)
    """

    tables = {'coo': 'monitoring_coo', 'obs': 'monitoring_obs', 'met': 'monitoring_met'}

    def __init__(self, db, name = None, angle = 'GON', dist = '.3f', 
                dt = '%Y-%m-%d %H:%M:%S', filt = None):
        """ Constructor
        """
        if angle == 'DMS':
            angle = 'GON'
            logging.warning('Angle type changed from DMS to GON')
        super(SqLiteWriter, self).__init__(name, angle, dist, dt, filt)
        if os.path.isfile(db):
            self.db = db
            # connect to local db
            self.conn = sqlite3.connect(db)
        else:
            logging.fatal('SqLite database does not exists: ' + db)

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass

    def WriteData(self, data):
        """ Write observation data to db

            :param data: dictionary with observation data
        """
        res = 0
        par = {}
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return
        # add datetime and/or id
        data = self.ExtendData(data)
        # select table
        if 'hz' in data:
            table = self.tables['obs']
        elif 'temp'in data:
            table = self.tables['met']
        elif 'east' in data or 'elev' in data:
            table = self.tables['coo']
        # build sql statement
        fields = ""
        values = ""
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                fields += key + ','
                if type(val) is str or type(val) is type(datetime.datetime.now()):
                    values += "'" + self.StrVal(val) + "'"
                else:
                    values += self.StrVal(val)
                values += ','
        sqlstr = 'INSERT INTO ' + table + '(' + fields[:-1] + ')' + \
            ' VALUES (' + values[:-1] + ');'
        c = self.conn.cursor()
        c.execute(sqlstr)
        # TODO error handling-> res
        self.conn.commit()
        return res

if __name__ == "__main__":
    myfile = SqLiteWriter(db = "test.sqlite")
    data = {'id': '1', 'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'distance': 123.6581, 'lengthincline': Angle(0.0015, 'GON'), 'crossincline': Angle(0.0020, 'GON')}
    print (myfile.WriteData(data))
    data = {'id': '1', 'east': 0.12345, 'north': 100.2365, 'elev': 123.6581}
    print (myfile.WriteData(data))
    data = {'id': '1', 'temp': 12.45, 'pressure': 1017}
    print (myfile.WriteData(data))
