#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    go through video frames to find an aruco code
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_arucoco.py --help for comamnd line options
"""
import cv2
import sys
import datetime
import re
import argparse
import matplotlib.pyplot as plt
import numpy as np

aruco = cv2.aruco

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
        help='video file to process')
    parser.add_argument('-f', '--fps', type=int, default=None,
        help='frame per sec')
    parser.add_argument('-d', '--dict', type=int, default=1,
        help='marker dictionary id, default=1 (DICT_4X4_100)')
    parser.add_argument('-c', '--code', type=int, 
        help='marker id to search, if not given all markers are listed')
    parser.add_argument('--fast', action="store_true",
        help='reduce input image size to double the template')
    parser.add_argument('--debug', type=int, default=0,
        help='display every nth frame with marked template position, default 0 (off)')
    args = parser.parse_args()      # process parameters

    # prepare aruco
    params = aruco.DetectorParameters_create()  # TODO set parameters
    if args.dict == 99:     # use special 3x3 dictionary
        aruco_dict = aruco.Dictionary_create(32, 3)
    else:
        aruco_dict = aruco.Dictionary_get(args.dict)

    spec = False
    if args.name in ("0", "1", "2", "3"):
        cap= cv2.videoCapture(int(sys.argv[3])) # open camera stream
        if args.fps:
            fps = 25
        t = datetime.now()
    else:
        fn = args.name[0]
        if re.match('([a-zA-Z])*[0-9]_[0-9]{8}_[0-9]{6}', fn):
            l = fn.split('_')
            t = datetime.datetime(int(l[-2][0:4]), int(l[-2][4:6]), int(l[-2][6:8]),
                int(l[-1][0:2]), int(l[-1][2:4]), int(l[-1][4:6]))
            tformat = '%Y-%m-%d %H:%M:%S.%f'
        else:
            t = datetime.datetime(1970, 1, 1, 0, 0, 0)
            tformat = '%H:%M:%S.%f'
        cap = cv2.VideoCapture(fn)     # open video file
        fps = cap.get(cv2.CAP_PROP_FPS)
        if args.fps:
            fps = args.fps              # override fps from commandline

    if not cap.isOpened():
        print("Error opening video file")
        sys.exit(2)
    # process video
    i = 0   # frame id
    dt = datetime.timedelta(0, 1.0 / fps)
    if args.debug:
        # prepare animated figure
        plt.ion()
    last_x = None
    last_y = None
    off_x = 0
    off_y = 0
    while True:
        ret, frame = cap.read() # get next frame
        if ret:
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if args.fast and last_x:
                off_x = max(0, last_x - templ_w // 2)
                off_y = max(0, last_y - templ_h // 2)
                off_x1 = min(last_x + 3 * templ_w // 2, img_gray.shape[1])
                off_y1 = min(last_y + 3 * templ_h // 2, img_gray.shape[0])
                img_gray = img_gray[off_y:off_y1,off_x:off_x1]
            corners, ids, rejectedImgPoints = aruco.detectMarkers(img_gray,
                aruco_dict, parameters=params)
            found = False
            x = y = 0
            if ids is not None:
                for j in range(ids.size):
                    if ids[j][0] == args.code:
                        # calculate center of aruco code
                        x = int(round(np.average(corners[j][0][:, 0])))
                        y = int(round(np.average(corners[j][0][:, 1])))
                        found = True

            if args.debug and i % args.debug == 0:
                plt.clf()
                plt.imshow(frame)
                plt.plot(x+off_x, y+off_y, "o")
                plt.pause(0.0001)
            if found:
                print("{:d},{:s},{:d},{:d},{:d}".format(i,
                    t.strftime(tformat), x+off_x, y+off_y, args.code))
            i += 1
            t = t + dt
            last_x = x + off_x
            last_y = y + off_y
        else:
            break
    cap.release()
