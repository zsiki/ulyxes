#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    go through video frames to find an aruco code
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_arucoco.py --help for comamnd line options
"""
import os
import sys
import argparse
import matplotlib.pyplot as plt

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from aruco_base import ArucoBase
from csvwriter import CsvWriter
from imagereader import ImageReader

class ImgsAruco(ArucoBase):
    """ class to scan images for ArUco code

        :param args: command line arguments from argparse
    """

    def __init__(self, args):
        """ initialize """
        # prepare aruco
        super(ImgsAruco, self).__init__(args)
        self.tformat = '%Y-%m-%d %H:%M:%S.%f'
        if self.calibration:
            filt = ['id', 'name', 'datetime', 'east', 'north',
                    'roll', 'pitch', 'yaw']
        else:
            filt = ['id', 'name', 'datetime', 'east', 'north']
        self.wrt = CsvWriter(fname=args.output, dt=self.tformat, filt=filt)
        self.rdr = ImageReader(args.names)

    def process(self):
        """ process images """
        if args.debug:
            # prepare animated figure
            plt.ion()
        while True:
            frame, t = self.rdr.GetNext()
            if frame is not None:
                name1 = os.path.split(self.rdr.srcname)[1]
                res = self.ProcessImg(frame, self.rdr.ind)
                if res:
                    if self.calibration:    # output pose, too
                        data = {'id': self.rdr.ind, 'name': name1,
                                'datetime': t,
                                'east': res["east"], 'north': res["north"],
                                'roll': res["euler_angles"][0],
                                'pitch': res["euler_angles"][1],
                                'yaw': res["euler_angles"][2]}
                    else:
                        data = {'id': self.rdr.ind, 'name': name1,
                                'datetime': t,
                                'east': res["east"], 'north': res["north"]}
                    self.wrt.WriteData(data)
            else:
                break

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('names', metavar='file_names', type=str, nargs="+",
                        help='image files to process')
    parser.add_argument('-d', '--dict', type=int, default=1,
                        help='marker dictionary id, default=1 (DICT_4X4_100)')
    parser.add_argument('-c', '--code', type=int,
                        help='marker id to search, if not given first found marker is used')
    parser.add_argument('--debug', type=int, default=0,
                        help='display every nth frame with marked template position, default 0 (off)')
    parser.add_argument('--delay', type=float, default=1,
                        help='delay in seconds between frames use with debug>0, default 1')
    parser.add_argument('-m', '--calibration', type=str, default=None,
                        help='use camera calibration from file')
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
    parser.add_argument('-o', '--output', type=str, default='stdout',
                        help='name of output file')

    args = parser.parse_args()      # process parameters
    I_A = ImgsAruco(args)
    I_A.process()
    if args.debug > 0:
        input('Press Enter to exit')
