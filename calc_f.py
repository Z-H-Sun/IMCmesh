#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 17 2022

Monte Carlo estimation of the volume fraction of the region where F(x,y,z) > T. F = O70, M15, or T131 level surface. A scatter 3D plot of the region will be given in real time.

@author: ZSun
"""

func = input('Level surface name (O70/M15/T131) = ___.\b\b\b\b').lower()
T = float(input('Let t = ____.\b\b\b\b\b'))

import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.ion()
fig = plt.figure()
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax = fig.gca(projection='3d')
try: ax.set_aspect('equal')
except: pass
try: ax.set_box_aspect((1,1,1))
except:pass
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_zlim(0, 1)

def o70(x, y, z):
    a=16*(np.cos(2*np.pi*x)*np.cos(2*np.pi*y)*np.cos(2*np.pi*z) + np.sin(2*np.pi*x)*np.sin(2*np.pi*y)*np.sin(2*np.pi*z))
    b=16*(np.cos(4*np.pi*(y-z)) + np.cos(4*np.pi*(y + z)))
    c=16*(np.cos(4*np.pi*(z-x)) + np.cos(4*np.pi*(z + x)))
    d=16*(np.cos(4*np.pi*(x-y)) + np.cos(4*np.pi*(x + y)))
    e=32*np.cos(8*np.pi*z)
    f=16*(np.cos(2*np.pi*x)*np.cos(2*np.pi*y)*np.cos(2*np.pi*3*z)-np.sin(2*np.pi*x)*np.sin(2*np.pi*y)*np.sin(2*np.pi*3*z))
    g=32*np.sin(4*np.pi*x)*np.sin(4*np.pi*y)*np.sin(4*np.pi*z)
    return a+0.15*b+0.1*c-0.05*e-0.4*f - T ####################
def m15(x, y, z):
    a=8*np.cos(2*np.pi*x)*np.cos(2*np.pi*y)
    b=8*np.cos(4*np.pi*z)
    c=-8*np.sin(4*np.pi*y)*np.sin(2*np.pi*z) 
    d=-8*np.sin(2*np.pi*y)*np.sin(2*np.pi*(x+z)) 
    e=8*np.cos(2*np.pi*y)*np.cos(2*np.pi*(x+2*z))
    return a+0.2*b+0.3*c+0.8*d - T ####################
def t131(x, y, z):
    a=8*(np.cos(2*np.pi*(x-y))+np.cos(2*np.pi*(x+y)))
    b=8*(np.cos(2*np.pi*x)+np.cos(2*np.pi*y))
    c=8*(np.cos(2*np.pi*x)-np.cos(2*np.pi*y))*np.cos(2*np.pi*z)
    d=16*np.cos(4*np.pi*z)
    e=16*np.cos(2*np.pi*x)*np.cos(2*np.pi*y)*np.cos(4*np.pi*z) 
    return c+0.2*a-0.9*b - T ####################

fracs = []
while True:
    try:
        xyz = []
        for _ in range(10000):
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            z = random.uniform(0, 1)
            if globals()[func](x, y, z) > 0: # F(x,y,z) - T > 0
                xyz.append((x, y, z))

        frac = len(xyz)/10000
        fracs.append(frac)
        points = ax.scatter(*zip(*xyz), s=5)
        print('VolFrac =', frac, end='. Press Ctrl-C to pause.\n')
        plt.pause(0.3)
    except KeyboardInterrupt:
        mean = np.mean(fracs)
        count = len(fracs)*10000
        sigma = np.sqrt(mean*(1-mean)/count)
        print('\nAvgVolFrac =', mean, '\u00b1', sigma, '(N =', count, end='). ')
        input('Press Enter to continue.')
    except:
        print('Error likely due to invalid func name ' + func)
    try: points.remove()
    except: pass