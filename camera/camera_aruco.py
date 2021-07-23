#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    go through video frames to find an aruco code
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    usage: camera_arucoco.py config.json
"""
# TODO logging messages

import sys
import os.path
import logging
import time
import matplotlib.pyplot as plt
from aruco_base import ArucoBase

sys.path.append('../pyapi/')

from imagereader import ImageReader
from httpwriter import HttpWriter
from csvwriter import CsvWriter
from dbwriter import DbWriter

class CameraAruco(ArucoBase):
    """ class to scan ArUco code in video image

        :param conf: json file name for parameters
    """

    def __init__(self, conf):
        """ initialize """
        super(CameraAruco, self).__init__(conf)
        self.rdr = ImageReader(self.camera_id, self.fps)
        self.tformat = '%Y-%m-%d %H:%M:%S.%f'
        # select writer
        if self.coo_wr.startswith("http://"):
            self.wrt = HttpWriter(url=self.coo_wr, mode='POST', dist='.4f',
                                  filt=['id', 'datetime', 'east', 'elev'])
        elif self.coo_wr.endswith(".csv"):
            self.wrt = CsvWriter(fname=self.coo_wr, dt=self.tformat,
                                 filt=['id', 'datetime', 'east', 'elev',
                                       'width', 'height', 'code'])
        else:
            self.wrt = DbWriter(db=self.coo_wr, table="monitoring_coo",
                                dist=".4f",
                                filt=['id', 'datetime', 'east', 'elev'])

    def process(self):
        """ process video frame by frame

            :returns: exit status 0 -OK
        """
        # process video
        if self.debug:
            # prepare animated figure
            plt.ion()
        scale = 1   # scale to metric
        t_start = 0 # for delay calculation
        t_end = t_gap = 1.0 / self.fps
        while True:
            # delay for fps
            if self.fps > 0:
                delay_time = t_gap - (t_end - t_start)
                if delay_time > 0.1:
                    print("Sleeping ", delay_time)
                    time.sleep(delay_time)
            t_start = time.perf_counter()
            frame, frame_time = self.rdr.GetNext() # get next frame
            print("New frame at ", str(frame_time))
            if frame is not None:
                res = self.ProcessImg(frame, self.rdr.ind)
                if res:
                    if self.size is not None:
                        scale = self.size / max(res['width'], res['height'])
                    if self.calibration:    # output pose, too
                        data = {'id': self.code, 'datetime': frame_time,
                                'east': res["east"] * scale,
                                'elev': res["north"] * scale,
                                'width': res['width'], 'height': res['height'],
                                'code': self.code,
                                'roll': res["euler_angles"][0],
                                'pitch': res["euler_angles"][1],
                                'yaw': res["euler_angles"][2]}
                    else:
                        data = {'id': self.code, 'datetime': frame_time,
                                'east': res["east"] * scale,
                                'elev': res["north"] * scale,
                                'width': res['width'], 'height': res['height'],
                                'code': self.code}
                    self.wrt.WriteData(data)
                else:   # no marker found search whole image next
                    self.last_x = self.last_y = None
                    self.off_y = self.off_x = 0
            else:
                break
            t_end = time.perf_counter()
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} config.json".format(sys.argv[0]))
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print("Confog file not found: {}".format(sys.argv[1]))
        sys.exit(2)
    C_A = CameraAruco(sys.argv[1])
    logging.basicConfig(format=C_A.log_format, filename=C_A.log_file)
    C_A.process()
