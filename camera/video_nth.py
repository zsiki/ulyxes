#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    save a given number of images from a video file/chanel from a start frame to
    image files
"""
import cv2
import sys
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # set up command line parameters
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
        help='video file  or input video chanel to process')
    parser.add_argument('-s', '--start', type=int, default=0,
        help='start frame to save from, default 0')
    parser.add_argument('-f', '--frames', type=int, default=1,
        help='number of frames to save, default 1')
    parser.add_argument('-t', '--total', action="store_true",
        help='report total frame number, it ignores --start and --frames')
    # process commentline parameters
    args = parser.parse_args()
    if args.name[0] in ("0", "1", "2", "3"):
        cap= cv2.videoCapture(int(args.name[0])) # open camera stream
        fname = 'chanel{}'.format(args.name[0])
    else:
        cap = cv2.VideoCapture(args.name[0])       # open video file
        fname = os.path.splitext(args.name[0])[0]  # remove extension
    n = args.start
    m = args.frames
    if not cap.isOpened():
        print("Error opening video file")
    else:
        # process video
        i = 0
        while i < (n + m) or args.total:
            ret, frame = cap.read() # get first frame
            if ret:
                if n <= i < n + m and not args.total:
                    cv2.imwrite('{}_{:08d}.png'.format(fname, i), frame)
            else:
                break
            i += 1
    cap.release()
    if args.total:
        print(i)
