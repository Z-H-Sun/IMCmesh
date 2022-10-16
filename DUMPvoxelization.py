#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2022

Read the DUMP files from DPD simulations. Extract the coordinates of a certain type bead in a certain frame. Voxelize the box and count # beads of interest in each voxel. Output the voxel array into .npy binary files. The .npy file could be visualized by loading it into tomviz; its reciprocal space pattern could be calculated by numpy.fft.fftn (See also: M15FT.py and showFFT.ipynb).

Usage: DUMPvoxelization.py [file] [frame] [type]
- file: the dump filename
- frame: the specific frame of interest in the DUMP file; usually the last frame (at equilibrium)
- type: the type of the bead of interest; usually the minority block. In our case, it is usually set as 3 (3=PDMS; see GenJanus.py)

@author: ZSun
"""

import sys
import numpy as np
import readDUMP # see `readDUMP.py`
VOXELNUM = (32, 32, 32) # voxelize the box into x*y*z grids
PLOT = True # whether to 3d visualize the result (experimental)
PLOT_ISOVAL = 1 # the isosurface for 3d rendering (the larger value gives fewer voxels)

VOXELNUM = np.array(VOXELNUM, dtype=np.int)
targetFile = sys.argv[1]
targetFrame = int(sys.argv[2])
targetType = int(sys.argv[3])
data = readDUMP.read(targetFile, targetFrame, targetType, True, True)[targetFrame][targetType]

xyz = np.array(tuple(data.values())) * VOXELNUM # rescale
stat = np.zeros(VOXELNUM, dtype=np.uint8)

def _round(coord): # round coordinates (taking into account the periodic boundary condition)
    coord = np.round(coord).astype(int)
    coord %= VOXELNUM # if reach the upper/lower bound, reset to be within the box
    return coord

for coord in xyz:
    coord = _round(coord)
    stat[tuple(coord)] += 1

np.save(targetFile+'.npy', stat)
print('Voxel info saved to', targetFile+'.npy')

if PLOT:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = plt.gca(projection='3d')
    ax.set_box_aspect(VOXELNUM) # this requires MatPlotLib >= 3.3.0
    ax.voxels(stat >= PLOT_ISOVAL, alpha=0.25) # this requires MatPlotLib >= 2.1.0
    plt.show()
