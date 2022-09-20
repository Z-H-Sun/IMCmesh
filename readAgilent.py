#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 28 2022

Read and process the ASCII output file from Agilent GPC. The traces will be normalized for the designated time window and stacked into a single graph. Output of the processed data into a csv file is optional.

Usage: readAgilent.py [file1] [file2] ...

@author: ZSun
"""

import csv
import matplotlib.pyplot as plt
import os.path as p
import sys
import time
timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())

# DEFAULT CONFIG BEGINS
# headers of interest
X = 'Retention time'
Y = 'rid1A/ELU'

# the range of data to normalize
NORMRANGE = (11, 27)

OFFSET = 0.2 # distance b/w curves along y
MARGIN = 0.25
AUTOCROP = True # adjust plot range according to NORMRANGE
LONGNAME = True # show filename or index in legend
XLABEL = 'Retention Time (min)'
YLABEL = 'dRI (normalized)'
MARKER = '-'
FONTPROP = {'weight':'bold'}
plt.rcParams['font.family'] = 'serif'
plt.rcParams["mathtext.fontset"] = "dejavuserif"
plt.rcParams['mathtext.default'] = 'bf'
plt.rcParams['axes.labelsize'] = 16

argv = sys.argv
try:
    dir = p.dirname(argv[1]) # the dir of the first input file
except:
    input('The input might be empty or illegal ... ')
    sys.exit()
fn = p.join(dir, 'output-%s.csv' % timestamp) # save in `dir`

OUTPUTNM = fn # output filename# DEFAULT CONFIG ENDS

num = 0
output = [[], []]

def plotFile(filename, offset=0):
    global num
    num += 1

    header = []
    data = []
    with open(filename, newline='') as f:
        r = csv.reader(f, delimiter="\t")
        dataStart = False
        for row in r:
            if not row: continue # empty row
            if dataStart:
                v = map(float, filter(None, map(str.strip, row))) # strip space, clear empty str, convert to float
                try: # see if it is indeed numerical data
                    data.append(tuple(v))
                except: pass
            else:
                try:
                    xIndex = row.index(X)
                    yIndex = row.index(Y)
                    dataStart = True
                except: pass

    dataT = tuple(zip(*data)) # transpose
    xVals = dataT[xIndex]
    yVals = dataT[yIndex]

    for i in range(len(xVals)):
        if not NORMRANGE[0] < xVals[i] < NORMRANGE[1]: continue
        t = yVals[i]
        try:
            if t < yMin: yMin = t
            elif t > yMax: yMax = t
        except NameError: # yMin and yMax not defined
            yMin = yMax = t

    yValsNew = tuple(map(lambda x: (x-yMin)/(yMax-yMin)+offset, yVals))
    longName = p.splitext(p.basename(filename))[0]
    l = plt.plot(xVals, yValsNew, MARKER, label=longName if LONGNAME else str(num))
    #if num==1: l[0].set_visible(False)
    output[0].append(longName)
    output[1].append(xVals)
    output[1].append(yValsNew)

for i in range(1, len(argv)):
    print(num, ':', argv[i])
    plotFile(argv[i], offset=(i-1)*OFFSET)
plt.legend(prop=FONTPROP)
plt.xlabel(XLABEL)
plt.ylabel(YLABEL)
if AUTOCROP:
    plt.xlim(NORMRANGE)
    plt.ylim(-MARGIN, 1+(num-1)*OFFSET+MARGIN)
plt.tight_layout()
plt.show()

print()
if input('Directly press Enter to save data as `%s`, or type anything to cancel ... ' % OUTPUTNM): sys.exit()
with open(OUTPUTNM, 'w', newline='') as f:
    f.write(',,'.join(output[0]))
    f.write('\n')
    for i in zip(*output[1]):
        f.write(','.join(map(str, i)))
        f.write('\n')
