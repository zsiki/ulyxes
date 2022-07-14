#!/bin/bash
#
# stream from raspi camera
# start this script on pi and
# use vlc on remote machine media/open networkstream and enter:
#     http://ip_of_pi:8160
#
raspivid -o - -t 0 -w 1000 -h 1000 -fps 24 |cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8160}' :demux=h264
