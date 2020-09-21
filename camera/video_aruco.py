#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    go through video frames to find an aruco code
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_arucoco.py --help for comamnd line options
"""
import sys
import datetime
import re
import argparse
import matplotlib.pyplot as plt
import numpy as np
import cv2
from aruco_base import ArucoBase

class VideoAruco(ArucoBase):
    """ class to scan ArUco code in video image

        :param args: command line arguments from argparse
    """

    def __init__(self, args):
        """ initialize """
        super(VideoAruco, self).__init__(args)

        if args.name in ("0", "1", "2", "3"):
            self.cap = cv2.videoCapture(int(args.name)) # open camera stream
            if args.fps:
                self.fps = 25
            self.t = datetime.now()
        else:
            fn = args.name[0]
            if re.match('([a-zA-Z])*[0-9]_[0-9]{8}_[0-9]{6}', fn):
                l = fn.split('_')
                self.t = datetime.datetime(int(l[-2][0:4]), int(l[-2][4:6]),
                                           int(l[-2][6:8]), int(l[-1][0:2]),
                                           int(l[-1][2:4]), int(l[-1][4:6]))
                self.tformat = '%Y-%m-%d %H:%M:%S.%f'
            else:
                self.t = datetime.datetime(1970, 1, 1, 0, 0, 0)
                self.tformat = '%H:%M:%S.%f'
            self.cap = cv2.VideoCapture(fn)     # open video file
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if args.fps:
                self.fps = args.fps              # override fps from commandline

    def __del__(self):
        try:
            self.cap.release()
        except:
            pass

    def process(self):
        """ process video frame by frame

            :returns: exit status 0 -OK
        """
        if not self.cap.isOpened():
            print("Error opening video file")
            return 2
        # process video
        i = 0   # frame id
        dt = datetime.timedelta(0, 1.0 / self.fps)
        if self.debug:
            # prepare animated figure
            plt.ion()
        while True:
            # TODO use ulyxes image reader?
            ret, frame = self.cap.read() # get next frame
            if ret:
                res = self.ProcessImg(frame, i)
                if res:
                    if self.calibration:    # output pose, too
                        # TODO use ulyxes writer
                        print("{:d},{:s},{:d},{:d},{:d},{:.6f},{:.6f},{:.6f}".format(i, self.t.strftime(self.tformat), res["east"], res["north"], self.code, res["euler_angles"][0], res["euler_angles"][1], res["euler_angles"][2]))
                    else:
                        print("{:d},{:s},{:d},{:d},{:d}".format(i, self.t.strftime(self.tformat), res["east"], res["north"], self.code))
                else:   # no marker found search whole image next
                    self.last_x = self.last_y = None
                    self.off_y = self.off_x = 0
                i += 1
                self.t += dt
            else:
                break
        return 0

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
        help='video file to process')
    parser.add_argument('-f', '--fps', type=int, default=None,
        help='frame per sec')
    parser.add_argument('-d', '--dict', type=int, default=1,
        help='marker dictionary id, default=1 (DICT_4X4_100)')
    parser.add_argument('-c', '--code', type=int, 
        help='marker id to search, if not given first found marker is used')
    parser.add_argument('--fast', action="store_true",
        help='reduce input image size doubling the marker size at latest found position')
    parser.add_argument('--debug', type=int, default=0,
        help='display every nth frame with marked marker position, default 0 (off)')
    parser.add_argument('-m', '--calibration', type=str, default=None,
        help='use camera calibration from file for undistort image and pose estimation')
    parser.add_argument('-s', '--size', type=float, default=0.28,
        help='marker size for pose extimation, default: 0.28 m')
    parser.add_argument('--hist', action="store_true",
        help='Increase image constrast using histogram')
    parser.add_argument('--lchanel', action="store_true",
        help='Increase image constrast using histogram on lchanel only')
    parser.add_argument('--clip', type=float, default=3.0,
        help='Clip limit for adaptive histogram, use with --hist, default: 3')
    parser.add_argument('--tile', type=int, default=8,
        help='Tile size for adaptive histogram,  use with --hist, default: 8')
    args = parser.parse_args()      # process parameters
    v_a = VideoAruco(args)
    v_a.process()
