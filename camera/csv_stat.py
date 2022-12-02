#! /usr/bin/env python3
"""
    Make statistics on a column of video_aruco/imgs_aruco output
    and optionaly change positions to metric

    use csv_stat.py --help for command line option
"""
import sys
import os.path
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('name', metavar='file_name', type=str, nargs=1,
                    help='CSV file to process')
parser.add_argument('-m', '--marker_size', type=float, default=None,
                    help='ArUco marker size in milimeters')
parser.add_argument('-c', '--column', type=str, default='height',
                    help='Column name to process: height/width/east/elev')
parser.add_argument('-s', '--sep', type=str, default=';',
                    help='Input file separator, default: ;')
args = parser.parse_args()

if args.column not in ('east', 'elev', 'width', 'height'):
    print(f"Invalid column: {args.column}, valid columns are: height/width/east/elev")
    sys.exit()
names = ['time', 'east', 'elev', 'width', 'height', 'code']
try:
    tmp_data = pd.read_csv(args.name[0], sep=args.sep, names=names,
                           parse_dates=['time'])
except:
    print(f"Error opening/reading file: {args.file_name}")
    sys.exit()
if args.marker_size is not None:
    # replace east and elev with metric value from upper left corner
    width_med = tmp_data[['width', 'code']].groupby('code').median()
    width_med.rename(columns={"code": "code", 'width': "med_width"},
                     inplace=True)
    height_med = tmp_data[['height', 'code']].groupby('code').median()
    height_med.rename(columns={"code": "code", 'height': "med_height"},
                      inplace=True)
    tmp_df = tmp_data.merge(width_med, left_on='code', right_on='code').merge(height_med, left_on='code', right_on='code')
    tmp_df['elev'] = tmp_df['elev'] * args.marker_size / tmp_df['med_height']
    tmp_df['east'] = tmp_df['east'] * args.marker_size / tmp_df['med_width']
    tmp_data = tmp_df[names]
    fno = os.path.splitext(args.name[0])[0] + '_metric' + \
          os.path.splitext(args.name[0])[1]
    pd.options.display.float_format = '{:,.2f}'.format
    tmp_data.to_csv(fno, sep=';', header=False)
df_mean = tmp_data[[args.column, 'code']].groupby('code').mean()
df_mean.rename(columns={"code": "code", args.column: "mean_" + args.column},
               inplace=True)
df_med = tmp_data[[args.column, 'code']].groupby('code').median()
df_med.rename(columns={"code": "code", args.column: "median_" + args.column},
              inplace=True)
df_std = tmp_data[[args.column, 'code']].groupby('code').std()
df_std.rename(columns={"code": "code", args.column: "std_" + args.column},
              inplace=True)
df_cnt = tmp_data[[args.column, 'code']].groupby('code').count()
df_cnt.rename(columns={"code": "code", args.column: "count"}, inplace=True)
df_min = tmp_data[[args.column, 'code']].groupby('code').min()
df_min.rename(columns={"code": "code", args.column: "min_" + args.column},
              inplace=True)
df_max = tmp_data[[args.column, 'code']].groupby('code').max()
df_max.rename(columns={"code": "code", args.column: "max_" + args.column},
              inplace=True)
result = pd.concat([df_mean, df_med, df_std, df_cnt, df_min, df_max],
                   axis=1, join="inner")
pd.options.display.float_format = '{:,.1f}'.format
print(result)
