#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    OBSOLATE use video_aruco.py

    go through video frames to find an aruco code
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    parameters are given in a json file

    JSON parameters:
        log_file: path to log file (file must exist)
        log_level: 10/20/30/40/50 DEBUG/INFO/WARNING/ERROR/FATAL
        log_format: format for log entries
        station_id: station point ID, optional (str)
        camera_id: camera ID, oprtional (str)
        fps: frame/sec in video file or sampling rate from camera
        dict: ArUco dictionary, default 1 (4x4_100)
        code: ArUco code to search
        size: size of ArUco marked in mm, external size of black border
        calibration: calibration file in yaml format
        hist: histogram enhancement of image, optional (int 0/1), default 0
        lchanel: use l chanel of image, optional, (int 0/1), default 0
        clip: for adaptive threshold, optional, (float), default 3.0
        tile: for adaptive threshold, optional, (int), default 8
        coo_wr: coordinate output (str)
            csv: path to putput file
            sqlite database: path to sqlite database file
            postgres database: connection string to pg
            http: url to remote application over http
        debug: visual feedback, optional (int 0/1), default 0

    usage: camera_aruco.py config.json
"""
# TODO logging messages

import sys
import os.path
import logging
import time
import cv2
import matplotlib.pyplot as plt
from aruco_base import ArucoBase

sys.path.append('../pyapi/')

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
                    #time.sleep(delay_time)
                    key = cv2.waitKey(int(delay_time * 1000)) #& 0xFF
                    print('key: ', key)
                    if key == ord('q'):
                        break
            t_start = time.perf_counter()
            frame, frame_time = self.rdr.GetNext() # get next frame
            print("New frame at ", str(frame_time))
            if frame is not None:
                results = self.ProcessImg(frame, self.rdr.ind)
                for res in results:
                    if self.size is not None:
                        scale = self.size / max(res['width'], res['height'])
                    if self.calibration:    # output pose, too
                        data = {'id': res['code'], 'datetime': frame_time,
                                'east': res["east"] * scale,
                                'elev': res["north"] * scale,
                                'width': res['width'], 'height': res['height'],
                                'roll': res["euler_angles"][0],
                                'pitch': res["euler_angles"][1],
                                'yaw': res["euler_angles"][2]}
                    else:
                        data = {'id': res['code'], 'datetime': frame_time,
                                'east': res["east"] * scale,
                                'elev': res["north"] * scale,
                                'width': res['width'], 'height': res['height']}
                    self.wrt.WriteData(data)
            else:
                break
            t_end = time.perf_counter()
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} config.json".format(sys.argv[0]))
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print("Config file not found: {}".format(sys.argv[1]))
        sys.exit(2)
    C_A = CameraAruco(sys.argv[1])
    logging.basicConfig(format=C_A.log_format, filename=C_A.log_file)
    C_A.process()
