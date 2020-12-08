#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Base class for ArUco processing
"""

from math import (sqrt, atan2)
import matplotlib.pyplot as plt
import numpy as np
import yaml
import cv2

class ArucoBase():
    """ virtual base class from aruco processing in images or video
    """

    def __init__(self, args):
        """ initialize """
        # prepare aruco
        self.params = cv2.aruco.DetectorParameters_create()  # TODO set parameters
        self.params.perspectiveRemoveIgnoredMarginPerCell = 0.25
        if args.dict == 99:     # use special 3x3 dictionary
            self.aruco_dict = cv2.aruco.Dictionary_create(32, 3)
        else:
            self.aruco_dict = cv2.aruco.Dictionary_get(args.dict)
        self.mtx = self.dist = None
        self.calibration = args.calibration
        if args.calibration:    # load callibration data
            with open(args.calibration) as f:
                c = yaml.load(f, Loader=yaml.FullLoader)
                self.mtx = np.array(c['camera_matrix'])
                self.dist = np.array(c['dist_coeff'])
        else:
            self.mtx = self.dist = None
        self.debug = args.debug
        self.clip = args.clip
        self.tile = args.tile
        self.fast = args.fast
        self.hist = args.hist
        self.lchanel = args.lchanel
        self.code = args.code
        self.size = args.size

        self.last_x = self.last_y = None
        self.off_x = self.off_y = 0
        self.off_x1 = self.off_y1 = 0
        self.marker_h = self.marker_w = 0
        self.fast = False
        self.clahe = None
        self.clahe = cv2.createCLAHE(clipLimit=self.clip,
                                     tileGridSize=(self.tile, self.tile))

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
        img = frame.copy()  # copy original (undistorted) image
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
                    self.marker_w = int(np.max(corners[j][0][:, 0]) -
                                        np.min(corners[j][0][:, 0]))
                    self.marker_h = int(np.max(corners[j][0][:, 1]) -
                                        np.min(corners[j][0][:, 1]))
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
            plt.imshow(frame)
            if found:
                plt.plot(x+self.off_x, y+self.off_y, "o", color="red")
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
