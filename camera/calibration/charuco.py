#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
""" calibrate camera using charuco board 7x5
"""
import sys
import argparse
import yaml
import numpy as np
import cv2

parser = argparse.ArgumentParser()
parser.add_argument('names', metavar='file_names', type=str, nargs='*',
                    help='board images from different directions to process or a video file')
parser.add_argument('-b', '--board', action="store_true",
                    help='save only board image to charuco.png file')
parser.add_argument('-w', '--width', type=int, default=5,
                    help='Width of board, default 5, max 10')
parser.add_argument('-e', '--height', type=int, default=7,
                    help='Height of board, default 7, max 10')
parser.add_argument('-c', '--camera', action="store_true",
                    help='use first camera or video file to take photos until enter pressed')
parser.add_argument('-s', '--save', action="store_true",
                    help='save camera images to file cal0.png, cal1.png if camera is used')
parser.add_argument('-o', '--output', type=str,
                    default="calibration_matrix.yaml",
                    help='output yaml camera calibration data file, default: calibration_matrix.yaml')

args = parser.parse_args()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
board = cv2.aruco.CharucoBoard_create(args.width, args.height, .025, .0125, dictionary)
img = board.draw((200 * args.width, 200 * args.height))
#img = board.draw((1000, 1400))

if args.board:
    # Dump the calibration board to a file
    name = 'charuco_{}x{}.png'.format(args.width, args.height)
    cv2.imwrite(name, img)
    sys.exit()

if not args.names and not args.camera:
    print("neither camera nor input images given")
    parser.print_help()
    sys.exit(0)

allCorners = []
allIds = []
decimator = 0

if args.camera:
    #Start capturing images for calibration
    if len(args.names) == 1 and names[0][-4:] in ("h264", ".mp4", ".avi"):
        cap = cv2.VideoCapture(args.names[0])
    else:
        cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)

        if ids is not None and len(ids) > 0:
            ret, corners1, ids1 = cv2.aruco.interpolateCornersCharuco(corners,
                                                                      ids,
                                                                      gray,
                                                                      board)
            cv2.aruco.drawDetectedMarkers(gray, corners, ids)

        cv2.imshow('frame', gray)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == 13:
            if corners1 is not None and ids1 is not None and len(ids1) > 3:
                allCorners.append(corners1)
                allIds.append(ids1)
            if args.save:
                fn = "cal{:d}.png".format(decimator)
                cv2.imwrite(fn, frame)
            decimator += 1
else:
    # load images from files
    for fn in args.names:
        # read images from files
        frame = cv2.imread(fn)
        if frame is None:
            print('error reading image: {}'.format(fn))
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)
        if ids is not None and len(ids) > 0:
            ret, corners1, ids1 = cv2.aruco.interpolateCornersCharuco(corners,
                                                                      ids,
                                                                      gray,
                                                                      board)
            if ret > 2:
                allCorners.append(corners1)
                allIds.append(ids1)
                decimator += 1

#Calibration fails for lots of reasons. Release the video if we do
try:
    imsize = gray.shape
    ret, mtx, dist, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(allCorners,
                                                                    allIds,
                                                                    board,
                                                                    imsize,
                                                                    None,
                                                                    None)
except:
    if args.camera:
        cap.release()
    print('Calibration failed')
    sys.exit(1)

if args.camera:
    cap.release()
    cv2.destroyAllWindows()
# transform matrix and distortion to writeable lists
print('Overall RMS: {}'.format(ret))
cal = {'camera_matrix': np.asarray(mtx).tolist(),
       'dist_coeff': np.asarray(dist).tolist()}
# and save to file
with open(args.output, "w") as f:
    yaml.dump(cal, f)
#print(cal)
