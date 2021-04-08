#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Draw time series from csv files or list

    Data series come from the columns of the csv files multi columns can be used from
    the same file. One column for x values (it can be numerical or date/time data) and
    more columns for y1, y2, .., yn. Alternatively lists can be given with the values.
    As many charts will be drawn as many y columns given.
    If more input files are given multiple lines will be drawn in the same subfigure.
    It is poissible to define different number of y columns for the input csv files.
    The input csv files may have different number of rows and columns. column indeces are
    zero based.
    The data series are given by a list with maximum 8 elements
    1st the name of the csv file separated by ';' and
        list of column ordinal numbers first is for x, the followings are for y values
        (0 base index), the same column can be repeated
        x column can be numerical or date/time, y columns are numerical
        or complex list [ x1, [y11, y12], x2, [y21 y22]]
        x and y vlaues can be numpy vectors
    2nd list of x, y1, y2, ... column indices
    3rd index of filter column or None if no filter
    4th regexp for filtering or None if no filter
    5th list of multipliers for the columns, default 1 for each column
    6th list of offsets for the columns, default 0 for each column
    7th list of simple format specifiers for y values, default is matplotlib defaults
    8th list of legend labels for y values, default filename:column

    Here is a simple example with three input files and two subplots

    first.csv:
    1;0.34;2.56
    2;0.58;1.43
    3;1.02;1.1

    second.csv:
    A;1.2;0.86;0.55;6.54
    B;1.9;1.7;0.72;5.78
    C;2.4;1.45;0.4;1.34
    D;2.8;0.86;.88;5.12

    third.csv
    1;0.75;1.8
    2;2.1;2.5
    3;1.8;3.1

    titles = ["line1", "line2", "points"]
    units = ["m", "mm", "degree"]
    data_series = [['first.csv', [0, 1, 2], None, None, [1, 1, 0.56], [0, 0, 0], ['g--', 'r'], ['l1', 'l2']],
                   [['second.csv', [1, 3, 2]], None, None, [1, 1, 1], [0, 0, 0], ['', ''], ['b1', 'b2']],
                   [['third.csv', [0, 2]], None, None, [1, 0.75], [0, -0.3], ['b+']]]
    g = GraphPlot(titles, units, data_series)
    g.draw()

"""
import csv
import os.path
import re
from datetime import datetime
import matplotlib.pyplot as plt
#from matplotlib.dates import DateFormatter
import numpy as np

class GraphPlot:
    """ class to plot a graph

        :param titles: list of titles for subplots
        :param units: units for aces
        :param data_series: list for each data file, filename, filter_column, filter_regexp, column numbers, scales, offsets, formats, labels; scales, offset, formats and labels are optional
    """
    SEPARATOR = ";" # TODO configurable separator for csv file

    def __init__(self, titles, units, data_series):
        """ initialize instance """
        self.titles = titles
        self.units = units
        self.x = []
        self.y = []
        self.fmts = []
        self.labels = []
        for serie in data_series:
            filter_col = None
            if len(serie) > 2:
                filter_col = serie[2]
            filter_val = None
            if len(serie) > 3:
                filter_val = serie[3]
            scales = [1] * len(serie[1])    # default scales
            if len(serie) > 4 and serie[4] is not None:
                scales = serie[4]
            offsets = [0] * len(serie[1])  # default offsets
            if len(serie) > 5 and serie[5] is not None:
                offsets = serie[5]
            if isinstance(serie[0], str):
                act_x, act_y = self.load(serie[0], serie[1], filter_col,
                                         filter_val, scales, offsets)
            else:
                act_x = serie[0]
                act_y = serie[1]
            self.x.append(act_x)
            self.y.append(act_y)
            fmt = [''] * (len(serie[1]) - 1)      # default formats
            if len(serie) > 6 and serie[6] is not None:
                fmt = serie[6]
            self.fmts.append(fmt)
            if isinstance(serie[0], str):
                label = ["{}:{}".format(serie[0], str(col))
                         for col in serie[1]]
            else:
                label = [str(col+1) for col in range(len(serie[1]))]
            if len(serie) > 7 and serie[7] is not None:
                label = serie[7]
            self.labels.append(label)
        try:
            self.main_title, _ = os.path.splitext(os.path.basename(data_series[0]))
        except:
            self.main_title, _ = os.path.splitext(os.path.basename(__file__))

    def valid(self):
        """ check validity of data set """
        # TODO
        rows = max([len(yi) for yi in self.y])
        if len(self.titles) != rows or len(self.units) != rows+1:
            return 1
        return 0

    def draw(self, target=None):
        """ draw multi graph

            :param target: None for screen or a file name (png)
        """
        rows = max([len(yi) for yi in self.y])      # number of charts to draw
        fig = plt.figure()
        fig.canvas.set_window_title(self.main_title)
        #fig.suptitle(self.main_title) # TODO overlapping
        for ind in range(rows):
            ax = plt.subplot(rows, 1, ind+1)
            for i in range(len(self.x)):
                if len(self.y[i]) > ind:
                    if isinstance(self.x[i][0], datetime):
                        plt.plot_date(self.x[i], self.y[i][ind], self.fmts[i][ind],
                                      label=self.labels[i][ind])
                    else:
                        plt.plot(self.x[i], self.y[i][ind], self.fmts[i][ind],
                                 label=self.labels[i][ind])
            plt.xticks(rotation=45)
            plt.xlabel(self.units[0])
            plt.ylabel(self.units[ind+1])
            plt.grid()
            plt.legend()
            ax.set_title(self.titles[ind])
            #ax.fmt_xdate = DateFormatter('% H:% M:% S')
        #fig.autofmt_xdate()
        fig.tight_layout()
        if target is None:
            plt.show()
        else:
            fig.savefig(target)

    @staticmethod
    def load(fname, cols, filter_col=None, filter_val=None,
             scales=None, offsets=None):
        """ load input data

            :param fname: name of csv input file
            :param filter_col: column number for fileter, optional
            :param filter_val: regular expression for filter, optional
            :param cols: ordinal column numbers to use
            :param scales: multipliers for columns, optional
            :param offsets: offsets for columns optional
            :returns tuple x and y values (multiple y series as list)
        """
        data = []
        if scales is None:
            scales = [1] * len(cols)    # default scales to 1
        if offsets is None:
            offsets = [0] * len(cols)   # oefault offsets to 0
        with open(fname, newline='') as f:
            reader = csv.reader(f, delimiter=GraphPlot.SEPARATOR)
            for row in reader:
                if filter_col is None or re.search(filter_val, row[filter_col]):
                    data.append(row)
        if re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", data[0][cols[0]]):
            x = [datetime.strptime(row[cols[0]], '%Y-%m-%d %H:%M:%S')
                 for row in data]
        else:
            x = [float(row[cols[0]]) * scales[0] + offsets[0] for row in data]
        y = []
        for i in range(1, len(cols)):
            y.append([float(row[cols[i]]) * scales[i] + offsets[i] for row in data])
        return (x, y)

    def corr(self, xi, yi, xj, yj):
        """ calculate cross correlation between ith and jth data seriess

            :param xi: index of first x values
            :param yi: index of y values belonging xi
            :param xj: index of second x values
            :param yj: index of y values belonging xj
        """
        # find common range of the two x series
        x1 = max(self.x[xi][0], self.x[xj][0])
        x2 = min(self.x[xi][-1], self.x[xj][-1])
        xi1 = 0
        while self.x[xi][xi1] < x1:
            xi1 += 1
        xj1 = 0
        while self.x[xj][xj1] < x1:
            xj1 += 1
        xi2 = len(self.x[xi]) - 1
        while self.x[xi][xi2] > x2:
            xi2 -= 1
        xj2 = len(self.x[xj]) - 1
        while self.x[xj][xj2] > x2:
            xj2 -= 1
        # interpolate to equal interval data
        if isinstance(self.x[xi][0], datetime):
            x1_orig = x1
            #x2_orig = x2
            delta = (x2 - x1).total_seconds()
            x1 = 0
            x2 = delta
        else:
            delta = x2 - x1
        n = max(xj2 - xj1, xi2 - xi1)   # use denser serie for interpolation
        dx = delta / n
        xx = [x1 + i * dx for i in range(n)]
        if isinstance(self.x[xi][0], datetime):
            # change x to seconds from start
            wxi = [(x - x1_orig).total_seconds() for x in self.x[xi][xi1:xi2]]
            wxj = [(x - x1_orig).total_seconds() for x in self.x[xj][xj1:xj2]]
            yyi = np.interp(xx, wxi, self.y[xi][yi][xi1:xi2])
            yyj = np.interp(xx, wxj, self.y[xj][yj][xj1:xj2])
        else:
            yyi = np.interp(xx, self.x[xi][xi1:xi2], self.y[xi][yi][xi1:xi2])
            yyj = np.interp(xx, self.x[xj][xj1:xj2], self.y[xj][yj][xj1:xj2])
        res = np.correlate(yyi, yyj, 'full')
        pos = np.argmax(res)        # position of first max value
        pos -= len(xx) + 1          # change to relative position
        c = -1e20
        j = 0
        for i in range(1, len(yyi) // 2):
            w = np.correlate(yyi[:-i], yyj[i:])[0]
            if w > c:
                c = w
                j = i
                plt.figure()
                plt.plot(xx[:-i], yyi[:-i], xx[:-i], yyj[i:])
                plt.grid()
                plt.show()
            w = np.correlate(yyj[:-i], yyi[i:])[0]
            if w > c:
                c = w
                j = -i
                plt.figure()
                plt.plot(xx[i:], yyj[:-i], xx[i:], yyi[i:])
                plt.grid()
                plt.show()
        print(j, c)
        plt.figure()
        plt.xcorr(yyi, yyj, usevlines=False, maxlags=n // 2)
        plt.grid()
        plt.show()
        return pos * dx

if __name__ == "__main__":
    from sys import argv
    from math import (sin, cos, pi)

    DEMO_ID = 1
    if len(argv) > 1:
        DEMO_ID = int(argv[1])
    if DEMO_ID == 0:
        TITLES = ["line1", "line2", "points"]
        UNITS = ["m", "mm", "degree", "m"]
        DATA_SERIES = [['test/first.csv', [0, 1, 2, 2], None, None, [1, 1, 0.56, 1], [0, 0, 0, 1],
                        ['g--', 'r', 'ro'], ['l1', 'l2', 'l2']],
                       ['test/second.csv', [1, 3, 2, 3], None, None, [1, 1, 1, 0.75], [0, 0, 0, -0.5],
                        ['', '', 'yx'], ['b1', 'b2', 'b1']],
                       ['test/third.csv', [0, 2], None, None, [1, 0.75], [0, -0.3], ['b+']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        G.draw()
    elif DEMO_ID == 1:
        TITLES = ["line1", "line2", "points"]
        UNITS = ["m", "mm", "degree", "m"]
        X1 = [1, 2, 3, 4, 5, 6]
        Y11 = [0.34, 0.58, 1.02, 1.21, 1.52, 1.61]
        Y12 = [2.56, 1.43, 1.1, 0.8, 0.48, 0.67]
        X2 = [1.2, 1.9, 2.4, 2.8, 3.5, 5.8]
        Y21 = [0.86, 1.7, 1.45, 0.86, 1.2, 3.0]
        Y22 = [0.55, 0.72, 0.4, 0.88, 0.99, 2.0]
        # x3 == x1
        Y31 = [1.8, 2.5, 3.1, 2.6, 2.3, 2.8]
        DATA_SERIES = [[X1, [Y11, Y12, Y12], None, None,
                        [1, 1, 0.56, 1], [0, 0, 0, 1],
                        ['g--', 'r', 'ro'], ['l1', 'l2', 'l2']],
                       [X2, [Y22, Y21, Y22], None, None,
                        [1, 1, 1, 0.75], [0, 0, 0, -0.5],
                        ['', '', 'yx'], ['b1', 'b2', 'b1']],
                       [X1, [Y31], None, None, [1, 0.75], [0, -0.3], ['b+']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        G.draw()
    elif DEMO_ID == 2:
        TITLES = ["trigonometry"]
        UNITS = ["fok", "-", "-"]
        DATA_SERIES = [['test/sin_cos.csv', [0, 2], None, None,
                        [1, 1], [0, 0], [''], ['sin']],
                       ['test/sin_cos.csv', [0, 3], None, None,
                        [1, 1], [0, 0], [''], ['cos']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        G.draw()
        #print(G.corr(0, 0, 1, 0))
    elif DEMO_ID == 3:
        TITLES = ["trigonometry"]
        UNITS = ["fok", "-", "-"]
        X = list(range(0, 370, 10))
        Y1 = [sin(xi / 180 * pi) for xi in range(0, 370, 10)]
        Y2 = [cos(xi / 180 * pi) for xi in range(0, 370, 10)]
        DATA_SERIES = [[X, [Y1], [0, 2], None, None,
                        [1, 1], [0, 0], [''], ['sin']],
                       [X, [Y2], [0, 3], None, None,
                        [1, 1], [0, 0], [''], ['cos']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        G.draw()
        #print(G.corr(0, 0, 1, 0))

    elif DEMO_ID == 4:
        TITLES = ["numpy arrays"]
        UNITS = ["fok", "-", "-"]
        X = np.arange(0, 361, 10)
        Y1 = np.sin(X / 180 * pi)
        Y2 = np.cos(X / 180 * pi)
        DATA_SERIES = [[X, [Y1], [0, 2], None, None,
                        [1, 1], [0, 0], [''], ['sin']],
                       [X, [Y2], [0, 3], None, None,
                        [1, 1], [0, 0], [''], ['cos']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        G.draw()
