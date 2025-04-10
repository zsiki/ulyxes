#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
""" calibrate camera using charuco board 7x5 or other size
    dictionary with 50 markers the max size is 8 x 11
    use DICT_4X4_250 for larger boards
"""
import sys
import re
import glob
import argparse
import json
import yaml
import numpy as np
import cv2
from cv2 import aruco
import matplotlib.pyplot as plt
from aruco_dict import ARUCO_DICT

SQUARE_LENGTH = 0.025  # chessboard square side length (normally in meters)
MARKER_LENGTH = 0.0125 # marker side length (same unit than squareLength)

# handling incompatibility introduced in openCV 4.8
if float(re.sub(r'^([0-9]+\.[0-9]).*', '\\1', cv2.__version__)) < 4.8:
    aruco.Dictionary = aruco.Dictionary_create
    aruco.getPredefinedDictionary = aruco.Dictionary_get
    aruco.DetectorParameters = aruco.DetectorParameters_create
    aruco.CharucoBoard = aruco.CharucoBoard_create

def extend_names(name_list):
    """ extend */? characters from the command line on windows
    """
    names = []
    for name in name_list:
        if '*' in name or '?' in name:
            names += glob.glob(name)
    return names

def show_markers(name, img, corners, ids):
    """ show image with found markers """
    title = f"{name}, {len(ids)} markers found"
    x = np.zeros(ids.size)
    y = np.zeros(ids.size)
    img1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for j in range(ids.size):
        x[j] = int(round(np.average(corners[j][0][:, 0])))
        y[j] = int(round(np.average(corners[j][0][:, 1])))
        cv2.putText(img1, str(ids[j][0]), (int(x[j]+2), int(y[j])),
                    cv2.FONT_HERSHEY_SIMPLEX, 8, (0, 255, 0), 12)
    plt.imshow(img1)
    plt.plot(x, y, "ro")
    plt.title(title)
    plt.show()

parser = argparse.ArgumentParser()
parser.add_argument('names', metavar='file_names', type=str, nargs='*',
                    help='board images from different directions to process or a video file')
parser.add_argument('-b', '--board', action="store_true",
        help='save only board to image file: charuco_widthxheight.png')
parser.add_argument('-w', '--width', type=int, default=5,
                    help='Width of board, default 5')
parser.add_argument('-e', '--height', type=int, default=7,
                    help='Height of board, default 7')
parser.add_argument('-f', '--format', choices = ['yaml', 'json', 'YAML', 'JSON'], default='yaml',
                    help='Format of output file yaml or json')
parser.add_argument('-m', '--multiplier', type=int, default=200,
                    help='Multiplier for board printing to set size in pixels, default 200')
parser.add_argument('-c', '--camera', action="store_true",
                    help='use first camera or video file to take photos until enter pressed')
parser.add_argument('-s', '--save', action="store_true",
                    help='save camera images to file cal0.png, cal1.png if camera is used')
parser.add_argument('-o', '--output', type=str,
                    default="calibration_matrix",
                    help='output yaml/json camera calibration data file, default: calibration_matrix.yaml')
parser.add_argument('-d', '--dictionary', type=str, default="DICT_4X4_100",
                    help='ArUco dictionary name or index, default DICT_4X4_100')
parser.add_argument('-m', '--min', type=int, default=20,
                    help='Minimal number of points on an image, default 20')
parser.add_argument('--debug', action="store_true",
                    help='Display found ArUco codes')

args = parser.parse_args()
if sys.platform.startswith('win'):
    args.names = extend_names(args.names)
wid = -1
try:
    wid = int(args.dictionary)
except ValueError:
    if args.dictionary in ARUCO_DICT:
        wid = ARUCO_DICT[args.dictionary]
if wid not in ARUCO_DICT.values():
    print("Unkonw ArUco dictionary name or index")
    print("Valid names/indices are:")
    for key, value in ARUCO_DICT.items():
        print(f"{value:2d} {key}")
    sys.exit()
dictionary = aruco.getPredefinedDictionary(wid)
if float(re.sub(r'^([0-9]+\.[0-9]).*', '\\1', cv2.__version__)) < 4.8:
    board = aruco.CharucoBoard_create(args.width, args.height,
            SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    img = board.draw((args.multiplier * args.width, args.multiplier * args.height))
else:
    board = aruco.CharucoBoard((args.width, args.height),
            SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    img = board.generateImage((args.multiplier * args.width, args.multiplier * args.height))

if args.board:
    # Dump the calibration board to a file
    name = 'charuco_{}x{}.png'.format(args.width, args.height)
    cv2.imwrite(name, img)
    sys.exit()

if not args.names and not args.camera:
    print("neither camera nor input images are given")
    parser.print_help()
    sys.exit(0)

allCorners = []
allIds = []
decimator = 0

if args.camera:
    #Start capturing images for calibration
    if len(args.names) == 1 and args.names[0][-4:] in ("h264", ".mp4", ".avi"):
        cap = cv2.VideoCapture(args.names[0])
    else:
        cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if float(re.sub(r'^([0-9]+\.[0-9]).*', '\\1', cv2.__version__)) < 4.8:
            corners, ids, _ = aruco.detectMarkers(gray, dictionary)
        else:
            detector = cv2.aruco.ArucoDetector(dictionary)
            corners, ids, _ = detector.detectMarkers(gray)
        if args.debug:
            show_markers("On-line camera", frame, corners, ids)
        if ids is not None and len(ids) > 0:
            if float(re.sub(r'^([0-9]+\.[0-9]).*', '\\1', cv2.__version__)) < 4.8:
                ret, corners1, ids1 = aruco.interpolateCornersCharuco(corners,
                                                                      ids,
                                                                      gray,
                                                                      board)
            else:
                ch_detector = aruco.CharucoDetector(board)
                ret, corners1, ids1 = ch_detector.detectBoard(gray, corners, ids)
            #aruco.drawDetectedMarkers(gray, corners, ids)

        #cv2.imshow('frame', gray)
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
    for fn in sorted(args.names):
        # read images from files
        frame = cv2.imread(fn)
        if frame is None:
            print('error reading image: {}'.format(fn))
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if float(re.sub(r'^([0-9]+\.[0-9]).*', '\\1', cv2.__version__)) < 4.8:
            corners, ids, _ = aruco.detectMarkers(gray, dictionary)
        else:
            detector = cv2.aruco.ArucoDetector(dictionary)
            corners, ids, _ = detector.detectMarkers(gray)

        if args.debug:
            show_markers(fn, frame, corners, ids)
        if ids is not None and len(ids) > 0:
            if float(re.sub(r'^([0-9]+\.[0-9]).*', '\\1', cv2.__version__)) < 4.8:
                ret, corners1, ids1 = aruco.interpolateCornersCharuco(corners,
                                                                      ids,
                                                                      gray,
                                                                      board)
            else:
                ch_detector = aruco.CharucoDetector(board)
                corners1, ids1, _, _ = ch_detector.detectBoard(gray)
                ret = len(corners1)
            if ret > args.min:
                allCorners.append(corners1)
                allIds.append(ids1)
                decimator += 1
            else:
                print(f"{fn} skipped")

#Calibration fails for lots of reasons. Release the video if we do
try:
    imsize = gray.shape[::-1]   #min(gray.shape), max(gray.shape)
    ret, mtx, dist, rvecs, tvecs = aruco.calibrateCameraCharuco(allCorners,
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
print(f'Overall RMS: {ret}')
cal = {'camera_matrix': np.asarray(mtx).tolist(),
       'dist_coeff': np.asarray(dist).tolist(),
       'img_size': list(imsize),
       'rms': ret}
# and save to file
if args.output[-4:].lower() != args.format.lower():
    args.output += '.' + args.format
with open(args.output, "w", encoding='ascii') as f:
    if args.format.lower() == 'yaml':
        yaml.dump(cal, f)
    else:
        json.dump(cal, f)
#print(cal)
