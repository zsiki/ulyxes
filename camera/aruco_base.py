#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Base class for ArUco processing
"""
# TODO test pose estimation

from math import (sqrt, atan2, hypot)
from os import path
import sys
import logging
import json
import matplotlib.pyplot as plt
import numpy as np
import yaml
import cv2
from confreader import ConfReader
from aruco_dict import ARUCO_DICT

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

# handle incompatibility introduced in openCV 4.8
if cv2.__version__ < '4.8':
    cv2.aruco.extendDictionary = cv2.aruco.Dictionary_create
    cv2.aruco.getPredefinedDictionary = cv2.aruco.Dictionary_get
    cv2.aruco.DetectorParameters = cv2.aruco.DetectorParameters_create

ALFA = 0    # parameter to getOptimalNewCameraMatrix
            # 0 - original area is preserved without invalid areas
            # 1 - total area preserved with invalid areas

class ArucoBase():
    """ virtual base class from aruco processing in images or video
    """

    def __init__(self, args):
        """ initialize """
        # default values
        self.clip = 3.0
        self.tile = 8
        self.code = None
        self.refine = False

        if isinstance(args, str):
            # get params from json
            self.json_params(args)
        else:
            # get params from command line
            self.args_params(args)
        #
        self.clahe = cv2.createCLAHE(clipLimit=self.clip,
                                     tileGridSize=(self.tile, self.tile))
        # ArUco detection parameters
        self.params = cv2.aruco.DetectorParameters()
        if  args.aruco_params is None:
            self.params.perspectiveRemoveIgnoredMarginPerCell = 0.25
            if self.refine:
                self.params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        else:
            # read params from json
            try:
                with open(args.aruco_params, encoding='ascii') as f:
                    data = f.read()
                js = json.loads(data)
            except:
                print('Error loading ArUco parameter file: ', args.aruco_params)
                sys.exit()
            for par in js:
                setattr(self.params, par, js[par])

    def json_params(self, fn):
        """ get params from json config

            :param fn: name of json config file
        """
        config_pars = {
            'log_file': {'required' : True, 'type': 'file'},
            'log_level': {'required' : True, 'type': 'int',
                          'set': [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]},
            'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
            'station_id': {'required' : False, 'type': 'str'},
            'camera_id': {'required' : False, 'type': 'str', 'default': '1'},
            'fps': {'required': False, 'type': 'float', 'default': 1},
            'dict': {'required': False, 'type': 'str', 'default': 1},
            'code': {'required': False, 'type': 'int', 'default': None},
            'size': {'required': False, 'type': 'float', 'default': 100.0},
            'calibration': {'required': False, 'type': 'file', 'default': None},
            'pose': {'required': False, 'type': 'bool', 'default': False},
            'hist': {'required': False, 'type': 'int', 'default': 0},
            'refine': {'required': False, 'type': 'int', 'default': 0},
            'lchanel': {'required': False, 'type': 'int', 'default': 0},
            'clip': {'required': False, 'type': 'float', 'default': 3.0},
            'tile': {'required': False, 'type': 'int', 'default': 8},
            'coo_wr': {'required': True, 'type': 'str'},
            'debug': {'required': False, 'type': 'int', 'default': 0},
            'delay': {'required': False, 'type': 'float', 'default': 0.01},
            '__comment__': {'required': False, 'type': 'str'}
        }
        try:
            cr = ConfReader('camera', fn, config_pars)
            cr.Load()
        except Exception:
            print(f"Error in config file: {sys.argv[1]}")
            sys.exit(-1)
        if not cr.Check():
            print("Config check failed")
            sys.exit(-1)
        try:
            wid = int(cr.json['dict'])
        except ValueError:
            if cr.json['dict'] in ARUCO_DICT:
                wid = ARUCO_DICT[cr.json['dict']]
            else:
                wid = 1
        if wid == 99:     # use special 3x3 dictionary
            self.aruco_dict = cv2.aruco.extendDictionary(32, 3)
        else:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(wid)
        self.mtx = self.dist = None
        self.calibration = cr.json['calibration']
        self.pose = cr.json['pose']
        if self.calibration:    # load callibration data
            if path.exists(self.calibration):
                with open(self.calibration, encoding='ascii') as f:
                    if self.calibration[-4:].lower() == 'yaml':
                        c = yaml.load(f, Loader=yaml.FullLoader)
                    else:
                        c = json.loads("".join(f.readlines()))
                    self.mtx = np.array(c['camera_matrix'])
                    self.dist = np.array(c['dist_coeff'])
                    self.cal_w, self.cal_h = c['img_size']
            else:
                print('Calibration file not found')
                sys.exit(1)
        self.camera_id = cr.json['camera_id']
        self.fps = cr.json['fps']
        self.debug = cr.json['debug']
        self.clip = cr.json['clip']
        self.tile = cr.json['tile']
        self.hist = cr.json['hist']
        self.lchanel = cr.json['lchanel']
        self.refine = cr.json['refine']
        self.code = cr.json['code']
        self.size = cr.json['size']
        self.coo_wr = cr.json['coo_wr']
        self.log_file = cr.json["log_file"]
        self.log_format = cr.json["log_format"]

    def args_params(self, args):
        """ get params from command line

            :param args: command line arguments from argparse
        """
        try:
            wid = int(args.dict)
        except ValueError:
            if args.dict in ARUCO_DICT:
                wid = ARUCO_DICT[args.dict]
            else:
                wid = 1
        if wid == 99:     # use special 3x3 dictionary
            self.aruco_dict = cv2.aruco.extendDictionary(32, 3)
        else:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(wid)
        self.mtx = self.dist = self.cal_w = self.cal_h = None
        self.calibration = args.calibration
        self.pose = args.pose if self.calibration else False
        if self.calibration:    # load callibration data
            if path.exists(self.calibration):
                with open(self.calibration, encoding='ascii') as f:
                    if self.calibration[-5:].lower() == '.yaml':
                        c = yaml.load(f, Loader=yaml.FullLoader)
                    else:
                        c = json.loads("".join(f.readlines()))
                    self.mtx = np.array(c['camera_matrix'])
                    self.dist = np.array(c['dist_coeff'])
                    self.cal_w, self.cal_h = c['img_size']
            else:
                print('Calibration file not found')
                sys.exit(1)
        self.debug = args.debug
        if args.delay < 0.001:
            self.delay = 0.001
        else:
            self.delay = args.delay
        self.clip = args.clip
        self.tile = args.tile
        self.hist = args.hist
        self.lchanel = args.lchanel
        self.code = args.code
        self.size = args.size
        self.refine = args.refine

    # TODO pose http://cs-courses.mines.edu/csci507/schedule/24/SquareMarkersOpenCV.pdf
    @staticmethod
    def rotationMatrixToEulerAngles(R):
        """ Calculates rotation matrix to euler angles

            :param R: rotation matrix
            :returns: vector of euler angles
        """
        sy = sqrt(R[0][0] * R[0][0] +  R[1][0] * R[1][0])
        y = atan2(-R[2][0], sy)
        if sy < 1e-6:
            # singular case
            x = atan2(-R[1][2], R[1][1])
            z = 0
        else:
            x = atan2(R[2][1], R[2][2])
            z = atan2(R[1][0], R[0][0])
        return np.array([x, y, z])

    def ProcessImg(self, frame, i):
        """ process single image

            :param frame: image to process
            :param i: frame id
            :returns: dictionary of position and pose
        """
        if self.calibration:    # undistort image using calibration
            h, w = frame.shape[:2]
            if (self.cal_w, self.cal_h) == (h, w):
                newmtx = self.mtx
            else:
                newmtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist,
                                                            (self.cal_w, self.cal_h), ALFA, (w, h))
            img = cv2.undistort(frame, self.mtx, self.dist, None, newmtx)
        else:
            img = frame.copy()  # copy original (undistorted) if no calibration
        if self.hist:
            if self.lchanel:
                lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                img_gray, _, _ = cv2.split(lab)
            else:
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_gray = self.clahe.apply(img_gray)
        else:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if cv2.__version__ < '4.8':
            corners, ids, _ = cv2.aruco.detectMarkers(img_gray, self.aruco_dict,
                                                      parameters=self.params)
        else:
            detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.params)
            corners, ids, _ = detector.detectMarkers(img_gray)
        x = y = 0
        res = []    # results
        if ids is not None:
            for j in range(ids.size):
                if self.code is None or ids[j][0] == self.code:
                    # calculate center of aruco code
                    x = np.average(corners[j][0][:, 0])
                    y = np.average(corners[j][0][:, 1])
                    marker_w = max(hypot(corners[j][0][0, 0] - corners[j][0][1, 0],
                                         corners[j][0][0, 1] - corners[j][0][1, 1]),
                                   hypot(corners[j][0][2, 0] - corners[j][0][3, 0],
                                         corners[j][0][2, 1] - corners[j][0][3, 1]))
                    marker_h = max(hypot(corners[j][0][0, 0] - corners[j][0][3, 0],
                                         corners[j][0][0, 1] - corners[j][0][3, 1]),
                                   hypot(corners[j][0][1, 0] - corners[j][0][2, 0],
                                         corners[j][0][1, 1] - corners[j][0][2, 1]))
                    actCorner = corners[j][0]
                    if self.pose:    # estimate pose
                        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners[j:j+1], self.size, self.mtx, self.dist)
                        # https://answers.opencv.org/question/16796/computing-attituderoll-pitch-yaw-from-solvepnp/?answer=52913#post-id-52913
                        r, _ = cv2.Rodrigues(rvec) # convert to rotation matrix
                        # https://www.learnopencv.com/rotation-matrix-to-euler-angles/
                        euler_angles = self.rotationMatrixToEulerAngles(r)
                    if self.pose:    # output pose, too
                        res.append({'code': ids[j][0], 'east': x, 'north': y,
                                    'width': marker_w, 'height': marker_h,
                                    'euler_angles': euler_angles})
                    else:
                        res.append({'code': ids[j][0], 'east': x, 'north': y,
                                    'width': marker_w, 'height': marker_h})
                    if self.code is not None:
                        break   # search for single marker
        if self.debug and i % self.debug == 0:
            plt.clf()
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            for r in res:
                plt.plot(r['east'], r['north'], "o", color="red")
                #plt.plot([actCorner[0][0], actCorner[1][0], actCorner[2][0],
                #          actCorner[3][0], actCorner[0][0]],
                #         [actCorner[0][1], actCorner[1][1], actCorner[2][1],
                #          actCorner[3][1], actCorner[0][1]])
            plt.pause(self.delay)
        return res
