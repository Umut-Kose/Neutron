#!/usr/bin/env python3
"""Simple analysis: open mca.root, plot MCA H1 and per-event Edep distribution.
Requires: uproot, numpy, matplotlib
Usage: python analysis/plot_mca_edep.py mca.root
"""
import sys
import uproot
import numpy as np
import matplotlib.pyplot as plt

fn = sys.argv[1] if len(sys.argv) > 1 else 'mca.root'
print('Opening', fn)
with uproot.open(fn) as f:
    # Try the histogram name 'MCA'
    if 'MCA' in f:
        h = f['MCA']
        # Use uproot histogram convenience method
        counts, edges = h.to_numpy()
        centers = 0.5 * (edges[:-1] + edges[1:])
        plt.figure(figsize=(8,4))
        plt.step(centers, counts, where='mid')
        plt.xlabel('ADC channel (approx keV)')
        plt.ylabel('Counts')
        plt.title('MCA')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('MCA.png')
        print('Wrote MCA.png')
    else:
        print('Histogram MCA not found in', fn)

    # Events ntuple
    if 'Events' in f:
        tree = f['Events']
        arr = tree.arrays(['edep','edepQuenched'], library='np')
        edep = arr['edep']
        edepq = arr['edepQuenched']
        plt.figure(figsize=(8,4))
        plt.hist(edepq*1000.0, bins=200, histtype='step')
        plt.xlabel('Quenched energy (keVee)')
        plt.ylabel('Events')
        plt.title('Per-event quenched Edep')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('EdepQuenched.png')
        print('Wrote EdepQuenched.png')
    else:
        print('Ntuple Events not found in', fn)

print('Done')
