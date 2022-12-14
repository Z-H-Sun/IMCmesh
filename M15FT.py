#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 5 2022

Simulate the SAXS curves by Fourier transform (FT) for 1) 3D continuous M15 and 2) sliced M15-in-LAM structures.
First, the real space models for the 2 cases are generated. This is based on the model `M15FT/M15_unitcell.npy`, which is generated by Mathematica (see GenLevelSurf.nb) and then voxelized and binaried into a 10*20*17 array. For each of the 2 cases, the generation methods are elaborated below, and the final outcomes are shown in `M15FT/M15_c.png` and `M15FT/M15_s.png`, repectively.
Then, the FFT is done, and the results are saved to `M15FT/M15_c.npy` and `M15FT/M15_s.npy`, respectively. The results can be visualized by `M15FTplot.py`

@author: ZSun
"""

import os
import numpy as np
import scipy.ndimage

os.chdir('M15FT')
data = np.load('M15_unitcell.npy') # 10*20*17
data = scipy.ndimage.interpolation.zoom(data, (1, 1, 1.17647)) # rescale z size to 20, which is necessary because the final array for FFT must be cubic, i.e. x=y=z
data = np.tile(data, (12, 6, 1)) # one repeating layer, size = 120*120*20

m15_c = np.tile(data, (1, 1, 6)) # The 3D continuous M15 model, size = 120*120*120
m15_s = np.zeros((120, 120, 120)) # The M15-in-LAM model composed of 4 repeating layers, interlaced with 4 empty layers each with a height of 15, so height = 20*4+10*4
for z in range(120):
    for x in range(120):
        for y in range(120):
            if z<20: # each repeating layer is with a different orientation to mimic the absence of interlayer correlation in experiments
                m15_s[x,y,z] = data[x,y,z] # rotated by 0 deg
            elif 29<z<50:
                m15_s[x,y,z] = data[y,119-x,z-30] # rotated by -90 deg
            elif 59<z<80:
                m15_s[x,y,z] = data[119-y,x,z-60] # rotated by +90 deg
            elif 89<z<110:
                m15_s[x,y,z] = data[119-x,119-y,z-90] # rotated by 180 deg

# adapted from https://stackoverflow.com/a/21242776
def radial_profile3D(data, resolution=1, ymax=None): # average the 3d FFT into 1d profile
    z, y, x = np.indices((data.shape))
    center = data.shape[0]/2
    r = np.sqrt((x - center)**2 + (y - center)**2 + (z - center)**2) / resolution # np.bincount only discretely counts values that fall within two neiboring intergers, i.e., the counting step size=resolution=1.0. In order to get more information (increaing resolution) or to mimic broadening in reality (lowering resolution), the data here are rescaled
    r = r.astype(np.int)
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    pair = np.array((np.arange(len(nr))*resolution, radialprofile)) # (q, I(q)) pair
    try: ymax = round(ymax/resolution)
    except: pass # ymax can be None
    return pair[:, 1:ymax] # 1: mask center spot; ymax: high-q region is useless

def FFT(data):
    output = np.fft.fftshift(np.abs(np.fft.fftn(data)))
    return output #/np.max(output) # normalize log abs FFT

m15_c_FT = radial_profile3D(FFT(m15_c), 0.6, 30)
m15_s_FT = radial_profile3D(FFT(m15_s), 0.8, 30)

np.save('M15-c_FT.npy', m15_c_FT/np.max(m15_c_FT)) # normalize and save
np.save('M15-s_FT.npy', m15_s_FT/np.max(m15_s_FT))
