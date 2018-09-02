import glob
import cv2
import numpy as np
import sys
sys.path.append('../lib/')
import math
import recognition as rec
import math

ms = np.load('calibparams.npy')

print(ms)



size = ms.shape

face1 = ms[0:int(size[0]/2),:]
face2 = ms[int(size[0]/2):size[0],:]



A = np.empty((0,8))
l = np.empty((0,1))


xs, ys = 0, 0
for i in range(0, int(size[0]/2)):
    xs += (face1[i,2] + face2[i,2])/2
    ys += (face1[i,3] + face2[i,3])/2

xa = xs/(size[0]/2)
ya = ys/(size[0]/2)

print(xa,ya)
for i in range(0, int(size[0]/2)):

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

params = np.array([[xa, x[4], x[5]],\
                   [ya, x[6], x[7]]])

np.save('aparams.npy', params)
