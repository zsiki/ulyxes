#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
""" calibrate camera using charuco board 7x5
"""
import sys
import glob
import argparse
import yaml
import numpy as np
import cv2
from cv2 import aruco
import matplotlib.pyplot as plt
from aruco_dict import ARUCO_DICT

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
    print(title)
    x = np.zeros(ids.size)
    y = np.zeros(ids.size)
    img1 = img.copy()
    for j in range(ids.size):
      x[j] = int(round(np.average(corners[j][0][:, 0])))
      y[j] = int(round(np.average(corners[j][0][:, 1])))
      cv2.putText(img1, str(ids[j][0]), (int(x[j]+2), int(y[j])), cv2.FONT_HERSHEY_SIMPLEX, 8, (0, 255, 0), 12)
    plt.imshow(img1)
    plt.plot(x, y, "ro")
    plt.title(title)
    plt.show()

parser = argparse.ArgumentParser()
parser.add_argument('names', metavar='file_names', type=str, nargs='*',
                    help='board images from different directions to process or a video file')
parser.add_argument('-b', '--board', action="store_true",
                    help='save only board image to charuco.png file')
parser.add_argument('-w', '--width', type=int, default=5,
                    help='Width of board, default 5')
parser.add_argument('-e', '--height', type=int, default=7,
                    help='Height of board, default 7')
parser.add_argument('-c', '--camera', action="store_true",
                    help='use first camera or video file to take photos until enter pressed')
parser.add_argument('-s', '--save', action="store_true",
                    help='save camera images to file cal0.png, cal1.png if camera is used')
parser.add_argument('-o', '--output', type=str,
                    default="calibration_matrix.yaml",
                    help='output yaml camera calibration data file, default: calibration_matrix.yaml')
parser.add_argument('-d', '--dictionary', type=str, default="DICT_4X4_50",
                    help='ArUco dictionary name, default DICT_4X4_50')
parser.add_argument('--debug', action="store_true",
                    help='Display found ArUco codes')

args = parser.parse_args()
if sys.platform.startswith('win'):
    args.names = extend_names(args.names)
if args.dictionary not in ARUCO_DICT:
    print(f"Unkonw ArUco dictionary name: {args.dictionary}")
    print(f"Valid names: {ARUCO_DICT}")
    sys.exit()
dictionary = aruco.getPredefinedDictionary(ARUCO_DICT[args.dictionary])
board = aruco.CharucoBoard_create(args.width, args.height, .025, .0125, dictionary)
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
        corners, ids, _ = aruco.detectMarkers(gray, dictionary)
        if args.debug:
            show_markers("On-line camera", frame, corners, ids)
        if ids is not None and len(ids) > 0:
            ret, corners1, ids1 = aruco.interpolateCornersCharuco(corners,
                                                                      ids,
                                                                      gray,
                                                                      board)
            aruco.drawDetectedMarkers(gray, corners, ids)

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
    for fn in sorted(args.names):
        # read images from files
        frame = cv2.imread(fn)
        if frame is None:
            print('error reading image: {}'.format(fn))
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, dictionary)
        if args.debug:
            show_markers(fn, frame, corners, ids)
        if ids is not None and len(ids) > 0:
            ret, corners1, ids1 = aruco.interpolateCornersCharuco(corners,
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
print('Overall RMS: {}'.format(ret))
cal = {'camera_matrix': np.asarray(mtx).tolist(),
       'dist_coeff': np.asarray(dist).tolist()}
# and save to file
with open(args.output, "w") as f:
    yaml.dump(cal, f)
#print(cal)
