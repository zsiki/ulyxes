#!/usr/bin/env python
"""
.. module:: arbitsection.py

.. moduleauthor:: Viktoria Zubaly, Zoltan Siki

    Sample application of Ulyxes PyAPI to measure an arbitrary  section
    target on a point or points to determine a plane and start this app
    coordinates and observations are written to csv file

    :param argv[1] (angle step): angle step between points in DEG, default 45
    :param argv[2] (sensor): 1100/1800/1200, default 1200
    :param argv[3] (port): serial port, default COM7
    :param argv[4] (number of points): number of measured points to determine a arbitrary plane, default 1 
    :param argv[5]  (tolerance): acceptable tolerance (meter) from the horizontal plane, default 0.01
    :param argv[6] (iteration): max iteration number for a point, default 10
"""

import sys
import re
import math
import numpy as np
import logging

sys.path.append('../pyapi/')

from angle import Angle, PI2
from serialiface import SerialIface
from csvwriter import CsvWriter
from totalstation import TotalStation

logging.getLogger().setLevel(logging.DEBUG)
# Process command line parameters
if len(sys.argv) > 1:
    stepinterval = Angle(float(sys.argv[1]), 'DEG')
else:
    stepinterval = Angle(20, 'DEG')
   
if len(sys.argv) > 2:
    stationtype = sys.argv[2]
else:
    stationtype = '1200'
if re.search('120[0-9]$', stationtype):
    from leicatps1200 import LeicaTPS1200
    mu = LeicaTPS1200()
elif re.search('110[0-9]$', stationtype):
    from leicatcra1100 import LeicaTCRA1100
    mu = LeicaTCRA1100()
elif re.search('550[0-9]$', stationtype):
    from trimble5500 import Trimble5500
    mu = Trimble5500()
else:
    print "unsupported instrument type"
    exit(1)
   
if len(sys.argv) > 3:
    port = (sys.argv[3])
else:
    port = 'COM7'
   
if len(sys.argv) > 4:
    numberOfPoints = int(sys.argv[4])
else:
    numberOfPoints = 2   
tol = 0.01
if len(sys.argv) > 5:
    tol = float(sys.argv[5])
# Number of iterations to find point on the chosen plane
maxiter = 10
if len(sys.argv) > 6:
    maxiter = int(sys.argv[6])
iface = SerialIface("rs-232", port)   ## eomRead='\n'
wrt = CsvWriter(angle = 'DMS', dist = '.3f',
                filt = ['id','east','north','elev'],
                fname = 'section.txt', mode = 'w', sep = ';')
ts = TotalStation(stationtype, mu, iface)
ts.SetATR(0)    # ATR mode off
ts.SetLock(0)   # Lock mode off
ts.SetEDMMode("RLSTANDARD")   # Reflectorless distance measurement
ts.SetRedLaser(1)

# Direction of the points to defining the plane
points = []
for i in range(numberOfPoints):
    raw_input("Target on %d point and press enter" % (i+1))
    ts.Measure()
    obs = ts.GetMeasure()
    if ts.measureIface.state != ts.measureIface.IF_OK or \
       'errorCode' in obs:
        print 'Start again!'
        exit(1)
    # Calculation of the directed coordinates according to the instrument's origin
    obs['east'] = obs['distance'] * math.sin(obs['v'].GetAngle()) * math.sin(obs['hz'].GetAngle())
    obs['north'] = obs['distance'] * math.sin(obs['v'].GetAngle()) * math.cos(obs['hz'].GetAngle())
    obs['elev'] = obs['distance'] * math.cos(obs['v'].GetAngle())
    wrt.WriteData(obs)
    points.append(obs) # Appending the observations to the list of measured points
    #print (points[i])

# Definition of the different planes   
if numberOfPoints == 1:   # in case of horizontal section
    plane = [0.0, 0.0, 1.0, -1 * points[0]['elev']]
elif numberOfPoints == 2:   # in case of vertical section
    plane = [points[0]['north'] - points[1]['north'],
            points[1]['east'] - points[0]['east'],
            0,
            points[0]['east']*points[1]['north']-points[1]['east']*points[0]['north']]
else:   # in case of arbitrary section
    plane = []
    plane.append((points[0]['north'] - points[1]['north']) * \
        (points[2]['elev'] - points[1]['elev']) - \
        (points[2]['north']-points[1]['north']) * \
        (points[0]['elev']-points[1]['elev']))
    plane.append((points[2]['east']-points[1]['east']) * \
        (points[0]['elev']-points[1]['elev']) - \
        (points[0]['east']-points[1]['east']) * \
        (points[2]['elev']-points[1]['elev']))
    plane.append((points[0]['east']-points[1]['east']) * \
        (points[2]['north']-points[1]['north']) - \
        (points[2]['east']-points[1]['east']) * \
        (points[0]['north']-points[1]['north']))
    plane.append(-plane[0] * points[0]['east'] - \
        plane[1] * points[0]['north'] - plane[2] * points[0]['elev'])
    
# Normalization of the plane coefficients
norm = math.sqrt(plane[0]**2 + plane[1]**2 + plane[2]**2)
plane = [ i / norm for i in plane]

# Checking the plane result with the observed points
for i in range(numberOfPoints):
    planeRes = plane[0]*points[i]['east']+plane[1]*points[i]['north']+plane[2]*points[i]['elev']+plane[3]
    logging.debug("Checking the distance for the first points: %d - %.3f" % (i, planeRes))

# Moving back to the first point
if numberOfPoints > 1:
    ts.Move(points[0]['hz'], points[0]['v'])
act = Angle(0)   # Actual angle from start point set to zero
w = True
while act.GetAngle() < PI2:   # Going around a whole circle
    ts.Measure()   # Measuring distance
    if ts.measureIface.state != ts.measureIface.IF_OK:
        ts.measureIface.state = ts.measureIface.IF_OK
        ts.MoveRel(stepinterval, Angle(0))  # TODO
        continue
    nextp = ts.GetMeasure()   # Get observation data
    if ts.measureIface.state != ts.measureIface.IF_OK or \
        not 'hz' in nextp or not 'v' in nextp or \
        not 'distance' in nextp:
        ts.measureIface.state = ts.measureIface.IF_OK
        ts.MoveRel(stepinterval, Angle(0))  # TODO
        continue
    # Calculating the coordinates of the next points
    nextp['east'] = nextp['distance'] * math.sin(nextp['v'].GetAngle()) * math.sin(nextp['hz'].GetAngle())
    nextp['north'] = nextp['distance'] * math.sin(nextp['v'].GetAngle()) * math.cos(nextp['hz'].GetAngle())
    nextp['elev'] = nextp['distance'] * math.cos(nextp['v'].GetAngle())
    
    index = 0
    intp = {}
    # Distance between the nextp and the plane
    dist = nextp['east'] * plane[0] + nextp['north'] * plane[1] + nextp['elev'] * plane[2] + plane[3]
    logging.debug("Distance  between the point and the plane: %d - %.3f" % dist)
    #print "dist=%.3f" % dist
    while abs(dist) > tol:   # Acceptable distance from the plane has to be lower than tolerance
        w = True
        # Calculation of the nadir point(intp) on the plane
        intp['east'] = nextp['east'] - plane[0] * dist
        intp['north'] = nextp['north'] - plane[1] * dist
        intp['elev'] = nextp['elev'] - plane[2] * dist
        dd = intp['east'] * plane[0] + intp['north'] * plane[1] + intp['elev'] * plane[2] + plane[3]
        logging.debug("Checking the distance for the nadir point: %.3f" % dd)
        
        # Calculating the zenith angle difference between nextp and it's nadir point
        zenith = nextp['v'].GetAngle()
        hdist = math.sin(zenith)*nextp['distance']
        hdist1 = math.sqrt(intp['east']**2 + intp['north']**2)
        if intp['elev'] < 0:
            zenith1 = math.atan(abs(intp['elev']) / hdist1) + math.pi/2.0
        else:
            zenith1 = math.atan(hdist1 / intp['elev'])
        
        # Calculating the horizontal angle between nextp and it's nadir point
        horiz = math.atan2(nextp['east'], nextp['north'])
        horiz1 = math.atan2(intp['east'], intp['north'])
        ts.MoveRel(Angle(horiz1- horiz), Angle(zenith1-zenith))  # Rotation of the nextp into the plane    
        ts.Measure()
        index += 1
        if index > maxiter or ts.measureIface.state != ts.measureIface.IF_OK:
            w = False
            ts.measureIface.state = ts.measureIface.IF_OK
            logging.warning('Missing measurement') #TODO
            break
        nextp = ts.GetMeasure()
        if not 'v' in nextp or not 'distance' in nextp:
            break
            
        # Calculating the coordinates of the nextp point
        nextp['east'] = nextp['distance'] * math.sin(nextp['v'].GetAngle()) * math.sin(nextp['hz'].GetAngle())
        nextp['north'] = nextp['distance'] * math.sin(nextp['v'].GetAngle()) * math.cos(nextp['hz'].GetAngle())
        nextp['elev'] = nextp['distance'] * math.cos(nextp['v'].GetAngle())
        # Checking the nextp whether on the plane within the given tolerance 
        dist = nextp['east'] * plane[0] + nextp['north'] * plane[1] + nextp['elev'] * plane[2] + plane[3]
    if 'distance' in nextp and w:
        wrt.WriteData(nextp)
    else:
        # In case of unmeasurable point the previous calculated point is used for continuing
        ts.measureIface.state = ts.measureIface.IF_OK
        nextp['east'] = nextq[0]
        nextp['north'] = nextq[1]
        nextp['elev'] = nextq[2]

    act += stepinterval # In case of success measurement, the instrument is rotating again with the stepinterval
    
    # Definition of the next point Q on the plane from the nextp
    # Rotating the normal vector into the plane
    rotationDelta = math.atan2(plane[0], plane[1]) # horizontal angle

    rotationZenith = math.atan2(math.sqrt(plane[0]**2 + plane[1]**2), plane[2]) # zenith angle

    MZ = np.array([[math.cos(rotationDelta), -math.sin(rotationDelta), 0.0],
                   [math.sin(rotationDelta), math.cos(rotationDelta), 0.0],
                   [0.0, 0.0, 1.0]]) # Rotation matrix around the "z" axis

    MEast = np.array([[1.0, 0.0, 0.0],
                      [0.0, math.cos(rotationZenith), -math.sin(rotationZenith)],
                      [0.0, math.sin(rotationZenith), math.cos(rotationZenith)]]) # Rotation matrix around the "x" axis

    Mstepinterval = np.array([[math.cos(stepinterval.GetAngle()), -math.sin(stepinterval.GetAngle()), 0.0],
                              [math.sin(stepinterval.GetAngle()), math.cos(stepinterval.GetAngle()), 0.0],
                              [0.0, 0.0, 1.0]]) # Rotation matrix with the stepinterval angle

    #print np.array([nextp['east'], nextp['north'], nextp['elev']])
    
    # Rotation of the normal vector into the plane
    nextpvar = np.dot(np.array([nextp['east'], nextp['north'], nextp['elev']]), np.dot(MZ, MEast))
    
    # Rotation with the stepinterval angle to the next point Q
    nextqvar = np.dot(nextpvar, Mstepinterval)
    
    # Defining the normal vector of the next point Q with rotation 
    nextq = np.dot(nextqvar, np.dot(np.linalg.inv(MEast), np.linalg.inv(MZ)))
    
    # Calculation of the horizontal and vertical angle of the next point Q for the actual rotation
    horizq = Angle(math.atan2(nextq[0], nextq[1]))
    if horizq.GetAngle() < 0:
        horizq = Angle(PI2 + horizq.GetAngle())
    zenithq = Angle(math.atan2(math.sqrt(nextq[0]**2 + nextq[1]**2), nextq[2]))
    
    ts.Move(horizq, zenithq) # Rotating to the Q point
