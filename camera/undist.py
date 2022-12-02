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
with open(sys.argv[1]) as f:
    try:
        c = yaml.load(f, Loader=yaml.FullLoader)
    except:
        print('Error loading calibration parameters {}'.format(sys.argv[1]))
        sys.exit(2)
    mtx = np.array(c['camera_matrix'])
    dist = np.array(c['dist_coeff'])

for fn in sys.argv[2:]:
    # extend wildcards on windows
    for name in glob.glob(fn):
        img = cv2.imread(name)
        if img is not None:
            # undistort 
            #h, w = img.shape[:2]
            #newmtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist,
            #                                            (w, h), ALFA, (w, h))
            # TODO next line zoom in image!
            #dst = cv2.undistort(img, mtx, dist, None, newmtx)
            dst = cv2.undistort(img, mtx, dist, None)
            on = os.path.split(name)
            cv2.imwrite(os.path.join(on[0], 'cal_' + on[1]), dst)
        else:
            print('Cannot read image {}'.format(fn))
