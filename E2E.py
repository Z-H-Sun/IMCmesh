# This script, on its own, presents statistical results for end to end distance of JBBCP backbones and branches (neglecting the homo-C domain), read from a DUMP file from DPD simulations. This is also a module file that will be imported by other python scripts.
# When `E2E.show_plot` is turned on, backbone and branch beads in the A-branch-B domain will be visualized. Click the > button to move to the next A-B branch, or click the >> button to fast forward (interval=`E2E.fastforward_interval`) to the last A-B branch of the current JBBCP macromolecule. In this process, all backbone beads from previous branches will remain visible unless `E2E.show_current_bb_only` is set. Do not close the matplotlib window until the last branch in the whole box is analyzed. You can make use of >| button to speed up the process. After that, click the > button again to finalize the analysis.
# When importing this module in other python scripts, you may want to turn on `E2E.silent`, which effectively turns off `E2E.show_plot` and `E2E.verbose`.
# Authors: R.Liu & Z.Sun

import numpy as np
PDMS_TYPE = 3
PS_TYPE = 2
PLA_TYPE = 7
BB_TYPE = 1 # bead type 1=backbone; 2=PS; 3=PDMS; 7=PLA

class E2E:

# default settings; can be changed on initialization
    BB_E2E_BINS = np.arange(1, 14, 1.5) # the bin edges for the histogram showing backbone end-to-end distribution: (min, max, step). See also `matplotlib.pyplot.hist`
    CUTOFF = 3 # there is no way for two bonded beads to be >3 units apart in any (x,y,or z) direction
    silent = False # do not print any result
    verbose = True # print detailed analysis info
    show_plot = True # show 3d rendering of JBBCP branches
    show_current_bb_only = False # whether to show previous backbone beads in the current JBBCP molecule
    fastforward_interval = 0.05 # pause time for each plot while fast forwarding (in the unit of second)

    def __init__(self, framedump, **JBBCP_config):
# arg1: dump[targetFrame], where `dump` is the dict provided by `readDUMP.read`
# **JBBCP_config: must contain the following:
# - N_ps, N_pdms, N_backbone_branched
# - N_backbone_pla: required only by triblocks
# - one can also pass on settings here, like `silent`, `verbose`, etc.
        self.__dict__.update(JBBCP_config)
        self.data = framedump
        self.boxsize = np.array(self.data['boxsize'])
        if not self.data['isTriblock']: self.N_backbone_pla = 0 # diblock
        self.N_psdms = self.N_ps+self.N_pdms
        self.N_minor = min(self.N_ps, self.N_pdms)
        M_psdms_1 = len(self.data[PS_TYPE])/self.N_ps
        M_psdms_2 = len(self.data[PDMS_TYPE])/self.N_pdms
        self.M_psdms = int(M_psdms_1)
        self.M_backbone = self.M_psdms // self.N_backbone_branched

        self.sorted_PS_id = sorted(self.data[PS_TYPE].keys())
        self.sorted_PDMS_id = sorted(self.data[PDMS_TYPE].keys())
        self.sorted_BB_id = sorted(self.data[BB_TYPE].keys())

        self.Re2 = [] # [R_{end2end}^2 for different m_psdms] (see Eqn (S5))
        self.Ri2 = [] # [[R_i^2 (i=1,2,...,N_minor)] for different m_psdms]
        self.bb_e2e_dist = [] # for each JBBCP, calculate the backbone end-to-end distance
        self.prev_bb_xyz = [] # the coordinates of the previous backbone beads in the current JBBCP molecule
        self.m_psdms = 0 # the current branch No. \in [0, 1, ..., M_psdms)

        if not self.silent:
            self.plt = __import__('matplotlib.pyplot').pyplot
            if self.verbose:
                print('# AB branches:', self.M_psdms)
                print('# backbones (JBBCPs):', self.M_backbone)

        if M_psdms_1 != M_psdms_2 or (not M_psdms_1.is_integer()):
            raise(RuntimeError('The settings of N_ps and/or N_pdms are likely incorrect'))
        if self.M_backbone*(self.N_backbone_branched+self.N_backbone_pla) != len(
        self.data[BB_TYPE]) or self.M_backbone*self.N_backbone_branched != self.M_psdms:
            raise(RuntimeError('The settings of N_backbone_pla and/or N_backbone_branched are likely incorrect'))

    def main(self): # workflow
        self.initPlot()
        self.next_branch()
        if self.m_psdms >= self.M_psdms: # the last branch has been analyzed
            return self.finalize()
        else: print('WARNING: unexpected close of matplotlib window. Further analysis not performed. If this is unintended, use the >| button to fast forward to the last branch, and then click the > button once more to show the final results.')    

# many macromolecules occupies more than one unit cell as the cell has periodic boundaries
# which causes abrupt change of coordinate values even between two neighboring beads
# transform is thus performed to accurately calculate the real inter-bead distances
    def next_branch(self, event=None):
        if self.m_psdms >= self.M_psdms:
            if self.show_plot and (not self.silent): self.plt.close()
            return
        m_backbone = self.m_psdms // self.N_backbone_branched
        m_branch = self.m_psdms % self.N_backbone_branched
        # the id assignment is such that: (see also: `GenJanus.py`)
        # (N_pdms+N_ps) consecutive beads are with the same backbone bead
        # and the smaller the id, the closer it is to the backbone bead
        # the backbone bead number was first assigned to the homo-PLA domain and then the branched domain
        bb_id = self.sorted_BB_id[m_backbone*(self.N_backbone_branched+self.N_backbone_pla)+self.N_backbone_pla+m_branch]
        bb_xyz = [self.data[BB_TYPE][bb_id]]
        pdms_id = self.sorted_PDMS_id[self.m_psdms*self.N_pdms : self.m_psdms*self.N_pdms+self.N_pdms]
        pdms_xyz = [self.data[PDMS_TYPE][i] for i in pdms_id]
        ps_id = self.sorted_PS_id[self.m_psdms*self.N_ps : self.m_psdms*self.N_ps+self.N_ps]
        ps_xyz = [self.data[PS_TYPE][i] for i in ps_id]
        branch_xyz = np.array(ps_xyz[::-1]+bb_xyz+pdms_xyz)

        for i in range(self.N_psdms):
            dist = branch_xyz[i] - branch_xyz[i+1]
            # for a given x/y/z direction, if offset is greater than CUTOFF, then shift one box period
            # both directions of the shift is taken into account, i.e. the sign of the shift
            shift = (dist > self.CUTOFF).astype(int)*self.boxsize - (dist < -self.CUTOFF).astype(int)*self.boxsize
            branch_xyz[i+1:] += shift

        re2 = np.sum((branch_xyz[0]-branch_xyz[-1])**2)
        ri2 = []
        for i in range(self.N_minor):
            ri2.append(np.sum((branch_xyz[self.N_ps-i-1] - branch_xyz[self.N_ps+i+1])**2))
        self.Re2.append(re2)
        self.Ri2.append(ri2)

        bb_xyz = branch_xyz[self.N_ps]
        if m_branch == 0:
            self.prev_bb_xyz.clear()
        else:
            dist = self.prev_bb_xyz[-1] - bb_xyz # if the current backbone bead crosses cell boundary, then shift the whole branch
            shift = (dist > self.CUTOFF).astype(int)*self.boxsize - (dist < -self.CUTOFF).astype(int)*self.boxsize
            branch_xyz += shift
            bb_xyz = branch_xyz[self.N_ps]
        if m_branch == self.N_backbone_branched-1: # the last bb bead pos
            _bb_e2e_dist = np.sqrt(np.sum((bb_xyz - self.prev_bb_xyz[0])**2))
            self.bb_e2e_dist.append(_bb_e2e_dist)
        self.prev_bb_xyz.append(bb_xyz)
        self.m_psdms += 1

        title = '#%d ($%d_{%d}$): [%d .. %d]-%d-[%d .. %d]'%(self.m_psdms, m_backbone+1, m_branch+1, pdms_id[0], pdms_id[-1], bb_id, ps_id[0], ps_id[-1])
        if self.verbose and (not self.silent):
            if m_branch == 0:
                print('\n'+'-'*50)
                print('Start analyzing JBBCP #', m_backbone+1)
            print('** Branch end-to-end analysis **')
            print(title)
            for i in range(self.N_minor):
                print('R_%d^2 ='%(i+1), ri2[i], end='; ')
            print()
            print('end2end dist =', np.sqrt(re2))
            print()
            if m_branch == self.N_backbone_branched-1:
                print('  ** Backbone end-to-end analysis **')
                print('  end2end dist =', _bb_e2e_dist)
        if self.show_plot and (not self.silent):
            xyzT = branch_xyz.T
            bbT = branch_xyz[N_ps] if self.show_current_bb_only else np.array(self.prev_bb_xyz).T # show prev bb
            self.ax.set_title(title)
            for i in self.plots:
                i.remove() # delete old plots
            self.plots.clear()
            self.plots.append(self.ax.scatter(*xyzT[:, self.N_ps+1:], label='A'))
            self.plots.append(self.ax.scatter(*xyzT[:, :self.N_ps], label='B'))
            self.plots.append(self.ax.scatter(*bbT, marker='s', label='bb'))
            self.plots.extend(self.ax.plot(*xyzT[:, self.N_ps+1:], alpha=0.5))
            self.plots.extend(self.ax.plot(*xyzT[:, :self.N_ps], alpha=0.5))
            self.plots.extend(self.ax.plot(*xyzT[:, self.N_ps-1:self.N_ps+2], alpha=0.5))
            if not self.show_current_bb_only: self.plots.extend(self.ax.plot(*bbT, '--k', lw=2, alpha=0.5))
            self.ax.legend()
            if self.m_psdms == 1: self.plt.show()
            else: self.plt.draw()
        else: # automatically move on
            self.next_branch()

    def fast_forward(self, event=None): # to the end of the current JBBCP molecule
        while self.m_psdms % self.N_backbone_branched:
            self.next_branch()
            if self.show_plot and (not self.silent): self.plt.pause(self.fastforward_interval)

    def to_last(self, event=None): # to the end of the whole box
        while self.m_psdms < self.M_psdms:
            self.next_branch()
            if self.show_plot and (not self.silent): self.plt.pause(self.fastforward_interval)

    def finalize(self):
        if not self.silent:
            hist = self.plt.hist(self.bb_e2e_dist, self.BB_E2E_BINS, rwidth=0.75)
            if self.verbose:
                print('\n'+'='*50); print('Analysis ends.')
                print('backbone end2end dist list:', [round(i, 2) for i in self.bb_e2e_dist])
        re2_avg = sum(self.Re2)/len(self.Re2)
        re2_sigma = np.sqrt(sum([(i-re2_avg)**2 for i in self.Re2])/(len(self.Re2)-1))
        # it is fine to get a huge sigma: recall that for random walk, sigma_{R^2}=\sqrt(2n**2-2n) >~ <R^2>
        if not self.silent:
            print('backbone e2e range\tcount')
            for i in range(len(self.BB_E2E_BINS)-1):
                print('   [', hist[1][i], ',', hist[1][i+1], ')\t', hist[0][i])
            self.plt.xticks(self.BB_E2E_BINS)
            self.plt.show()
            print('\nbranch e2e <R_e^2>:', re2_avg, '±', re2_sigma)
            print('\ni\t <R_i^2>\t R_{i,max}')
        Ri2T = np.array(self.Ri2).T
        Ri2_avg = []
        Rmax = (np.arange(self.N_minor)+1)*2
        for i,x in enumerate(Ri2T):
            avg = np.mean(x)
            sigma = np.sqrt(np.sum((x-avg)**2)/(len(x)-1))
            if not self.silent: print(i+1, '\t', round(avg, 2), '±', round(sigma,2) , '\t', Rmax[i])
            Ri2_avg.append(avg)
        Ri2_avg = np.array(Ri2_avg)

        result = np.polyfit(Rmax, Ri2_avg, 1, full=True)
        a, b = result[0]
        sse = result[1][0]
        sst = np.sum((Ri2_avg-np.mean(Ri2_avg))**2)
        r2 = 1 - sse/sst
        a_sigma = a*np.sqrt((1/r2-1)/(self.N_minor-2))
        if not self.silent:
            print('\nWARNING: The calculation of `b` below is correct ONLY WHEN the current frame is a homogeneous disordered state (usually Frame #0 after premixing).')
            print('<R_i^2> =', a, '*R_{i,max}', '+' if b>0 else '', b, '; r^2= ', r2)
            print('Kuhn segment length = ', a, '±', a_sigma)
            dummy = np.arange(self.N_minor+1)*2
            self.plt.plot(Rmax, Ri2_avg, '-o', label='$\\langle R_i^2\\rangle$')
            self.plt.plot(dummy, a*dummy+b, '--', label='LinFit')
            self.plt.legend()
            self.plt.show()
        return {'br_e2e_msd': re2_avg, 'kuhn_len': a}

    def initPlot(self):
        if (not self.show_plot) or self.silent: return

        def toggleAxes(event=None):
            self.ax._axis3don = not self.ax._axis3don
            self.plt.draw()
        def toggleAutoscale(event=None):
            if self.ax.get_autoscale_on():
                self.ax.autoscale(False)
                self.ax.set_xlim(0, self.boxsize[0])
                self.ax.set_ylim(0, self.boxsize[1])
                self.ax.set_zlim(0, self.boxsize[2])
            else:
                self.ax.autoscale(True)
            self.plt.draw()

        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib.widgets import Button
        self.plots = []
        self.plt.subplots_adjust(left=0, right=1, top=0.95, bottom=0)
        self.ax = self.plt.gca(projection='3d')
        self.ax.set_box_aspect(self.boxsize.copy()) # this requires MatPlotLib >= 3.3.0
        toggleAutoscale() # turn off autoscale and set box bounds
        self.bNext = Button(self.plt.axes((0.81, 0.07, 0.05, 0.05)), '>') # onclick: go to next branch
        self.bNext.on_clicked(self.next_branch)
        self.bForward = Button(self.plt.axes((0.87, 0.07, 0.05, 0.05)), '>>') # onclick: go to the last branch of the current JBBCP
        self.bForward.on_clicked(self.fast_forward)
        self.bLast = Button(self.plt.axes((0.93, 0.07, 0.05, 0.05)), '>|') # onclick: go to the last branch of the whole cell
        self.bLast.on_clicked(self.to_last)

        self.bAxes = Button(self.plt.axes((0.81, 0.01, 0.08, 0.05)), 'Axes') # toggle visibility of the Cartesian axes
        self.bAxes.on_clicked(toggleAxes)
        self.bAutoscale = Button(self.plt.axes((0.9, 0.01, 0.08, 0.05)), 'Zoom') # toggle autoscale (zoom-in/out)
        self.bAutoscale.on_clicked(toggleAutoscale)

if __name__ == '__main__':
    import readDUMP # see `readDUMP.py`
# example 1: diblock; output final results only
    targetFile = '44D-A4B7_20.dump'
    targetFrame = 10
    targetTypes = (BB_TYPE, PS_TYPE, PDMS_TYPE)
    verbose = False
    data = readDUMP.read(targetFile, targetFrame, targetTypes, False, verbose)[targetFrame]
    e2e = E2E(data, N_ps=7, N_pdms=4, N_backbone_branched=20, verbose=verbose, show_plot=False)
    print('final results:', e2e.main())
    input('press enter to continue.')

# example 2: triblock; continuous analysis of multiple frames: for the same dump file, there is no need to read it repetitively
    targetFile = '42T-C10_20-A4B7_20.dump'
    targetFrames = (0, 10)
    targetTypes = (BB_TYPE, PS_TYPE, PDMS_TYPE)
    targetConfig = {'N_ps':7, 'N_pdms':4, 'N_backbone_branched':20, 'N_backbone_pla':20}
    verbose = True
    data = readDUMP.read(targetFile, targetFrames, targetTypes, False, verbose)
    e2e = E2E(data[targetFrames[1]], verbose=verbose, **targetConfig) # show_plot=True
    print('\n\nresults for frame #', targetFrames[1])
    e2e.main()
    input('press enter to continue.')

    # frame#0: disordered homogeneous mixture after premixing
    e2e = E2E(data[targetFrames[0]], silent=True, **targetConfig)
    print('\n\nfinal results for frame #', targetFrames[0], ':', e2e.main())
    input('press enter to continue.')
