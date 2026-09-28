"""S6 part 1: numerical closure (linearity, DOS offsets vs Vg and thickness, 6.3/13.2 nm mesh, KCL, native zeros,
SS_min fragility, interpolation and gm-grid uncertainty). Reads only existing run outputs."""
import json, math
import numpy as np
from s6_lib import *

out = {}
P = lambda *a: print(*a)

# ---------- 1. exact linearity of Id in mu_band (same DOS, same deck otherwise) ----------
P('=== 1. Linearity of Id in mu_band ===')
for a, b, mua, mub, lab in [('run_0038', 'run_0029', 17.69, 18.13, '2 nm DOS 384/192 (B1 vs check C)'),
                            ('run_0003', 'run_0008', 16.8, 18.13, '2 nm DOS 96/48 reduced deck (stage pair)')]:
    va, ia = read_idvg(a); vb, ib = read_idvg(b)
    common = np.intersect1d(va, vb); ia2 = np.array([ia[va == v][0] for v in common]); ib2 = np.array([ib[vb == v][0] for v in common])
    msk = ia2 > 1e-14; r = ib2[msk] / ia2[msk]
    exp_r = mub / mua
    P(f'{lab}: {b}/{a} expected {exp_r:.6f}; observed mean {r.mean():.6f}, min {r.min():.6f}, max {r.max():.6f} over {msk.sum()} pts with Id>1e-14 (Vg {common[msk][0]}..{common[msk][-1]})')
    out[f'linearity_{a}_{b}'] = dict(expected=exp_r, mean=float(r.mean()), min=float(r.min()), max=float(r.max()), n=int(msk.sum()))

# ---------- 2. DOS discretization offsets vs Vg ----------
P('\n=== 2. DOS 96/48 -> 384/192 offset (same mu after exact rescale) ===')
cases = [('2.0', 'run_0012', 'run_0029', 1.0, '96/48 -> 384/192 (both mu 18.13)'),
         ('2.0', 'run_0012', 'run_0019', 1.0, '96/48 -> 192/96 (both mu 18.13)'),
         ('6.3', 'run_0015', 'run_0039', 11.69 / 11.41, 'run_0015 (mu 11.69, 96/48) vs B2 (mu 11.41, 384/192) x 11.69/11.41'),
         ('13.2', 'run_0013', 'run_0040', 61.9 / 60.39, 'run_0013 (mu 61.9, 96/48) vs B3 (mu 60.39, 384/192) x 61.9/60.39')]
dos = {}
for t, a, b, sc, lab in cases:
    va, ia = read_idvg(a); vb, ib = read_idvg(b); ib = ib * sc
    rows = []
    for v in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5, 3.0]:
        x, y = ia[va == v][0], ib[vb == v][0]; rows.append((v, y / x - 1))
    ta = float(t); ra = robust(va, ia); rb = robust(vb, ib)
    la = legacy(va, ia, ta); lb = legacy(vb, ib, ta)
    d = dict(dIon_pct=100 * (ib[-1] / ia[-1] - 1), dVcc_mV=1000 * (rb['V_1e-9'] - ra['V_1e-9']), dSS_10_9=rb['SS_10_9'] - ra['SS_10_9'], dSS_11_10=rb['SS_11_10'] - ra['SS_11_10'],
             dSS_10_8=rb['SS_10_8'] - ra['SS_10_8'], dVlin_mV=1000 * (lb['Vth_lin_V'] - la['Vth_lin_V']), dgm_pct=100 * (lb['gm_max_A_V_um'] / la['gm_max_A_V_um'] - 1), dgap7_mV=1000 * (rb['gap7'] - ra['gap7']))
    dos[f'{t}_{a}_{b}'] = d
    P(f'{t} nm {lab}:')
    P('   dId/Id (%) at Vg: ' + ', '.join(f'{v:g}: {100*r:+.2f}' for v, r in rows))
    P('   ' + ', '.join(f'{k} {v:+.2f}' for k, v in d.items()))
out['dos'] = dos
# Richardson-type estimate of the residual beyond 384/192 at 2 nm (96->192->384)
va, i96 = read_idvg('run_0012'); _, i192 = read_idvg('run_0019'); _, i384 = read_idvg('run_0029')
e1 = i192[-1] / i96[-1] - 1; e2 = i384[-1] / i192[-1] - 1; p = math.log(e1 / e2, 2); resid = e2 / (2 ** p - 1)
P(f'\n2 nm Ion: 96->192 {100*e1:+.3f} %, 192->384 {100*e2:+.3f} %, observed order p = {p:.2f}; Richardson residual beyond 384/192 = {100*resid:+.3f} %')
out['richardson_2nm'] = dict(e96_192=e1, e192_384=e2, order=p, residual=resid)
for v in [0.7, 1.0, 1.5, 2.0]:
    a, b, c = i96[va == v][0], i192[va == v][0], i384[va == v][0]
    e1v, e2v = b / a - 1, c / b - 1
    P(f'   Vg {v}: 96->192 {100*e1v:+.3f} %, 192->384 {100*e2v:+.3f} %')

# ---------- 3. mesh checks ----------
P('\n=== 3. Mesh x0.7 ===')
for t, a, b in [('6.3', 'run_0015', 'run_0036'), ('13.2', 'run_0013', 'run_0028')]:
    va, ia = read_idvg(a); vb, ib = read_idvg(b); ta = float(t)
    fl = floor_med(ta); msk = (ia > 5 * fl) & (ib > 5 * fl)
    dl = np.abs(np.log10(ib[msk]) - np.log10(ia[msk]))
    ra, rb = robust(va, ia), robust(vb, ib); la, lb = legacy(va, ia, ta), legacy(vb, ib, ta)
    d = dict(max_dlog=float(dl.max()), rms_dlog=float(np.sqrt((dl ** 2).mean())), dVcc_mV=1000 * (rb['V_1e-9'] - ra['V_1e-9']), dSS_11_10=rb['SS_11_10'] - ra['SS_11_10'], dSS_10_9=rb['SS_10_9'] - ra['SS_10_9'],
             dSS_10_8=rb['SS_10_8'] - ra['SS_10_8'], dVlin_mV=1000 * (lb['Vth_lin_V'] - la['Vth_lin_V']), dgm_pct=100 * (lb['gm_max_A_V_um'] / la['gm_max_A_V_um'] - 1), dIon_pct=100 * (ib[-1] / ia[-1] - 1), dSSmin=lb['SS_mV_dec'] - la['SS_mV_dec'])
    out[f'mesh_{t}'] = d
    P(f'{t} nm {b} vs {a}: ' + ', '.join(f'{k} {v:+.4f}' for k, v in d.items()))

# ---------- 4. KCL and native zeros ----------
P('\n=== 4. KCL and native zeros (runs 0012-0052 with idvg.dat) ===')
kcl = []
for n in range(12, 53):
    rid = f'run_{n:04d}'
    try: d = run_dir(rid)
    except FileNotFoundError: continue
    if not (d / 'execution.json').exists(): continue
    ex = read_exec(rid); v = ex.get('validation', {})
    rec = dict(run=rid, max_kcl=v.get('max_kcl_abs_A'), limit=v.get('kcl_abs_limit_applied_A'), fails=v.get('kcl_fail_count'))
    if (d / 'idvg.dat').exists():
        vg, i = read_idvg(rid); npz = i <= 0
        rec.update(nonpos=int(npz.sum()), vg_max_nonpos=float(vg[npz].max()) if npz.any() else None,
                   max_abs_below=float(np.abs(i[vg <= (vg[npz].max() if npz.any() else -9)]).max()) if npz.any() else None,
                   first_vg_above_1e15=float(vg[np.argmax(i > 1e-15)]))
    kcl.append(rec)
for r in kcl: P(r)
out['kcl'] = kcl
tr = [r for r in kcl if r.get('nonpos') is not None]
P('max KCL over transfer runs: %.3g A; max |Id| at or below the highest-Vg native zero: %.3g A/um; highest Vg of a native zero: %.2f V' % (
    max(r['max_kcl'] for r in tr), max(r['max_abs_below'] for r in tr if r['max_abs_below'] is not None), max(r['vg_max_nonpos'] for r in tr if r['vg_max_nonpos'] is not None)))

# ---------- 5. SS_min fragility ----------
P('\n=== 5. SS_min window phase: run_0012 vs B1 (run_0038), run_0003 vs run_0008 ===')
for t, runs in [(2.0, ['run_0012', 'run_0038', 'run_0029', 'run_0019', 'run_0016', 'run_0003', 'run_0008']), (13.2, ['run_0013', 'run_0040', 'run_0017', 'run_0028'])]:
    fl = floor_med(t); thr = 5 * fl
    for rid in runs:
        vg, i = read_idvg(rid); m = legacy(vg, i, t); r = robust(vg, i)
        first = vg[np.argmax(i > thr)]
        P(f'{t} nm {rid}: 5x floor {thr:.3g}; first native point above = {first:.2f} V (Id {i[vg==first][0]:.3g}; previous point {i[vg==round(first-0.05,2)][0]:.3g}); SS_min {m["SS_mV_dec"]:.1f}; SS_11_10 {fmt(r["SS_11_10"],"{:.1f}")}; SS_10_9 {r["SS_10_9"]:.1f}; SS_cc {r["SS_10_8"]:.1f}')

# ---------- 6. interpolation uncertainty (log-linear vs PCHIP) ----------
P('\n=== 6. Crossing interpolation: log-linear minus PCHIP (mV) ===')
interp = {}
for lab, t, src in [('meas', 2.0, None), ('meas', 6.3, None), ('meas', 13.2, None), ('B1', 2.0, 'run_0038'), ('B2', 6.3, 'run_0039'), ('B3', 13.2, 'run_0040'), ('C1', 6.3, 'run_0052')]:
    vg, i = meas(t) if src is None else read_idvg(src); r = robust(vg, i)
    d = {k: 1000 * (r[k] - r[k + '_pchip']) for k in ['V_1e-11', 'V_1e-10', 'V_1e-9', 'V_1e-8', 'V_1e-7'] if r[k] is not None and r[k + '_pchip'] is not None}
    dss = {k: r[k] - r[k + '_pchip'] for k in ['SS_11_10', 'SS_10_9', 'SS_10_8'] if r[k] is not None and r[k + '_pchip'] is not None}
    interp[f'{lab}_{t}'] = dict(dV_mV=d, dSS=dss)
    P(f'{lab} {t}: ' + ', '.join(f'{k} {v:+.2f}' for k, v in d.items()) + ' | ' + ', '.join(f'{k} {v:+.2f}' for k, v in dss.items()))
out['interp'] = interp

# ---------- 7. gm grid effect: measured curve re-sampled as the simulation grid, then np.interp back ----------
P('\n=== 7. gm_max / Vth_lin grid effect (measured curves passed through the simulation grid) ===')
vg_sim, _ = read_idvg('run_0038')
gridfx = {}
for t in [2.0, 6.3, 13.2]:
    vg, i = meas(t); base = pkg_metrics(vg, i, False, t)
    sub = np.array([i[np.argmin(np.abs(vg - v))] for v in vg_sim]); back = np.interp(vg, vg_sim, sub)
    m2 = pkg_metrics(vg, back, False, t)
    gridfx[t] = dict(dgm_pct=100 * (m2['gm_max_A_V_um'] / base['gm_max_A_V_um'] - 1), dVlin_mV=1000 * (m2['Vth_lin_V'] - base['Vth_lin_V']), dVcc_mV=1000 * (m2['Vth_cc_1e-9_V'] - base['Vth_cc_1e-9_V']))
    P(f'{t} nm: gm_max {100*(m2["gm_max_A_V_um"]/base["gm_max_A_V_um"]-1):+.2f} %, Vth_lin {1000*(m2["Vth_lin_V"]-base["Vth_lin_V"]):+.1f} mV, Vth_cc {1000*(m2["Vth_cc_1e-9_V"]-base["Vth_cc_1e-9_V"]):+.2f} mV')
out['gm_grid'] = gridfx

# ---------- 8. ID-VD vs transfer consistency at Vd = 0.7 V ----------
P('\n=== 8. Path independence: ID-VD (Vd = 0.7 V) vs transfer curve at the same Vg, same mu ===')
import csv as _csv
path = {}
for t, rt, ro, sc in [(2.0, 'run_0038', 'run_0041', 17.6897 / 17.69), (6.3, 'run_0039', 'run_0042', 11.582 / 11.41), (13.2, 'run_0040', 'run_0043', 61.6046 / 60.39)]:
    vg, i = read_idvg(rt); i = i * sc
    rows = list(_csv.DictReader((run_dir(ro) / 'output_characteristics.csv').open()))
    diffs = []
    for vgv in [1.0, 1.5, 2.0, 2.5, 3.0]:
        idd = [float(r['id_A_per_um']) for r in rows if abs(float(r['vg_V']) - vgv) < 1e-9 and abs(float(r['vd_V']) - 0.7) < 1e-9][0]
        itr = i[np.argmin(np.abs(vg - vgv))]; diffs.append(100 * (idd / itr - 1))
    path[t] = diffs
    P(f'{t} nm {ro} vs {rt} x{sc:.6f}: dId % at Vg 1/1.5/2/2.5/3 = ' + ', '.join(f'{d:+.3f}' for d in diffs))
out['path'] = path

json.dump(out, open(Path(__file__).with_name('s6_part1_out.json'), 'w'), indent=1, default=float)
