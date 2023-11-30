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
import json
import yaml
import numpy as np
import cv2

ALFA = 0    # parameter to getOptimalNewCameraMatrix
            # 0 - original area is preserved without invalid areas
            # 1 - total area preserved with invalid areas

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} calibration_yaml image [image] [...]")
    sys.exit(1)
# load camera calibration data
try:
    with open(sys.argv[1], encoding='ascii') as f:
        if sys.argv[1][-5:].lower() == '.yaml':
            c = yaml.load(f, Loader=yaml.FullLoader)
        else:
            c = json.loads("".join(f.readlines()))
except:
    print(f'Error loading calibration parameters {sys.argv[1]}')
    sys.exit(2)
mtx = np.array(c['camera_matrix'])
dist = np.array(c['dist_coeff'])
cal_w, cal_h = c['img_size']

for fn in sys.argv[2:]:
    # extend wildcards on windows
    for name in glob.glob(fn):
        img = cv2.imread(name)
        if img is not None:
            # undistort
            h, w = img.shape[:2]
            if (cal_w, cal_h) == (w, h):
                newmtx = mtx
            else:
                # scale camera matrix to different resolution
                newmtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist,
                                                            (cal_w, cal_h), ALFA, (w, h))
            dst = cv2.undistort(img, mtx, dist, None, newmtx)
            on = os.path.split(name)
            cv2.imwrite(os.path.join(on[0], 'cal_' + on[1]), dst)
        else:
            print(f'Cannot read image {fn}')
