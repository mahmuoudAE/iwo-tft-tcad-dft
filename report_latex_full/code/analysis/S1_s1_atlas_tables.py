"""S1 (electrostatics): tables built ONLY from existing ATLAS outputs + measured data.
No ATLAS launch. Reads results/runs/*/execution.json, comparison.csv, cb/qfn/n profiles.
"""
import os, sys, json, glob, csv
import numpy as np

PKG = r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1"
OUT = os.path.join(PKG, 'analysis_2026-09-25', 'scratch', 'S1')
RUNS = os.path.join(PKG, 'results', 'runs')
sys.path.insert(0, os.path.join(PKG, 'scripts'))

def rdir(rid):
    return glob.glob(os.path.join(RUNS, rid + '_*'))[0]

def exe(rid):
    return json.load(open(os.path.join(rdir(rid), 'execution.json')))

def meta(rid):
    return json.load(open(os.path.join(rdir(rid), 'metadata.json')))

def read_xy(path):
    xs, ys = [], []
    for line in open(path):
        p = line.split()
        if len(p) != 2:
            continue
        try:
            xs.append(float(p[0])); ys.append(float(p[1]))
        except ValueError:
            pass
    return np.array(xs), np.array(ys)

KEYS = ['Vth_cc_1e-9_V', 'Vth_lin_V', 'SS_min_window_mV_dec', 'SS_cc_1e-10_1e-8_mV_dec', 'gm_max_A_V_um', 'Ion_A_per_um']
runs = ['run_0012', 'run_0016', 'run_0014', 'run_0015', 'run_0030', 'run_0031', 'run_0032', 'run_0033',
        'run_0034', 'run_0035', 'run_0013', 'run_0017', 'run_0020', 'run_0021', 'run_0022', 'run_0023', 'run_0024', 'run_0025']
res = {}
print('run      t    Qf        dEc    mu0   | Vth_cc  Vth_lin  gap   SSmin  SScc   gm_max    Ion      | active RMSE')
for r in runs:
    e = exe(r); m = meta(r)['material']
    s = e['device_metrics_sim']; x = e['device_metrics_exp']
    res[r] = {'sim': {k: s[k] for k in KEYS}, 'exp': {k: x[k] for k in KEYS}, 't': m['t_nm'], 'Qf': m['Qf_cm2'],
              'dEc': m['dEc_eV'], 'mu0': m['mu0'], 'Nd': m['Nd_cm3'], 'Nt': m['Nt_cm3'], 'label': e['label'],
              'rmse_active': e['fit_metrics']['regions']['active']['rmse_log10']}
    print(f"{r} {m['t_nm']:5.1f} {m['Qf_cm2']:9.3g} {m['dEc_eV']:6.3f} {m['mu0']:6.2f} | {s['Vth_cc_1e-9_V']:6.3f} {s['Vth_lin_V']:7.3f} "
          f"{s['Vth_lin_V']-s['Vth_cc_1e-9_V']:5.3f} {s['SS_min_window_mV_dec']:6.1f} {s['SS_cc_1e-10_1e-8_mV_dec']:6.1f} {s['gm_max_A_V_um']:9.3e} {s['Ion_A_per_um']:9.3e} | {res[r]['rmse_active']:.3f}  {e['label']}")

print('\nMeasured (from execution.json exp blocks):')
for r in ['run_0012', 'run_0014', 'run_0013']:
    x = res[r]['exp']
    print(f"t={res[r]['t']}: Vth_cc {x['Vth_cc_1e-9_V']:.3f} Vth_lin {x['Vth_lin_V']:.3f} gap {x['Vth_lin_V']-x['Vth_cc_1e-9_V']:.3f} SSmin {x['SS_min_window_mV_dec']:.1f} SScc {x['SS_cc_1e-10_1e-8_mV_dec']:.1f} gm {x['gm_max_A_V_um']:.3e} Ion {x['Ion_A_per_um']:.3e}")

# Campaign A deltas vs run_0014 and vs measurement
print('\nCampaign A (6.3 nm) deltas vs run_0014 | vs measured')
base = res['run_0014']['sim']; meas = res['run_0014']['exp']
for r in ['run_0015', 'run_0030', 'run_0031', 'run_0032', 'run_0033', 'run_0034', 'run_0035']:
    s = res[r]['sim']
    d = lambda k: s[k] - base[k]
    dm = lambda k: s[k] - meas[k]
    print(f"{r}: dVcc {d('Vth_cc_1e-9_V'):+.3f} dSSmin {d('SS_min_window_mV_dec'):+.1f} dSScc {d('SS_cc_1e-10_1e-8_mV_dec'):+.1f} dVlin {d('Vth_lin_V'):+.3f} "
          f"dgm {100*d('gm_max_A_V_um')/base['gm_max_A_V_um']:+.1f}% dIon {100*d('Ion_A_per_um')/base['Ion_A_per_um']:+.1f}% || vs meas: Vcc {dm('Vth_cc_1e-9_V'):+.3f} "
          f"SSmin {dm('SS_min_window_mV_dec'):+.1f} SScc {dm('SS_cc_1e-10_1e-8_mV_dec'):+.1f} Vlin {dm('Vth_lin_V'):+.3f} gm {100*dm('gm_max_A_V_um')/meas['gm_max_A_V_um']:+.1f}% Ion {100*dm('Ion_A_per_um')/meas['Ion_A_per_um']:+.1f}%")

# Horizontal offset dVg(I) = Vg_meas(I) - Vg_sim(I), and vertical log ratio at fixed Vg
def vg_at(vg, idv, level):
    idv = np.asarray(idv); ok = idv > 0
    for i in range(len(vg) - 1):
        if ok[i] and ok[i+1] and idv[i] < level <= idv[i+1]:
            a, b = np.log10(idv[i]), np.log10(idv[i+1])
            return vg[i] + (np.log10(level) - a) / (b - a) * (vg[i+1] - vg[i])
    return np.nan

levels = [1e-10, 1e-9, 1e-8, 3e-8, 1e-7, 2e-7, 3e-7]
print('\nHorizontal offset Vg_meas(I) - Vg_sim(I) [V] at I (A/um) =', levels)
curves = {}
for r in ['run_0012', 'run_0014', 'run_0015', 'run_0030', 'run_0031', 'run_0032', 'run_0033', 'run_0034', 'run_0035', 'run_0013', 'run_0016', 'run_0017']:
    rows = list(csv.DictReader(open(os.path.join(rdir(r), 'comparison.csv'))))
    vg = np.array([float(x['vg_V']) for x in rows]); im = np.array([float(x['measured_A_per_um']) for x in rows]); isim = np.array([float(x['atlas_A_per_um']) for x in rows])
    curves[r] = (vg, im, isim)
    off = [vg_at(vg, im, L) - vg_at(vg, isim, L) for L in levels]
    print(f"{r} ({res[r]['t']} nm): " + ' '.join(f"{o:+.3f}" for o in off))

# measured-curve based constant-current-definition effect: Vg(1e-9*ratio) - Vg(1e-9)
print('\nCC-definition effect from MEASURED curves: Vth shift if the film had the 2 nm mobility')
data = list(csv.DictReader(open(os.path.join(PKG, 'data', 'experimental_clean.csv'))))
meas = {}
for t in [2.0, 6.3, 13.2, 31.8]:
    rr = [d for d in data if abs(float(d['thickness_nm']) - t) < 1e-6]
    meas[t] = (np.array([float(d['vg_V']) for d in rr]), np.array([float(d['id_A_per_um']) for d in rr]))
muFE = {2.0: 12.15, 6.3: 10.95, 13.2: 50.17}
mu0 = {2.0: res['run_0012']['mu0'], 6.3: res['run_0015']['mu0'], 13.2: res['run_0013']['mu0']}
for t in [6.3, 13.2]:
    vg, idv = meas[t]
    for name, mu in [('mu_FE', muFE), ('mu0_band_eff', mu0)]:
        ratio = mu[t] / mu[2.0]
        dv = vg_at(vg, idv, 1e-9 * ratio) - vg_at(vg, idv, 1e-9)
        print(f"t={t}: {name} ratio {ratio:.3f} -> Vth_cc(if mu were the 2 nm value) - Vth_cc = {dv:+.3f} V  (log10 ratio {np.log10(ratio):+.3f})")

# Profiles at near_vth / on from ATLAS (channel centre x = 12 um)
print('\nATLAS depth profiles at x=12 um (IWO only): Ec-EFn at back/front, band bending, sheet n')
for r in ['run_0012', 'run_0014', 'run_0015', 'run_0030', 'run_0034', 'run_0035', 'run_0013', 'run_0017']:
    d = rdir(r); t = res[r]['t']
    dev = open(os.path.join(d, 'device.in')).read()
    import re
    vnear = re.findall(r'solve vstep=[-\d.]+ vfinal=([-\d.]+) name=gate\nsave outf=near_vth.str', dev)
    for snap in ['vth', 'on']:
        y, cb = read_xy(os.path.join(d, f'cb_{snap}.dat')); _, qf = read_xy(os.path.join(d, f'qfn_{snap}.dat')); _, n = read_xy(os.path.join(d, f'n_{snap}.dat'))
        # IWO = depth 0.070 .. 0.070 + t (um); air above has n=0
        msk = (y >= 0.07 - 1e-7) & (y <= 0.07 + t * 1e-3 + 1e-7)
        yy, cc, qq, nn = y[msk], cb[msk], qf[msk], n[msk]
        # remove duplicate depth points
        _, idx = np.unique(yy, return_index=True); yy, cc, qq, nn = yy[idx], cc[idx], qq[idx], nn[idx]
        ns = np.trapezoid(nn, yy * 1e-4)
        cen = np.trapezoid(nn * (yy - yy[0]) * 1e3, yy) / np.trapezoid(nn, yy)
        print(f"{r} {snap} (Vg={vnear[0] if snap=='vth' else 3.0}): Ec-Efn back {cc[0]-qq[0]:+.3f} eV, front {cc[-1]-qq[-1]:+.3f} eV, Ec(back)-Ec(front) {cc[0]-cc[-1]:+.3f} eV, n_s {ns:.3e} cm^-2, centroid from back {cen:.2f} nm of {t}")

json.dump(res, open(os.path.join(OUT, 's1_atlas_tables.json'), 'w'), indent=1)
