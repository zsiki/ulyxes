#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    go through image files to find template and correlation
    image file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use imgs_correlation.py --help for comamnd line options
"""
import os
import sys
import datetime
import argparse
import matplotlib.pyplot as plt
import cv2
from template_base import TemplateBase

sys.path.append('../pyapi/')

from csvwriter import CsvWriter

class ImgsCorrelation(TemplateBase):
    """ process a serie of images for template matching """

    def __init__(self, args):
        """ initialize """
        super(ImgsCorrelation, self).__init__(args)
        self.tformat = '%Y-%m-%d %H:%M:%S.%f'
        self.wrt = CsvWriter(fname=args.output, dt=self.tformat,
                             filt=['id', 'name', 'datetime', 'east', 'north'])

    def process(self):
        """ process image serie

        """
        i = 0   # frame id
        if self.debug:
            # prepare animated figure
            plt.ion()
        for name in self.names:
            t = datetime.datetime.fromtimestamp(os.path.getmtime(name))
            name1 = os.path.split(name)[1]
            frame = cv2.imread(name)
            if frame is not None:
                res = self.ProcessImg(frame, i)
                if res:
                    if self.calibration:
                        data = {'id': i, 'name': name1, 'datetime': t,
                                'east': res["east"], 'north': res["north"],
                                'roll': res["euler_angles"][0],
                                'pitch': res["euler_angles"][1],
                                'yaw': res["euler_angles"][2]}
                    else:
                        data = {'id': i, 'name': name1, 'datetime': t,
                                'east': res["east"], 'north': res["north"]}
                    self.wrt.WriteData(data)


if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('names', metavar='file_names', type=str, nargs="+",
        help='image files to process')
    parser.add_argument('-t', '--template', type=str, required=True,
        help='template image to find in video frames')
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
    i_c = ImgsCorrelation(args)
    i_c.process()                   # process files
