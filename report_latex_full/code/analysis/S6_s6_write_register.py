"""Writes analysis_2026-09-25/PREDICTIONS_REGISTER.md and predictions_canonical.csv from the part-3 outputs
(s6_part3_out.json, s6_canonical_rows.json). No simulator call; no package file is modified."""
import csv, hashlib, json, math
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from s6_lib import PKG, run_dir, meas, fmt

HERE = Path(__file__).resolve().parent; AN = HERE.parents[1] if HERE.name == 'S6' else None
AN = PKG / 'analysis_2026-09-25'
o = json.loads((HERE / 's6_part3_out.json').read_text()); canon = json.loads((HERE / 's6_canonical_rows.json').read_text())
FILMS = [2.0, 6.3, 13.2]; VGS = [1.0, 1.5, 2.0, 2.5, 3.0]; VDS = ['0.05', '0.1', '0.5', '1.0', '2.0', '3.0']
IDVD = {2.0: 'run_0041', 6.3: 'run_0042', 13.2: 'run_0043'}
VLIN300 = {t: o['ref'][f'{t}']['Vth_lin_V'] for t in FILMS}

# normalised output curves Id(Vd)/Id(Vd=0.7) (removes the 300 K transfer-calibration residual) -> canonical rows
for t in FILMS:
    rows = list(csv.DictReader((run_dir(IDVD[t]) / 'output_characteristics.csv').open()))
    for vg in VGS:
        pts = {round(float(r['vd_V']), 3): float(r['id_A_per_um']) for r in rows if abs(float(r['vg_V']) - vg) < 1e-9}
        for vd, i in sorted(pts.items()):
            if vd > 0: canon.append(dict(film=f'{t:g} nm', T_K=300.0, variant='as_simulated_300K', Vg=vg, Vd=vd, quantity='Id_over_Id_at_Vd0p7', value=i / pts[0.7], unit='-', run_id=IDVD[t]))
# calibration residual at Vd = 0.7 V (model / measured transfer curve at the same Vg) - context, not a prediction
calres = {}
for t in FILMS:
    vg, i = meas(t)
    for v in VGS:
        im = float(i[np.argmin(np.abs(vg - v))]); calres[(t, v)] = o['idvd'][f'{t}_{v}']['Id07'] / im

csv_path = AN / 'predictions_canonical.csv'
with csv_path.open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['film', 'T_K', 'variant', 'Vg', 'Vd', 'quantity', 'value', 'unit', 'run_id']); w.writeheader()
    for r in canon:
        r = dict(r); v = r['value']
        if isinstance(v, float): r['value'] = f'{v:.6g}'
        w.writerow(r)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files = ['data/experimental_clean.csv', 'scripts/extract_metrics.py', 'config/iwo_material_model.yaml', 'config/campaign_B_recal_predictions.json', 'results/campaigns/campaign_B_recal_predictions.json']
for rid in ['run_0038', 'run_0039', 'run_0040']:
    d = run_dir(rid).relative_to(PKG).as_posix(); files += [f'{d}/idvg.dat', f'{d}/execution.json', f'{d}/device.in']
for rid in ['run_0041', 'run_0042', 'run_0043']:
    d = run_dir(rid).relative_to(PKG).as_posix(); files += [f'{d}/output_characteristics.csv', f'{d}/execution.json', f'{d}/device.in']
for rid in ['run_0044', 'run_0045', 'run_0046', 'run_0047']:
    d = run_dir(rid).relative_to(PKG).as_posix(); files += [f'{d}/idvg.dat', f'{d}/execution.json', f'{d}/device.in', f'{d}/deckbuild.out']
files += ['analysis_2026-09-25/scratch/S6/s6_lib.py', 'analysis_2026-09-25/scratch/S6/s6_part3_predictions.py', 'analysis_2026-09-25/scratch/S6/s6_write_register.py',
          'analysis_2026-09-25/scratch/S6/s6_part3_out.txt', 'analysis_2026-09-25/predictions_canonical.csv']
hashes = [(p, sha(PKG / p)) for p in files]
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

L = []; A = L.append
A('# Prediction register: IWO V1 ATLAS model, ID-VD and elevated-temperature transfer predictions')
A('')
A(f'**Registered (UTC): {now}.** Registrant: specialist S6, analysis_2026-09-25 (no ATLAS launch by S6; every number below is read from the real ATLAS runs listed, or derived from them by the exact operations stated). '
  'None of the predicted quantities was used in calibration, and no measurement of them was in the project\'s possession at registration time. Januar et al. 2026 SI Fig. S12 (2 nm transfer curves at 65 and 85 C) exists but is NOT in the package; it is the first intended test.')
A('')
A('## 1. Model state that is being registered')
A('- Model V1 (`config/iwo_material_model.yaml`), physical structure, classical electrons-only drift-diffusion with Fermi statistics, acceptor tail NTA/WTA (WTA 0.040 eV), deep and interface Gaussians, fixed front charge Qf, uniform Nd_eff(t), confinement law dEc = 0.9205 t^-1.3815 eV, Nc(m*(t)), constant spatially uniform band mobility, ideal Ohmic Pd contacts, DOS levels 384/192.')
A('- Calibrated (300 K, Vd 0.7 V, one ID-VG per film): mu_band = 17.6897 (2 nm), 11.582 (6.3 nm), 61.6046 cm^2/Vs (13.2 nm); Qf = 1.73e12 cm^-2 (2 and 13.2 nm, shared) and 8.7e10 cm^-2 (6.3 nm, device-specific "tuned" configuration).')
A('- 300 K references: run_0038 (B1) x 17.6897/17.69 = x0.999983, run_0039 (B2) x 11.582/11.41 = x1.015074, run_0040 (B3) x 61.6046/60.39 = x1.020113 (exact: Id is linear in the uniform constant mobility; verified run_0029/run_0038 ratio 1.024879 vs 1.024873 expected over 43 points; ID-VD at Vd 0.7 V equals the rescaled transfer curves to <0.001 % at all 15 (film, Vg) points).')
A('- Temperature assumptions (campaign B plan): Nc, Nv proportional to T^1.5 (ATLAS); Eg T-independent (egalpha = 0); NTA/WTA, Dit, deep states, Qf, Nd_eff T-independent; tail occupancy at the lattice temperature (thermal equilibrium, isothermal, no self-heating).')
A('- Known calibration residuals the predictions inherit (final converged comparison, S6 report section 1): 2 nm gm_max -8.6 %, Vth_lin -0.127 V; 6.3 nm gm_max -23 %, Vth_lin -0.354 V (on-state shape NOT reproduced; the 6.3 nm predictions are lower-confidence); 13.2 nm gm_max -2.6 %.')
A('')
A('## 2. Temperature caveat (tmu) and the two registered variants')
A('ATLAS applied its silicon-default constant-mobility temperature exponent (printed "tmu = 1.5" in `run_0045/deckbuild.out`, REGIONAL MOBILITY MODEL SUMMARY, lines ~384-423: "mu = 12.977 @ 358 K, tmu = 1.5"), i.e. mu_band(T) = mu_band(300 K)(T/300)^-1.5, although the plan declared a T-independent band mobility. Because the mobility is uniform and constant, the current is exactly proportional to that factor, so two variants are exact:')
A('- **P-phonon** = as simulated (band mobility falls as T^-1.5).')
A('- **P-MTR** = simulated currents x (T/300)^+1.5 = x1.19665 (338.15 K) and x1.30426 (358.15 K): T-independent band mobility, multiple-trapping-and-release through the equilibrium tail only.')
A('The as-simulated runs must never be quoted as "T-independent mobility". A measured result between the variants is read through an effective exponent: mu_band proportional to T^-g with g = -ln(R_meas/R_MTR)/ln(T/300), where R is the measured and P-MTR-predicted ratio of the same current quantity (Ion or mu_FE) at T vs 300 K.')
A('')
A('## 3. Extraction definitions (apply identically to future measured curves)')
A('`scripts/extract_metrics.py` (unchanged) for Vth_cc (Id = 1e-9 A/um, log-linear), Vth_lin (secant gm on the 0.05 V grid, linear extrapolation at gm_max), mu_FE = gm_max L/(W Cox Vd) (L 20 um, Cox 8.955e-7 F/cm^2, Vd 0.7 V), Ion = Id(3 V). Simulated curves are first interpolated (np.interp) from the native grid (0.05 V for -1..1.5 V, 0.1 V above) onto the 0.05 V measurement grid, as in `scripts/run_atlas.py`. Added fixed-current metrics (S6): V(I) = Vg at Id = I (log-linear), SS(I1..I2) = [V(I2)-V(I1)]/log10(I2/I1) for 1e-11..1e-10, 1e-10..1e-9 and 1e-10..1e-8 A/um. SS_min is NOT registered (window-phase artefact, S6 report 1.4). Ea(Vg) = -k_B dln(Id)/d(1/T) at fixed Vg and Vd 0.7 V (least squares over the available temperatures). **The primary registered quantities are the changes (dVth, dSS, ratios, Ea), to be compared with changes measured on the same device relative to its own 300 K curve**; absolute values carry the 300 K calibration residual.')
A('')
A('## 4. ID-VD predictions (300 K; runs B8 run_0041, B9 run_0042, B10 run_0043; Vd 0-0.5 V in 0.05 V steps, 0.5-3 V in 0.1 V steps)')
A('')
A('### 4.1 Drain current (A/um)')
A('| film | Vg (V) | Id @0.05 | Id @0.1 | Id @0.5 | Id @1 | Id @2 | Id @3 V | Id @0.7 (= calibrated transfer) | model/measured at Vd 0.7 (calibration residual, context) |')
A('|---|---|---|---|---|---|---|---|---|---|')
for t in FILMS:
    for vg in VGS:
        d = o['idvd'][f'{t}_{vg}']; I = d['Id']
        A(f'| {t:g} nm | {vg:g} | ' + ' | '.join(f'{I[k]:.4g}' for k in VDS) + f' | {d["Id07"]:.4g} | {calres[(t, vg)]:.3f} |')
A('')
A('### 4.2 Output-curve shape (the genuine prediction content: normalised to the calibrated Vd = 0.7 V point)')
A('| film | Vg | Vg - Vth_lin(300 K model) (V) | Id(0.1)/Id(0.05) | d2Id/dVd2 at Vd->0 (A/um/V^2) | gd0 (S/um, quadratic fit 0-0.1 V) | Vd_sat: gd = 10 % of gd0 (V) | gd at Vd 3 V (S/um) | gd(3 V)/gd0 | Id(3)/Id(0.7) | Id(0.1)/Id(0.7) |')
A('|---|---|---|---|---|---|---|---|---|---|---|')
for t in FILMS:
    for vg in VGS:
        d = o['idvd'][f'{t}_{vg}']; I = d['Id']
        A(f'| {t:g} nm | {vg:g} | {vg - VLIN300[t]:+.2f} | {d["r_lin"]:.4f} | {2*d["curv_b"]:.3g} | {d["gd0"]:.4g} | {fmt(d["vdsat10"], "{:.2f}")} | {d["gd3"]:.3g} | {100*d["gd3_over_gd0"]:.2f} % | {I["3.0"]/d["Id07"]:.4f} | {I["0.1"]/d["Id07"]:.4f} |')
A('')
A('Gradual-channel reference: Id(0.1)/Id(0.05) = 2 x [1 - 0.05/Vov]/[1 - 0.025/Vov] < 2 for an Ohmic contact (Vov = effective overdrive); every registered value is 1.80-1.98 with negative low-Vd curvature (no S-shape). Output conductance at 3 V is 0.01-0.68 % of gd0 (L = 20 um, no channel-length modulation, no parallel path in the model).')
A('')
A('### 4.3 Film ratios Id(t)/Id(2 nm) at equal Vg and Vd')
A('| ratio | Vg | Vd 0.05 | 0.1 | 0.5 | 1 | 2 | 3 V |')
A('|---|---|---|---|---|---|---|---|')
for t in [6.3, 13.2]:
    for vg in VGS:
        rr = o[f'ratio_{t}_{vg}']
        A(f'| {t:g}/2 nm | {vg:g} | ' + ' | '.join(f'{rr[k]:.3f}' for k in VDS) + ' |')
A('')
A('## 5. Elevated-temperature transfer predictions (Vd 0.7 V; B11 run_0044 338.15 K 2 nm; B12 run_0045, B13 run_0046, B14 run_0047 at 358.15 K)')
A('')
A('### 5.1 300 K references (rescaled B1/B2/B3)')
A('| film | Vth_cc (V) | V(1e-11) (V) | V(1e-7) (V) | SS 1e-11..1e-10 | SS 1e-10..1e-9 | SS 1e-10..1e-8 (mV/dec) | Vth_lin (V) | mu_FE (cm^2/Vs) | Ion (A/um) |')
A('|---|---|---|---|---|---|---|---|---|---|')
for t in FILMS:
    r = o['ref'][f'{t}']
    A(f'| {t:g} nm | {r["V_1e-9"]:.4f} | {r["V_1e-11"]:.4f} | {r["V_1e-7"]:.4f} | {r["SS_11_10"]:.1f} | {r["SS_10_9"]:.1f} | {r["SS_10_8"]:.1f} | {r["Vth_lin_V"]:.4f} | {r["mu_FE_cm2Vs"]:.3f} | {r["Ion_A_per_um"]:.4g} |')
A('')
A('### 5.2 Changes relative to 300 K')
A('| film | T (K) | variant | Vth_cc (V) | dVth_cc (mV) | dV(1e-11) (mV) | dV(1e-7) (mV) | SS 1e-11..1e-10 (d) | SS 1e-10..1e-9 (d) | SS 1e-10..1e-8 (d) | dVth_lin (mV) | mu_FE (ratio) | Ion (A/um) | dIon (%) |')
A('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for key in ['2.0_338.15', '2.0_358.15', '6.3_358.15', '13.2_358.15']:
    for var in ['P-phonon', 'P-MTR']:
        d = o['temp'][f'{key}_{var}']; t, T = key.split('_')
        A(f'| {float(t):g} nm | {T} | {var} | {d["Vth_cc"]:.4f} | {d["dVth_cc_mV"]:+.1f} | {d["dV1e11_mV"]:+.1f} | {d["dV1e7_mV"]:+.1f} | {d["SS_11_10"]:.1f} ({d["dSS_11_10"]:+.1f}) | {d["SS_10_9"]:.1f} ({d["dSS_10_9"]:+.1f}) | {d["SS_10_8"]:.1f} ({d["dSS_10_8"]:+.1f}) | {d["dVth_lin_mV"]:+.1f} | {d["mu_FE"]:.3f} (x{d["mu_FE_ratio"]:.4f}) | {d["Ion"]:.4g} | {d["dIon_pct"]:+.2f} |')
A('')
rp, rm = o['ratio_T_P-phonon'], o['ratio_T_P-MTR']
A(f'Thickness ratio mu_FE(13.2)/mu_FE(2): {rp["mu300"]:.3f} (300 K) -> {rm["mu358"]:.3f} (358.15 K) in both variants (+{100*(rm["mu358"]/rm["mu300"]-1):.1f} %); Ion(13.2)/Ion(2): {rp["ion300"]:.3f} -> {rp["ion358"]:.3f}. The tmu factor is common to all films, so the ratios are variant-independent.')
A('')
A('### 5.3 Apparent activation energy of Id at fixed Vg (meV; Vd 0.7 V; 2 nm fit over 300/338.15/358.15 K with the two pair values in brackets, 6.3 and 13.2 nm over 300/358.15 K)')
A('| film | variant | Vg 0 | 0.5 | 1.0 | 1.5 | 2.0 | 3.0 V |')
A('|---|---|---|---|---|---|---|---|')
for t in FILMS:
    for var in ['P-phonon', 'P-MTR']:
        cells = []
        for v in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]:
            e = o['ea'][f'{t}_{var}_{v}']
            if not e: cells.append('n/a (Id < 1e-16)'); continue
            s = f'{e["Ea_meV"]:+.1f}' + (f' ({e["pairs"][0]:+.1f}, {e["pairs"][1]:+.1f})' if t == 2.0 else '') + ('' if e['measurable'] else ' *')
            cells.append(s)
        A(f'| {t:g} nm | {var} | ' + ' | '.join(cells) + ' |')
A('')
A('\\* below 5x the measured 300 K off-floor of that film: not measurable on the existing devices. The P-MTR minus P-phonon difference is the tmu term, +1.5 k_B T_eff = +42.3 meV for 300-358.15 K, at every Vg.')
A('')
A('### 5.4 Cross-check against the pre-registered analytic MTR expectation (S2 section 4, 1-D surrogate, 300 -> 350 K, T-independent mu)')
s2 = {2.0: dict(dVcc=-64, mu=0.993, ion=1.004, dVlin=-15), 13.2: dict(dVcc=-66, mu=0.999, ion=1.011, dVlin=-24)}
A('| film | quantity at 350 K | S2 surrogate (registered 2026-09-24T18:57Z) | ATLAS P-MTR (interpolated linearly in T) | difference |')
A('|---|---|---|---|---|')
for t in [2.0, 13.2]:
    c = o['s2_compare'][f'{t}']
    A(f'| {t:g} nm | dVth_cc (mV) | {s2[t]["dVcc"]} | {c["dVcc"]:+.1f} | {c["dVcc"]-s2[t]["dVcc"]:+.1f} |')
    A(f'| {t:g} nm | mu_FE ratio | {s2[t]["mu"]} | {c["mu"]:.4f} | {c["mu"]-s2[t]["mu"]:+.4f} |')
    A(f'| {t:g} nm | Ion ratio | {s2[t]["ion"]} | {c["ion"]:.4f} | {c["ion"]-s2[t]["ion"]:+.4f} |')
    A(f'| {t:g} nm | dVth_lin (mV) | {s2[t]["dVlin"]} | {c["dVlin"]:+.1f} | {c["dVlin"]-s2[t]["dVlin"]:+.1f} |')
A('Ea (P-MTR, 300-358 K fit) vs S2 (300-350 K): 2 nm 124/57/23/8/2 vs 120/56/23/7/1 meV at Vg 0.5/1/1.5/2/3 V; 13.2 nm 163/63/21/8/5/2 vs 156/61/20/8/4/2 meV at Vg 0/0.5/1/1.5/2/3 V. This is a model-vs-surrogate consistency test (numerical), not an experimental validation.')
A('')
A('## 6. What each outcome would falsify')
A('| registered prediction | model value(s) | measured outcome that falsifies | assumption falsified |')
A('|---|---|---|---|')
A('| Low-Vd linearity, all films and Vg | Id(0.1)/Id(0.05) = 1.80-1.98; d2Id/dVd2 < 0 at Vd -> 0 | ratio > 2.0 or upward (S-shaped) curvature below ~0.2 V, in particular at 2 nm only | ideal Ohmic Pd/IWO injection (S5 M2: confinement-raised barrier); also the mu_band = intrinsic lumping |')
n01 = ' / '.join(f'{o["idvd"][f"{t}_3.0"]["Id"]["0.1"] / o["idvd"][f"{t}_3.0"]["Id07"]:.3f}' for t in FILMS)
A(f'| Normalised output Id(0.1)/Id(0.7) at Vg 3 V | {n01} (2 / 6.3 / 13.2 nm) | measured value lower by more than the repeatability, growing with Id | negligible Rsd (series resistance compresses the low-Vd end); thickness ordering of the deficit identifies which film carries Rc |')
A('| Saturation | Vd_sat(10 %) 0.43-1.80 V (2 nm), 0.44-1.90 (6.3), 0.68-2.30 (13.2) for Vg 1-3 V | quasi-saturation well below these (> ~0.3 V lower) | constant mobility and zero Rsd (field-dependent mobility or Rsd) |')
A('| Output conductance at Vd 3 V | 0.01-0.19 % of gd0 (2, 6.3 nm), 0.03-0.68 % (13.2 nm) | several % of gd0, or rising with t | no parallel/ungated path, long-channel electrostatics (S4 floor path; back-channel conduction) |')
A('| Film ratios at low Vd | Id(13.2)/Id(2) at Vd 0.1 V = 26.5 / 10.8 / 7.44 / 6.29 / 5.75 (Vg 1-3 V) | low-Vd ratio differing from the Vd 0.7 V ratio beyond the predicted Vd dependence | thickness-independent (zero) contact resistance |')
A('| On-current vs T (2 nm, 358 K) | P-MTR +0.99 %, P-phonon -22.6 % (mu_FE x0.992 / x0.760) | dIon > ~+5 % (g < -0.2) | T-independent or phonon-like band mobility: activated band mobility / percolation (S2 4b predicts mu x1.03-1.39) |')
A('| On-current vs T | as above | dIon near -22 % (g ~ +1.5) | T-independent band mobility (band-like phonon-limited transport instead) |')
A('| Thickness ratio mu_FE(13.2)/mu_FE(2) | 4.40 -> 4.44 at 358 K (both variants) | shrinks toward ~3.3 (or 2.7-3.3) | common band-transport mechanism in all films (S2: barrier-limited thin films, phonon-limited 13.2 nm) |')
A('| dVth_cc at 358 K | P-MTR -73 / -79 / -76 mV; P-phonon -41 / -47 / -57 mV (2 / 6.3 / 13.2 nm); dVth_lin -27 / -35 / -30 mV in both | at 358 K, outside the -35 ... -85 mV envelope of the two variants beyond the (NOT DETERMINED, to be measured) repeatability, or a thickness spread >> 20 mV | equilibrium tail filling as the only T-dependent charge (e.g. thermally ionized V_O donors, T-dependent Qf, hysteresis) |')
A('| dVth_cc at 338 K (2 nm) | P-MTR -49 mV; P-phonon -28 mV | as above | as above |')
A('| Subthreshold Ea at fixed Vg | P-MTR 124 / 128 / 63 meV at 0.5 V; 57 / 53 / 21 meV at 1 V (2 / 6.3 / 13.2 nm) | ordering Ea(2) ~ Ea(6.3) > Ea(13.2) violated beyond ~10 meV | tail/EF alignment (Vth) ordering of the model; a different EF-Ec at the 6.3 nm film |')
A('| On-state Ea (Vg 3 V) | P-MTR +1.5 / +3.5 / +2.4 meV; P-phonon -40.6 / -38.8 / -39.9 meV | thin-film Ea(3 V) exceeding the 13.2 nm value by > ~10 meV | thickness-independent transport mechanism (structural/percolation step, S2) |')
A('| SS at fixed current, 358 K | P-MTR: SS 1e-10..1e-9 -12.1 / -12.5 / -10.6 mV/dec; P-phonon +2.0 / +2.4 / -3.3 | increase > ~20 mV/dec | T-independent tail (WTA) and Dit; thermal-equilibrium trapping |')
A('')
A('## 7. Numerical uncertainty of the registered numbers')
A('- Id, Ion, mu_FE ratios: DOS residual beyond 384/192 +0.16 % at 2 nm (Richardson, observed order 2.0 from runs 0012/0019/0029), smaller for 6.3/13.2 nm (offsets scale ~Nt); mesh x0.7 <= 0.013 % (runs 0036, 0028); linear rescale exact to 1e-5. DOS convergence was verified at 300 K only (not at 338/358 K).')
A('- Vth_cc, V(I): +/-1 mV (DOS residual < 0.5 mV, mesh 0.3-0.4 mV, log-linear vs PCHIP interpolation <= 1.5 mV). Fixed-current SS: +/-1 mV/dec. Vth_lin: grid-limited, -5 to -12 mV bias of the simulation grid relative to a 0.05 V measurement (0.1 V solver steps above 1.5 V); gm_max: -0.4 to -0.7 %.')
A('- Ea: < 0.5 meV (numerical); ID-VD: Vd_sat +/-0.05 V (0.1 V grid); gd(3 V) at Vg 1 V is set by current differences of ~5e-13 A/um per 0.1 V and carries up to ~5 % numerical uncertainty (KCL residual up to 1e-14 A in runs 0041/0042).')
A('- Physical/model-form uncertainty is NOT included in these numbers (S6 report sections 3-4).')
A('')
A('## 8. Run IDs')
A('300 K references: run_0038 (B1, 2 nm), run_0039 (B2, 6.3 nm tuned), run_0040 (B3, 13.2 nm). ID-VD: run_0041 (B8), run_0042 (B9), run_0043 (B10). Elevated T: run_0044 (B11, 2 nm, 338.15 K), run_0045 (B12, 2 nm, 358.15 K), run_0046 (B13, 6.3 nm, 358.15 K), run_0047 (B14, 13.2 nm, 358.15 K). Linearity check: run_0029 vs run_0038. All launches are logged in `results/RUN_INDEX.csv` (finish rows 2026-09-24T19:28:46Z to 21:54:12Z).')
A('')
A('## 9. Canonical machine-readable file')
A(f'`analysis_2026-09-25/predictions_canonical.csv` ({len(canon)} rows; columns film, T_K, variant, Vg, Vd, quantity, value, unit, run_id). Variants: as_simulated_300K (ID-VD), reference_300K, P-phonon, P-MTR. It holds every ID-VD point (Vd > 0), the normalised output curves, the derived output metrics, the full predicted transfer curves (Vg >= -1 V, Id > 1e-16 A/um) for every film, temperature and variant, the metric changes and the Ea values.')
A('')
A('## 10. Source files and SHA-256 (computed with Python hashlib at registration)')
A('| file (relative to the package root) | SHA-256 |')
A('|---|---|')
for p, h in hashes: A(f'| `{p}` | `{h}` |')
A('')
A('Any later change to these files, to the extraction definitions or to the model state invalidates the prospective status of this register; a revised register must be a new, separately timestamped file.')
(AN / 'PREDICTIONS_REGISTER.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('written', now, len(canon), 'rows'); print('\n'.join(f'{p} {h}' for p, h in hashes))
