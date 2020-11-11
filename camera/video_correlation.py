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
sys.path.append('../pyapi/')

import datetime
import re
import argparse
import matplotlib.pyplot as plt
from template_base import TemplateBase
from csvwriter import CsvWriter

class VideoCorrelation(TemplateBase):
    """ process video for template matching """

    def __init__(self, args):
        """ initialize """
        super(VideoCorrelation, self).__init__(args)
        fn = args.name[0]
        self.tformat = '%Y-%m-%d %H:%M:%S.%f'
        if re.search('[0-9]_[0-9]{8}_[0-9]{6}', fn):
            l = fn.split('_')
            self.rdr.act = datetime.datetime(int(l[-2][0:4]), int(l[-2][4:6]),
                                             int(l[-2][6:8]), int(l[-1][0:2]),
                                             int(l[-1][2:4]), int(l[-1][4:6]))
        self.wrt = CsvWriter(fname=args.output, dt=self.tformat,
                             filt=['id', 'datetime', 'east', 'north'])

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
            if frame is not None:
                res = self.ProcessImg(frame, self.rdr.ind)
                if res:
                    if self.calibration: # output pose too
                        data = {'id': self.rdr.ind, 'datetime': t,
                                'east': res["east"], 'north': res["north"],
                                'roll': res["euler_angles"][0],
                                'pitch': res["euler_angles"][1],
                                'yaw': res["euler_angles"][2]}
                    else:
                        data = {'id': self.rdr.ind, 'datetime': t,
                                'east': res["east"], 'north': res["north"]}
                    self.wrt.WriteData(data)
            else:
                break

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
    parser.add_argument('--calibration', type=str, default=None,
                        help='use camera calibration from file for undistort image and pose estimation')
    parser.add_argument('-o', '--output', type=str,
                        help='name of output file')

    args = parser.parse_args()      # process parameters
    V_C = VideoCorrelation(args)
    V_C.process()
