#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    go through video frames to find template and correlation
    video file name can contain date and time like: pi1_YYYYmmdd_HHMMSS.h264
    output sent to standard output in the form:
    line,date/time,column,row,statistic

    use video_correlation.py --help for comamnd line options
"""
import cv2
import sys
import datetime
import re
import argparse
import matplotlib.pyplot as plt
import numpy as np

def img_correlation(img, templ):
    """ find most similar part to templ on img
    img must be larger than templ in both dimensions
    templ - template grayscale image (numpy array of uint8)
    img   - grayscale image to seek for templ (numpy array of uint8)

    returns upper left corner of templ in img and statistic
    """
    rows, cols = img.shape
    trows, tcols = templ.shape
    row = col = None
    mins = trows * tcols * 255         # max statistic
    t = templ.astype(int)
    for i in range(rows - trows):
        i1 = i + trows
        for j in range(cols - tcols):
            j1 = j + tcols
            s = np.sum(np.absolute(t - img[i:i1,j:j1]))
            if s < mins:
                mins = s
                row = i
                col = j   
    return (col, row, s)

if __name__ == "__main__":
    # set up command line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('name', metavar='file_name', type=str, nargs=1,
        help='video file to process')
    parser.add_argument('-t', '--template', type=str, required=True,
        help='template image to find in video frames')
    parser.add_argument('-f', '--fps', type=int, default=None,
        help='frame per sec')
    parser.add_argument('-m', '--method', type=int, default=5,
        help='method to compare video frame and template, 0/1/2/3/4/5 TM_SQDIFF/TM_SQDIFF_NORMED/TM_CCORR/TM_CCORR_NORMED/CV_TM_CCOEFF/CV_TM_CCOEFF_NORMED, default 5')
    parser.add_argument('-r', '--refresh_template', action="store_true",
        help='refresh template after each frames')
    parser.add_argument('--fast', action="store_true",
        help='reduce input image size to double the template')
    parser.add_argument('-d', '--debug', type=int, default=0,
        help='display every nth frame with marked template position, default 0 (off)')
    args = parser.parse_args()      # process parameters
    # selected method
    minv = 2    # index of min value
    maxv = 3    # index of max value
    methods = ((cv2.TM_SQDIFF, minv), (cv2.TM_SQDIFF_NORMED, minv),
        (cv2.TM_CCORR, maxv), (cv2.TM_CCORR_NORMED, maxv),
        (cv2.TM_CCOEFF, maxv), (cv2.TM_CCOEFF_NORMED, maxv))

    spec = False
    if args.method in range(6):
        method = methods[args.method]
    elif args.method == 99:
        spec = True
    else:
        print('Invalid method id: {}'.format(args.method))
        sys.exit(3)
    # open template and convert to grayscale
    try:
        templ_gray = cv2.imread(args.template, cv2.IMREAD_GRAYSCALE)
    except:
        print('Error opening template image {}'.format(args.template))
        sys.exit(1)
    templ_h, templ_w = templ_gray.shape
    if args.name in ("0", "1", "2", "3"):
        cap= cv2.videoCapture(int(sys.argv[3])) # open camera stream
        if args.fps:
            fps = 25
        t = datetime.now()
    else:
        fn = args.name[0]
        if re.match('([a-zA-Z])*[0-9]_[0-9]{8}_[0-9]{6}', fn):
            l = fn.split('_')
            t = datetime.datetime(int(l[-2][0:4]), int(l[-2][4:6]), int(l[-2][6:8]),
                int(l[-1][0:2]), int(l[-1][2:4]), int(l[-1][4:6]))
            tformat = '%Y-%m-%d %H:%M:%S.%f'
        else:
            t = datetime.datetime(1970, 1, 1, 0, 0, 0)
            tformat = '%H:%M:%S.%f'
        cap = cv2.VideoCapture(fn)     # open video file
        fps = cap.get(cv2.CAP_PROP_FPS)
        if args.fps:
            fps = args.fps              # override fps from commandline

    if not cap.isOpened():
        print("Error opening video file")
        sys.exit(2)
    # process video
    i = 0   # frame id
    dt = datetime.timedelta(0, 1.0 / fps)
    if args.debug:
        # prepare animated figure
        plt.ion()
    last_x = None
    last_y = None
    off_x = 0
    off_y = 0
    while True:
        ret, frame = cap.read() # get next frame
        if ret:
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if args.fast and last_x:
                off_x = max(0, last_x - templ_w // 2)
                off_y = max(0, last_y - templ_h // 2)
                off_x1 = min(last_x + 3 * templ_w // 2, img_gray.shape[1])
                off_y1 = min(last_y + 3 * templ_h // 2, img_gray.shape[0])
                img_gray = img_gray[off_y:off_y1,off_x:off_x1]
            if spec:
                x, y, s = img_correlation(img_gray, templ_gray)
            else:
                result = cv2.matchTemplate(img_gray, templ_gray, method[0])
                min_max = cv2.minMaxLoc(result)
                x = min_max[method[1]][0]
                y = min_max[method[1]][1]
                s = result[min_max[method[1]][0]][min_max[method[1]][1]]
            if args.debug and i % args.debug == 0:
                plt.clf()
                plt.imshow(frame)
                plt.plot(x+off_x, y+off_y, "o")
                plt.pause(0.0001)
            print("{:d},{:s},{:d},{:d},{:f}".format(i,
                    t.strftime(tformat), x+off_x, y+off_y, s))
            i += 1
            t = t + dt
            if args.refresh_template:
                # get template from last image
                templ_gray = img_gray[y:y+templ_h,x:x+templ_w]
            last_x = x + off_x
            last_y = y + off_y
        else:
            break
    cap.release()
