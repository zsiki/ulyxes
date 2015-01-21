#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: resultlog
    :platform: Linux, Windows
    :synopsis: log file handler

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""
import os
import tempfile
import datetime
import time

class ResultLog(object):
    """ File based logging for Surveying Calculations. Events & calculation results are logged into this file.
    """
    resultlog_message = ""
    
    def __init__(self, logfile, log_level=0, repeat_count=3):
        """ initialize log file if the given file cannot be opened for output then a log.log file in the temperary directory will be used

            :param logfile: name of the log file it will be created if neccessary, messages will be appended to the end
            :param log_level: level of logs 0/1/2 error/warning/debug
            :param repeat_count: retry count on fail accessing log file
        """
        self.repeat_count = repeat_count   # retry count for i/o operations
        self.log_level = log_level         # level of messages
        for i in range(self.repeat_count * 2):
            try:
                f = open(logfile, "a")
                break
            except(IOError):
                f = None
                if i == self.repeat_count:
                    logfile = os.path.join(tempfile.gettempdir(), "log.log")
        f.close()
        self.logfile = logfile

    def reset(self):
        """ Delete content of log file
        """
        for i in range(self.repeat_count):
            try:
                os.remove(self.logfile)
                break
            except(OSError):
                pass

    def write(self, msg = "", level = 0):
        """ Write a  simple message to log

            :param msg: message to write
        """
        if level > self.log_level:
            return

        for i in range(self.repeat_count):
            try:
                f = open(self.logfile, "a")
                for i in range(self.repeat_count):
                    try:
                        f.write(msg + '\n')
                        break
                    except (IOError):
                        pass
                break
            except (IOError):
                pass
        try:
            f.close()
        except (IOError):
            pass

    def write_log(self, msg, level=0):
        """ Write log message with date & time

            :param msg: message to write
        """
        d = time.strftime("%Y-%m-%d %H:%M:%S",
            datetime.datetime.now().timetuple())
        self.write(d + " - " + msg, level)
