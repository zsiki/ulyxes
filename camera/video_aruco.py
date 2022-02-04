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
from aruco_base import ArucoBase

sys.path.append('../pyapi/')

from csvwriter import CsvWriter
from imagereader import ImageReader

class VideoAruco(ArucoBase):
    """ class to scan ArUco code in video image

        :param args: command line arguments from argparse
    """

    def __init__(self, args):
        """ initialize """
        super(VideoAruco, self).__init__(args)
        fn = args.name[0]
        self.rdr = ImageReader(fn, fps=args.fps)
        self.tformat = '%Y-%m-%d %H:%M:%S.%f'
        if re.search('[0-9]_[0-9]{8}_[0-9]{6}', fn):
            l = fn.split('_')
            self.rdr.act = datetime.datetime(int(l[-2][0:4]), int(l[-2][4:6]),
                                             int(l[-2][6:8]), int(l[-1][0:2]),
                                             int(l[-1][2:4]), int(l[-1][4:6]))
        self.wrt = CsvWriter(fname=args.output, dt=self.tformat,
                             filt=['id', 'datetime', 'east', 'north', 'width', 'height', 'code'])

    def process(self):
        """ process video frame by frame

            :returns: exit status 0 -OK
        """
        # process video
        if self.debug:
            # prepare animated figure
            plt.ion()
        while True:
            frame, t = self.rdr.GetNext() # get next frame
            if frame is not None:
                results = self.ProcessImg(frame, self.rdr.ind)
                if results:
                    for res in results:
                        print(res)
                        if self.code is None or self.code == res['code']:
                            if self.calibration:    # output pose, too
                                data = {'id': self.rdr.ind, 'datetime': t,
                                        'east': res["east"],
                                        'north': res["north"],
                                        'width': res['width'],
                                        'height': res['height'],
                                        'code': res['code'],
                                        'roll': res["euler_angles"][0],
                                        'pitch': res["euler_angles"][1],
                                        'yaw': res["euler_angles"][2]}
                            else:
                                data = {'id': self.rdr.ind, 'datetime': t,
                                        'east': res["east"],
                                        'north': res["north"],
                                        'width': res['width'],
                                        'height': res['height'],
                                        'code': res['code']}
                            self.wrt.WriteData(data)
            else:
                break
        return 0

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='video file to process or camera ID (e.g. 0)')
    parser.add_argument('-f', '--fps', type=int, default=None,
                        help='frame per sec')
    parser.add_argument('-d', '--dict', type=int, default=1,
                        help='marker dictionary id, default=1 (DICT_4X4_100)')
    parser.add_argument('-c', '--code', type=int,
                        help='marker id to search, if not given all found markers are detected')
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
    parser.add_argument('-o', '--output', type=str,
                        help='name of output file')
    args = parser.parse_args()      # process parameters
    V_A = VideoAruco(args)
    V_A.process()
