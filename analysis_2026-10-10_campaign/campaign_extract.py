#!/usr/bin/env python3
"""C12 (CAMPAIGN_DESIGN.md section 8): campaign wrapper around the REGISTERED extraction. NO simulator call; reads finished run
directories and data/experimental_clean.csv, never writes into results/ or data/. The registered files
(analysis_2026-10-06_extraction/PROTOCOL.md, extraction.py, run_extraction.py) are imported, never edited.

  python analysis_2026-10-10_campaign/campaign_extract.py RUN_DIR [RUN_DIR ...]          per-run extraction + campaign metrics
  python analysis_2026-10-10_campaign/campaign_extract.py compare RUN_DIR REF_DIR [--rule numerics|s1_05|s1_06]

Per run (transfer runs with a measured film 2.0 / 6.3 / 13.2 nm):
  - run_extraction.analyse() on the native terminal_currents.csv (I_D in A/um, no rescaling) with the measured floor; if it
    raises, every quantity is extracted separately and a failure is flagged {"invalid": reason} (guards);
  - V_th,cc at 1e-9 and 5e-10 A/um, SS in the registered window 5e-11..5e-10 A/um and in the A1 normalised window
    [r, 10 r] x I_on,MEASURED (r from the measured floors and I_on, amendment A1: 2.15e-5), mu_FE at 1.0..3.0 V, V_th,ELR,
    the power-law fit (V_T, mu0, gamma) and the off floor;
  - campaign metrics (CAMPAIGN_DESIGN 5.1): RMSE_sub (measured I_D in [10 x floor, 1e-9 A/um]), RMSE_on (V_G 1..3 V) of
    log10 I_D on the measured grid (PCHIP of log10 max(I, 1e-40) over the native grid, no extrapolation, coverage reported),
    the film's J term (RMSE_sub^2 + RMSE_on^2)/2, and signed errors in V_th,cc, I_D(3 V) and mu_FE(1.5 / 2 / 3 V);
  - S6 permittivity runs: mu_FE also with the run's own (perturbed) C_ox, next to the registered C_ox.
Labels: the STATUS labels of run_extraction.py (written for the per-film V1 calibration) are NOT inherited. CAMPAIGN_STATUS below
relabels every quantity for the shared-parameter campaign. A number from this wrapper is calibration output unless the film was
held out (S5), and is never called validation.
compare: differences RUN - REF used by the S1 rules (numerics 0.01 dec / 5 mV / 3 mV/dec; S1-05 +40..+70 mV; S1-06 1e-3 relative
above 1e-14 A/um) with a PASS/FAIL line for the requested rule.
Output: analysis_2026-10-10_campaign/extract/<run_id>.json (and compare_<run>_vs_<ref>.json); printed summary."""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

import campaign_tools as ct

EXDIR = ct.PKG / 'analysis_2026-10-06_extraction'
sys.path.insert(0, str(EXDIR))
import extraction as ex  # noqa: E402  (registered, unchanged)
import run_extraction as rx  # noqa: E402  (registered, unchanged; importing it runs nothing)

OUT = ct.HERE / 'extract'
FILMS = rx.FILMS
CAMPAIGN_STATUS = {
    'vth_cc': 'constrained by the shared whole-curve fit (one Q_f for all films); FITTED-parameter output, not a prediction',
    'ss': 'not fitted directly (shape; shared N_s, W_T)', 'mu_fe': 'not fitted directly (shape; shared mu law scale)',
    'pl': 'not fitted directly (power-law summary of the simulated curve)', 'rmse': 'objective term of the shared calibration',
    'held_out': 'S5 held-out film only: retrospective transferability, not validation'}
LOGEPS = 1e-40


def measured():
    meas = rx.load_measured(); info = {}
    for t in FILMS:
        vg, i = meas[t]; fl, sfl = rx.floor_with_sigma(vg, i)
        info[t] = dict(vg=vg, i=i, floor=fl, sig_floor=sfl, ion=float(i[-1]))
    r = 10 * max(info[t]['floor'] / info[t]['ion'] for t in FILMS)   # amendment A1 (amendment_a1.py windows('ion'))
    for t in FILMS: info[t]['a1_window'] = (r * info[t]['ion'], 10 * r * info[t]['ion'])
    return info, r


def resolve(run):
    p = Path(run); return p if p.is_absolute() else ct.PKG / p


def load_run(run):
    d = resolve(run); exj = json.loads((d / 'execution.json').read_text())
    with open(d / 'terminal_currents.csv', newline='') as f:
        a = np.array([(float(r['vg_V']), float(r['id_A_per_um'])) for r in csv.DictReader(f)])
    a = a[np.argsort(a[:, 0])]
    return d, exj, a[:, 0], a[:, 1]


def log_interp(vg, i, x):
    """PCHIP of log10 max(I, 1e-40) over the native grid, evaluated at x; NaN outside the solved range (no extrapolation)"""
    f = PchipInterpolator(vg, np.log10(np.maximum(i, LOGEPS)), extrapolate=False)
    y = f(np.asarray(x, float)); return np.where((x >= vg[0] - 1e-9) & (x <= vg[-1] + 1e-9), y, np.nan)


def window_rmse(vg_m, i_m, floor, vg, i):
    """CAMPAIGN_DESIGN 5.1 windows on the measured grid; returns per-window RMSE, coverage and the film's J term"""
    ls = log_interp(vg, i, vg_m); lm = np.log10(i_m)
    masks = {'sub': (i_m >= 10 * floor) & (i_m <= 1e-9), 'on': (vg_m >= 1 - 1e-9) & (vg_m <= 3 + 1e-9)}
    out = {}
    for k, msk in masks.items():
        cov = msk & np.isfinite(ls); n = int(msk.sum())
        out[k] = dict(points=n, covered=int(cov.sum()), coverage=(float(cov.sum()) / n if n else 0.0),
                      rmse_dec=(float(np.sqrt(np.mean((ls[cov] - lm[cov]) ** 2))) if cov.any() else None),
                      mean_signed_dec=(float(np.mean(ls[cov] - lm[cov])) if cov.any() else None))
    ok = out['sub']['rmse_dec'] is not None and out['on']['rmse_dec'] is not None
    out['J_term'] = (out['sub']['rmse_dec'] ** 2 + out['on']['rmse_dec'] ** 2) / 2 if ok else None
    out['coverage_ok_95pct'] = bool(min(out['sub']['coverage'], out['on']['coverage']) >= 0.95)
    return out


def guarded(fn, *a):
    try: return fn(*a)
    except Exception as e: return {'invalid': f'{type(e).__name__}: {e}'}


def analyse_guarded(vg, i, floor, sfl, vg_fit, i_fit):
    """run_extraction.analyse() first; on an exception, the same registered functions one by one with explicit invalid flags"""
    try:
        r = rx.analyse(vg, i, True, floor, sfl, vg_fit, i_fit); r['guard'] = 'analyse() completed'; return r
    except Exception as e:
        r = {'guard': f'analyse() raised {type(e).__name__}: {e}; quantities extracted separately'}
    r['vth_cc'] = guarded(ex.crossing, vg, i, rx.I_CC, True); r['vth_cc_10nA'] = guarded(ex.crossing, vg, i, rx.I_CC10, True)
    r['ss'] = guarded(rx.ss_rule, vg, i, *rx.WIN, True, floor, sfl)
    g = ex.gm(vg, i); mu = ex.MU_FACTOR * g
    r['mu_fe'] = {f'{v:.1f}': ({'mu_fe': float(mu[k])} if abs(vg[k] - v) < 1e-6 else {'invalid': f'no native point at {v} V'})
                  for v in rx.VG_REPORT for k in [int(np.argmin(abs(vg - v)))]}
    r['pl'] = guarded(ex.pl_fit, vg_fit, i_fit, *rx.FIT_PRIMARY)
    return r


def val(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d: return None
        d = d[k]
    return d


def extract(run, info=None):
    if info is None: info, _ = measured()
    d, exj, vg, i = load_run(run); t = float(exj['thickness_nm'])
    res = {'run_id': exj['run_id'], 'run_dir': str(d.relative_to(ct.PKG)).replace('\\', '/'), 'thickness_nm': t, 'status_runner': exj.get('status'),
           'labels': CAMPAIGN_STATUS}
    if t not in FILMS: res['invalid'] = f'no measured film {t} nm (31.8 nm stress / predictions: whole-curve metrics only)'; return res
    M = info[t]; vg_m, i_m = M['vg'], M['i']
    cmp = d / 'comparison.csv'
    if cmp.exists():
        with open(cmp, newline='') as f: c = np.array([(float(r['vg_V']), float(r['atlas_A_per_um'])) for r in csv.DictReader(f)])
        vg_fit, i_fit = c[:, 0], c[:, 1]
    else:
        vg_fit = vg_m[(vg_m >= vg[0]) & (vg_m <= vg[-1])]; i_fit = np.interp(vg_fit, vg, i)
    s = analyse_guarded(vg, i, M['floor'], M['sig_floor'], vg_fit, i_fit)
    a1 = guarded(ex.ss_window, vg, i, *M['a1_window'], True)
    res['extraction'] = {'vth_cc_V': val(s, 'vth_cc', 'v'), 'vth_cc_sig_V': val(s, 'vth_cc', 'sig'), 'vth_cc_5e-10_V': val(s, 'vth_cc_10nA', 'v'),
                         'ss_fixed_mV_dec': val(s, 'ss', 'ss'), 'ss_fixed_window_A_per_um': list(rx.WIN), 'ss_a1_mV_dec': val(a1, 'ss'),
                         'ss_a1_window_A_per_um': list(M['a1_window']), 'mu_fe': {k: v.get('mu_fe', v) for k, v in (s.get('mu_fe') or {}).items()},
                         'vth_elr_V': val(s, 'elr', 'v'), 'pl_vt_V': val(s, 'pl', 'vt'), 'pl_mu0': val(s, 'pl', 'mu0'), 'pl_gamma': val(s, 'pl', 'gamma'),
                         'off_floor_sim_A_per_um': float(ex.off_floor(vg, i)), 'guard': s.get('guard'),
                         'invalid': {k: v['invalid'] for k, v in s.items() if isinstance(v, dict) and 'invalid' in v}}
    # measured reference values from the same registered functions on the measured curve
    mvc =ex.crossing(vg_m, i_m, rx.I_CC, False)['v']; mg = ex.MU_FACTOR * ex.gm(vg_m, i_m)
    mu_m = {f'{v:.1f}': float(mg[int(np.argmin(abs(vg_m - v)))]) for v in (1.5, 2.0, 3.0)}
    w = window_rmse(vg_m, i_m, M['floor'], vg, i)
    e = res['extraction']
    res['campaign_metrics'] = {'rmse_sub_dec': w['sub']['rmse_dec'], 'rmse_on_dec': w['on']['rmse_dec'], 'J_term': w['J_term'], 'windows': w,
                               'dVth_cc_V': (e['vth_cc_V'] - mvc) if e['vth_cc_V'] is not None else None,
                               'Id3V_err_pct': float(100 * (i[np.argmin(abs(vg - 3.0))] / i_m[-1] - 1)),
                               'mu_fe_err_pct': {k: (100 * (e['mu_fe'][k] / mu_m[k] - 1) if isinstance(e['mu_fe'].get(k), float) else None) for k in mu_m},
                               'measured_reference': {'vth_cc_V': mvc, 'mu_fe': mu_m, 'floor_A_per_um': M['floor'], 'ion_A_per_um': M['ion']}}
    # S6 permittivity runs: mu_FE with the run's own C_ox as well (the registered C_ox stays the comparable number)
    geo = [o for o in exj.get('overrides', []) if o.startswith('geometry.')]
    if geo:
        _, g, _ = ct.configs(ct.V3, geo); cox_run = ct.bd.cox(g)
        if abs(cox_run / ex.COX - 1) > 1e-9:
            res['extraction']['mu_fe_run_cox'] = {k: (v * ex.COX / cox_run if isinstance(v, float) else v) for k, v in e['mu_fe'].items()}
            res['extraction']['cox_run_F_cm2'] = cox_run
    return res


def compare(run, ref, rule=None):
    info, _ = measured(); a, b = extract(run, info), extract(ref, info)
    _, _, vg, i = load_run(run); _, _, vgr, ir = load_run(ref)
    common = np.intersect1d(np.round(vg, 6), np.round(vgr, 6))
    ia = np.array([i[np.argmin(abs(vg - v))] for v in common]); ib = np.array([ir[np.argmin(abs(vgr - v))] for v in common])
    big = (np.abs(ia) > 1e-14) & (np.abs(ib) > 1e-14)
    ea, eb = a.get('extraction', {}), b.get('extraction', {}); ca, cb = a.get('campaign_metrics', {}), b.get('campaign_metrics', {})
    def dif(x, y): return (x - y) if (x is not None and y is not None) else None
    d = {'run': a['run_id'], 'ref': b['run_id'], 'thickness_nm': a['thickness_nm'],
         'dVth_cc_mV': (1e3 * dif(ea.get('vth_cc_V'), eb.get('vth_cc_V'))) if dif(ea.get('vth_cc_V'), eb.get('vth_cc_V')) is not None else None,
         'dSS_fixed_mV_dec': dif(ea.get('ss_fixed_mV_dec'), eb.get('ss_fixed_mV_dec')), 'dSS_a1_mV_dec': dif(ea.get('ss_a1_mV_dec'), eb.get('ss_a1_mV_dec')),
         'd_rmse_sub_dec': dif(ca.get('rmse_sub_dec'), cb.get('rmse_sub_dec')), 'd_rmse_on_dec': dif(ca.get('rmse_on_dec'), cb.get('rmse_on_dec')),
         'max_abs_dlog10_I_above_1e-14_dec': float(np.max(np.abs(np.log10(ia[big]) - np.log10(ib[big])))) if big.any() else None,
         'max_rel_dI_above_1e-14': float(np.max(np.abs(ia[big] / ib[big] - 1))) if big.any() else None, 'common_points': int(len(common))}
    # active-RMSE change: the runner's own active-region RMSE (execution.json fit_metrics), as written by run_atlas.score
    fa = json.loads((resolve(run) / 'execution.json').read_text()).get('fit_metrics', {}); fb = json.loads((resolve(ref) / 'execution.json').read_text()).get('fit_metrics', {})
    d['d_active_rmse_dec'] = dif(val(fa, 'regions', 'active', 'rmse_log10'), val(fb, 'regions', 'active', 'rmse_log10'))
    if rule == 'numerics':
        checks = [d['d_active_rmse_dec'], d['dVth_cc_mV'], d['dSS_fixed_mV_dec'], d['dSS_a1_mV_dec']]
        if any(x is None for x in checks): d['verdict'] = 'UNVERIFIED (a quantity could not be extracted)'
        else: d['verdict'] = 'PASS' if (abs(checks[0]) <= 0.01 and abs(checks[1]) <= 5 and abs(checks[2]) <= 3 and abs(checks[3]) <= 3) else 'FAIL (adopt the refined setting, S1 rule)'
        d['rule'] = '|d active RMSE| <= 0.01 dec, |dV_th,cc| <= 5 mV, |dSS| <= 3 mV/dec (fixed and A1 windows)'
    elif rule == 's1_05':
        x = d['dVth_cc_mV']; d['rule'] = 'S1-05 (3-D NC) minus S0-01: dV_th,cc in +40..+70 mV'
        d['verdict'] = 'UNVERIFIED' if x is None else ('PASS' if 40 <= x <= 70 else 'FAIL (audit the NC override before S3)')
    elif rule == 's1_06':
        x = d['max_rel_dI_above_1e-14']; d['rule'] = 'S1-06 (two carriers) vs S1-02: |dI/I| <= 1e-3 wherever both |I| > 1e-14 A/um'
        d['verdict'] = 'UNVERIFIED' if x is None else ('PASS' if x <= 1e-3 else 'FAIL (drop the electron-only assumption)')
    return d


def main(argv):
    if not argv: print(__doc__); return 2
    OUT.mkdir(exist_ok=True)
    if argv[0] == 'compare':
        rule = argv[argv.index('--rule') + 1] if '--rule' in argv else None
        d = compare(argv[1], argv[2], rule); (OUT / f'compare_{d["run"]}_vs_{d["ref"]}.json').write_text(json.dumps(d, indent=1, default=float))
        print(json.dumps(d, indent=1, default=float)); return 0 if not str(d.get('verdict', 'PASS')).startswith(('FAIL', 'UNVERIFIED')) else 1
    info, r = measured(); print(f'A1 normalisation r = {r:.4g} (amendment A1: 2.15e-5)')
    for run in argv:
        res = extract(run, info); (OUT / f'{res["run_id"]}.json').write_text(json.dumps(res, indent=1, default=float))
        e, c = res.get('extraction', {}), res.get('campaign_metrics', {})
        print(json.dumps({'run_id': res['run_id'], 't': res['thickness_nm'], 'vth_cc_V': e.get('vth_cc_V'), 'dVth_cc_V': c.get('dVth_cc_V'),
                          'ss_fixed': e.get('ss_fixed_mV_dec'), 'ss_a1': e.get('ss_a1_mV_dec'), 'rmse_sub': c.get('rmse_sub_dec'), 'rmse_on': c.get('rmse_on_dec'),
                          'J_term': c.get('J_term'), 'coverage_ok': (c.get('windows') or {}).get('coverage_ok_95pct'), 'Id3V_err_pct': c.get('Id3V_err_pct'),
                          'invalid': e.get('invalid') or res.get('invalid')}, default=float))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
