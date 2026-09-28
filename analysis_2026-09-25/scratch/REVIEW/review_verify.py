#!/usr/bin/env python3
"""Referee re-computation of load-bearing specialist claims (REVIEW.md).
Reads only raw files (data/experimental_clean.csv, results/runs/*/{comparison.csv,idvg.dat,execution.json,metadata.json},
deckbuild.out). Uses scripts/extract_metrics.py unchanged (imported). No ATLAS launch, no package file modified."""
import sys, json, math, csv, glob
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import extract_metrics as em   # unchanged package extractor

RUNS = ROOT / 'results' / 'runs'
Q = 1.602176634e-19
COX = em.COX
qC = Q / COX * 1e12          # V per 1e12 cm^-2
out = {}

def rdir(rid):
    return Path(glob.glob(str(RUNS / f'{rid}_*'))[0])

def exe(rid):
    return json.loads((rdir(rid) / 'execution.json').read_text())

def meta(rid):
    return json.loads((rdir(rid) / 'metadata.json').read_text())

def comp(rid):
    rows = list(csv.DictReader((rdir(rid) / 'comparison.csv').open()))
    return (np.array([float(r['vg_V']) for r in rows]), np.array([float(r['measured_A_per_um']) for r in rows]),
            np.array([float(r['atlas_A_per_um']) for r in rows]))

def native(rid, name='idvg.dat'):
    lines = (rdir(rid) / name).read_text().split('\n')[4:]
    xy = np.array([[float(v) for v in l.split()] for l in lines if l.strip()])
    return xy[:, 0], xy[:, 1]

def meas(t):
    return em.load_curve(ROOT / 'data' / 'experimental_clean.csv', t)

def V_at(vg, idv, I):
    return em.crossing(vg, idv, I)

def p(*a):
    print(*a)

# ---------------------------------------------------------------- 0. measured metrics
p('=== 0. measured metrics (extract_metrics.py unchanged)')
M = {}
for t in (2.0, 6.3, 13.2, 31.8):
    vg, idv = meas(t); M[t] = em.metrics(vg, idv, False, t)
    m = M[t]
    p(t, {k: (float('%.5g' % v) if isinstance(v, (float, np.floating)) else v) for k, v in m.items() if k in ('Vth_cc_1e-9_V', 'Vth_lin_V', 'SS_mV_dec', 'SS_cc_1e-10_1e-8_mV_dec', 'gm_max_A_V_um', 'mu_FE_cm2Vs', 'Ion_A_per_um', 'off_band_median_A_per_um')})
    gm = np.gradient(idv, vg); p('   gm argmax at Vg =', vg[int(np.argmax(gm))], ' gm(3V)/gm_max =', round(gm[-1] / gm.max(), 4))

# ---------------------------------------------------------------- 1. run metrics recomputed from comparison.csv
p('\n=== 1. simulated metrics recomputed from comparison.csv (atlas column, already np.interp onto the 0.05 V grid)')
RUNLIST = ['run_0001', 'run_0002', 'run_0003', 'run_0004', 'run_0005', 'run_0007', 'run_0012', 'run_0013', 'run_0014', 'run_0015', 'run_0016', 'run_0017',
           'run_0019', 'run_0029', 'run_0030', 'run_0031', 'run_0032', 'run_0033', 'run_0034', 'run_0035', 'run_0036', 'run_0037', 'run_0038',
           'run_0039', 'run_0040', 'run_0048', 'run_0049', 'run_0050', 'run_0051', 'run_0052']
S = {}
for rid in RUNLIST:
    try:
        ex = exe(rid); t = ex['thickness_nm']; vg, mm, pr = comp(rid)
        m = em.metrics(vg, pr, True, t); S[rid] = dict(m, t=t, rmse=ex['fit_metrics']['regions']['active']['rmse_log10'], ion_err=ex['fit_metrics']['on_error_3V_percent'])
        dj = ex['device_metrics_sim']
        keys = [k for k in ('Vth_cc_1e-9_V', 'SS_cc_1e-10_1e-8_mV_dec', 'gm_max_A_V_um', 'Ion_A_per_um') if k in dj]
        same = all(abs((m[k] or 0) - (dj[k] or 0)) < 1e-9 * max(1, abs(dj[k] or 0)) for k in keys) if keys else 'n/a (older execution.json schema)'
        p(rid, t, 'Vcc %.4f Vlin %.4f SSmin %s SScc %.1f gm %.4e muFE %.3f Ion %.4e RMSE %.4f IonErr %+.2f%% | matches execution.json: %s' % (
            m['Vth_cc_1e-9_V'], m['Vth_lin_V'], ('%.1f' % m['SS_mV_dec']) if m['SS_mV_dec'] else None, m['SS_cc_1e-10_1e-8_mV_dec'] or float('nan'), m['gm_max_A_V_um'], m['mu_FE_cm2Vs'], m['Ion_A_per_um'], S[rid]['rmse'], S[rid]['ion_err'], same))
    except Exception as e:
        p(rid, 'ERROR', e)

def miss(rid):
    return S[rid]['Vth_cc_1e-9_V'] - M[S[rid]['t']]['Vth_cc_1e-9_V']

p('\n--- V1: A6 (run_0034) vs run_0014 Vth_cc miss')
p('run_0014 miss %+.4f V ; run_0034 (A6) miss %+.4f V ; run_0015 miss %+.4f V' % (miss('run_0014'), miss('run_0034'), miss('run_0015')))
p('gap (Vth_lin - Vth_cc): meas 6.3 %.4f ; run_0014 %.4f ; run_0015 %.4f ; run_0034 %.4f ; B0 %.4f ; C1 %.4f' % (
    M[6.3]['Vth_lin_V'] - M[6.3]['Vth_cc_1e-9_V'], *[S[r]['Vth_lin_V'] - S[r]['Vth_cc_1e-9_V'] for r in ('run_0014', 'run_0015', 'run_0034', 'run_0037', 'run_0052')]))

p('\n--- V2: B0 run_0037')
b0 = S['run_0037']
p('B0 Vcc %.4f Vlin %.4f SS_cc %.2f SS_min %.2f muFE %.3f Ion err %+.2f%%; meas SS_cc %.2f SS_min %.2f' % (
    b0['Vth_cc_1e-9_V'], b0['Vth_lin_V'], b0['SS_cc_1e-10_1e-8_mV_dec'], b0['SS_mV_dec'], b0['mu_FE_cm2Vs'], b0['ion_err'], M[6.3]['SS_cc_1e-10_1e-8_mV_dec'], M[6.3]['SS_mV_dec']))
p('B0 SS_cc - run_0015 SS_cc = %+.1f ; B0 SS_min - run_0015 SS_min = %+.1f' % (b0['SS_cc_1e-10_1e-8_mV_dec'] - S['run_0015']['SS_cc_1e-10_1e-8_mV_dec'], b0['SS_mV_dec'] - S['run_0015']['SS_mV_dec']))

# ---------------------------------------------------------------- 3. saturation-formula reproduction
p('\n=== V3: saturation-formula mobility mu_sat = 2L/(W Cox) (d sqrt(Id)/dVg)^2 with several derivative schemes')
K = 2 * em.L_CM / (em.W_CM * COX)
try:
    from scipy.signal import savgol_filter
except Exception:
    savgol_filter = None
musat = {}
for t in (2.0, 6.3, 13.2):
    vg, idv = meas(t); s = np.sqrt(idv); h = vg[1] - vg[0]
    sch = {}
    sch['central np.gradient(sqrt Id)'] = np.gradient(s, vg)
    sch['forward diff'] = np.append(np.diff(s) / h, np.nan)
    sch['backward diff'] = np.insert(np.diff(s) / h, 0, np.nan)
    sch['gm/(2 sqrt Id), central gm'] = np.gradient(idv, vg) / (2 * s)
    if savgol_filter is not None:
        for w in (5, 7, 9):
            sch[f'Savitzky-Golay w{w} o2'] = savgol_filter(s, w, 2, deriv=1, delta=h)
    res = {}
    for k, d in sch.items():
        v = K * d ** 2; v = np.where(np.isfinite(v), v, -1); i = int(np.argmax(v)); res[k] = (float(v[i]), float(vg[i]))
    musat[t] = res
    p(t, ' '.join(f'[{k}: {v[0]:.2f} @ {v[1]:.2f} V]' for k, v in res.items()))
    vcc, vlin = M[t]['Vth_cc_1e-9_V'], M[t]['Vth_lin_V']; vp = res['central np.gradient(sqrt Id)'][1]
    p('   central-scheme peak at %.2f V: Vov vs Vth_cc = %.2f V, vs Vth_lin = %.2f V (Vd 0.7 V); mu_sat/mu_FE(lin) = %.3f' % (vp, vp - vcc, vp - vlin, res['central np.gradient(sqrt Id)'][0] / M[t]['mu_FE_cm2Vs']))
p('ratio 13.2/2 (central) = %.3f ; paper 27.4/5.1 = %.3f' % (musat[13.2]['central np.gradient(sqrt Id)'][0] / musat[2.0]['central np.gradient(sqrt Id)'][0], 27.4 / 5.1))

# ---------------------------------------------------------------- 4. floors
p('\n=== V4: off-state floors')
fl = {}
for t in (2.0, 6.3, 13.2):
    vg, idv = meas(t)
    for lo, hi in ((-2, -0.5), (-3, -0.5), (-3, -2)):
        sel = (vg >= lo - 1e-9) & (vg <= hi + 1e-9); x = vg[sel]; y = idv[sel]
        med = float(np.median(y)); sl = np.polyfit(x, np.log10(y), 1)[0]
        dev = y / med
        p(f'{t} [{lo},{hi}] n={sel.sum()} median {med:.3e} min {y.min():.3e} max {y.max():.3e} max/min {y.max()/y.min():.2f} '
          f'p10/p90 of I/median {np.percentile(dev,10):.3f}/{np.percentile(dev,90):.3f} slope {sl:+.4f} dec/V; total current (x290 um) {med*290:.2e} A')
        if (lo, hi) == (-2, -0.5): fl[t] = med
    # half-window medians to test flatness vs Vg
    a = np.median(idv[(vg >= -3) & (vg <= -1.75)]); b = np.median(idv[(vg >= -1.75) & (vg <= -0.5)])
    p(f'   median(-3..-1.75)/median(-1.75..-0.5) = {a/b:.3f}')
p('floor ratio 13.2/2 = %.1f (exponent %.3f); 6.3/2 = %.1f (exp %.3f); 13.2/6.3 = %.1f (exp %.3f)' % (
    fl[13.2] / fl[2.0], math.log(fl[13.2] / fl[2.0]) / math.log(6.6), fl[6.3] / fl[2.0], math.log(fl[6.3] / fl[2.0]) / math.log(3.15), fl[13.2] / fl[6.3], math.log(fl[13.2] / fl[6.3]) / math.log(13.2 / 6.3)))
for t in (2.0, 6.3, 13.2):
    p(f'  floor/Ion {t}: {fl[t]/M[t]["Ion_A_per_um"]:.2e}')

# ---------------------------------------------------------------- 5. q/Cox and rigid-shift equivalence
p('\n=== V5: q/Cox rigid shifts')
p('q/Cox = %.5f V per 1e12 cm^-2 ; dQf 1.73e12-8.7e10 -> %.4f V ; 1.73e12 -> %.4f V ; 1.73e12-4.76e10 -> %.4f V' % (qC, 1.643 * qC, 1.73 * qC, (1.73 - 0.0476) * qC))
dEc = lambda t: 0.9205 * t ** -1.3815
p('dEc law: 2 nm %.4f, 6.3 nm %.4f, 13.2 nm %.4f eV; dEc(2) as charge %.3e cm^-2' % (dEc(2), dEc(6.3), dEc(13.2), dEc(2) / qC * 1e12))
def hshift(ra, rb, currents):
    va, ia = native(ra); vb, ib = native(rb); r = []
    for I in currents:
        a = V_at(va, ia, I); b = V_at(vb, ib, I); r.append(None if (a is None or b is None) else a - b)
    return r
cur = [1e-14, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 3e-7]
for ra, rb, lab in (('run_0012', 'run_0016', '2 nm QC on - off'), ('run_0013', 'run_0017', '13.2 nm QC on - off'), ('run_0003', 'run_0001', '2 nm Qf 1.73e12 - 0'),
                    ('run_0004', 'run_0002', '13.2 nm Qf 1.73e12 - 0'), ('run_0007', 'run_0005', '6.3 nm Qf 8.7e10 - 1.73e12'), ('run_0034', 'run_0014', '6.3 nm A6 - run_0014')):
    try:
        p(lab, ' '.join(f'{I:.0e}:{(d if d is None else round(d,4))}' for I, d in zip(cur, hshift(ra, rb, cur))))
    except Exception as e:
        p(lab, 'ERROR', e)
p('Vth_cc realised confinement: 2 nm (0012-0016) %.4f ; 13.2 nm (0013-0017) %.4f ; 6.3 nm (0014 - (0034 - Qf shift)) %.4f' % (
    S['run_0012']['Vth_cc_1e-9_V'] - S['run_0016']['Vth_cc_1e-9_V'], S['run_0013']['Vth_cc_1e-9_V'] - S['run_0017']['Vth_cc_1e-9_V'],
    S['run_0014']['Vth_cc_1e-9_V'] - (S['run_0034']['Vth_cc_1e-9_V'] - (1.73 - 0.0476) * qC)))
p('SS_cc 0012 / 0016 / meas2: %.1f / %.1f / %.1f' % (S['run_0012']['SS_cc_1e-10_1e-8_mV_dec'], S['run_0016']['SS_cc_1e-10_1e-8_mV_dec'], M[2.0]['SS_cc_1e-10_1e-8_mV_dec']))

# ---------------------------------------------------------------- 6. DOS offset
p('\n=== V6: DOS 96/48 -> 384/192 Ion offset at equal mu')
mu = lambda rid: meta(rid)['material']['mu_band']
for a, b in (('run_0012', 'run_0029'), ('run_0012', 'run_0038'), ('run_0015', 'run_0039'), ('run_0013', 'run_0040')):
    ia, ib = S[a]['Ion_A_per_um'], S[b]['Ion_A_per_um']; ma, mb = mu(a), mu(b)
    p(f'{a} (mu {ma}) Ion {ia:.5e} ; {b} (mu {mb}) Ion {ib:.5e} ; offset at equal mu = {100*(ib*ma/mb/ia-1):+.3f} %')
i96, i192, i384 = S['run_0012']['Ion_A_per_um'], S['run_0019']['Ion_A_per_um'], S['run_0029']['Ion_A_per_um']
p('mu 0012/0019/0029: %s %s %s' % (mu('run_0012'), mu('run_0019'), mu('run_0029')))
d1 = i192 / i96 - 1; d2 = i384 / i192 - 1; pr = math.log(d1 / d2) / math.log(2)
p(f'refinement 96->192 {100*d1:+.3f} %, 192->384 {100*d2:+.3f} %, observed order p = {pr:.2f}, Richardson residual beyond 384 = {100*d2/(2**pr-1):+.3f} %')
p('mu recal: 2 nm %.4f 6.3 nm %.4f 13.2 nm %.4f' % (18.13 * M[2.0]['Ion_A_per_um'] / (S['run_0029']['Ion_A_per_um']), 11.41 * M[6.3]['Ion_A_per_um'] / S['run_0039']['Ion_A_per_um'], 60.39 * M[13.2]['Ion_A_per_um'] / S['run_0040']['Ion_A_per_um']))
va, ia = native('run_0029'); vb, ib = native('run_0038'); sel = (ia > 1e-14) & (ib > 1e-14)
r = ia[sel] / ib[sel]; p(f'linearity run_0029/run_0038 over {sel.sum()} pts: mean {r.mean():.6f} min {r.min():.6f} max {r.max():.6f} ; mu ratio {mu("run_0029")/mu("run_0038"):.6f}')

# ---------------------------------------------------------------- 7. tmu
p('\n=== V7: tmu factor')
for T in (338.15, 358.15):
    p(f'T {T}: (T/300)^-1.5 = {(T/300)**-1.5:.5f} ; (T/300)^+1.5 = {(T/300)**1.5:.5f}')
rough2 = (1 - 0.287 / 2) ** 2
p('2 nm mun at 300 K = mu_band 17.6897 x (1-0.287/2)^2 = %.4f (deckbuild prints "mu = 12.977 @ 358 K, tmu 1.5")' % (17.6897 * rough2))
for rid, ref, T, t in (('run_0045', 'run_0038', 358.15, 2.0), ('run_0044', 'run_0038', 338.15, 2.0), ('run_0046', 'run_0039', 358.15, 6.3), ('run_0047', 'run_0040', 358.15, 13.2)):
    vg, idv = native(rid); ion = idv[-1]; vr, ir = native(ref); ionr = ir[-1]
    ex = exe(rid); mm = ex.get('device_metrics_sim', {})
    p(f'{rid} ({T} K) Ion_native {ion:.4e} / {ref} {ionr:.4e} = {ion/ionr:.4f} ; x(T/300)^1.5 = {ion/ionr*(T/300)**1.5:.4f} ; mu_band run/ref {mu(rid)}/{mu(ref)}')

# ---------------------------------------------------------------- 8. S1 decomposition
p('\n=== V8: S1 "86 % of the 2->6.3 drop is confinement"')
dm = S['run_0012']['Vth_cc_1e-9_V'] - S['run_0014']['Vth_cc_1e-9_V']
p('ATLAS 2->6.3 model drop (0012-0014) %.4f V ; bare dEc difference %.4f eV -> %.1f %% ; realised (counterfactual) confinement difference %.4f V -> %.1f %%' % (
    dm, dEc(2) - dEc(6.3), 100 * (dEc(2) - dEc(6.3)) / dm,
    (S['run_0012']['Vth_cc_1e-9_V'] - S['run_0016']['Vth_cc_1e-9_V']) - (S['run_0014']['Vth_cc_1e-9_V'] - (S['run_0034']['Vth_cc_1e-9_V'] - (1.73 - 0.0476) * qC)),
    100 * ((S['run_0012']['Vth_cc_1e-9_V'] - S['run_0016']['Vth_cc_1e-9_V']) - (S['run_0014']['Vth_cc_1e-9_V'] - (S['run_0034']['Vth_cc_1e-9_V'] - (1.73 - 0.0476) * qC))) / dm))
d213m = M[2.0]['Vth_cc_1e-9_V'] - M[13.2]['Vth_cc_1e-9_V']; qc213 = (S['run_0012']['Vth_cc_1e-9_V'] - S['run_0016']['Vth_cc_1e-9_V']) - (S['run_0013']['Vth_cc_1e-9_V'] - S['run_0017']['Vth_cc_1e-9_V'])
p('measured 2->13.2 Vth_cc step %.4f V ; model step (0012-0013) %.4f ; realised confinement share %.4f V = %.1f %% of the measured step' % (
    d213m, S['run_0012']['Vth_cc_1e-9_V'] - S['run_0013']['Vth_cc_1e-9_V'], qc213, 100 * qc213 / d213m))
p('runs 0001/0002 offsets vs measured: 2 nm %+.4f, 13.2 nm %+.4f (diff %.4f V)' % (miss('run_0001'), miss('run_0002'), miss('run_0001') - miss('run_0002')))
p('runs 0003/0004 offsets vs measured: 2 nm %+.4f, 13.2 nm %+.4f' % (miss('run_0003'), miss('run_0004')))
for rid in ('run_0001', 'run_0002', 'run_0003', 'run_0004'):
    mt = meta(rid)['material']; p(f'   {rid}: Qf {mt.get("Qf_cm2")} mu_band {mt.get("mu_band")} full_structure {meta(rid).get("full_structure")}')

# ---------------------------------------------------------------- 9. SS_min
p('\n=== V9: SS_min window phase (2 nm)')
thr = 5 * fl[2.0]
for rid in ('run_0012', 'run_0038', 'run_0029'):
    vg, mm, pr = comp(rid); i = int(np.argmin(abs(vg - 0.15)))
    p(f'{rid}: Id(0.15 V) {pr[i]:.4e} vs 5xfloor {thr:.4e} -> window starts {"0.15" if pr[i] > thr else ">=0.20"} ; SS_min {S[rid]["SS_mV_dec"]:.2f}')
p('run_0013 / run_0017 SS_min %.1f / %.1f' % (S['run_0013']['SS_mV_dec'], S['run_0017']['SS_mV_dec']))

# ---------------------------------------------------------------- 10. fixed-current SS with / without floor subtraction
p('\n=== V10: fixed-current SS (measured), with and without subtracting the off-band median')
def ssfix(vg, idv, i1, i2):
    a = V_at(vg, idv, i1); b = V_at(vg, idv, i2)
    return None if (a is None or b is None) else (b - a) / math.log10(i2 / i1) * 1000
for t in (2.0, 6.3, 13.2):
    vg, idv = meas(t); sub = idv - fl[t]; sub = np.where(sub > 0, sub, np.nan)
    # crossing() needs positive values; replace nan by tiny
    sub2 = np.where(np.isfinite(sub), sub, 1e-30)
    p(t, 'SS 1e-11..1e-10: raw %s sub %s ; 1e-10..1e-9: raw %s sub %s' % tuple(
        (None if v is None else round(v, 1)) for v in (ssfix(vg, idv, 1e-11, 1e-10), ssfix(vg, sub2, 1e-11, 1e-10), ssfix(vg, idv, 1e-10, 1e-9), ssfix(vg, sub2, 1e-10, 1e-9))))
for rid in ('run_0038', 'run_0039', 'run_0040'):
    vg, ii = native(rid); p(rid, 'sim SS 1e-11..1e-10 %.1f ; 1e-10..1e-9 %.1f' % (ssfix(vg, ii, 1e-11, 1e-10), ssfix(vg, ii, 1e-10, 1e-9)))

# ---------------------------------------------------------------- 11. symmetric leave-one-out, QC vs no QC
p('\n=== V11: one-offset Vth_cc stories, QC vs no-QC (rigid Qf shift exact)')
Vm = {t: M[t]['Vth_cc_1e-9_V'] for t in (2.0, 6.3, 13.2)}
QC = {2.0: S['run_0012']['Vth_cc_1e-9_V'], 6.3: S['run_0014']['Vth_cc_1e-9_V'], 13.2: S['run_0013']['Vth_cc_1e-9_V']}           # Qf 1.73e12
NQ = {2.0: S['run_0016']['Vth_cc_1e-9_V'], 6.3: S['run_0034']['Vth_cc_1e-9_V'] - (1.73 - 0.0476) * qC, 13.2: S['run_0017']['Vth_cc_1e-9_V']}  # all at Qf 1.73e12
for name, mod in (('QC', QC), ('noQC', NQ)):
    res = {t: mod[t] - Vm[t] for t in Vm}
    p(name, 'raw residuals at Qf 1.73e12:', {t: round(v, 4) for t, v in res.items()})
    for anchor in (2.0, 6.3, 13.2):
        off = -res[anchor]; r = {t: res[t] + off for t in Vm if t != anchor}
        rms = math.sqrt(np.mean([v ** 2 for v in r.values()]))
        p(f'   Qf fitted on {anchor} nm only -> held-out misses {dict((k, round(v,4)) for k,v in r.items())}  rms {rms:.4f} V ; Qf = {(1.73 - off/qC):.3f}e12 cm^-2')
    off = -np.mean(list(res.values())); r = {t: res[t] + off for t in Vm}; p('   LSQ offset over all 3 -> residuals', {k: round(v, 4) for k, v in r.items()}, 'rms %.4f V' % math.sqrt(np.mean([v ** 2 for v in r.values()])))
    # leave-one-out with LSQ offset on the other two
    loo = {}
    for h in Vm:
        others = [t for t in Vm if t != h]; off = -np.mean([res[t] for t in others]); loo[h] = res[h] + off
    p('   LOO (offset from the other two) held-out misses', {k: round(v, 4) for k, v in loo.items()}, 'rms %.4f' % math.sqrt(np.mean([v ** 2 for v in loo.values()])))

# ---------------------------------------------------------------- 12. S2 LOO power law vs step
p('\n=== V12: LOO on mu_FE (fit 2 & 13.2, predict 6.3)')
mf = {t: M[t]['mu_FE_cm2Vs'] for t in (2.0, 6.3, 13.2)}
b = math.log(mf[13.2] / mf[2.0]) / math.log(6.6); pred = mf[2.0] * (6.3 / 2) ** b
p(f'power-law exponent {b:.4f}; predicted mu(6.3) {pred:.2f} vs {mf[6.3]:.2f} -> x{pred/mf[6.3]:.2f}')
p(f'step with t_c in (6.3,13.2): predicted mu(6.3) = mu(2) = {mf[2.0]:.2f} -> x{mf[2.0]/mf[6.3]:.3f}; step with t_c in (2,6.3): predicted {mf[13.2]:.2f} -> x{mf[13.2]/mf[6.3]:.2f}')
p('Nt exponent ln4/ln6.6 = %.4f ; Nt law check 2e19 (2/6.3)^0.75 = %.3e, (2/13.2)^0.75 = %.3e' % (math.log(4) / math.log(6.6), 2e19 * (2 / 6.3) ** 0.75, 2e19 * (2 / 13.2) ** 0.75))

# ---------------------------------------------------------------- 13. CC-definition mobility effect (S1)
p('\n=== V13: CC-definition effect on measured 13.2 nm (S1: +0.108 / +0.115 V)')
vg, idv = meas(13.2)
for lab, ratio in (('mu_FE', mf[13.2] / mf[2.0]), ('mu0 4.45', 4.45)):
    p(lab, 'ratio %.3f  Vg(1e-9 x ratio) - Vg(1e-9) = %+.4f V' % (ratio, V_at(vg, idv, 1e-9 * ratio) - V_at(vg, idv, 1e-9)))

# ---------------------------------------------------------------- 14. 31.8 nm apparent mu_FE
p('\n=== V14: 31.8 nm')
vg, idv = meas(31.8); gm = np.gradient(idv, vg); i = int(np.argmax(gm))
p('31.8 nm gm_max %.4e at Vg %.2f V -> mu_FE %.2f ; Id(-3 V) %.3e ; local gm maxima at Vg: %s' % (gm[i], vg[i], M[31.8]['mu_FE_cm2Vs'], idv[0],
  [float(vg[k]) for k in range(1, len(gm) - 1) if gm[k] > gm[k - 1] and gm[k] >= gm[k + 1] and gm[k] > 0.5 * gm.max()]))

# ---------------------------------------------------------------- 15. isolation Ion (brief 5b vs S6)
p('\n=== V15: isolation runs Ion vs same-mu baselines')
for rid, ref in (('run_0048', 'run_0038'), ('run_0049', 'run_0040'), ('run_0050', 'run_0038'), ('run_0051', 'run_0040')):
    p(f'{rid} (mu {mu(rid)}) vs {ref} (mu {mu(ref)}): dIon {100*(S[rid]["Ion_A_per_um"]/S[ref]["Ion_A_per_um"]-1):+.2f} % ; vs measured {S[rid]["ion_err"]:+.2f} % ; dVth_cc {S[rid]["Vth_cc_1e-9_V"]-S[ref]["Vth_cc_1e-9_V"]:+.4f} V ; dSS_cc {S[rid]["SS_cc_1e-10_1e-8_mV_dec"]-S[ref]["SS_cc_1e-10_1e-8_mV_dec"]:+.1f}')

# ---------------------------------------------------------------- 16. A7 mesh, active-region spans
p('\n=== V16: A7 mesh check and active-region spans')
p('run_0036 RMSE %.5f Ion err %+.3f%% ; run_0015 RMSE %.5f ; dVth_cc %.5f V' % (S['run_0036']['rmse'], S['run_0036']['ion_err'], S['run_0015']['rmse'], S['run_0036']['Vth_cc_1e-9_V'] - S['run_0015']['Vth_cc_1e-9_V']))
for rid in ('run_0012', 'run_0015', 'run_0013', 'run_0038', 'run_0039', 'run_0040'):
    vg, mm, pr = comp(rid); o = float(np.median(mm[(vg >= -2) & (vg <= -.5)])); act = mm > 5 * o   # config/solver.yaml scoring.active_multiplier = 5.0
    cnt = exe(rid)['fit_metrics']['regions']['active']['count']
    p(f'{rid}: active region Vg {vg[act].min():.2f}..{vg[act].max():.2f} V, n={act.sum()} (execution.json count {cnt}), Id {mm[act].min():.2e}..{mm[act].max():.2e} ({math.log10(mm[act].max()/mm[act].min()):.2f} dec)')

# ---------------------------------------------------------------- 17. paper SS claim 60-70 mV/dec
p('\n=== V17: smallest point-to-point SS on the measured curves (paper claims 60-70 mV/dec)')
for t in (2.0, 6.3, 13.2):
    vg, idv = meas(t); lg = np.log10(idv); d = np.diff(lg); ss = np.where(d > 0, 0.05 / np.where(d > 0, d, 1) * 1000, np.inf)
    j = int(np.argmin(ss)); p(f'{t}: min 2-point SS {ss[j]:.1f} mV/dec between Vg {vg[j]:.2f} and {vg[j+1]:.2f} (Id {idv[j]:.2e} -> {idv[j+1]:.2e}); SS_min(5-pt, floor-gated) {M[t]["SS_mV_dec"]:.1f}')
    # 5-point without floor gate
    best = min(((vg[i+2]-vg[i-2])/(lg[i+2]-lg[i-2])*1000, vg[i]) for i in range(2, len(vg)-2) if lg[i+2] > lg[i-2])
    p(f'     5-pt SS without floor gate: {best[0]:.1f} at Vg {best[1]:.2f}')

# ---------------------------------------------------------------- 18. tuned run: overdrive vs mobility share of the +26.8 % Ion
p('\n=== V18: share of run_0014 Ion error due to mobility choice')
i14 = S['run_0014']['Ion_A_per_um']; i15 = S['run_0015']['Ion_A_per_um']; m14 = mu('run_0014'); m15 = mu('run_0015')
p(f'run_0014 Ion {i14:.4e} (mu {m14}); run_0015 {i15:.4e} (mu {m15}); run_0015 rescaled to mu {m14}: {i15*m14/m15:.4e} -> {100*(i15*m14/m15/M[6.3]["Ion_A_per_um"]-1):+.2f} % ; log share of mobility in the +26.8 %: {math.log(m14/m15)/math.log(i14/M[6.3]["Ion_A_per_um"])*100:.1f} %')
p('run_0015 gap %.4f vs meas %.4f ; gm %.4e vs %.4e (%+.1f %%) ; Vth_lin miss %+.4f' % (S['run_0015']['Vth_lin_V'] - S['run_0015']['Vth_cc_1e-9_V'], M[6.3]['Vth_lin_V'] - M[6.3]['Vth_cc_1e-9_V'],
    S['run_0015']['gm_max_A_V_um'], M[6.3]['gm_max_A_V_um'], 100 * (S['run_0015']['gm_max_A_V_um'] / M[6.3]['gm_max_A_V_um'] - 1), S['run_0015']['Vth_lin_V'] - M[6.3]['Vth_lin_V']))
p('\n=== V19: small analytic checks quoted in REVIEW.md')
E1 = lambda t, m: 0.376 / (m * t * t)     # infinite-well parabolic bound, eV (t in nm), as used by S2
tx = (0.376 / (0.208 * 0.9205)) ** (1 / (2 - 1.3815))
p(f'dEc law vs infinite-well bound (m* 0.208): 6.3 nm {dEc(6.3):.4f} vs {E1(6.3,0.208):.4f} eV (x{dEc(6.3)/E1(6.3,0.208):.2f}); 13.2 nm {dEc(13.2):.4f} vs {E1(13.2,0.208):.4f} (x{dEc(13.2)/E1(13.2,0.208):.2f}); crossover t = {tx:.3f} nm')
p('WF +/-0.2 eV as Qf-equivalent: %.3e cm^-2' % (0.2 / qC * 1e12))
for t in (2.0, 13.2):
    vp = musat[t]['central np.gradient(sqrt Id)'][1]; vov = vp - M[t]['Vth_cc_1e-9_V']
    p(f'{t} nm: S2 heuristic Vd/(2Vov-Vd) with Vov vs Vth_cc = {0.7/(2*vov-0.7):.3f} ; actual mu_sat/mu_FE = {musat[t]["central np.gradient(sqrt Id)"][0]/M[t]["mu_FE_cm2Vs"]:.3f}')
p('no-QC Qf difference 13.2 vs 2 nm: %.3e cm^-2 (%.4f V)' % ((NQ[2.0] - Vm[2.0] - (NQ[13.2] - Vm[13.2])) / qC * 1e12, (NQ[2.0] - Vm[2.0]) - (NQ[13.2] - Vm[13.2])))
p('B1 / B3 (as run) Vth_cc misses: %+.4f / %+.4f V' % (miss('run_0038'), miss('run_0040')))
p('B1 on-state: gap %.4f vs meas %.4f (%+.4f V) ; gm %+.2f %%' % (S['run_0038']['Vth_lin_V'] - S['run_0038']['Vth_cc_1e-9_V'], M[2.0]['Vth_lin_V'] - M[2.0]['Vth_cc_1e-9_V'],
    (S['run_0038']['Vth_lin_V'] - S['run_0038']['Vth_cc_1e-9_V']) - (M[2.0]['Vth_lin_V'] - M[2.0]['Vth_cc_1e-9_V']), 100 * (S['run_0038']['gm_max_A_V_um'] / M[2.0]['gm_max_A_V_um'] - 1)))
p('C1 share of run_0015 gap miss: %.1f %%' % (100 * ((S['run_0052']['Vth_lin_V'] - S['run_0052']['Vth_cc_1e-9_V']) - (S['run_0015']['Vth_lin_V'] - S['run_0015']['Vth_cc_1e-9_V'])) / ((M[6.3]['Vth_lin_V'] - M[6.3]['Vth_cc_1e-9_V']) - (S['run_0015']['Vth_lin_V'] - S['run_0015']['Vth_cc_1e-9_V']))))
p('mu_band values in metadata: ' + ', '.join(f'{r}:{mu(r)}' for r in ('run_0012', 'run_0013', 'run_0014', 'run_0015', 'run_0034', 'run_0037', 'run_0052')))
