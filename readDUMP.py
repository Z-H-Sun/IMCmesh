#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2022

This is a module file that will be imported by other python scripts. The `readDUMP.read` method reads the DUMP files from DPD simulations and outputs the data to an organized dict. The structure of the dict is shown below

dict{<int frame>: <dict frameData>, ...}
  - frameData: dict{'isTriblock', Boolean, 'timestep': int, 'boxsize': <float[] lx,ly,lz>; <int type>: <dict beadData>, ...}
    - beadData: dict{<beadID>: <float[] x,y,z>}

@author: ZSun
"""

# In our dump files, each line has 5 elements, which are
# AtomID AtomType x y z respectively
# Change below accordingly if the sequence is different
DUMP_DATALINE_LEN = 5
DUMP_ID_INDEX = 0
DUMP_TYPE_INDEX = 1
DUMP_XYZ_INDEX = slice(2, 5)
DUMP_TIMESTEP_LINE = 'item: timestep' # all lowercase
DUMP_BOXSIZE_LINE = 'item: box bounds pp pp pp'
PLA_TYPE = 7 # PLA bead is defined as type #7

class nestedDict(dict): # subclass of dict that circumvents KeyError https://stackoverflow.com/a/24089632
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def read(targetFile, targetFrame, targetType, normalize=True, debugInfo=False):
    """
    arg1: dump filename
    arg2: None=store all frames; x (int)=read one specific frame #x; [x, y, ...] (iteratable)=read frams #x, #y, ...
    arg3: None=store all types of beads; x (int)=discard all other beads but #x; [x, y, ...]=store beads #x, #y, ...
    arg4: whether the coornidates are normalized into 0-1 range
    arg5: print verbose info
    output: dict (see above)
    """
    global isTriblock
    isTriblock = False # once bead type # 7 is detected, this value will be set True
    if isinstance(targetFrame, int): targetFrame = (targetFrame,)
    if isinstance(targetType, int): targetType = (targetType,)
    frame = -1
    output = nestedDict()
    with open(targetFile) as file:
        while True:
            line = file.readline()
            if line.strip().lower() == DUMP_TIMESTEP_LINE or (not line): # next 'item: timestep' or EOF
                if debugInfo and (frame in output): # end reading the last frame; print statistics
                    print('\ntimestep', timestep)
                    print('boxsize', boxsize)
                    print('isTriblock', isTriblock)
                    print('beadtypes:')
                    for i in output[frame]:
                        if not isinstance(i, str): print('  # beads ( type', i, '):', len(output[frame][i]))
                if line: # not EOF
                    frame += 1
                    timestep = int(file.readline())
                    continue
                else: break
            if targetFrame and (frame not in targetFrame): continue
            # if frame # is the target frame
            if line.strip().lower() == DUMP_BOXSIZE_LINE: # 'item: box bounds pp pp pp'
                boxsize = []
                lowerbound = []
                for _ in range(3):
                    size = file.readline().split()
                    lowerbound.append(float(size[0]))
                    boxsize.append(float(size[1])-float(size[0]))
                output[frame]['boxsize'] = boxsize
                output[frame]['timestep'] = timestep
                isTriblock = output[frame].setdefault('isTriblock', False) # default; might change later
                continue
            line = line.split() # AtomID AtomType x y z
            if len(line) != DUMP_DATALINE_LEN: continue
            beadType = int(line[DUMP_TYPE_INDEX])
            if beadType == PLA_TYPE: isTriblock = output[frame]['isTriblock'] = True
            if targetType and (beadType not in targetType): continue
            # if bead type is the target type
            beadXYZ = []
            for i in range(3): # reset coordinates w.r.t the origin
                x = float(line[DUMP_XYZ_INDEX][i])-lowerbound[i]
                if not normalize: x *= boxsize[i]
                beadXYZ.append(x)
            output[frame][beadType][int(line[DUMP_ID_INDEX])] = beadXYZ
    return output
