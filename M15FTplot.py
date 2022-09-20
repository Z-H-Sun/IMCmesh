#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 5 2022

Show the simulated SAXS curves for 1) 3D continuous M15 and 2) sliced M15-in-LAM structures.
See also: `M15FT.py`
The "powder XRD pattern" for the first case is predicted by Mercury (CCDC) from an "artifical" crystal file of M15 space group, `M15FT/M15-ballstick.cif`.

@author: ZSun
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import Akima1DInterpolator

XLABEL = r'$\tilde q\ ({\rm Boxsize}^{-1})$'
YLABEL = 'Intensity (a.u.)'
plt.rcParams['font.family'] = 'serif'
plt.rcParams["mathtext.fontset"] = "dejavuserif"
plt.rcParams['axes.labelsize'] = 16

x0,y0 = np.load('M15FT/M15-c_FT.npy')
x1,y1 = np.load('M15FT/M15-s_FT.npy')

pxrd = [[0.253271956, 0], [0.457301303, 69.5835], # PXRD raw data from Mercury
        [0.473166251, 144.397], [0.488950124, 627.581], # [q, I(q)]
        [0.496810812, 2731.11], [0.504650218, 2113.64],
        [0.512468007, 565.181], [0.520263843, 337.239],
        [0.535788323, 457.897], [0.543516303, 872.132],
        [0.551220999, 2876.13], [0.558902083, 10000],
        [0.566559226, 3018.05], [0.574192099, 901.904],
        [0.581800376, 480.01], [0.596941837, 434.628],
        [0.604474373, 1062.23], [0.611981016, 3624.36],
        [0.619461443, 1190.58], [0.626915334, 361.457],
        [0.649114608, 83.2434], [0.707066307, 27.1859],
        [0.735325125, 84.116], [0.742311835, 263.667],
        [0.749266747, 1034.18], [0.756189563, 367.319],
        [0.769937723, 45.046], [0.874980671, 29.8195],
        [0.893642021, 256.246], [0.899786263, 1125.59],
        [0.911958854, 157.881], [0.92992411, 299.586],
        [0.935833199, 858.518], [0.941702201, 233.179],
        [0.959066171, 26.4104], [0.98718124, 31.8842],
        [0.998132928, 327.825], [1.003544754, 211.716],
        [1.014239211, 29.0028], [1.029954484, 173.093],
        [1.035104967, 70.9502], [1.045272691, 10.801],
        [1.106922372, 19.5965], [1.115706511, 192.031],
        [1.120026985, 215.006], [1.128523815, 29.0196],
        [1.136827278, 44.6662], [1.144935951, 508.029],
        [1.148916806, 212.592], [1.156730701, 29.487],
        [1.168079509, 55.2892], [1.171762585, 219.895],
        [1.175395468, 105.08], [1.182510029, 13.2821], [1.22470725, 0]]
pxrdp = [[0.253271956, 0], [0.496810812, 2731.11], [0.558902083, 10000],
        [0.611981016, 3624.36], [0.707066307, 27.1859], [0.749266747, 1034.18],
        [0.899786263, 1125.59], [0.935833199, 858.518], [0.998132928, 327.825],
        [1.029954484, 173.093], [1.120026985, 215.006], [1.144935951, 508.029],
        [1.171762585, 219.895], [1.22470725, 0]]
px, py = zip(*pxrd)
px = np.array(px)*23.8 # normalization of q
py = np.array(py)/10000 # normalization of I(q)
pxp, pyp = zip(*pxrdp)
pxp = np.array(pxp)*23.8
pyp = np.array(pyp)/10000

model0 = Akima1DInterpolator(x0, y0) # smooth the curves
model1 = Akima1DInterpolator(x1, y1)

X0 = np.linspace(x0.min(), x0.max(), 500)
Y0 = model0(X0)
X1 = np.linspace(x1.min(), x1.max(), 500)
Y1 = model1(X1)

plt.figure()
plt.plot(px, py, 'C3x', ms=5, alpha=0.8) # PXRD
kwargs = {'textcoords': 'offset points', 'arrowprops': {'arrowstyle': '->'}, 'fontsize': 'x-small'}
plt.annotate('001', xy=(6, 0.05), xytext=(0, 20), ha='center', **kwargs) # index the peaks
plt.annotate('002', xy=(11.8, 0.3), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('110\n021', xy=(13.8, 1), xytext=(32, 0), ha='right', va='center', **kwargs)
plt.annotate('111', xy=(14.6, 0.75), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('022', xy=(16.8, 0.05), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('11$\\overline{2}$', xy=(17.8, 0.15), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('130    \n023    ', xy=(21.4, 0.15), xytext=(0, 20), ha='center', **kwargs)
plt.annotate(' 131\n 113', xy=(22.3, 0.12), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('200\n040\n004', xy=(23.9, 0.08), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('   13$\\overline{2}$', xy=(24.6, 0.04), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('202  \n042  ', xy=(26.7, 0.045), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('221\n11$\\overline{4}$', xy=(27.3, 0.085), xytext=(0, 30), ha='center', **kwargs)
plt.annotate(' 133', xy=(28, 0.045), xytext=(0, 20), ha='center', **kwargs)
plt.annotate('    222', xy=(29.2, 0.045), xytext=(0, 20), ha='center', **kwargs)
plt.plot(pxp, pyp, 'C3|', ms=12, markeredgewidth=2, alpha=0.8)

plt.plot(X0, Y0)
plt.xlabel(XLABEL)
plt.ylabel(YLABEL)
plt.tight_layout()
plt.show()

plt.figure()
plt.plot(X1, Y1)
plt.xlabel(XLABEL)
plt.ylabel(YLABEL)
plt.tight_layout()
plt.show()
