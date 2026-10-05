"""Model V2, step T0 (no ATLAS launch), 2026-10-06.

(a) Off-current floors: what conductance would a gate-independent (ungated) strip of each film have, computed from
    the model's own V1 donor, trap and mobility values, and does its thickness scaling match the measured floors?
(b) DFT -> TCAD: the V1 thickness laws for the conduction-band shift dEc(t) and the mass m*(t) are replaced by laws
    through our own DFT points (qe_workflow RESULTS_LOG). Because every trap level in the decks is referenced to Ec
    and the source/drain are ideal Ohmic contacts, a change of the electron affinity moves the whole transfer curve
    rigidly along Vg by exactly the change of dEc; a change of Qf is also an exact rigid shift (verified to 1 mV,
    EVIDENCE_BRIEF sec. 4); Id is exactly linear in a uniform constant mobility. The V2 curves therefore follow from
    the calibrated V1 runs by exact transformations, and the outcome of the pre-registered 6.3 nm test is computed
    here BEFORE any launch (T3 then checks it in ATLAS).
Outputs: t0_results.json and printed tables (copied into T0_PRECHECKS.md).
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'scripts'))
from extract_metrics import metrics  # noqa: E402  (the package's own metric definitions)
from material_laws import nc_3d      # noqa: E402

KT = 8.617333262e-5 * 300.0
Q = 1.602176634e-19
COX = 8.955369814335959e-07          # F/cm^2 (DEVICE_STRUCTURE.md)
CQ = COX / Q                          # 5.59e12 cm^-2 V^-1
VD = 0.7
FILMS = [2.0, 6.3, 13.2]
RUNS = {2.0: 'run_0038', 6.3: 'run_0039', 13.2: 'run_0040'}
MU_RUN = {2.0: 17.69, 6.3: 11.41, 13.2: 60.39}            # mu_band used in those runs (campaign B)
MU_CAL = {2.0: 17.69, 6.3: 11.581987, 13.2: 61.604561}    # recalibrated mu_band (make_figures.py:18)
QF_RUN = {2.0: 1.73e12, 6.3: 8.7e10, 13.2: 1.73e12}       # 6.3 nm run_0039 is the TUNED configuration
QF_V1 = 1.73e12

# ------------------------------------------------------------------ V1 laws (config/iwo_material_model.yaml)
V1 = dict(a=0.9205, p=1.3815, b=0.1311, q=1.4121)
dEc_v1 = lambda t: V1['a'] * t ** -V1['p']                  # dEc = dEg (partition 1.0)
mstar_v1 = lambda t: 0.208 + V1['b'] * t ** -V1['q']
Nt = lambda t: 2.0e19 * (2.0 / t) ** 0.75
Nd = lambda t, tc=20.0: 2.5e17 * (1 + (t / tc) ** 4)
rough = lambda t: (1 - 0.287 / t) ** 2
WTA = 0.040

# ------------------------------------------------------------------ DFT points (qe_workflow/cern_htcondor/results/RESULTS_LOG.md)
# dEc relative to bulk, PBE: 1.98 nm two-step alignment with the a/2 window (+0.281; double average +0.287);
# 0.95 nm = 2 nm value + same-termination EA difference (+0.567) = +0.848 (the 'recommended' 1 nm value).
DFT = {'dEc': {0.95: 0.848, 1.98: 0.281}, 'dEg': {0.95: 0.900, 1.98: 0.335},
       'mstar': {'bulk': 0.159, 0.95: 0.281, 1.98: 0.20615}, 'hse_over_pbe': (1.06, 1.11)}


def power_through(p1, p2):
    (t1, y1), (t2, y2) = p1, p2
    p = math.log(y1 / y2) / math.log(t2 / t1)
    return y1 * t1 ** p, p


a_c, p_c = power_through((0.95, DFT['dEc'][0.95]), (1.98, DFT['dEc'][1.98]))
a_g, p_g = power_through((0.95, DFT['dEg'][0.95]), (1.98, DFT['dEg'][1.98]))
b_m, q_m = power_through((0.95, DFT['mstar'][0.95] - DFT['mstar']['bulk']), (1.98, DFT['mstar'][1.98] - DFT['mstar']['bulk']))
dEc_v2 = lambda t: a_c * t ** -p_c
dEg_v2 = lambda t: a_g * t ** -p_g
mstar_v2 = lambda t: 0.208 + b_m * t ** -q_m

# measured m* sensitivity of Vth_cc (isolation runs 0050/0051: m* x1.3 -> -0.043 V at 2 nm, -0.028 V at 13.2 nm)
S_M = {2.0: -0.043, 13.2: -0.028}
s_m = lambda t: np.interp(math.log(t), [math.log(2.0), math.log(13.2)], [S_M[2.0], S_M[13.2]])
dv_mass = lambda t: s_m(t) * math.log(mstar_v2(t) / mstar_v1(t)) / math.log(1.3)


# ------------------------------------------------------------------ helpers: curves, shifts, metrics
def run_dir(t):
    return next((PKG / 'results' / 'runs').glob(RUNS[t] + '_*'))


def measured(t):
    rows = [r for r in csv.DictReader((PKG / 'data' / 'experimental_clean.csv').open()) if abs(float(r['thickness_nm']) - t) < 1e-6]
    return np.array([float(r['vg_V']) for r in rows]), np.array([float(r['id_A_per_um']) for r in rows])


def native(t):
    rows = list(csv.DictReader((run_dir(t) / 'terminal_currents.csv').open()))
    return np.array([float(r['vg_V']) for r in rows]), np.array([float(r['id_A_per_um']) for r in rows])


def transform(t, dv, mu_new, vg_out):
    """ATLAS curve of the run, shifted right by dv (V) and scaled to mu_new; log-linear interpolation."""
    vg, i = native(t)
    li = np.log10(np.clip(i, 1e-40, None))
    x = np.clip(vg_out - dv, vg[0], vg[-1])
    return (mu_new / MU_RUN[t]) * 10 ** np.interp(x, vg, li)


def score(t, isim):
    vg, im = measured(t)
    floor = np.median(im[(vg >= -2) & (vg <= -0.5)])
    act = im > 5 * floor
    res = np.log10(np.clip(isim, 1e-40, None) / im)
    m = metrics(vg, isim, True, t)
    return {'rmse_active_dec': float(np.sqrt(np.mean(res[act] ** 2))), 'Vth_cc': m['Vth_cc_1e-9_V'], 'Vth_lin': m['Vth_lin_V'],
            'SS_cc': m['SS_cc_1e-10_1e-8_mV_dec'], 'Ion': m['Ion_A_per_um'], 'mu_FE': m['mu_FE_cm2Vs']}


def meas_metrics(t):
    vg, im = measured(t)
    m = metrics(vg, im, False, t)
    return {'Vth_cc': m['Vth_cc_1e-9_V'], 'Vth_lin': m['Vth_lin_V'], 'SS_cc': m['SS_cc_1e-10_1e-8_mV_dec'], 'Ion': m['Ion_A_per_um'],
            'mu_FE': m['mu_FE_cm2Vs']}


# ------------------------------------------------------------------ (a) off-current screen
E = np.arange(-3.5, 1.0, 0.0005)            # energy relative to Ec (eV)
X = np.arange(0.0, 60.0, 0.005)


def fermi(e, ef):
    return 1.0 / (1.0 + np.exp(np.clip((e - ef) / KT, -700, 700)))


def free_n(ef, nc):
    eta = ef / KT
    return nc * 2 / math.sqrt(math.pi) * np.trapezoid(np.sqrt(X) / (1 + np.exp(np.clip(X - eta, -700, 700))), X)


G_TAIL = lambda t: (Nt(t) / WTA) * np.exp(np.minimum(E, 0) / WTA) * (E <= 0)
G_DEEP = 5e16 * np.exp(-((E + 0.6) / 0.15) ** 2)                        # NGA cm^-3/eV, EGA 0.6, WGA 0.15
G_IT = 1.16757e19 * 2.5e-8 * np.exp(-((E + 0.301554) / 0.123975) ** 2)  # deck region-2 sheet (cm^-2/eV)


def neutral_ef(t, case, it_scale=1.0, nd_scale=1.0, mstar=None):
    nc = nc_3d(mstar(t) if mstar else mstar_v1(t))
    tc = t * 1e-7

    def excess(ef):
        f = fermi(E, ef)
        neg = (free_n(ef, nc) + np.trapezoid(G_TAIL(t) * f, E) + np.trapezoid(G_DEEP * f, E)) * tc
        if case in ('D', 'Q'):
            neg += it_scale * np.trapezoid(G_IT * f, E)
        pos = nd_scale * Nd(t) * tc + (QF_V1 if case == 'Q' else 0.0)
        return neg - pos

    lo, hi = -2.5, 0.5
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if excess(mid) > 0 else (mid, hi)
    ef = 0.5 * (lo + hi)
    return ef, free_n(ef, nc)


def floor_screen():
    meas = {}
    for t in FILMS:
        vg, im = measured(t)
        meas[t] = float(np.median(im[(vg >= -2) & (vg <= -0.5)]))
    out = {'measured_floor_A_per_um': meas, 'cases': {}}
    for case, label in (('N', 'film neutral, no surface charge'), ('D', 'plus the V1 interface acceptor sheet'),
                        ('Q', 'plus the V1 interface sheet and Qf 1.73e12 (same bottom interface as the channel)')):
        rows = {}
        for t in FILMS:
            ef, n = neutral_ef(t, case)
            mu0 = MU_CAL[t] * rough(t)
            rows[t] = {'EF_minus_Ec_eV': ef, 'n_free_cm3': n, 'mu0': mu0, 'sheet_conductance_S': Q * n * mu0 * t * 1e-7}
        g13 = rows[13.2]['sheet_conductance_S']
        geo = meas[13.2] / VD / g13          # (W/L) per um of device width that reproduces the 13.2 nm floor
        for t in FILMS:
            rows[t]['predicted_floor_A_per_um'] = rows[t]['sheet_conductance_S'] * geo * VD
            rows[t]['predicted_over_measured'] = rows[t]['predicted_floor_A_per_um'] / meas[t]
        out['cases'][case] = {'label': label, 'films': rows, 'W_over_L_per_um_width': geo,
                              'exponent_2_to_13p2': math.log(g13 / rows[2.0]['sheet_conductance_S']) / math.log(6.6)}
    # fragility of case D: the interface acceptor sheet (ASSUMED) and Nd0 (FITTED, weakly constrained by the transfer
    # curves) scaled one at a time; (W/L) re-fitted on 13.2 nm each time; also case D with the V2 (DFT) mass law
    sens = {}
    for name, kw in (('Dit x0.5', dict(it_scale=0.5)), ('Dit x2', dict(it_scale=2.0)), ('Nd0 x0.5', dict(nd_scale=0.5)),
                     ('Nd0 x2', dict(nd_scale=2.0)), ('V2 mass law', dict(mstar=mstar_v2))):
        sig = {}
        for t in FILMS:
            ef, n = neutral_ef(t, 'D', **kw)
            sig[t] = Q * n * MU_CAL[t] * rough(t) * t * 1e-7
        geo = meas[13.2] / VD / sig[13.2]
        sens[name] = {t: sig[t] * geo * VD / meas[t] for t in (2.0, 6.3)}
    out['case_D_sensitivity_pred_over_meas'] = sens
    ex = math.log(meas[13.2] / meas[2.0]) / math.log(6.6)
    out['measured_exponent_2_to_13p2'] = ex
    out['empirical_power_law'] = {'exponent': ex, 'loo_6p3_predicted': meas[2.0] * (6.3 / 2) ** ex,
                                  'loo_6p3_ratio': meas[2.0] * (6.3 / 2) ** ex / meas[6.3]}
    return out


# ------------------------------------------------------------------ (b) DFT swap: exact transformations
def dft_swap():
    tab = {}
    for t in FILMS + [0.95, 0.75, 0.51]:
        tab[t] = {'dEc_V1': dEc_v1(t), 'dEc_V2': dEc_v2(t), 'mstar_V1': mstar_v1(t), 'mstar_V2': mstar_v2(t),
                  'Nc_V1': nc_3d(mstar_v1(t)), 'Nc_V2': nc_3d(mstar_v2(t))}
    # rigid shift of each curve when only the laws change (curve moves right by dEc change, + mass term)
    shift = {t: (dEc_v2(t) - dEc_v1(t)) + dv_mass(t) for t in FILMS}
    # V2 calibration = V1 protocol: ONE shared Qf (least squares on the active log-RMSE of the 2 and 13.2 nm
    # anchors) and mu_band per anchor from Ion (exact). Scan the shared Qf shift.
    best = None
    for dvq in np.arange(-0.02, 0.12, 0.0005):
        tot = 0.0
        for t in (2.0, 13.2):
            vg, im = measured(t)
            cur = transform(t, shift[t] + dvq, MU_RUN[t], vg)
            mu = MU_RUN[t] * im[-1] / cur[-1]
            tot += score(t, cur * mu / MU_RUN[t])['rmse_active_dec'] ** 2
        if best is None or tot < best[0]:
            best = (tot, dvq)
    dvq = float(best[1])
    qf_v2 = QF_V1 - dvq * CQ
    res = {'laws': {'dEc_V2': f'{a_c:.5f} t^-{p_c:.5f}', 'dEg_V2': f'{a_g:.5f} t^-{p_g:.5f}', 'mstar_V2': f'0.208 + {b_m:.5f} t^-{q_m:.5f}'},
           'table': tab, 'rigid_shift_from_laws_V': shift, 'shared_Qf_shift_V': dvq, 'Qf_V2_cm2': qf_v2, 'films': {}}
    mu_v2 = {}
    for t in (2.0, 13.2):
        vg, im = measured(t)
        v1 = score(t, transform(t, 0.0, MU_CAL[t], vg))
        cur = transform(t, shift[t] + dvq, MU_RUN[t], vg)
        mu_v2[t] = MU_RUN[t] * im[-1] / cur[-1]
        res['films'][t] = {'role': 'anchor', 'V1': v1, 'V2': score(t, transform(t, shift[t] + dvq, mu_v2[t], vg)),
                           'mu_band_V2': mu_v2[t], 'measured': meas_metrics(t)}
    # 6.3 nm pre-registered prediction: start from run_0039 (tuned Qf 8.7e10) and move it to the shared V1 Qf
    # (exact), then apply the V2 law shift and the V2 Qf; mobility: P = power law through the V2 anchors, E = Ion-normalized
    t = 6.3
    vg, im = measured(t)
    dv_v1 = -(QF_V1 - QF_RUN[t]) / CQ
    n_mu = math.log(mu_v2[13.2] / mu_v2[2.0]) / math.log(13.2 / 2.0)
    mu_p = mu_v2[2.0] * (t / 2.0) ** n_mu
    v1_shared = transform(t, dv_v1, MU_CAL[t], vg)
    cur_p = transform(t, dv_v1 + shift[t] + dvq, mu_p, vg)
    mu_e = mu_p * im[-1] / cur_p[-1]
    res['films'][t] = {'role': 'held-out prediction', 'V1_shared_Qf_muCal': score(t, v1_shared),
                       'V2_P_mu_powerlaw': score(t, cur_p), 'V2_E_mu_Ion_normalized': score(t, cur_p * mu_e / mu_p),
                       'mu_P': mu_p, 'mu_E': mu_e, 'mu_powerlaw_exponent': n_mu, 'measured': meas_metrics(t),
                       'shift_components_V': {'tuned->shared Qf (V1)': dv_v1, 'laws': shift[t], 'V2 Qf': dvq}}
    return res


def main():
    out = {'floor_screen': floor_screen(), 'dft_swap': dft_swap()}
    (Path(__file__).parent / 't0_results.json').write_text(json.dumps(out, indent=1, default=float))
    fs = out['floor_screen']
    print('== (a) floors: measured', {t: f'{v:.3e}' for t, v in fs['measured_floor_A_per_um'].items()},
          f"exponent 2->13.2: {fs['measured_exponent_2_to_13p2']:.3f}")
    for c, d in fs['cases'].items():
        print(f"  case {c} ({d['label']}): exponent {d['exponent_2_to_13p2']:.2f}; (W/L)/um {d['W_over_L_per_um_width']:.3e}")
        for t, r in d['films'].items():
            print(f"    {t:5} nm  EF-Ec {r['EF_minus_Ec_eV']:+.3f} eV  n {r['n_free_cm3']:.2e}  mu0 {r['mu0']:.2f}  "
                  f"pred floor {r['predicted_floor_A_per_um']:.2e}  pred/meas {r['predicted_over_measured']:.2f}")
    for k, v in fs['case_D_sensitivity_pred_over_meas'].items():
        print(f"  case D, {k:12}: pred/meas 2 nm {v[2.0]:.2f}, 6.3 nm {v[6.3]:.2f}")
    e = fs['empirical_power_law']
    print(f"  empirical t^{e['exponent']:.3f} through 2 & 13.2 nm: 6.3 nm predicted {e['loo_6p3_predicted']:.3e} (x{e['loo_6p3_ratio']:.2f} of measured)")
    d = out['dft_swap']
    print('== (b) laws:', d['laws'])
    for t, r in d['table'].items():
        print(f"  {t:5} nm  dEc V1 {r['dEc_V1']:.4f}  V2 {r['dEc_V2']:.4f}  (d {r['dEc_V2'] - r['dEc_V1']:+.4f})   m* V1 {r['mstar_V1']:.4f}  V2 {r['mstar_V2']:.4f}")
    print('  rigid shifts from the laws (V):', {t: round(v, 4) for t, v in d['rigid_shift_from_laws_V'].items()})
    print(f"  shared Qf shift {d['shared_Qf_shift_V']:+.4f} V -> Qf_V2 = {d['Qf_V2_cm2']:.4e} cm^-2")
    for t, r in d['films'].items():
        print(f"  {t} nm ({r['role']}): measured {r['measured']}")
        for k, v in r.items():
            if isinstance(v, dict) and 'rmse_active_dec' in v:
                print(f"     {k:24} rmse {v['rmse_active_dec']:.3f}  Vth_cc {v['Vth_cc']:.3f}  Vth_lin {v['Vth_lin']:.3f}  SS_cc {v['SS_cc']:.1f}  Ion {v['Ion']:.3e}  muFE {v['mu_FE']:.2f}")
        for k in ('mu_band_V2', 'mu_P', 'mu_E', 'mu_powerlaw_exponent', 'shift_components_V'):
            if k in r:
                print(f'     {k}: {r[k]}')


if __name__ == '__main__':
    main()
