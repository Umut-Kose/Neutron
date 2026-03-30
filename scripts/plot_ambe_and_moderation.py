#!/usr/bin/env python3
"""
Robust plot of AmBe spectrum and a crude moderation estimate through HDPE.
Saves ambe_moderation_estimate.png and prints numeric summaries.
"""
import os
import sys
import math
import re
import numpy as np
import matplotlib.pyplot as plt

# Files (repo-root relative)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AMBE_MAC = os.path.join(ROOT, 'ambe_points.mac')
AMBE_TXT = os.path.join(ROOT, 'ambe_spectrum.txt')

# regex for floating point numbers
num_re = re.compile(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?')

def extract_number(tok):
    if tok is None:
        return None
    m = num_re.search(tok)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None


def read_points():
    points = []
    # prefer generated macro
    if os.path.exists(AMBE_MAC):
        with open(AMBE_MAC) as f:
            for ln in f:
                ln = ln.split('#', 1)[0].strip()
                if not ln:
                    continue
                if '/gps/hist/point' not in ln:
                    continue
                parts = ln.split()
                # accept both "/gps/hist/point <E> <weight>" (3 tokens)
                # and "/gps/hist/point <index> <E> <weight>" (4 tokens)
                if len(parts) < 3:
                    continue
                # energy and weight are expected to be the last two tokens
                e = extract_number(parts[-2])
                w = extract_number(parts[-1])
                if e is None or w is None:
                    continue
                points.append((e, w))

    # fallback to the plain spectrum file
    if not points and os.path.exists(AMBE_TXT):
        with open(AMBE_TXT) as f:
            for ln in f:
                ln = ln.split('#', 1)[0].strip()
                if not ln:
                    continue
                parts = re.split(r'\s+', ln)
                if len(parts) < 2:
                    continue
                e = extract_number(parts[0])
                w = extract_number(parts[1])
                if e is None or w is None:
                    continue
                points.append((e, w))

    return points


def main():
    pts = read_points()
    if not pts:
        print('No AmBe points found in', AMBE_MAC, 'or', AMBE_TXT)
        sys.exit(1)

    Es = np.array([p[0] for p in pts], dtype=float)
    Ws = np.array([p[1] for p in pts], dtype=float)

    if np.allclose(Ws.sum(), 0.0):
        print('Warning: sum of weights is zero; switching to uniform weights')
        Ws = np.ones_like(Ws)

    Ws = Ws / Ws.sum()

    print('Parsed %d points. Energy range (MeV): %.6g - %.6g' % (len(Es), Es.min(), Es.max()))
    print('Sum weights (normalized): %.12g' % Ws.sum())

    # energy bins (logarithmic)
    # choose a floor small enough to include thermalized/very-low-energy neutrons
    # use the smaller of a tiny floor and Es.min()*0.01 so we don't accidentally
    # set Emin larger than thermal energy when Es.min() is relatively large.
    Emin = min(1e-11, Es.min() * 0.01)
    Emax = max(Es.max() * 10.0, 10.0)
    nbins = 200
    ebins = np.logspace(math.log10(Emin), math.log10(Emax), nbins + 1)

    orig_hist, _ = np.histogram(Es, bins=ebins, weights=Ws)
    orig_pdf = orig_hist / np.diff(ebins)

    # crude moderation model parameters (polyethylene CH2)
    rho_PE = 0.94  # g/cm3
    A_mol = 14.0
    NA = 6.02214076e23
    n_mol = rho_PE / A_mol * NA
    n_H = n_mol * 2.0
    sigma_s_H = 20e-24  # cm^2 (approx)
    Sigma_s = n_H * sigma_s_H
    if Sigma_s <= 0:
        Sigma_s = 0.1
    mfp = 1.0 / Sigma_s
    xi = 1.0
    Sigma_a = 1e-4

    thicknesses_cm = [5.0, 10.0, 15.0]

    def moderated_pdf(thickness_cm):
        ncoll = thickness_cm / mfp
        out_Es = Es * np.exp(-ncoll * xi)
        surv = math.exp(-Sigma_a * thickness_cm)
        out_Ws = Ws * surv
        thermal_thresh = 1e-6
        out_Es[out_Es < thermal_thresh] = 2.5e-8
        hist, _ = np.histogram(out_Es, bins=ebins, weights=out_Ws)
        pdf = hist / np.diff(ebins)
        return pdf

    mods = {f'{t}cm': moderated_pdf(t) for t in thicknesses_cm}

    # compute per-point PDF estimate (weight divided by local binwidth)
    # find which bin each original point falls into
    idx = np.searchsorted(ebins, Es) - 1
    # clamp
    idx = np.clip(idx, 0, len(ebins) - 2)
    widths = np.diff(ebins)
    point_pdf = Ws / widths[idx]

    # plot
    plt.figure(figsize=(9,5))
    xb = np.sqrt(ebins[:-1] * ebins[1:])
    plt.loglog(xb, orig_pdf + 1e-40, label='Original AmBe')
    # overlay discrete AmBe points as markers
    plt.scatter(Es, point_pdf, marker='o', s=30, c='k', edgecolor='w', zorder=10, label='AmBe points')
    for k, pdf in mods.items():
        plt.loglog(xb, pdf + 1e-40, label=f'After {k} HDPE (crude)')
    plt.xlabel('Neutron energy [MeV]')
    plt.ylabel('Probability density (per MeV)')
    plt.legend()
    plt.grid(which='both', ls=':', alpha=0.5)
    plt.title('AmBe spectrum and crude HDPE moderation estimate')
    plt.tight_layout()
    outpng = os.path.join(ROOT, 'ambe_moderation_estimate.png')
    plt.savefig(outpng, dpi=200)
    print('Wrote', outpng)

    # numeric summaries
    for k, pdf in mods.items():
        print(k, 'total probability (sum pdf*binwidth)=', np.sum(pdf * np.diff(ebins)))

    # If Geant4 produced empirical files of outgoing neutron energies, plot them
    import glob
    emp_glob = sorted(glob.glob(os.path.join(ROOT, 'neutron_energies_after_hdpe*.txt')))
    if emp_glob:
        plt.figure(figsize=(9,5))
        plt.loglog(xb, orig_pdf + 1e-40, label='Original AmBe')
        # overlay discrete AmBe points on empirical figure as well
        plt.scatter(Es, point_pdf, marker='o', s=30, c='k', edgecolor='w', zorder=10, label='AmBe points')
        for ef in emp_glob:
            emp = []
            with open(ef) as f:
                for ln in f:
                    ln = ln.split('#',1)[0].strip()
                    if not ln: continue
                    try:
                        emp.append(float(ln))
                    except Exception:
                        continue
            if not emp:
                continue
            emp = np.array(emp, dtype=float)
            emp_hist, _ = np.histogram(emp, bins=ebins)
            # normalize to counts (pdf per MeV scaled by counts)
            emp_pdf = emp_hist / np.diff(ebins) / max(1, emp_hist.sum())
            label = os.path.basename(ef).replace('neutron_energies_after_hdpe', '').replace('.txt','')
            if label == '': label = 'Geant4 outgoing'
            plt.loglog(xb, emp_pdf + 1e-40, label=f'Geant4 outgoing {label}')
        plt.xlabel('Neutron energy [MeV]')
        plt.ylabel('Counts (normalized)')
        plt.legend()
        plt.grid(which='both', ls=':', alpha=0.5)
        plt.title('Geant4 recorded neutron energies after HDPE')
        plt.tight_layout()
        outpng2 = os.path.join(ROOT, 'neutron_energies_after_hdpe_all.png')
        plt.savefig(outpng2, dpi=200)
        print('Wrote', outpng2)

if __name__ == '__main__':
    main()
