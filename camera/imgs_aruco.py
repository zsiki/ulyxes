#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    go through video frames to find an aruco code
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_arucoco.py --help for comamnd line options
"""
import os
import cv2
import sys
import datetime
import re
import argparse
import matplotlib.pyplot as plt
import numpy as np
import yaml

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('names', metavar='file_names', type=str, nargs="+",
        help='image files to process')
    parser.add_argument('-d', '--dict', type=int, default=1,
        help='marker dictionary id, default=1 (DICT_4X4_100)')
    parser.add_argument('-c', '--code', type=int, 
        help='marker id to search, if not given first found marker is used')
    parser.add_argument('--fast', action="store_true",
        help='reduce input image size doubling the marker at latest found position')
    parser.add_argument('--debug', type=int, default=0,
        help='display every nth frame with marked template position, default 0 (off)')
    parser.add_argument('-m', '--calibration', type=str, default=None,
        help='use camera calibration from file')
    args = parser.parse_args()      # process parameters

    # prepare aruco
    params = cv2.aruco.DetectorParameters_create()  # TODO set parameters
#    params.perspectiveRemoveIgnoredMarginPerCell = 0.33
    if args.dict == 99:     # use special 3x3 dictionary
        aruco_dict = cv2.aruco.Dictionary_create(32, 3)
    else:
        aruco_dict = cv2.aruco.Dictionary_get(args.dict)
    if args.calibration:    # load callibration data
        c = yaml.load(f, Loader=yaml.FullLoader)
        tx = np.array(c['camera_matrix'])
        dist = np.array(c['dist_coeff'])

    spec = False
    # process images
    if args.debug:
        # prepare animated figure
        plt.ion()
    last_x = None
    last_y = None
    off_x = 0
    off_y = 0
    for name in args.names:
        name1 = os.path.split(name)[1]
        frame = cv2.imread(name)
        if frame is not None:
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if args.calibration:    # undistort image using calibration
                img_gray = cv2.undistort(img_gray, mtx, dist, None)
            if args.fast and last_x:
                off_x = max(0, last_x - marker_w // 2)
                off_y = max(0, last_y - marker_h // 2)
                off_x1 = min(last_x + 3 * marker_w // 2, img_gray.shape[1])
                off_y1 = min(last_y + 3 * marker_h // 2, img_gray.shape[0])
                img_gray = img_gray[off_y:off_y1,off_x:off_x1]
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(img_gray,
                aruco_dict, parameters=params)
            found = False
            x = y = 0
            if ids is not None:
                for j in range(ids.size):
                    if args.code is None:
                        args.code = ids[j][0] # use first found code
                    if ids[j][0] == args.code:
                        # calculate center of aruco code
                        x = int(round(np.average(corners[j][0][:, 0])))
                        y = int(round(np.average(corners[j][0][:, 1])))
                        marker_w = np.max(corners[j][0][:, 0]) - np.min(corners[j][0][:, 0])
                        marker_h = np.max(corners[j][0][:, 1]) - np.min(corners[j][0][:, 1])
                        found = True

            if args.debug and i % args.debug == 0:
                plt.clf()
                plt.imshow(frame)
                plt.plot(x+off_x, y+off_y, "o")
                plt.pause(0.0001)
            if found:
                print("{:s},{:d},{:d},{:d}".format(name1, x+off_x, y+off_y, ids[j, 0]))
                last_x = x + off_x  # save last position
                last_y = y + off_y
            else:   # no marker found
                last_x = last_y = None
                off_x = off_y = 0
