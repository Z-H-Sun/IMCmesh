#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 07 2022

Average enthalpy from .out file and entropy from .dump file to generate Fig S56

@author: runze
"""

# for enthalpy, you need .out from LAMMPS
# first, an initial trial is carried out at a given N_backbone, N_ps, N_pdms, etc.
# this serves as a reference state to make different runs comparable
# then, in a separate run, the captured structure in the initial run is allowed to relax at different \chi values
# arg1: the filename for *the initial trial run*
# arg2: the timestep for the disordered homogeneous state (usually 800 000) in the initial run
# arg3: the filename for *the separate run*
# arg4-5: the range of timesteps where the morphology stabilizes in the second separate run

def enthalpy(filename1, homoStep, filename2, startStep, endStep):

    ref_tot_eng = 0
    
    for line in open(filename1):
        val = line.split()
        try: timestep = int(val[0])
        except: timestep = -1
        if timestep == homoStep:
            ref_tot_eng = float(val[4])
            break
# note the `homoStep` timestep will show up twice: right before and right after the last premixing step
# we need the first one as the reference state, which will be subtracted from each tot_eng value later
# the second one, with inter-bead interactions "turned on," cannot be used as reference
# because energies will be different with different \chi values, which make results from different runs non-comparable
# there might be a little problem, however, if the first energy is chosen as reference
# that DeltaG will be greater than zero, which is confusing as micro-phase separation should be exergonic (spontaneous)
# but what we formulate here is a relative scale for G but not absolute values
# so we randomly choose a reference state (to make comparisons consistent) with inter-bead interactions turned off
# and thus the real energy for that disordered state should be higher

    tot_eng = dict() # {<int timestep>: <float tot_eng>}
    start_reading = False

    for line in open(filename2):
        val = line.split()
        try: timestep = int(val[0])
        except: timestep = -1
        if (timestep == startStep):
            start_reading = True
        if (start_reading):
            tot_eng[timestep] = float(val[4]) - ref_tot_eng
        if (timestep == endStep):
            break

    mean = sum(tot_eng.values()) / len(tot_eng)
    return {'ref_tot_eng': ref_tot_eng, 'tot_eng': tot_eng, 'mean_tot_eng': mean}


# for entropy, you need .dump from LAMMPS
# given discussion above, the *separation runs* do not contain information of the disordered homogeneous state
# so the initial trial run is also necessary to calculate the Kuhn lenth, etc.
# arg1: the filename for *the initial trial run*
# arg2: the frame right after premixing; should be a disordered homogeneous state (usually frame #1)
# arg3: the filename for *the separate run*
# arg4-5: the range of frames where the morphology is already at equilibrium
# **kwargs: example: N_ps=7, N_pdms=4, N_backbone_branched=20, N_backbone_pla=20, see E2E.py
# do not confuse timestep and frame No.
def entropy(dumpFile1, homoFrame, dumpFile2, startFrame, endFrame, **dumpConfig):
    from E2E import BB_TYPE, PS_TYPE, PDMS_TYPE, E2E
    from readDUMP import read

    dumpTypes = (BB_TYPE, PS_TYPE, PDMS_TYPE)
    N_br = dumpConfig['N_ps']+dumpConfig['N_pdms']
    data = read(dumpFile1, homoFrame, dumpTypes, False, False)
    result0 = E2E(data[homoFrame], silent=True, **dumpConfig).main()
    b = result0['kuhn_len']
    Rhomo2 = result0['br_e2e_msd']
    ret = {'b': b, 'R_homo^2': Rhomo2}

    mean_entropy_term = 0
    data = read(dumpFile2, range(startFrame, endFrame+1), dumpTypes, False, False)
    for i in range(startFrame, endFrame+1):
        Rf2 = E2E(data[i], silent=True, **dumpConfig).main()['br_e2e_msd']
        entropy_term = 3*(Rf2-Rhomo2)/2/N_br/(N_br+1)/b**2 # see equation S5
        mean_entropy_term += entropy_term
        ret[data[i]['timestep']] = {'R_f^2': Rf2, '-TdS': entropy_term}
    mean_entropy_term /= (endFrame-startFrame+1)
    ret['mean_entropy_term'] = mean_entropy_term
    return ret

if __name__ == '__main__':
# example
    fn = ('42T-C10_20-A4B7_20_common', '42T-C10_20-A4B7_20_aAB=40')
    H = enthalpy(fn[0]+'.out', 800000, fn[1]+'.out', 8000000, 12000000)
    S = entropy(fn[0]+'.dump', 1, fn[1]+'.out', 8, 12, **{'N_ps':7, 'N_pdms':4, 'N_backbone_branched':20, 'N_backbone_pla':20})
    print(enthalpy)
    print(entropy)
    print('free energy =', H['mean_tot_eng'] + S['mean_entropy_term'])
