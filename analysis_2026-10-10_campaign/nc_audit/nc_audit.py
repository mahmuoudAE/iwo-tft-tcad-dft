#!/usr/bin/env python3
"""NC audit of C10 S1-05 (run_0072, 3-D NC300 = 3.21785e18) against S0-01 (run_0061, quasi-2D NC300 = 1.373e19), 2.0 nm.

ANALYSIS ONLY. No simulator call, no deck generation, no write outside this folder (nc_audit/). Reads the finished run folders
(device.in, deckbuild.out, terminal_currents.csv, chan/avg probe exports, cb/qfn/n exports, *.str structures, acceptor_r*.dat)
and imports campaign_extract.compare() (registered extraction; its own writer main() is NOT called).

  <venv python> nc_audit.py            -> nc_audit_results.json + printed tables

Parts
  1  shift/scale diagnostic (rigid V_G shift, optional log-current offset) per window, local horizontal shift vs current level
  2  exact ATLAS nodal charge balance at x = 12 um at the three saved biases (equilibrium, near_vth = 0.7 V, final = 3 V)
  3  1-D vertical Poisson model of the film at x = 12 um (ATLAS's own trap tables and occupancy formula), validated on part 2
  4  matched-current decomposition of dV_G = V_G(S1-05) - V_G(S0-01) into band-position, free-carrier and trap terms
  5  analytic estimates  dV ~ delta (1 + C_trap/C_ox)  (linear, both ends) and the rigid-profile nonlinear form
  6  quasi-2D NC inside F_1/2 versus genuine 2-D statistics (F_0 carriers, Fermi-Dirac trap occupancy): dV_th and dI_on
"""
import csv
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq, minimize_scalar

HERE = Path(__file__).resolve().parent
CAMP = HERE.parent
PKG = CAMP.parent
RUNS = {'S0-01': PKG / 'results/runs/run_0061_2p0_c10_s0_01_2p0', 'S1-05': PKG / 'results/runs/run_0072_2p0_c10_s1_05_2p0'}
RUN_ID = {'S0-01': 'run_0061', 'S1-05': 'run_0072'}
NC = {'S0-01': 1.373e19, 'S1-05': 3.21785e18}        # device.in line 72/73 (nc300), echoed in deckbuild.out "Nc (per cc)"

# ---- deck constants (device.in of both runs; identical apart from nc300) ----
KB = 8.617333262e-5
KT = KB * 300.0                                       # eV (models temp=300)
Q = 1.602176634e-19
EPS0 = 8.8541878128e-14
EPS_S = 9.3 * EPS0                                    # material IWO permittivity=9.3
COX = 1.0 / (2e-7 / (9.0 * EPS0) + 1.5e-6 / (19.57 * EPS0))   # Al2O3 2 nm eps 9.0 + HfO2 15 nm eps 19.57 (header: 8.9554e-7)
QF = 1.38345e12                                       # interface qf (cm^-2), positive fixed charge at y = 0
ND = 2.5e17                                           # doping uniform n.type, regions 1 and 2 (complete ionisation: 'incomplete F')
PHI_MS = 4.7 - 4.01839                                # gate workfunction - IWO affinity (eV)
Y_TOP, Y_R12, Y_INT, Y_PROBE = -2e-7, -0.25e-7, 0.0, -1e-7     # cm; region 1 = [-2, -0.25] nm, region 2 = [-0.25, 0] nm
DELTA = KT * np.log(NC['S0-01'] / NC['S1-05'])        # pure statistics shift (non-degenerate), eV
LEVELS = [1e-15, 1e-14, 1e-13, 1e-12, 1e-11, 1e-10, 5e-10, 1e-9, 3e-9, 1e-8, 3e-8, 1e-7, 3e-7, 5e-7]

# ---------------------------------------------------------------- Fermi integrals
def _f12(eta):
    return 2 / np.sqrt(np.pi) * quad(lambda x: np.sqrt(x) / (1 + np.exp(min(x - eta, 700))), 0, max(eta, 0) + 60, limit=400, epsabs=0, epsrel=1e-11)[0]


ETA_T = np.linspace(-20, 40, 6001)
LNF12_T = np.log([_f12(e) for e in ETA_T])
_lnF12 = PchipInterpolator(ETA_T, LNF12_T)
_inv = PchipInterpolator(LNF12_T, ETA_T)


def F12(eta):
    eta = np.asarray(eta, float); e = np.exp(np.minimum(eta, -20))
    return np.where(eta < -20, e * (1 - e / 2 ** 1.5), np.exp(_lnF12(np.clip(eta, -20, 40))))


def F12inv(x):
    x = np.asarray(x, float); lx = np.log(x)
    return np.where(lx < LNF12_T[0], lx, _inv(np.clip(lx, LNF12_T[0], LNF12_T[-1])))


def F0(eta):
    return np.logaddexp(0, eta)


def F0inv(x):
    x = np.asarray(x, float); return np.where(x < 1e-8, np.log(x), np.log(np.expm1(np.maximum(x, 1e-300))))


# ---------------------------------------------------------------- ATLAS trap tables (afile) and occupancy
def load_table(fn):
    a = np.array([[float(v) for v in l.split()[1:]] for l in open(fn) if l.startswith('d ')])
    return a[np.argsort(a[:, 0])]                     # depth below Ec (eV), tail, gaussian, total (cm^-3/eV)


TAB = {r: load_table(RUNS['S0-01'] / f'acceptor_r{r}.dat') for r in (1, 2)}
for r in (1, 2):   # the tables of both runs are identical apart from the timestamp line (checked in part 0)
    assert np.allclose(TAB[r], load_table(RUNS['S1-05'] / f'acceptor_r{r}.dat'), rtol=0, atol=0)


def occupied(r, X):
    """occupied (negatively charged) acceptor density in region r, split (tail, gaussian), cm^-3.
    ATLAS steady-state acceptor occupancy with the hole terms dropped (p and p1 ~ 0 for E_g = 3.38 eV, carriers=1):
        f(E) = n / (n + n1(E)),  n1(E) = NC exp(-(Ec - E)/kT)   ->   f = X / (X + exp(-d/kT)),  X = n/NC,  d = Ec - E
    X = F_1/2(eta) reproduces ATLAS (verified against the stored ionised-acceptor field to < 0.1 %); X = exp(eta) is the
    Fermi-Dirac occupancy referenced to E_Fn (identical in the non-degenerate limit). Integration: trapezoid on the afile grid."""
    d, tail, gau = TAB[r][:, 0], TAB[r][:, 1], TAB[r][:, 2]
    X = np.atleast_1d(np.asarray(X, float))[:, None]
    f = X / (X + np.exp(-d / KT)[None, :])
    return np.trapezoid(tail[None, :] * f, d, axis=1), np.trapezoid(gau[None, :] * f, d, axis=1)


# tabulate occupied densities vs eta (fast interpolation inside the ODE)
ETA_G = np.linspace(-80, 30, 11001)
OCC = {}
for mode, Xf in (('atlas', F12), ('fd', np.exp), ('f0x', F0)):
    for r in (1, 2):
        t_, g_ = occupied(r, Xf(ETA_G))
        OCC[(mode, r)] = (PchipInterpolator(ETA_G, np.log(np.maximum(t_, 1e-300))), PchipInterpolator(ETA_G, np.log(np.maximum(g_, 1e-300))))


def occ_eta(mode, r, eta):
    a, b = OCC[(mode, r)]; eta = np.clip(eta, ETA_G[0], ETA_G[-1]); return np.exp(a(eta)), np.exp(b(eta))


# ---------------------------------------------------------------- structure files
def read_str(fn, x0=12.0):
    coords = {}; codes = None; rows = []
    for line in open(fn, errors='replace'):
        if line.startswith('c '):
            p = line.split(); coords[int(p[1])] = (float(p[2]), float(p[3]))
        elif line.startswith('s '):
            codes = [int(v) for v in line.split()[2:]]
        elif line.startswith('n '):
            p = line.split(); rows.append((int(p[1]), int(p[3]), [float(v) for v in p[4:]]))
    col = {c: i for i, c in enumerate(codes)}
    out = {1: [], 2: []}
    for idx, reg, v in rows:
        x, y = coords[idx + 1]                      # 'n' indices are 0-based, 'c' indices 1-based
        if reg in (1, 2) and abs(x - x0) < 1e-9:
            out[reg].append((y * 1e-4, v[col[121]], v[col[113]], v[col[106]], v[col[1038000]], v[col[1036000]]))
    return {r: np.array(sorted(out[r])) for r in (1, 2)}   # columns: y (cm), n, Ec (eV), QFL (eV), NA- , NA total


def nodal_balance(run, fn, vg):
    s = read_str(RUNS[run] / fn); res = {}
    n_sh = sum(np.trapezoid(s[r][:, 1], s[r][:, 0]) for r in (1, 2))
    na_sh = sum(np.trapezoid(s[r][:, 4], s[r][:, 0]) for r in (1, 2))
    # independent reconstruction of NA- at every node from n and the run's NC (ATLAS occupancy formula)
    rec = {r: np.array([occupied(r, nn / NC[run])[0][0] + occupied(r, nn / NC[run])[1][0] for nn in s[r][:, 1]]) for r in (1, 2)}
    # the region-1 node on the region 1/2 boundary (y = -0.25 nm) carries the region-2 trap fields in the .str file: excluded here
    keep = {1: s[1][:, 0] < Y_R12 - 1e-12, 2: np.ones(len(s[2]), bool)}
    rel = max(float(np.max(np.abs(rec[r][keep[r]] / s[r][keep[r], 4] - 1))) for r in (1, 2))
    comp = {}
    for r in (1, 2):
        t_, g_ = occupied(r, s[r][:, 1] / NC[run])
        comp[f'tail_r{r}'] = float(np.trapezoid(t_, s[r][:, 0])); comp[f'gauss_r{r}'] = float(np.trapezoid(g_, s[r][:, 0]))
    qfl = float(s[2][-1, 3]); u0 = float(s[2][-1, 2] - qfl); ut = float(s[1][0, 2] - qfl)
    yc = s[1][:, 0]; ic = int(np.argmin(abs(yc - Y_PROBE)))
    qs = QF + ND * (-Y_TOP) - n_sh - na_sh
    vg_check = PHI_MS - float(s[2][-1, 2]) - Q * qs / COX
    res.update(dict(vg=vg, qfl_eV=qfl, Vn=-qfl, u_top_eV=ut, u_int_eV=u0, u_centre_eV=float(s[1][ic, 2] - qfl), y_centre_cm=float(yc[ic]),
                    n_centre=float(s[1][ic, 1]), n_sheet=float(n_sh), NAm_sheet=float(na_sh), NAm_components_sheet=comp,
                    NAm_reconstruction_max_rel_err=rel, Qs_over_q=float(qs), vg_from_gate_equation=float(vg_check),
                    gate_equation_residual_mV=1e3 * float(vg_check - vg)))
    return res, s


# ---------------------------------------------------------------- 1-D vertical model at x = 12 um
# fast scalar tables on the uniform eta grid ETA_G (linear interpolation of logarithms, step 0.01)
_E0, _DE, _NE = ETA_G[0], ETA_G[1] - ETA_G[0], len(ETA_G)
_LN = {'F12': np.log(F12(ETA_G)), 'F0': np.log(F0(ETA_G))}
for (mode, r), (a_, b_) in OCC.items():
    _LN[(mode, r, 't')] = a_(ETA_G); _LN[(mode, r, 'g')] = b_(ETA_G)
_LN = {k: v.tolist() for k, v in _LN.items()}


def _lk(key, eta):
    x = (eta - _E0) / _DE
    if x <= 0: i, w = 0, 0.0
    elif x >= _NE - 1: i, w = _NE - 2, 1.0
    else: i = int(x); w = x - i
    t = _LN[key]; return math.exp(t[i] + w * (t[i + 1] - t[i]))


_STAT = {'atlas': ('F12', 'atlas'), 'f0_atlasocc': ('F0', 'f0x'), 'true2d': ('F0', 'fd')}


def film(u_top, nc, stat='atlas', ngrid=None, yprobe=Y_PROBE, n1=350, n2=100):
    """integrate Poisson from the free top surface (zero field under the 70 nm air layer, Neumann top boundary) down to the
    Al2O3 interface with fixed-step RK4. u = Ec - E_Fn (eV); u'' = q (N_D - n - N_A^-)/eps_IWO (E_Fn flat across the film).
    stat: 'atlas' (n = NC F1/2(eta), ATLAS occupancy X = F1/2), 'f0_atlasocc' (n = NC F0, X = n/NC = F0),
          'true2d' (n = NC F0, Fermi-Dirac occupancy X = exp(eta))."""
    fk, ok = _STAT[stat]

    def dens(r, u):
        eta = -u / KT
        return nc * _lk(fk, eta), _lk((ok, r, 't'), eta), _lk((ok, r, 'g'), eta)

    def acc(r, u):
        n, t_, g_ = dens(r, u); return Q * (ND - n - t_ - g_) / EPS_S
    out = {}; u, du = float(u_top), 0.0
    for r, (ya, yb, N) in ((1, (Y_TOP, Y_R12, n1)), (2, (Y_R12, Y_INT, n2))):
        h = (yb - ya) / N; ys = [ya]; us = [u]
        for k in range(N):
            k1u, k1v = du, acc(r, u)
            k2u, k2v = du + 0.5 * h * k1v, acc(r, u + 0.5 * h * k1u)
            k3u, k3v = du + 0.5 * h * k2v, acc(r, u + 0.5 * h * k2u)
            k4u, k4v = du + h * k3v, acc(r, u + h * k3u)
            u += h / 6 * (k1u + 2 * k2u + 2 * k3u + k4u); du += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            ys.append(ya + (k + 1) * h); us.append(u)
        d = np.array([dens(r, b) for b in us])
        out[r] = dict(y=np.array(ys), u=np.array(us), n=d[:, 0], tail=d[:, 1], gau=d[:, 2])
    sh = {k: float(sum(np.trapezoid(out[r][k], out[r]['y']) for r in (1, 2))) for k in ('n', 'tail', 'gau')}
    sh_r = {f'{k}_r{r}': float(np.trapezoid(out[r][k], out[r]['y'])) for r in (1, 2) for k in ('tail', 'gau')}
    qs = QF + ND * (-Y_TOP) - sh['n'] - sh['tail'] - sh['gau']
    u0 = float(out[2]['u'][-1]); uc = float(np.interp(yprobe, out[1]['y'], out[1]['u']))
    nc_probe = float(np.exp(np.interp(yprobe, out[1]['y'], np.log(out[1]['n']))))
    gauss_check = EPS_S * du / Q - (ND * (-Y_TOP) - sh['n'] - sh['tail'] - sh['gau'])   # Gauss law closure (cm^-2)
    return dict(u_top=u_top, u_int=u0, u_centre=uc, n_centre=nc_probe, n_sheet=sh['n'], tail_sheet=sh['tail'], gauss_sheet=sh['gau'],
                comps=sh_r, Qs_over_q=qs, vg_minus_vn=PHI_MS - u0 - Q * qs / COX, gauss_closure_cm2=float(gauss_check), profile=out)


def solve_for(target, value, nc, stat='atlas', lo=-0.35, hi=1.6, yprobe=Y_PROBE):
    """find u_top so that target ('n_centre' | 'n_sheet' | 'vg_minus_vn') equals value"""
    def g(ut):
        m = film(ut, nc, stat, yprobe=yprobe, n1=175, n2=50); v = m[target]
        return (np.log(v) - np.log(value)) if target != 'vg_minus_vn' else (v - value)
    ut = brentq(g, lo, hi, xtol=1e-10)
    return film(ut, nc, stat, yprobe=yprobe)


# ---------------------------------------------------------------- run curves
def load_curves(run):
    d = RUNS[run]
    with open(d / 'terminal_currents.csv', newline='') as f:
        a = np.array([(float(r['vg_V']), float(r['id_A_per_um'])) for r in csv.DictReader(f)])
    a = a[np.argsort(a[:, 0])]

    def dat(fn):
        rows = [l.split() for l in open(d / fn).read().splitlines()[4:] if l.strip()]
        b = np.array([(float(x), float(y)) for x, y in rows]); return b[np.argsort(b[:, 0])]
    return dict(vg=a[:, 0], i=a[:, 1], nc=dat('chan_electrons_vg.dat'), navg=dat('avg_electrons_vg.dat'))


def mono(vg, y, vmin):
    k = (vg >= vmin) & (y > 0); return vg[k], np.log10(y[k])


def vg_at(curve, level, vmin):
    v, ly = mono(curve['vg'], curve['i'], vmin)
    f = PchipInterpolator(v, ly)
    if not (ly.min() <= np.log10(level) <= ly.max()): return None
    return float(brentq(lambda x: f(x) - np.log10(level), v[0], v[-1]))


def logi_fun(curve, vmin):
    v, ly = mono(curve['vg'], curve['i'], vmin); return PchipInterpolator(v, ly, extrapolate=False), v


def at_vg(arr, vg):
    f = PchipInterpolator(arr[:, 0], np.log10(np.maximum(arr[:, 1], 1e-300))); return float(10 ** f(vg))


def ss_local(curve, level, vmin, h=0.02):
    """local subthreshold swing dV_G/dlog10 I at a current level (mV/dec), central difference in log I"""
    a = vg_at(curve, level * 10 ** h, vmin); b = vg_at(curve, level * 10 ** -h, vmin)
    return None if (a is None or b is None) else 1e3 * (a - b) / (2 * h)


# ---------------------------------------------------------------- part 1: shift/scale diagnostic
def shift_diag(c0, c1, vmin0, vmin1):
    f0, v0 = logi_fun(c0, vmin0)
    v1, l1 = mono(c1['vg'], c1['i'], vmin1)
    wins = {'deep_sub_1e-15..1e-12': (l1 >= -15) & (l1 <= -12), 'sub_1e-14..1e-9 (campaign sub window range)': (l1 >= -14) & (l1 <= -9),
            'fixed_SS_window_5e-11..5e-10': (l1 >= np.log10(5e-11)) & (l1 <= np.log10(5e-10)),
            'near_threshold_1e-9..1e-7': (l1 >= -9) & (l1 <= -7), 'on_VG_1..3V': (v1 >= 1 - 1e-9) & (v1 <= 3 + 1e-9),
            'active_1e-14..3V': (l1 >= -14)}
    out = {}
    for name, k in wins.items():
        x, y = v1[k], l1[k]

        def res(dv, c=0.0):
            p = f0(x - dv); m = np.isfinite(p); return y[m] - p[m] - c, int(m.sum())
        if len(x) == 0: continue
        r1 = minimize_scalar(lambda dv: (np.mean(res(dv)[0] ** 2) if res(dv)[1] >= max(3, len(x) // 2) else 1e3), bounds=(0.0, 0.3), method='bounded', options={'xatol': 1e-6})
        rr, npts = res(r1.x)

        def obj2(dv):
            e, k_ = res(dv); return np.mean((e - e.mean()) ** 2) if k_ >= max(3, len(x) // 2) else 1e3
        r2 = minimize_scalar(obj2, bounds=(0.0, 0.3), method='bounded', options={'xatol': 1e-6})
        e2, _ = res(r2.x); c2 = float(e2.mean()); e2 = e2 - c2
        out[name] = dict(points=npts, shift_only=dict(dV_mV=1e3 * r1.x, rms_resid_dec=float(np.sqrt(np.mean(rr ** 2))), max_abs_resid_dec=float(np.max(np.abs(rr)))),
                         shift_plus_scale=dict(dV_mV=1e3 * r2.x, log10_scale=c2, rms_resid_dec=float(np.sqrt(np.mean(e2 ** 2))), max_abs_resid_dec=float(np.max(np.abs(e2)))))
    loc = []
    for L in LEVELS:
        a, b = vg_at(c0, L, vmin0), vg_at(c1, L, vmin1)
        loc.append(dict(I_A_per_um=L, vg_S0=a, vg_S1=b, dV_mV=(1e3 * (b - a) if (a is not None and b is not None) else None),
                        SS_S0=ss_local(c0, L, vmin0), SS_S1=ss_local(c1, L, vmin1)))
    vert = []
    for v in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        i0 = float(np.interp(v, c0['vg'], c0['i'])); i1 = float(np.interp(v, c1['vg'], c1['i']))
        vert.append(dict(vg=v, I_S0=i0, I_S1=i1, dlog10I=float(np.log10(i1 / i0))))
    return dict(windows=out, local_horizontal_shift=loc, vertical_at_fixed_VG=vert)


# ---------------------------------------------------------------- main
def main():
    os.environ.setdefault('IWO_MODEL_FILE', 'config/iwo_material_model_v3.yaml')
    R = {'constants': dict(kT_eV=KT, Cox_F_cm2=COX, Cox_over_q_cm2_per_V=COX / Q, delta_eV=DELTA, NC=NC, NC_ratio=NC['S0-01'] / NC['S1-05'],
                           phi_ms_eV=PHI_MS, Qf_cm2=QF, Nd_cm3=ND)}
    print(f'delta = kT ln(NC0/NC1) = {1e3 * DELTA:.3f} meV ; Cox = {COX:.5e} F/cm2 ; Cox/q = {COX / Q:.4e} cm^-2/V')

    # ---- part 0: the registered compare (no writing by campaign_extract)
    try:
        sys.path.insert(0, str(CAMP)); import campaign_extract as ce
        cmpd = ce.compare(str(RUNS['S1-05']), str(RUNS['S0-01']), 's1_05'); R['registered_compare'] = cmpd
        print('registered compare:', json.dumps({k: cmpd[k] for k in ('dVth_cc_mV', 'dSS_fixed_mV_dec', 'dSS_a1_mV_dec', 'd_active_rmse_dec', 'verdict')}, default=float))
    except Exception as e:  # pragma: no cover
        R['registered_compare'] = {'error': f'{type(e).__name__}: {e}'}; print('compare failed', e)

    C = {r: load_curves(r) for r in RUNS}
    VMIN = {'S0-01': -0.1, 'S1-05': -0.05}     # first solved points above the 1e-17 A/um noise band (KCL floor ~1e-18)

    # ---- part 1
    R['part1_shift'] = shift_diag(C['S0-01'], C['S1-05'], VMIN['S0-01'], VMIN['S1-05'])
    print('\nPART 1  windows (S0-01 -> S1-05):')
    for k, v in R['part1_shift']['windows'].items():
        print(f"  {k:45s} n={v['points']:3d}  shift {v['shift_only']['dV_mV']:7.1f} mV rms {v['shift_only']['rms_resid_dec']:.3f} max {v['shift_only']['max_abs_resid_dec']:.3f} | "
              f"shift+scale {v['shift_plus_scale']['dV_mV']:7.1f} mV, log10 s {v['shift_plus_scale']['log10_scale']:+.3f}, rms {v['shift_plus_scale']['rms_resid_dec']:.3f}")
    for v in R['part1_shift']['local_horizontal_shift']:
        print(f"  I={v['I_A_per_um']:.0e}  dV={v['dV_mV'] if v['dV_mV'] is None else round(v['dV_mV'], 1)} mV  SS0={v['SS_S0'] and round(v['SS_S0'], 1)}  SS1={v['SS_S1'] and round(v['SS_S1'], 1)}")
    for v in R['part1_shift']['vertical_at_fixed_VG']:
        print(f"  VG={v['vg']}: dlog10 I = {v['dlog10I']:+.3f}")

    # ---- part 2: exact nodal balances
    R['part2_nodal'] = {}
    print('\nPART 2  ATLAS nodal balance at x = 12 um')
    for run in RUNS:
        R['part2_nodal'][run] = {}
        for fn, vg in (('equilibrium.str', 0.0), ('near_vth.str', 0.7), ('final.str', 3.0)):
            b, _ = nodal_balance(run, fn, vg); R['part2_nodal'][run][fn] = b
            print(f"  {run} {fn:16s} VG={vg}: Vn={b['Vn']:.4f} u_top={b['u_top_eV']:.4f} u_c={b['u_centre_eV']:.4f} u_int={b['u_int_eV']:.4f} "
                  f"n_sh={b['n_sheet']:.3e} NA_sh={b['NAm_sheet']:.3e} gate-eq resid {b['gate_equation_residual_mV']:+.2f} mV, NA- recon err {b['NAm_reconstruction_max_rel_err']:.1e}")

    # ---- part 3: 1-D model validation against the nodes
    R['part3_model_validation'] = {}
    print('\nPART 3  1-D model vs ATLAS nodes (model matched to the ATLAS centre-node n)')
    for run in RUNS:
        for fn in ('equilibrium.str', 'near_vth.str', 'final.str'):
            b = R['part2_nodal'][run][fn]
            m = solve_for('n_centre', b['n_centre'], NC[run], yprobe=b['y_centre_cm'])   # matched at the ATLAS node position
            v = dict(model_u_top=m['u_top'], atlas_u_top=b['u_top_eV'], model_u_int=m['u_int'], atlas_u_int=b['u_int_eV'],
                     model_n_sheet=m['n_sheet'], atlas_n_sheet=b['n_sheet'], model_NA_sheet=m['tail_sheet'] + m['gauss_sheet'], atlas_NA_sheet=b['NAm_sheet'],
                     model_vg=m['vg_minus_vn'] + b['Vn'], atlas_vg=b['vg'])
            v['vg_error_mV'] = 1e3 * (v['model_vg'] - v['atlas_vg'])
            R['part3_model_validation'][f'{run}:{fn}'] = v
            print(f"  {run} {fn:16s} u_top {m['u_top']:.4f}/{b['u_top_eV']:.4f}  u_int {m['u_int']:.4f}/{b['u_int_eV']:.4f}  n_sh {m['n_sheet']:.3e}/{b['n_sheet']:.3e}  "
                  f"NA_sh {m['tail_sheet'] + m['gauss_sheet']:.3e}/{b['NAm_sheet']:.3e}  VG {v['model_vg']:.4f}/{b['vg']:.4f} ({v['vg_error_mV']:+.1f} mV)")

    # ---- part 4 + 5: matched-current decomposition and analytic estimates
    R['part4_matched_current'] = []
    print('\nPART 4/5  matched-current decomposition, dV_G = V_G(S1-05) - V_G(S0-01) [mV]')
    hdr = ('I', 'dVG_ATLAS', 'stat(-du_int)', 'stat_centre', 'free', 'tail', 'deepG', 'itG', 'model_sum', 'closure(dVn)', 'n_c S1/S0', 'eta_c S0', 'eta_c S1',
           'lin_S0', 'lin_S1', 'rigid_nl', 'SSreg')
    print('  ' + ' '.join(f'{h:>12s}' for h in hdr))
    for L in LEVELS:
        row = {'I_A_per_um': L}; ms = {}
        ok = True
        for run in RUNS:
            vg = vg_at(C[run], L, VMIN[run])
            if vg is None: ok = False; break
            ncent = at_vg(C[run]['nc'], vg); m = solve_for('n_centre', ncent, NC[run]); ms[run] = m
            row[run] = dict(vg=vg, n_centre_probe=ncent, n_avg_probe=at_vg(C[run]['navg'], vg), u_centre=m['u_centre'], u_int=m['u_int'], u_top=m['u_top'],
                            eta_centre=-m['u_centre'] / KT, eta_int=-m['u_int'] / KT, n_sheet=m['n_sheet'], tail_sheet=m['tail_sheet'], gauss_sheet=m['gauss_sheet'],
                            comps=m['comps'], vg_minus_vn_model=m['vg_minus_vn'], Vn_inferred=vg - m['vg_minus_vn'],
                            Ec_minus_EFn_centre_eV=m['u_centre'], Ec_minus_EFn_int_eV=m['u_int'])
        if not ok: continue
        a, b = ms['S0-01'], ms['S1-05']; k = 1e3 * Q / COX
        t = dict(dVG_ATLAS=1e3 * (row['S1-05']['vg'] - row['S0-01']['vg']), stat_int=-1e3 * (b['u_int'] - a['u_int']), stat_centre=-1e3 * (b['u_centre'] - a['u_centre']),
                 free=k * (b['n_sheet'] - a['n_sheet']), tail=k * (b['comps']['tail_r1'] + b['comps']['tail_r2'] - a['comps']['tail_r1'] - a['comps']['tail_r2']),
                 deepG=k * (b['comps']['gau_r1'] - a['comps']['gau_r1']), itG=k * (b['comps']['gau_r2'] - a['comps']['gau_r2']))
        t['model_sum'] = t['stat_int'] + t['free'] + t['tail'] + t['deepG'] + t['itG']
        t['closure_dVn'] = t['dVG_ATLAS'] - t['model_sum']
        t['film_bending_part_of_stat'] = t['stat_int'] - t['stat_centre']
        # part 5: analytic estimates around the S0-01 / S1-05 states
        def trapsheet(m, shift_eV):     # rigid shift of the whole S0-01 profile by shift_eV toward Ec (E_F up)
            tot = 0.0
            for r in (1, 2):
                eta = -(m['profile'][r]['u'] - shift_eV) / KT; tt, gg = occ_eta('atlas', r, eta); tot += np.trapezoid(tt + gg, m['profile'][r]['y'])
            return tot
        h = 1e-4
        ctrap0 = Q * (trapsheet(a, h) - trapsheet(a, -h)) / (2 * h) / COX           # C_trap/C_ox (dimensionless), S0-01 state
        ctrap1 = Q * (trapsheet(b, h) - trapsheet(b, -h)) / (2 * h) / COX
        def nfree(m, s, nc): return sum(np.trapezoid(nc * F12(-(m['profile'][r]['u'] - s) / KT), m['profile'][r]['y']) for r in (1, 2))
        cn0 = Q * (nfree(a, h, NC['S0-01']) - nfree(a, -h, NC['S0-01'])) / (2 * h) / COX
        t['Ctrap_over_Cox_S0'] = ctrap0; t['Ctrap_over_Cox_S1'] = ctrap1; t['Cn_over_Cox_S0'] = cn0
        t['lin_S0'] = 1e3 * DELTA * (1 + ctrap0); t['lin_S1'] = 1e3 * DELTA * (1 + ctrap1)
        t['rigid_nonlinear'] = 1e3 * DELTA + 1e3 * Q * (trapsheet(a, DELTA) - trapsheet(a, 0.0)) / COX
        ss0 = ss_local(C['S0-01'], L, VMIN['S0-01']); t['registered_style_SS_S0'] = (1e3 * DELTA * ss0 / (1e3 * KT * np.log(10))) if ss0 else None
        t['n_centre_ratio_S1_over_S0'] = row['S1-05']['n_centre_probe'] / row['S0-01']['n_centre_probe']
        row['terms_mV'] = t; R['part4_matched_current'].append(row)
        vals = [L, t['dVG_ATLAS'], t['stat_int'], t['stat_centre'], t['free'], t['tail'], t['deepG'], t['itG'], t['model_sum'], t['closure_dVn'],
                t['n_centre_ratio_S1_over_S0'], row['S0-01']['eta_centre'], row['S1-05']['eta_centre'], t['lin_S0'], t['lin_S1'], t['rigid_nonlinear'],
                t['registered_style_SS_S0'] or float('nan')]
        print('  ' + ' '.join(f'{v:12.3g}' for v in vals))

    # ---- part 6: quasi-2D NC in F1/2 versus genuine 2-D statistics (S0-01 parameters)
    print('\nPART 6  S0-01 statistics: quasi-2D NC in F1/2 (ATLAS) vs true 2-D (F0 carriers + FD traps), same NC = N2D/t')
    eta = np.array([-10, -5, -3, -2, -1, 0, 1, 2, 3])
    R['part6_functions'] = [dict(eta=float(e), F12_over_F0=float(F12(e) / F0(e)), trap_X_atlas_over_fd=float(F12(e) / np.exp(e))) for e in eta]
    for d in R['part6_functions']: print(f"  eta={d['eta']:+.0f}: F1/2/F0 = {d['F12_over_F0']:.4f} ; ATLAS trap drive F1/2/exp(eta) = {d['trap_X_atlas_over_fd']:.4f}")
    R['part6_device'] = []
    for L in (1e-12, 1e-10, 1e-9, 1e-8, 1e-7, 'VG=3V'):
        if L == 'VG=3V':
            ref = R['part2_nodal']['S0-01']['final.str']; a = solve_for('n_centre', ref['n_centre'], NC['S0-01']); vref = a['vg_minus_vn']
        else:
            row = next(r for r in R['part4_matched_current'] if r['I_A_per_um'] == L); a = solve_for('n_centre', row['S0-01']['n_centre_probe'], NC['S0-01']); vref = a['vg_minus_vn']
        out = dict(level=L, eta_centre=-a['u_centre'] / KT, eta_int=-a['u_int'] / KT, n_sheet_q2d=a['n_sheet'])
        for stat in ('f0_atlasocc', 'true2d'):
            bsh = solve_for('n_sheet', a['n_sheet'], NC['S0-01'], stat)          # same sheet density -> V_G shift
            bvg = solve_for('vg_minus_vn', vref, NC['S0-01'], stat)              # same gate drive -> sheet-density (current) ratio
            out[stat] = dict(dVG_same_nsheet_mV=1e3 * (bsh['vg_minus_vn'] - vref), nsheet_ratio_same_VG=bvg['n_sheet'] / a['n_sheet'],
                             trap_sheet_ratio_same_nsheet=(bsh['tail_sheet'] + bsh['gauss_sheet']) / (a['tail_sheet'] + a['gauss_sheet']))
        R['part6_device'].append(out)
        print(f"  {str(L):>7s}: eta_c {out['eta_centre']:+.2f} eta_int {out['eta_int']:+.2f} | F0 carriers only: dVG {out['f0_atlasocc']['dVG_same_nsheet_mV']:+.2f} mV, "
              f"n ratio {out['f0_atlasocc']['nsheet_ratio_same_VG']:.4f} | true 2-D: dVG {out['true2d']['dVG_same_nsheet_mV']:+.2f} mV, n ratio {out['true2d']['nsheet_ratio_same_VG']:.4f}, "
              f"trap ratio {out['true2d']['trap_sheet_ratio_same_nsheet']:.3f}")

    # ---- equivalence: NC change == trap-level shift by delta (ATLAS occupancy depends on n/NC only)
    R['equivalence'] = dict(statement='At fixed n, f = n/(n + NC exp(-d/kT)); NC -> NC/r is identical to every trap depth d -> d + kT ln r (deeper). '
                                      'For the exponential tail this is NTA -> NTA r^(kT/WTA); for the Gaussians EGA -> EGA + kT ln r. '
                                      'In the non-degenerate limit the free-carrier part is a rigid band shift kT ln r (absorbed by Q_f).',
                            r=NC['S0-01'] / NC['S1-05'], tail_amplitude_factor=float((NC['S0-01'] / NC['S1-05']) ** (KT / 0.04)),
                            Qf_equivalent_cm2=float(COX * DELTA / Q))
    (HERE / 'nc_audit_results.json').write_text(json.dumps(R, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
    print('\nwritten', HERE / 'nc_audit_results.json')


if __name__ == '__main__':
    main()
