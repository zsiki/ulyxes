#! /usr/bin/env python3
""" create a distortion image using calibration data and image size
"""
import sys
from os import path
from math import hypot
import argparse
import json
import yaml
import numpy as np
import cv2
import matplotlib.pyplot as plt

# read camera matrix and distortion parameters

ALFA = 0    # parameter to getOptimalNewCameraMatrix
            # 0 - original area is preserved without invalid areas
            # 1 - total area preserved with invalid areas

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--grid', type=int, default=200,
                        help='pixel distance for grid, default=200')
    parser.add_argument('-s', '--scale', type=float, default=5,
                        help='scale for distortion vectors, default=5')
    parser.add_argument('-w', '--width', type=int, default=None,
                        help='image width, default=image width')
    parser.add_argument('-e', '--height', type=int, default=None,
                        help='image height, default=image height')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Save image to file ')

    parser.add_argument('names', metavar='file_names', type=str, nargs=1,
                    help='yaml or json file with calibration data')
    args = parser.parse_args()
    if path.exists(args.names[0]):
        with open(args.names[0], encoding='ascii') as f:
            if args.names[0][-5:].lower() == '.yaml':
                c = yaml.load(f, Loader=yaml.FullLoader)
            else:
                c = json.loads("".join(f.readlines()))
            mtx = np.array(c['camera_matrix'])
            dist = np.array(c['dist_coeff'])
            cal_w, cal_h = c['img_size']
    else:
        print(f'Calibration file not found: {args.names[0]}')
        sys.exit(1)
    # calculate undistorted position of points
    if args.height is None or args.width is None or \
            (cal_w, cal_h) == (args.height, args.width):
        newmtx = mtx
        args.width, args.height = cal_w, cal_h
    else:
        newmtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist,
                         (cal_w, cal_h), ALFA, (args.width, args.height))
    # grid point coordinates
    pp = np.array([ (x, y)
                     for x in range(args.grid, args.width, args.grid)
                     for y in range(args.grid, args.height, args.grid)],
                   dtype=np.float64)
    points = np.zeros((1, pp.shape[0], pp.shape[1]))
    points[0] = pp
    points1 = cv2.undistortPoints(points, mtx, dist, None, newmtx)
    for p, p1 in zip(points[0], points1[:,0,:]):
        d0, d1 = p - p1
        d = hypot(d0, d1)
        plt.arrow(p[0], p[1], d0 * args.scale, d1 * args.scale)
    plt.axis('scaled')
    if args.output:
        plt.savefig(args.output)
    else:
        plt.show()
