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
import yaml
import numpy as np
import cv2

if len(sys.argv) < 3:
    print("Usage: calibration_yaml image [image] [...]")
    sys.exit(1)
with open(sys.argv[1]) as f:
    try:
        c = yaml.load(f, Loader=yaml.FullLoader)
    except:
        print('Error loading calibration parameters {}'.format(sys.argv[1]))
        sys.exit(2)
    mtx = np.array(c['camera_matrix'])
    dist = np.array(c['dist_coeff'])

for fn in sys.argv[2:]:
    img = cv2.imread(fn)
    if img:
        # undistort
        dst = cv2.undistort(img, mtx, dist, None)
        on = os.path.split(fn)
        cv2.imwrite(os.path.join(on[0], 'cal_' + on[1]), dst)
    else:
        print('Cannot read image {}'.format(fn))
