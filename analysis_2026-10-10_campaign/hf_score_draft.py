#!/usr/bin/env python3
"""*** DRAFT, NOT FROZEN. NOT TO BE USED FOR SCORING until the H-F operational definitions are frozen by a logged entry
(work chat / register amendment) by the user. *** v3 2026-10-13: the Codex rulings of 2026-10-13 (~01:55Z: "GO-WITH-CHANGES on the
definitions") are encoded with blocking fix B4, and the Codex v2 review (~03:10Z, FIX_FIRST) fixes 3 (consumer side: only a sealed,
role- and digest-bound native confirmation counts) and 4 (role identity of every input of D1-D5), with ruling (e). v4: the Codex v3
review (FIX_FIRST) fix 1 - D5 dispatches by registered branch name; IGZO counts only through its qualified triple with a bound S3-27
PASS (a native route under the IGZO name is refused), and the contacts native route is explicitly UNAVAILABLE (CONTACT_ROUTE_AVAILABLE =
False) until the contact run roles and one shared contact model are registered (ruling ii). Written before any H-F launch (S3-10..S3-13,
S3-27 held in campaign_C10_DIAG_HF).

Draft operational definitions of the register's H-F predictions (iwo-tft-research-private/codex/work_chat/HYPOTHESIS_REGISTER.md,
tag register-rev2-frozen-20261010T1833Z, section "H-F: the 6.3 nm shape residual is unexplained (renamed, A7)", lines 238-247).
Each definition, its register source line and the ruling are in HF_DEFINITIONS_DRAFT_2026-10-13.md. No CLI scoring command exists on
purpose: the only command is `selftest` (synthetic curves only). The functions take run dictionaries from profile_s4s5.load (eligibility,
label and digest included), measured-curve dictionaries (campaign_extract.measured) and sealed native-confirmation records
(profile_s4s5.native_confirmation); every result carries STATUS (DRAFT). NO simulator call; nothing is written.

Register text implemented (quoted):
  l.241 "Contacts S3-17 to S3-23 are conditional. Trigger, frozen now: run them only if the 6.3 nm shape RMSE stays > 0.15 dec
        after S3-10 to S3-13."
  l.244 "Two-film reference: 6.3 nm needs a rigid shift of +0.28 +- 0.08 V and a current scale of 0.15 to 0.35."
  l.245 "Baseline shape RMSE > 0.15 dec."
  l.246 "IGZO.TOKYO improves 6.3 nm by >= 0.05 dec and moves gamma toward 0.9 to 1.3, and gives gamma >= 0.5 at 13.2 nm (measured
        0.27). It is therefore not adopted under the rule that no film may get worse."
  l.247 "Falsified if the baseline passes, or any natively confirmed branch passes 5.3 for all three films."
  l.240 "S3-10 to S3-13, with native confirmation S3-27 required before any branch counts (restored, A7)."   l.242 "The S5 fold that
        leaves out 6.3 nm."

Roles (Codex v2 fix 4): every input is checked against its designated run - label (campaign matrix) and film - and, for the baseline,
the S1-01 start parameters: S0-01 c10_s0_01_2p0 (2.0 nm), S1-01 c10_s1_01_6p3 (6.3), S1-02 c10_s1_02_13p2 (13.2), S3-10 c10_s3_10_6p3,
S3-11 c10_s3_11_2p0, S3-12 c10_s3_12_6p3, S3-13 c10_s3_13_13p2. Native confirmations (fix 3): S3-27 vs S3-12 and S1-07 vs S0-01, as
sealed profile_s4s5.native_confirmation records accepted only for their role and the reference run actually used (digest).

Definitions (Codex ruling 2026-10-13 on each; the drafter's choices 1-5 of the v1 digest):
  shape RMSE (ruling 1): sqrt of the film's equal-window J term ((RMSE_sub^2 + RMSE_on^2) / 2, CAMPAIGN_DESIGN 5.1 windows on the measured
    grid) after a free rigid shift dV and current scale s; dV by a 5 mV grid over +-0.5 V plus bounded refinement, s closed form; both
    windows >= 95 % covered at the optimum. A bound hit or a coverage gap is UNRESOLVED. "Baseline" = S1-01 (6.3 nm) at the start parameters.
  D1 two-film reference (ruling 2): shared (dV0, mu_inf, ell) profiled on the quasi-2D S0-01 (2.0 nm) and S1-02 (13.2 nm) only; the
    extra profiled shift dV_n and scale s_n on top of the two-film S1-01 prediction are scored SEPARATELY and JOINTLY (shift 0.20..0.36 V,
    scale 0.15..0.35, edges inclusive) at the optimum; near-optimal (degeneracy) ranges are reported; the direct V_th,cc difference is a
    diagnostic only. A two-film profile that is not qualified (not valid / at a bound) leaves D1 UNRESOLVED.
  D2 baseline shape (ruling 1): shape RMSE(S1-01) > 0.15 dec -> PASS.
  D3 IGZO.TOKYO (ruling 3; S3-11/12/13 at GAMMA0 -0.31 vs S0-01/S1-01/S1-02; every part UNRESOLVED without a bound S3-27 PASS):
    a) PRIMARY: shape gain shape(S1-01) - shape(S3-12) >= 0.05 dec (the shared-profile 6.3 nm term is reported, not scored);
    b) "toward": the native power-law gamma of S3-12 is closer to [0.9, 1.3] than S1-01's, or stays inside if S1-01 is already inside;
       a failed or V_T-bound fit (either run) is UNRESOLVED;
    c) native gamma(S3-13) >= 0.5 (failed / bound fit UNRESOLVED);
    d) "not adopted under the no-worse rule" needs an ACTUAL worsening (> 0.03 dec in some film's RMSE_sub / RMSE_on); insufficient gain
       alone is FAIL; an unqualified adoption profile is UNRESOLVED.
  D4 contact trigger (ruling 4, reading A): exactly the roles S1-01, S3-10 and S3-12, each a labelled 6.3 nm shape fit of its run; FIRE iff
    every shape RMSE > 0.15 dec; S3-12 counts only with a bound S3-27 PASS (failed, missing, timed-out or unbound -> UNRESOLVED).
  D5 falsification (ruling 4, B4, ruling e): two baseline routes - (i) a VALID S1-01 6.3 nm shape fit with shape RMSE <= 0.15 dec, (ii) a
    QUALIFIED baseline triple (S0-01/S1-01/S1-02; valid, OK, not at a bound, bound S1-07 PASS) passing 5.3 at all three films - and every
    confirmed branch: IGZO ONLY through a qualified S3-11/12/13 triple with a bound S3-27 PASS (v4: a native route under the IGZO name is
    refused); contacts: route UNAVAILABLE (v4, Codex v3 fix 1 / ruling ii: run roles and one shared contact model are not registered, so
    the row is UNKNOWN); any other name has no route. A valid evaluated confirmation FAIL counts as evaluated and cannot falsify; a
    missing, timed-out or unevaluable confirmation is UNKNOWN. A decisive qualified falsification stands on its own; NOT FALSIFIED needs the complete prescribed
    inventory (IGZO always; contacts iff D4 FIRE; unknown set if D4 is UNRESOLVED).
  S5 fold leaving out 6.3 nm (ruling 5): "test listed, no separate H-F prediction"; H-J's forecast is retained.
"""
import math
import sys

import numpy as np
from scipy.optimize import minimize_scalar

import campaign_extract as ce
import profile_shared as ps
import profile_s4s5 as P

STATUS = 'DRAFT (H-F operational definitions NOT frozen; not a registered score; not to be used for scoring until frozen by a logged entry)'
TAG = 'register-rev2-frozen-20261010T1833Z'
RULINGS = 'Codex rulings 2026-10-13 (~01:55Z, ~03:10Z and the v3 review) encoded in the draft; the user freezes it (or not) by a logged entry'
HF = {'shift_V': (0.28, 0.08), 'scale': (0.15, 0.35), 'shape_dec': 0.15, 'igzo_gain_dec': 0.05, 'gamma_6p3': (0.9, 1.3), 'gamma_13p2_min': 0.5,
      'trigger_dec': 0.15, 'adopt_worse_dec': 0.03, 'adopt_gain_dec': 0.03}
DV_BOUND, DV_STEP, COV_MIN, DEGEN_DEC = 0.5, 0.005, 0.95, 0.01
IGZO_G0 = -0.31                     # S3-11/12/13 GAMMA0 (the only IGZO seed in the rev2 H-F set)
ROLE_RUNS = {'S0-01': ('c10_s0_01_2p0', 2.0), 'S1-01': ('c10_s1_01_6p3', 6.3), 'S1-02': ('c10_s1_02_13p2', 13.2), 'S3-10': ('c10_s3_10_6p3', 6.3),
             'S3-11': ('c10_s3_11_2p0', 2.0), 'S3-12': ('c10_s3_12_6p3', 6.3), 'S3-13': ('c10_s3_13_13p2', 13.2)}   # campaign matrix labels
ROLES = {k: ROLE_RUNS[k][0] for k in ('S1-01', 'S3-10', 'S3-12')}   # D4: exactly these roles
TRIPLES = {'baseline': {'roles': {2.0: 'S0-01', 6.3: 'S1-01', 13.2: 'S1-02'}, 'confirmation': 'S1-07', 'reference_film': 2.0},
           'IGZO': {'roles': {2.0: 'S3-11', 6.3: 'S3-12', 13.2: 'S3-13'}, 'confirmation': 'S3-27', 'reference_film': 6.3}}
IGZO_BRANCH = 'IGZO.TOKYO (S3-11/12/13, S3-27)'
CONTACT_BRANCH = 'contacts (S3-17..S3-23)'
BRANCH_KIND = {IGZO_BRANCH: 'IGZO'}
CONTACT_ROUTE_AVAILABLE = False     # Codex v3 fix 1 / ruling (ii): contact run roles and one shared contact model are not registered yet
CONTACT_UNAVAILABLE = ('contacts route unavailable: the contact run roles and one shared contact model are not registered (Codex v3 fix 1, '
                       'ruling ii) - UNKNOWN, cannot falsify')
NC_Q2D = 'solver.physics_options.nc300_override_cm3[2.0]='
DISCLOSURE = ('RETROSPECTIVE inputs: S0-01 (run_0061), S1-01 (run_0068), S1-02 (run_0069) and the measured curves were seen before these '
              'definitions were written; the V2 result is known (V2 triple: 6.3 nm shape-only residual 0.036 dec at a free shift of +0.24 V, '
              'IMPLEMENTATION.md 11.7; a different model, the same metric)')
S5_6P3 = {'definition': 'S5 fold that leaves out 6.3 nm (register l.242)', 'reading': 'test listed, no separate H-F prediction (Codex ruling 5)',
          'forecast': "H-J's forecast for the fold is retained unchanged; nothing in this file scores the fold for H-F"}
Q = ps.Q
TINY = 1e-12


def _out(d): return {'status': STATUS, 'register_tag': TAG, 'rulings': RULINGS, **d}


def band(x, lo, hi):
    """registered bands: both edges inclusive (as score_register.band)"""
    return 'PASS' if lo - TINY <= x <= hi + TINY else 'FAIL'


def _windows(Mt):
    return {'sub': (Mt['i'] >= 10 * Mt['floor']) & (Mt['i'] <= 1e-9), 'on': (Mt['vg'] >= 1 - 1e-9) & (Mt['vg'] <= 3 + 1e-9)}


def role_ok(r, role):
    lab, t = ROLE_RUNS[role]; return r.get('label') == lab and r.get('t') is not None and abs(float(r['t']) - t) < 1e-9


def _require_role(r, role):
    """Codex v2 fix 4: the run must be the designated run of the role (label and film)"""
    if not role_ok(r, role):
        raise SystemExit(f'refused: {r.get("run_id")} ({r.get("label")}, {r.get("t")} nm) is not the {role} run {ROLE_RUNS[role]} (role identity, Codex v2 fix 4)')


def _require_start(r, role, **kw):
    _require_role(r, role)
    why = P.at_start(r, **kw)
    if why: raise SystemExit(f'refused: {role} ({r.get("run_id")}) must be at the S1-01 start parameters (Codex ruling 1): {why}')


# ------------------------------------------------------------------------------------------------ shape RMSE (free shift + scale)
def _shape_terms(r, Mt, dv):
    """J term at shift dv with the closed-form optimal log10 scale: J(ls) = ((a + ls)^2_sub + (b + ls)^2_on) / 2 is minimal at
    ls = -(mean a + mean b) / 2"""
    lt = ps.transformed_log(r, -dv * r['cox'] / Q, 1.0, Mt['vg']); lm = np.log10(Mt['i']); W = _windows(Mt)
    a = (lt - lm)[W['sub'] & np.isfinite(lt)]; b = (lt - lm)[W['on'] & np.isfinite(lt)]
    cov = {k: (float((W[k] & np.isfinite(lt)).sum()) / max(1, int(W[k].sum()))) for k in W}
    if a.size == 0 or b.size == 0: return float('inf'), 0.0, cov
    ls = -(a.mean() + b.mean()) / 2
    return float(0.5 * (np.mean((a + ls) ** 2) + np.mean((b + ls) ** 2))), float(ls), cov


def shape_fit(r, Mt):
    """shape RMSE of one film (ruling 1): free rigid shift (5 mV grid over +-0.5 V + bounded refinement: global within the bound,
    deterministic) and closed-form scale; a bound hit or < 95 % window coverage is UNRESOLVED (valid False). The run must be eligible (B1);
    the result carries the run's label, film and digest (role checks downstream)."""
    P.require_eligible([r], 'the H-F shape fit')
    grid = np.round(np.arange(-DV_BOUND, DV_BOUND + 1e-12, DV_STEP), 9)
    J = np.array([_shape_terms(r, Mt, v)[0] for v in grid]); k = int(np.argmin(J))
    lo, hi = max(-DV_BOUND, grid[k] - DV_STEP), min(DV_BOUND, grid[k] + DV_STEP)
    f = minimize_scalar(lambda v: _shape_terms(r, Mt, v)[0], bounds=(lo, hi), method='bounded', options={'xatol': 1e-7})
    dv = float(f.x) if f.fun <= J[k] else float(grid[k]); Jm, ls, cov = _shape_terms(r, Mt, dv)
    near = grid[np.sqrt(np.maximum(J, 0)) <= math.sqrt(Jm) + DEGEN_DEC] if np.isfinite(Jm) else np.array([])
    ls_near = [(_shape_terms(r, Mt, v)[1]) for v in near] if near.size else []
    at_bound = abs(dv) > DV_BOUND - DV_STEP / 2
    ok = np.isfinite(Jm) and not at_bound and min(cov.values()) >= COV_MIN
    vg2, i2 = P.transformed_points(r, -dv * r['cox'] / Q, 10 ** ls)
    act = _active_rmse(vg2, i2, Mt)
    if np.isfinite(Jm): near = np.append(near, dv); ls_near = list(ls_near) + [ls]   # the refined optimum belongs to its own range
    return {'film_nm': r['t'], 'run': r.get('run_id'), 'label': r.get('label'), 'digest': P.run_digest(r),
            'shape_rmse_dec': float(math.sqrt(Jm)) if np.isfinite(Jm) else None,
            'free_dV_V': dv, 'free_scale': float(10 ** ls), 'coverage': cov, 'at_dV_bound': bool(at_bound),
            'near_optimal_dV_range_V': [float(near.min()), float(near.max())] if near.size else None,
            'near_optimal_scale_range': [float(10 ** min(ls_near)), float(10 ** max(ls_near))] if len(ls_near) else None,
            'near_optimal_rule': f'grid shifts whose shape RMSE is within {DEGEN_DEC} dec of the minimum (shift/scale degeneracy, reported)',
            'secondary_active_rmse_after_free_fit_dec': act,
            'valid': bool(ok), 'why_invalid': None if ok else ('shift at the +-0.5 V bound (UNRESOLVED)' if at_bound else
                                                               'window coverage < 95 % (no extrapolation)' if np.isfinite(Jm) else 'empty window')}


def _active_rmse(vg, i, Mt, mult=5.0):
    o = float(np.median(Mt['i'][(Mt['vg'] >= -2) & (Mt['vg'] <= -0.5)])); act = Mt['i'] > mult * o
    cov = (Mt['vg'] >= vg[0] - 1e-9) & (Mt['vg'] <= vg[-1] + 1e-9); m = act & cov
    if not m.any(): return None
    le = np.log10(np.maximum(np.interp(Mt['vg'], vg, i), 1e-40)) - np.log10(Mt['i'])
    return float(np.sqrt(np.mean(le[m] ** 2)))


# ------------------------------------------------------------------------------------------------ D1 two-film reference
def two_film_reference(r20, r132, r63, info):
    """D1 (register l.244; Codex ruling 2): r20 = S0-01, r132 = S1-02, r63 = S1-01 (roles enforced)"""
    for r, role in ((r20, 'S0-01'), (r132, 'S1-02'), (r63, 'S1-01')): _require_start(r, role)
    if not any(str(o).startswith(NC_Q2D) for o in r20.get('overrides') or []):
        raise SystemExit('refused: the 2.0 nm training run must be the quasi-2D S0-01 (nc300_override_cm3[2.0]; Codex ruling 2), not the 3-D NC S1-05')
    if abs(r63['qf'] - r20['qf']) > 1e-9 * abs(r20['qf']) or abs(r63['cox'] - r20['cox']) > 1e-12 * r20['cox']:
        raise SystemExit('refused: the 6.3 nm run does not share the launched Q_f / C_ox of the training runs')
    tf = P.profile_films([r20, r132], {t: info[t] for t in (2.0, 13.2)}); qual = P.qualification(tf)
    p = tf['profiled']; dv2 = p['dV0_V']; s2 = ps.mu_law(p['mu_inf_cm2Vs'], p['ell_nm'], 6.3, r63['mstar']) / r63['mu_band']
    J63, per = ps.triple_J([r63], info, p['dQf_cm2'], p['mu_inf_cm2Vs'], p['ell_nm'])
    fit = shape_fit(r63, info[6.3])
    dvn = fit['free_dV_V'] - dv2; sn = fit['free_scale'] / s2
    (c, h), (slo, shi) = HF['shift_V'], HF['scale']
    if qual: v1 = v2 = f'unresolved (two-film training profile not qualified: {"; ".join(qual)})'
    elif not fit['valid']: v1 = v2 = f'unresolved (6.3 nm free fit: {fit["why_invalid"]})'
    else: v1, v2 = band(dvn, c - h, c + h), band(sn, slo, shi)
    joint = 'PASS' if v1 == v2 == 'PASS' else 'FAIL' if 'FAIL' in (v1, v2) else v1
    rng, srng = fit['near_optimal_dV_range_V'], fit['near_optimal_scale_range']
    vgp, ip = P.transformed_points(r63, p['dQf_cm2'], s2); M = info[6.3]
    vp = ce.ex.crossing(vgp, ip, ce.rx.I_CC, True)['v']; vmc = ce.ex.crossing(M['vg'], M['i'], ce.rx.I_CC, False)['v']
    diag = {'dVth_cc_meas_minus_pred_V': (vmc - vp) if (vp is not None and vmc is not None) else None,
            'label': 'DIAGNOSTIC only (Codex ruling 2): V_th,cc(measured) - V_th,cc(two-film prediction) at 1e-9 A/um; not scored'}
    return _out({'definition': 'D1 two-film reference (register l.244; Codex ruling 2)', 'roles': {'S0-01': r20.get('run_id'), 'S1-02': r132.get('run_id'),
                 'S1-01': r63.get('run_id')}, 'training': tf, 'two_film_dV0_V': dv2, 'two_film_scale_6p3': s2, 'diagnostic_direct_dVth': diag,
                 'two_film_prediction_6p3': {'sqrtJ_term_dec': float(math.sqrt(per[6.3]['J_term'])) if np.isfinite(per[6.3]['J_term']) else None,
                                             'rmse_sub_dec': per[6.3]['sub']['rmse_dec'], 'rmse_on_dec': per[6.3]['on']['rmse_dec'],
                                             'coverage': {k: per[6.3][k]['coverage'] for k in ('sub', 'on')}, 'label': 'reported (H-J reporting rule), not scored'},
                 'free_fit_6p3': fit, 'needed_shift_V': dvn, 'needed_scale': sn,
                 'degeneracy_ranges': {'needed_shift_V': [rng[0] - dv2, rng[1] - dv2] if rng else None,
                                       'needed_scale': [srng[0] / s2, srng[1] / s2] if srng else None, 'label': 'reported; the optimum is scored'},
                 'needed_shift_near_optimal_range_V': [rng[0] - dv2, rng[1] - dv2] if rng else None,
                 'sign_convention': 'needed_shift > 0: the two-film 6.3 nm curve must move to more positive V_G (I_needed(V) = s I_pred(V - dV))',
                 'scored': {'shift': v1, 'scale': v2, 'joint': joint}, 'shift_verdict': v1, 'scale_verdict': v2, 'verdict': joint,
                 'registered': '+0.28 +- 0.08 V and scale 0.15..0.35 (both edges inclusive); scored separately and jointly',
                 'disclosure': DISCLOSURE})


# ------------------------------------------------------------------------------------------------ D2 baseline shape
def baseline_shape(r63, info):
    """D2 (register l.245; ruling 1; v2 fix 4): S1-01 (6.3 nm) at the start parameters, against the 6.3 nm target"""
    _require_start(r63, 'S1-01')
    f = shape_fit(r63, info[6.3])
    v = (f'unresolved ({f["why_invalid"]})' if not f['valid'] else 'PASS (shape RMSE > 0.15 dec: the prediction holds)'
         if f['shape_rmse_dec'] > HF['shape_dec'] else 'FAIL (shape RMSE <= 0.15 dec)')
    return _out({'definition': 'D2 baseline shape RMSE > 0.15 dec (register l.245; Codex ruling 1)', 'role': 'S1-01', 'fit': f, 'verdict': v,
                 'disclosure': DISCLOSURE})


# ------------------------------------------------------------------------------------------------ D3 IGZO
def gamma_pl(r, Mt):
    """native power-law gamma (registered extraction.pl_fit over V_G 1..3 V on the measured grid inside the solved range, the native
    current linearly interpolated as in comparison.csv)"""
    vg_fit = Mt['vg'][(Mt['vg'] >= r['vg'][0] - 1e-9) & (Mt['vg'] <= r['vg'][-1] + 1e-9)]; i_fit = np.interp(vg_fit, r['vg'], r['i'])
    try: f = ce.ex.pl_fit(vg_fit, i_fit, *ce.rx.FIT_PRIMARY)
    except Exception as e: return {'gamma': None, 'invalid': f'{type(e).__name__}: {e}'}
    return {'gamma': f['gamma'], 'sig_gamma': f['sig_gamma'], 'at_bound': f['at_bound'], 'rms_log10': f['rms_log10'], 'vt': f['vt']}


def _band_dist(x, lo, hi): return 0.0 if lo <= x <= hi else min(abs(x - lo), abs(x - hi))


def _gamma_ok(g): return g.get('gamma') is not None and not g.get('at_bound')


def toward_band(g_base, g_igzo, lo, hi):
    """ruling 3: reduced distance to [lo, hi], or remaining inside if the baseline is already inside"""
    db, di = _band_dist(g_base, lo, hi), _band_dist(g_igzo, lo, hi)
    if db == 0.0: return 'PASS (stays inside the band)' if di == 0.0 else 'FAIL (baseline inside, IGZO leaves the band)'
    return f'PASS (distance {db:.3g} -> {di:.3g})' if di < db else f'FAIL (distance {db:.3g} -> {di:.3g}: not reduced)'


def igzo_prediction(base, igzo, s3_27, info):
    """D3 (register l.246; ruling 3). base / igzo: {2.0: run, 6.3: run, 13.2: run} = S0-01/S1-01/S1-02 and S3-11/S3-12/S3-13 (roles and start
    parameters enforced); s3_27: the sealed profile_s4s5.native_confirmation record of S3-27 against THIS S3-12 (v2 fix 3)"""
    for t in P.FILMS:
        _require_start(base[t], TRIPLES['baseline']['roles'][t]); _require_start(igzo[t], TRIPLES['IGZO']['roles'][t], mobility='igzo_tokyo', g0=IGZO_G0)
    st, why = P.confirmation_status(s3_27, 'S3-27', P.run_digest(igzo[6.3]))
    gate = f'{"PASS" if st else "not confirmed"}: {why}'
    if st is not True:
        u = f'unresolved (S3-27 native confirmation not established: {why[:100]})'
        return _out({'definition': 'D3 IGZO.TOKYO (register l.246; Codex ruling 3)', 'gate_S3_27': gate, 'confirmation': s3_27 if isinstance(s3_27, dict) else None,
                     'a_gain': u, 'b_gamma_6p3': u, 'c_gamma_13p2': u, 'd_not_adopted': u, 'verdict': u})
    sb, si = shape_fit(base[6.3], info[6.3]), shape_fit(igzo[6.3], info[6.3])
    if sb['valid'] and si['valid']:
        gain = sb['shape_rmse_dec'] - si['shape_rmse_dec']; va = 'PASS' if gain >= HF['igzo_gain_dec'] - TINY else 'FAIL'
    else: gain, va = None, 'unresolved (a 6.3 nm shape fit is not valid)'
    gb, gi, g13 = gamma_pl(base[6.3], info[6.3]), gamma_pl(igzo[6.3], info[6.3]), gamma_pl(igzo[13.2], info[13.2])
    lo, hi = HF['gamma_6p3']
    vb = toward_band(gb['gamma'], gi['gamma'], lo, hi) if _gamma_ok(gb) and _gamma_ok(gi) else 'unresolved (a native power-law fit failed or is at its V_T bound)'
    vc = ('PASS' if g13['gamma'] >= HF['gamma_13p2_min'] - TINY else 'FAIL') if _gamma_ok(g13) else 'unresolved (native power-law fit failed or at its V_T bound)'
    try:
        ad = P.adopt_films([igzo[t] for t in P.FILMS], [base[t] for t in P.FILMS], info)
        worse = any(v > HF['adopt_worse_dec'] for d in ad['per_film_worsening_dec'].values() for v in d.values())
        q = P.qualification(ad['branch']) + P.qualification(ad['base'])
        if q: vd = f'unresolved (adoption profile not qualified: {"; ".join(q)[:120]})'
        elif worse: vd = 'PASS (actual worsening: not adopted under the no-worse rule)'
        elif ad['arithmetic_pass']: vd = 'FAIL (IGZO passes the adoption arithmetic)'
        else: vd = 'FAIL (not adopted by the gain clause only: no actual worsening; ruling 3)'
        adr = {'gain_dec': ad['sqrtJ_gain_dec'], 'worsening_dec': ad['per_film_worsening_dec'], 'arithmetic': ad['verdict']}
    except SystemExit as e:
        vd, adr = f'unresolved (adoption arithmetic refused: {e})', None
    sec = None
    if adr is not None:
        sec = {'base_sqrtJ_term_6p3': math.sqrt(ad['base']['profiled']['per_film']['6.3']['J_term']),
               'igzo_sqrtJ_term_6p3': math.sqrt(ad['branch']['profiled']['per_film']['6.3']['J_term']), 'label': 'secondary, reported (not scored)'}
        sec['gain_dec'] = sec['base_sqrtJ_term_6p3'] - sec['igzo_sqrtJ_term_6p3']
    parts = (va, vb, vc, vd)
    v = 'PASS' if all(x.startswith('PASS') for x in parts) else 'FAIL' if any(x.startswith('FAIL') for x in parts) else 'unresolved'
    return _out({'definition': 'D3 IGZO.TOKYO (register l.246; Codex ruling 3)', 'gate_S3_27': gate, 'confirmation': s3_27,
                 'a_gain': va, 'a_shape_rmse_dec': {'S1-01': sb['shape_rmse_dec'], 'S3-12': si['shape_rmse_dec']}, 'a_gain_dec': gain,
                 'a_secondary_shared_profile': sec,
                 'b_gamma_6p3': vb, 'gamma_native': {'S1-01': gb, 'S3-12': gi, 'S3-13': g13},
                 'b_strict_inside_diagnostic': (None if gi.get('gamma') is None else bool(lo <= gi['gamma'] <= hi)),
                 'c_gamma_13p2': vc, 'd_not_adopted': vd, 'd_adoption': adr, 'verdict': v})


# ------------------------------------------------------------------------------------------------ D4 contact trigger
def contact_trigger(shapes, s3_27):
    """D4 (register l.241; ruling 4, reading A). shapes: exactly {'S1-01', 'S3-10', 'S3-12'} -> shape_fit of the designated 6.3 nm runs (label,
    film and digest checked); s3_27: the sealed S3-27 confirmation record bound to the S3-12 run of shapes['S3-12'] (v2 fix 3)"""
    roles = set(shapes); st = None
    if roles != set(ROLES): prim = f'UNRESOLVED (roles {sorted(roles)} are not exactly {sorted(ROLES)})'
    else:
        st, why = P.confirmation_status(s3_27, 'S3-27', shapes['S3-12'].get('digest'))
        bad = [k for k, v in shapes.items() if v.get('film_nm') != 6.3 or v.get('label') != ROLES[k] or not v.get('digest')]
        inv = [k for k, v in shapes.items() if not v.get('valid')]
        if bad: prim = f'UNRESOLVED (shape fits not identified as the prescribed 6.3 nm runs (label, film, digest): {bad})'
        elif st is not True: prim = f'UNRESOLVED (IGZO S3-12 not natively confirmed: {why})'
        elif inv: prim = 'UNRESOLVED (a shape RMSE is not valid: ' + ', '.join(inv) + ')'
        elif all(v['shape_rmse_dec'] > HF['trigger_dec'] for v in shapes.values()): prim = 'FIRE: run S3-17..S3-23 (every prescribed 6.3 nm shape RMSE > 0.15 dec)'
        else: prim = 'DO NOT FIRE (a prescribed 6.3 nm shape RMSE <= 0.15 dec: ' + ', '.join(k for k, v in shapes.items() if v['shape_rmse_dec'] <= HF['trigger_dec']) + ')'
    return _out({'definition': 'D4 contact trigger (register l.241; Codex ruling 4, reading A)', 'roles': sorted(ROLES), 'S3-27_confirmed': st,
                 'confirmation': s3_27 if isinstance(s3_27, dict) else None, 'values_dec': {k: v.get('shape_rmse_dec') for k, v in shapes.items()}, 'verdict': prim})


def prescribed_branches(trigger):
    """the branches D5 must evaluate: IGZO always; contacts iff D4 FIRE; None (unknown set) iff D4 is UNRESOLVED"""
    v = str((trigger or {}).get('verdict', 'UNRESOLVED'))
    return [IGZO_BRANCH, CONTACT_BRANCH] if v.startswith('FIRE') else [IGZO_BRANCH] if v.startswith('DO NOT FIRE') else None


# ------------------------------------------------------------------------------------------------ D5 falsification
def profiled_triple_acceptance(R, info, confirmation=None, kind='baseline', allow_approximate=False):
    """5.3 at every film of a three-film shared profile (offline; kind 'profiled', A10). kind 'baseline' (S0-01/S1-01/S1-02, start
    parameters, confirmed by S1-07 against S0-01) or 'IGZO' (S3-11/12/13, confirmed by S3-27 against S3-12). B4 + v2 fix 3: the verdicts
    are usable only if the profile is QUALIFIED and the confirmation record is a bound PASS for this role and reference run; otherwise every
    film is 'unresolved' and the computed criteria are kept only as an unqualified diagnostic."""
    if kind not in TRIPLES: raise SystemExit(f'unknown triple kind {kind}')
    K = TRIPLES[kind]; byt = {r['t']: r for r in R}
    if sorted(byt) != list(P.FILMS): raise SystemExit('profiled_triple_acceptance needs one run per film 2.0 / 6.3 / 13.2 nm')
    for t, role in K['roles'].items():
        if kind == 'baseline': _require_start(byt[t], role)
        else: _require_start(byt[t], role, mobility='igzo_tokyo', g0=IGZO_G0)
    R = [byt[t] for t in P.FILMS]
    p = P.profile_films(R, info, allow_approximate); pp = p['profiled']; acc = {}
    for r in R:
        s = ps.mu_law(pp['mu_inf_cm2Vs'], pp['ell_nm'], r['t'], r['mstar']) / r['mu_band']
        vg, i = P.transformed_points(r, pp['Qf_cm2'] - r['qf'], s); acc[r['t']] = P.acceptance(vg, i, r['t'], info, kind='profiled')
    st, why = P.confirmation_status(confirmation, K['confirmation'], P.run_digest(byt[K['reference_film']]))
    q = P.qualification(p) + ([] if st is True else [f'transformation not natively confirmed ({why})'])
    use = acc if not q else {t: {'film_nm': t, 'kind': 'profiled', 'verdict': f'unresolved (profile not qualified: {"; ".join(q)[:160]})'} for t in acc}
    return _out({'kind': kind, 'labels': {str(t): byt[t].get('label') for t in P.FILMS}, 'profile': p, 'confirmation': confirmation,
                 'confirmation_status': st, 'qualified': not q, 'qualification': q, 'acceptance': use,
                 'diagnostic_acceptance_unqualified': acc if q else None})


def native_acceptance(r, info):
    """native 5.3 of one eligible native run (kind native), carrying the run's identity (for the contacts native route of D5)"""
    P.require_eligible([r], 'native 5.3 acceptance')
    a = P.acceptance(r['vg'], r['i'], r['t'], info, kind='native')
    return {**a, 'run': r.get('run_id'), 'label': r.get('label'), 'digest': P.run_digest(r), 'eligible': True}


def _all_pass(acc):
    if acc is None or sorted(acc) != list(P.FILMS): return None
    v = [str(a.get('verdict')) for a in acc.values()]
    return True if all(x == 'PASS' for x in v) else False if any(x.startswith('FAIL') for x in v) else None


def _triple_route(triple, kind):
    """(fires, why, confirmation status) of a profiled triple: kind, role labels, qualification and the bound confirmation are recomputed
    from the embedded data (B4, v2 fixes 3-4)"""
    if not triple: return None, 'missing', None
    K = TRIPLES[kind]
    if triple.get('kind') != kind: return None, f'triple of kind {triple.get("kind")}, not {kind}', None
    labs = triple.get('labels') or {}
    if any(labs.get(str(t)) != ROLE_RUNS[role][0] for t, role in K['roles'].items()): return None, f'triple runs are not {list(K["roles"].values())}', None
    prof = triple.get('profile') or {}; films = list(prof.get('films') or []); digs = list(prof.get('run_digests') or [])
    ref = digs[films.index(K['reference_film'])] if K['reference_film'] in films and len(digs) == len(films) else None
    st, why = P.confirmation_status(triple.get('confirmation'), K['confirmation'], ref)
    if st is not True: return (False if st is False else None), why, st
    q = P.qualification(prof)
    if q: return None, 'not qualified: ' + '; '.join(q), st
    return _all_pass(triple.get('acceptance')), 'qualified profiled triple with a bound confirmation', st


def _native_route(nat):
    """native 5.3 at all three films (kept for the contacts route; NOT reachable while CONTACT_ROUTE_AVAILABLE is False; once enabled it also
    needs the registered contact roles and one shared contact model, which do not exist yet)"""
    if not nat or sorted(nat) != list(P.FILMS): return None, 'native 5.3 missing at some film'
    bad = [t for t, a in nat.items() if a.get('kind') != 'native' or a.get('eligible') is not True or not a.get('digest')]
    if bad: return None, f'native acceptance without an eligible, identified native run at {bad}'
    return _all_pass(nat), 'native 5.3 of eligible native runs at all three films'


def falsification(baseline_shape_res, baseline_triple, branches, prescribed):
    """D5 (register l.247; ruling 4, B4, ruling e). baseline_shape_res: baseline_shape(); baseline_triple: profiled_triple_acceptance(kind
    'baseline', S1-07 record); branches: [{'name': IGZO_BRANCH, 'triple': profiled_triple_acceptance(kind 'IGZO', S3-27 record)} or
    {'name': CONTACT_BRANCH, 'native_acceptance': {t: native_acceptance(run, info)}}]; prescribed: prescribed_branches(contact_trigger(...)).
    v4 (Codex v3 fix 1): the route is chosen by the registered branch NAME first; IGZO only through its triple (a native route is refused),
    contacts UNAVAILABLE (UNKNOWN), any other name has no route."""
    rows = []
    f = (baseline_shape_res or {}).get('fit') or {}; sv = str((baseline_shape_res or {}).get('verdict', 'missing'))
    ident = f.get('film_nm') == 6.3 and f.get('label') == ROLE_RUNS['S1-01'][0]
    sh = (None if not baseline_shape_res or not ident or not f.get('valid') or sv.startswith('unresolved') else sv.startswith('FAIL'))
    rows.append({'name': 'baseline (shape route: valid S1-01 6.3 nm fit, shape RMSE <= 0.15 dec)', 'fires': sh,
                 'why': None if sh is not None else ('not the S1-01 6.3 nm fit (v2 fix 4)' if baseline_shape_res and not ident else f'shape route unresolved ({sv[:80]})')})
    b, why, _ = _triple_route(baseline_triple, 'baseline')
    rows.append({'name': 'baseline (5.3 route: qualified triple passes at all three films)', 'fires': b if b is not False or why.startswith('qualified') else None, 'why': why})
    for br in branches:
        name = br.get('name')
        if name in BRANCH_KIND:
            if br.get('native_acceptance') is not None:
                fires, why, conf = None, f'native route refused for {name}: only its qualified triple with a bound confirmation counts (Codex v3 fix 1)', None
            else:
                fires, why, conf = _triple_route(br.get('triple'), BRANCH_KIND[name])
                if conf is False: why = f'confirmation FAIL (valid evaluated): counted as evaluated, cannot falsify (ruling e; {why})'
        elif name == CONTACT_BRANCH:
            if not CONTACT_ROUTE_AVAILABLE: fires, why, conf = None, CONTACT_UNAVAILABLE, None
            else: fires, why = _native_route(br.get('native_acceptance')); conf = 'native runs'
        else: fires, why, conf = None, 'no evaluation route for this branch (unregistered name)', None
        rows.append({'name': br['name'], 'branch': True, 'confirmation': conf, 'fires': fires, 'why': why})
    names = [r['name'] for r in rows if r.get('branch')]
    missing = None if prescribed is None else [n for n in prescribed if n not in names]
    open_ = [r['name'] for r in rows if r['fires'] is None and (not r.get('branch') or prescribed is None or r['name'] in (prescribed or []))]
    if any(r['fires'] is True for r in rows): v = 'FALSIFIED (' + '; '.join(r['name'] for r in rows if r['fires'] is True) + ')'
    elif prescribed is None: v = 'UNRESOLVED (the prescribed branch set is unknown: the contact trigger is UNRESOLVED)'
    elif missing: v = f'UNRESOLVED (prescribed branch(es) missing: {missing})'
    elif open_: v = f'UNRESOLVED (not evaluated or UNKNOWN: {open_})'
    else: v = 'NOT FALSIFIED (both baseline routes negative; every prescribed branch evaluated without a confirmed pass at all three films)'
    return _out({'definition': 'D5 falsification (register l.247; Codex ruling 4, B4, ruling e)', 'rows': rows, 'prescribed': prescribed, 'missing_prescribed': missing,
                 'not_confirmed': [r['name'] for r in rows if r.get('branch') and r['confirmation'] is False], 'verdict': v})


# ------------------------------------------------------------------------------------------------ S5 fold leaving out 6.3 nm
def s5_fold_6p3():
    """ruling 5: listed as an H-F test, no separate H-F prediction; H-J's forecast is retained"""
    return _out({**S5_6P3, 'verdict': 'NO H-F PREDICTION (test listed; H-J forecast retained)'})


def main(argv):
    if argv[:1] == ['selftest']:
        import test_hf_score_draft as T; return T.main(argv[1:])
    if not argv: print(__doc__)
    print('DRAFT: no scoring command until the H-F definitions are frozen by a logged entry. Only `selftest` runs.'); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
