import cv2
import numpy as np
import math


def intersection(line1, line2):
    A1, B1 =  float(line1[1] - line1[3]), float(-(line1[0] - line1[2]))
    A2, B2 =  float(line2[1] - line2[3]), float(-(line2[0] - line2[2]))
    #print(line1[1])


    C1 = float(A1 * line1[0] + B1 * line1[1])
    C2 = float(A2 * line2[0] + B2 * line2[1])


    try:

        x = (C1/A1) - (B1/A1)*((C2 - A2*C1/A1)/(B2 - A2*B1/A1))
        y = (C2 - A2*C1/A1)/(B2 - A2*B1/A1)


        if (line1[0] <= x <= line1[2] or line1[0] >= x >= line1[2]) and (line1[1] <= y <= line1[3] or line1[1] >= y >= line1[3]) and (line2[0] <= x <= line2[2] or line2[0] >= x >= line2[2]) and (line2[1] <= y <= line2[3] or line2[1] >= y >= line2[3]):
            return [x, y]
        else:
            return False
    except:
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

def recogChessPattern(pic):
    gray = cv2.cvtColor(pic, cv2.COLOR_RGB2GRAY)

    black = np.empty((20,20))
    white = np.empty((20,20))
    black[:,:] = 0
    white[:,:] = 255

    template = np.append(np.append(black, white, axis=1), np.append(white, black, axis=1), axis=0)

    gray = gray.astype(np.uint8)
    template = template.astype(np.uint8)

    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    pic[max_loc[1] + 20, max_loc[0]+20] = [0,255,0]


    cv2.namedWindow('check', cv2.WINDOW_NORMAL)
    cv2.imshow('check', pic)
    cv2.resizeWindow('check', 600, 600)
    cv2.waitKey()

    return (max_loc[0] + 20, max_loc[1]+20)

def recog(pic):

    hsv = cv2.cvtColor(pic, cv2.COLOR_RGB2HSV)

    binary = cv2.adaptiveThreshold(hsv[:,:,2] ,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY_INV, 15, 3)

    lines = cv2.HoughLinesP(binary, 1, np.pi/360, 150, None, 20 , 1)

    l = len(lines)

    for x1, y1, x2, y2 in lines[:,0,:]:
        cv2.line(pic, (x1, y1), (x2, y2), (0,0,255), 1, cv2.LINE_AA)
    x, y, n = 0, 0, 0
    for i in range(0,l):
        for j in range(i,l):
            if i != j:
                inter = intersection(lines[i,0,:], lines[j,0,:])

                if inter:
                    x += inter[0]
                    y += inter[1]
                    n += 1
                    cv2.circle(pic,(int(inter[0]), int(inter[1])), 1, (255,0,0), -1)

    #cv2.namedWindow('check', cv2.WINDOW_NORMAL)
    #cv2.imshow('check', pic)
    #cv2.resizeWindow('check', 600, 600)
    cv2.namedWindow('check', cv2.WINDOW_NORMAL)
    cv2.imshow('check', pic)
    cv2.resizeWindow('check', 600, 600)
    cv2.waitKey()
    return [round(x/n,0), round(y/n,0)]
