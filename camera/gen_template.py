#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    generate template for template matching from the first frame with aruco
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_arucoco.py --help for comamnd line options
"""
import sys
import datetime
import re
import os.path
import argparse
from aruco_base import ArucoBase

sys.path.append('../pyapi/')

from imagereader import ImageReader
from imagewriter import ImageWriter

class VideoTemplateGen(ArucoBase):
    """ class to scan ArUco code in video image

        :param args: command line arguments from argparse
    """

    def __init__(self, args):
        """ initialize """
        super(VideoTemplateGen, self).__init__(args)
        fn = args.name[0]
        self.rdr = ImageReader(fn, fps=args.fps)
        self.wrt = ImageWriter(os.path.basename(fn), os.path.dirname(fn))
        self.tformat = '%Y-%m-%d %H:%M:%S.%f'
        if re.search('[0-9]_[0-9]{8}_[0-9]{6}', fn):
            l = fn.split('_')
            self.rdr.act = datetime.datetime(int(l[-2][0:4]), int(l[-2][4:6]),
                                             int(l[-2][6:8]), int(l[-1][0:2]),
                                             int(l[-1][2:4]), int(l[-1][4:6]))
        self.calibration = None

    def process(self):
        """ process video frame by frame until a code found

            :returns: exit status 0 -OK
        """
        # process video
        name = "NotFound"
        while True:
            frame, _ = self.rdr.GetNext() # get next frame
            if frame is None:
                break
            res = self.ProcessImg(frame, self.rdr.ind)
            if res:     # aruco found
                east = res["east"]
                north = res["north"]
                width2 = int(res['width'] * 1.1 / 2)
                height2 = int(res['height'] * 1.1 / 2)
                data = frame[east-width2:east+width2, north-height2:north+height2]
                name = self.wrt.WriteData(data)
                break
        return name

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='video file to processi or camera ID (e.g. 0)')
    parser.add_argument('-d', '--dict', type=int, default=1,
                        help='marker dictionary id, default=1 (DICT_4X4_100)')
    parser.add_argument('-m', '--calibration', type=str, default=None,
                        help='dummy arg for compatibility')
    parser.add_argument('--debug', type=int, default=0,
                        help='dummy arg for compatibility')
    parser.add_argument('--clip', type=float, default=3.0,
                        help='dummy arg for compatibility')
    parser.add_argument('--tile', type=int, default=8,
                        help='dummy arg for compatibility')
    parser.add_argument('--fast', action="store_true",
                        help='dummy arg for compatibility')
    parser.add_argument('--hist', action="store_true",
                        help='dummy arg for compatibility')
    parser.add_argument('--lchanel', action="store_true",
                        help='dummy arg for compatibility')
    parser.add_argument('-s', '--size', type=float, default=0.28,
                        help='dummy arg for compatibility')
    parser.add_argument('-f', '--fps', type=int, default=None,
                        help='dummy arg for compatibility')
    parser.add_argument('-c', '--code', type=int,
                        help='marker id to search, if not given first found marker is used')
    args = parser.parse_args()      # process parameters
    V_A = VideoTemplateGen(args)
    print(V_A.process())
