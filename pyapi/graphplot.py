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
    The data series are given by a list with maximum 6 elements
    1st list of x values
    2nd list of y1, y2, ... values
    3th list of simple format specifiers for y values, default is matplotlib defaults
    4th list of legend labels for y values, default ordinal index

    There are some simple examples at the end of the code
"""

import os.path
import re
from datetime import datetime
import matplotlib.pyplot as plt
#from matplotlib.dates import DateFormatter
import numpy as np

def dict2lists(dict_src, x_key, y_keys, rel=False, mirror=1, scale=1.0):
    """ convert list of dictionaries to vectors x can be string of date time or numerical string

        :param dict_src: loaded list of dictionaries from CsvReader
        :param x_key: key for x values
        :param y_keys: keys for multiple y values
        :param rel: relative values to first in ys
        :param mirror: 1/-1 multiplier for y to mirror
        :param scale: multiplier for y values
        :returns: tuple of lists of x and y values
    """
    date_format = None
    if re.match("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}",
                dict_src[0][x_key]):
        date_format = '%Y-%m-%d %H:%M:%S.%f'
    elif re.match("[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}",
                  dict_src[0][x_key]):
        date_format = '%Y/%m/%d %H:%M:%S.%f'
    elif re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", dict_src[0][x_key]):
        date_format = '%Y-%m-%d'
    elif re.match("[0-9]{4}/[0-9]{2}/[0-9]{2}", dict_src[0][x_key]):
        date_format = '%Y/%m/%d'
    if date_format:
        x = [datetime.strptime(d[x_key], date_format) for d in dict_src]
    else:
        x = [float(d[x_key]) for d in dict_src]
    ys = []
    for y_key in y_keys:
        rel_val = 0
        if rel:
            rel_val = float(dict_src[0][y_key])
        y = [(float(d[y_key]) - rel_val) * mirror * scale for d in dict_src]
        ys.append(y)
    return (x, ys)

class GraphPlot:
    """ class to plot a graph

        :param titles: list of titles for subplots
        :param units: units for aces
        :param data_series: list for each data serie, x, ys, formats, labels; formats and labels are optional
    """

    def __init__(self, titles, units, data_series):
        """ initialize instance """
        self.titles = titles
        self.units = units
        self.x = []
        self.y = []
        self.fmts = []
        self.labels = []
        for serie in data_series:
            self.x.append(serie[0])
            self.y.append(serie[1])
            fmt = [''] * len(serie[1])      # default formats
            if len(serie) > 2 and serie[2] is not None:
                fmt = serie[2]
            self.fmts.append(fmt)
            label = [str(col+1) for col in range(len(serie[1]))]
            if len(serie) > 3 and serie[3] is not None:
                label = serie[3]
            self.labels.append(label)
        self.main_title, _ = os.path.splitext(os.path.basename(__file__))

    def valid(self):
        """ check validity of data sets """
        n_err = 0
        n_xserie = len(self.x)
        n_yserie = len(self.y)
        if n_xserie == 0 or n_yserie == 0:
            print("missing x or y data series")
            return n_err + 1
        if n_xserie != n_yserie:
            n_err += 1
            print("x-y series number different")
        max_y = max([len(y) for y in self.y])
        if len(self.titles) != max_y:
            n_err += 1
            print("titles-x series")
        if len(self.units) != max_y + 1:    # there is unit for x too
            n_err += 1
            print("units-x series")
        if len(self.fmts) != n_xserie:
            n_err += 1
            print("fmts-x series")
        for i in range(len(self.x)):
            n_x = len(self.x[i])
            n_ys = len(self.y[i])
            if len(self.fmts[i]) != n_ys:
                n_err += 1
                print(f"fmts-y length {i}")
            if len(self.labels[i]) != n_ys:
                n_err += 1
                print(f"fmts-y length {i}")
            for j in range(len(self.y[i])):
                n_y = len(self.y[i][j])
                if n_y != n_x:
                    n_err += 1
                    print(f"different x-y length {i}")
        return n_err

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
                if len(self.y[i]) > ind and self.y[i][ind] is not None and len(self.y[i][ind]) > 0:
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
        # interpolate to equal interval data
        if isinstance(self.x[xi][0], datetime):
            x1_orig = x1
            #x2_orig = x2
            delta = (x2 - x1).total_seconds()
            x1 = 0
            x2 = delta
        else:
            delta = x2 - x1
        n = max(len(self.x[xi]), len(self.x[xj]))   # use denser serie for interpolation
        #dx = delta / n
        xx = np.linspace(x1, x2, n)
        if isinstance(self.x[xi][0], datetime):
            # change x to seconds from start
            wxi = [(x - x1_orig).total_seconds() for x in self.x[xi]]
            wxj = [(x - x1_orig).total_seconds() for x in self.x[xj]]
            yyi = np.interp(xx, wxi, self.y[xi][yi])
            yyj = np.interp(xx, wxj, self.y[xj][yj])
        else:
            yyi = np.interp(xx, self.x[xi], self.y[xi][yi])
            yyj = np.interp(xx, self.x[xj], self.y[xj][yj])
        res = np.correlate(yyi, yyj, 'full')
        lags = np.arange(-n + 1, n)
        return lags, res

if __name__ == "__main__":
    from sys import argv
    from math import (sin, cos, pi)

    DEMO_ID = 1
    if len(argv) > 1:
        DEMO_ID = int(argv[1])
    if DEMO_ID == 1:
        TITLES = ["line1", "line2", "points"]
        UNITS = ["m", "mm", "degree", "m"]
        X1 = [1, 2, 3, 4, 5, 6]
        Y11 = [0.34, 0.58, 1.02, 1.21, 1.52, 1.61]
        Y12 = [2.56, 1.43, 1.1, 0.8, 0.48, 0.67]
        X2 = [1.2, 1.9, 2.4, 2.8, 3.5, 5.8]
        Y21 = [0.86, 1.7, 1.45, 0.86, 1.2, 3.0]
        Y22 = [0.55, 0.72, 0.4, 0.88, 0.99, 2.0]
        Y23 = [6.54, 5.78, 1.34, 5.12, 4.01, 3.6]
        # x3 == x1
        Y31 = [1.8, 2.5, 3.1, 2.6, 2.3, 2.8]
        DATA_SERIES = [[X1, [Y11, Y12, Y12],
                        ['g--', 'r', 'ro'], ['l1', 'l2', 'l2']],
                       [X2, [Y22, Y21, Y23],
                        None, ['b1', 'b2', 'b3']],
                       [X1, [Y31], ['b+']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        if G.valid() == 0:
            G.draw()
    elif DEMO_ID == 2:
        TITLES = ["trigonometry"]
        UNITS = ["fok", "-"]
        X = list(range(0, 370, 10))
        Y1 = [sin(xi / 180 * pi) for xi in range(0, 370, 10)]
        Y2 = [cos(xi / 180 * pi) for xi in range(0, 370, 10)]
        DATA_SERIES = [[X, [Y1], None, ['sin']],
                       [X, [Y2], None, ['cos']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        if G.valid() == 0:
            G.draw()

    elif DEMO_ID == 3:
        TITLES = ["numpy arrays"]
        UNITS = ["fok", "-"]
        X = np.arange(0, 361, 10)
        Y1 = np.sin(X / 180 * pi)
        Y2 = np.cos(X / 180 * pi)
        DATA_SERIES = [[X, [Y1], None, ['sin']],
                       [X, [Y2], None, ['cos']]]
        G = GraphPlot(TITLES, UNITS, DATA_SERIES)
        if G.valid() == 0:
            G.draw()
