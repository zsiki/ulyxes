#!/usr/bin/env python
"""
.. module:: dbwriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

import os.path
import logging
import sqlite3

try:
    import psycopg2
except:
    pass

from angle import Angle
from writer import Writer

class DbWriter(Writer):
    """ Class to write observations/coordinates to a database

            :param db: name of database file or connect string (str)
            :param table: name of table to write (str)
            :param name: name of writer (str)
            :param angle: angle unit to use (str), DMS not supported
            :param dist: distance and coordinate format (str)
            :param dt: date/time format (str), default ansi
            :param filt: list of allowed keys (list)
    """

    def __init__(self, db, table, name=None, angle='GON', dist='.3f',
                 dt='%Y-%m-%d %H:%M:%S', filt=None):
        """ Constructor
        """
        if angle == 'DMS':
            angle = 'GON'
            logging.warning('Angle type changed from DMS to GON')
        super().__init__(name, angle, dist, dt, filt)
        self.db = db
        self.conn = None
        if os.path.isfile(db):
            # connect to sqlite db
            try:
                self.conn = sqlite3.connect(db)
            except Exception:
                logging.fatal('Cannot open database')
        else:
            # connect to postgres
            try:
                self.conn = psycopg2.connect(db)
            except Exception:
                logging.fatal('Cannot open database')
        self.table = table

    def __del__(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def WriteData(self, data):
        """ Write observation data to db

            :param data: dictionary with observation data
        """
        res = 0
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return None
        # add datetime and/or id
        data = self.ExtendData(data)
        # build sql statement
        fields = ""
        values = ""
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                fields += key + ','
                if isinstance(val, (int, float, Angle)):
                    values += self.StrVal(val)
                elif val is None:
                    values += 'NULL'
                else:
                    values += "'" + self.StrVal(val) + "'"
                values += ','
        sqlstr = 'INSERT INTO ' + self.table + '(' + fields[:-1] + ')' + \
            ' VALUES (' + values[:-1] + ');'
        try:
            c = self.conn.cursor()
            c.execute(sqlstr)
            self.conn.commit()
        except Exception as e:
            logging.error(str(e))
            return -1
        return res

if __name__ == "__main__":
    from sys import argv

    if len(argv) > 1:
        db = argv[1]
    else:
        db = ""
    myfile = DbWriter(db=db, table='monitoring_obs')
    data = {'id': '1', 'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), \
            'distance': 123.6581, 'lengthincline': Angle(0.0015, 'GON'), \
            'crossincline': Angle(0.0020, 'GON')}
    print(myfile.WriteData(data))
    myfile = DbWriter(db=db, table='monitoring_coo')
    data = {'id': '1', 'east': 0.12345, 'north': 100.2365, 'elev': 123.6581}
    print(myfile.WriteData(data))
    myfile = DbWriter(db=db, table='monitoring_met')
    data = {'id': '1', 'temp': 12.45, 'pressure': 1017}
    print(myfile.WriteData(data))
