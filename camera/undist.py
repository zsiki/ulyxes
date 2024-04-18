#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
    Undistort images using camera calibration data from yaml file
    command line parameters:
        calibration_data - yamp file with camera matrix and distortion params
        images to undistort
"""
import sys
import os.path
import glob
import argparse
import json
import yaml
import numpy as np
import cv2

ALFA = 0    # parameter to getOptimalNewCameraMatrix
            # 0 - original area is preserved without invalid areas
            # 1 - total area preserved with invalid areas

parser = argparse.ArgumentParser()
parser.add_argument('names', metavar='file_names', type=str, nargs="+",
                    help='image files to undistort')
parser.add_argument('-c', '--calibration', type=str, default=None,
                    help='File name storing calibration info')
parser.add_argument('-w', '--width', type=int, default=None,
                    help='width for target image, pixel, default = source image')
parser.add_argument('-e', '--height', type=int,
                    help='height for target image, pixel, default = source image')
parser.add_argument('-a', '--alfa', type=float, default=ALFA,
                    help=f'alfa parameter, default={ALFA}')
parser.add_argument('-p', '--prefix', type=str, default='cal_',
                    help=f'prefix for output image files, default=cal_')

args = parser.parse_args()
# load camera calibration data
try:
    with open(args.calibration, encoding='ascii') as f:
        if args.calibration[-5:].lower() == '.yaml':
            c = yaml.load(f, Loader=yaml.FullLoader)
        else:
            c = json.loads("".join(f.readlines()))
except:
    print(f'Error loading calibration parameters {args.calibration}')
    sys.exit(2)
mtx = np.array(c['camera_matrix'])
dist = np.array(c['dist_coeff'])
cal_w, cal_h = c['img_size']

for fn in args.names:
    # extend wildcards on windows
    for name in glob.glob(fn):
        img = cv2.imread(name)
        if img is not None:
            # undistort
            h, w = img.shape[:2]
            if args.width is None or args.height is None:
                tw, th = w, h
            else:
                tw, th = args.width, args.height
            # scale camera matrix to different resolution
            newmtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist,
                                                        (w, h), ALFA, (tw, th))
            dst = cv2.undistort(img, mtx, dist, None, newmtx)
            x, y, ww, hh = roi
            dst = dst[y:y+hh, x:x+ww]
            on = os.path.split(name)
            target = os.path.join(on[0], args.prefix + on[1])
            try:
                cv2.imwrite(target, dst)
            except:
                print(f'Cannot write taget image file {target}')
        else:
            print(f'Cannot read image {fn}')
