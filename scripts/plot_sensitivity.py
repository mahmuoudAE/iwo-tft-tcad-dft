#!/usr/bin/env python3
"""plots/sensitivity_overview.png: (a) no-confinement counterfactual overlays at 2 and 13.2 nm, (b) one-at-a-time
metric changes at 2 nm from tables/SENSITIVITY_OAT.csv. No simulator call."""
import csv
from pathlib import Path
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
def curve(run):
    d = next(p for p in (ROOT / 'results' / 'runs').iterdir() if p.name.startswith(run)); r = list(csv.DictReader((d / 'comparison.csv').open()))
    return np.array([float(x['vg_V']) for x in r]), np.array([float(x['measured_A_per_um']) for x in r]), np.array([float(x['atlas_A_per_um']) for x in r])
fig = plt.figure(figsize=(13, 8)); gs = fig.add_gridspec(2, 2)
for i, (t, ref, cf) in enumerate([(2.0, 'run_0012', 'run_0016'), (13.2, 'run_0013', 'run_0017')]):
    ax = fig.add_subplot(gs[0, i]); vg, me, si = curve(ref); _, _, sc = curve(cf)
    ax.semilogy(vg, me, 'k.', ms=4, label='measured'); ax.semilogy(vg, np.maximum(si, 1e-40), 'r-', label='final model (confinement law on)'); ax.semilogy(vg, np.maximum(sc, 1e-40), 'b--', label='counterfactual: dEg = 0, m* = bulk')
    ax.set_ylim(1e-15, 1e-5); ax.set_xlabel('VG (V)'); ax.set_ylabel('ID (A/um), VD = 0.7 V'); ax.set_title(f'{t} nm: confinement law switched off ({cf} vs {ref})', fontsize=9); ax.legend(fontsize=7); ax.grid(alpha=.3)
rows = [r for r in csv.DictReader((ROOT / 'tables' / 'SENSITIVITY_OAT.csv').open()) if float(r['thickness_nm']) == 2.0 and r['case'] != 'no_confinement']
lab = [r['case'] for r in rows]; x = np.arange(len(rows))
for j, (key, name, scale) in enumerate([('dVth_cc_V', 'dVth (mV)', 1000.0), ('dSS_mV_dec', 'dSS_min (mV/dec)', 1.0)]):
    ax = fig.add_subplot(gs[1, j]) if j == 0 else ax
    if j == 0:
        ax.bar(x - 0.2, [float(r['dVth_cc_V']) * 1000 for r in rows], 0.4, label='dVth (mV)'); ax.bar(x + 0.2, [float(r['dSS_mV_dec']) for r in rows], 0.4, label='dSS_min (mV/dec)')
        ax.set_xticks(x); ax.set_xticklabels(lab, rotation=30, ha='right', fontsize=8); ax.axhline(0, color='k', lw=.6); ax.legend(fontsize=8); ax.grid(alpha=.3, axis='y'); ax.set_title('2 nm one-at-a-time perturbations (runs 0020-0027 vs run_0012)', fontsize=9)
ax = fig.add_subplot(gs[1, 1]); ax.bar(x - 0.2, [float(r['dIon_pct']) for r in rows], 0.4, label='dIon at 3 V (%)'); ax.bar(x + 0.2, [float(r['dmu_FE_pct']) for r in rows], 0.4, label='dmu_FE (%)')
ax.set_xticks(x); ax.set_xticklabels(lab, rotation=30, ha='right', fontsize=8); ax.axhline(0, color='k', lw=.6); ax.legend(fontsize=8); ax.grid(alpha=.3, axis='y'); ax.set_title('2 nm one-at-a-time perturbations: on-state', fontsize=9)
fig.suptitle('Counterfactual and sensitivity runs (real ATLAS, identical extraction); cases: chi -/+0.1 eV, Nd x2, Nt x1.5, WTA +5 meV, Dit x3, eps 10.55, overlap 4 um', fontsize=9)
fig.tight_layout(); fig.savefig(ROOT / 'plots' / 'sensitivity_overview.png', dpi=140); print('plots/sensitivity_overview.png')
