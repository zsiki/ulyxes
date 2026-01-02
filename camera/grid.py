#! /usr/bin/env python3
"""
    It generates an image with rectangular grid and
    projective transformed and radial distorted copy

    use it with projector.py
"""
import argparse
import cv2
import skimage as ski
import numpy as np

COLORS = {'white': (255, 255, 255),
          'black' : (0, 0, 0),
          'red': (0, 0, 255),
          'blue': (0, 255, 0),
          'green': (255, 0, 0)}

def radial_distortion(x_y):
    """Distort coordinates `xy` symmetrically around their own center."""
    k = np.array([0.02, 0.04, 0.001])
    p = np.array([0.01, 0.05])
    x_y_c = (x_y - np.array([width / 2, height / 2])) / 200
    radius = np.linalg.norm(x_y_c, axis=1)
    # radial distortion
    radial = 1 + k[0] * radius**2 + k[1] * radius**4 + k[2] * radius**6
    res = x_y_c * radial[:, None]
    xy = x_y_c[:,0] * x_y_c[:,1]    # x * y
    res += np.c_[2 * p[0] * xy + p[1] * (radius**2 + 2 * x_y_c[:,0]**2),
                 p[0] * (radius**2 + 2 * x_y_c[:,1]**2) + 2 * p[1] * xy]
    res += x_y_c * 200 + np.array([width / 2, height / 2])
    return res

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--width', type=int, default=1920,
                    help='Imge width, default: 1920')
parser.add_argument('-e', '--height', type=int, default=1080,
                    help='Imge height, default: 1080')
parser.add_argument('-g', '--grid', type=int, default=200,
                    help='Distance between grid lines, default: 200')
parser.add_argument('-m,', '--margin', type=int, default=0,
                    help='Margin around grid, default: 0')
parser.add_argument('-t,', '--type', choices=['grid', 'chessboard', 'charuco'],
                    default='grid',
                    help='Type of image grid/chessboard/charuco, default: grid')
parser.add_argument('-l,', '--linewidth', type=int, default=3,
                    help='Width of grid lines, default: 3')
parser.add_argument('-c,', '--color', choices=COLORS, default='white',
                    help='Name of line/block color, default: white')
args = parser.parse_args()
width, height = args.width, args.height
grid = args.grid
margin = args.margin
c = COLORS.get(args.color, (255,255,255))
# fill image with black background
img = np.zeros((height, width, 3), dtype=np.uint8)
# generate corner points
points = []
for i in range(margin, height-margin+1, grid):
    for j in range(margin, width-margin+1, grid):
        points.append((float(j), float(i)))
# generate perfect image
if args.type == 'grid':
    for i in range(margin, height-margin+1, grid):
        cv2.line(img, (margin, i), (width-margin, i), c, args.linewidth)
    for i in range(margin, width-margin+1, grid):
        cv2.line(img, (i, margin), (i, height-margin), c, args.linewidth)
elif args.type in ('chessboard', 'charuco'):
    ii = 0
    cid = 0
    for i in range(margin, height-margin-grid, grid):
        jj = 0
        for j in range(margin, width-margin-grid, grid):
            if (ii + jj) % 2 == 1:
                cv2.rectangle(img, (j, i), (j+grid, i+grid), c, -1)
                if args.type == 'charuco':
                    dic = cv2.aruco.getPredefinedDictionary(1)
                    ch_size = 3 * grid // 4
                    charuco =cv2.aruco.generateImageMarker(dic, cid, ch_size, 0)
                    row = i + grid // 8
                    col = j + grid // 8
                    img[row:row+ch_size,col:col+ch_size] = cv2.cvtColor(charuco, cv2.COLOR_GRAY2BGR)
                    cid += 1
            jj += 1
        ii += 1
points = np.array(points, dtype=np.float32)

cv2.imwrite('grid.png', img)
with open('grid.txt', 'w', encoding='ASCII') as coo:
    for p in points:
        print(f"{p[0]:7.1f} {p[1]:7.1f} {p[0]:7.1f} {p[1]:7.1f}", file=coo)
# create projective transformed image
# Define the projective transformation matrix
matrix = np.array([[1, -0.05, 100],
                   [0.1, 0.9, 50],
                   [0.00015, 0.00015, 1]])
# Create the ProjectiveTransform object
tform = ski.transform.ProjectiveTransform(matrix=matrix)
# Apply the transformation to the image
tf_img = ski.transform.warp(img, tform.inverse)
img_uint8 = (255 * tf_img).astype(np.uint8)
cv2.imwrite('grid_prj.png', img_uint8)
# Transform points
tf_points = tform(points)
with open('grid_prj.txt', 'w', encoding='ASCII') as coo:
    for p in np.c_[tf_points, points]:
        print(f"{p[0]:7.0f} {p[1]:7.0f} {p[2]:7.0f} {p[3]:7.0f}", file=coo)
# Create radial distortion & tangetial image
tf_img = ski.transform.warp(img, radial_distortion) #, cval=1.0)
img_uint8 = (255 * tf_img).astype(np.uint8)
cv2.imwrite('grid_rad.png', img_uint8)
tf_points = radial_distortion(points)
with open('grid_rad.txt', 'w', encoding='ASCII') as coo:
    for p in np.c_[tf_points, points]:
        print(f"{p[0]:7.0f} {p[1]:7.0f} {p[2]:7.0f} {p[3]:7.0f}", file=coo)
