#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    go through video frames to find an aruco code
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264 or ordinal number of camera e.g. 0
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_arucoco.py --help for comamnd line options
"""
import sys
import os
import signal
import datetime
import re
import argparse
import matplotlib.pyplot as plt
from aruco_dict import ARUCO_DICT

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
from sqlitewriter import SqLiteWriter
from imagereader import ImageReader
from imagewriter import ImageWriter

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
        t = re.search('[0-9]_[0-9]{8}_[0-9]{6}', fn)
        t1 = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}', fn)
        t2 = re.search('[0-9]{8}_[0-9]{6}', fn)
        if t:
            # raspivid
            l = t.group()
            self.rdr.act = datetime.datetime(int(l[2:6]), int(l[6:8]),
                                             int(l[8:10]), int(l[11:13]),
                                             int(l[13:15]), int(l[15:]))
        elif t1:
            # dino lite
            l = t1.group()
            self.rdr.act = datetime.datetime(int(l[0:4]), int(l[5:7]),
                                             int(l[8:10]), int(l[11:13]),
                                             int(l[13:15]), int(l[15:]))
        elif t2:
            # mobil
            l = t2.group()
            self.rdr.act = datetime.datetime(int(l[0:4]), int(l[4:6]),
                                             int(l[6:8]), int(l[9:11]),
                                             int(l[11:13]), int(l[13:]))
        if re.match('sqlite:', args.output):
            self.wrt = SqLiteWriter(db=args.output[7:],
                                    table='aruco_coo',
                                    filt=['id', 'datetime', 'east', 'north', 'width', 'height', 'code'])
        else:
            self.wrt = CsvWriter(fname=args.output, dt=self.tformat, mode='w',
                                 filt=['id', 'datetime', 'east', 'north', 'width', 'height', 'code'])
        self.img_wrt = None
        if args.img_path:
            self.img_wrt = ImageWriter('', args.img_path, itype=args.img_type)


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
                if self.img_wrt:
                    self.img_wrt.WriteData(frame, 'gray')
                results = self.ProcessImg(frame, self.rdr.ind)
                if results:
                    for res in results:
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

def dir_path(img_path):
    """ check existence of image path

        :param img_path: path to target folder for images
    """
    if not os.path.isdir(img_path):
        raise argparse.ArgumentTypeError("image path is not valid: " + img_path)
    return img_path

def exit_on_ctrl_c(signal, frame):
    """ catch interrupt (Ctrl/C) and exit gracefully """
    print("\nCtrl/C was pressed, exiting...")
    sys.exit(0)

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='video file to process or camera ID (e.g. 0)')
    parser.add_argument('-f', '--fps', type=int, default=None,
                        help='frame per sec')
    parser.add_argument('-d', '--dict', type=str, default="DICT_4X4_50",
                        help='marker dictionary id or dictionary name, default=1 (DICT_4X4_100)')
    parser.add_argument('-c', '--code', type=int,
                        help='marker id to search, if not given all found markers are detected')
    parser.add_argument('--debug', type=int, default=0,
                        help='display every nth frame with marked marker position, default 0 (off)')
    parser.add_argument('--delay', type=float, default=0.01,
                        help='delay in seconds between frames in debug')
    parser.add_argument('-m', '--calibration', type=str, default=None,
                        help='use camera calibration from file for undistort image and pose estimation')
    parser.add_argument('-s', '--size', type=float, default=0.28,
                        help='marker size for pose extimation, default: 0.28 m')
    parser.add_argument('--hist', action="store_true",
                        help='Increase image constrast using histogram')
    parser.add_argument('--lchanel', action="store_true",
                        help='Increase image constrast using histogram on lchanel only of CIELAB color space, use with --hist')
    parser.add_argument('--refine', action="store_true",
                        help='Refine corners with subpixels')
    parser.add_argument('--clip', type=float, default=3.0,
                        help='Clip limit for adaptive histogram, use with --hist, default: 3')
    parser.add_argument('--tile', type=int, default=8,
                        help='Tile size for adaptive histogram,  use with --hist, default: 8')
    parser.add_argument('-o', '--output', type=str, default='stdout',
                        help='name of output file')
    parser.add_argument('-i', '--img_path', type=dir_path,
                        help='path to save images to')
    parser.add_argument('-t', '--img_type', type=str, default='png',
                        help='image type to save to, use with --img_path, default png')
    signal.signal(signal.SIGINT, exit_on_ctrl_c)    # catch Ctrl/C
    args = parser.parse_args()                      # process parameters
    V_A = VideoAruco(args)
    if V_A.rdr.source is None:
        print("Invalid imput file(s)")
        sys.exit()
    V_A.process()                                   # process images
