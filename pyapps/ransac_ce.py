#! /usr/bin/env python3
"""
    Multi-circle/ellipse fiting using RANSAC filtering before LSM circle fitting
    CLI parameters:
        csv file with id and x,y,z coordinates
        -e/--elev elevations of circle sections (list)
        -s/--sep separator in csv file, default ;
        -i/--withid there is an id in csv file in front of coordinates
        -p/--print_coo print filtered coordinates, too

    Results are written to stdout:
        center_x, center_y, elevation, rms, number_of_ransac_filtered_points/total_number_of_points
"""

import sys
from math import atan, atan2, acos, sin, cos, sqrt, hypot, pi
from random import shuffle
import os.path
import numpy as np
import matplotlib.pyplot as plt

def generate_points(x0, y0, ap, bp, phi, npts=100, tmin=0, tmax=2*np.pi):
    """ generate test points on ellipse/circle
        x0, y0 center of ellipse/circle
        ap, bp semi axices (ap = bp circle)
        phi rotation
        npts number of points
        noise to move x and y
        tmin, tmax agle parameter range
    """
    t = np.linspace(tmin, tmax, npts)
    x = x0 + ap * np.cos(t) * np.cos(phi) - bp * np.sin(t) * np.sin(phi)
    y = y0 + ap * np.cos(t) * np.sin(phi) + bp * np.sin(t) * np.cos(phi)
    return x, y

def circle(x, y):
    """ horizontal circle through points using LSM if more than 3 points given
        x - x coordinates of points, numpy vector
        y - y coordinates of points, numpy vector
        returns tuple of x0, y0, r, rms
    """
    # coefficients of unknowns
    A = np.c_[x, y, np.ones_like(x)]
    # pure term
    b = -(x * x + y * y)
    # solution for a1, a2, a3
    Q = np.linalg.inv(A.T @ A)
    par = Q @ (A.T @ b)
    # calculating the original unknowns
    x0 = -0.5 * par[0]
    y0 = -0.5 * par[1]
    r = sqrt(x0**2 + y0**2 - par[2])
    #residuals
    res = np.sqrt((x - x0)**2 + (y - y0)**2) - r
    #root mean square error
    rms = sqrt(np.mean(res**2))
    return x0, y0, r, rms

def sign(x):
    """ signum function """
    return  1 if x > 0 else -1 if x < 0 else 0

def point_ellipse_dist(a, b, xp, yp):
    """ distance from ellipsoid center at the origin and no rotation
        https://iquilezles.org/articles/ellipsedist/
        a, b semi axices of ellipse
        xp, yp point to calculate distance from
        returns distance
    """
    xp = abs(xp); yp = abs(yp)
    if xp > yp:
        a, b = b, a
        xp, yp = yp, xp
    l = b * b - a * a
    m = a * xp / l; m2 = m * m
    n = b * yp / l; n2 = n * n
    c = (m2 + n2 - 1.0) / 3.0; c3 = c**3
    q = c3 + m2 * n2 * 2.0
    d = c3 + m2 * n2
    g = m + m * n2
    if d < 0.0:
        p = acos(q / c3) / 3.0
        s = cos(p)
        t = sin(p) * sqrt(3.0)
        rx = sqrt(-c * (s + t + 2.0) + m2)
        ry = sqrt(-c * (s - t + 2.0) + m2)
        co = (ry + sign(l) * rx + abs(g) / (rx * ry) - m) / 2.0
    else:
        h = 2.0 * m * n * sqrt(d)
        s = sign(q + h) * abs(q + h)**(1.0 / 3.0)
        u = sign(q - h) * abs(q - h)**(1.0 / 3.0)
        rx = -s - u - c * 4.0 + 2.0 * m2
        ry = (s - u) * sqrt(3.0)
        rm = sqrt(rx * rx + ry * ry)
        p = ry / sqrt(rm -rx)
        co = (p + 2.0 * g / rm - m) / 2.0
    si = sqrt(abs(1.0 - co * co))
    xe, ye = a * co, b * si
    return hypot(xe - xp, ye - yp)

def dist_ellipse(x0, y0, ap, bp, phi, x, y):
    """ calculate distances from ellipse
        x0, y0 center of ellipse
        ap, bp semi-majos and semi-minor axis
        phi otation angle of ellipse
        x, y arry of coordinates
    """
    dist = np.zeros(x.shape[0])
    for i in range(x.shape[0]):
        xw = x[i] - x0
        yw = y[i] - y0
        xt = xw * cos(phi) + yw * sin(phi)
        yt = -xw * sin(phi) + yw * cos(phi)
        dist[i] = point_ellipse_dist(ap, bp, xt, yt)
    return dist

def rms_ellipse(x0, y0, ap, bp, phi, x, y):
    """ calculate rms error
        x0, y0 enter of ellipse
        ap, bp semi-majos and semi-minor axis
        phi otation angle of ellipse
        x, y arry of coordinates
    """
    dist = dist_ellipse(x0, y0, ap, bp, phi, x, y)
    rms = sqrt(np.mean(dist**2))
    return rms

def par2geom(A, B, C, D, E, F):
    """ calculate geometrical parameters from A B C D E F"""
    ap = abs(-sqrt(abs(2 * (A * E**2 + C * D**2 - B * D * E  + (B**2 - 4 * A * C) * F) * ((A + C) + sqrt((A - C)**2 + B**2)))) / (B**2 - 4 * A * C))
    bp = abs(-sqrt(abs(2 * (A * E**2 + C * D**2 - B * D * E  + (B**2 - 4 * A * C) * F) * ((A + C) - sqrt((A - C)**2 + B**2)))) / (B**2 - 4 * A * C))
    x0 = (2 * C * D - B * E) / (B**2 - 4 * A * C)
    y0 = (2 * A * E - B * D) / (B**2 - 4 * A * C)
    phi = atan2(-B, C-A) / 2
    if ap < bp:
        ap, bp = bp, ap
        phi -= np.pi / 2
    while phi < 0:
        phi += 2 * np.pi
    while phi > np.pi:
        phi -= np.pi
    return x0, y0, ap, bp, phi

def ellipse(x, y):
    """ horizontal ellipse through points using LSM if more than 5 points given
        Ax^2 + Bxy + Cy^2 + Dx + Ey + F = 0
        x - x coordinates of points, numpy vector
        returns tuple of x0, y0, a, b, phi 
    """
    mat = np.c_[x**2, x*y, y**2, x, y, np.ones_like(x)]
    S = mat.T @ mat
    eigvals, eigvecs = np.linalg.eig(S)
    eigvals_sorted_idx = np.argsort(eigvals)
    eigvals = eigvals[eigvals_sorted_idx]
    eigvecs = eigvecs[:, eigvals_sorted_idx]
    # Get the ellipse coefficients from the eigenvector
    A, B, C, D, E, F = eigvecs[:, 0]

    #if B**2 - 4 * A * C >= 0:
    #    return None # not an ellipse
    # calculating center of ellipse
    x0, y0, ap, bp, phi = par2geom(A, B, C, D, E, F)
    #root mean square error
    rms = rms_ellipse(x0, y0, ap, bp, phi, x, y)
    return x0, y0, ap, bp, phi, rms

def dist_circle(xc, yc, r, x, y):
    """
        Calculate distances from circle
    """
    return np.sqrt((x - xc)**2 + (y - yc)**2) - r

def ransac_circle(x, y, r_tol=0.025):
    """
        Select points close to the same ellipse
        x - x coordinates of points, numpy vector
        y - y coordinates of points, numpy vector
        r_tol - max radial distance from circle to accept point
        returns tuple x, y of filtered points
    """
    n = x.shape[0]
    n_try = 5 * n
    best = 0
    best_x = np.zeros(1)
    best_y = np.zeros(1)
    indices = list(range(n))
    for _ in range(n_try):
        shuffle(indices)
        index = indices[:3]
        x3 = x[index]   # three random points
        y3 = y[index]
        try:
            xc, yc, r3, _ = circle(x3, y3)
        except:
            #print("circle failed")
            continue
        # distance from the circle
        dist = np.absolute(dist_circle(xc, yc, r3, x, y))
        n_fit = dist[dist < r_tol].size
        if n_fit > best:
            best = n_fit
            best_x = x[dist < r_tol]
            best_y = y[dist < r_tol]
        if n_fit == n:  # all points on circle early exit
            break
    return best_x, best_y

def ransac_ellipse(x, y, r_tol=0.025):
    """
        Select points close to the same ellipse
        x - x coordinates of points, numpy vector
        y - y coordinates of points, numpy vector
        r_tol - max radial distance from ellipse to accept point
        returns tuple x, y of filtered points
    """
    n = x.shape[0]
    n_try = 5 * n
    best = 0
    best_x = np.zeros(1)
    best_y = np.zeros(1)
    indices = list(range(n))
    for _ in range(n_try):
        shuffle(indices)
        index = indices[:5]
        x5 = x[index]   # five random points
        y5 = y[index]
        try:
            xc, yc, ap, bp, phi, _ = ellipse(x5, y5)
        except:
            #print("ellipse failed")
            continue
        # distance from the ellipse
        dist = dist_ellipse(xc, yc, ap, bp, phi, x, y)
        n_fit = dist[dist < r_tol].size
        if n_fit > best:
            best = n_fit
            best_x = x[dist < r_tol]
            best_y = y[dist < r_tol]
        if n_fit == n:  # all points on ellipse early exit
            break
    return best_x, best_y

def ell_draw(x, y, xr, yr, x0, y0, ap, bp, phi, title=''):
    """ draw the ellipse
        x, y all points
        xr, yr RANSAC filtered points
        x0, y0, ap, bp, phi ellipse parameters
    """
    plt.rcParams['font.size'] = 14
    plt.plot(x, y, 'x', label='outliers')
    plt.plot(xr, yr, 'o', label='inliers')
    x_lst, y_lst = generate_points(x0, y0, ap, bp, phi, 100)
    plt.plot(x_lst, y_lst)
    plt.axis('scaled')
    plt.title(title)
    plt.xlabel('[m]')
    plt.ylabel('[m]')
    plt.legend()
    plt.show()

def dist_line_3d(x0, y0, z0, a, b, c, x, y, z):
    """ Calculat distance between line and points
    """
    p0 = np.array([x0, y0, z0])
    p1 = p0 + np.array([a, b, c])
    pp = np.c_[(x, y, z)] - p0
    cross = np.cross(pp, p1-p0)
    dist = np.linalg.norm(cross, axis=1, ord=2)
    return dist

def line_3d(x, y, z):
    """ Fit 3D line to points
        returns a point on line and the direction
    """
    line_data = np.c_[(x, y, z)]
    line_mean = line_data.mean(axis=0)
    _, _, eigen_vec = np.linalg.svd(line_data - line_mean)
    return np.r_[(line_mean, eigen_vec[0])]

if __name__ == "__main__":

    import argparse
    import pandas as pd

    parser = argparse.ArgumentParser(prog='ransac_ce', description='fit circle or ellipse to points using RANSAC filtering')
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                        help='input ascii point cloud, use "test" to generate poins')
    parser.add_argument('-s', '--sep', type=str, default=";",
                        help='field separator in input file, default=;')
    parser.add_argument('-t', '--tol', type=float, default=0.025,
                        help='Tolerance for RANSAC, default 0.025 m')
    parser.add_argument('-v', '--vtol', type=float, default=0.025,
                        help='Vertical tolerance for sections, default 0.025 m')
    parser.add_argument('-i', '--withid', action='store_true',
                        help='there is an id in first column of input file')
    parser.add_argument('-p', '--print_coo', action='store_true',
                        help='print coordinates of points on ellipse/circle')
    parser.add_argument('-e','--elev', nargs='+', required=False, default=['0'],
                        help='elevations to make sections, default=0')
    parser.add_argument('--ellipse', action='store_true',
                        help='fit ellipse not circle')
    parser.add_argument('-d', '--draw', action='store_true',
                        help='draw result')
    args = parser.parse_args()
    npts = 10  # number of point for drawing
    if args.name[0] == 'test':
        # generate random points
        x0_orig = 4
        y0_orig = -3.5
        ap_orig = 7
        bp_orig = 3
        phi_orig = np.pi / 4
        noise = 0.01
        n_outlier = npts // 10
        if args.ellipse:
            x_orig, y_orig = generate_points(x0_orig, y0_orig, ap_orig, bp_orig, phi_orig, npts=npts,tmax=np.pi/2)
            print(f"orig: {x0_orig} {y0_orig} {ap_orig} {bp_orig} {phi_orig * 180 / np.pi}")
        else:
            x_orig, y_orig = generate_points(x0_orig, y0_orig, ap_orig, ap_orig, 0, npts =npts)
            print(f"orig: {x0_orig} {y0_orig} {ap_orig}")
        x = x_orig + noise * np.random.normal(size=npts) - noise / 2
        y = y_orig + noise * np.random.normal(size=npts) - noise / 2
        z = np.zeros(x.shape)
        # add outliers
        x[-n_outlier:] += np.random.rand(n_outlier) * ap_orig - ap_orig / 2
        y[-n_outlier:] += np.random.rand(n_outlier) * ap_orig - ap_orig / 2
        df = pd.DataFrame({'x': x, 'y': y, 'z': z})
    else:
        if args.withid:
            cols = [1,2,3]
        else:
            cols = [0,1,2]
        if not os.path.exists(args.name[0]):
            print(f"File not found: {args.name[0]}")
            sys.exit(1)
        try:
            df = pd.read_csv(args.name[0], sep=args.sep, usecols=cols,
                             names=["x", "y", "z"])
        except pd.errors.ParserError:
            print(f"File parse error: {args.name[0]}")
            sys.exit(2)
    centers = []
    for i, h in enumerate(args.elev):
        height = float(h)
        # select points on given height
        section = df[(df['z'] > height-args.vtol) & (df['z'] < height+args.vtol)]
        if len(section) > 3:
            x = section['x'].to_numpy()
            y = section['y'].to_numpy()
            # find best RANSAC circle
            if args.ellipse:
                xr, yr = ransac_ellipse(x, y, args.tol)
            else:
                xr, yr = ransac_circle(x, y, args.tol)
            # calculate LSM circle/ellipse
            if args.ellipse:
                pars = ellipse(xr, yr)
                if pars:
                    xc, yc, ap, bp, phi, rms = pars
                    print(f"Ellipse: {xc:.3f},{yc:.3f},{height:.3f},{ap:.3f},{bp:.3f},{phi * 180 / np.pi:.4f},{rms:.3f},{xr.shape[0]}/{len(section)}")
                else:
                    print("Ellipse failed...")
                    continue
            else:
                xc, yc, r, rms = circle(xr, yr)
                print(f"Circle: {xc:.3f},{yc:.3f},{height:.3f},{r:.3f},{rms:.3f},{xr.shape[0]}/{len(section)}")
                ap = bp = r
                phi = 0
            if args.print_coo:
                print("Filtered points")
                if args.ellipse:
                    dd = dist_ellipse(xc, yc, ap, bp, phi, xr, yr)
                else:
                    dd = dist_circle(xc, yc, r, xr, yr)
                print("      East         North      Distance")
                for xi, yi, d in zip(xr, yr, dd):
                    print(f"{xi:12.3f} {yi:12.3f} {d:12.3f}")
            centers.append([xc, yc, height])
            if args.draw:
                ell_draw(x, y, xr, yr, xc, yc, ap, bp, phi, f"Section {h} m")
        else:
            print(f"Failed at elevation {h}")
    if len(centers) > 2:
        # fit 3D line
        cc = np.array(centers)
        l3d = line_3d(cc[:,0], cc[:,1], cc[:,2])
        print(f"Axis line:\n x = {l3d[0]:12.3f} + {l3d[3]:12.6f} * t\n y = {l3d[1]:12.3f} + {l3d[4]:12.6f} * t\n z = {l3d[2]:12.3f} + {l3d[5]:12.6f} * t\n")
        tilt = atan(sqrt(l3d[3]**2 + l3d[4]**2) / l3d[5]) / pi * 200
        azi = atan2(l3d[3], l3d[4]) / pi * 200
        if azi < 0:
            azi += 400
        print(f"Tilt angle: {tilt:.4f} gon, Tilt direction: {azi:.4f} gon")
        dd = dist_line_3d(l3d[0], l3d[1], l3d[2], l3d[3], l3d[4], l3d[5], cc[:,0], cc[:,1], cc[:,2])
        rms = sqrt(np.mean(dd**2))
        print(f"RMS: {rms:.3f}")
        if args.print_coo:
            print("      East         North     Elevation     Distance")
            for xi, yi, zi, d in zip(cc[:,0], cc[:,1], cc[:,2], dd):
                print(f"{xi:12.3f} {yi:12.3f} {zi:12.3f} {d:12.3f}")
