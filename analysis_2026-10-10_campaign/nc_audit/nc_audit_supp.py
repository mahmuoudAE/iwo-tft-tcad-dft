#!/usr/bin/env python3
"""Supplement to nc_audit.py (ANALYSIS ONLY: no simulator call, no file written outside nc_audit/, deck text built in memory only).

  A  intrinsic 1-D split at matched LOCAL density (S0-01 state at each current level; S1-05 model at the same centre density)
  B  reparametrisation test: quasi-2D NC with (Q_f - C_ox delta/q, every acceptor level delta deeper  ==  NTA x exp(delta/W_TA),
     Gaussians delta deeper) against the 3-D-NC model, at matched sheet density: residual V_G difference
  C  extracted SS (fixed and A1 windows) of both runs and the measured 2.0 nm film (registered functions, no writing)
  D  H-E arithmetic: all-confinement-off at 2.0 / 6.3 / 13.2 nm decomposed into affinity (exactly rigid), NC (statistics x traps)
     and mobility (I ~ MUN exactly) terms, from the existing curves; S3 deck parameters read from in-memory deck text
Output: nc_audit_supp_results.json
"""
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nc_audit as A  # noqa: E402

OUT = {}

# ---------------- A: intrinsic matched-local-density split
R = json.loads((HERE / 'nc_audit_results.json').read_text())
k = 1e3 * A.Q / A.COX
OUT['A_matched_local_density'] = []
print('A  matched local density (S0-01 state at the current level; S1-05 model at the same centre n) [mV]')
print('     I      dV_1D   stat(-du_int)  pure_delta  bending  tail   itG   deepG  free')
for row in R['part4_matched_current']:
    L = row['I_A_per_um']; nc0 = row['S0-01']['n_centre_probe']
    a = A.solve_for('n_centre', nc0, A.NC['S0-01']); b = A.solve_for('n_centre', nc0, A.NC['S1-05'])
    t = dict(I=L, dV_1D=1e3 * (b['vg_minus_vn'] - a['vg_minus_vn']), stat_int=-1e3 * (b['u_int'] - a['u_int']), stat_centre=-1e3 * (b['u_centre'] - a['u_centre']),
             tail=k * (b['comps']['tail_r1'] + b['comps']['tail_r2'] - a['comps']['tail_r1'] - a['comps']['tail_r2']),
             itG=k * (b['comps']['gau_r2'] - a['comps']['gau_r2']), deepG=k * (b['comps']['gau_r1'] - a['comps']['gau_r1']), free=k * (b['n_sheet'] - a['n_sheet']),
             tail_sheet_S0=a['comps']['tail_r1'] + a['comps']['tail_r2'], tail_sheet_S1=b['comps']['tail_r1'] + b['comps']['tail_r2'])
    t['bending'] = t['stat_int'] - t['stat_centre']
    OUT['A_matched_local_density'].append(t)
    print(f"  {L:7.0e} {t['dV_1D']:7.1f} {t['stat_int']:9.1f} {t['stat_centre']:11.1f} {t['bending']:8.1f} {t['tail']:6.1f} {t['itG']:5.2f} {t['deepG']:6.3f} {t['free']:6.1f}")

# ---------------- B: reparametrisation (non-identifiability) test
delta = A.DELTA
for r in (1, 2):
    d, tail, gau = A.TAB[r][:, 0], A.TAB[r][:, 1], A.TAB[r][:, 2]
    tail_s = np.interp(d - delta, d, tail, left=0.0); gau_s = np.interp(d - delta, d, gau, left=0.0)
    X = A.F12(A.ETA_G)[:, None]; f = X / (X + np.exp(-d / A.KT)[None, :])
    A._LN[('eq', r, 't')] = np.log(np.maximum(np.trapezoid(tail_s[None, :] * f, d, axis=1), 1e-300)).tolist()
    A._LN[('eq', r, 'g')] = np.log(np.maximum(np.trapezoid(gau_s[None, :] * f, d, axis=1), 1e-300)).tolist()
A._STAT['eq'] = ('F12', 'eq')
qf_eq = A.QF - A.COX * delta / A.Q
OUT['B_reparametrisation'] = dict(Qf_equiv_cm2=qf_eq, dQf_cm2=A.QF - qf_eq, NTA_factor=math.exp(delta / 0.04), Gaussian_depth_shift_eV=delta, rows=[])
print(f"\nB  quasi-2D NC with Q_f {qf_eq:.4e} (-{A.QF - qf_eq:.3e}), acceptor levels {1e3 * delta:.1f} meV deeper (tail x{math.exp(delta / 0.04):.3f}) vs 3-D NC")
for row in R['part4_matched_current']:
    nsh = row['S1-05']['n_sheet']; b = A.solve_for('n_sheet', nsh, A.NC['S1-05'])
    qf0 = A.QF; A.QF = qf_eq
    try: e = A.solve_for('n_sheet', nsh, A.NC['S0-01'], 'eq')
    finally: A.QF = qf0
    dv = 1e3 * (e['vg_minus_vn'] - b['vg_minus_vn'])
    OUT['B_reparametrisation']['rows'].append(dict(I=row['I_A_per_um'], n_sheet=nsh, eta_int_3D=-b['u_int'] / A.KT, dVG_equiv_minus_3D_mV=dv))
    print(f"  {row['I_A_per_um']:7.0e} n_sh {nsh:.3e} eta_int(3-D) {-b['u_int'] / A.KT:+6.2f}  V_G(equivalent quasi-2D) - V_G(3-D) = {dv:+7.2f} mV")

# ---------------- C: SS values (registered extraction, no writing)
os.environ.setdefault('IWO_MODEL_FILE', 'config/iwo_material_model_v3.yaml')
sys.path.insert(0, str(A.CAMP)); import campaign_extract as ce  # noqa: E402
info, rA1 = ce.measured()
OUT['C_extraction'] = {}
for run in A.RUNS:
    x = ce.extract(str(A.RUNS[run]), info); e = x['extraction']; c = x['campaign_metrics']
    OUT['C_extraction'][run] = dict(vth_cc=e['vth_cc_V'], ss_fixed=e['ss_fixed_mV_dec'], ss_a1=e['ss_a1_mV_dec'], a1_window=e['ss_a1_window_A_per_um'],
                                    rmse_sub=c['rmse_sub_dec'], rmse_on=c['rmse_on_dec'], dVth_vs_meas=c['dVth_cc_V'], Id3V_err_pct=c['Id3V_err_pct'],
                                    meas_vth_cc=c['measured_reference']['vth_cc_V'])
import extraction as ex  # noqa: E402  (registered)
import run_extraction as rx  # noqa: E402
vg_m, i_m = info[2.0]['vg'], info[2.0]['i']
try: ssm = rx.ss_rule(vg_m, i_m, *rx.WIN, False, info[2.0]['floor'], info[2.0]['sig_floor'])
except Exception as err: ssm = {'invalid': str(err)}
try: ssm_a1 = ex.ss_window(vg_m, i_m, *info[2.0]['a1_window'], False)
except Exception as err: ssm_a1 = {'invalid': str(err)}
OUT['C_extraction']['measured_2p0'] = dict(ss_fixed=ssm, ss_a1=ssm_a1)
print('\nC  extraction:', json.dumps(OUT['C_extraction'], default=float)[:1500])

# ---------------- D: H-E arithmetic
sys.path.insert(0, str(A.PKG / 'scripts'))
import campaign_tools as ct  # noqa: E402
mx = ct.matrix(); ent = {e['id']: e for e in mx['planned_launches']} if isinstance(mx.get('planned_launches'), list) else {}
if not ent:
    for v in mx.values():
        if isinstance(v, list):
            for e in v:
                if isinstance(e, dict) and 'id' in e: ent[e['id']] = e
decks = {}
for rid in ('S0-01', 'S1-05', 'S1-01', 'S1-02', 'S3-01', 'S3-02', 'S3-03'):
    e = ent.get(rid)
    if e is None: continue
    try:
        txt, meta = ct.entry_deck(e['campaign_entry'], ct.V3)
        st = '\n'.join(ct.statements(txt))
        g = lambda key: (re.search(rf'\b{key}=([0-9.eE+-]+)', st).group(1) if re.search(rf'\b{key}=([0-9.eE+-]+)', st) else None)
        decks[rid] = dict(affinity=g('affinity'), nc300=g('nc300'), mun=g('mun'), eg300=g('eg300'), nta=g('nta'))
    except Exception as err:
        decks[rid] = {'error': f'{type(err).__name__}: {err}'}
OUT['D_deck_parameters_in_memory'] = decks
print('\nD  deck parameters (in-memory deck text, nothing written):', json.dumps(decks))

C0, C1 = A.load_curves('S0-01'), A.load_curves('S1-05')
V0 = lambda L: A.vg_at(C0, L, -0.1); V1 = lambda L: A.vg_at(C1, L, -0.05)
Icc = 1e-9
try:
    nc_off = float(decks['S3-01']['nc300']); mun_off = float(decks['S3-01']['mun']); mun_on = float(decks['S0-01']['mun'])
    aff_off = float(decks['S3-01']['affinity']); aff_on = float(decks['S0-01']['affinity'])
except Exception:
    nc_off, mun_off, mun_on, aff_off, aff_on = 2.38e18, 21.6265 * (1 - 0.287 / 2.0) ** 2, 12.977, 4.3, 4.01839
s_nc = A.NC['S1-05'] / nc_off; s_mu = mun_off / mun_on
d_nc1 = 1e3 * (V1(Icc) - V0(Icc))
d_nc2_secant = d_nc1 * math.log(s_nc) / math.log(A.NC['S0-01'] / A.NC['S1-05'])
d_nc2_scale = 1e3 * (V1(Icc * s_nc) - V1(Icc))
d_mu_lo = 1e3 * (V1(Icc * s_nc / s_mu) - V1(Icc * s_nc)); d_mu_hi = 1e3 * (V1(Icc / s_mu) - V1(Icc))
d_aff = -1e3 * (aff_off - aff_on)
lo = d_aff + d_nc1 + d_nc2_secant + d_mu_lo; hi = d_aff + d_nc1 + d_nc2_scale + d_mu_hi
OUT['D_HE_2p0'] = dict(affinity_mV=d_aff, NC_quasi2D_to_3D_mV=d_nc1, NC_3D_to_bulkmass_secant_mV=d_nc2_secant, NC_3D_to_bulkmass_scale_mV=d_nc2_scale,
                      mobility_mV=[d_mu_lo, d_mu_hi], mun_ratio=s_mu, nc_ratio_S1_to_off=s_nc, all_off_vs_S0_01_mV=[lo, hi],
                      all_off_vs_S1_05_mV=[lo - d_nc1, hi - d_nc1], registered='-230 +/- 40 mV (H-E, includes NC as +55 mV)')
print(f"\nD  2.0 nm all-off (S3-01) vs S0-01 at 1e-9 A/um: affinity {d_aff:.1f} mV (exactly rigid), NC 1.373e19->3.218e18 {d_nc1:+.1f} (S1-05, ATLAS), "
      f"3.218e18->{nc_off:.3e} {d_nc2_secant:+.1f}..{d_nc2_scale:+.1f}, mobility x{s_mu:.4f} {d_mu_hi:+.1f}..{d_mu_lo:+.1f}  =>  {lo:+.0f}..{hi:+.0f} mV "
      f"(vs S1-05: {lo - d_nc1:+.0f}..{hi - d_nc1:+.0f} mV)")

# thicker films: NC (mass only) and mobility terms read through each film's own local slope at 1e-9 A/um
OUT['D_HE_thick'] = {}
for rid_on, rid_off, run_dir, dEc in (('S1-01', 'S3-02', 'run_0068_6p3_c10_s1_01_6p3', 0.0622), ('S1-02', 'S3-03', 'run_0069_13p2_c10_s1_02_13p2', 0.0235)):
    try:
        A.RUNS['tmp'] = A.PKG / 'results/runs' / run_dir; Cx = A.load_curves('tmp')
        vmin = float(Cx['vg'][np.argmax(Cx['i'] > 1e-16)])
        don, doff = decks.get(rid_on, {}), decks.get(rid_off, {})
        r_nc = float(don['nc300']) / float(doff['nc300']); r_mu = float(doff['mun']) / float(don['mun'])
        aff = -1e3 * (float(doff['affinity']) - float(don['affinity']))
        ss = A.ss_local(Cx, Icc, vmin)
        d_nc = 1e3 * (A.vg_at(Cx, Icc * r_nc, vmin) - A.vg_at(Cx, Icc, vmin)); d_mu = 1e3 * (A.vg_at(Cx, Icc / r_mu, vmin) - A.vg_at(Cx, Icc, vmin))
        OUT['D_HE_thick'][rid_off] = dict(affinity_mV=aff, NC_scale_upper_mV=d_nc, NC_bare_mV=1e3 * A.KT * math.log(r_nc), mobility_mV=d_mu, SS_local_1e9=ss,
                                          nc_ratio=r_nc, mun_ratio=r_mu, total_mV=aff + d_nc + d_mu)
        print(f"   {rid_off}: affinity {aff:.1f}, NC (x1/{r_nc:.4f}) {d_nc:+.1f} (bare {1e3 * A.KT * math.log(r_nc):.1f}), mobility (x{r_mu:.4f}) {d_mu:+.1f}, "
              f"SS(1e-9) {ss:.0f} mV/dec => {aff + d_nc + d_mu:+.1f} mV")
    except Exception as err:
        OUT['D_HE_thick'][rid_off] = {'error': f'{type(err).__name__}: {err}'}; print('   ', rid_off, 'error', err)

(HERE / 'nc_audit_supp_results.json').write_text(json.dumps(OUT, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
print('\nwritten', HERE / 'nc_audit_supp_results.json')
