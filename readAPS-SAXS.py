#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Oct 31 2021

Read and process the 1D averaged SAXS profile from Argonne APS. The traces will be stacked into a single graph.

Usage: readAPS-SAXS.py [file1] [file2] ...

@author: ZSun
"""

OFFSET = 0.5 # distance b/w curves along y
XRANGE = (0.005, 0.2) # range of q values to be plotted (Angstrom^-1)
MARKER = '-o'

import numpy as np
import matplotlib.pyplot as plt

def read(filename):
    with open(filename) as f:
        data = []
        for d in f:
            d = d.split()
            try:
                if float(d[1]) == 0.0: continue
            except:
                continue
            data.append(d[0:2])
    return np.array(data, dtype=np.float32).T

def plot(data, xlim=None, ylim=None, default=True, offset=0):
    global num # curve No.
    num += 1
    x, y = data
    if xlim is not None: # crop data outside of the range
        mask = (x >= xlim[0]) & (x <= xlim[1])
        x = x[mask]; y = y[mask]
    elif default: # default range of X
        mask = (x >= XRANGE[0]) & (x <= XRANGE[1])
        x = x[mask]; y = y[mask]
    if ylim is not None:
        plt.ylim(ylim)

    plt.plot(x, y*10**offset, MARKER, markersize=2, label=str(num))
    plt.xlabel(r'$q$ / $\rm{\AA}^{-1}$', fontsize=14)
    plt.ylabel('$I(q)$', fontsize=14)

import sys
argv = sys.argv
plt.figure()
plt.xscale('log')
plt.yscale('log')
#plt.tight_layout()
plt.subplots_adjust(left=0.12, right=0.99, top=0.99, bottom=0.13)
num = 0
for i in range(1, len(argv)):
    plot(read(argv[i]), offset=(i-1)*OFFSET)
plt.legend()
plt.show()