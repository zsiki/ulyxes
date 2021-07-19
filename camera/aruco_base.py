#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Base class for ArUco processing
"""
# TODO remove fast mode not faster
# TODO if code not given find all markers
# TODO test pose estimation

from math import (sqrt, atan2, hypot)
from os import path
import sys
import logging
import matplotlib.pyplot as plt
import numpy as np
import yaml
import cv2

sys.path.append('../pyapi/')

from confreader import ConfReader

class ArucoBase():
    """ virtual base class from aruco processing in images or video
    """

    def __init__(self, args):
        """ initialize """
        # prepare aruco
        self.params = cv2.aruco.DetectorParameters_create()  # TODO set parameters
        self.params.perspectiveRemoveIgnoredMarginPerCell = 0.25
        self.clip = 3.0
        self.tile = 8
        self.code = None

        if isinstance(args, str):
            # get params from json
            self.json_params(args)
        else:
            # get params from command line
            self.args_params(args)
        #
        self.last_x = self.last_y = None
        self.off_x = self.off_y = 0
        self.off_x1 = self.off_y1 = 0
        self.marker_h = self.marker_w = 0
        self.fast = False
        self.clahe = cv2.createCLAHE(clipLimit=self.clip,
                                     tileGridSize=(self.tile, self.tile))


    def json_params(self, fn):
        """ get params from json config """
        config_pars = {
            'log_file': {'required' : True, 'type': 'file'},
            'log_level': {'required' : True, 'type': 'int',
                          'set': [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]},
            'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
            'station_id': {'required' : True, 'type': 'str'},
            'camera_id': {'required' : False, 'type': 'str', 'default': '1'},
            'fps': {'required': False, 'type': 'float', 'default': 1},
            'dict': {'required': False, 'type': 'int', 'default': 1},
            'code': {'required': False, 'type': 'int', 'default': None},
            'size': {'required': False, 'type': 'float', 'default': 100.0},
            'calibration': {'required': False, 'type': 'file', 'default': None},
            'hist': {'required': False, 'type': 'int', 'default': 0},
            'lchanel': {'required': False, 'type': 'int', 'default': 0},
            'clip': {'required': False, 'type': 'float', 'default': 3.0},
            'tile': {'required': False, 'type': 'int', 'default': 8},
            'coo_wr': {'required': True, 'type': 'str'},
            'debug': {'required': False, 'type': 'int', 'default': 0},
            '__comment__': {'required': False, 'type': 'str'}
        }
        try:
            cr = ConfReader('camera', fn, config_pars)
            cr.Load()
        except Exception:
            print("Error in config file: {0}".format(sys.argv[1]))
            sys.exit(-1)
        if not cr.Check():
            print("Config check failed")
            sys.exit(-1)
        if cr.json['dict'] == 99:     # use special 3x3 dictionary
            self.aruco_dict = cv2.aruco.Dictionary_create(32, 3)
        else:
            self.aruco_dict = cv2.aruco.Dictionary_get(cr.json['dict'])
        self.mtx = self.dist = None
        self.calibration = cr.json['calibration']
        if self.calibration:    # load callibration data
            if path.exists(self.calibration):
                with open(self.calibration) as f:
                    c = yaml.load(f, Loader=yaml.FullLoader)
                    self.mtx = np.array(c['camera_matrix'])
                    self.dist = np.array(c['dist_coeff'])
            else:
                print('Calibration file not found')
                sys.exit(1)
        self.camera_id = cr.json['camera_id']
        self.fps = cr.json['fps']
        self.debug = cr.json['debug']
        self.clip = cr.json['clip']
        self.tile = cr.json['tile']
        #self.fast = args.fast
        self.hist = cr.json['hist']
        self.lchanel = cr.json['lchanel']
        self.code = cr.json['code']
        self.size = cr.json['size']
        self.coo_wr = cr.json['coo_wr']
        self.log_file = cr.json["log_file"]
        self.log_format = cr.json["log_format"]

    def args_params(self, args):
        """ get params from command line """
        if args.dict == 99:     # use special 3x3 dictionary
            self.aruco_dict = cv2.aruco.Dictionary_create(32, 3)
        else:
            self.aruco_dict = cv2.aruco.Dictionary_get(args.dict)
        self.mtx = self.dist = None
        self.calibration = args.calibration
        if self.calibration:    # load callibration data
            if path.exists(self.calibration):
                with open(self.calibration) as f:
                    c = yaml.load(f, Loader=yaml.FullLoader)
                    self.mtx = np.array(c['camera_matrix'])
                    self.dist = np.array(c['dist_coeff'])
            else:
                print('Calibration file not found')
                sys.exit(1)
        self.debug = args.debug
        self.clip = args.clip
        self.tile = args.tile
        #self.fast = args.fast
        self.hist = args.hist
        self.lchanel = args.lchanel
        self.code = args.code
        self.size = args.size

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
            # TODO check it https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html
            h, w = frame.shape[:2]
            newmtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist,
                                                        (w, h), 1, (w, h))
            frame = cv2.undistort(frame, self.mtx, self.dist, None, newmtx)
            # crop image
            frame = frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
        img = frame.copy()  # copy original (undistorted) image for display
        if self.fast and self.last_x:    # crop image for fast mode
            self.off_x = max(0, self.last_x - self.marker_w)
            self.off_y = max(0, self.last_y - self.marker_h)
            self.off_x1 = min(self.last_x + self.marker_w, img.shape[1])
            self.off_y1 = min(self.last_y + self.marker_h, img.shape[0])
            img = frame[self.off_y:self.off_y1, self.off_x:self.off_x1]
        if self.hist:
            if self.lchanel:
                lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                img_gray, _, _ = cv2.split(lab)
            else:
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_gray = self.clahe.apply(img_gray)
        else:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = \
                cv2.aruco.detectMarkers(img_gray, self.aruco_dict,
                                        parameters=self.params)
        found = False
        x = y = 0
        if ids is not None:
            for j in range(ids.size):
                if self.code is None:
                    self.code = ids[j][0]   # use first found code
                if ids[j][0] == self.code:
                    # calculate center of aruco code
                    x = int(round(np.average(corners[j][0][:, 0])))
                    y = int(round(np.average(corners[j][0][:, 1])))
                    self.marker_w = max(hypot(corners[j][0][0, 0] -
                                              corners[j][0][0, 1],
                                              corners[j][0][1, 0] -
                                              corners[j][0][1, 1]),
                                        hypot(corners[j][0][2, 0] -
                                              corners[j][0][2, 1],
                                              corners[j][0][3, 0] -
                                              corners[j][0][3, 1]))
                    self.marker_h = max(hypot(corners[j][0][1, 0] -
                                              corners[j][0][1, 1],
                                              corners[j][0][2, 0] -
                                              corners[j][0][2, 1]),
                                        hypot(corners[j][0][3, 0] -
                                              corners[j][0][3, 1],
                                              corners[j][0][0, 0] -
                                              corners[j][0][0, 1]))
                    #self.marker_w = int(np.max(corners[j][0][:, 0]) -
                    #                    np.min(corners[j][0][:, 0]))
                    #self.marker_h = int(np.max(corners[j][0][:, 1]) -
                    #                    np.min(corners[j][0][:, 1]))
                    actCorner = corners[j][0]
                    found = True
                    if self.calibration:    # estimate pose
                        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners[j:j+1], self.size, self.mtx, self.dist)
                        # https://answers.opencv.org/question/16796/computing-attituderoll-pitch-yaw-from-solvepnp/?answer=52913#post-id-52913
                        r, _ = cv2.Rodrigues(rvec) # convert to rotation matrix
                        # https://www.learnopencv.com/rotation-matrix-to-euler-angles/
                        euler_angles = self.rotationMatrixToEulerAngles(r)
                        cv2.aruco.drawAxis(frame, self.mtx, self.dist, rvec,
                                           tvec, 0.01)
                    break

        if self.debug and i % self.debug == 0:
            plt.clf()
            plt.imshow(img)
            if found:
                plt.plot(x+self.off_x, y+self.off_y, "o", color="red")
                plt.plot([actCorner[0][0], actCorner[1][0], actCorner[2][0],
                          actCorner[3][0], actCorner[0][0]],
                         [actCorner[0][1], actCorner[1][1], actCorner[2][1],
                          actCorner[3][1], actCorner[0][1]])
            plt.pause(0.0001)
        if found:
            self.last_x = x + self.off_x  # save last position
            self.last_y = y + self.off_y
            if self.calibration:    # output pose, too
                return {'east': self.last_x, 'north': self.last_y,
                        'width': self.marker_w, 'height': self.marker_h,
                        'euler_angles': euler_angles}
            return {'east': self.last_x, 'north': self.last_y,
                    'width': self.marker_w, 'height': self.marker_h}
        # no marker found search whole image next
        self.last_x = self.last_y = None
        self.off_y = self.off_x = 0
        return None
