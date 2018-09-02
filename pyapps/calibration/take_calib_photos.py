import sys
sys.path.append('../ulyxes/pyapi')
sys.path.append('../lib/')
from camerastation import CameraStation
from totalstation import TotalStation
from remotemeasureunit  import RemoteMeasureUnit
from tcpiface import TCPIface
from angle import Angle
import math
import time
import numpy as np
import recognition as rec
import cv2


if __name__ == '__main__':

    print(sys.argv[0])
    resolution = (int(sys.argv[1]), int(sys.argv[1]))
    mesMatrix = (int(sys.argv[2]), int(sys.argv[3]))


    mu = RemoteMeasureUnit()

    iface = TCPIface('test', ('192.168.1.102', 8081), timeout=25)

    ts = CameraStation('test', mu, iface)


    first = {}
    last = {}
    print('Mark out the calibration area')
    ts.SetATR(0)
    ts.Measure()
    target = ts.GetMeasure()
    first['hz'] = target['hz'] - Angle('0-10-0', 'DMS')
    first['v'] = target['v'] - Angle('0-10-0', 'DMS')
    last['hz'] = target['hz'] + Angle('0-10-0', 'DMS')
    last['v'] = target['v'] + Angle('0-10-0', 'DMS')
    print(target)
    input('Press enter to start calibration')

    steps = 3


    hz = [first['hz']]
    v = [first['v']]

    r = {}
    r['hz'] = (last['hz'].GetAngle('RAD') - first['hz'].GetAngle('RAD'))/2
    r['v'] = (last['v'].GetAngle('RAD') - first['v'].GetAngle('RAD'))/2

    for i in range(1, mesMatrix[0] - 1):
        hz.append(first['hz'] + Angle(i * r['hz'], 'RAD'))
    for i in range(1, mesMatrix[1] - 1):
        v.append(first['v'] + Angle(i * r['v'], 'RAD'))

    hz.append(last['hz'])
    v.append(last['v'])


    face1 = np.empty((0,4))
    face2 = np.empty((0,4))



    for vv in v:
        for hzz in hz:

            ts.Move(hzz, vv)
            ans = 'n'
            while ans == 'n':
                try:
                    angles = ts.GetAngles()

                    name = 'pics/hz'+angles['hz'].GetAngle('DMS')+'v'+angles['v'].GetAngle('DMS')+'.png'
                    file = open(name, 'w+b')
                    ts.TakePhoto(file, resolution)
                    file.close()

                    img = cv2.imread(name, 1)

                    picCoord = rec.recogChessPattern(img)
                    line = [[angles['hz'].GetAngle('RAD'), angles['v'].GetAngle('RAD'), picCoord[0], picCoord[1]]]
                    print(line)
                    ans = 'y'
                except:
                    ans = 'n'
            face1 = np.append(face1, line , axis=0)
    print(face1)
    input('Turn station to second face')
    for vv in v:
        for hzz in hz:

            ts.Move(hzz + Angle(180, 'DEG'), Angle(360, 'DEG') - vv)
            ans = 'n'
            while ans == 'n':
                try:
                    angles = ts.GetAngles()

                    name = 'pics/hz'+angles['hz'].GetAngle('DMS')+'v'+angles['v'].GetAngle('DMS')+'.png'
                    file = open(name, 'w+b')
                    ts.TakePhoto(file, resolution)
                    file.close()

                    img = cv2.imread(name, 1)

                    picCoord = rec.recogChessPattern(img)
                    line = [[angles['hz'].GetAngle('RAD'), angles['v'].GetAngle('RAD'), picCoord[0], picCoord[1]]]
                    print(line)
                    ans = 'y'
                except:
                    ans = 'n'
            face2 = np.append(face2, line, axis=0)

    calib = np.append(face1, face2, axis=0)
    np.save('calibparams.npy', calib)




    A = np.empty((0,8))
    l = np.empty((0,1))


    xs, ys = 0, 0
    for i in range(0, int(face1.shape[0])):
        xs += (face1[i,2] + face2[i,2])/2
        ys += (face1[i,3] + face2[i,3])/2

    xa = xs/(face1.shape[0])
    ya = ys/(face1.shape[0])

    print(xa,ya)
    for i in range(0, int(face1.shape[0])):

        Arows = np.array([[1,0,0,0,(face1[i,2]-xa)/math.sin(face1[i,1]), (face1[i,3]-ya)/math.sin(face1[i,1]),0            , 0           ],\
                          [0,1,0,0,0                                   , 0                                   ,face1[i,2]-xa,face1[i,3]-ya],\
                          [0,0,1,0,(face2[i,2]-xa)/math.sin(face2[i,1]), (face2[i,3]-ya)/math.sin(face2[i,1]),0            ,0            ],\
                          [0,0,0,1,0                                   , 0                                   ,face2[i,2]-xa,face2[i,3]-ya]])
        lrows = np.array([[face1[i,0]],\
                          [face1[i,1]],\
                          [face2[i,0]],\
                          [face2[i,1]]])

        A = np.append(A, Arows, axis=0)
        l = np.append(l, lrows, axis=0)

    X0 = np.array([[xa],[ya],[1],[1],[1],[1]])
    print(A)

    #x = np.dot(np.dot(np.linalg.pinv(np.dot(np.transpose(A),A)),np.transpose(A)),l)


    x = np.dot(np.linalg.pinv(np.dot(np.transpose(A),A)),np.dot(np.transpose(A),l))
    print(x)


    v = np.dot(A,x)
    print(v)

    params = np.array([[xa, x[4], x[5], resolution[0]],\
                       [ya, x[6], x[7], resolution[1]]])

    np.save('aparams_'+str(int(target['distance'])*100) + '_' + str(resolution[0]) + '.npy', params)
