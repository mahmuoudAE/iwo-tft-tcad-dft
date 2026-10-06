#!/usr/bin/env python3
"""Final presentation of the three metrics for the three thicknesses, measured vs TCAD: constant-current threshold,
subthreshold swing (on-current-normalised window, amendment A1; the registered fixed window stays in RESULTS.md) and field-effect mobility versus V_G.
Values are read from results.json / results_a1.json. Output: figures/final/*.{png,pdf}, FINAL_SUMMARY.md, final_table.csv.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
import extraction as ex  # noqa: E402
import run_extraction as rx  # noqa: E402
from style import plt, FILM, HALF_W, panel_label  # noqa: E402

OUT = HERE / 'figures' / 'final'
OUT.mkdir(parents=True, exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
A1 = json.loads((HERE / 'results_a1.json').read_text())
MEAS = rx.load_measured()
TC = {t: rx.load_tcad(t) for t in rx.FILMS}
F = [str(t) for t in rx.FILMS]
T = np.array(rx.FILMS)
LEG = dict(fontsize=6.2, frameon=True, framealpha=0.95, edgecolor='0.75', handlelength=1.8)
TXT = dict(fontsize=6.0, linespacing=1.4, bbox=dict(fc='white', ec='0.75', lw=0.5, pad=2.0))
C1, C2 = '#0072B2', '#7F7F7F'


def get(path_fn):
    return np.array([path_fn(f) for f in F])


def new(letter, ylabel):
    fig, a = plt.subplots(figsize=(HALF_W, 2.6))
    panel_label(a, letter)
    a.set_xlabel('IWO thickness (nm)'); a.set_ylabel(ylabel); a.set_xticks(rx.FILMS)
    return fig, a


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf'); fig.savefig(OUT / f'{name}.png', dpi=300); plt.close(fig); print('saved', name)


def pair(a, mv, ms, sv, ss, c, lab):
    a.errorbar(T, mv, yerr=ms, fmt='o-', color=c, ms=4.5, lw=1.1, capsize=2, elinewidth=0.8, label=f'{lab}measured')
    a.errorbar(T, sv, yerr=ss, fmt='s--', color=c, ms=5.5, lw=1.1, mfc='none', mew=1.1, capsize=2, elinewidth=0.8, label=f'{lab}TCAD')


# ---- values
vm, vms = get(lambda f: R['films'][f]['measured']['vth_cc']['v']), get(lambda f: R['films'][f]['measured']['vth_cc']['sig'])
vs, vss = get(lambda f: R['films'][f]['simulated']['vth_cc']['v']), get(lambda f: R['films'][f]['simulated']['vth_cc']['sig'])
nm_, nms = get(lambda f: A1['films'][f]['results']['main']['measured']), get(lambda f: A1['films'][f]['results']['main']['sig_measured'])
ns_, nss = get(lambda f: A1['films'][f]['results']['main']['tcad']), get(lambda f: A1['films'][f]['results']['main']['sig_tcad'])
fm, fms = get(lambda f: R['films'][f]['measured']['ss']['ss']), get(lambda f: R['films'][f]['measured']['ss']['sig'])
fs, fss = get(lambda f: R['films'][f]['simulated']['ss']['ss']), get(lambda f: R['films'][f]['simulated']['ss']['sig'])

# (a) threshold
fig, a = new('a', '$V_{th,cc}$ (V)')
pair(a, vm, vms, vs, vss, C1, '')
dl = ' / '.join(f'{1e3 * (y2 - y1):+.0f}' for y1, y2 in zip(vm, vs))
a.set_ylim(-0.1, 0.95); a.legend(loc='lower left', **LEG)
a.text(0.96, 0.95, f'$I_D = 10^{{-9}}$ A/$\\mu$m ($I_DL/W$ = 20 nA), $V_D$ = 0.7 V\nTCAD $-$ meas.: {dl} mV', transform=a.transAxes,
       ha='right', va='top', **TXT)
save(fig, 'final_a_threshold_cc')

# (b) SS
fig, a = new('b', 'SS (mV/dec)')
pair(a, nm_, nms, ns_, nss, C1, '')
a.set_ylim(95, 150); a.legend(loc='lower left', **LEG)
a.text(0.96, 0.95, 'window [2.15$\\times10^{-5}$, 2.15$\\times10^{-4}$]$\\times I_{on}$', transform=a.transAxes, ha='right', va='top', **TXT)
save(fig, 'final_b_ss')

# (c) mobility versus V_G, all films
fig, a = plt.subplots(figsize=(HALF_W, 2.6))
panel_label(a, 'c')
for t in rx.FILMS:
    vg, i = MEAS[t]; tc = TC[t]; col = FILM[t]
    _, sig = ex.gm_sigma(vg, i)
    k = (vg >= 1.0 - 1e-9) & (vg <= 3.0 + 1e-9)
    mu = ex.MU_FACTOR * ex.gm(vg, i)
    ks = (tc['vg'] >= 1.0 - 1e-9) & (tc['vg'] <= 3.0 + 1e-9)
    a.errorbar(vg[k], mu[k], yerr=ex.MU_FACTOR * sig[k], fmt='o', ms=2.6, mfc='none', mec=col, mew=0.7, ecolor=col, elinewidth=0.5)
    a.plot(tc['vg'][ks], ex.MU_FACTOR * ex.gm(tc['vg'], tc['i'])[ks], '-', color=col, lw=1.3, label=f'{t:.1f} nm')
a.set_xlim(0.95, 3.05); a.set_ylim(0, 56)
a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$\\mu_{FE}$ (cm$^2$/Vs)')
a.legend(loc='center right', title='circles: measured\nlines: TCAD', title_fontsize=5.8, **LEG)
save(fig, 'final_c_mobility_vs_vg')

# ---- table
rows = []
for j, f in enumerate(F):
    m, s = R['films'][f]['measured'], R['films'][f]['simulated']
    row = {'film_nm': f, 'Vth_cc_meas_V': vm[j], 'Vth_cc_meas_sig': vms[j], 'Vth_cc_TCAD_V': vs[j], 'Vth_cc_TCAD_sig': vss[j],
           'SS_norm_meas': nm_[j], 'SS_norm_meas_sig': nms[j], 'SS_norm_TCAD': ns_[j], 'SS_norm_TCAD_sig': nss[j]}
    for v in ('1.0', '1.5', '2.0', '2.5', '3.0'):
        row[f'muFE_{v}V_meas'] = m['mu_fe'][v]['mu_fe']; row[f'muFE_{v}V_meas_sig'] = m['mu_fe'][v]['sig']
        row[f'muFE_{v}V_TCAD'] = s['mu_fe'][v]['mu_fe']; row[f'muFE_{v}V_TCAD_sig'] = s['mu_fe'][v]['sig']
    rows.append(row)
with open(HERE / 'final_table.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

pm = lambda a_, b_, n=3: f'{a_:.{n}f} ± {b_:.{n}f}'
L = ['# Final values: threshold, SS and mobility for the three thicknesses (generated by final_summary.py)', '',
     'Measured devices at V_D = 0.7 V (one device per thickness) and the calibrated V1 TCAD runs 0038 / 0039 / 0040.',
     'Uncertainties are 1 sigma (measurement noise and extraction method); they do not include device-to-device spread.', '',
     '| quantity | 2.0 nm meas. | 2.0 nm TCAD | 6.3 nm meas. | 6.3 nm TCAD | 13.2 nm meas. | 13.2 nm TCAD | TCAD status |',
     '|---|---|---|---|---|---|---|---|']


def line(name, mv, ms, sv, ss, n, status):
    cells = ' | '.join(f'{pm(mv[j], ms[j], n)} | {pm(sv[j], ss[j], n)}' for j in range(3))
    L.append(f'| {name} | {cells} | {status} |')


line('V_th,cc at 1e-9 A/um (V)', vm, vms, vs, vss, 3, 'fitted (Q_f)')
line('SS, normalised window (mV/dec)', nm_, nms, ns_, nss, 1, '2.0 nm fitted; 6.3, 13.2 nm not fitted')
for v in ('1.0', '1.5', '2.0', '2.5', '3.0'):
    mv = get(lambda f: R['films'][f]['measured']['mu_fe'][v]['mu_fe']); ms = get(lambda f: R['films'][f]['measured']['mu_fe'][v]['sig'])
    sv = get(lambda f: R['films'][f]['simulated']['mu_fe'][v]['mu_fe']); ss = get(lambda f: R['films'][f]['simulated']['mu_fe'][v]['sig'])
    line(f'mu_FE at V_G = {v} V (cm2/Vs)', mv, ms, sv, ss, 2, 'shape not fitted; level set by I_on fit')
L += ['', '## Figure captions', '',
      '**(a) `final_a_threshold_cc`.** Constant-current threshold voltage (I_D = 1 nA/um, I_D L/W = 20 nA, V_D = 0.7 V) against '
      'IWO thickness, measured (filled circles) and TCAD (open squares). Numbers give TCAD - measured. The TCAD fixed charge was '
      'fitted to this threshold (one value shared by 2.0 and 13.2 nm), so the agreement is a calibration residual, not a validation. Lines between thicknesses are guides to the eye.', '',
      '**(b) `final_b_ss`.** Subthreshold swing against thickness, measured (filled circles) and TCAD (open squares), in a one-decade current window normalised to each device\'s on-current, '
      '[2.15e-5, 2.15e-4] x I_on, at least 10 x above the off-state floor in every film, so no floor correction is needed. TCAD agrees within 3 mV/dec at 2.0 and 6.3 nm and is 16 mV/dec too high at 13.2 nm (excess near-edge tail states in the model at this thickness). The tail parameters were fitted on the 2.0 nm device only, so only 6.3 and 13.2 nm are tests. The normalised window was defined after the first results and registered as protocol amendment A1 before its TCAD values were computed. Lines are guides to the eye.', '',
      '**(c) `final_c_mobility_vs_vg`.** Field-effect mobility mu_FE = L g_m/(W C_ox V_D) between V_G = 1 and 3 V, measured '
      '(circles, error bars = local measurement noise) and TCAD (lines). The TCAD band mobility was fitted to I_D(3 V) of each '
      'film; the gate-voltage dependence is not fitted. Below about V_G = V_T + V_D the device is not in the linear regime and '
      'mu_FE is a normalised transconductance. C_ox is the geometric value (0.896 uF/cm2); with the effective capacitance (C_eff/C_ox = 0.87) all mobilities, measured and TCAD, would be about 15 % higher.']
(HERE / 'FINAL_SUMMARY.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('\n'.join(L[:16]))
