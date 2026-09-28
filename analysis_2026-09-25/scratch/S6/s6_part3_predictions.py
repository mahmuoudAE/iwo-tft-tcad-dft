"""S6 part 3: prediction register computations from real ATLAS outputs (B8-B10 ID-VD; B11-B14 elevated T; 300 K
references B1/B2/B3 rescaled exactly to the mu used in the prediction runs). Two temperature variants:
  P-phonon = as simulated (ATLAS silicon-default TMUN 1.5: mu(T) = mu300 (T/300)^-1.5, verified in run_0045 deckbuild.out)
  P-MTR    = simulated currents x (T/300)^+1.5 (T-independent band mobility; exact because Id is linear in a spatially
             uniform constant mobility, verified in part 1 to 1e-5).
Writes s6_part3_out.json and the canonical rows (s6_canonical_rows.json) consumed by s6_write_register.py."""
import csv, json, math
import numpy as np
from s6_lib import *

MU_PRED = {2.0: 17.6897, 6.3: 11.582, 13.2: 61.6046}          # mu_band in B8-B14 decks (campaign_B overrides)
REF = {2.0: ('run_0038', 17.69), 6.3: ('run_0039', 11.41), 13.2: ('run_0040', 60.39)}
IDVD = {2.0: 'run_0041', 6.3: 'run_0042', 13.2: 'run_0043'}
TRUNS = {(2.0, 338.15): 'run_0044', (2.0, 358.15): 'run_0045', (6.3, 358.15): 'run_0046', (13.2, 358.15): 'run_0047'}
FILMS = [2.0, 6.3, 13.2]; VGS_OUT = [1.0, 1.5, 2.0, 2.5, 3.0]; VDS = [0.05, 0.1, 0.5, 1.0, 2.0, 3.0]
VG_EA = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
tag = lambda t: {2.0: '2p0', 6.3: '6p3', 13.2: '13p2'}[t]
canon = []; out = {}
def C(film, T, var, vg, vd, q, val, unit, rid):
    canon.append(dict(film=f'{film:g} nm', T_K=T, variant=var, Vg=vg, Vd=vd, quantity=q, value=val, unit=unit, run_id=rid))

# ------------------------------------------------------------------ ID-VD
print('=== ID-VD predictions (300 K, ideal Ohmic Pd, constant mu, Vd sweep 0-3 V) ===')
idvd = {}
for t in FILMS:
    rid = IDVD[t]; rows = list(csv.DictReader((run_dir(rid) / 'output_characteristics.csv').open()))
    for vg in VGS_OUT:
        pts = sorted([(float(r['vd_V']), float(r['id_A_per_um'])) for r in rows if abs(float(r['vg_V']) - vg) < 1e-9])
        vd = np.array([p[0] for p in pts]); i = np.array([p[1] for p in pts])
        at = lambda x: float(i[np.argmin(np.abs(vd - x))])
        h = 0.05; I1, I2 = at(0.05), at(0.1); b = (I2 - 2 * I1) / (2 * h * h); a = (4 * I1 - I2) / (2 * h)
        g = np.gradient(i, vd); g0 = a
        vsat = None
        for k in range(1, len(vd)):
            if g[k] <= 0.1 * g0 and vd[k] > 0:
                vsat = float(vd[k - 1] + (vd[k] - vd[k - 1]) * (g[k - 1] - 0.1 * g0) / (g[k - 1] - g[k])); break
        gd3 = (at(3.0) - at(2.9)) / 0.1
        d = dict(Id={x: at(x) for x in VDS}, r_lin=I2 / I1, curv_b=b, gd0=g0, vdsat10=vsat, gd3=gd3, gd3_over_gd0=gd3 / g0, Id07=at(0.7))
        idvd[(t, vg)] = d
        for x in vd[vd > 0]: C(t, 300.0, 'as_simulated_300K', vg, float(x), 'Id', float(i[vd == x][0]), 'A/um', rid)
        C(t, 300.0, 'as_simulated_300K', vg, '0.1/0.05', 'Id_ratio_Vd0p1_over_Vd0p05', I2 / I1, '-', rid)
        C(t, 300.0, 'as_simulated_300K', vg, '0-0.1', 'gd0_quadratic_fit', g0, 'S/um', rid)
        C(t, 300.0, 'as_simulated_300K', vg, '0-0.1', 'd2Id_dVd2_at_0', 2 * b, 'A/um/V^2', rid)
        C(t, 300.0, 'as_simulated_300K', vg, '-', 'Vd_sat_gd_10pct_of_gd0', vsat if vsat is not None else '>3', 'V', rid)
        C(t, 300.0, 'as_simulated_300K', vg, 3.0, 'gd_output_conductance', gd3, 'S/um', rid)
        C(t, 300.0, 'as_simulated_300K', vg, 3.0, 'gd3_over_gd0', gd3 / g0, '-', rid)
        print(f'{t:>4} nm Vg {vg}: ' + ', '.join(f'Id({x})={d["Id"][x]:.4g}' for x in VDS) + f'; r(0.1/0.05)={I2/I1:.4f}; d2Id/dVd2(0)={2*b:.3g}; gd0={g0:.4g}; Vdsat10={fmt(vsat,"{:.2f}")}; gd(3V)={gd3:.3g} ({100*gd3/g0:.2f} % of gd0)')
out['idvd'] = {f'{k[0]}_{k[1]}': v for k, v in idvd.items()}
print('\nFilm ratios Id(t)/Id(2 nm):')
for t in [6.3, 13.2]:
    for vg in VGS_OUT:
        rr = {x: idvd[(t, vg)]['Id'][x] / idvd[(2.0, vg)]['Id'][x] for x in VDS}
        for x in VDS: C(t, 300.0, 'as_simulated_300K', vg, x, f'Id_ratio_{tag(t)}_over_2p0', rr[x], '-', f'{IDVD[t]}/{IDVD[2.0]}')
        print(f'{t} / 2.0 nm, Vg {vg}: ' + ', '.join(f'{x}: {rr[x]:.3f}' for x in VDS))
        out[f'ratio_{t}_{vg}'] = rr

# ------------------------------------------------------------------ temperature
print('\n=== Temperature predictions (Vd 0.7 V) ===')
curves = {}
for t in FILMS:
    rid, mu_run = REF[t]; vg, i = read_idvg(rid); sc = MU_PRED[t] / mu_run
    curves[(t, 300.0, 'ref')] = (vg, i * sc, f'{rid} x{sc:.6f}')
for (t, T), rid in TRUNS.items():
    vg, i = read_idvg(rid); f = (T / 300.0) ** 1.5
    curves[(t, T, 'P-phonon')] = (vg, i, rid); curves[(t, T, 'P-MTR')] = (vg, i * f, f'{rid} x(T/300)^1.5={f:.5f}')
M = {k: all_metrics(v[0], v[1], k[0]) for k, v in curves.items()}
temp = {}
for (t, T, var), m in M.items():
    if var == 'ref': continue
    r = M[(t, 300.0, 'ref')]
    d = dict(Vth_cc=m['V_1e-9'], dVth_cc_mV=1000 * (m['V_1e-9'] - r['V_1e-9']), dV1e7_mV=1000 * (m['V_1e-7'] - r['V_1e-7']), dV1e11_mV=1000 * (m['V_1e-11'] - r['V_1e-11']),
             SS_11_10=m['SS_11_10'], dSS_11_10=m['SS_11_10'] - r['SS_11_10'], SS_10_9=m['SS_10_9'], dSS_10_9=m['SS_10_9'] - r['SS_10_9'], SS_10_8=m['SS_10_8'], dSS_10_8=m['SS_10_8'] - r['SS_10_8'],
             Vth_lin=m['Vth_lin_V'], dVth_lin_mV=1000 * (m['Vth_lin_V'] - r['Vth_lin_V']), mu_FE=m['mu_FE_cm2Vs'], mu_FE_ratio=m['mu_FE_cm2Vs'] / r['mu_FE_cm2Vs'],
             Ion=m['Ion_A_per_um'], dIon_pct=100 * (m['Ion_A_per_um'] / r['Ion_A_per_um'] - 1), gap=m['gap_lin'], dgap_mV=1000 * (m['gap_lin'] - r['gap_lin']))
    temp[(t, T, var)] = d
    rid = curves[(t, T, var)][2]
    for q, u in [('Vth_cc', 'V'), ('dVth_cc_mV', 'mV'), ('SS_11_10', 'mV/dec'), ('dSS_11_10', 'mV/dec'), ('SS_10_9', 'mV/dec'), ('dSS_10_9', 'mV/dec'), ('SS_10_8', 'mV/dec'), ('dSS_10_8', 'mV/dec'),
                 ('Vth_lin', 'V'), ('dVth_lin_mV', 'mV'), ('mu_FE', 'cm2/Vs'), ('mu_FE_ratio', '-'), ('Ion', 'A/um'), ('dIon_pct', '%')]:
        C(t, T, var, '-' if q not in ('Ion', 'dIon_pct') else 3.0, 0.7, q, d[q], u, rid)
    print(f'{t:>4} nm {T} K {var:8s}: Vcc {d["Vth_cc"]:.4f} (d {d["dVth_cc_mV"]:+.1f} mV); dV(1e-11) {d["dV1e11_mV"]:+.1f}; dV(1e-7) {d["dV1e7_mV"]:+.1f}; SS 1e-11..1e-10 {d["SS_11_10"]:.1f} ({d["dSS_11_10"]:+.1f}); '
          f'1e-10..1e-9 {d["SS_10_9"]:.1f} ({d["dSS_10_9"]:+.1f}); SS_cc {d["SS_10_8"]:.1f} ({d["dSS_10_8"]:+.1f}); Vlin {d["Vth_lin"]:.3f} ({d["dVth_lin_mV"]:+.1f}); mu_FE {d["mu_FE"]:.3f} (x{d["mu_FE_ratio"]:.4f}); Ion {d["Ion"]:.4g} ({d["dIon_pct"]:+.2f} %)')
for (t, T, var), (vg, i, rid) in curves.items():
    for k, v in enumerate(vg):
        if v >= -1.0 and i[k] > 1e-16:
            C(t, T, 'reference_300K' if var == 'ref' else var, float(v), 0.7, 'Id', float(i[k]), 'A/um', rid)
    if var == 'ref':
        m = M[(t, T, var)]
        for q, key, u in [('Vth_cc', 'V_1e-9', 'V'), ('SS_11_10', 'SS_11_10', 'mV/dec'), ('SS_10_9', 'SS_10_9', 'mV/dec'), ('SS_10_8', 'SS_10_8', 'mV/dec'), ('Vth_lin', 'Vth_lin_V', 'V'), ('mu_FE', 'mu_FE_cm2Vs', 'cm2/Vs'), ('Ion', 'Ion_A_per_um', 'A/um')]:
            C(t, 300.0, 'reference_300K', 3.0 if q == 'Ion' else '-', 0.7, q, m[key], u, rid)
out['temp'] = {f'{k[0]}_{k[1]}_{k[2]}': v for k, v in temp.items()}
out['ref'] = {f'{t}': {k: M[(t, 300.0, 'ref')][k] for k in ['V_1e-9', 'SS_11_10', 'SS_10_9', 'SS_10_8', 'Vth_lin_V', 'mu_FE_cm2Vs', 'Ion_A_per_um', 'V_1e-7', 'V_1e-11']} for t in FILMS}

# mu_FE and Ion thickness ratios at 358 K
for var in ['P-phonon', 'P-MTR']:
    r300 = M[(13.2, 300.0, 'ref')]['mu_FE_cm2Vs'] / M[(2.0, 300.0, 'ref')]['mu_FE_cm2Vs']; r358 = M[(13.2, 358.15, var)]['mu_FE_cm2Vs'] / M[(2.0, 358.15, var)]['mu_FE_cm2Vs']
    i300 = M[(13.2, 300.0, 'ref')]['Ion_A_per_um'] / M[(2.0, 300.0, 'ref')]['Ion_A_per_um']; i358 = M[(13.2, 358.15, var)]['Ion_A_per_um'] / M[(2.0, 358.15, var)]['Ion_A_per_um']
    print(f'{var}: mu_FE(13.2)/mu_FE(2) 300 K {r300:.4f} -> 358 K {r358:.4f} ({100*(r358/r300-1):+.2f} %); Ion ratio {i300:.4f} -> {i358:.4f}')
    out[f'ratio_T_{var}'] = dict(mu300=r300, mu358=r358, ion300=i300, ion358=i358)
    C(13.2, 358.15, var, '-', 0.7, 'mu_FE_ratio_13p2_over_2p0', r358, '-', 'run_0047/run_0045'); C(13.2, 300.0, 'reference_300K', '-', 0.7, 'mu_FE_ratio_13p2_over_2p0', r300, '-', 'run_0040/run_0038')

# ------------------------------------------------------------------ activation energies
print('\n=== Apparent activation energy Ea(Vg) = -k dln(Id)/d(1/T) (meV), Vd 0.7 V ===')
ea = {}
def idat(key, v):
    vg, i, _ = curves[key]; return float(i[np.argmin(np.abs(vg - v))])
for t in FILMS:
    Ts = [300.0, 338.15, 358.15] if t == 2.0 else [300.0, 358.15]
    for var in ['P-phonon', 'P-MTR']:
        for v in VG_EA:
            I = [idat((t, 300.0, 'ref'), v)] + [idat((t, T, var), v) for T in Ts[1:]]
            if min(I) <= 1e-16: ea[(t, var, v)] = None; continue
            x = np.array([1 / (K_B * T) for T in Ts]); y = np.log(np.array(I))
            e_all = -np.polyfit(x, y, 1)[0] * 1000
            e_pair = [-(y[k + 1] - y[k]) / (x[k + 1] - x[k]) * 1000 for k in range(len(Ts) - 1)]
            ea[(t, var, v)] = dict(Ea_meV=float(e_all), pairs=[float(e) for e in e_pair], I=I, measurable=bool(I[0] > 5 * floor_med(t)))
            rid = '+'.join([curves[(t, 300.0, 'ref')][2]] + [curves[(t, T, var)][2] for T in Ts[1:]])
            C(t, '/'.join(f'{T:g}' for T in Ts), var, v, 0.7, 'Ea_apparent', float(e_all), 'meV', rid)
        print(f'{t:>4} nm {var:8s}: ' + '; '.join(f'Vg {v}: {ea[(t,var,v)]["Ea_meV"]:+.1f}' + (f' (pairs {", ".join(f"{e:+.1f}" for e in ea[(t,var,v)]["pairs"])})' if t == 2.0 else '') + ('' if ea[(t,var,v)]['measurable'] else ' [below 5x measured floor]') if ea[(t, var, v)] else f'Vg {v}: n/a' for v in VG_EA))
out['ea'] = {f'{k[0]}_{k[1]}_{k[2]}': v for k, v in ea.items()}

# ------------------------------------------------------------------ comparison with S2 analytic (350 K)
print('\n=== ATLAS P-MTR interpolated to 350 K vs S2 analytic MTR expectation ===')
s2 = {2.0: dict(dVcc=-64, mu=0.993, ion=1.004, dVlin=-15, ea={0.0: 504, 0.5: 120, 1.0: 56, 1.5: 23, 2.0: 7, 3.0: 1}),
      13.2: dict(dVcc=-66, mu=0.999, ion=1.011, dVlin=-24, ea={0.0: 156, 0.5: 61, 1.0: 20, 1.5: 8, 2.0: 4, 3.0: 2})}
cmp = {}
for t in [2.0, 13.2]:
    if t == 2.0: Ta, Tb = 338.15, 358.15; A = temp[(t, Ta, 'P-MTR')]; B = temp[(t, Tb, 'P-MTR')]
    else: Ta, Tb = 300.0, 358.15; A = dict(dVth_cc_mV=0.0, mu_FE_ratio=1.0, dIon_pct=0.0, dVth_lin_mV=0.0); B = temp[(t, Tb, 'P-MTR')]
    w = (350.0 - Ta) / (Tb - Ta); li = lambda k: A[k] + w * (B[k] - A[k])
    c = dict(dVcc=li('dVth_cc_mV'), mu=li('mu_FE_ratio'), ion=1 + li('dIon_pct') / 100, dVlin=li('dVth_lin_mV'))
    cmp[t] = c
    print(f'{t} nm @350 K (linear-in-T interpolation {Ta}-{Tb}): dVth_cc {c["dVcc"]:+.1f} mV (S2 {s2[t]["dVcc"]}); mu_FE x{c["mu"]:.4f} (S2 x{s2[t]["mu"]}); Ion x{c["ion"]:.4f} (S2 x{s2[t]["ion"]}); dVth_lin {c["dVlin"]:+.1f} mV (S2 {s2[t]["dVlin"]})')
    print('   Ea (ATLAS P-MTR, 300-358 K fit) vs S2 (300-350 K): ' + '; '.join(f'Vg {v}: {ea[(t,"P-MTR",v)]["Ea_meV"]:.0f} vs {s2[t]["ea"][v]}' for v in VG_EA if ea[(t, 'P-MTR', v)]))
out['s2_compare'] = cmp
json.dump(out, open(Path(__file__).with_name('s6_part3_out.json'), 'w'), indent=1, default=float)
json.dump(canon, open(Path(__file__).with_name('s6_canonical_rows.json'), 'w'), indent=0, default=float)
print('canonical rows:', len(canon))
