#!/usr/bin/env python3
"""
Plot empirical outgoing neutron spectra for each HDPE thickness (5,10,15 cm).
Saves per-thickness PNGs and a combined figure.
"""
import os, glob
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def read_emp(fn):
    arr = []
    with open(fn) as f:
        for ln in f:
            ln = ln.split('#',1)[0].strip()
            if not ln: continue
            try:
                arr.append(float(ln))
            except Exception:
                continue
    return np.array(arr, dtype=float)

def make_bins(Es):
    Emin = max(1e-9, Es.min()*0.1)
    Emax = max(Es.max()*1.1, 11.0)
    nbins = 200
    ebins = np.logspace(np.log10(Emin), np.log10(Emax), nbins+1)
    return ebins

def plot_single(ecent, pdf, fname, title):
    plt.figure(figsize=(8,4.2))
    plt.loglog(ecent, pdf, drawstyle='steps-mid')
    plt.fill_between(ecent, pdf, step='mid', alpha=0.3)
    plt.xlabel('Neutron Energy (MeV)')
    plt.ylabel('Normalized weight (per MeV)')
    plt.title(title)
    plt.grid(which='both', ls=':', alpha=0.4)
    plt.tight_layout()
    plt.savefig(fname, dpi=200)
    plt.close()

def main():
    files = sorted(glob.glob(os.path.join(ROOT, 'neutron_energies_after_hdpe_*cm.txt')))
    if not files:
        print('No empirical files found')
        return
    data = {}
    for f in files:
        key = os.path.basename(f).replace('neutron_energies_after_hdpe_','').replace('.txt','')
        arr = read_emp(f)
        if arr.size == 0: continue
        data[key] = arr

    # decide bins from combined data and ambe analytic points
    all_vals = np.hstack(list(data.values()))
    ebins = make_bins(all_vals)
    ecent = np.sqrt(ebins[:-1]*ebins[1:])

    # per-thickness plots
    for k, arr in data.items():
        counts, _ = np.histogram(arr, bins=ebins)
        total = counts.sum()
        pdf = counts / total / np.diff(ebins)
        outpng = os.path.join(ROOT, f'neutron_pdf_{k}.png')
        plot_single(ecent, pdf, outpng, f'Neutron outgoing spectrum after {k} HDPE')
        print('Wrote', outpng)

    # combined figure
    plt.figure(figsize=(9,5))
    for k, arr in data.items():
        counts, _ = np.histogram(arr, bins=ebins)
        total = counts.sum()
        pdf = counts / total / np.diff(ebins)
        plt.loglog(ecent, pdf, label=f'{k}')
    plt.xlabel('Neutron Energy (MeV)')
    plt.ylabel('Normalized weight (per MeV)')
    plt.title('Geant4::outgoing neutron spectra after HDPE')
    plt.grid(which='both', ls=':', alpha=0.4)
    plt.legend(title='Thickness')
    plt.tight_layout()
    outall = os.path.join(ROOT, 'neutron_pdf_all_thicknesses.png')
    plt.savefig(outall, dpi=200)
    print('Wrote', outall)

if __name__ == '__main__':
    main()
