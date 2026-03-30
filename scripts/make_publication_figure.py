#!/usr/bin/env python3
"""
Create a publication-ready combined spectrum figure and CSV summaries.
Writes:
 - publication_combined_spectrum.png
 - publication_combined_spectrum.pdf
 - ambe_analytic_bins.csv
 - emp_neutron_energies_after_hdpe_5cm.csv/_10cm/_15cm

"""
import os, math, glob
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AMBE_MAC = os.path.join(ROOT, 'ambe_points.mac')

def read_points():
    pts = []
    if os.path.exists(AMBE_MAC):
        with open(AMBE_MAC) as f:
            for ln in f:
                ln = ln.split('#',1)[0].strip()
                if not ln: continue
                if '/gps/hist/point' not in ln: continue
                parts = ln.split()
                if len(parts) < 3: continue
                e = float(parts[-2])
                w = float(parts[-1])
                pts.append((e,w))
    if not pts:
        raise SystemExit('No AMBE points found')
    Es = np.array([p[0] for p in pts], dtype=float)
    Ws = np.array([p[1] for p in pts], dtype=float)
    Ws /= Ws.sum()
    return Es, Ws

def analytic_moderation(Es, Ws, ebins):
    # same crude model as earlier script
    rho_PE = 0.94
    A_mol = 14.0
    NA = 6.02214076e23
    n_mol = rho_PE / A_mol * NA
    n_H = n_mol * 2.0
    sigma_s_H = 20e-24
    Sigma_s = n_H * sigma_s_H
    if Sigma_s <= 0: Sigma_s = 0.1
    mfp = 1.0 / Sigma_s
    xi = 1.0
    Sigma_a = 1e-4
    thicknesses_cm = [5.0, 10.0, 15.0]
    mods = {}
    for t in thicknesses_cm:
        ncoll = t / mfp
        out_Es = Es * np.exp(-ncoll * xi)
        surv = math.exp(-Sigma_a * t)
        out_Ws = Ws * surv
        out_Es[out_Es < 1e-6] = 2.5e-8
        hist, _ = np.histogram(out_Es, bins=ebins, weights=out_Ws)
        pdf = hist / np.diff(ebins)
        mods[t] = pdf
    return mods

def emp_hist_from_file(fname, ebins):
    arr = []
    with open(fname) as f:
        for ln in f:
            ln = ln.split('#',1)[0].strip()
            if not ln: continue
            try:
                arr.append(float(ln))
            except Exception:
                continue
    if not arr:
        return None
    arr = np.array(arr, dtype=float)
    counts, _ = np.histogram(arr, bins=ebins)
    return counts

def write_csv_bins(ebin_centers, pdf, csvpath):
    with open(csvpath, 'w') as f:
        f.write('E_center_MeV,PDF_per_MeV\n')
        for e,p in zip(ebin_centers, pdf):
            f.write(f"{e:.6e},{p:.6e}\n")

def write_csv_counts(ebin_centers, counts, csvpath):
    with open(csvpath, 'w') as f:
        f.write('E_center_MeV,counts,err_plus,err_minus\n')
        for e,c in zip(ebin_centers, counts):
            # Poisson errors (approx symmetric)
            err = math.sqrt(c)
            f.write(f"{e:.6e},{int(c)},{err:.6e},{err:.6e}\n")

def main():
    Es, Ws = read_points()
    Emin = min(1e-11, Es.min() * 0.01)
    Emax = max(Es.max() * 10.0, 10.0)
    nbins = 200
    ebins = np.logspace(math.log10(Emin), math.log10(Emax), nbins + 1)
    ecent = np.sqrt(ebins[:-1] * ebins[1:])

    # analytic original pdf
    orig_hist, _ = np.histogram(Es, bins=ebins, weights=Ws)
    orig_pdf = orig_hist / np.diff(ebins)
    # write analytic bins CSV
    write_csv_bins(ecent, orig_pdf, os.path.join(ROOT, 'ambe_analytic_bins.csv'))

    # compute per-point PDF for plotting (weight divided by local binwidth)
    idx = np.searchsorted(ebins, Es) - 1
    idx = np.clip(idx, 0, len(ebins) - 2)
    widths = np.diff(ebins)
    point_pdf = Ws / widths[idx]

    # moderation
    mods = analytic_moderation(Es, Ws, ebins)
    for t,pdf in mods.items():
        write_csv_bins(ecent, pdf, os.path.join(ROOT, f'ambe_analytic_{int(t)}cm_bins.csv'))

    # empirical files
    emp_files = sorted(glob.glob(os.path.join(ROOT, 'neutron_energies_after_hdpe_*cm.txt')))
    emp_counts = {}
    for ef in emp_files:
        counts = emp_hist_from_file(ef, ebins)
        if counts is None: continue
        emp_counts[os.path.basename(ef)] = counts
        # write per-file CSV
        name = os.path.basename(ef).replace('.txt','.csv')
        write_csv_counts(ecent, counts, os.path.join(ROOT, name))

    # plotting
    plt.figure(figsize=(8,6))
    # analytic original
    plt.loglog(ecent, orig_pdf, color='k', lw=1.5, label='AmBe (analytic)')
    # analytic moderated (dashed)
    colors = ['C1','C2','C3']
    for c, (t,pdf) in zip(colors, mods.items()):
        plt.loglog(ecent, pdf, c=c, lw=1.2, ls='--', label=f'Analytic after {int(t)} cm HDPE')

    # overlay discrete AmBe points (markers)
    plt.scatter(Es, point_pdf, marker='D', c='0.2', s=28, edgecolor='w', zorder=11, label='AmBe points')

    # empirical overlay as markers with Poisson error bars
    for fname, counts in emp_counts.items():
        label = fname.replace('neutron_energies_after_hdpe_','').replace('.txt','')
        counts = counts.astype(float)
        total = counts.sum()
        if total <= 0:
            continue
        # normalized to counts fraction per MeV for plotting consistency
        pdf_emp = counts / total / np.diff(ebins)
        err = np.sqrt(counts) / (total * np.diff(ebins))
        plt.errorbar(ecent, pdf_emp, yerr=err, fmt='o', ms=3, label=f'Geant4 {label}')

    plt.xlabel('Neutron energy [MeV]')
    plt.ylabel('Probability density (per MeV)')
    plt.title('AmBe spectrum — analytic and Geant4 after HDPE')
    plt.legend(fontsize='small', ncol=2)
    plt.grid(which='both', ls=':', alpha=0.4)
    plt.tight_layout()
    outpng = os.path.join(ROOT, 'publication_combined_spectrum.png')
    outpdf = os.path.join(ROOT, 'publication_combined_spectrum.pdf')
    plt.savefig(outpng, dpi=300)
    plt.savefig(outpdf)
    print('Wrote', outpng, outpdf)

if __name__ == '__main__':
    main()
