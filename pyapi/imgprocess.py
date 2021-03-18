#!/usr/bin/env python
"""
.. module:: imgprocess.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor::  Bence Turak <bence.turak@gmail.com>
"""
import cv2
import numpy as np
import math
#mport statistics as st

def intersection(line1, line2):
    A1, B1 =  line1[1] - line1[3], -(line1[0] - line1[2])
    A2, B2 =  line2[1] - line2[3], -(line2[0] - line2[2])


    C1 = A1 * line1[0] + B1 * line1[1]
    C2 = A2 * line2[0] + B2 * line2[1]

    try:
        x = (C1/A1) - (B1/A1)*((C2 - A2*C1/A1)/(B2 - A2*B1/A1))
        y = (C2 - A2*C1/A1)/(B2 - A2*B1/A1)


        if (line1[0] <= x <= line1[2] or line1[0] >= x >= line1[2]) and (line1[1] <= y <= line1[3] or line1[1] >= y >= line1[3]) and (line2[0] <= x <= line2[2] or line2[0] >= x >= line2[2]) and (line2[1] <= y <= line2[3] or line2[1] >= y >= line2[3]):
            return [x, y]
        else:
            return False
    except Exception:
        return False

def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def findNearPoints(points, max_dist):
    nearPoints = []
    l = len(points)
    for i in range(0, l):
        if any(points[i,:]):
            nearPoints.append([i])
            for j in range(i + 1, l):

                if any(points[j,:]):
                    if dist(points[i,:], points[j,:]) < max_dist:
                        nearPoints[-1].append(j)
                        points[j,:] = [0,0]
            points[i,:] = [0,0]
    return nearPoints

class ImgProcess(object):
    '''Image provessing class

        :param src: source of the picture (string)
    '''

    POINT = 0
    LINE = 1
    RECT = 2
    CRIRCLE = 3
    def __init__(self, src):
        '''constructor
        '''

        if isinstance(src, str):
            self._src = src
            self.img = cv2.imread(src, 1)
        else:
            raise TypeError('Src must be string!')

    def findTargets(self):
        '''find targets on the picture

            :returns: x, y, n ()
        '''
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)#convert to grayscale
        blur = cv2.GaussianBlur(gray, (5,5), 25)#bluring

        binary = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 1, 5, 3)#make binary

        edges = cv2.Canny(binary, 20, 150)#detect edges

        lines = cv2.HoughLinesP(edges, 1, np.pi/180.0, 15, np.array([]), 200, 25)#detect lines

        #calculate intersections of lines
        l = len(lines)
        points = np.empty((0,2), int)

        for i in range(0, l):
            for j in range(i, l):
                inter = intersection(lines[i][0], lines[j][0])
                if inter:
                    points = np.append(points, np.array([inter]), axis=0)

        nearPoints = findNearPoints(np.copy(points), 7)#select the nearest intersection points
        #calculate the targets midpoint from intersection points (presently the average of the points)
        targets = np.empty((0,3), int)
        for n in nearPoints:
            l = len(n)
            sumX, sumY = 0, 0
            for e in n:
                sumX += points[e,0]
                sumY += points[e,1]

            targets = np.append(targets, np.array([[sumX/l, sumY/l, l]]), axis=0)

        result = self.img.copy()
        for x, y, n in targets:
            result = cv2.circle(result,(int(x), int(y)), 10, (0,0,255), 1)

        #cv2.namedWindow('check', cv2.WINDOW_NORMAL)
        #cv2.imshow('check', result)
        #cv2.resizeWindow('check', 600, 600)
        #cv2.waitKey()
        return targets

        #cv2.imwrite('lines.png', result)

    def view(self):
        cv2.imshow(self._src ,self.img)

    def check(self, targets):

        check = self.img.copy()

        i = 0
        for datas in targets:
            #if obj == objects.POINT:

            check = cv2.circle(check ,(int(datas[0]), int(datas[1])), 15, (0,0,255), -1)

            check = cv2.putText(check, str(i), (int(datas[0]) + 15, int(datas[1]) + 15), cv2.FONT_HERSHEY_SIMPLEX, 8, (0,0,255), 4)
            i += 1

        cv2.namedWindow('check', cv2.WINDOW_NORMAL)
        cv2.imshow('check', check)
        cv2.resizeWindow('check', 600, 600)
        cv2.waitKey()

        order = input("Give the correct objects order!")
        return order

        return
