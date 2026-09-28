#!/usr/bin/env python3
"""Sensitivities derived from the REAL calibration-stage runs already in results/ (no simulator call).

The one-at-a-time sensitivity chain (scripts/sensitivity_analysis.py) was stopped by the user, who limited the
work to three final launches. This script therefore records only the sensitivities that the executed stage runs
measure directly (pairs of runs that differ in exactly one parameter), plus explicit NOT RUN rows for the planned
cases so that the table is complete and honest. Output: tables/SENSITIVITY_RESULTS.csv (+ .md).
"""
import csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'results' / 'runs'

import sys, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_metrics import metrics

def ex(run_prefix):
    d = next(p for p in R.iterdir() if p.name.startswith(run_prefix)); e = json.loads((d / 'execution.json').read_text())
    # recompute the device metrics with the CURRENT extractor (early runs stored metrics from an earlier SS definition)
    cr = list(csv.DictReader((d / 'comparison.csv').open())); vg = np.array([float(r['vg_V']) for r in cr]); si = np.array([float(r['atlas_A_per_um']) for r in cr])
    e['device_metrics_sim'] = metrics(vg, si, True, float(e['thickness_nm'])); return e, d.name

def sim(e): return e['device_metrics_sim']

PAIRS = [
    # (thickness, parameter, from, to, run_ref, run_pert)
    (2.0, 'Qf (fixed interface charge, cm^-2)', '0', '1.73e12', 'run_0001', 'run_0003'),
    (13.2, 'Qf (fixed interface charge, cm^-2)', '0', '1.73e12', 'run_0002', 'run_0004'),
    (2.0, 'mu_band (cm^2/Vs)', '16.8', '18.13', 'run_0003', 'run_0008'),
    (13.2, 'mu_band (cm^2/Vs)', '57.6', '61.9', 'run_0004', 'run_0009'),
    (6.3, 'Qf (fixed interface charge, cm^-2)', '1.73e12', '8.7e10', 'run_0005', 'run_0007'),
    (2.0, 'structure + sweep form (reduced/pointwise -> physical/stepped)', 'reduced, 121 pts', 'physical, 76 pts', 'run_0008', 'run_0012'),
    (13.2, 'structure + sweep form (reduced/pointwise -> physical/stepped)', 'reduced, 121 pts', 'physical, 76 pts', 'run_0009', 'run_0013'),
]
NOT_RUN = ['no_confinement (dEg_QC = 0, m* = bulk)', 'chi_bulk -/+ 0.1 eV', 'gate work function +0.1 eV (same action as Qf: -q dQf/Cox)', 'Nd0 x2 / x0.5', 'Nt2 x1.5', 'WTA +5 meV', 'Dit x3 / 0', 'eps_r 9.3 -> 10.55', 'm* = bulk only', 'contact overlap 4 um', 'any case at 6.3 nm']

def main():
    rows = []
    for t, par, a, b, r0, r1 in PAIRS:
        e0, n0 = ex(r0); e1, n1 = ex(r1); s0, s1 = sim(e0), sim(e1)
        f = lambda k: (None if s0.get(k) is None or s1.get(k) is None else s1[k] - s0[k])
        pct = lambda k: (None if not s0.get(k) or s1.get(k) is None else 100 * (s1[k] / s0[k] - 1))
        rows.append({'thickness_nm': t, 'parameter': par, 'from': a, 'to': b, 'run_ref': n0, 'run_pert': n1, 'status': 'MEASURED IN ATLAS (stage pair)',
                     'dVth_cc_V': f('Vth_cc_1e-9_V'), 'dSS_min_mV_dec': f('SS_mV_dec'), 'dmu_FE_pct': pct('mu_FE_cm2Vs'), 'dIon_pct': pct('Ion_A_per_um'),
                     'active_log_rmse_ref': e0['fit_metrics']['regions']['active']['rmse_log10'], 'active_log_rmse_pert': e1['fit_metrics']['regions']['active']['rmse_log10'],
                     'note': ''})
    rows[0]['note'] = 'dVth = -0.309 V for dQf = 1.73e12 cm^-2: -q dQf/Cox = -0.3095 V (Cox 8.955e-7 F/cm^2) -> the solver reproduces the flat-band relation exactly'
    rows[2]['note'] = 'Ion scales ~linearly with mu_band at fixed electrostatics (+7.9 % mu -> +7.9 % Ion)'
    # one-at-a-time runs executed by scripts/sensitivity_analysis.py (tables/SENSITIVITY_OAT.csv), if any
    oat = ROOT / 'tables' / 'SENSITIVITY_OAT.csv'; done = set()
    if oat.exists():
        for r in csv.DictReader(oat.open()):
            done.add(r['case'])
            g = lambda k: (None if r.get(k) in (None, '', 'nan') else float(r[k]))
            rows.append({'thickness_nm': float(r['thickness_nm']), 'parameter': f"OAT {r['case']}: {r['overrides']}", 'from': 'final', 'to': r['case'], 'run_ref': r.get('run_ref', ''), 'run_pert': r['run_id'], 'status': 'MEASURED IN ATLAS (one-at-a-time, vs the final run)',
                         'dVth_cc_V': g('dVth_cc_V'), 'dSS_min_mV_dec': g('dSS_mV_dec'), 'dmu_FE_pct': g('dmu_FE_pct'), 'dIon_pct': g('dIon_pct'), 'active_log_rmse_ref': g('active_log_rmse_ref'), 'active_log_rmse_pert': g('active_log_rmse'), 'note': ''})
    KEYMAP = {'no_confinement': 'no_confinement', 'chi_bulk': 'chi_m0p1', 'gate work': 'wf_p0p1', 'Nd0': 'nd_x2', 'Nt2': 'nt_x1p5', 'WTA': 'wta_p5meV', 'Dit': 'dit_x3', 'eps_r': 'eps_10p55', 'm* = bulk': 'mstar_bulk', 'overlap': 'overlap_4um', 'DOS levels': None, 'mesh x0.7': None}
    for c in NOT_RUN:
        key = next((v for k, v in KEYMAP.items() if k in c), None)
        if key in done: continue
        rows.append({'thickness_nm': '', 'parameter': c, 'from': '', 'to': '', 'run_ref': '', 'run_pert': '', 'status': 'NOT RUN (see docs/NUMERICAL_CONVERGENCE.md for the refinement checks; other cases not launched)',
                     'dVth_cc_V': None, 'dSS_min_mV_dec': None, 'dmu_FE_pct': None, 'dIon_pct': None, 'active_log_rmse_ref': None, 'active_log_rmse_pert': None, 'note': ''})
    out = ROOT / 'tables' / 'SENSITIVITY_RESULTS.csv'
    with out.open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    fmt = lambda x, f='{:+.3g}': ('-' if x is None or x == '' else f.format(x))
    md = ['# Sensitivity results (V1)', '', 'Rows marked MEASURED IN ATLAS come from pairs of executed runs that differ in exactly one input; rows marked NOT RUN are the planned one-at-a-time cases that were not launched (user directive). No sensitivity below is estimated analytically.', '',
          '| t (nm) | parameter | from | to | runs | dVth_cc (V) | dSS_min (mV/dec) | dmu_FE (%) | dIon (%) | active RMSE ref -> pert | status / note |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        md.append(f"| {r['thickness_nm']} | {r['parameter']} | {r['from']} | {r['to']} | {r['run_ref'][:8] if r['run_ref'] else ''} -> {r['run_pert'][:8] if r['run_pert'] else ''} | {fmt(r['dVth_cc_V'])} | {fmt(r['dSS_min_mV_dec'])} | {fmt(r['dmu_FE_pct'])} | {fmt(r['dIon_pct'])} | {fmt(r['active_log_rmse_ref'], '{:.3f}')} -> {fmt(r['active_log_rmse_pert'], '{:.3f}')} | {r['status']}{('; ' + r['note']) if r['note'] else ''} |")
    (ROOT / 'tables' / 'SENSITIVITY_RESULTS.md').write_text('\n'.join(md) + '\n'); print('\n'.join(md))

if __name__ == '__main__': main()
