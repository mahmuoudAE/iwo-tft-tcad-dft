"""S6 part 2: robust-metric tables (final converged comparison, isolation tests B4-B7 with rigid-shift test, 6.3 nm
hypothesis closure A1-A7, B0, C1). Rescaling by exact linearity in mu_band (verified in part 1 to 1e-5)."""
import json
import numpy as np
from s6_lib import *

MU = {2.0: 17.6896871948524, 6.3: 11.581986680320135, 13.2: 61.60456093550155}
KEYS = ['V_1e-9', 'SS_11_10', 'SS_10_9', 'SS_10_8', 'SS_mV_dec', 'Vth_lin_V', 'gap_lin', 'V_1e-7', 'gap7', 'gm_max_A_V_um', 'mu_FE_cm2Vs', 'Ion_A_per_um', 'Ion_over_gm_V']
res = {}

def row(lab, m):
    return (f"| {lab} | {fmt(m['V_1e-9'])} | {fmt(m['SS_11_10'],'{:.1f}')} | {fmt(m['SS_10_9'],'{:.1f}')} | {fmt(m['SS_10_8'],'{:.1f}')} | {fmt(m['SS_mV_dec'],'{:.1f}')} | "
            f"{fmt(m['Vth_lin_V'])} | {fmt(m['gap_lin'])} | {fmt(m['V_1e-7'])} | {fmt(m['gap7'])} | {m['gm_max_A_V_um']:.4g} | {m['mu_FE_cm2Vs']:.2f} | {m['Ion_A_per_um']:.4g} | {m['Ion_over_gm_V']:.3f} |")
HDR = ('| curve | Vth_cc 1e-9 (V) | SS 1e-11..1e-10 | SS 1e-10..1e-9 | SS 1e-10..1e-8 (SS_cc) | SS_min (fragile) | Vth_lin (V) | gap Vlin-Vcc (V) | V(1e-7) (V) | V(1e-7)-Vcc (V) | gm_max (A/V/um) | mu_FE | Ion (A/um) | Ion/gm (V) |\n'
       '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')

print('=== A. Final converged comparison (DOS 384/192, recalibrated mu; exact linear rescale) ===')
print(HDR)
final = {}
for t, rid, mu_run in [(2.0, 'run_0038', 17.69), (6.3, 'run_0039', 11.41), (13.2, 'run_0040', 60.39)]:
    vg, i = meas(t); me = all_metrics(vg, i, t, False); final[f'meas_{t}'] = me; print(row(f'measured {t} nm', me))
    if t == 13.2:
        fl = floor_med(t); ms = all_metrics(vg, i, t, False, floor_sub=fl); final[f'meas_{t}_floorsub'] = ms
        print(row(f'measured {t} nm, floor {fl:.2g} subtracted (fixed-current markers only)', ms))
    vg, i = read_idvg(rid); sc = MU[t] / mu_run; m = all_metrics(vg, i * sc, t); final[f'final_{t}'] = m; final[f'final_{t}_scale'] = sc
    print(row(f'{rid} x{sc:.5f} (mu {MU[t]:.3f})', m))
    old = {2.0: 'run_0012', 6.3: 'run_0015', 13.2: 'run_0013'}[t]; vg, i = read_idvg(old); mo = all_metrics(vg, i, t); final[f'old_{t}'] = mo
    print(row(f'{old} (DOS 96/48, reference)', mo))
res['final'] = final
print('\nSim - measured (final converged):')
for t in [2.0, 6.3, 13.2]:
    s, e = final[f'final_{t}'], final[f'meas_{t}']
    d = {k: (s[k] - e[k]) if (s[k] is not None and e[k] is not None) else None for k in ['V_1e-9', 'SS_11_10', 'SS_10_9', 'SS_10_8', 'Vth_lin_V', 'gap_lin', 'V_1e-7', 'gap7']}
    d['gm_pct'] = 100 * (s['gm_max_A_V_um'] / e['gm_max_A_V_um'] - 1); d['Ion_pct'] = 100 * (s['Ion_A_per_um'] / e['Ion_A_per_um'] - 1)
    print(t, {k: (None if v is None else round(v, 4)) for k, v in d.items()})
    res[f'diff_{t}'] = d
for k in ['SS_11_10', 'SS_10_9', 'SS_10_8']:
    s, e = final['final_13.2'][k], final['meas_13.2_floorsub'][k]
    print(f'13.2 nm {k}: sim {s:.1f} vs floor-subtracted measured {fmt(e, "{:.1f}")}')

print('\n=== B. Isolation tests (DOS 384/192, same mu as baseline) ===')
print(HDR)
iso = {}
for lab, t, base, pert in [('WF +0.1 eV', 2.0, 'run_0038', 'run_0048'), ('WF +0.1 eV', 13.2, 'run_0040', 'run_0049'), ('m* x1.3', 2.0, 'run_0038', 'run_0050'), ('m* x1.3', 13.2, 'run_0040', 'run_0051'),
                           ('chi -0.1 eV (DOS 96/48)', 2.0, 'run_0012', 'run_0020'), ('chi +0.1 eV (DOS 96/48)', 2.0, 'run_0012', 'run_0021')]:
    vb, ib = read_idvg(base); vp, ip = read_idvg(pert); mb = all_metrics(vb, ib, t); mp = all_metrics(vp, ip, t)
    print(row(f'{base} base {t}', mb)); print(row(f'{pert} {lab}', mp))
    d = {k: (mp[k] - mb[k]) for k in ['V_1e-9', 'SS_11_10', 'SS_10_9', 'SS_10_8', 'Vth_lin_V', 'gap_lin', 'gap7']}
    d['Ion_pct'] = 100 * (mp['Ion_A_per_um'] / mb['Ion_A_per_um'] - 1); d['gm_pct'] = 100 * (mp['gm_max_A_V_um'] / mb['gm_max_A_V_um'] - 1)
    # rigid-shift test: best shift s (multiple of 0.05 V) such that Ip(Vg) = Ib(Vg - s) on common grid points
    best = None
    for s in np.round(np.arange(-0.3, 0.301, 0.05), 3):
        pts = [(v, ip[k]) for k, v in enumerate(vp) if np.any(np.abs(vb - (v - s)) < 1e-9) and ip[k] > 1e-13]
        if len(pts) < 10: continue
        dl = np.array([abs(np.log10(y) - np.log10(ib[np.abs(vb - (v - s)) < 1e-9][0])) for v, y in pts])
        if best is None or dl.max() < best[1]: best = (float(s), float(dl.max()), float(np.median(dl)), len(pts))
    d['rigid_best_shift_V'], d['rigid_max_dlog'], d['rigid_median_dlog'], d['rigid_npts'] = best
    iso[f'{lab}_{t}'] = d
    print(f'   delta: ' + ', '.join(f'{k} {v:+.4g}' for k, v in d.items() if v is not None))
res['iso'] = iso
# thickness dependence of the 2 -> 13.2 differences
for lab, b2, p2, b13, p13 in [('WF', 'run_0038', 'run_0048', 'run_0040', 'run_0049'), ('mstar', 'run_0038', 'run_0050', 'run_0040', 'run_0051')]:
    M = {r: all_metrics(*read_idvg(r), t) for r, t in [(b2, 2.0), (p2, 2.0), (b13, 13.2), (p13, 13.2)]}
    dv_b = M[b13]['V_1e-9'] - M[b2]['V_1e-9']; dv_p = M[p13]['V_1e-9'] - M[p2]['V_1e-9']
    ir_b = M[b13]['Ion_A_per_um'] / M[b2]['Ion_A_per_um']; ir_p = M[p13]['Ion_A_per_um'] / M[p2]['Ion_A_per_um']
    ss_b = M[b13]['SS_10_8'] - M[b2]['SS_10_8']; ss_p = M[p13]['SS_10_8'] - M[p2]['SS_10_8']
    mr_b = M[b13]['mu_FE_cm2Vs'] / M[b2]['mu_FE_cm2Vs']; mr_p = M[p13]['mu_FE_cm2Vs'] / M[p2]['mu_FE_cm2Vs']
    print(f'{lab}: dVth_cc(2->13.2) {dv_b:+.4f} -> {dv_p:+.4f} (change {1000*(dv_p-dv_b):+.1f} mV); Ion ratio 13.2/2 {ir_b:.4f} -> {ir_p:.4f} ({100*(ir_p/ir_b-1):+.2f} %); '
          f'SS_cc difference 13.2-2 {ss_b:+.1f} -> {ss_p:+.1f}; mu_FE ratio {mr_b:.4f} -> {mr_p:.4f}')
    res[f'tdep_{lab}'] = dict(dV_base=dv_b, dV_pert=dv_p, Iratio_base=ir_b, Iratio_pert=ir_p, dSS_base=ss_b, dSS_pert=ss_p, muratio_base=mr_b, muratio_pert=mr_p)
# rigid-shift test for Qf pairs
for lab, base, pert, t in [('Qf 0 -> 1.73e12 (2 nm)', 'run_0001', 'run_0003', 2.0), ('Qf 0 -> 1.73e12 (13.2 nm)', 'run_0002', 'run_0004', 13.2), ('Qf 1.73e12 -> 8.7e10 (6.3 nm)', 'run_0005', 'run_0007', 6.3)]:
    vb, ib = read_idvg(base); vp, ip = read_idvg(pert)
    ma, mb2 = robust(vb, ib), robust(vp, ip)
    print(f'{lab}: dV at 1e-11/1e-10/1e-9/1e-8/1e-7 = ' + ', '.join(f"{1000*(mb2[k]-ma[k]):+.1f}" for k in ['V_1e-11', 'V_1e-10', 'V_1e-9', 'V_1e-8', 'V_1e-7'] if ma[k] is not None and mb2[k] is not None) + ' mV')

print('\n=== C. 6.3 nm hypothesis closure (robust metrics) ===')
print(HDR)
hyp = {}
vg, i = meas(6.3); hyp['meas'] = all_metrics(vg, i, 6.3, False); print(row('measured 6.3 nm', hyp['meas']))
for lab, rid, sc in [('run_0014 validation (Qf 1.73e12, mu 12.4, 96/48)', 'run_0014', 1.0), ('run_0015 tuned (Qf 8.7e10, mu 11.69, 96/48)', 'run_0015', 1.0),
                     ('B2 run_0039 x1.01507 (tuned, 384/192)', 'run_0039', MU[6.3] / 11.41), ('A7 run_0036 mesh x0.7 of run_0015', 'run_0036', 1.0),
                     ('A3 run_0030 back -1.64e12', 'run_0030', 1.0), ('A1 run_0031 t=5.3 nm', 'run_0031', 1.0), ('A2 run_0032 Nd0 1e16', 'run_0032', 1.0),
                     ('A4 run_0033 Dit x5', 'run_0033', 1.0), ('A6 run_0034 no QC, Qf from 2 nm (held-out)', 'run_0034', 1.0), ('A5 run_0035 combination', 'run_0035', 1.0),
                     ('B0 run_0037 S2 re-partition (96/48)', 'run_0037', 1.0), ('C1 run_0052 S4 near-Ec band + mu 15.4 (384/192)', 'run_0052', 1.0)]:
    vg, i = read_idvg(rid); m = all_metrics(vg, i * sc, 6.3); hyp[rid] = m; print(row(lab, m))
res['hyp'] = hyp
json.dump(res, open(Path(__file__).with_name('s6_part2_out.json'), 'w'), indent=1, default=float)
