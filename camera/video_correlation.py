#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    go through video frames to find template and correlation
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_correlation.py --help for comamnd line options
"""

import sys
import os
import datetime
import re
import signal
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

from template_base import TemplateBase
from csvwriter import CsvWriter
from sqlitewriter import SqLiteWriter
from imagereader import ImageReader
from imagewriter import ImageWriter

class VideoCorrelation(TemplateBase):
    """ process video for template matching """

    def __init__(self, args):
        """ initialize """
        super(VideoCorrelation, self).__init__(args)
        fn = args.name[0]
        self.rdr = ImageReader(fn, fps=args.fps)
        self.tformat = '%Y-%m-%d %H:%M:%S.%f'
        if re.search('[0-9]_[0-9]{8}_[0-9]{6}', fn):
            l = fn.split('_')
            self.rdr.act = datetime.datetime(int(l[-2][0:4]), int(l[-2][4:6]),
                                             int(l[-2][6:8]), int(l[-1][0:2]),
                                             int(l[-1][2:4]), int(l[-1][4:6]))
        if re.match('sqlite:', args.output):
            self.wrt = SqLiteWriter(db=args.output[7:],
                                    table='template_coo',
                                    filt=['id', 'datetime', 'east', 'north', 'quality'])
        else:
            self.wrt = CsvWriter(fname=args.output, dt=self.tformat,
                                 filt=['id', 'datetime', 'east', 'north', 'quality'])
        self.img_wrt = None
        if args.img_path:
            self.img_wrt = ImageWriter('', args.img_path, itype=args.img_type)


    def process(self):
        """ process image serie

            :returns: exit status 0 -OK
        """
        # process video
        if self.debug:
            # prepare animated figure
            plt.ion()
        while True:
            frame, t = self.rdr.GetNext() # get next frame
            if frame is None:
                break
            if self.img_wrt:
                self.img_wrt.WriteData(frame)
            res = self.ProcessImg(frame, self.rdr.ind)
            if res:
                data = {'id': self.rdr.ind, 'datetime': t,
                        'east': res["east"], 'north': res["north"],
                        'quality': res['quality']}
                self.wrt.WriteData(data)

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
                        help='video file to process')
    parser.add_argument('-t', '--template', type=str, required=True,
                        help='template image to find in video frames')
    parser.add_argument('-f', '--fps', type=int, default=None,
                        help='frame per sec')
    parser.add_argument('-m', '--method', type=int, default=5,
                        help='method to compare video frame and template, 0/1/2/3/4/5 TM_SQDIFF/TM_SQDIFF_NORMED/TM_CCORR/TM_CCORR_NORMED/CV_TM_CCOEFF/CV_TM_CCOEFF_NORMED, default 5')
    parser.add_argument('-r', '--refresh_template', action="store_true",
                        help='refresh template after each frames')
    parser.add_argument('--fast', action="store_true",
                        help='reduce input image size to double the template')
    parser.add_argument('-d', '--debug', type=int, default=0,
                        help='display every nth frame with marked template position, default 0 (off)')
    parser.add_argument('--delay', type=float, default=0.01,
                        help='delay in seconds between frames in debug')
    parser.add_argument('--calibration', type=str, default=None,
                        help='use camera calibration from file for undistort image and pose estimation')
    parser.add_argument('-o', '--output', type=str, default='stdout',
                        help='name of output file')
    parser.add_argument('-i', '--img_path', type=dir_path,
                        help='path to save images to')
    parser.add_argument('--img_type', type=str, default='png',
                        help='image type to save to, use with --img_path, default png')
    signal.signal(signal.SIGINT, exit_on_ctrl_c)    # catch Ctrl/C
    args = parser.parse_args()      # process parameters
    V_C = VideoCorrelation(args)
    V_C.process()
