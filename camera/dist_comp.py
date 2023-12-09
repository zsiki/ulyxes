#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    compare distorted and undistorted pairs of images
    parameters the two csv file from imgs_aruco.py
"""
from os import path
import argparse
import sys
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scale', type=float, default=5,
                        help='scale for distortion vectors, default=5')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Save image to file ')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print marker coordinates to stdout')
    parser.add_argument('names', metavar='file_names', type=str, nargs=2,
                    help='the name of two csv files for distorted and undistorted pairs')
    args = parser.parse_args()

    if not path.exists(args.names[0]) or not path.exists(args.names[1]):
        print("Input file(s) not found")
        sys.exit()
    names = ["seq", "time", "east", "north", "width", "height", "code"]
    l1 = pd.read_csv(args.names[0], names=names, sep=";")
    l2 = pd.read_csv(args.names[1], names=names, sep=";")
    for ind, rec1 in l1.iterrows():
        try:
            rec2 = l2.loc[l2["code"] == rec1["code"]].iloc[0]
        except IndexError:
            if args.debug:
                print(f"{rec1['code']} {rec1['east']:6.1f} {rec1['north']:6.1f} not found")
            continue
        plt.arrow(rec1["east"], rec1["north"],
                  (rec1["east"]-rec2["east"]) * args.scale,
                  (rec1["north"]-rec2["north"]) * args.scale)
        if args.debug:
            print(f"{rec1['code']:3d} {rec1['east']:6.1f} {rec1['north']:6.1f} {rec2['east']:6.1f} {rec2['north']:6.1f}")
    plt.axis('scaled')
    plt.title(f"{args.names[0]} - {args.names[1]}")
    if args.output:
        plt.savefig(args.output)
    else:
        plt.show()
