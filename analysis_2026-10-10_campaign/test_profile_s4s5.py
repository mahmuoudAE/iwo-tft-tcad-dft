#!/usr/bin/env python3
"""Tests for profile_s4s5.py (2026-10-13). Synthetic transfer curves and synthetic "measured" curves only, plus a REAL-FILE smoke part
that reads the run files of run_0061 / run_0068 / run_0069 / run_0072 / run_0074 (never run_0075, never results/sealed) with SYNTHETIC
targets (ce.measured is replaced, so no measured curve is compared with them), and one runner cross-check of the 5.3 active RMSE on
the already-seen S0-01 (2.0 nm) and S1-02 (13.2 nm) runs. Nothing is launched and nothing is written outside a temporary folder.

  <venv python> -B analysis_2026-10-10_campaign/test_profile_s4s5.py [--no-real]
Prints one 'ok' / 'FAIL' line per case and 'N/M ok'; exit 0 only if every case passes.
"""
import copy
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import qmc

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import campaign_extract as ce  # noqa: E402
import profile_shared as ps  # noqa: E402
import profile_s4s5 as P  # noqa: E402

EX = ce.ex
Q = P.Q
COX = EX.COX
# native grid = the runner's stepped sweep (76 points, as terminal_currents.csv of run_0061): 0.2 V to -1 V, 0.05 V to 1.5 V, 0.1 V to 3 V;
# it carries native points at 1.5, 2.0 and 3.0 V (5.3 native sampling, A10)
VG_RUN = np.round(np.concatenate([np.arange(-3.0, -1.0 - 1e-9, 0.2), np.arange(-1.0, 1.5 + 1e-9, 0.05), np.arange(1.6, 3.0 + 1e-9, 0.1)]), 6)
VG_M = np.round(np.arange(-3.0, 3.0 + 1e-9, 0.05), 6)     # measured grid (121 points)
QF0 = 1.38345e12
TRUE = {'lNs': 12.62, 'WT': 0.0415, 'g0': None}
TRUE_NUIS = {'dQf': -0.45e12, 'mu_inf': 80.0, 'ell': 9.0}   # dV0 = +0.080 V: the shifted on window stays inside the solved range
FILMS = P.FILMS


def mstar(t): return 0.208 + 0.11116 * t ** -1.26387
def rough(t): return (1 - 0.287 / t) ** 2
def props(t): return mstar(t), rough(t)
def mu_law(mu_inf, ell, t): return ps.mu_law(mu_inf, ell, t, mstar(t))


def shape(x, t):
    """synthetic shape parameters: subthreshold width S (V) and on-state exponent g; the launched coordinates act on the shape"""
    S = 0.12 + 0.05 * (x['lNs'] - 12.5) + 1.2 * (x['WT'] - 0.04) + 0.002 * t
    g = 1.6 + 0.4 * (x['lNs'] - 12.5) - 6.0 * (x['WT'] - 0.04) + (x.get('g0') or 0.0)
    return S, g


def curve(vg, x, t, qf, mu_band, extra_shift=0.0, k=3e-10):
    S, g = shape(x, t); v0 = 0.3 + 0.02 * t + extra_shift
    u = (np.asarray(vg, float) - v0 + Q * (qf - QF0) / COX) / S
    sp = np.where(u > 30, u, np.log1p(np.exp(np.minimum(u, 30))))
    return mu_band * k * sp ** g + 1e-17


NC2 = 'solver.physics_options.nc300_override_cm3[2.0]=1.373e+19'   # the registered film-keyed input (quasi-2D NC300 at 2.0 nm only)


def synth_run(t, x, qf=QF0, mu_inf=100.005, ell=7.248, rid=None, extra_shift=0.0, breakers=(), overrides=None, label=None, vg=None):
    """overrides=None: the registered film-keyed inputs (NC2 at 2.0 nm, nothing at 6.3 / 13.2 nm), as the matrix S4A-* entries"""
    if overrides is None: overrides = (NC2,) if abs(t - 2.0) < 1e-9 else ()
    mb = mu_law(mu_inf, ell, t); vg = VG_RUN.copy() if vg is None else np.asarray(vg, float)
    return {'run_id': rid or f'syn_{t}_{x["lNs"]:.3f}_{x["WT"]:.4f}', 't': t, 'vg': vg, 'i': curve(vg, x, t, qf, mb, extra_shift),
            'cox': COX, 'mstar': mstar(t), 'mu_band': mb, 'mun': mb * rough(t), 'qf': qf, 'breakers': list(breakers), 'x': dict(x),
            'branch': {'tail_alpha': 1.0, 'nt_bulk_cm3': 0.0, 'mobility': 'igzo_tokyo' if x.get('g0') is not None else 'constant',
                       'schottky_barrier_eV': None}, 'props': props, 'overrides': list(overrides), 'label': label,
            'eligibility': {'eligible': True, 'problems': [], 'source': 'synthetic run (complete, finite)'}}


def synth_info(x=TRUE, nuis=TRUE_NUIS, films=FILMS, floor=1e-15, distort=None):
    """synthetic measured curves = the synthetic model at x with the true Q_f / mu law (distort: {t: callable(vg, i) -> i})"""
    info = {}
    for t in films:
        i = curve(VG_M, x, t, QF0 + nuis['dQf'], mu_law(nuis['mu_inf'], nuis['ell'], t))
        if distort and t in distort: i = distort[t](VG_M, i)
        info[t] = {'vg': VG_M.copy(), 'i': i, 'floor': floor, 'sig_floor': 0.0, 'ion': float(i[-1])}
    r = 10 * max(info[t]['floor'] / info[t]['ion'] for t in info)
    for t in info: info[t]['a1_window'] = (r * info[t]['ion'], 10 * r * info[t]['ion'])
    return info


def synth_cand(cid, x, stage='S4a', films=FILMS, fold=None, **kw):
    return P.candidate({'id': cid, 'stage': stage, 'fold': fold, 'runs': {str(t): synth_run(t, x, rid=f'{cid}_{t}', **kw) for t in films}})


def lhs_archive(n=14, seed=20261010, g0=False):
    """an S4a-like archive: candidate 1 = the start point, then a Latin hypercube over the design ranges (same map as the matrix)"""
    pts = qmc.LatinHypercube(d=3 if g0 else 2, seed=seed).random(n)
    xs = [{'lNs': math.log10(4e12), 'WT': 0.040, 'g0': -0.31 if g0 else None}]
    xs += [{'lNs': 12 + a[0], 'WT': 0.025 + 0.035 * a[1], 'g0': (-0.6 + 1.2 * a[2]) if g0 else None} for a in pts]
    return [synth_cand(f'S4A-{k + 1:02d}', x) for k, x in enumerate(xs)]


class Poison(dict):
    """a measured-curve entry that fails on any access (proves that a fold never reads its held-out film)"""
    def __getitem__(self, k): raise AssertionError(f'held-out measured curve accessed ({k})')
    def get(self, k, d=None): raise AssertionError(f'held-out measured curve accessed ({k})')


# ------------------------------------------------------------------------------------------------ cases
def cases_profile(ok):
    info = synth_info()
    R = [synth_run(t, TRUE) for t in FILMS]
    t0 = time.time(); p = P.profile_films(R, info); pp = p['profiled']
    dv_true = -Q * TRUE_NUIS['dQf'] / COX
    ok('profile_films (3 films) recovers dV0, mu_inf, ell of an exact synthetic target',
       abs(pp['dV0_V'] - dv_true) < 1e-4 and abs(pp['mu_inf_cm2Vs'] / 80 - 1) < 1e-3 and abs(pp['ell_nm'] - 9) < 2e-2 and pp['sqrtJ_dec'] < 1e-3 and p['valid'],
       f'dV0 {pp["dV0_V"]:.5f} vs {dv_true:.5f}, mu {pp["mu_inf_cm2Vs"]:.4f}, ell {pp["ell_nm"]:.4f}, sqrtJ {pp["sqrtJ_dec"]:.2e}, {time.time() - t0:.1f} s')
    p2 = P.profile_films([R[0], R[2]], {t: info[t] for t in (2.0, 13.2)}); q2 = p2['profiled']
    ok('profile_films (2 films: 2.0 + 13.2) recovers the same values (mu_inf, ell exactly determined by two scales)',
       abs(q2['dV0_V'] - dv_true) < 1e-4 and abs(q2['mu_inf_cm2Vs'] / 80 - 1) < 1e-3 and abs(q2['ell_nm'] - 9) < 2e-2 and q2['sqrtJ_dec'] < 1e-3)
    try: P.profile_films([R[0]], info); r1 = False
    except SystemExit: r1 = True
    ok('profile_films refuses a single film', r1)
    Rq = [synth_run(2.0, TRUE), synth_run(13.2, TRUE, qf=QF0 + 1e11)]
    try: P.profile_films(Rq, info); r2 = False
    except SystemExit as e: r2 = 'share one Q_f' in str(e)
    ok('profile_films refuses runs with different Q_f', r2)
    Rb = [synth_run(2.0, TRUE, breakers=('schottky_sd',)), synth_run(13.2, TRUE, breakers=('schottky_sd',))]   # one shared model (v2 fix 1)
    try: P.profile_films(Rb, info); r3 = False
    except SystemExit: r3 = True
    ok('tunnelling/Schottky run refused without allow_approximate; labelled APPROXIMATE with it',
       r3 and P.profile_films(Rb, info, allow_approximate=True)['verdict'] in ('APPROXIMATE', 'UNVERIFIED (coverage < 95 % or optimizer not converged: confirm natively)'))
    Jr, _ = ps.triple_J(R, info, pp['dQf_cm2'], pp['mu_inf_cm2Vs'], pp['ell_nm'])
    ok('the reported J is profile_shared.triple_J at the profiled values (equal-film J of CAMPAIGN_DESIGN 5.1)', Jr == pp['J'])
    # shifting the launched Q_f does not change the profiled ABSOLUTE Q_f (exact transformation), only dV0
    Rs = [synth_run(t, TRUE, qf=QF0 + 3e11) for t in FILMS]; ps_ = P.profile_films(Rs, info)['profiled']
    ok('launched Q_f +3e11: same absolute profiled Q_f, dV0 relative to the launched value',
       abs(ps_['Qf_cm2'] - pp['Qf_cm2']) < 2e8 and abs((ps_['dV0_V'] - pp['dV0_V']) - Q * 3e11 / COX) < 2e-4)
    up = synth_info(nuis=dict(TRUE_NUIS, dQf=+1.0e12)); pu = P.profile_films(R, up)   # dV0 = -0.18 V
    ok('no extrapolation: a profile whose shift pushes the on window past +3 V is UNVERIFIED, never OK (coverage < 95 %)',
       pu['verdict'].startswith('UNVERIFIED') and not pu['valid'] and min(f['coverage_on'] for f in pu['profiled']['per_film'].values()) < 0.95)
    B = P.Blind(info, (2.0, 13.2))
    try: B[6.3]; r4 = False
    except PermissionError: r4 = True
    try: P.profile_films(R, B); r5 = False
    except PermissionError: r5 = True
    ok('Blind: the held-out film cannot be read, and profile_films on it raises', r4 and r5 and B.hidden == [6.3])


def cases_surrogate(ok):
    dims = ('lNs', 'WT')
    # exact quadratic J in unit coordinates with its minimum at u* = (0.55, 0.40)
    us = np.array([0.55, 0.40]); Hm = np.array([[2.0, 0.3], [0.3, 1.0]])
    Jq = lambda u: 0.02 + float((u - us) @ Hm @ (u - us))
    rng = np.random.default_rng(1); U = np.vstack([[0.5, 0.42], rng.random((14, 2))])
    pool = [{'id': f'p{k}', 'stage': 'S4a', 'x': P.from_unit(u, dims), 'sqrtJ': math.sqrt(Jq(u))} for k, u in enumerate(U)]
    pr = P.propose(pool, dims)
    h = 0.5 / 14; ub = U[0]; prop = np.array(pr['proposal_unit'])
    ok('trust region (stratum, A1) = half the S4a stratum width (1/28 of each range)', np.allclose(pr['trust_halfwidth_unit'], [h, h]))
    ok('surrogate fit of an exact quadratic J has ~0 residual', pr['surrogate_fit']['rms_J'] < 1e-12 and pr['surrogate_fit']['rank'] == 6)
    ok('the proposal stays inside the trust box around the best archive point', bool(np.all(np.abs(prop - ub) <= h + 1e-9)))
    exp = np.clip(us, ub - h, ub + h)   # convex quadratic: box-constrained minimum computed directly below
    from scipy.optimize import minimize as mn
    bx = mn(Jq, ub, method='L-BFGS-B', bounds=list(zip(ub - h, ub + h))).x
    ok('the proposal is the box-constrained surrogate minimum', np.allclose(prop, bx, atol=1e-5), f'{prop} vs {bx} (unconstrained {us}, clipped {exp})')
    pool_in = [dict(p) for p in pool]; pool_in[0]['x'] = P.from_unit(us + [0.02, -0.02], dims); pool_in[0]['sqrtJ'] = math.sqrt(Jq(us + [0.02, -0.02]))
    pr2 = P.propose(pool_in, dims)
    ok('minimum inside the box -> the proposal is the exact surrogate minimum', np.allclose(pr2['proposal_unit'], us, atol=1e-5))
    pool_d = [dict(p) for p in pool]; pool_d[0]['x'] = P.from_unit(us, dims); pool_d[0]['sqrtJ'] = math.sqrt(Jq(us))
    pr3 = P.propose(pool_d, dims); d3 = float(np.min(np.linalg.norm(np.array([P.unit(p['x'], dims) for p in pool_d]) - np.array(pr3['proposal_unit']), axis=1)))
    ok('surrogate minimum at an evaluated point -> the next distinct ranked point (A1), never a duplicate launch',
       pr3['verdict'].startswith('PROPOSAL') and pr3['selected_rank'] >= 1 and d3 >= pr3['distinct_tolerance_unit'], f'rank {pr3["selected_rank"]}, distance {d3:.2e}')
    occ = [P.unit(p['x'], dims) for p in pool]
    ok('select_distinct: lowest-ranked unoccupied candidate; all occupied -> None (stall)',
       P.select_distinct([(0.1, occ[0], 'g'), (0.2, occ[1] + 0.5, 'g')], occ, 1e-3) == 1 and P.select_distinct([(0.1, occ[0], 'g')], occ, 1e-3) is None)
    pr4 = P.propose(pool[:6], dims)
    ok('a full 2-D quadratic needs >= 7 valid points: refused below (A3)', pr4['verdict'].startswith('REFUSED'))
    ok('trust region fixed at range/28 in every dimension (2-D and 3-D; A1 ruling)', np.allclose(P.trust_halfwidth(2), [h, h]) and np.allclose(P.trust_halfwidth(3), [h] * 3))
    ok('the surrogate value is labelled a ranking device only', 'ranking device only' in pr['labels'] and 'rank_only' in ''.join(pr.keys()))
    # stop rule (A4)
    s = P.s4b_stop(0.40, [0.35, 0.345, 0.342, 0.341])
    ok('S4b stop: 3 successive running-best improvements < 0.01 dec -> STOP', s['verdict'].startswith('STOP') and s['remaining'] == 2)
    ok('S4b stop: worse candidates count as no improvement', P.s4b_stop(0.40, [0.41, 0.45, 0.50])['verdict'].startswith('STOP'))
    ok('S4b stop: an improvement >= 0.01 inside the last three -> CONTINUE', P.s4b_stop(0.40, [0.399, 0.398, 0.385])['verdict'] == 'CONTINUE')
    ok('S4b: 6 candidates used -> DONE', P.s4b_stop(0.40, [0.30, 0.25, 0.20, 0.15, 0.10, 0.05])['verdict'].startswith('DONE'))
    # abort rule (A5)
    mk = lambda v, s_: {'valid': True, 'profiled': {'sqrtJ_dec': v, 'per_film': {'6.3': {'mean_signed_on_dec': s_}}}}
    a1 = P.s4a_abort([mk(0.35 + 0.01 * k, 0.4 if k < 13 else -0.1) for k in range(15)])
    a2 = P.s4a_abort([mk(0.25 + 0.01 * k, 0.4) for k in range(15)])
    a3 = P.s4a_abort([mk(0.35, 0.4 if k < 11 else -0.1) for k in range(15)])
    a4 = P.s4a_abort([mk(0.35, 0.4) for k in range(12)] + [{'valid': False}] * 3)
    a5 = P.s4a_abort([mk(0.25, 0.4)] + [{'valid': False}] * 14)
    a6 = P.s4a_abort([mk(0.35, 0.4 if k < 5 else -0.1) for k in range(12)] + [{'valid': False}] * 3)
    ok('S4a abort: best > 0.30 and >= 80 % same-sign 6.3 nm on-state error (complete inventory) -> ABORT', a1['verdict'].startswith('ABORT') and abs(a1['same_sign_fraction'] - 13 / 15) < 1e-12)
    ok('S4a abort: best <= 0.30 -> no abort; 73 % same sign -> no abort', a2['verdict'].startswith('NO ABORT') and a3['verdict'].startswith('NO ABORT'))
    ok('S4a abort: invalid profiles are unknown, never given a sign; 12 same-sign + 3 unknown -> UNRESOLVED (an unknown may be the best)',
       a4['n_invalid'] == 3 and a4['n_valid'] == 12 and a4['verdict'].startswith('UNRESOLVED') and a4['on_6p3_sign_counts']['unknown'] == 3)
    ok('S4a abort with unknowns: an evaluated sqrt(J) <= 0.30 establishes NO ABORT; a sign fraction that cannot reach 80 % establishes NO ABORT',
       a5['verdict'].startswith('NO ABORT') and a6['verdict'].startswith('NO ABORT') and a6['same_sign_fraction_upper'] < 0.8, f'{a6["same_sign_fraction_upper"]:.3f}')


def cases_surrogate_e2e(ok):
    info = synth_info(); C = lhs_archive()
    t0 = time.time(); res = P.surrogate(C, info)
    ok('surrogate end-to-end: 15 S4a candidates profiled, abort and stop evaluated, a proposal inside the trust box',
       res['n_S4a'] == 15 and 's4a_abort' in res and res['s4b_stop']['verdict'] == 'CONTINUE' and res['verdict'].startswith('PROPOSAL'),
       f'{time.time() - t0:.1f} s, verdict {res["verdict"]}')
    pr = res['proposal']; box = pr['trust_box']
    ok('proposal within the trust box; native launch values carry the profiled Q_f and mu_band (S4B template)',
       all(box[d][0] - 1e-12 <= pr['proposal'][d] <= box[d][1] + 1e-12 for d in box) and set(res['native_launch_values']['per_film']) == {'2.0', '6.3', '13.2'})
    # sequential S4b: launch the proposals natively (synthetic), re-profile, and follow the stop rule; the archive values are native
    hist = []; C2 = list(C)
    for k in range(6):
        r = P.surrogate(C2, info)
        if not r['verdict'].startswith('PROPOSAL'): break
        x = dict(r['proposal']['proposal']); x['g0'] = None
        C2.append(synth_cand(f'S4B-{k + 1:02d}', x, stage='S4b')); hist.append(x)
    final = P.surrogate(C2, info)
    best4a = min(a['sqrtJ'] for a in final['archive'] if a['stage'] == 'S4a'); best = min(a['sqrtJ'] for a in final['archive'] if a['sqrtJ'] is not None)
    ok('sequential S4b never worsens the running best and ends by STOP (incl. OPTIMIZER STALL) or DONE, never a duplicate launch',
       best <= best4a + 1e-12 and final['verdict'].startswith(('STOP', 'DONE')) and len(hist) >= 1, f'{len(hist)} S4b steps, best {best4a:.4f} -> {best:.4f}, {final["verdict"][:20]}')
    # an S4b launch that did not complete: UNKNOWN in the archive, unknown improvement, its point stays occupied (B1/B3)
    xu = dict(res['proposal']['proposal']); xu['g0'] = None; cu = synth_cand('S4B-01', xu, stage='S4b')
    for r in cu['R']: r['eligibility'] = {'eligible': False, 'problems': ['runner status TIMEOUT', 'timed out'], 'timed_out': True}
    cu = P.candidate({'id': 'S4B-01', 'stage': 'S4b', 'runs': {str(r['t']): r for r in cu['R']}})
    ru = P.surrogate(C + [cu], info); row = next(a for a in ru['archive'] if a['id'] == 'S4B-01')
    du = float(np.linalg.norm(np.array(ru['proposal']['proposal_unit']) - P.unit(xu, ('lNs', 'WT'))))
    ok('an incomplete S4b launch is UNKNOWN (never profiled), has an unknown improvement, and its point is not proposed again',
       row['state'].startswith('UNKNOWN') and row['sqrtJ'] is None and ru['s4b_stop']['improvements_dec'] == [None] and ru['verdict'].startswith('PROPOSAL')
       and du >= ru['proposal']['distinct_tolerance_unit'], f'{row["state"][:60]}; distance {du:.2e}')
    # surrogate only ranks: the S4b archive values equal a fresh native profile of the launched curves
    last = C2[-1]; fresh = P.profile_films(last['R'], info)['profiled']['sqrtJ_dec']
    ok('archive values are native profiled sqrt(J), never surrogate values', abs(next(a['sqrtJ'] for a in final['archive'] if a['id'] == last['id']) - fresh) < 1e-12)
    try: P.surrogate([synth_cand('S5-x', TRUE, stage='S5', films=(2.0, 13.2), fold=6.3)] + C, info); r1 = False
    except SystemExit: r1 = True
    ok('surrogate refuses S5 candidates in the S4 archive', r1)
    try: P.dims_of(C + [synth_cand('IG', dict(TRUE, g0=-0.3))]); r2 = False
    except SystemExit: r2 = True
    ok('archive mixing IGZO and constant-mobility candidates is refused', r2)
    # abort path: a target the model family cannot fit (6.3 nm on-state far off) -> abort before S4b (all 15 S4a profiles valid)
    bad = synth_info(distort={6.3: lambda v, i: i * np.where(v > 0.8, 10 ** (1.0 * (v - 0.8)), 1.0)})
    rb = P.surrogate(C, bad)
    ok('S4a abort fires on a systematic 6.3 nm on-state misfit with a complete, valid S4a inventory (best sqrt(J) > 0.30, same sign)',
       rb['verdict'].startswith('ABORT') and rb['s4a_abort']['n_valid'] == 15, f'{rb["s4a_abort"]["verdict"][:40]}; best {rb["s4a_abort"]["best_sqrtJ_dec"]:.3f}')
    # the opposite misfit leaves 5 of 15 profiles UNVERIFIED (on window past +3 V): the abort is not established (B3/A5)
    bad2 = synth_info(distort={6.3: lambda v, i: i * np.where(v > 0.8, 10 ** (-1.2 * (v - 0.8)), 1.0)})
    rb2 = P.surrogate(C, bad2)
    ok('S4a abort with unverified profiles (unknown results) is UNRESOLVED and S4b is not skipped on that basis',
       rb2['s4a_abort']['verdict'].startswith('UNRESOLVED') and rb2['s4a_abort']['n_invalid'] > 0 and not rb2['verdict'].startswith('ABORT'),
       f'{rb2["s4a_abort"]["n_invalid"]} invalid; {rb2["verdict"][:50]}')


def cases_loo(ok):
    t0 = time.time(); F = _fold_fixture(); info, tr, C, C2, dec, rf = F['info'], F['train'], F['C'], F['C2'], F['dec'], F['rf']
    r = P.loo_select(C, 6.3, tr, decision=dec)
    ok('LOO fold 6.3: training films 2.0 and 13.2 only; the held-out film is not in the measured set and Blind hides it',
       r['training_films'] == [2.0, 13.2] and r['fold_candidates_done'] == 0 and 'hidden: [6.3]' in r['blind'] and r['decision_sha256'] == dec['sha256'],
       f'{time.time() - t0:.1f} s (fixture included)')
    ok('LOO: a next adaptive training candidate is proposed (fewer than 4 fold candidates), no frozen record yet',
       r['verdict'].startswith('TRAINING') and r['next_training_candidate']['verdict'].startswith('PROPOSAL') and 'frozen' not in r
       and set(r['native_launch_values']['per_film']) == {'2.0', '13.2'})
    try: P.loo_select(C + [synth_cand('S4B-01', TRUE, stage='S4b')], 6.3, tr, decision=dec); r1 = False
    except SystemExit: r1 = True
    try: P.loo_select(C + [synth_cand('S5-H2p0-1', TRUE, stage='S5', films=(6.3, 13.2), fold=2.0)], 6.3, tr, decision=dec); r2 = False
    except SystemExit: r2 = True
    ok('LOO refuses S4b candidates (they saw all films) and other folds\' candidates', r1 and r2)
    try: P.loo_select(C, 6.3, tr, decision=dict(dec, same_as_full_data=False)); r5 = False
    except SystemExit as e: r5 = 'sha256' in str(e)
    try: P.loo_select(C, 6.3, tr, decision=_decision(2.0, info)); r6 = False
    except SystemExit as e: r6 = 'fold' in str(e)
    ok('LOO refuses an edited branch decision and a decision of another fold (B2: the decision is bound)', r5 and r6)
    ok('after 4 fold candidates: FROZEN best and runner-up (the two lowest training sqrt(J), distinct candidates)', rf['verdict'].startswith('FROZEN')
       and [f['rank'] for f in rf['frozen']] == ['best', 'runner_up'] and rf['frozen'][0]['training_sqrtJ_dec'] <= rf['frozen'][1]['training_sqrtJ_dec']
       and rf['frozen'][0]['candidate'] != rf['frozen'][1]['candidate'])
    fb = rf['frozen'][0]; cb = next(c for c in C2 if c['id'] == fb['candidate'])
    p2 = P.profile_films([r_ for r_ in cb['R'] if r_['t'] in (2.0, 13.2)], tr)['profiled']
    ok('frozen record: Q_f = training-profiled value; mu_band(6.3) from the two-film law with m*(6.3); nothing from 6.3 nm data',
       abs(fb['Qf_cm2'] - p2['Qf_cm2']) < 1e-3 * abs(p2['Qf_cm2']) and abs(fb['held_out']['mu_band_cm2Vs'] - ps.mu_law(p2['mu_inf_cm2Vs'], p2['ell_nm'], 6.3, mstar(6.3))) < 1e-9 * 50)
    ok('frozen record sha256 is the hash of its canonical content; it lists every S4a and fold candidate with run digests and the code sha256',
       fb['sha256'] == hashlib.sha256(P._canon({k: v for k, v in fb.items() if k != 'sha256'}).encode()).hexdigest()
       and all(len(e['runs']) == 2 and all(len(x['digest']) == 64 for x in e['runs']) for e in fb['inventory']['S4a'] + fb['inventory']['fold'])
       and fb['code_sha256'] == P.CODE_SHA)
    # native held-out launch with the frozen values -> 5.3 acceptance on the (now visible) held-out film
    nat = synth_run(6.3, fb['coords'], qf=fb['Qf_cm2'], mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'], rid='native_6p3')
    sc = P.loo_score(fb, nat, info, committed_sha256=fb['sha256'])
    ok('loo_score on the native frozen run (committed hash): 5.3 criteria evaluated, verdict PASS/FAIL, labelled retrospective',
       sc['verdict'].startswith(('PASS', 'FAIL')) and 'not validation' in sc['labels'], sc['verdict'][:60])
    tam = dict(fb); tam['Qf_cm2'] *= 1.01
    try: P.loo_score(tam, nat, info, committed_sha256=fb['sha256']); r3 = False
    except SystemExit as e: r3 = 'sha256' in str(e)
    wrong = synth_run(6.3, fb['coords'], qf=fb['Qf_cm2'] * 1.02, mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'])
    try: P.loo_score(fb, wrong, info, committed_sha256=fb['sha256']); r4 = False
    except SystemExit as e: r4 = 'does not carry the frozen' in str(e)
    other = synth_run(6.3, fb['coords'], qf=fb['Qf_cm2'], mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'], overrides=['solver.dos_levels.numa=96'])
    try: P.loo_score(fb, other, info, committed_sha256=fb['sha256']); r7 = False
    except SystemExit as e: r7 = 'settings' in str(e)
    ok('loo_score refuses an edited record, a native run without the frozen values and one with other non-fitted settings', r3 and r4 and r7)


def cases_branch(ok):
    info = synth_info(x=dict(TRUE, g0=-0.2))   # truth contains a mobility-shape term the base cannot reproduce
    base = {str(t): synth_run(t, TRUE, rid=f'base_{t}') for t in FILMS}
    good = {str(t): synth_run(t, dict(TRUE, g0=-0.2), rid=f'ig_{t}') for t in FILMS}
    meh = {str(t): synth_run(t, dict(TRUE, g0=-0.05), rid=f'ig2_{t}') for t in FILMS}
    spec = {'base': base, 'full_data_choice': ['igzo_a'], 'branches': [
        {'name': 'igzo_a', 'group': 'mobility', 'runs': good, 'converged': True, 'activation_ok': True, 'pure_shift_or_scale': False},
        {'name': 'igzo_b', 'group': 'mobility', 'runs': meh, 'converged': True, 'activation_ok': True, 'pure_shift_or_scale': False}]}
    tr = {t: info[t] for t in (2.0, 13.2)}
    try: P.loo_branch(spec, 6.3, {**info, 6.3: Poison()}); r0 = False
    except SystemExit as e: r0 = 'held-out' in str(e)
    r = P.loo_branch(spec, 6.3, tr)
    ok('loo_branch: training-only measured set (a set holding the held-out film is refused); two-film adoption arithmetic, the lowest-sqrt(J) '
       'member of a group wins, same as full data; the decision is sealed', r0 and r['fold_choice'] == ['igzo_a'] and r['same_as_full_data'] and len(r['sha256']) == 64
       and P.verify_seal(r, 'decision') is r, f'{[(b["name"], round(b.get("gain_dec", 0), 4), b["adopted_candidate"]) for b in r["branches"]]}')
    spec2 = dict(spec, full_data_choice=[]); d2 = P.loo_branch(spec2, 6.3, tr)
    ok('loo_branch: a different choice than the full data -> DIFFERENT, fold branch = IGZO, S3 centre with the branch GAMMA0 (A7)',
       d2['verdict'].startswith('DIFFERENT') and d2['fold_branch']['mobility'] == 'igzo_tokyo' and d2['full_data_branch']['mobility'] == 'constant'
       and abs(d2['centre_x']['g0'] + 0.2) < 1e-12 and set(d2['centre_launch_values']['per_film']) == {'2.0', '13.2'})
    spec3 = copy.deepcopy(spec); spec3['branches'][0]['activation_ok'] = False; spec3['branches'][1]['activation_ok'] = False
    ok('loo_branch: caller flags (activation) block adoption', P.loo_branch(spec3, 6.3, tr)['fold_choice'] == [])
    a = P.adopt_films([good['2.0'], good['13.2']], [base['2.0'], base['13.2']], info)
    ok('adopt_films: gain >= 0.03 dec and no film worse by > 0.03 dec', a['verdict'] == 'ARITHMETIC PASS' and a['sqrtJ_gain_dec'] >= 0.03)
    # A7 (Codex ruling; DRAFT until a logged register amendment): four registered S3-centred points, ranked on training data only
    dims, pts = P.a7_points(d2); hw = 0.5 / P.N_LHS
    U = np.array([P.unit(x, dims) for x in pts]); uc = P.unit(d2['centre_x'], dims)
    ok('A7 points: 3-D tetrahedral points around the S3 centre at the A1 half-width, inside the design ranges',
       dims == P.DIMS and len(pts) == 4 and np.allclose(np.abs(U - uc), hw, atol=2e-3) and np.allclose(U.mean(axis=0), uc, atol=2e-3) and np.all((U >= 0) & (U <= 1)))
    r7 = P.loo_select([], 6.3, tr, decision=d2)
    ok('A7 fold: the next registered point and the S3 centre launch values are listed; verdict DRAFT (amendment + user go needed)',
       r7['verdict'].startswith('A7 LOCAL DESIGN (DRAFT)') and r7['next_training_candidate']['proposal'] == pts[0] and 'amendment' in r7['verdict'])
    try: P.loo_select(lhs_archive(), 6.3, tr, decision=d2); r8 = False
    except SystemExit as e: r8 = 'S4a archive' in str(e)
    C7 = [synth_cand(f'S5-H6p3-{k + 1}', x, stage='S5', films=(2.0, 13.2), fold=6.3) for k, x in enumerate(pts)]
    n7, f7 = P.loo_select(C7, 6.3, tr, decision=d2), P.loo_select(C7, 6.3, tr, decision=d2, amendment_ref='TEST ONLY (synthetic)')
    ok('A7 fold: the S4a archive is refused; four completed points do not freeze without --amendment; with it the records carry mode A7 and the reference',
       r8 and n7['verdict'].startswith('REFUSED') and 'frozen' not in n7 and f7['verdict'].startswith('FROZEN') and f7['frozen'][0]['mode'].startswith('A7')
       and f7['frozen'][0]['amendment_ref'] == 'TEST ONLY (synthetic)', n7['verdict'][:80])
    wrong7 = [synth_cand(f'S5-H6p3-{k + 1}', dict(x, WT=x['WT'] + 0.003), stage='S5', films=(2.0, 13.2), fold=6.3) for k, x in enumerate(pts)]
    try: P.loo_select(wrong7, 6.3, tr, decision=d2); r9 = False
    except SystemExit as e: r9 = 'registered A7' in str(e)
    ok('A7 fold: candidates that are not the registered points are refused', r9)


def cases_acceptance(ok):
    info = synth_info()
    t = 6.3; x = TRUE; mb = mu_law(TRUE_NUIS['mu_inf'], TRUE_NUIS['ell'], t)
    i_ok = curve(VG_RUN, x, t, QF0 + TRUE_NUIS['dQf'], mb)
    a = P.acceptance(VG_RUN, i_ok, t, info)
    ok('5.3: a run equal to the measured model passes every criterion', a['verdict'] == 'PASS', json.dumps({k: v.get('value') for k, v in a['criteria'].items()}, default=float)[:200])
    a2 = P.acceptance(VG_RUN, curve(VG_RUN, x, t, QF0 + TRUE_NUIS['dQf'] - 0.2 * COX / Q, mb), t, info)
    ok('5.3: a +0.2 V shifted curve fails V_th,cc (|dV| > 0.10 V)', a2['criteria']['dVth_cc_V']['ok'] is False and a2['verdict'].startswith('FAIL'))
    a3 = P.acceptance(VG_RUN, 1.5 * i_ok, t, info)
    ok('5.3: x1.5 current fails I_D(3 V) (+50 %) but keeps SS and V_th within limits', a3['criteria']['Id3V_err_pct']['ok'] is False and a3['criteria']['SS_a1_err_pct']['ok'] is True)
    a4 = P.acceptance(VG_RUN[VG_RUN <= 2.0], i_ok[VG_RUN <= 2.0], t, info)
    ok('5.3: a curve that does not reach 3 V is unresolved for I_D(3 V) and mu_FE(3 V), never a pass', a4['criteria']['Id3V_err_pct']['ok'] is None and not a4['verdict'].startswith('PASS'))
    # runner definition of the active RMSE
    vm, im = info[t]['vg'], info[t]['i']; o = np.median(im[(vm >= -2) & (vm <= -0.5)]); act = im > 5 * o
    le = np.log10(np.maximum(np.interp(vm, VG_RUN, 1.3 * i_ok), 1e-40)) - np.log10(im)
    ok('5.3 active RMSE = run_atlas.score definition', abs(P.acceptance(VG_RUN, 1.3 * i_ok, t, info)['criteria']['active_rmse_dec']['value'] - np.sqrt(np.mean(le[act] ** 2))) < 1e-12)
    r = synth_run(t, x, qf=QF0, mu_inf=TRUE_NUIS['mu_inf'], ell=TRUE_NUIS['ell'])
    vgp, ip = P.transformed_points(r, TRUE_NUIS['dQf'], 1.0)
    ok('transformed_points = the exact shift of the native points (dV = -q dQf / C_ox)', np.allclose(curve(vgp, x, t, QF0 + TRUE_NUIS['dQf'], r['mu_band']), ip, rtol=1e-12))


def cases_jacobian(ok):
    names = ['lNs', 'WT', 'dV0', 'lmu', 'ell']
    rng = np.random.default_rng(3); Jo = np.linalg.qr(rng.normal(size=(60, 5)))[0] / np.array([P.SCALE[n] for n in names])
    ao = P.jac_analysis(Jo, names)
    ok('jac_analysis: orthogonal scaled columns -> condition 1, no flag', abs(ao['condition_number_range_scaled'] - 1) < 1e-9 and not ao['flag'])
    Jc = Jo.copy(); Jc[:, 1] = Jc[:, 0] * P.SCALE['lNs'] / P.SCALE['WT'] + 1e-4 * Jo[:, 1]
    ac = P.jac_analysis(Jc, names)
    ok('jac_analysis: nearly collinear N_s / W_T columns -> flag, |corr| > 0.95 and a weak combination of lNs and WT',
       ac['flag'] and ac['max_abs_corr'] > 0.95 and ac['weak_combinations'] and abs(ac['weak_combinations'][-1]['combination_scaled_units']['lNs']) > 0.5)
    info = synth_info(); C = lhs_archive()
    C += [synth_cand(f'S4B-{k:02d}', {'lNs': 12.62 + dx, 'WT': 0.0415 + dw, 'g0': None}, stage='S4b')
          for k, (dx, dw) in enumerate([(0.03, 0.0), (-0.03, 0.0), (0.0, 0.001), (0.0, -0.001), (0.02, 0.0007), (-0.02, -0.0007)], 1)]
    t0 = time.time(); jr = P.jacobian(C, info)
    ok('jacobian on a synthetic S4a + S4b archive: 5 parameters, variants k = 4, 6, all; verdict given', jr['parameters'] == names
       and [v['k_neighbours'] for v in jr['variants']][:2] == [4, 6] and jr['verdict'], f'{time.time() - t0:.1f} s; {jr["verdict"][:40]}; '
       f'cond {jr["primary"]["condition_number_range_scaled"]:.3g}; max|corr| {jr["primary"]["max_abs_corr"]:.3f}')
    # analytic check of the profiled columns at the best point: d r / d log10 mu_inf = w and d r / d ell = -w / ((t + ell) ln 10)
    best = next(c for c in C if c['id'] == jr['best']['id']); p = P.profile_films(best['R'], info)['profiled']
    r0, keys = P.resid_vec(best['R'], info, p['Qf_cm2'], p['mu_inf_cm2Vs'], p['ell_nm'])
    rl, _ = P.resid_vec(best['R'], info, p['Qf_cm2'], p['mu_inf_cm2Vs'] * 10 ** 1e-3, p['ell_nm'])
    re_, _ = P.resid_vec(best['R'], info, p['Qf_cm2'], p['mu_inf_cm2Vs'], p['ell_nm'] + 1e-2)
    fin = np.isfinite(r0)
    ok('profiled columns: d log10 I / d log10 mu_inf = 1 and d / d ell = -1/((t + ell) ln 10) at every point',
       np.allclose(((rl - r0) / 1e-3)[fin], 1.0, atol=1e-6) and np.allclose(((re_ - r0) / 1e-2)[fin], np.array([-1 / ((k[0] + p['ell_nm'] + 5e-3) * math.log(10)) for k in keys])[fin], rtol=1e-3))
    tr = P.jacobian([c for c in C if c['stage'] == 'S4a'][:3], info)
    ok('jacobian with too few neighbours -> UNRESOLVED', tr['verdict'].startswith('UNRESOLVED'))
    try: P.jacobian(C + [synth_cand('S5-z', TRUE, stage='S5', films=(2.0, 13.2), fold=6.3)], info); r1 = False
    except SystemExit: r1 = True
    ok('jacobian refuses S5 candidates (archive = S4a + S4b)', r1)


def cases_sensitivity(ok):
    info = synth_info()
    base = [synth_run(t, TRUE, rid=f'b{t}') for t in FILMS]
    pert = [synth_run(t, TRUE, rid=f'p{t}', extra_shift=0.05) for t in FILMS]   # an input that shifts every curve by +50 mV
    s = P.sensitivity(pert, base, info)
    ok('S6 sensitivity: a +50 mV built-in shift moves the profiled dV0 by -50 mV and leaves mu_inf, ell', abs(s['movement']['dV0_V'] + 0.05) < 2e-4
       and abs(s['movement']['log10_mu_inf']) < 1e-3 and abs(s['movement']['ell_nm']) < 0.05 and s['verdict'] == 'OK')
    p63 = [synth_run(6.3, TRUE, rid='p6.3', extra_shift=0.03, label='c10_s6_23_6p3')]
    try: P.sensitivity(p63, base, info); r1 = False
    except SystemExit: r1 = True
    s2 = P.sensitivity(p63, base, info, fill_from_base=True)
    ok('S6 sensitivity: the designated film-local S6-23 perturbation needs --fill-from-base, which is labelled', r1 and s2['films'] == [2.0, 6.3, 13.2]
       and 'FILLED FROM BASE' in s2['labels'][0])
    pe = [synth_run(t, TRUE, rid=f'e{t}', extra_shift=0.02, label=f'c10_s6_1{k}') for k, t in enumerate((2.0, 13.2))]
    s3 = P.sensitivity(pe, base, info)
    ok('S6 sensitivity: a perturbation run at two films is compared with the base on the same two films (A9)', s3['films'] == [2.0, 13.2]
       and s3['base']['films'] == [2.0, 13.2])


# ------------------------------------------------------------------------------------------------ Codex review 2026-10-13 ~01:55Z: regressions
# One case per blocking counterexample (B1..B5) and per ruling that changes behaviour. Each case runs on its own (a crash is a FAIL of
# that case only), so the red phase against the submitted code (sha256 fe9a4d34...) lists every defect separately.
START_X = {'lNs': math.log10(4e12), 'WT': 0.040, 'g0': None}
X2 = {'lNs': 12.40, 'WT': 0.0450, 'g0': None}
RUN73 = 'results/runs/run_0073_13p2_c10_s1_06_13p2'          # already-seen S1-06: TIMEOUT, no exported currents
NC = 'solver.physics_options.nc300_override_cm3[2.0]='


def _case(ok, name, fn):
    try: cond, info = fn()
    except BaseException as e:   # SystemExit included: an unexpected refusal is a failure of this case
        cond, info = False, f'{type(e).__name__}: {str(e)[:300]}'
    ok(name, cond, info)


def _cand_ov(cid, x, ov_by_film, stage='S4a', qf=QF0, mu_inf=100.005, ell=7.248):
    """an archive entry whose runs carry the given override strings (values matter: Codex B1)"""
    return {'id': cid, 'stage': stage, 'runs': {str(t): synth_run(t, x, qf=qf, mu_inf=mu_inf, ell=ell, rid=f'{cid}_{t}', overrides=ov_by_film.get(t, ()))
                                                for t in FILMS}}


def _patched_copy(run, patch, model_patch=None):
    """a temporary copy of an already-seen run (execution.json patched; optionally the material model); written only to a temporary
    folder, never under results/"""
    import shutil, tempfile
    src = ce.resolve(run); d = Path(tempfile.mkdtemp(prefix='s4s5_regr_')) / src.name; d.mkdir()
    for f in ('execution.json', 'terminal_currents.csv', 'material_model_used.json'):
        if (src / f).is_file(): shutil.copy2(src / f, d / f)
    exj = json.loads((d / 'execution.json').read_text())
    exj.update(patch(exj) if callable(patch) else patch); (d / 'execution.json').write_text(json.dumps(exj, indent=1))
    if model_patch:
        m = json.loads((d / 'material_model_used.json').read_text()); model_patch(m); (d / 'material_model_used.json').write_text(json.dumps(m, indent=1))
    return d


_A7 = {}


def _a7_fixture():
    """a changed-branch fold (truth with an IGZO-like term; the fold picks igzo_a, the full data picked nothing): sealed decision, the four
    registered A7 points launched synthetically at the training films, frozen with a (synthetic) amendment reference; built once"""
    if _A7: return _A7
    info = synth_info(x=dict(TRUE, g0=-0.2)); tr = {t: info[t] for t in (2.0, 13.2)}
    spec = {'base': {str(t): synth_run(t, TRUE, rid=f'base_{t}') for t in FILMS}, 'full_data_choice': [], 'branches': [
        {'name': 'igzo_a', 'group': 'mobility', 'runs': {str(t): synth_run(t, dict(TRUE, g0=-0.2), rid=f'ig_{t}') for t in FILMS},
         'converged': True, 'activation_ok': True, 'pure_shift_or_scale': False}]}
    dec = P.loo_branch(spec, 6.3, tr); dims, pts = P.a7_points(dec)
    C7 = [synth_cand(f'S5-H6p3-{k + 1}', x, stage='S5', films=(2.0, 13.2), fold=6.3) for k, x in enumerate(pts)]
    _A7.update(info=info, train=tr, spec=spec, dec=dec, pts=pts, C7=C7, rf=P.loo_select(C7, 6.3, tr, decision=dec, amendment_ref='TEST ONLY (synthetic)'))
    return _A7


def _base_spec(films=FILMS, x=TRUE):
    return {'base': {str(t): synth_run(t, x, rid=f'base_{t}') for t in films}, 'full_data_choice': [], 'branches': []}


def _decision(held=6.3, info=None, spec=None):
    info = info or synth_info(); train = [t for t in FILMS if t != held]
    return P.loo_branch(spec or _base_spec(), held, {t: info[t] for t in train})


_FOLD = {}


def _fold_fixture():
    """S4a archive (15 candidates) + the 4 adaptive candidates of fold 6.3, launched synthetically; built once"""
    if _FOLD: return _FOLD
    info = synth_info(); tr = {t: info[t] for t in (2.0, 13.2)}; C = lhs_archive(); dec = _decision(6.3, info)
    C2 = list(C)
    for k in range(P.LOO_N):
        rr = P.loo_select(C2, 6.3, tr, decision=dec); x = dict(rr['next_training_candidate']['proposal']); x['g0'] = None
        C2.append(synth_cand(f'S5-H6p3-{k + 1}', x, stage='S5', films=(2.0, 13.2), fold=6.3))
    _FOLD.update(info=info, train=tr, C=C, C2=C2, dec=dec, rf=P.loo_select(C2, 6.3, tr, decision=dec))
    return _FOLD


def cases_regressions(ok):
    real = all((ce.ct.PKG / v).is_dir() for v in (RUNS['0061'], RUNS['0069'], RUN73))
    # ---- B1: eligibility before fitting; non-fitted settings bound across the archive
    def b1_timeout_copy():
        if not real: return True, 'skipped: real run files missing'
        d = _patched_copy(RUNS['0061'], {'status': 'TIMEOUT', 'timed_out': True, 'returncode': 1})
        r = P.load(str(d)); el = r['eligibility']; r69 = P.load(RUNS['0069'])
        syn = real_targets([P.load(RUNS['0061']), r69], {'dQf': -0.6e12, 'mu_inf': 70.0, 'ell': 11.0})
        try: P.profile_films([r, r69], syn); ref = False
        except SystemExit as e: ref = 'not eligible' in str(e) and 'timed out' in str(e)
        return el['eligible'] is False and el['timed_out'] is True and any('timed out' in p for p in el['problems']) and ref, str(el['problems'])
    _case(ok, 'REGRESSION B1 (Codex: timeout fact lost on load): a timed-out run keeps its timeout fact and is refused before fitting', b1_timeout_copy)
    def b1_run0073():
        if not real: return True, 'skipped: real run files missing'
        el = P.load(RUN73)['eligibility']
        return el['eligible'] is False and el['timed_out'] is True and 'no exported currents' in el['problems'], str(el['problems'])
    _case(ok, 'REGRESSION B1: the real TIMEOUT run_0073 (no export) loads as an ineligible record with its timeout fact, never a crash', b1_run0073)
    def b1_mixed_nc():
        A = _cand_ov('S4A-01', TRUE, {2.0: [NC + '1.373e+19']}); B = _cand_ov('S4A-02', X2, {2.0: [NC + '5e+18']})
        try: P.load_archive({'candidates': [A, B]}); return False, 'accepted'
        except SystemExit as e: return 'non-fitted settings differ' in str(e), str(e)[:200]
    _case(ok, 'REGRESSION B1 (Codex: mixed-NC archive accepted): two NC300 values at 2.0 nm cannot enter one calibration archive', b1_mixed_nc)
    def b1_shared_setting():
        A = _cand_ov('S4A-01', TRUE, {t: ['solver.dos_levels.numa=384'] for t in FILMS}); B = _cand_ov('S4A-02', X2, {t: ['solver.dos_levels.numa=96'] for t in FILMS})
        try: P.load_archive({'candidates': [A, B]}); return False, 'accepted'
        except SystemExit as e: return 'non-fitted settings differ' in str(e), str(e)[:200]
    _case(ok, 'REGRESSION B1: a shared setting that differs between candidates (DOS grid 384 vs 96) is refused in one archive', b1_shared_setting)
    def b1_allowed():
        ov = lambda ns, wt, qf, t, mb: [f'thickness_laws.Nt_cm3.Nt2={ns / 2e-7:.6g}', f'thickness_laws.WTA_eV.value={wt}',
                                        f'traps.fixed_interface_charge_Qf_cm2.value={qf:.6g}', f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{t}]={mb:.6g}']
        A = _cand_ov('S4A-01', TRUE, {t: ov(4e12, 0.0415, QF0, t, 40) + ([NC + '1.373e+19'] if t == 2.0 else []) for t in FILMS})
        B = _cand_ov('S4A-02', X2, {t: ov(2.5e12, 0.045, QF0 + 1e11, t, 33) + ([NC + '1.373e+19'] if t == 2.0 else []) for t in FILMS}, qf=QF0 + 1e11)
        C = P.load_archive({'candidates': [A, B]})
        return len(C) == 2, 'coordinates (Nt2, WTA) and profiled values (Q_f, mu_band) may differ; NC equal'
    _case(ok, 'B1: launched coordinates and profiled nuisance values may differ between candidates (everything else is bound)', b1_allowed)
    # ---- B2: fold loading training-only before Blind; fold binding
    def b2_cli():
        import contextlib, io, tempfile
        info = synth_info(); C = lhs_archive(); runmap = {}; arch = {'candidates': []}
        for c in C:
            e = {'id': c['id'], 'stage': c['stage'], 'runs': {}}
            for r in c['R']: name = f'syn:{c["id"]}:{r["t"]}'; runmap[name] = r; e['runs'][str(r['t'])] = name
            arch['candidates'].append(e)
        tmp = Path(tempfile.mkdtemp(prefix='s4s5_cli_')); (tmp / 'archive.json').write_text(json.dumps(arch))
        (tmp / 'decision.json').write_text(json.dumps(_decision(6.3, info), default=float))
        calls = []; saved = (P.load, getattr(P, 'measured_training', None), ce.measured)
        def boom(): raise AssertionError('ce.measured() called: every measured curve (held-out film included) loaded before Blind')
        P.load = lambda name: runmap[name]; P.measured_training = lambda train: calls.append(sorted(train)) or {t: info[t] for t in train}; ce.measured = boom
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = P.main(['loo_select', str(tmp / 'archive.json'), '--held', '6.3', '--decision', str(tmp / 'decision.json'), '--out', str(tmp)])
        finally:
            P.load, ce.measured = saved[0], saved[2]
            if saved[1] is None: del P.measured_training
            else: P.measured_training = saved[1]
        return code == 0 and calls == [[2.0, 13.2]], f'exit {code}; training-film loads {calls}'
    _case(ok, 'REGRESSION B2 (Codex: CLI loads all measurements before Blind): loo_select loads the two training films only', b2_cli)
    def b2_refuse_full():
        info = synth_info()
        try: P.loo_select(lhs_archive(), 6.3, info, decision=_decision(6.3, info)); return False, 'accepted'
        except SystemExit as e: return 'held-out' in str(e), str(e)[:160]
    _case(ok, 'REGRESSION B2: a fold given a measured set that contains the held-out film is refused (training-only loading)', b2_refuse_full)
    def b2_binding():
        F = _fold_fixture(); rf = F['rf']; fb = rf['frozen'][0]
        nat = synth_run(6.3, fb['coords'], qf=fb['Qf_cm2'], mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'], rid='native_6p3')
        bound = (fb['decision_sha256'] == F['dec']['sha256'] and len(fb['inventory']['fold']) == 4 and len(fb['inventory']['S4a']) == 15
                 and fb['settings']['shared_overrides'] is not None and fb['mode'].startswith('S4a archive'))
        try: P.loo_score(fb, nat, F['info'], committed_sha256=None); r1 = False
        except SystemExit as e: r1 = 'committed' in str(e)
        tam = P.seal(dict(fb, Qf_cm2=fb['Qf_cm2'] * 1.01))
        nat2 = synth_run(6.3, fb['coords'], qf=tam['Qf_cm2'], mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'], rid='native_6p3_tampered')
        try: P.loo_score(tam, nat2, F['info'], committed_sha256=fb['sha256']); r2 = False
        except SystemExit as e: r2 = 'committed' in str(e)
        sc = P.loo_score(fb, nat, F['info'], committed_sha256=fb['sha256'])
        return bound and r1 and r2 and sc['frozen_sha256'] == fb['sha256'], f'bound {bound}; uncommitted refused {r1}; edited+re-hashed refused {r2}'
    _case(ok, 'REGRESSION B2: frozen records bind the branch decision, the exact inventory and settings; scoring needs the externally committed hash '
              '(an edited, re-hashed record is refused)', b2_binding)
    def b2_distinct():
        F = _fold_fixture(); fold = [c for c in F['C2'] if c['stage'] == 'S5']
        dup = synth_cand('S5-H6p3-4', fold[2]['x'], stage='S5', films=(2.0, 13.2), fold=6.3)
        r = P.loo_select(F['C'] + fold[:3] + [dup], 6.3, F['train'], decision=F['dec'])
        return 'frozen' not in r and 'distinct' in r['verdict'], r['verdict'][:120]
    _case(ok, 'REGRESSION B2/A6: four DISTINCT fold candidates are required; a duplicated point never freezes', b2_distinct)
    def b2_no_early():
        import contextlib, inspect, io
        with contextlib.redirect_stdout(io.StringIO()): code = P.main(['loo_select', 'x.json', '--held', '6.3', '--freeze-now'])
        return 'freeze_now' not in inspect.signature(P.loo_select).parameters and code == 2, f'exit {code}'
    _case(ok, 'REGRESSION A6: no early primary freeze (--freeze-now removed)', b2_no_early)
    # ---- B3: unknown results in the stopping rules
    mk = lambda v, s_: {'valid': True, 'profiled': {'sqrtJ_dec': v, 'per_film': {'6.3': {'mean_signed_on_dec': s_}}}}
    def b3_abort_one_valid():
        a = P.s4a_abort([mk(0.35, 0.4)] + [{'valid': False}] * 14)
        return a['verdict'].startswith('UNRESOLVED'), a['verdict'][:120]
    _case(ok, 'REGRESSION B3 (Codex: 1 valid + 14 invalid S4a -> "80 % systematic"): the abort is UNRESOLVED', b3_abort_one_valid)
    def b3_abort_missing():
        a = P.s4a_abort([mk(0.35 + 0.01 * k, 0.4) for k in range(14)])   # 14 of the 15 S4a candidates
        return a['verdict'].startswith('UNRESOLVED'), a['verdict'][:120]
    _case(ok, 'REGRESSION B3/A5: a missing S4a candidate may be the best: the abort conclusion is UNRESOLVED (complete inventory)', b3_abort_missing)
    def b3_stop_missing():
        s1 = P.s4b_stop(0.40, [None, None, None]); s2 = P.s4b_stop(0.40, [0.399, None, 0.398, 0.397])
        return not s1['verdict'].startswith('STOP') and not s2['verdict'].startswith('STOP') and s1['improvements_dec'] == [None] * 3, f'{s1["verdict"][:60]} / {s2["verdict"][:60]}'
    _case(ok, 'REGRESSION B3 (Codex: 3 missing S4b results -> 3 non-improvements): unresolved attempts never establish the stop', b3_stop_missing)
    def b3_next_distinct():
        dims = ('lNs', 'WT'); us = np.array([0.55, 0.40]); Hm = np.array([[2.0, 0.3], [0.3, 1.0]]); Jq = lambda u: 0.02 + float((u - us) @ Hm @ (u - us))
        rng = np.random.default_rng(1); U = np.vstack([us, rng.random((14, 2))])
        pool = [{'id': f'p{k}', 'stage': 'S4a', 'x': P.from_unit(u, dims), 'sqrtJ': math.sqrt(Jq(u))} for k, u in enumerate(U)]
        pr = P.propose(pool, dims); u = np.array(pr['proposal_unit'])
        d = float(np.min(np.linalg.norm(U - u, axis=1)))
        return pr['verdict'].startswith('PROPOSAL') and d >= P.DUP_SEP - 1e-12 and pr['selected_rank'] >= 1, f'{pr["verdict"][:40]}; distance {d:.2e}'
    _case(ok, 'REGRESSION A1: surrogate minimum on an evaluated point -> the lowest-ranked DISTINCT feasible point is proposed', b3_next_distinct)
    def b3_stall():
        info = synth_info(); C = lhs_archive(); saved = getattr(P, 'select_distinct', None)
        P.select_distinct = lambda *a, **k: None
        try: res = P.surrogate(C, info)
        finally:
            if saved is None: del P.select_distinct
            else: P.select_distinct = saved
        return res['verdict'].startswith('STOP S4b: OPTIMIZER STALL') and res['s4b_stop']['improvements_dec'] == [], res['verdict'][:100]
    _case(ok, 'REGRESSION A1/B3: exhaustion of distinct points is an OPTIMIZER STALL, never invented native non-improvements', b3_stall)
    # ---- B5: full numerical column rank
    def b5_rank():
        names = ['lNs', 'WT', 'dV0', 'lmu', 'ell']; Qm = np.linalg.qr(np.random.default_rng(1).normal(size=(5, 5)))[0]
        a = P.jac_analysis(Qm[:3, :] / np.array([P.SCALE[n] for n in names]), names)
        nul = [w for w in a['weak_combinations'] if w['singular_value'] == 0.0]
        return a['flag'] and a['full_column_rank'] is False and a['column_rank'] == 3 and len(nul) == 2, f'flag {a["flag"]}, rank {a.get("column_rank")}'
    _case(ok, 'REGRESSION B5 (Codex: reduced SVD omits null directions): 3 residuals x 5 parameters (rank 3) never permits individual values', b5_rank)
    def a3_rank():
        dims = ('lNs', 'WT'); t_ = np.linspace(0.1, 0.9, 10)
        pool = [{'id': f'L{k}', 'stage': 'S4a', 'x': P.from_unit([a, a], dims), 'sqrtJ': 0.1 + (a - 0.4) ** 2} for k, a in enumerate(t_)]
        pr = P.propose(pool, dims)
        return pr['verdict'].startswith('REFUSED') and 'rank' in pr['verdict'], pr['verdict'][:120]
    _case(ok, 'REGRESSION A3: a rank-deficient quadratic design (10 collinear archive points) is refused, never extrapolated', a3_rank)
    # ---- nuisance range anchored to one baseline Q_f
    def anchor():
        c = COX / Q; R = [synth_run(t, TRUE, qf=QF0 - 0.4 * c) for t in FILMS]   # launched +0.4 V from the anchor (a re-profiled S4b launch)
        info = synth_info(nuis=dict(TRUE_NUIS, dQf=-0.7 * c))                     # the target needs +0.7 V from the anchor (+0.3 V from the launch)
        p = P.profile_films(R, info); pp = p['profiled']
        return pp['at_bound']['dV0'] and abs(pp['dV0_from_anchor_V'] - 0.5) < 2e-3 and p['qualified'] is False, f'dV0 from anchor {pp.get("dV0_from_anchor_V")}'
    _case(ok, 'REGRESSION (anchor): the +-0.5 V nuisance range is anchored to the baseline Q_f; a re-profiled launch gains no extra range', anchor)
    # ---- A9, A10, S4c
    def a10_native():
        info = synth_info(); t = 6.3; vg = VG_RUN[np.abs(VG_RUN - 1.5) > 1e-9]
        i_ok = curve(vg, TRUE, t, QF0 + TRUE_NUIS['dQf'], mu_law(TRUE_NUIS['mu_inf'], TRUE_NUIS['ell'], t))
        a = P.acceptance(vg, i_ok, t, info, kind='native'); m = a['criteria']['mu_FE_err_pct']['per_V']['1.5']
        return m['ok'] is None and 'native' in m['how'] and not a['verdict'].startswith('PASS'), f'{m["how"]}; {a["verdict"][:60]}'
    _case(ok, 'REGRESSION A10: native 5.3 scoring keeps native sampling (no native point at 1.5 V -> mu_FE(1.5) unresolved, never interpolated)', a10_native)
    def a9_fill():
        info = synth_info(); base = [synth_run(t, TRUE, rid=f'b{t}') for t in FILMS]
        try: P.sensitivity([synth_run(6.3, TRUE, rid='p6.3', extra_shift=0.03, label='c10_s6_02_6p3')], base, info, fill_from_base=True); r1 = False
        except SystemExit as e: r1 = 'film-local' in str(e)
        s = P.sensitivity([synth_run(6.3, TRUE, rid='p6.3', extra_shift=0.03, label='c10_s6_23_6p3')], base, info, fill_from_base=True)
        return r1 and s['films'] == [2.0, 6.3, 13.2] and any('FILLED FROM BASE' in x for x in s['labels']), str(s['labels'])[:160]
    _case(ok, 'REGRESSION A9: only a designated film-local perturbation (S6-23) may be filled from the base, explicitly labelled', a9_fill)
    def a1_a2():
        import inspect
        try: P.trust_halfwidth(2, 'nn'); r1 = False
        except SystemExit: r1 = True
        return r1 and 's4a_only' not in inspect.signature(P.surrogate).parameters and P.S4C_TOL_DEC == 0.01, f'nn refused {r1}'
    _case(ok, 'REGRESSION A1/A2/A10: no nn trust switching, no S4a-only surrogate; S4c tolerance 0.01 dec', a1_a2)


# ------------------------------------------------------------------------------------------------ Codex v2 review 2026-10-13 ~03:10Z: regressions
def cases_regressions_v3(ok):
    real = all((ce.ct.PKG / v).is_dir() for v in (RUNS['0061'], RUNS['0069'], RUNS['0074']))
    ns9 = math.log10(9e19 * 2e-7)
    # ---- fix 1: the shared-model guard inside profile_films
    def f1_synthetic():
        info = synth_info(); R = [synth_run(2.0, TRUE), synth_run(13.2, dict(TRUE, lNs=ns9))]
        try: p = P.profile_films(R, {t: info[t] for t in (2.0, 13.2)}); return False, f'accepted: {p["verdict"]}, qualified {p.get("qualified")}'
        except SystemExit as e: return 'shared model' in str(e), str(e)[:160]
    _case(ok, 'REGRESSION v3 fix 1 (Codex: direct profiling bypasses shared-model consistency): films with Nt2 2e19 and 9e19 are refused by profile_films', f1_synthetic)
    def f1_real():
        if not real: return True, 'skipped: real run files missing'
        def mp(m): m['thickness_laws']['Nt_cm3']['Nt2'] = 9e19
        d = _patched_copy(RUNS['0069'], lambda e: {'overrides': [o if 'Nt_cm3.Nt2' not in o else 'thickness_laws.Nt_cm3.Nt2=9e+19' for o in e['overrides']]}, mp)
        r = P.load(str(d)); r61 = P.load(RUNS['0061'])
        syn = real_targets([r61, P.load(RUNS['0069'])], {'dQf': -0.6e12, 'mu_inf': 70.0, 'ell': 11.0})
        try: p = P.profile_films([r61, r], syn); return False, f'eligible {r["eligibility"]["eligible"]}; accepted: {p["verdict"]}, qualified {p.get("qualified")}'
        except SystemExit as e: return r['eligibility']['eligible'] and 'shared model' in str(e), str(e)[:160]
    _case(ok, 'REGRESSION v3 fix 1 (real files): an eligible copy of run_0069 with Nt2 9e19 cannot be profiled with run_0061 (Nt2 2e19)', f1_real)
    # ---- fix 2: input-only expected held-out signature in every mode
    def f2_a7():
        A = _a7_fixture(); rec = A['rf']['frozen'][0]
        nat = synth_run(6.3, rec['coords'], qf=rec['Qf_cm2'], mu_inf=rec['mu_inf_cm2Vs'], ell=rec['ell_nm'], rid='native_6p3_nc',
                        overrides=['solver.physics_options.nc300_override_cm3[6.3]=3.769e+18'])
        try: sc = P.loo_score(rec, nat, A['info'], committed_sha256=rec['sha256']); return False, f'scored: {sc["verdict"][:60]}'
        except SystemExit as e: return 'settings' in str(e) and bool((rec.get('settings') or {}).get('held_out_expected_sha256')), str(e)[:160]
    _case(ok, 'REGRESSION v3 fix 2 (Codex: A7 omits held-out physics binding): an A7 prediction with a film-specific NC300 at 6.3 nm is refused', f2_a7)
    def f2_s4a():
        F = _fold_fixture(); rec = F['rf']['frozen'][0]
        nat = synth_run(6.3, rec['coords'], qf=rec['Qf_cm2'], mu_inf=rec['mu_inf_cm2Vs'], ell=rec['ell_nm'], rid='native_6p3_nc',
                        overrides=['solver.physics_options.nc300_override_cm3[6.3]=3.769e+18'])
        try: P.loo_score(rec, nat, F['info'], committed_sha256=rec['sha256']); return False, 'scored'
        except SystemExit as e: return 'settings' in str(e) and len(rec['settings']['held_out_expected_sha256']) == 64, str(e)[:120]
    _case(ok, 'v3 fix 2: the S4a-archive mode binds the same input-only expected signature (S4a runs at the held film must equal it)', f2_s4a)
    # ---- fix 3: native confirmation wraps both endpoints' eligibility, roles and digests (real files: S1-07 vs S0-01)
    def f3_timeout():
        if not real: return True, 'skipped: real run files missing'
        d = _patched_copy(RUNS['0074'], {'status': 'TIMEOUT', 'timed_out': True, 'returncode': 1})
        raw = ps.check(str(d), RUNS['0061'])['verdict']
        rec = P.native_confirmation(str(d), RUNS['0061'], 'S1-07')
        return raw.startswith('PASS') and rec['verdict'].startswith('UNKNOWN') and rec['native']['eligible'] is False, f'unchanged profile_shared.check: {raw[:30]}; wrapped: {rec["verdict"][:70]}'
    _case(ok, 'REGRESSION v3 fix 3 (Codex: a timed-out confirmation endpoint can PASS): the wrapped confirmation of a timed-out S1-07 copy is UNKNOWN', f3_timeout)
    def f3_roles():
        if not real: return True, 'skipped: real run files missing'
        rec = P.native_confirmation(RUNS['0074'], RUNS['0061'], 'S1-07')
        try: P.native_confirmation(RUNS['0074'], RUNS['0061'], 'S3-27'); r1 = False
        except SystemExit as e: r1 = 'role' in str(e)
        st = P.confirmation_status(rec, 'S3-27', rec['reference']['digest'])
        return (rec['verdict'] == 'PASS' and rec['native']['digest'] == P.file_digest(ce.resolve(RUNS['0074'])) and r1 and st[0] is None
                and P.confirmation_status(rec, 'S1-07', rec['reference']['digest'])[0] is True), f'{rec["verdict"]}; as S3-27: {st[1]}'
    _case(ok, 'REGRESSION v3 fix 3: S1-07 (run_0074 vs run_0061) confirms only its own role and reference digest; it cannot stand in for S3-27', f3_roles)


# ------------------------------------------------------------------------------------------------ Codex v3 review 2026-10-13 (FIX_FIRST)
def _deck_record(eid, patch=None):
    """a SYNTHETIC run record built only from a registered input deck (the campaign_matrix.json entry of eid: its overrides, routed as
    run_atlas.execute, material model from the campaign model file IWO_MODEL_FILE = V2, physics options as profile_s4s5.load): no run
    output is read"""
    E = {e['id']: e['campaign_entry'] for e in ce.ct.matrix()['runs']}; e = E[eid]
    ov = [patch(o) for o in e['overrides']] if patch else list(e['overrides'])
    m, _, _ = ce.ct.configs(ce.ct.V2, ov); m = json.loads(json.dumps(m, default=str))
    _, g, s = ce.ct.configs(ce.ct.V3, [o for o in ov if o.startswith(('solver.', 'geometry.'))])
    po = json.loads(json.dumps(s.get('physics_options') or {}, default=str))
    br = [k for k in ('gate_tunnelling', 'oxide_tat', 'schottky_sd') if ce.ct.bd.on((po.get(k) or {}).get('enabled'))]
    return {'run_id': f'deck_{eid}', 'label': e['label'], 't': float(e['thickness']), 'm': m, 'po': po, 'cox': ce.ct.bd.cox(g), 'overrides': ov, 'breakers': br}


def cases_regressions_v4(ok):
    # ---- fix 2: S5 scoring refuses a record frozen by different code
    def code_mismatch():
        F = _fold_fixture(); fb = F['rf']['frozen'][0]
        nat = synth_run(6.3, fb['coords'], qf=fb['Qf_cm2'], mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'], rid='native_6p3')
        old = P.seal(dict(fb, code_sha256='0' * 64))
        try: sc = P.loo_score(old, nat, F['info'], committed_sha256=old['sha256']); return False, f'scored: {sc["verdict"][:50]} ({sc.get("code_note")})'
        except SystemExit as e: return 'code' in str(e) and 'profile_s4s5.py' in str(e), str(e)[:160]
    _case(ok, 'REGRESSION v4 fix 2 (Codex v3: S5 accepts a sealed, committed record frozen by older code): refused before scoring', code_mismatch)
    def code_missing():
        F = _fold_fixture(); fb = F['rf']['frozen'][0]
        nat = synth_run(6.3, fb['coords'], qf=fb['Qf_cm2'], mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'], rid='native_6p3')
        nc = P.seal({k: v for k, v in fb.items() if k not in ('code_sha256', 'sha256')})
        try: P.loo_score(nc, nat, F['info'], committed_sha256=nc['sha256']); return False, 'scored without a code hash'
        except SystemExit as e: return 'code' in str(e), str(e)[:120]
    _case(ok, 'REGRESSION v4 fix 2: a frozen record without a code hash is refused too', code_missing)
    def code_same():
        F = _fold_fixture(); fb = F['rf']['frozen'][0]
        nat = synth_run(6.3, fb['coords'], qf=fb['Qf_cm2'], mu_inf=fb['mu_inf_cm2Vs'], ell=fb['ell_nm'], rid='native_6p3')
        sc = P.loo_score(fb, nat, F['info'], committed_sha256=fb['sha256'])
        return fb['code_sha256'] == P.CODE_SHA and 'same code' in sc['code_note'], sc['code_note']
    _case(ok, 'v4 fix 2: a record frozen by this code is still scored (code_note: same code)', code_same)
    def conf_code():
        ref = synth_run(2.0, TRUE, rid='s0_01', label='c10_s0_01_2p0', overrides=[NC + '1.373e+19'])
        nat = synth_run(2.0, TRUE, qf=QF0 + 1e12, rid='s1_07', label='c10_s1_07_2p0', overrides=[NC + '1.373e+19'])
        rec = P.native_confirmation(nat, ref, 'S1-07', checker=lambda a, b: {'verdict': 'PASS: profiling exact within 0.01 dec on every J-window point'})
        old = P.seal(dict(rec, code_sha256='0' * 64)); d = P.run_digest(ref)
        a, b = P.confirmation_status(rec, 'S1-07', d), P.confirmation_status(old, 'S1-07', d)
        return a[0] is True and b[0] is None and 'code' in b[1], f'{a} / {b}'
    _case(ok, 'REGRESSION v4 fix 2 (same class): a native-confirmation record made by other code is UNKNOWN, never a bound PASS', conf_code)
    # ---- ruling (iii): the S4c route is explicitly disabled until its wrapper binds the variable reference, settings, eligibility, digests
    def s4c_disabled():
        ref = synth_run(6.3, TRUE, rid='s4c_ref', label='c10_s4c_01_6p3'); nat = synth_run(6.3, TRUE, qf=QF0 + 1e12, rid='s4c_nat', label='c10_s4c_01_6p3')
        try: P.native_confirmation(nat, ref, 'S4c', checker=lambda a, b: {'verdict': 'PASS'}); return False, 'accepted'
        except SystemExit as e: return getattr(P, 'S4C_ROUTE_AVAILABLE', None) is False and 'S4c' in str(e) and 'disabled' in str(e), str(e)[:160]
    _case(ok, 'v4 ruling (iii): the S4c confirmation route is explicitly disabled (execution gate) until its wrapper is bound', s4c_disabled)
    # ---- ruling (iv): IGZO signature fidelity from the registered input decks (S3-11/12/13, S3-15, S3-27) with synthetic records
    def igzo_signature():
        D = {k: _deck_record(k) for k in ('S3-11', 'S3-12', 'S3-13', 'S3-15', 'S3-27', 'S1-01')}
        sig = lambda k: P.fixed_signature(D[k])['sha256']
        e63 = P.expected_signature([D['S3-11'], D['S3-13']], 6.3)['sha256']
        e20 = P.expected_signature([D['S3-12'], D['S3-13']], 2.0)['sha256']
        e132 = P.expected_signature([D['S3-11'], D['S3-12']], 13.2)['sha256']
        tg = _deck_record('S3-12', lambda o: 'solver.physics_options.mobility.tgamma=200' if o.startswith('solver.physics_options.mobility.tgamma=') else o)
        nc = dict(D['S3-12'], overrides=D['S3-12']['overrides'] + ['solver.physics_options.nc300_override_cm3[6.3]=3.769e+18'])
        good = e63 == sig('S3-12') and e20 == sig('S3-11') and e132 == sig('S3-13')
        same = sig('S3-27') == sig('S3-12') and sig('S3-15') == sig('S3-12')
        diff = P.fixed_signature(tg)['sha256'] != e63 and P.fixed_signature(nc)['sha256'] != e63 and sig('S1-01') != e63
        return good and same and diff, f'held-out match {good}; S3-27/S3-15 same {same}; tgamma / NC300[6.3] / baseline differ {diff}'
    _case(ok, 'v4 ruling (iv): IGZO expected held-out signatures built from the registered S3-11/12/13 decks equal the deck signatures at every film; '
              'S3-27 (Q_f, mu_band) and S3-15 (GAMMA0 seed) share it; tgamma, a 6.3 nm NC300 or the baseline mobility break it', igzo_signature)
    # ---- A7 wording (Codex v3): no exact-profiling promise for contacts; the refusal stays until a contact confirmation protocol exists
    def a7_contacts():
        A = _a7_fixture()
        C7 = [synth_cand(f'S5-H6p3-{k + 1}', x, stage='S5', films=(2.0, 13.2), fold=6.3, breakers=['schottky_sd']) for k, x in enumerate(A['pts'])]
        try: rr = P.loo_select(C7, 6.3, A['train'], decision=A['dec'], amendment_ref='TEST ONLY (synthetic)')
        except SystemExit as e: return 'Schottky' in str(e), f'refused: {str(e)[:120]}'
        txt = json.dumps(rr, default=str)
        return 'frozen' not in rr and not rr['verdict'].startswith('FROZEN') and 'Schottky' in txt, rr['verdict'][:120]
    _case(ok, 'v4 A7 wording: an A7 fold whose points carry a contacts (Schottky) option is not profiled (no approximate fold profiling) and freezes nothing',
          a7_contacts)


# ------------------------------------------------------------------------------------------------ Codex rulings 2026-10-13 ~03:10Z (a)-(f)
def cases_rulings_v3(ok):
    dims = ('lNs', 'WT')
    # (a) ASSUMED spending rule: separation >= 1/56 and distinct deck-rounded inputs
    o = [np.array([0.5, 0.5])]
    near, far = np.array([0.5 + 0.9 / 56, 0.5]), np.array([0.5 + 1.0 / 56, 0.5])
    ok('ruling (a): DUP_SEP = 1/56 (h/2); a point closer than 1/56 is not distinct, one at 1/56 is (deck inputs differ)',
       abs(P.DUP_SEP - 1 / 56) < 1e-15 and P.select_distinct([(0, near, 'g'), (1, far, 'g')], o, P.DUP_SEP, dims, {P.deck_inputs(P.from_unit(o[0], dims), dims)}) == 1)
    x = {'lNs': math.log10(6.0249e12), 'WT': 0.044949, 'g0': -0.31049}
    ok('ruling (a): deck rounding as make_campaign_matrix.py S4A (N_s 4 significant figures, W_T 4 decimals, GAMMA0 3 decimals)',
       P.deck_inputs(x, P.DIMS) == (6.025e12, 0.0449, -0.31) and abs(10 ** P.deck_point(x, P.DIMS)['lNs'] - 6.025e12) < 1)
    # (b) S4a inventory gates the unconditional freeze
    F = _fold_fixture(); fold = [c for c in F['C2'] if c['stage'] == 'S5']
    bad = P.candidate({'id': 'S4A-07', 'stage': 'S4a', 'runs': {str(r['t']): dict(r, eligibility={'eligible': False, 'problems': ['runner status TIMEOUT', 'timed out']})
                                                                for r in next(c for c in F['C'] if c['id'] == 'S4A-07')['R']}})
    Cb = [c if c['id'] != 'S4A-07' else bad for c in F['C']] + fold
    r1 = P.loo_select(Cb, 6.3, F['train'], decision=F['dec'])
    ex = {'rule': 'terminal ineligible S4a candidates (TIMEOUT) are excluded from the fold ranking (TEST ONLY, synthetic)', 'ref': 'TEST-ONLY', 'ids': ['S4A-07']}
    r2 = P.loo_select(Cb, 6.3, F['train'], decision=F['dec'], exclusions=ex)
    r3 = P.loo_select([c for c in F['C'] if c['id'] != 'S4A-03'] + fold, 6.3, F['train'], decision=F['dec'], exclusions=None)
    try: P.loo_select(F['C'] + fold, 6.3, F['train'], decision=F['dec'], exclusions=dict(ex, ids=['S4A-02'])); r4 = False
    except SystemExit as e: r4 = 'terminal ineligible' in str(e)
    ok('ruling (b): an UNKNOWN S4a candidate blocks the unconditional freeze (conditional ranking is DIAGNOSTIC); an explicit prospective exclusion of a '
       'terminal ineligible candidate allows it (recorded); a missing candidate blocks; a resolved candidate cannot be excluded',
       'frozen' not in r1 and r1['verdict'].startswith('UNRESOLVED') and 'DIAGNOSTIC' in r1['conditional_ranking_diagnostic']['label']
       and r2['verdict'].startswith('FROZEN') and r2['frozen'][0]['inventory']['excluded']['ids'] == ['S4A-07']
       and 'frozen' not in r3 and 'S4A-03' in r3['verdict'] and r4, r1['verdict'][:80])
    # (c) convergence flags visible
    info = synth_info(); Rc = [synth_run(t, TRUE) for t in (2.0, 13.2)]; Rc[0]['eligibility'] = dict(Rc[0]['eligibility'], convergence_flags=3)
    pc = P.profile_films(Rc, {t: info[t] for t in (2.0, 13.2)})
    ok('ruling (c): convergence flags stay visible (warning) without excluding an eligible run', pc['valid'] and any('convergence flags' in w for w in pc['warnings']))
    # (d) two selected branches: frozen original nuisance starts; no proposal without centre values
    truth = dict(TRUE, g0=-0.15, lNs=12.90); info = synth_info(x=truth); tr = {t: info[t] for t in (2.0, 13.2)}
    tail = {str(t): dict(synth_run(t, dict(TRUE, lNs=12.90), rid=f'tail_{t}'), branch={'tail_alpha': 0.0, 'nt_bulk_cm3': 0.0, 'mobility': 'constant',
                                                                                      'schottky_barrier_eV': None}) for t in FILMS}
    spec = {'base': {str(t): synth_run(t, TRUE, rid=f'base_{t}') for t in FILMS}, 'full_data_choice': [], 'branches': [
        {'name': 'igzo_a', 'group': 'mobility', 'runs': {str(t): synth_run(t, dict(TRUE, g0=-0.15), rid=f'ig_{t}') for t in FILMS}, 'converged': True,
         'activation_ok': True, 'pure_shift_or_scale': False},
        {'name': 'tail_b', 'group': 'tail', 'runs': tail, 'converged': True, 'activation_ok': True, 'pure_shift_or_scale': False}]}
    d2 = P.loo_branch(spec, 6.3, tr); lv = d2['centre_launch_values']
    ok('ruling (d): a fold choosing two branches launches at the frozen original nuisance starts (Q_f anchor, start mu law), combined branch',
       d2['fold_choice'] == ['igzo_a', 'tail_b'] and 'frozen original' in d2['centre_source'] and abs(lv['Qf_cm2'] - P.QF_ANCHOR) < 1
       and abs(lv['per_film']['2.0']['mu_band_cm2Vs'] - ps.mu_law(100.005, 7.248, 2.0, mstar(2.0))) < 1e-9
       and d2['fold_branch'] == {'tail_alpha': 0.0, 'nt_bulk_cm3': 0.0, 'mobility': 'igzo_tokyo', 'schottky_barrier_eV': None},
       f'choice {d2["fold_choice"]}; {d2.get("centre_source", "")[:50]}')
    A = _a7_fixture(); dn = P.seal(dict(A['dec'], centre_launch_values=None))
    rn = P.loo_select([], 6.3, A['train'], decision=dn)
    ok('ruling (d): an A7 fold without centre launch values gives no proposal (UNRESOLVED)', rn['verdict'].startswith('UNRESOLVED') and 'next_training_candidate' not in rn)
    # (f) bound-limited values: used in the search, with warnings
    rows = [{'id': 'S4A-01', 'sqrtJ': 0.3, 'bound_limited': ['mu_inf']}, {'id': 'S4A-02', 'sqrtJ': 0.4, 'bound_limited': []}]
    w = P._bound_warn(rows, 'sqrtJ'); rs = P.surrogate(lhs_archive(), synth_info())
    ok('ruling (f): bound-limited objective values are kept for the search and flagged (warnings in surrogate / loo_select output)',
       len(w) == 1 and 'S4A-01' in w[0] and 'unqualified' in w[0] and 'warnings' in rs and all('bound_limited' in a for a in rs['archive']))


# ------------------------------------------------------------------------------------------------ real run files, synthetic targets
RUNS = {'0061': 'results/runs/run_0061_2p0_c10_s0_01_2p0', '0068': 'results/runs/run_0068_6p3_c10_s1_01_6p3', '0069': 'results/runs/run_0069_13p2_c10_s1_02_13p2',
        '0072': 'results/runs/run_0072_2p0_c10_s1_05_2p0', '0074': 'results/runs/run_0074_2p0_c10_s1_07_2p0'}


def real_targets(R, nuis):
    """synthetic 'measured' curves made from the REAL run curves by a known transformation (no measured file is read)"""
    info = {}
    for r in R:
        lt = ps.transformed_log(r, nuis['dQf'], ps.mu_law(nuis['mu_inf'], nuis['ell'], r['t'], r['mstar']) / r['mu_band'], VG_M)
        k = np.isfinite(lt); info[r['t']] = {'vg': VG_M[k], 'i': 10 ** lt[k], 'floor': 1e-14, 'sig_floor': 0.0, 'ion': float(10 ** lt[k][-1])}
    return info


def cases_real(ok):
    for k, v in RUNS.items():
        if not (ce.ct.PKG / v).is_dir(): ok(f'real-file smoke skipped: {v} missing', True); return
    trip = [RUNS['0061'], RUNS['0068'], RUNS['0069']]
    R = [P.load(x) for x in trip]
    nuis = {'dQf': -0.6e12, 'mu_inf': 70.0, 'ell': 11.0}
    syn = real_targets(R, nuis)
    real_measured = ce.measured
    try:
        ce.measured = lambda: (syn, 2.15e-5)   # profile_shared.profile reads its targets through ce.measured: synthetic here
        t0 = time.time(); a = ps.profile(trip, 'synthetic-target smoke'); b = P.profile_films(R, syn)
    finally:
        ce.measured = real_measured
    pa, pb = a['profiled'], b['profiled']
    same = all(abs(pa[k] - pb[k]) <= 1e-12 * max(1.0, abs(pa[k])) for k in ('sqrtJ_dec', 'Qf_cm2', 'mu_inf_cm2Vs', 'ell_nm'))
    ok('REAL FILES (run_0061/0068/0069), synthetic targets: profile_films == profile_shared.profile for a triple (bitwise)', same,
       f'{time.time() - t0:.1f} s; sqrtJ {pa["sqrtJ_dec"]:.2e} vs {pb["sqrtJ_dec"]:.2e}')
    ok('REAL FILES, synthetic targets: the known transformation is recovered through real curves',
       abs(pb['dQf_cm2'] - nuis['dQf']) < 1e-3 * 1e12 and abs(pb['mu_inf_cm2Vs'] / nuis['mu_inf'] - 1) < 1e-3 and abs(pb['ell_nm'] - nuis['ell']) < 0.05 and pb['sqrtJ_dec'] < 1e-3)
    c = P.candidate({'id': 'BASE', 'runs': dict(zip(('2.0', '6.3', '13.2'), trip))})
    nv = P.nuisance_at(c, {'profiled': {'Qf_cm2': 1.38345e12, 'mu_inf_cm2Vs': 100.005, 'ell_nm': 7.248}})
    ok('REAL FILES: launched coordinates read from the runs (N_s 4e12, W_T 0.040, constant mobility) and the start mu_band values reproduced',
       abs(10 ** c['x']['lNs'] - 4e12) < 1 and c['x']['WT'] == 0.04 and c['x']['g0'] is None and c['branch']['mobility'] == 'constant'
       and all(abs(nv['per_film'][t]['mu_band_cm2Vs'] / m - 1) < 2e-4 for t, m in (('2.0', 17.6897), ('6.3', 44.1956), ('13.2', 63.2597))))
    try: P.candidate({'id': 'X', 'runs': {'2.0': RUNS['0074'], '13.2': RUNS['0069']}}); r1 = False
    except SystemExit as e: r1 = 'Q_f differs' in str(e)
    try: P.load_archive({'candidates': [{'id': 'A', 'runs': dict(zip(('2.0', '6.3', '13.2'), trip))},
                                        {'id': 'B', 'runs': {'2.0': RUNS['0072'], '6.3': RUNS['0068'], '13.2': RUNS['0069']}}]}); r2 = False
    except SystemExit as e: r2 = 'non-fitted settings differ' in str(e)
    try: P.load('results/sealed/campaigns/x'); r3 = False
    except SystemExit: r3 = True
    ok('REAL FILES: Q_f mismatch refused; NC-convention mixing (run_0072 3-D NC vs quasi-2D) refused; results/sealed refused', r1 and r2 and r3)
    # B1 on every already-seen smoke run: eligibility = score_register.run_problems (C3) with the profiling statuses; never a crash
    import score_register as sr
    allr = sorted(p.name for p in (ce.ct.PKG / 'results' / 'runs').glob('run_00[67]*') if 61 <= int(p.name[4:8]) <= 74)
    elig, same = {}, True
    for name in allr:
        rr = P.load(f'results/runs/{name}'); d_, e_, c_ = sr.load(f'results/runs/{name}')
        same &= rr['eligibility']['problems'] == sr.run_problems(e_, c_, statuses=P.PROFILE_STATUSES); elig[name[:8]] = rr['eligibility']['eligible']
    bad = sorted(k for k, v in elig.items() if not v)
    ok('REAL FILES (run_0061..run_0074): every run loads with its eligibility = score_register.run_problems; ineligible = SIMULATOR_ERROR 0062-0064, '
       'SIGN_REVERSAL 0066, TIMEOUT 0073', len(allr) == 14 and same and bad == ['run_0062', 'run_0063', 'run_0064', 'run_0066', 'run_0073'], f'ineligible {bad}')
    sig = {k: P.fixed_signature(P.load(RUNS[k]))['sha256'] for k in ('0061', '0072', '0074')}
    ok('REAL FILES: S1-07 (run_0074: other Q_f and mu_band only) has the same non-fitted settings as S0-01; S1-05 (3-D NC) does not',
       sig['0061'] == sig['0074'] and sig['0061'] != sig['0072'])
    ok('REAL FILES: S0-01 / S1-01 / S1-02 are at the S1-01 start parameters; S1-07 (other Q_f) is not',
       all(P.at_start(P.load(RUNS[k])) == [] for k in ('0061', '0068', '0069')) and P.at_start(P.load(RUNS['0074'])) != [])
    mt = P.measured_training((2.0, 13.2)); full_, _ = real_measured()
    es = P.expected_signature([P.load(RUNS['0061']), P.load(RUNS['0069'])], 6.3); s68 = P.fixed_signature(P.load(RUNS['0068']))
    ok('REAL FILES (v2 fix 2): the input-only expected 6.3 nm signature from run_0061 + run_0069 equals the actual S1-01 run_0068 signature',
       es['sha256'] == s68['sha256'], es['sha256'][:16] + ' / ' + s68['sha256'][:16])
    mx = json.loads((HERE / 'campaign_matrix.json').read_text()); fk = {}
    for e in mx['runs']:
        if e['id'].startswith('S4A'):
            r_ = {'overrides': e['campaign_entry']['overrides']}; fk.setdefault(e['film_nm'], set()).add(tuple(P.film_keyed(r_)))
    ok('FILM_KEYED equals the film-keyed inputs of every campaign_matrix S4A-* entry (read only)', all(fk[t] == {tuple(sorted(P.FILM_KEYED[t]))} for t in FILMS), str(fk))
    ok('measured_training((2.0, 13.2)) = campaign_extract.measured for the training films (vg, i, floor, sig_floor, I_on), no 6.3 nm entry',
       sorted(mt) == [2.0, 13.2] and all(np.array_equal(mt[t]['vg'], full_[t]['vg']) and np.array_equal(mt[t]['i'], full_[t]['i'])
                                         and all(mt[t][k] == full_[t][k] for k in ('floor', 'sig_floor', 'ion')) for t in (2.0, 13.2)))
    # 5.3 acceptance active RMSE and I_D(3 V) reproduce the runner's execution.json numbers (S0-01 / S1-02, already-seen runs; real measured data)
    info, _ = ce.measured(); good = True; msg = []
    for key in ('0061', '0069'):
        r = P.load(RUNS[key]); exj = json.loads((ce.resolve(RUNS[key]) / 'execution.json').read_text())
        acc = P.acceptance(r['vg'], r['i'], r['t'], info)['criteria']
        d1 = abs(acc['active_rmse_dec']['value'] - exj['fit_metrics']['regions']['active']['rmse_log10'])
        d2 = abs(acc['Id3V_err_pct']['value'] - exj['fit_metrics']['on_error_3V_percent'])
        good &= d1 < 1e-9 and d2 < 1e-9; msg.append(f'{key}: dRMSE {d1:.1e}, dId3V {d2:.1e}')
    ok('REAL FILES: 5.3 active RMSE and I_D(3 V) error equal execution.json fit_metrics (run_0061, run_0069)', good, '; '.join(msg))


def main(argv):
    res = []
    def ok(name, cond, info=''): res.append((name, bool(cond), info))
    P.STARTS = np.linspace(-0.4, 0.4, 3)   # fewer optimiser starts for synthetic speed (the real-file equivalence test restores 9)
    groups = [cases_profile, cases_surrogate, cases_surrogate_e2e, cases_loo, cases_branch, cases_acceptance, cases_jacobian, cases_sensitivity]
    if '--regressions-only' in argv: groups, argv = [], list(argv) + ['--no-real']
    groups = groups + [cases_regressions, cases_regressions_v3, cases_rulings_v3]
    groups = groups + [cases_regressions_v4]
    if '--v3-only' in argv: groups, argv = [cases_regressions_v3], list(argv) + ['--no-real']
    if '--v4-only' in argv: groups, argv = [cases_regressions_v4], list(argv) + ['--no-real']
    for g in groups:
        try: g(ok)
        except Exception as e:   # a crash is a failed case, never a silent skip
            import traceback; ok(f'{g.__name__} raised {type(e).__name__}: {e}', False, traceback.format_exc()[-800:])
    if '--no-real' not in argv:
        P.STARTS = np.linspace(-0.4, 0.4, 9)
        try: cases_real(ok)
        except Exception as e:
            import traceback; ok(f'cases_real raised {type(e).__name__}: {e}', False, traceback.format_exc()[-800:])
    for n, p, i in res: print(('ok   ' if p else 'FAIL ') + n + (f'   [{i}]' if i else ''))
    print(f'{sum(p for _, p, _ in res)}/{len(res)} ok')
    return 0 if all(p for _, p, _ in res) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
