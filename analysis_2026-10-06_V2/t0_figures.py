"""Figures of step T0 from t0_results.json: (a) measured off-state floors vs the ungated-strip variants,
(b) conduction-band shift laws V1 (literature proxies) vs V2 (this work's DFT), (c) conduction-band share of the gap opening."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from style import FULL_W, panel_label  # noqa: E402
import t0_prechecks as t0  # noqa: E402

R = json.loads((HERE / 't0_results.json').read_text())
fs = R['floor_screen']
fig, ax = plt.subplots(1, 3, figsize=(FULL_W, 3.9), gridspec_kw=dict(wspace=0.55))
ts = np.array([2.0, 6.3, 13.2])
meas = np.array([fs['measured_floor_A_per_um'][str(t)] for t in ts])
ax[0].loglog(ts, meas, 'ks', ms=5, label='measured floor', zorder=5)
for c, (case, col, lab) in enumerate((('N', '#1f77b4', 'strip N: neutral film'), ('D', '#d62728', 'strip D: + interface acceptors'),
                                      ('Q', '#7f7f7f', 'strip Q: + Qf as channel'))):
    d = fs['cases'][case]['films']
    ax[0].loglog(ts, [d[str(t)]['predicted_floor_A_per_um'] for t in ts], 'o-', color=col, ms=3, lw=1, label=f"{lab} (t$^{{{fs['cases'][case]['exponent_2_to_13p2']:.2f}}}$)")
sens = fs['case_D_sensitivity_pred_over_meas']
lo = [min(v[str(t)] for v in sens.values()) * meas[k] for k, t in enumerate(ts[:2])] + [meas[2]]
hi = [max(v[str(t)] for v in sens.values()) * meas[k] for k, t in enumerate(ts[:2])] + [meas[2]]
ax[0].fill_between(ts, lo, hi, color='#d62728', alpha=0.15, lw=0, label=r'strip D, Dit or $N_{d0}$ $\times$0.5 to $\times$2')
ax[0].set_xlabel('IWO thickness (nm)'); ax[0].set_ylabel(r'off-state floor (A/$\mu$m)'); ax[0].legend(fontsize=5, loc='upper center', bbox_to_anchor=(0.5, -0.24), frameon=False)
ax[0].set_xticks(ts); ax[0].set_xticklabels([f'{t:g}' for t in ts]); ax[0].minorticks_off()
tt = np.logspace(np.log10(0.45), np.log10(15), 200)
ax[1].loglog(tt, t0.dEc_v1(tt), color='0.5', lw=1.2, label=r'V1: $\Delta E_c=\Delta E_g$ (Lin 2022, Si 2021)')
ax[1].loglog(tt[tt >= 0.95], t0.dEc_v2(tt[tt >= 0.95]), color='#d62728', lw=1.4, label=r'V2: $\Delta E_c$ law (this work)')
ax[1].loglog(tt[tt >= 0.95], t0.dEg_v2(tt[tt >= 0.95]), color='#d62728', lw=0.9, ls='--', label=r'V2: $\Delta E_g$ law (this work)')
ax[1].loglog(list(t0.DFT['dEc']), list(t0.DFT['dEc'].values()), 'o', color='#d62728', ms=4, label=r'DFT $\Delta E_c$ (this work)')
ax[1].loglog(list(t0.DFT['dEg']), list(t0.DFT['dEg'].values()), 'o', mfc='none', color='#d62728', ms=4, label=r'DFT $\Delta E_g$ (this work)')
for t in ts:
    ax[1].axvline(t, color='k', lw=0.4, ls=':')
ax[1].set_xlabel('IWO thickness (nm)'); ax[1].set_ylabel('shift relative to bulk (eV)'); ax[1].legend(fontsize=5, loc='upper center', bbox_to_anchor=(0.5, -0.24), frameon=False)
tb = R['dft_swap']['table']
ax[2].bar([0, 1, 2], [R['dft_swap']['rigid_shift_from_laws_V'][str(t)] * 1000 for t in ts], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax[2].axhline(0, color='k', lw=0.5)
ax[2].set_xticks([0, 1, 2]); ax[2].set_xticklabels([f'{t:g}' for t in ts]); ax[2].set_xlabel('IWO thickness (nm)'); ax[2].set_ylabel('curve shift V1 $\\rightarrow$ V2 (mV)')
for k, t in enumerate(ts):
    v = R['dft_swap']['rigid_shift_from_laws_V'][str(t)] * 1000
    ax[2].text(k, v - 6, f'{v:.0f}', ha='center', va='top', fontsize=6.5)
ax[2].set_ylim(-95, 10)
for k, a in enumerate(ax):
    panel_label(a, 'abc'[k])
(HERE / 'figures').mkdir(exist_ok=True)
for ext in ('png', 'pdf'):
    fig.savefig(HERE / 'figures' / f't0_floor_and_laws.{ext}', dpi=200, bbox_inches='tight')
print('written figures/t0_floor_and_laws.png/.pdf')
