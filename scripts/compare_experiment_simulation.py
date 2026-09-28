#!/usr/bin/env python3
"""Build tables/EXPERIMENTAL_VS_SIMULATION.{csv,md} and the per-thickness overlay/residual plots from the
best V1 runs listed in results/BEST_RUNS_V1.json (no simulator call). Same extraction algorithm
(scripts/extract_metrics.py) for measured and simulated curves.
"""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_metrics import metrics
ROOT = Path(__file__).resolve().parents[1]

def pct(a, b):
    return None if (a is None or b is None or a == 0) else 100.0 * (b / a - 1.0)

def main():
    best = json.loads((ROOT / 'results' / 'BEST_RUNS_V1.json').read_text())
    rows = []; md = ['# Experimental vs simulation (V1 best verified runs)', '', 'Same extractor for both curves (scripts/extract_metrics.py): Vth = constant current 1e-9 A/um (log interpolation); SS = steepest 0.2 V window with Id above 5x the MEASURED off floor of that thickness and below 1 % of Ion, applied to both curves so the same current range is evaluated (SS_cc, the average slope between the 1e-10 and 1e-8 A/um crossings, is in the CSV); mu_FE = gm_max L/(W Cox Vd) at Vd = 0.7 V; Ion = Id(+3 V); Ioff = min Id (simulation: min POSITIVE Id, native zeros counted). Currents in A/um. Vth differences are absolute (no % for sign-changing quantities).', '',
          '| t (nm) | run | Vth_exp (V) | Vth_sim (V) | dVth (V) | SS_exp | SS_sim (mV/dec) | mu_exp | mu_sim (cm^2/Vs) | Ion_exp | Ion_sim | dIon % | Ioff_exp | Ioff_sim (min pos.) | zeros | Ion/Ioff exp | Ion/Ioff sim | active log RMSE | notes |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    keys = [k for k in ['2p0', '6p3', '13p2', '31p8'] if k in best] + [k for k, v in best.items() if isinstance(v, dict) and 'directory' in v and k not in ('2p0', '6p3', '13p2', '31p8')]
    for key in keys:
        b = best[key]; d = ROOT / b['directory']; t = float(b.get('thickness_nm', key.replace('p', '.')))
        cr = list(csv.DictReader((d / 'comparison.csv').open())); vg = np.array([float(r['vg_V']) for r in cr]); me = np.array([float(r['measured_A_per_um']) for r in cr]); si = np.array([float(r['atlas_A_per_um']) for r in cr])
        ex = json.loads((d / 'execution.json').read_text()); fm = ex['fit_metrics']
        E = metrics(vg, me, False, t); S = metrics(vg, si, True, t)
        r = {'thickness_nm': t, 'run_id': b['run_id'], 'VDS_V': 0.7, 'Vth_exp_V': E['Vth_cc_1e-9_V'], 'Vth_sim_V': S['Vth_cc_1e-9_V'], 'Vth_error_V': (None if None in (E['Vth_cc_1e-9_V'], S['Vth_cc_1e-9_V']) else S['Vth_cc_1e-9_V'] - E['Vth_cc_1e-9_V']),
             'SS_exp_mV_dec': E['SS_mV_dec'], 'SS_sim_mV_dec': S['SS_mV_dec'], 'SS_error_pct': pct(E['SS_mV_dec'], S['SS_mV_dec']), 'SScc_exp_mV_dec': E['SS_cc_1e-10_1e-8_mV_dec'], 'SScc_sim_mV_dec': S['SS_cc_1e-10_1e-8_mV_dec'], 'mu_exp_cm2Vs': E['mu_FE_cm2Vs'], 'mu_sim_cm2Vs': S['mu_FE_cm2Vs'], 'mu_error_pct': pct(E['mu_FE_cm2Vs'], S['mu_FE_cm2Vs']),
             'Ion_exp_A_per_um': E['Ion_A_per_um'], 'Ion_sim_A_per_um': S['Ion_A_per_um'], 'Ion_error_pct': pct(E['Ion_A_per_um'], S['Ion_A_per_um']), 'Ioff_exp_A_per_um': E['Ioff_A_per_um'], 'Ioff_sim_minpos_A_per_um': S['Ioff_A_per_um'], 'sim_native_zero_count': S['native_zero_count'],
             'Ioff_error_pct': (pct(E['Ioff_A_per_um'], S['Ioff_A_per_um']) if S['native_zero_count'] == 0 else None), 'IonIoff_exp': E['Ion_over_Ioff'], 'IonIoff_sim': S['Ion_over_Ioff'], 'IonIoff_ratio_error': (None if S['native_zero_count'] else pct(E['Ion_over_Ioff'], S['Ion_over_Ioff'])),
             'log_RMSE_active': fm['regions']['active']['rmse_log10'], 'log_RMSE_all_positive': fm['regions']['all']['rmse_log10'], 'linear_RMSE_active_A_per_um': fm['regions']['active']['rmse_linear_A_per_um'], 'max_abs_log_active': fm['max_abs_log10_active'], 'notes': b.get('note', '')}
        rows.append(r)
        fmt = lambda x, f='{:.3g}': ('-' if x is None else f.format(x))
        md.append(f"| {t} | {b['run_id']} | {fmt(r['Vth_exp_V'], '{:.2f}')} | {fmt(r['Vth_sim_V'], '{:.2f}')} | {fmt(r['Vth_error_V'], '{:+.2f}')} | {fmt(r['SS_exp_mV_dec'], '{:.0f}')} | {fmt(r['SS_sim_mV_dec'], '{:.0f}')} | {fmt(r['mu_exp_cm2Vs'], '{:.1f}')} | {fmt(r['mu_sim_cm2Vs'], '{:.1f}')} | {fmt(r['Ion_exp_A_per_um'], '{:.2e}')} | {fmt(r['Ion_sim_A_per_um'], '{:.2e}')} | {fmt(r['Ion_error_pct'], '{:+.1f}')} | {fmt(r['Ioff_exp_A_per_um'], '{:.1e}')} | {fmt(r['Ioff_sim_minpos_A_per_um'], '{:.1e}')} | {S['native_zero_count']} | {fmt(r['IonIoff_exp'], '{:.1e}')} | {fmt(r['IonIoff_sim'], '{:.1e}')}{' (>)' if S['native_zero_count'] else ''} | {r['log_RMSE_active']:.3f} | {r['notes']} |")
    with (ROOT / 'tables' / 'EXPERIMENTAL_VS_SIMULATION.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    md += ['', 'Ioff_sim is the minimum positive simulated current; where native zeros exist the simulated Ion/Ioff is a lower bound and no percentage error is reported. The measured off-state floors are not modelled (docs/LIMITATIONS.md).']
    (ROOT / 'tables' / 'EXPERIMENTAL_VS_SIMULATION.md').write_text('\n'.join(md) + '\n'); print('\n'.join(md))

if __name__ == '__main__': main()
