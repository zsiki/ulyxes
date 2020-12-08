#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Virtual base class for template matching
"""

import yaml
import matplotlib.pyplot as plt
import numpy as np
import cv2

class TemplateBase():
    """
        Base class for template matching

        :param args: command line arguments
    """

    minv = 2    # index of min value
    maxv = 3    # index of max value
    methods = ((cv2.TM_SQDIFF, 2),
               (cv2.TM_SQDIFF_NORMED, 2),
               (cv2.TM_CCORR, 3),
               (cv2.TM_CCORR_NORMED, 3),
               (cv2.TM_CCOEFF, 3),
               (cv2.TM_CCOEFF_NORMED, 3))

    def __init__(self, args):
        """ initialize """
        self.templ = cv2.imread(args.template, cv2.IMREAD_GRAYSCALE)
        if self.templ is None:
            print("Error reading template: []".format(args.template))
            exit(1)
        self.templ_h, self.templ_w = self.templ.shape
        self.last_x = self.last_y = None
        self.off_x = self.off_y = 0
        self.off_x1 = self.off_y1 = 0

        self.spec = False
        self.method = 0
        if args.method in range(6):
            self.method = self.methods[args.method]
        elif args.method == 99:
            self.spec = True
        self.fast = args.fast
        self.debug = args.debug
        self.refresh_template = args.refresh_template
        try:
            self.names = args.names
        except:
            pass
        self.calibration = args.calibration
        if args.calibration:    # load callibration data
            with open(args.calibration) as f:
                c = yaml.load(f, Loader=yaml.FullLoader)
                self.mtx = np.array(c['camera_matrix'])
                self.dist = np.array(c['dist_coeff'])
        else:
            self.mtx = self.dist = None

    def img_correlation(self, img):
        """ find most similar part to templ on img
        img must be larger than templ in both dimensions
        img   - grayscale image to seek for templ (numpy array of uint8)

        returns upper left corner of templ in img and statistic
        """
        rows, cols = img.shape
        trows, tcols = self.templ.shape
        row = col = None
        mins = trows * tcols * 255         # max statistic
        t = self.templ.astype(int)
        for i in range(rows - trows):
            i1 = i + trows
            for j in range(cols - tcols):
                j1 = j + tcols
                s = np.sum(np.absolute(t - img[i:i1, j:j1]))
                if s < mins:
                    mins = s
                    row = i
                    col = j
        return (col, row, s)

    def ProcessImg(self, frame, i):
        """ process single image

            :param frame: image to process
            :param i: frame id
            :returns: dictionary of match position
        """
        if self.calibration:    # undistort image using calibration
            h, w = frame.shape[:2]
            newmtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist,
                                                        (w, h), 1, (w, h))
            frame = cv2.undistort(frame, self.mtx, self.dist, None, newmtx)
            # crop image
            frame = frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.fast and self.last_x:
            self.off_x = max(0, self.last_x - self.templ_w // 2)
            self.off_y = max(0, self.last_y - self.templ_h // 2)
            self.off_x1 = min(self.last_x + 3 * self.templ_w // 2,
                              img_gray.shape[1])
            self.off_y1 = min(self.last_y + 3 * self.templ_h // 2,
                              img_gray.shape[0])
            img_gray = img_gray[self.off_y:self.off_y1, self.off_x:self.off_x1]
        if self.spec:
            x, y, s = self.img_correlation(img_gray, self.templ)
        else:
            result = cv2.matchTemplate(img_gray, self.templ, self.method[0])
            min_max = cv2.minMaxLoc(result)
            x = min_max[self.method[1]][0]
            y = min_max[self.method[1]][1]
            s = result[min_max[self.method[1]][0]][min_max[self.method[1]][1]]
        if self.debug and i % self.debug == 0:
            plt.clf()
            plt.imshow(frame)
            plt.plot(x+self.off_x, y+self.off_y, "o")
            plt.pause(0.0001)
        if self.refresh_template:
            # get template from last image
            self.templ = img_gray[y:y+self.templ_h, x:x+self.templ_w]
        self.last_x = x + self.off_x
        self.last_y = y + self.off_y
        return {'east': self.last_x, 'north': self.last_y, 'quality': s}
