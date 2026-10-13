#!/usr/bin/env python3
"""Synthetic tests for hf_score_draft.py (DRAFT H-F definitions v4, 2026-10-13, Codex rulings encoded). Synthetic curves ONLY: no run
directory and no measured file is read (the H-F quantities are deliberately not computed on real runs before the definitions are
frozen). Nothing is written.

  <venv python> -B analysis_2026-10-10_campaign/test_hf_score_draft.py [--regressions-only]     (or: hf_score_draft.py selftest)
"""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hf_score_draft as H  # noqa: E402
import profile_s4s5 as P  # noqa: E402
import test_profile_s4s5 as T  # noqa: E402  (synthetic transfer-curve generator)

Q, COX = T.Q, T.COX
NUIS0 = {'dQf': 0.0, 'mu_inf': 80.0, 'ell': 9.0}
X0 = dict(P.START_X)                       # baseline = S1-01 start parameters (ruling 1)
XG = dict(X0, g0=H.IGZO_G0)                # S3-11/12/13: start parameters with IGZO.TOKYO GAMMA0 -0.31
Q2D = [H.NC_Q2D + '1.373e+19']             # the quasi-2D NC override of S0-01 (2.0 nm)
LAB = {2.0: 'c10_s0_01_2p0', 6.3: 'c10_s1_01_6p3', 13.2: 'c10_s1_02_13p2'}


def info_with_63(dv=0.28, s=0.25, x63=None, distort=None, nuis=NUIS0):
    """2.0 / 13.2 nm 'measured' = the synthetic model (X0, nuis); 6.3 nm 'measured' = the two-film model prediction at 6.3 nm moved
    by +dv (to more positive V_G) and scaled by s (optionally another shape x63 or a distortion)"""
    info = T.synth_info(x=X0, nuis=nuis)
    mb = T.mu_law(nuis['mu_inf'], nuis['ell'], 6.3)
    i = s * T.curve(T.VG_M - dv, x63 or X0, 6.3, T.QF0 + nuis['dQf'], mb)
    if distort: i = distort(T.VG_M, i)
    info[6.3] = dict(info[6.3], i=i, ion=float(i[-1]))
    r = 10 * max(info[t]['floor'] / info[t]['ion'] for t in info)
    for t in info: info[t]['a1_window'] = (r * info[t]['ion'], 10 * r * info[t]['ion'])
    return info


LABG = {2.0: 'c10_s3_11_2p0', 6.3: 'c10_s3_12_6p3', 13.2: 'c10_s3_13_13p2'}   # S3-11 / S3-12 / S3-13 (IGZO.TOKYO, GAMMA0 -0.31)
CHECK = {'PASS': 'PASS: profiling exact within 0.01 dec on every J-window point', 'FAIL': 'FAIL: profiling approximate -> every S4b candidate run natively',
         'UNV': 'UNVERIFIED (not every J-window point is covered in either direction)'}


def runs(x=X0, films=T.FILMS, labels=LAB, **kw):
    """baseline-like synthetic runs: the 2.0 nm run carries the quasi-2D NC override (S0-01), labels as the matrix"""
    return {t: T.synth_run(t, x, rid=f'syn_{labels[t]}', overrides=Q2D if t == 2.0 else (), label=labels[t], **kw) for t in films}


def mkconf(role, ref, verdict='PASS', eligible=True):
    """a sealed native-confirmation record (profile_s4s5.native_confirmation) of a synthetic native endpoint against the reference run;
    the unchanged profile_shared.check needs run directories, so a checker returning the given verdict is injected"""
    lab = {'S1-07': 'c10_s1_07_2p0', 'S3-27': 'c10_s3_27_6p3'}[role]
    nat = T.synth_run(ref['t'], ref['x'], qf=T.QF0 + 1e12, label=lab, rid=f'native_{role}', overrides=Q2D if ref['t'] == 2.0 else ())
    if not eligible: nat['eligibility'] = {'eligible': False, 'problems': ['runner status TIMEOUT', 'timed out'], 'timed_out': True}
    return P.native_confirmation(nat, ref, role, checker=lambda a, b: {'verdict': CHECK[verdict]})


def info_d3():
    """2.0 / 13.2 nm truth = baseline start (true dV0 = +0.21 V); 6.3 nm truth = the IGZO-like shape: fits and adoption profiles covered"""
    NU = dict(T.TRUE_NUIS, dQf=-1.2e12)
    info = T.synth_info(x=X0, nuis=NU); i63 = T.curve(T.VG_M, XG, 6.3, T.QF0 + NU['dQf'], T.mu_law(80, 9, 6.3)); info[6.3] = dict(info[6.3], i=i63, ion=float(i63[-1]))
    return info


def cases_regressions_v3(ok):
    """Codex v2 review 2026-10-13 ~03:10Z, fixes 3 (consumer side) and 4: one isolated case per counterexample"""
    def case(name, fn):
        try: cond, info = fn()
        except BaseException as e: cond, info = False, f'{type(e).__name__}: {str(e)[:300]}'
        ok(name, cond, info)
    base, ig = runs(), runs(XG, labels=LABG); info4 = info_d3()
    def raw_dict():
        d = H.igzo_prediction(base, ig, {'verdict': CHECK['PASS']}, info4)
        return all(d[k].startswith('unresolved') for k in ('a_gain', 'b_gamma_6p3', 'c_gamma_13p2', 'd_not_adopted', 'verdict')), f'gate {str(d.get("gate_S3_27"))[:80]}'
    case('REGRESSION v3 fix 3 (Codex: H-F accepts an unbound check PASS): a raw check dict is not a confirmation; every D3 part unresolved', raw_dict)
    def substitute():
        rec07 = mkconf('S1-07', base[2.0])
        d = H.igzo_prediction(base, ig, rec07, info4)
        sh = {k: dict(H.shape_fit(r, info4[6.3])) for k, r in (('S1-01', base[6.3]), ('S3-12', ig[6.3]))}
        sh['S3-10'] = dict(sh['S1-01'], label=H.ROLES['S3-10'], run='syn_s3_10', digest='d-s3-10')
        t = H.contact_trigger(sh, rec07)
        return d['verdict'].startswith('unresolved') and t['verdict'].startswith('UNRESOLVED'), f'D3 {d["verdict"][:40]}; D4 {t["verdict"][:70]}'
    case('REGRESSION v3 fix 3 (Codex: an unrelated S1-07 PASS substitutes for S3-27): D3 and D4 stay unresolved', substitute)
    def timed_out():
        rec = mkconf('S3-27', ig[6.3], eligible=False); d = H.igzo_prediction(base, ig, rec, info4)
        return rec['verdict'].startswith('UNKNOWN') and d['verdict'].startswith('unresolved'), f'{rec["verdict"][:60]}; D3 {d["verdict"][:40]}'
    case('REGRESSION v3 fix 3: a timed-out S3-27 endpoint gives an UNKNOWN confirmation (never PASS); D3 unresolved', timed_out)
    def other_reference():
        other = T.synth_run(6.3, XG, label=LABG[6.3], rid='another_s3_12', extra_shift=0.01)
        d = H.igzo_prediction(base, ig, mkconf('S3-27', other), info4)
        return d['verdict'].startswith('unresolved') and 'digest' in d['gate_S3_27'], d['gate_S3_27'][:100]
    case('REGRESSION v3 fix 3: an S3-27 PASS bound to another S3-12 run (reference digest differs) does not confirm this S3-12', other_reference)
    def wrong_film():
        info = info_with_63(0.28, 0.25, distort=lambda v, i: i * 10 ** (0.5 * np.sin(1.5 * v)))
        try: b = H.baseline_shape(base[13.2], info); return False, f'accepted the 13.2 nm S1-02 curve: shape {b["fit"]["shape_rmse_dec"]}, {b["verdict"][:40]}'
        except SystemExit as e: return 'S1-01' in str(e), str(e)[:140]
    case('REGRESSION v3 fix 4 (Codex: baseline shape accepts the wrong film): S1-02 (13.2 nm) against the 6.3 nm target is refused', wrong_film)
    def wrong_route():
        bad = {'verdict': 'FAIL (shape RMSE <= 0.15 dec)', 'fit': {'valid': True, 'shape_rmse_dec': 0.10, 'film_nm': 13.2, 'label': 'c10_s1_02_13p2'}}
        f = H.falsification(bad, _triple(['PASS', 'FAIL: dVth_cc_V', 'PASS'], conf=None), [{'name': H.IGZO_BRANCH, 'triple': _triple(['FAIL: x', 'PASS', 'PASS'], kind='IGZO', conf=None)}],
                            [H.IGZO_BRANCH])
        return not f['verdict'].startswith('FALSIFIED'), f['verdict'][:100]
    case('REGRESSION v3 fix 4: a shape fit of S1-02 (13.2 nm, RMSE 0.10) cannot falsify H-F through the baseline shape route', wrong_route)
    def wrong_roles():
        R = runs(); info = info_with_63()
        try: H.two_film_reference(R[2.0], R[13.2], T.synth_run(6.3, X0, label='c10_s6_02_6p3'), info); r1 = False
        except SystemExit as e: r1 = 'S1-01' in str(e)
        ig2 = dict(ig); ig2[6.3] = T.synth_run(6.3, XG, label='c10_s3_14_6p3')
        try: H.igzo_prediction(base, ig2, mkconf('S3-27', ig[6.3]) if hasattr(P, 'native_confirmation') else None, info4); r2 = False
        except SystemExit as e: r2 = 'S3-12' in str(e)
        sf = {'shape_rmse_dec': 0.3, 'valid': True, 'film_nm': 6.3}
        t = H.contact_trigger({'S1-01': sf, 'S3-10': sf, 'S3-12': sf}, None)
        return r1 and r2 and t['verdict'].startswith('UNRESOLVED'), f'D1 role refused {r1}; D3 role refused {r2}; D4 unlabelled {t["verdict"][:40]}'
    case('REGRESSION v3 fix 4: role identity in D1-D4 (a 6.3 nm run that is not S1-01, an IGZO run that is not S3-12, unlabelled D4 fits)', wrong_roles)


def cases_regressions_v4(ok):
    """Codex v3 review 2026-10-13 (FIX_FIRST), counterexample 1: D5 can bypass IGZO confirmation through the native route; ruling (ii):
    the contacts native route counts only once its run roles and one shared contact model are registered - until then it is unavailable"""
    def case(name, fn):
        try: cond, info = fn()
        except BaseException as e: cond, info = False, f'{type(e).__name__}: {str(e)[:300]}'
        ok(name, cond, info)
    onef = _triple(['PASS', 'FAIL: dVth_cc_V', 'PASS'])
    nat = {t: {'kind': 'native', 'verdict': 'PASS', 'eligible': True, 'digest': f'd-native-{t}'} for t in T.FILMS}
    def igzo_native():
        f = H.falsification(SH_RES, onef, [{'name': H.IGZO_BRANCH, 'native_acceptance': nat}], [H.IGZO_BRANCH])
        row = [r for r in f['rows'] if r.get('branch')][0]
        return f['verdict'].startswith('UNRESOLVED') and row['fires'] is None, f'{f["verdict"][:90]} / row: {str(row.get("why"))[:80]}'
    case('REGRESSION v4 fix 1 (Codex v3: three native PASS records under the IGZO branch name falsify without S3-27): UNRESOLVED, never FALSIFIED', igzo_native)
    def igzo_both():
        f = H.falsification(SH_RES, onef, [{'name': H.IGZO_BRANCH, 'native_acceptance': nat, 'triple': _triple(['FAIL: x', 'PASS', 'PASS'], kind='IGZO')}], [H.IGZO_BRANCH])
        return not f['verdict'].startswith('FALSIFIED'), f['verdict'][:100]
    case('REGRESSION v4 fix 1: a native route attached to the IGZO branch next to its triple cannot falsify (native route refused for IGZO)', igzo_both)
    def contacts_disabled():
        f = H.falsification(SH_RES, onef, [{'name': H.IGZO_BRANCH, 'triple': _triple(['FAIL: x', 'PASS', 'PASS'], kind='IGZO')},
                                           {'name': H.CONTACT_BRANCH, 'native_acceptance': nat}], [H.IGZO_BRANCH, H.CONTACT_BRANCH])
        row = [r for r in f['rows'] if r['name'] == H.CONTACT_BRANCH][0]
        return (f['verdict'].startswith('UNRESOLVED') and row['fires'] is None and 'unavailable' in str(row['why'])
                and H.CONTACT_ROUTE_AVAILABLE is False), f'{f["verdict"][:90]} / {str(row["why"])[:90]}'
    case('REGRESSION v4 fix 1 / ruling (ii): the contacts native route is explicitly unavailable (roles and shared contact model not registered): '
         'native PASS at all films -> UNRESOLVED', contacts_disabled)
    def other_name():
        f = H.falsification(SH_RES, onef, [{'name': H.IGZO_BRANCH, 'triple': _triple(['FAIL: x', 'PASS', 'PASS'], kind='IGZO')},
                                           {'name': 'unregistered branch', 'native_acceptance': nat}], [H.IGZO_BRANCH])
        row = [r for r in f['rows'] if r['name'] == 'unregistered branch'][0]
        return not f['verdict'].startswith('FALSIFIED') and row['fires'] is None, f['verdict'][:100]
    case('REGRESSION v4 fix 1: a native route under an unregistered branch name cannot falsify', other_name)


def cases(ok):
    R = runs()
    # ---- D1 two-film reference (ruling 2): exact recovery, separate and joint scores, degeneracy, diagnostic direct dV_th
    d1 = H.two_film_reference(R[2.0], R[13.2], R[6.3], info_with_63(0.28, 0.25))
    ok('D1: recovers the needed shift +0.28 V and scale 0.25 of a synthetic 6.3 nm anomaly -> PASS (shift, scale and joint scored)',
       abs(d1['needed_shift_V'] - 0.28) < 2e-3 and abs(d1['needed_scale'] / 0.25 - 1) < 1e-2 and d1['scored'] == {'shift': 'PASS', 'scale': 'PASS', 'joint': 'PASS'}
       and d1['verdict'] == 'PASS', f'shift {d1["needed_shift_V"]:.4f} V, scale {d1["needed_scale"]:.4f}, shape {d1["free_fit_6p3"]["shape_rmse_dec"]:.2e}')
    dg = d1['diagnostic_direct_dVth']
    ok('D1: the direct V_th,cc difference is a labelled DIAGNOSTIC (not scored); for a rigid anomaly it exceeds the shift (scale effect at 1e-9 A/um)',
       dg['dVth_cc_meas_minus_pred_V'] is not None and dg['dVth_cc_meas_minus_pred_V'] > 0.28 and 'DIAGNOSTIC' in dg['label'], f'{dg["dVth_cc_meas_minus_pred_V"]:.4f} V')
    ok('D1: the two-film training uses the quasi-2D 2.0 nm and 13.2 nm only and recovers the true mu law', d1['training']['films'] == [2.0, 13.2]
       and abs(d1['training']['profiled']['mu_inf_cm2Vs'] / 80 - 1) < 1e-3 and abs(d1['training']['profiled']['ell_nm'] - 9) < 0.05)
    d1b = H.two_film_reference(R[2.0], R[13.2], R[6.3], info_with_63(0.40, 0.25))
    d1c = H.two_film_reference(R[2.0], R[13.2], R[6.3], info_with_63(0.25, 0.60))
    ok('D1: shift outside 0.20..0.36 V -> shift FAIL; scale outside 0.15..0.35 -> scale FAIL; each scored separately, the joint fails',
       d1b['scored'] == {'shift': 'FAIL', 'scale': 'PASS', 'joint': 'FAIL'} and d1c['scored'] == {'shift': 'PASS', 'scale': 'FAIL', 'joint': 'FAIL'})
    d1n = H.two_film_reference(R[2.0], R[13.2], R[6.3], info_with_63(-0.10, 0.25))
    ok('D1 sign convention: an anomaly to more NEGATIVE V_G gives a negative needed shift (FAIL against +0.28)',
       abs(d1n['needed_shift_V'] + 0.10) < 2e-3 and d1n['shift_verdict'] == 'FAIL', f'{d1n["needed_shift_V"]:.4f} {d1n["shift_verdict"]}')
    d1m = H.two_film_reference(R[2.0], R[13.2], R[6.3], info_with_63(-0.28, 0.25))
    ok('D1: a needed shift that moves the on window past +3 V (here -0.28 V) is unresolved (no extrapolation), never FAIL/PASS', d1m['verdict'].startswith('unresolved'), d1m['verdict'])
    ok('band(): both edges inclusive, outside fails', H.band(0.20, 0.20, 0.36) == 'PASS' and H.band(0.36, 0.20, 0.36) == 'PASS' and H.band(0.35, 0.15, 0.35) == 'PASS'
       and H.band(0.1999, 0.20, 0.36) == 'FAIL' and H.band(0.3501, 0.15, 0.35) == 'FAIL')
    R2 = dict(R); R2[6.3] = T.synth_run(6.3, X0, qf=T.QF0 + 1e11, label=LAB[6.3])
    try: H.two_film_reference(R2[2.0], R2[13.2], R2[6.3], info_with_63()); r1 = False
    except SystemExit: r1 = True
    R3 = dict(R); R3[2.0] = T.synth_run(2.0, X0, label=LAB[2.0], overrides=())   # the S0-01 role without the quasi-2D NC (as S1-05)
    try: H.two_film_reference(R3[2.0], R3[13.2], R3[6.3], info_with_63()); r2 = False
    except SystemExit as e: r2 = 'quasi-2D' in str(e)
    ok('D1 refuses a 6.3 nm run off the start parameters (other Q_f) and a 2.0 nm run without the quasi-2D NC (3-D NC S1-05)', r1 and r2)
    d1x = H.two_film_reference(R[2.0], R[13.2], R[6.3], info_with_63(0.70, 0.25))
    ok('D1: a free shift beyond the +-0.5 V bound is unresolved, never PASS/FAIL', d1x['verdict'].startswith('unresolved'), d1x['verdict'])
    d1q = H.two_film_reference(R[2.0], R[13.2], R[6.3], info_with_63(0.28, 0.25, nuis=dict(NUIS0, mu_inf=450.0)))
    ok('D1: a two-film training profile at a range bound (mu_inf 300) is not qualified -> unresolved', d1q['verdict'].startswith('unresolved')
       and 'not qualified' in d1q['verdict'], d1q['verdict'][:100])
    dr = d1['degeneracy_ranges']
    ok('D1 reports the shift and scale degeneracy ranges around the scored optimum', dr['needed_shift_V'][0] <= d1['needed_shift_V'] <= dr['needed_shift_V'][1]
       and dr['needed_scale'][0] <= d1['needed_scale'] * (1 + 1e-9) and d1['needed_scale'] <= dr['needed_scale'][1] * (1 + 1e-9))
    # ---- D2 baseline shape (ruling 1)
    d2a = H.baseline_shape(R[6.3], info_with_63(0.28, 0.25))
    wig = lambda v, i: i * 10 ** (0.5 * np.sin(1.5 * v))
    d2b = H.baseline_shape(R[6.3], info_with_63(0.28, 0.25, distort=wig))
    ok('D2: a pure shift/scale anomaly has shape RMSE ~0 -> FAIL; a shape distortion -> > 0.15 dec -> PASS',
       d2a['fit']['shape_rmse_dec'] < 1e-3 and d2a['verdict'].startswith('FAIL') and d2b['fit']['shape_rmse_dec'] > 0.15 and d2b['verdict'].startswith('PASS'),
       f'{d2a["fit"]["shape_rmse_dec"]:.2e} / {d2b["fit"]["shape_rmse_dec"]:.3f}')
    try: H.baseline_shape(T.synth_run(6.3, T.TRUE, label=LAB[6.3]), info_with_63()); r3 = False
    except SystemExit as e: r3 = 'start parameters' in str(e)
    ok('D2: "baseline" = S1-01 at the start parameters; another point is refused; D1/D2 carry the retrospective disclosure (inputs seen, V2 known)',
       r3 and 'RETROSPECTIVE' in d2a['disclosure'] and '0.036' in d1['disclosure'])
    f = H.shape_fit(R[6.3], info_with_63(0.13, 0.4)[6.3])
    ok('shape_fit: shift relative to the run = anomaly shift (dQf = 0 here), scale = anomaly scale x law ratio',
       abs(f['free_dV_V'] - 0.13) < 2e-3 and abs(f['free_scale'] / (0.4 * T.mu_law(80, 9, 6.3) / R[6.3]['mu_band']) - 1) < 1e-2)
    rx = dict(R[6.3], eligibility={'eligible': False, 'problems': ['timed out']})
    try: H.shape_fit(rx, info_with_63()[6.3]); r4 = False
    except SystemExit as e: r4 = 'not eligible' in str(e)
    ok('shape_fit refuses an ineligible run (B1: validated before fitting)', r4)
    # ---- D3 IGZO (ruling 3)
    base, ig = runs(), runs(XG, labels=LABG)
    PASS27 = mkconf('S3-27', ig[6.3])   # sealed S3-27 record bound to this S3-12 (v2 fix 3)
    infoU = T.synth_info(x=X0, nuis=dict(T.TRUE_NUIS, dQf=+1.0e12)); i63 = T.curve(T.VG_M, XG, 6.3, T.QF0 + 1.0e12, T.mu_law(80, 9, 6.3))
    infoU[6.3] = dict(infoU[6.3], i=i63, ion=float(i63[-1]))
    d3 = H.igzo_prediction(base, ig, PASS27, infoU)
    ok('D3: an adoption profile with < 95 % window coverage leaves d unresolved (never a pass by default)', d3['d_not_adopted'].startswith('unresolved'), d3['d_not_adopted'][:90])
    NU = dict(T.TRUE_NUIS, dQf=-1.2e12)   # true dV0 = +0.21 V: the S1-01 and S3-12 free fits and the adoption profiles stay covered
    info4 = T.synth_info(x=X0, nuis=NU); i64 = T.curve(T.VG_M, XG, 6.3, T.QF0 + NU['dQf'], T.mu_law(80, 9, 6.3)); info4[6.3] = dict(info4[6.3], i=i64, ion=float(i64[-1]))
    d3w = H.igzo_prediction(base, ig, PASS27, info4)
    ok('D3: IGZO-like branch fits 6.3 nm only -> shape gain >= 0.05 dec (primary) and an ACTUAL worsening at 2.0/13.2 (d PASS)',
       d3w['a_gain'] == 'PASS' and d3w['d_not_adopted'].startswith('PASS (actual worsening'), f'gain {d3w["a_gain_dec"]}; d {d3w["d_not_adopted"]}; adoption {d3w["d_adoption"]}')
    g = d3w['gamma_native']; lo, hi = H.HF['gamma_6p3']
    exp_b = H.toward_band(g['S1-01']['gamma'], g['S3-12']['gamma'], lo, hi) if (H._gamma_ok(g['S1-01']) and H._gamma_ok(g['S3-12'])) else 'unresolved'
    ok('D3 b/c: verdicts follow the native power-law gammas (b "toward" the band, c >= 0.5); a failed/bound fit is unresolved',
       d3w['b_gamma_6p3'][:4] == exp_b[:4] and (d3w['c_gamma_13p2'] == ('PASS' if g['S3-13']['gamma'] >= 0.5 else 'FAIL') if H._gamma_ok(g['S3-13']) else d3w['c_gamma_13p2'].startswith('unresolved')),
       f'b {d3w["b_gamma_6p3"]}; c {d3w["c_gamma_13p2"]}; gammas {[round(v.get("gamma") or float("nan"), 3) for v in g.values()]}')
    tb = H.toward_band
    ok('D3 b "toward" (ruling 3): reduced distance, or staying inside when the baseline is inside',
       tb(1.6, 1.4, 0.9, 1.3).startswith('PASS') and tb(1.6, 1.7, 0.9, 1.3).startswith('FAIL') and tb(1.0, 1.2, 0.9, 1.3).startswith('PASS')
       and tb(1.0, 1.35, 0.9, 1.3).startswith('FAIL') and tb(0.5, 0.6, 0.9, 1.3).startswith('PASS') and tb(0.5, 1.75, 0.9, 1.3).startswith('FAIL'))
    def conj(d):
        parts = [d[k] for k in ('a_gain', 'b_gamma_6p3', 'c_gamma_13p2', 'd_not_adopted')]
        return 'PASS' if all(x.startswith('PASS') for x in parts) else 'FAIL' if any(x.startswith('FAIL') for x in parts) else 'unresolved'
    ok('D3: overall = conjunction of a-d (any FAIL -> FAIL; otherwise any unresolved -> unresolved)', d3['verdict'] == conj(d3) and d3w['verdict'] == conj(d3w),
       f'{d3["verdict"]} / {d3w["verdict"]}')
    info_all = T.synth_info(x=XG, nuis=NU)
    d3b = H.igzo_prediction(base, ig, PASS27, info_all)
    ok('D3 d: IGZO better at every film -> adopted -> d FAIL', d3b['d_not_adopted'].startswith('FAIL (IGZO passes'), d3b['d_not_adopted'])
    d3c = H.igzo_prediction(base, ig, mkconf('S3-27', ig[6.3], 'FAIL'), info4)
    d3d = H.igzo_prediction(base, ig, None, info4)
    ok('D3: without an S3-27 PASS every part is unresolved (register: native confirmation before any branch counts)',
       all(d3c[k].startswith('unresolved') for k in ('a_gain', 'b_gamma_6p3', 'c_gamma_13p2', 'd_not_adopted', 'verdict')) and d3d['verdict'].startswith('unresolved'))
    try: H.igzo_prediction(base, runs(dict(X0, g0=0.2), labels=LABG), PASS27, info4); r5 = False
    except SystemExit as e: r5 = 'start parameters' in str(e)
    ok('D3: the IGZO runs must be S3-11/12/13 (start parameters, GAMMA0 -0.31); another seed is refused', r5)
    # ---- D4 contact trigger (ruling 4, reading A, exact roles)
    sf = lambda v, role, valid=True, label=None: {'shape_rmse_dec': v, 'valid': valid, 'film_nm': 6.3, 'label': label or H.ROLES[role],
                                                  'digest': P.run_digest(ig[6.3]) if role == 'S3-12' else f'd-{role}'}
    sh = lambda a, b, c, **kw: {'S1-01': sf(a, 'S1-01'), 'S3-10': sf(b, 'S3-10', **kw), 'S3-12': sf(c, 'S3-12')}
    t1 = H.contact_trigger(sh(0.3, 0.25, 0.2), PASS27)
    t2 = H.contact_trigger(sh(0.3, 0.25, 0.1), PASS27)
    t4 = H.contact_trigger(sh(0.3, 0.25, 0.2, valid=False), PASS27)
    t5 = H.contact_trigger(sh(0.15, 0.25, 0.2), PASS27)
    t6 = H.contact_trigger(sh(0.3, 0.25, 0.2, label='c10_s3_11_2p0'), PASS27)
    ok('D4: fires only if every prescribed 6.3 nm shape RMSE > 0.15; invalid -> UNRESOLVED; 0.15 does not fire; a fit from the wrong run -> UNRESOLVED',
       t1['verdict'].startswith('FIRE') and t2['verdict'].startswith('DO NOT') and t4['verdict'].startswith('UNRESOLVED') and t5['verdict'].startswith('DO NOT')
       and t6['verdict'].startswith('UNRESOLVED'))
    ok('D5 prescribed set from D4: FIRE -> IGZO + contacts; DO NOT FIRE -> IGZO; UNRESOLVED -> unknown (None)',
       H.prescribed_branches(t1) == [H.IGZO_BRANCH, H.CONTACT_BRANCH] and H.prescribed_branches(t2) == [H.IGZO_BRANCH] and H.prescribed_branches(t4) is None)
    # ---- D5 falsification (ruling 4 + B4)
    NOSH = {'verdict': 'FAIL (shape RMSE <= 0.15 dec)', 'fit': {'valid': True, 'shape_rmse_dec': 0.1, 'film_nm': 6.3, 'label': 'c10_s1_01_6p3'}}
    UNSH = {'verdict': 'unresolved (shift at the +-0.5 V bound)', 'fit': {'valid': False}}
    allp, onef = _triple(['PASS'] * 3), _triple(['PASS', 'FAIL: dVth_cc_V', 'PASS'])
    gall, gone = _triple(['PASS'] * 3, kind='IGZO'), _triple(['PASS', 'FAIL: dVth_cc_V', 'PASS'], kind='IGZO')
    IG = lambda tri: {'name': H.IGZO_BRANCH, 'triple': tri}
    pres = [H.IGZO_BRANCH]
    f1 = H.falsification(SH_RES, allp, [IG(gone)], pres)
    f2 = H.falsification(SH_RES, onef, [IG(gall)], pres)
    f3 = H.falsification(SH_RES, onef, [IG(_triple(['PASS'] * 3, kind='IGZO', conf='FAIL'))], pres)
    f4 = H.falsification(SH_RES, onef, [IG(gone), {'name': 'no tail S3-10 (6.3 nm only)', 'triple': None}], pres)
    f5 = H.falsification(SH_RES, _triple(['PASS'] * 3, conf=None), [IG(gone)], pres)
    f6 = H.falsification(NOSH, onef, [IG(gone)], pres)
    f7 = H.falsification(UNSH, onef, [IG(gone)], pres)
    f8 = H.falsification(SH_RES, onef, [IG(gone)], [H.IGZO_BRANCH, H.CONTACT_BRANCH])
    nat = {t: {'kind': 'native', 'verdict': 'PASS', 'eligible': True, 'digest': f'd-contacts-{t}'} for t in T.FILMS}
    f9 = H.falsification(SH_RES, onef, [IG(gone), {'name': H.CONTACT_BRANCH, 'native_acceptance': nat}], [H.IGZO_BRANCH, H.CONTACT_BRANCH])
    f10 = H.falsification(SH_RES, onef, [IG(_triple(['PASS'] * 3, kind='IGZO', conf='UNV'))], pres)
    nat2 = dict(nat); nat2[6.3] = dict(nat[6.3], eligible=False)
    f11 = H.falsification(SH_RES, onef, [IG(gone), {'name': H.CONTACT_BRANCH, 'native_acceptance': nat2}], [H.IGZO_BRANCH, H.CONTACT_BRANCH])
    ok('D5 (ruling e): an unevaluable IGZO confirmation (UNVERIFIED check) is UNKNOWN -> UNRESOLVED; contacts native 5.3 needs eligible identified runs',
       f10['verdict'].startswith('UNRESOLVED') and f11['verdict'].startswith('UNRESOLVED'), f10['verdict'][:60] + ' / ' + f11['verdict'][:60])
    ok('D5: a qualified baseline triple passing at all films falsifies; a confirmed branch passing falsifies; an unconfirmed one cannot (listed)',
       f1['verdict'].startswith('FALSIFIED (baseline (5.3') and f2['verdict'].startswith(f'FALSIFIED ({H.IGZO_BRANCH}') and f3['verdict'].startswith('NOT FALSIFIED')
       and H.IGZO_BRANCH in f3['not_confirmed'])
    ok('D5: a VALID shape fit without residual falsifies (shape route); an unresolved shape route or an unconfirmed baseline transformation -> UNRESOLVED',
       f6['verdict'].startswith('FALSIFIED (baseline (shape') and f7['verdict'].startswith('UNRESOLVED') and f5['verdict'].startswith('UNRESOLVED'))
    ok('D5: a non-prescribed one-film branch (S3-10) does not block; a missing prescribed contacts branch -> UNRESOLVED; native 5.3 of contacts at all films '
       'is UNRESOLVED while the contacts route is unavailable (v4, Codex v3 fix 1 / ruling ii)',
       f4['verdict'].startswith('NOT FALSIFIED') and f8['verdict'].startswith('UNRESOLVED') and f9['verdict'].startswith('UNRESOLVED'))
    tri = [R[t] for t in T.FILMS]
    pa = H.profiled_triple_acceptance(tri, T.synth_info(x=X0), confirmation=mkconf('S1-07', R[2.0]))   # true dV0 = +0.08 V: the profiled curves cover 3 V
    pu = H.profiled_triple_acceptance(tri, T.synth_info(x=X0))
    ok('D5 helper: the qualified profiled triple that equals the truth passes 5.3 at every film (kind profiled); without the S1-07 PASS it is unqualified, '
       'every film unresolved', pa['qualified'] and all(a['verdict'] == 'PASS' and a['kind'] == 'profiled' for a in pa['acceptance'].values())
       and not pu['qualified'] and all(a['verdict'].startswith('unresolved') for a in pu['acceptance'].values()),
       str({t: a['verdict'][:30] for t, a in pa['acceptance'].items()}))
    pn = H.profiled_triple_acceptance(tri, T.synth_info(x=X0, nuis=dict(T.TRUE_NUIS, dQf=+0.3e12)), confirmation=mkconf('S1-07', R[2.0]))   # dV0 = -0.054 V
    ok('D5 helper: a profiled curve moved to negative V_G leaves I_D(3 V) unresolved (no extrapolation), so 5.3 cannot pass offline',
       all(a['criteria']['Id3V_err_pct']['ok'] is None and not a['verdict'].startswith('PASS') for a in pn['acceptance'].values()))
    s5 = H.s5_fold_6p3()
    ok('S5 fold leaving out 6.3 nm: "test listed, no separate H-F prediction"; H-J forecast retained (ruling 5)',
       s5['verdict'].startswith('NO H-F PREDICTION') and 'H-J' in s5['forecast'])
    # ---- DRAFT labelling
    outs = [d1, d2a, d3, d3c, t1, f1, pa, s5]
    ok('every H-F result carries the DRAFT status, the register tag and the rulings note', all(o['status'] == H.STATUS and 'NOT frozen' in o['status']
       and o['register_tag'] == H.TAG and 'Codex rulings 2026-10-13' in o['rulings'] for o in outs))
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()): codes = (H.main(['two_film_reference', 'a', 'b', 'c']), H.main([]))
    ok('the CLI has no scoring command (only selftest)', codes == (2, 2))


PASS27 = {'verdict': 'PASS: profiling exact within 0.01 dec on every J-window point'}
SH_RES = {'verdict': 'PASS (shape RMSE > 0.15 dec: the prediction holds)', 'fit': {'valid': True, 'shape_rmse_dec': 0.3, 'film_nm': 6.3, 'label': 'c10_s1_01_6p3'}}


_REF = {}


def _triple(verdicts, valid=True, kind='baseline', conf='PASS', at_bound=False):
    """a profiled-triple result as profiled_triple_acceptance returns it: kind, role labels, run digests and the bound native-confirmation
    record (S1-07 for the baseline, S3-27 for IGZO; conf None = no record); falsification recomputes the qualification from these"""
    if not _REF: _REF.update(baseline=runs(), IGZO=runs(XG, labels=LABG))
    R = _REF[kind]; role, ft = ('S1-07', 2.0) if kind == 'baseline' else ('S3-27', 6.3)
    return {'kind': kind, 'labels': {str(t): R[t]['label'] for t in T.FILMS},
            'profile': {'valid': valid, 'verdict': 'OK' if valid else 'UNVERIFIED (optimizer not converged: confirm natively)', 'films': list(T.FILMS),
                        'run_digests': [P.run_digest(R[t]) for t in T.FILMS], 'profiled': {'at_bound': {'dV0': at_bound, 'mu_inf': False, 'ell': False}}},
            'confirmation': mkconf(role, R[ft], conf) if conf else None, 'acceptance': {t: {'verdict': v} for t, v in zip(T.FILMS, verdicts)}}


def cases_regressions(ok):
    """Codex review 2026-10-13 ~01:55Z, blocker B4 (and the D4 role rule): one isolated case per counterexample"""
    def case(name, fn):
        try: cond, info = fn()
        except BaseException as e: cond, info = False, f'{type(e).__name__}: {str(e)[:300]}'
        ok(name, cond, info)
    def unverified():
        R = runs(); info = T.synth_info(x=X0); real = P.profile_films
        def unv(*a, **k):
            p = real(*a, **k); return dict(p, valid=False, verdict='UNVERIFIED (coverage < 95 % or optimizer not converged: confirm natively)')
        P.profile_films = unv
        try:
            pa0 = H.profiled_triple_acceptance([R[t] for t in T.FILMS], info)
            leak = [t for t, a in pa0['acceptance'].items() if a['verdict'] == 'PASS']
            try: pa1 = H.profiled_triple_acceptance([R[t] for t in T.FILMS], info, confirmation=mkconf('S1-07', R[2.0]))
            except TypeError as e: return False, f'PASS verdicts from an UNVERIFIED profile: {leak}; {e}'
        finally:
            P.profile_films = real
        return (not leak and pa1['qualified'] is False and any('UNVERIFIED' in q or 'not valid' in q for q in pa1['qualification'])
                and not any(a['verdict'] == 'PASS' for a in pa1['acceptance'].values())), f'PASS verdicts from an UNVERIFIED profile: {leak}'
    case('REGRESSION B4 (Codex: an UNVERIFIED profile supplies all-PASS 5.3 acceptance): no PASS leaves an unqualified profile', unverified)
    def unverified_route():
        f = H.falsification(SH_RES, _triple(['PASS'] * 3, valid=False), [{'name': H.IGZO_BRANCH, 'triple': _triple(['FAIL: x', 'PASS', 'PASS'], kind='IGZO')}],
                            [H.IGZO_BRANCH])
        return f['verdict'].startswith('UNRESOLVED'), f['verdict'][:120]
    case('REGRESSION B4: an all-PASS baseline triple from an UNVERIFIED profile cannot falsify H-F (5.3 route unresolved)', unverified_route)
    def missing_branch():
        bt = _triple(['PASS', 'FAIL: dVth_cc_V', 'PASS']); ig = _triple(['FAIL: Id3V_err_pct', 'PASS', 'PASS'], kind='IGZO')
        ig0 = _triple(['FAIL: Id3V_err_pct', 'PASS', 'PASS'], kind='IGZO', conf=None); B = H.IGZO_BRANCH
        f1 = H.falsification(SH_RES, bt, [], [B])
        f2 = H.falsification(SH_RES, bt, [{'name': B, 'triple': ig}], [B])
        f3 = H.falsification(SH_RES, bt, [{'name': B, 'triple': ig0}], [B])
        f4 = H.falsification(SH_RES, bt, [{'name': B, 'triple': ig}], None)
        return (f1['verdict'].startswith('UNRESOLVED') and f2['verdict'].startswith('NOT FALSIFIED') and f3['verdict'].startswith('UNRESOLVED')
                and f4['verdict'].startswith('UNRESOLVED')), ' / '.join(f['verdict'][:40] for f in (f1, f2, f3, f4))
    case('REGRESSION B4 (Codex: a missing prescribed branch is not UNRESOLVED): missing branch, missing native confirmation or an unknown '
         'prescribed set -> UNRESOLVED', missing_branch)
    ig12 = runs(XG, labels=LABG)[6.3]
    sf = lambda v, role: {'shape_rmse_dec': v, 'valid': True, 'film_nm': 6.3, 'label': H.ROLES.get(role, 'x'), 'digest': P.run_digest(ig12) if role == 'S3-12' else f'd-{role}'}
    def trigger_unconfirmed():
        sh = {'S1-01': sf(0.3, 'S1-01'), 'S3-10': sf(0.25, 'S3-10'), 'S3-12': sf(0.1, 'S3-12')}
        t1 = H.contact_trigger(sh, mkconf('S3-27', ig12, 'FAIL'))
        t2 = H.contact_trigger(sh, None)
        return t1['verdict'].startswith('UNRESOLVED') and t2['verdict'].startswith('UNRESOLVED'), f'{t1["verdict"][:50]} / {t2["verdict"][:50]}'
    case('REGRESSION ruling 4: missing or unconfirmed IGZO (S3-27) makes the contact trigger UNRESOLVED (S3-12 never silently dropped)', trigger_unconfirmed)
    def trigger_roles():
        t = H.contact_trigger({'S1-01': sf(0.3, 'S1-01'), 'S3-10': sf(0.25, 'S3-10'), 'S3-12': sf(0.2, 'S3-12'), 'S3-11': sf(0.4, 'S3-11')}, mkconf('S3-27', ig12))
        return t['verdict'].startswith('UNRESOLVED') and 'roles' in t['verdict'], t['verdict'][:100]
    case('ruling 4: the trigger takes exactly the prescribed roles (S1-01, S3-10, S3-12)', trigger_roles)


def main(argv=()):
    res = []
    def ok(name, cond, info=''): res.append((name, bool(cond), info))
    P.STARTS = np.linspace(-0.4, 0.4, 3)
    if '--regressions-only' not in argv and '--v3-only' not in argv and '--v4-only' not in argv:
        try: cases(ok)
        except Exception as e:
            import traceback; ok(f'cases raised {type(e).__name__}: {e}', False, traceback.format_exc()[-1200:])
    if '--v3-only' not in argv and '--v4-only' not in argv: cases_regressions(ok)
    if '--v4-only' not in argv: cases_regressions_v3(ok)
    cases_regressions_v4(ok)
    for n, p, i in res: print(('ok   ' if p else 'FAIL ') + n + (f'   [{i}]' if i else ''))
    print(f'{sum(p for _, p, _ in res)}/{len(res)} ok')
    return 0 if all(p for _, p, _ in res) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
