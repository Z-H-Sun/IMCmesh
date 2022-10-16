# Present statistical results for end to end distance of JBBCP backbones in the homo-C domains in different lamellar superstructures, read from a DUMP file from DPD simulations. This generates Fig S51.
# This script is similar to `E2E.py`, but only backbones not branches are analyized, so the > button has the same function as the >> button. You can make use of >| button to speed up the process. After that, click the > button again to finalize the analysis. Refer to `E2E.py` for more info
# Authors: R.Liu & Z.Sun

from E2E import BB_TYPE, PS_TYPE, PDMS_TYPE, E2E
import numpy as np
import matplotlib.pyplot as plt

class E2E_bb_PLA(E2E):

# see `E2E.py`
# framedump: must load `BB_TYPE`
# edges: a list of (N-1) values of y coordinates that divide the box into N regions in height
# **JBBCP_config: must contain the following: N_backbone_branched and N_backbone_pla
    def __init__(self, framedump, edges, **JBBCP_config):
        self.__dict__.update(JBBCP_config)
        self.data = framedump
        self.edges = edges
        self.boxsize = np.array(self.data['boxsize'])
        if not self.data['isTriblock']: raise(RuntimeError('This is not a triblock JBBCP'))
        self.N_backbone = self.N_backbone_branched+self.N_backbone_pla
        M_backbone = len(self.data[BB_TYPE]) / self.N_backbone
        self.M_backbone = int(M_backbone)
        if verbose: print('# backbones (JBBCPs):', self.M_backbone)
        self.sorted_BB_id = sorted(self.data[BB_TYPE].keys())
        self.m_backbone = 0 # the current branch No. \in [0, 1, ..., M_backbone)
        self.bb_e2e_dist = [[] for _ in range(len(edges)+1)] # calculate backbone end to end dist in each region

        self.m_psdms = self.m_backbone # alias to be compatible with the superclass
        self.M_psdms = self.M_backbone
        self.fast_forward = self.next_branch
        self.silent = False
        self.plt = plt

        if not M_backbone.is_integer():
            raise(RuntimeError('The settings of N_backbone_pla and/or N_backbone_branched are likely incorrect'))

    def next_branch(self, event=None): # next backbone
        if self.m_backbone >= self.M_backbone:
            if self.show_plot: plt.close()
            return
        # the id assignment is such that: (see also: `GenJanus.py`)
        # the backbone bead number was first assigned to the homo-PLA domain and then the branched domain
        bb_id = self.sorted_BB_id[self.m_backbone*self.N_backbone:self.m_backbone*self.N_backbone+self.N_backbone_pla]
        bb_xyz = np.array([self.data[BB_TYPE][i] for i in bb_id])

        # for a given x/y/z direction, if offset is greater than CUTOFF, then shift one box period
        for i in range(1, self.N_backbone_pla): 
            dist = bb_xyz[i-1] - bb_xyz[i]
            shift = (dist > self.CUTOFF).astype(int)*self.boxsize - (dist < -self.CUTOFF).astype(int)*self.boxsize
            bb_xyz[i:] += shift

        bb_y = np.mean(bb_xyz[:, 1])
        region = 0
        for i in self.edges: # which region
            if bb_y > i: region += 1

        re = np.sqrt(np.sum((bb_xyz[0]-bb_xyz[-1])**2)) # end-to-end dist
        self.bb_e2e_dist[region].append(re)
        self.m_backbone += 1
        self.m_psdms = self.m_backbone # alias

        title = '#%d: [%d .. %d]'%(self.m_backbone, bb_id[0], bb_id[-1])
        if self.verbose:
            print(title)
            print('Region #', region+1, '; end to end dist =', re)
        if self.show_plot:
            if self.m_backbone == 1: # plot dividing surfaces
                xx, zz = np.meshgrid((0, self.boxsize[0]), (0, self.boxsize[2]))
                for i in self.edges:
                    yy = xx*0+i
                    self.ax.plot_surface(xx, yy, zz, alpha=0.5)
            xyzT = bb_xyz.T
            self.ax.set_title(title)
            for i in self.plots:
                i.remove() # delete old plots
            self.plots.clear()
            self.plots.append(self.ax.scatter(*xyzT, c='C'+str(region), label='Region #'+str(region+1)))
            self.plots.extend(self.ax.plot(*xyzT, 'C'+str(region), alpha=0.5))
            self.ax.legend()
            if self.m_backbone == 1: plt.show()
            else: plt.draw()
        else: # automatically move on
            self.next_branch()

    def finalize(self):
        if self.verbose: print('\n'+'='*50)
        for i, x in enumerate(self.bb_e2e_dist):
            print('Region #', i+1)
            if self.verbose:
                print('  backbone end2end dist list:', [round(i, 2) for i in x])
            re_avg = sum(x)/len(x)
            re_sigma = np.sqrt(sum([(j-re_avg)**2 for j in x])/(len(x)-1))
            # it is fine to get a huge sigma: recall that for random walk, sigma_{R^2}=\sqrt(2n**2-2n) >~ <R^2>
            print('  backbones end2end dist avg:', re_avg, '±', re_sigma, '( N =', len(x), ')')
            hist = plt.hist(x, self.BB_E2E_BINS, rwidth=0.75)
            print('  backbone e2e range\tcount')
            for i in range(len(self.BB_E2E_BINS)-1):
                print('    [',hist[1][i], ',', hist[1][i+1], ')\t', hist[0][i])
            plt.xticks(self.BB_E2E_BINS)
            plt.show()
            print('-'*50)

# example
if __name__ == '__main__':
    import readDUMP # see `readDUMP.py`
    targetFile = '119T-C10_20-A4B7_20.trilayer.dump'
    targetFrame = 10
    targetTypes = BB_TYPE
    targetConfig = {'N_backbone_branched':20, 'N_backbone_pla':20}
    regions = (33, 54,)
    bins = np.arange(1.7, 16, 1.5)
    verbose = True
    data = readDUMP.read(targetFile, targetFrame, targetTypes, False, verbose)[targetFrame]
    e2e_bb = E2E_bb_PLA(data, regions, verbose=verbose, BB_E2E_BINS=bins, fastforward_interval=0.1, **targetConfig)
    e2e_bb.main()
