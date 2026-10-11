#!/usr/bin/env python3
"""Scoring code for the FROZEN hypothesis register, written and frozen BEFORE any S2/S3/AFF result (2026-10-11; review fixes 2026-10-11,
still before any S2/S3/AFF launch). NO simulator call; reads finished run directories only and writes analysis_2026-10-10_campaign/register_scores/*.json.

Register: iwo-tft-research-private/codex/work_chat/HYPOTHESIS_REGISTER.md, git tag register-rev2-frozen-20261010T1833Z
(revision 2, FROZEN 2026-10-10T18:33:13Z). Rule text implemented here (quoted from the register; section in brackets):

[0 Censoring rule]
  - A quantity below the demonstrated numerical resolution is reported as *below resolution*.
  - It counts as consistent with an upper-bound prediction only if that resolution is below the bound.
  - Otherwise it is *unresolved*, never a pass.
  - Current balance (KCL) is a sanity check, not an uncertainty estimate.
[1 Convergence]  resolved leakage within 0.1 dec under mesh refinement.
[H-E, AFF scoring, frozen (A16)]
  AFF-2p0 shifts V_th,cc by -281.6 +- 5 mV; AFF-6p3 shifts it by -62.2 +- 5 mV; the shift is rigid at every current level within +-5 mV.
  - Current levels: every 0.5 dec, from max(1e-13 A/um, 10 x the run's demonstrated resolution) up to the smaller of the two curves'
    maximum current divided by 1.5.
  - Interpolation: linear interpolation of V_G against log10 I between adjacent bias points.
  - Range and exclusions: only the range supported by both curves is used. There is no extrapolation. Censored, non-positive and
    below-resolution points are excluded.
  - Rigid means max |dV_G(I) - dV_th,cc| <= 5 mV.
  - Unresolved if fewer than 3 levels qualify.
[H-E all-inputs-off, S3-01..03 vs S0-01 / S1-01 / S1-02]  dV_th,cc at 2.0 nm: -0.13 +- 0.03 V (A13, S1-informed pre-S3 registration)
  AND the preserved revision-1 registration -0.23 +- 0.04 V (both scored, neither replaces the other); 6.3 nm: -0.062 +- 0.015 V;
  13.2 nm: -0.023 +- 0.008 V.   S3-01 - S1-05 = -0.272 +- 0.010 V (A13; not independent of the 2.0 nm all-off band).
[H-B]  I(0.7 V)/I(0.1 V) = 7.0 +- 0.5.  With (W/L)_par fitted on 13.2 nm only (calibration film frozen: 13.2 nm; Q_f branch frozen:
  with Q_f), the predicted floors at both 6.3 and 2.0 nm lie within 0.5 dec of the measured ones. The no-Q_f branch is reported as a
  sensitivity and is never selected (never a registered prediction).
[H-C]  (all subject to the censoring rule)  Nominal leakage at -3 V <= 1e-2 x floor of the same film, but only if a numerical ceiling
  below that bound is demonstrated, otherwise unresolved; extreme generation <= 1e-20 A/um, or below resolution with the resolution
  stated; worst-case leakage fails the registered flatness (slope > 2x measured + 2 sigma) or thickness-scaling criterion; resolved
  leakage under S2-11 changes by <= 0.1 dec.  Falsified if a converged tested mechanism passes all the floor criteria of
  CAMPAIGN_DESIGN 7.2 (valid points >= 80 %, |d_floor_ratio| <= 0.5 dec, |floor_slope| <= 2|measured| + 2 sigma, KCL).
[H-F]  NOT scored here (no frozen definition of the two-film reference, gamma targets or contact trigger in code yet): the H-F entries
  sit in config/campaign_C10_DIAG_HF.json, runnable=false until that scoring is implemented and frozen.

Definitions used to apply the rules (implementation choices, stated so they can be reviewed; none changes a registered number):
  * V_th,cc = registered extraction (analysis_2026-10-06_extraction/extraction.crossing at run_extraction.I_CC = 1e-9 A/um: last upward
    crossing over the whole curve, log-linear between adjacent points), via campaign_extract.load_run. A crossing whose bracket holds a
    censored point is unsupported (None -> the shift and rigidity are unresolved); there is no fall-back to an earlier crossing. AFF
    levels use the same rule. AFF top level = min over the two curves of max(I_D > 0) / 1.5 (register: "the curves' maximum current").
  * Point exclusions: non-positive I_D; censored = the runner's kcl_pass = 0 (terminal_currents.csv); below resolution = I_D < res.
    The runner's above_abs_floor (|I_D| > KCL absolute limit) censors only while the resolution is the KCL PROXY; with a demonstrated
    resolution it is a report flag (register 0: KCL is not an uncertainty estimate).
  * Resolution, one per quantity (the register does not define "demonstrated resolution" operationally; the method needs the user's
    sign-off as a logged amendment):
      I_D-type (I_D, dI_D, strip currents, AFF levels): --resolution R --resolution-source TEXT. The CLI refuses R without a source.
      I_G ceiling (hc_nominal): --resolution-ig R --resolution-ig-source FILE, FILE = a resolution_pair JSON of this scorer on column
        ig_raw_A from two gate-tunnelling runs, neither of them under test, and R >= its candidate. Anything else is PROVISIONAL.
      hc_mesh uses the I_G ceiling if given (the S2-11/S0-02 pair itself is refused as circular), else the I_D-type current resolution,
        labelled as such.
    Without a value: the runner's KCL absolute limit as a PROXY; every verdict is PROVISIONAL and a proxy never passes an upper bound.
    For AFF the level floor max(1e-13, 10 x res) is independent of res whenever res <= 1e-14 A/um (reported).
  * Leakage at -3 V = |I_G(V_G = -3 V)| (ig_raw_A, 1 um mesh width = A/um); KCL-censored at -3 V -> unresolved.
  * Generation (gen_core) = |I_D(run) - I_D(control)| over the CAMPAIGN_DESIGN 7.1 floor window V_G in [-2, -0.5] V at common bias points.
    A difference is resolved only if both currents are resolved and differ by > 0.1 dec (section 1 tolerance) or in sign, or if ONE is
    resolved more than 0.1 dec above res (lower bound |I| - res). Unresolved differences carry a ceiling (res; (10^0.1 - 1) max|I|; |I| + res).
    FAIL if a resolved lower bound exceeds the bound; a KCL-censored window point makes the verdict at best unresolved.
  * S2-11 (mesh_core): per common V_G, both below res -> skipped; resolved in both -> |dlog10 |I_G|| (inf on a sign change); resolved in
    ONE run only -> change >= log10(|I_G|/res): > 0.1 dec is a resolved change (FAIL), otherwise an unresolved point (never dropped);
    KCL-censored -> unresolved point. PASS needs >= 3 points resolved in both runs (implementation definition, as the AFF 3-level rule).
  * Worst case (hc_worst): flatness = |floor_slope| of total log10 I_D over the window (7.1) of S2-08 against the 7.2 limit; thickness
    scaling = |d_floor_ratio(S2-08 vs S1-02) - d_floor_ratio(S0-02 = run_0067 vs S0-01)| > 0.5 dec (7.2; S2-07 at 6.3 nm is kept out by
    the register). Registered verdict: PASS if either criterion fails, FAIL only if both are evaluated and both hold, else unresolved.
    The slopes of |I_G| and of dI_D are reported, not scored.
  * hc_explains: the four 7.2 criteria for a mechanism run against its matched control; H-C is falsified only if they all hold AND the
    mechanism is converged: QTNLSC by a registered S2-11 hc_mesh PASS (--mesh-score), ITAT (S2-12/S2-13) never without a logged amendment
    (TAT.SLICEPTS = 12 default untested, 5.28 PDF p.322), generation by no mechanism-specific refinement run (unresolved).
  * Floors = post_run_checks.FLOORS (MEASURED/DERIVED).
  * Labels: 'registered test (tag)' only for the registered entry labels (REG), with labels shared by several launches pinned to their
    registered run (PIN: c10_s0_02_2p0 = run_0067); the no-Q_f H-B branch is 'sensitivity, not a registered prediction'; (S2-03, S0-01)
    is a 'design-defined pair (CAMPAIGN_DESIGN 7.1)', confounded by the carrier count; anything else (or --smoke) is a smoke test.
    Output files carry the prefix smoke_ / sensitivity_ / design_ accordingly (none for registered results).

  python analysis_2026-10-10_campaign/score_register.py aff RUN BASE [--resolution R --resolution-source TEXT] [--smoke]
  python analysis_2026-10-10_campaign/score_register.py he_alloff RUN BASE | s3_minus_s105 S3-01_RUN S1-05_RUN
  python analysis_2026-10-10_campaign/score_register.py hb_ratio STRIP_RUN | hb_transfer RUN_13p2 RUN_6p3|none RUN_2p0
  python analysis_2026-10-10_campaign/score_register.py hc_nominal RUN [--resolution-ig R --resolution-ig-source PAIR.json]
  python analysis_2026-10-10_campaign/score_register.py hc_generation RUN CONTROL | hc_mesh S2-11_RUN S0-02_RUN(run_0067)
  python analysis_2026-10-10_campaign/score_register.py hc_worst S2-08_RUN S1-02_RUN S0-02_RUN(run_0067) S0-01_RUN
  python analysis_2026-10-10_campaign/score_register.py hc_explains RUN CONTROL [--mesh-score register_scores/hc_mesh_*.json]
  python analysis_2026-10-10_campaign/score_register.py resolution_pair RUN_REFINED RUN_REF [column]   (PROPOSED resolution, not registered)
  python analysis_2026-10-10_campaign/score_register.py selftest          (synthetic curves only; no run data)
"""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

import campaign_extract as ce
import post_run_checks as pc

TAG = 'register-rev2-frozen-20261010T1833Z'
OUT = ce.ct.HERE / 'register_scores'
SMOKE = 'smoke test, not a registered result'
SENS = 'sensitivity, not a registered prediction'
DESIGN = 'design-defined pair (CAMPAIGN_DESIGN 7.1), not defined by the register'
PREFIX = ((SMOKE, 'smoke_'), (SENS, 'sensitivity_'), (DESIGN, 'design_'))   # output file prefix by label; registered results have none
I_CC = ce.rx.I_CC                       # 1e-9 A/um
AFF = {'levels_dec': 0.5, 'floor_A': 1e-13, 'res_mult': 10.0, 'top_div': 1.5, 'rigid_mV': 5.0, 'min_levels': 3, 'shift_tol_mV': 5.0}
REG = {   # registered (run label, reference label) -> registered numbers
    'aff': {('c10_aff_2p0_2p0', 'c10_s0_01_2p0'): -281.6, ('c10_aff_6p3_6p3', 'c10_s1_01_6p3'): -62.2},
    'he_alloff': {('c10_s3_01_2p0', 'c10_s0_01_2p0'): {'A13': (-0.13, 0.03), 'rev1_original': (-0.23, 0.04)},
                  ('c10_s3_02_6p3', 'c10_s1_01_6p3'): {'registered': (-0.062, 0.015)}, ('c10_s3_03_13p2', 'c10_s1_02_13p2'): {'registered': (-0.023, 0.008)}},
    's3_minus_s105': {('c10_s3_01_2p0', 'c10_s1_05_2p0'): (-0.272, 0.010)},
    'hb_ratio': {'c10_s2_14_13p2', 'c10_s2_15_2p0', 'c10_s2_16_13p2', 'c10_s2_17_2p0', 'c10_strip_6p3_6p3'},
    'hb_transfer': {('c10_s2_14_13p2', 'c10_strip_6p3_6p3', 'c10_s2_15_2p0'): 'registered (Q_f branch)',
                    ('c10_s2_16_13p2', None, 'c10_s2_17_2p0'): 'sensitivity (no-Q_f branch, never selected)'},
    'hc_nominal': {'c10_s2_04_2p0', 'c10_s2_06_13p2'},
    # register A9: S2-01 and S2-02 are the matched generation controls. S1-06 (run_0073) timed out (register section 0: unresolved) and
    # has no terminal_currents.csv, so it is no control. (S2-03, S0-01) is a CAMPAIGN_DESIGN 7.1 pair, not a register pair (KIND).
    'hc_generation': {('c10_s2_01_13p2', 'c10_s2_02_13p2'), ('c10_s2_03_2p0', 'c10_s0_01_2p0')},
    'hc_mesh': {('c10_s2_11_2p0', 'c10_s0_02_2p0')},
    'hc_worst': {('c10_s2_08_13p2', 'c10_s1_02_13p2', 'c10_s0_02_2p0', 'c10_s0_01_2p0')},
    'hc_explains': {('c10_s2_04_2p0', 'c10_s0_01_2p0'), ('c10_s2_06_13p2', 'c10_s1_02_13p2'), ('c10_s2_08_13p2', 'c10_s1_02_13p2'),
                    ('c10_s2_12_2p0', 'c10_s2_04_2p0'), ('c10_s2_13_13p2', 'c10_s2_06_13p2'), ('c10_s2_01_13p2', 'c10_s2_02_13p2'),
                    ('c10_s2_03_2p0', 'c10_s0_01_2p0')}}
_S203 = DESIGN + '; S2-03 has 2 carriers and S0-01 1 (confounded by the carrier count; register A9 names only S2-01/S2-02 as matched generation controls)'
KIND = {('hb_transfer', ('c10_s2_16_13p2', None, 'c10_s2_17_2p0')): SENS + ' (register H-B: the no-Q_f branch is reported as a sensitivity, never selected)',
        ('hc_generation', ('c10_s2_03_2p0', 'c10_s0_01_2p0')): _S203, ('hc_explains', ('c10_s2_03_2p0', 'c10_s0_01_2p0')): _S203}
PIN = {'c10_s0_02_2p0': 'run_0067'}   # label of run_0062..run_0067; register H-C: S2-11 is relative to the redefined S0-02 (run_0067 form)
HB = (7.0, 0.5); HB_DEC = 0.5; GEN_BOUND = 1e-20; NOM_FRAC = 1e-2; MESH_DEC = 0.1; MESH_MIN_PTS = 3; TS_DEC = 0.5; FLOOR_WIN = (-2.0, -0.5)
SPREAD = 10 ** MESH_DEC - 1.0           # largest relative difference of two currents that agree within 0.1 dec


# ---------------------------------------------------------------- data
def load(run):
    """(dir, execution.json, columns of terminal_currents.csv sorted by V_G) of a finished transfer run"""
    d = ce.resolve(run); exj = json.loads((d / 'execution.json').read_text())
    with open(d / 'terminal_currents.csv', newline='') as f: rows = list(csv.DictReader(f))
    c = {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}; o = np.argsort(c['vg_V'])
    return d, exj, {k: v[o] for k, v in c.items()}


def resolution(exjs, given, source):
    """I_D-type resolution (I_D, dI_D, strip currents, AFF levels): (value A/um, source, demonstrated?). A given value is demonstrated
    only WITH its source (the CLI refuses it without); none given -> PROXY max(runner KCL absolute limit) of the runs (not demonstrated)"""
    if given is not None:
        return (float(given), source, True) if source else (float(given), 'given WITHOUT a source: not demonstrated (PROVISIONAL)', False)
    v = max(float(e.get('validation', {}).get('kcl_abs_limit_applied_A', 1e-17)) for e in exjs)
    return v, 'PROXY: runner KCL absolute limit (register 0: KCL is a sanity check, not a demonstrated resolution)', False


def gt_on(exj, opt='gate_tunnelling'):
    """the run's overrides switch physics_options.<opt>.enabled on"""
    return any(o.split('=', 1)[0].strip() == f'solver.physics_options.{opt}.enabled' and ce.ct.bd.on(o.split('=', 1)[1]) for o in exj.get('overrides', []) if '=' in o)


def ig_resolution(exjs, given, source, under_test=()):
    """I_G ceiling for H-C leakage (register H-C: 'only if a numerical ceiling below that bound is demonstrated'): demonstrated only by a
    resolution_pair JSON of this scorer on column ig_raw_A whose two runs both have gate tunnelling on and are not under test (no
    circular use), with the value >= the pair's candidate. Otherwise PROVISIONAL; no value -> the KCL PROXY."""
    if given is None: return resolution(exjs, None, None)
    why = None
    try:
        j = json.loads(Path(source or '').read_text()); pair = [json.loads((ce.resolve(j[k]) / 'execution.json').read_text()) for k in ('run_dir', 'ref_dir')]
    except Exception:
        j = None; why = 'not a resolution_pair JSON of this scorer with readable run directories'
    if j is not None:
        ids = {e['run_id'] for e in pair}
        if j.get('column') != 'ig_raw_A': why = f'pair column {j.get("column")}, not ig_raw_A'
        elif not all(gt_on(e) for e in pair): why = 'the pair is not two gate-tunnelling runs'
        elif ids & set(under_test): why = f'circular: the pair contains a run under test ({", ".join(sorted(ids & set(under_test)))})'
        elif j.get('candidate_resolution_A_per_um') is None or float(given) < float(j['candidate_resolution_A_per_um']) * (1 - 1e-9): why = 'value below the pair candidate'
    if why: return float(given), f'{source}: NOT a demonstrated I_G ceiling ({why}); PROVISIONAL', False
    return float(given), f'{source}: I_G refinement pair {j["run"]} vs {j["ref"]} (candidate {float(j["candidate_resolution_A_per_um"]):.3g} A/um)', True


def valid_mask(c, res, demonstrated=False):
    """I_D > 0, KCL passed and >= res; the runner's above_abs_floor censors only under the KCL PROXY (a report flag otherwise)"""
    i = c['id_A_per_um']; m = (i > 0) & (c['kcl_pass'] > 0) & (i >= res)
    return m if demonstrated else m & (c['above_abs_floor'] > 0)


def kcl_mask(c):
    """V_th,cc brackets (1e-9 A/um) lie far above every resolution: only KCL censoring and positivity apply"""
    return (c['id_A_per_um'] > 0) & (c['kcl_pass'] > 0)


def v_at(vg, i, ok, level):
    """V_G at I = level: the LAST upward crossing of the whole curve (the registered crossing rule), log-linear; None (unsupported) if
    there is none or if either bracket point is excluded (no fall-back to an earlier crossing)"""
    ks = ce.ex.upward_crossings(vg, i, level)
    if not ks or not (ok[ks[-1]] and ok[ks[-1] + 1]): return None
    return ce.ex.cross_loglin(vg, i, level, ks[-1])


def vth_cc(vg, i, ok):
    """registered V_th,cc (extraction.crossing at I_CC: last upward crossing, log-linear), None if its bracket is censored"""
    return v_at(vg, i, ok, I_CC)


def window(vg): return (vg >= FLOOR_WIN[0] - 1e-9) & (vg <= FLOOR_WIN[1] + 1e-9)


def common(va, vb, win=False):
    com = np.intersect1d(np.round(va, 6), np.round(vb, 6)); return com[window(com)] if win else com


def at(vg, v): return int(np.argmin(np.abs(vg - v)))


def status(labels, key, smoke, run_ids=()):
    """(label, registered numbers or None, notes): registered only for the registered entry labels, without --smoke, and with every
    pinned label resolving to its registered run; KIND relabels a sensitivity or a design-defined pair (never a registered prediction)"""
    reg = REG[key]; hit = labels in reg; labs = labels if isinstance(labels, tuple) else (labels,)
    note = [f'{l} is registered as {PIN[l]} only (got {r})' for l, r in zip(labs, run_ids) if l in PIN and r != PIN[l]]
    if smoke or not hit or note: return SMOKE, None, note
    return KIND.get((key, labels), f'registered test ({TAG})'), (reg.get(labels) if isinstance(reg, dict) else None), note


def prefix(label): return next((p for l, p in PREFIX if label.startswith(l)), '')


def resolution_pair(a, b, col='id_A_per_um', tol=MESH_DEC):
    """PROPOSAL, not a registered definition: candidate demonstrated resolution from a numerical-refinement pair (register section 1
    'Convergence': resolved currents within 0.1 dec under refinement). R = the largest max(|I_a|, |I_b|) over common V_G points that
    disagree by > tol dec, change sign or are zero; every point with both currents above R agrees within tol. With no disagreeing point,
    R = the smallest common same-sign current (lowest current at which agreement was shown). Cite it with --resolution-source; an I_G
    ceiling (--resolution-ig-source) needs this JSON on ig_raw_A from two gate-tunnelling runs."""
    da, ea, ca = load(a); db, eb, cb = load(b); com = common(ca['vg_V'], cb['vg_V']); bad, good = [], []
    for v in com:
        x, y = ca[col][at(ca['vg_V'], v)], cb[col][at(cb['vg_V'], v)]
        if x * y > 0 and abs(math.log10(abs(x)) - math.log10(abs(y))) <= tol: good.append(min(abs(x), abs(y)))
        else: bad.append(max(abs(x), abs(y)))
    R = max(bad) if bad else (min(good) if good else None)
    rel = lambda d: str(d.relative_to(ce.ct.PKG)).replace('\\', '/') if d.is_relative_to(ce.ct.PKG) else str(d)
    return {'test': 'resolution proposal from a refinement pair (NOT registered)', 'label': SMOKE, 'run': ea['run_id'], 'ref': eb['run_id'], 'column': col,
            'run_dir': rel(da), 'ref_dir': rel(db), 'run_gate_tunnelling': gt_on(ea), 'ref_gate_tunnelling': gt_on(eb),
            'tolerance_dec': tol, 'common_points': int(len(com)), 'disagreeing_points': len(bad), 'candidate_resolution_A_per_um': R}


def band(x, c, h): return 'unresolved (no value: no crossing or censored bracket)' if x is None else ('PASS' if abs(x - c) <= h + 1e-12 else 'FAIL')


def censored_upper(x, bound, res, demonstrated):
    """register section 0 applied to an upper-bound prediction x <= bound"""
    if x is None or not math.isfinite(x): return 'unresolved (no value)'
    if x <= 0 or x < res:
        if demonstrated and res < bound: return f'below resolution ({res:.3g} A/um), consistent with the bound (resolution < bound)'
        return f'unresolved: below resolution ({res:.3g} A/um' + (', not demonstrated' if not demonstrated else '') + f'), resolution not demonstrated below the bound {bound:.3g}'
    if x <= bound: return 'PASS' if demonstrated else 'unresolved (resolved only against a resolution that is not demonstrated; a pass needs a demonstrated resolution)'
    return 'FAIL' if demonstrated else 'FAIL (PROVISIONAL: resolution not demonstrated)'


# ---------------------------------------------------------------- H-E
def aff_core(vg_a, i_a, ok_a, vg_b, i_b, ok_b, res, dvth_cc):
    """frozen A16 rule on two curves (a = intervention, b = baseline); returns levels and the rigidity verdict"""
    top = min(i_a[i_a > 0].max() if (i_a > 0).any() else 0.0, i_b[i_b > 0].max() if (i_b > 0).any() else 0.0) / AFF['top_div']   # curves' maximum current
    lo = max(AFF['floor_A'], AFF['res_mult'] * res); lv = []
    k = 0
    while top > 0 and lo * 10 ** (AFF['levels_dec'] * k) <= top * (1 + 1e-12):
        L = lo * 10 ** (AFF['levels_dec'] * k); va, vb = v_at(vg_a, i_a, ok_a, L), v_at(vg_b, i_b, ok_b, L)
        lv.append({'I_A_per_um': L, 'V_run': va, 'V_ref': vb, 'dV_mV': (1e3 * (va - vb) if va is not None and vb is not None else None)}); k += 1
    q = [x for x in lv if x['dV_mV'] is not None]
    dev = max((abs(x['dV_mV'] - dvth_cc) for x in q), default=None) if dvth_cc is not None else None
    if dvth_cc is None: v = 'unresolved (no V_th,cc: no crossing or censored bracket)'
    elif len(q) < AFF['min_levels']: v = f'unresolved ({len(q)} qualifying levels < {AFF["min_levels"]})'
    else: v = 'RIGID (PASS)' if dev <= AFF['rigid_mV'] + 1e-9 else 'NOT RIGID (FAIL)'
    return {'level_floor_A_per_um': lo, 'level_top_A_per_um': top, 'levels': lv, 'qualifying_levels': len(q),
            'max_abs_dV_minus_dVth_cc_mV': dev, 'rigidity': v}


def aff(run, base, given=None, source=None, smoke=False):
    _, ea, ca = load(run); _, eb, cb = load(base); res, src, demo = resolution([ea, eb], given, source)
    oa, ob = valid_mask(ca, res, demo), valid_mask(cb, res, demo)
    va, vb = vth_cc(ca['vg_V'], ca['id_A_per_um'], oa), vth_cc(cb['vg_V'], cb['id_A_per_um'], ob)
    dv = 1e3 * (va - vb) if va is not None and vb is not None else None
    lab, exp, note = status((ea['label'], eb['label']), 'aff', smoke, (ea['run_id'], eb['run_id']))
    r = aff_core(ca['vg_V'], ca['id_A_per_um'], oa, cb['vg_V'], cb['id_A_per_um'], ob, res, dv)
    out = {'test': 'H-E AFF (A16 frozen scoring)', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id'], 'run_label': ea['label'], 'ref_label': eb['label'],
           'resolution_A_per_um': res, 'resolution_source': src, 'level_floor_independent_of_resolution_if_res_le': AFF['floor_A'] / AFF['res_mult'],
           'Vth_cc_run_V': va, 'Vth_cc_ref_V': vb, 'dVth_cc_mV': dv, **r}
    if note: out['label_note'] = note
    if exp is not None: out['registered_shift_mV'] = exp; out['shift_verdict'] = band(dv, exp, AFF['shift_tol_mV'])
    if not demo: out['rigidity'] = 'PROVISIONAL (resolution not demonstrated): ' + out['rigidity']
    return out


def he_alloff(run, base, smoke=False):
    _, ea, ca = load(run); _, eb, cb = load(base); lab, exp, note = status((ea['label'], eb['label']), 'he_alloff', smoke, (ea['run_id'], eb['run_id']))
    va, vb = vth_cc(ca['vg_V'], ca['id_A_per_um'], kcl_mask(ca)), vth_cc(cb['vg_V'], cb['id_A_per_um'], kcl_mask(cb)); dv = (va - vb) if va is not None and vb is not None else None
    out = {'test': 'H-E all-inputs-off dV_th,cc', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id'], 'Vth_cc_run_V': va, 'Vth_cc_ref_V': vb, 'dVth_cc_V': dv}
    if note: out['label_note'] = note
    if exp: out['bands'] = {k: {'band_V': f'{c:+.3f} +- {h:.3f}', 'verdict': band(dv, c, h)} for k, (c, h) in exp.items()}
    return out


def s3_minus_s105(run, ref, smoke=False):
    _, ea, ca = load(run); _, eb, cb = load(ref); lab, exp, note = status((ea['label'], eb['label']), 's3_minus_s105', smoke, (ea['run_id'], eb['run_id']))
    va, vb = vth_cc(ca['vg_V'], ca['id_A_per_um'], kcl_mask(ca)), vth_cc(cb['vg_V'], cb['id_A_per_um'], kcl_mask(cb)); dv = (va - vb) if va is not None and vb is not None else None
    out = {'test': 'H-E S3-01 - S1-05 (A13)', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id'], 'Vth_cc_run_V': va, 'Vth_cc_ref_V': vb, 'difference_V': dv}
    if note: out['label_note'] = note
    if exp: out.update({'band_V': f'{exp[0]:+.3f} +- {exp[1]:.3f}', 'verdict': band(dv, *exp), 'note': 'not independent of the 2.0 nm all-off band (register A13/A16)'})
    return out


# ---------------------------------------------------------------- H-B
def strip_iv(run):
    d = ce.resolve(run); exj = json.loads((d / 'execution.json').read_text())
    with open(d / 'strip_iv.csv', newline='') as f: rows = list(csv.DictReader(f))
    return exj, {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def strip_point(c, v, res):
    k = int(np.argmin(np.abs(c['vd_V'] - v)))
    if abs(c['vd_V'][k] - v) > 1e-6: return None, 'no solved point at %.1f V' % v
    i = c['id_A_per_um'][k]
    if not (c['kcl_pass'][k] > 0): return None, f'censored (KCL) at {v} V'
    if i <= 0 or i < res: return None, f'below resolution or non-positive at {v} V ({i:.3g} A/um, resolution {res:.3g})'
    return float(i), 'resolved'


def hb_ratio(run, given=None, source=None, smoke=False):
    exj, c = strip_iv(run); res, src, demo = resolution([exj], given, source); lab, _, note = status(exj['label'], 'hb_ratio', smoke, (exj['run_id'],))
    i1, s1 = strip_point(c, 0.1, res); i7, s7 = strip_point(c, 0.7, res)
    r = (i7 / i1) if (i1 and i7) else None
    v = band(r, *HB) if r is not None else f'unresolved ({s1}; {s7})'
    return {'test': 'H-B strip I(0.7)/I(0.1)', 'label': lab, 'run': exj['run_id'], 'run_label': exj['label'], 'I_0p1V': i1, 'I_0p7V': i7, 'ratio': r,
            'band': '7.0 +- 0.5', 'verdict': v if demo or r is None else f'{v} (PROVISIONAL: resolution {res:.3g} not demonstrated)', 'resolution_A_per_um': res, 'resolution_source': src,
            **({'label_note': note} if note else {})}


def hb_transfer(r13, r63, r20, given=None, source=None, smoke=False):
    """(W/L)_par fitted on 13.2 nm: I_floor,pred(t) = I_strip(t, 0.7 V) x L_p x (W/L)_par (CAMPAIGN_DESIGN 7.3) -> pred(t) = floor(13.2) I_strip(t)/I_strip(13.2)"""
    runs = {13.2: r13, 6.3: r63, 2.0: r20}; data = {t: (strip_iv(r) if r else None) for t, r in runs.items()}
    rs = {t: resolution([d[0]], given, source) for t, d in data.items() if d}; demo = all(x[2] for x in rs.values())   # each run's own resolution
    labs = tuple(d[0]['label'] if d else None for d in data.values())
    lab, kind, note = status(labs, 'hb_transfer', smoke, tuple(d[0]['run_id'] if d else None for d in data.values()))
    lp = {d[0].get('strip', {}).get('L_p_um') for d in data.values() if d}
    I = {t: (strip_point(d[1], 0.7, rs[t][0]) if d else (None, 'no run')) for t, d in data.items()}
    out = {'test': 'H-B floor transfer, (W/L)_par fitted on 13.2 nm', 'label': lab, 'branch': kind, 'runs': {t: (d[0]['run_id'] if d else None) for t, d in data.items()},
           'L_p_um': sorted(lp, key=str), 'I_strip_0p7V': {t: v[0] for t, v in I.items()}, 'floors_measured': pc.FLOORS,
           'resolution_A_per_um': {t: x[0] for t, x in rs.items()}, 'resolution_source': {t: x[1] for t, x in rs.items()}}
    if note: out['label_note'] = note
    if len(lp) != 1 or None in lp: out['verdict'] = 'unresolved (strip decks with different or missing L_p)'; return out
    if I[13.2][0] is None: out['verdict'] = f'unresolved (13.2 nm calibration strip: {I[13.2][1]})'; return out
    wl = pc.FLOORS[13.2] / (I[13.2][0] * lp.pop()); out['WL_par_per_um'] = wl; per = {}
    for t in (6.3, 2.0):
        if I[t][0] is None: per[t] = {'verdict': f'unresolved ({I[t][1]})'}; continue
        e = math.log10(pc.FLOORS[13.2] * I[t][0] / I[13.2][0] / pc.FLOORS[t])
        per[t] = {'pred_floor_A_per_um': pc.FLOORS[13.2] * I[t][0] / I[13.2][0], 'log10_pred_over_meas': e, 'verdict': 'PASS' if abs(e) <= HB_DEC else 'FAIL'}
    out['films'] = per
    vs = [per[t]['verdict'] for t in per]
    out['verdict'] = ('FAIL' if 'FAIL' in vs else 'PASS' if all(v == 'PASS' for v in vs) else 'unresolved') + ('' if demo else ' (PROVISIONAL: resolution not demonstrated)')
    return out


# ---------------------------------------------------------------- H-C
def hc_nominal(run, ig_given=None, ig_source=None, smoke=False):
    _, exj, c = load(run); res, src, demo = ig_resolution([exj], ig_given, ig_source, (exj['run_id'],)); t = float(exj['thickness_nm'])
    lab, _, note = status(exj['label'], 'hc_nominal', smoke, (exj['run_id'],))
    k = at(c['vg_V'], -3.0); hit = abs(c['vg_V'][k] + 3.0) < 1e-6; cens = hit and not (c['kcl_pass'][k] > 0)
    x = abs(float(c['ig_raw_A'][k])) if hit else None
    b = NOM_FRAC * pc.FLOORS[t]
    return {'test': 'H-C nominal leakage |I_G(-3 V)| <= 1e-2 x floor', 'label': lab, 'run': exj['run_id'], 'run_label': exj['label'], 'abs_IG_m3V_A_per_um': x,
            'bound_A_per_um': b, 'resolution_A_per_um': res, 'resolution_source': src, **({'label_note': note} if note else {}),
            'verdict': 'unresolved (KCL-censored at -3 V)' if cens else censored_upper(x, b, res, demo)}


def gen_core(ca, cb, res, demo, bound=GEN_BOUND):
    """H-C generation on two runs' columns (a = mechanism, b = control), common V_G of the 7.1 floor window (rules in the module docstring)"""
    pts = []
    rv = lambda c, k: abs(c['id_A_per_um'][k]) >= res and c['id_A_per_um'][k] != 0 and (demo or c['above_abs_floor'][k] > 0)
    for v in common(ca['vg_V'], cb['vg_V'], True):
        ka, kb = at(ca['vg_V'], v), at(cb['vg_V'], v); a, b = float(ca['id_A_per_um'][ka]), float(cb['id_A_per_um'][kb]); p = {'vg_V': float(v), 'I_run': a, 'I_ctrl': b}
        if not (ca['kcl_pass'][ka] > 0 and cb['kcl_pass'][kb] > 0): p['class'] = 'censored (KCL)'
        elif rv(ca, ka) and rv(cb, kb):
            if a * b > 0 and abs(math.log10(abs(a)) - math.log10(abs(b))) <= MESH_DEC: p.update({'class': 'not resolved: within the 0.1 dec numerical spread', 'ceiling': SPREAD * max(abs(a), abs(b))})
            else: p.update({'class': 'resolved', 'lower': abs(a - b), 'upper': abs(a - b)})
        elif rv(ca, ka) or rv(cb, kb):
            x = abs(a) if rv(ca, ka) else abs(b)
            if math.log10(x / res) > MESH_DEC: p.update({'class': 'resolved (one run only)', 'lower': x - res, 'upper': x + res})
            else: p.update({'class': 'not resolved: one run within 0.1 dec of the resolution', 'ceiling': x + res})
        else: p.update({'class': 'below resolution', 'ceiling': res})
        pts.append(p)
    lo = [p['lower'] for p in pts if 'lower' in p]; up = [p['upper'] for p in pts if 'upper' in p]; cl = [p['ceiling'] for p in pts if 'ceiling' in p]
    cz = [p['vg_V'] for p in pts if p['class'].startswith('censored')]
    if not pts: v = 'unresolved (no common point in the window)'
    elif lo and max(lo) > bound: v = 'FAIL' if demo else 'FAIL (PROVISIONAL: resolution not demonstrated)'
    elif cz: v = f'unresolved (KCL-censored at V_G {cz}: never a pass, not a fail from those points)'
    else:
        parts = ([censored_upper(max(up), bound, res, demo)] if up else []) + ([censored_upper(0.0, bound, max(cl), demo)] if cl else [])
        bad = [s for s in parts if not (s == 'PASS' or s.startswith('below resolution'))]
        v = bad[0] if bad else (parts[0] if len(parts) == 1 else 'PASS (resolved points); ' + parts[1])
    return {'common_points': len(pts), 'resolved_points': len(lo), 'max_abs_dID_lower_A_per_um': max(lo, default=None), 'max_abs_dID_upper_A_per_um': max(up, default=None),
            'max_unresolved_ceiling_A_per_um': max(cl, default=None), 'kcl_censored_vg': cz, 'verdict': v, 'points': pts}


def hc_generation(run, ctrl, given=None, source=None, smoke=False):
    _, ea, ca = load(run); _, eb, cb = load(ctrl); res, src, demo = resolution([ea, eb], given, source)
    lab, _, note = status((ea['label'], eb['label']), 'hc_generation', smoke, (ea['run_id'], eb['run_id']))
    return {'test': 'H-C generation max |dI_D| over V_G in [-2, -0.5] V <= 1e-20 A/um', 'label': lab, 'run': ea['run_id'], 'control': eb['run_id'],
            'bound_A_per_um': GEN_BOUND, 'resolution_A_per_um': res, 'resolution_source': src, **({'label_note': note} if note else {}), **gen_core(ca, cb, res, demo)}


def mesh_core(ca, cb, res, demo):
    """S2-11 rule (module docstring) on two runs' columns: a = refined run, b = reference"""
    pts = []
    for v in common(ca['vg_V'], cb['vg_V']):
        ka, kb = at(ca['vg_V'], v), at(cb['vg_V'], v); a, b = float(ca['ig_raw_A'][ka]), float(cb['ig_raw_A'][kb]); p = {'vg_V': float(v), 'IG_run': a, 'IG_ref': b}
        ra, rb = abs(a) >= res and a != 0, abs(b) >= res and b != 0
        if not (ca['kcl_pass'][ka] > 0 and cb['kcl_pass'][kb] > 0): p['class'] = 'censored (KCL)'
        elif not ra and not rb: continue   # below resolution in both runs: not resolved leakage
        elif ra and rb: p.update({'class': 'resolved', 'dlog10': float(abs(math.log10(abs(a)) - math.log10(abs(b)))) if a * b > 0 else float('inf')})
        else:
            d = math.log10((abs(a) if ra else abs(b)) / res)
            p.update({'class': 'resolved in one run only', 'dlog10_lower_bound': d} if d > MESH_DEC else {'class': 'unresolved: resolved in one run only, within 0.1 dec of the resolution'})
        pts.append(p)
    ch = [p.get('dlog10', p.get('dlog10_lower_bound')) for p in pts if 'dlog10' in p or 'dlog10_lower_bound' in p]
    nres = sum('dlog10' in p for p in pts); unr = [p['vg_V'] for p in pts if p['class'].startswith(('censored', 'unresolved'))]
    if ch and max(ch) > MESH_DEC: v = 'FAIL'
    elif unr: v = f'unresolved (censored or one-sided unresolved points at V_G {unr})'
    elif nres < MESH_MIN_PTS: v = f'unresolved ({nres} points resolved in both runs < {MESH_MIN_PTS})'
    else: v = 'PASS'
    return {'common_points': int(len(common(ca['vg_V'], cb['vg_V']))), 'scored_points': len(pts), 'resolved_both_points': nres,
            'max_change_dec': max(ch, default=None), 'verdict': v if demo or v.startswith('unresolved') else 'PROVISIONAL (resolution not demonstrated): ' + v, 'points': pts}


def hc_mesh(run, ref, given=None, source=None, ig_given=None, ig_source=None, smoke=False):
    _, ea, ca = load(run); _, eb, cb = load(ref)
    if ig_given is not None: res, src, demo = ig_resolution([ea, eb], ig_given, ig_source, (ea['run_id'], eb['run_id']))
    else: res, src, demo = resolution([ea, eb], given, source); src = 'current resolution (I_D-type; not an I_G ceiling; implementation definition): ' + src
    lab, _, note = status((ea['label'], eb['label']), 'hc_mesh', smoke, (ea['run_id'], eb['run_id']))
    return {'test': 'H-C S2-11: resolved |I_G| changes by <= 0.1 dec', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id'],
            'refinement': 'oxide y-mesh x0.5 at the 0.002/0.017 um lines, y = 0 line kept: Al2O3 about x1.5, HfO2 about x2 (QTNLSC only; not ITAT/TAT.SLICEPTS)',
            'resolution_A_per_um': res, 'resolution_source': src, **({'label_note': note} if note else {}), **mesh_core(ca, cb, res, demo)}


def leak_slopes(c, cc, t, res):
    """reported only (not scored): least-squares slopes over the 7.1 window of log10 |I_G| (points >= res, KCL passed) and of log10 dI_D
    (dI_D = I_D - control interpolated, points above the 7.1 KCL limit, as post_run_checks.floor_metrics)"""
    w = window(c['vg_V']); ig = np.abs(c['ig_raw_A']); m = w & (ig >= res) & (ig > 0) & (c['kcl_pass'] > 0)
    d = c['id_A_per_um'] - np.interp(c['vg_V'], cc['vg_V'], cc['id_A_per_um']); md = w & (d > max(1e-17, 0.1 * pc.FLOORS[t]))
    return {'IG_slope_dec_per_V': pc.slope(c['vg_V'][m], np.log10(ig[m]))[0] if m.sum() >= 3 else None, 'IG_points': int(m.sum()),
            'dID_slope_dec_per_V': pc.slope(c['vg_V'][md], np.log10(d[md]))[0] if md.sum() >= 3 else None, 'dID_points': int(md.sum())}


def worst_verdict(flat, thick):
    """register H-C worst case: holds if the leakage FAILS flatness OR thickness scaling; FAIL only if both are evaluated and both hold"""
    f = [n for n, s in (('flatness', flat), ('thickness scaling', thick)) if s.startswith('fails')]
    if f: return 'PASS (worst-case leakage fails ' + ' and '.join(f) + ')'
    if flat.startswith('flat') and thick.startswith('holds'): return 'FAIL (flat within the registered limit and thickness scaling holds)'
    return 'unresolved (neither criterion fails and at least one could not be evaluated)'


def hc_worst(run, ctrl, run2, ctrl2, given=None, source=None, smoke=False):
    """S2-08 (13.2 nm, control S1-02) with S0-02 = run_0067 (2.0 nm, control S0-01) for thickness scaling (module docstring)"""
    (d, exj, c), (dc, ejc, cc), (d2, ej2, c2), (dc2, ejc2, cc2) = load(run), load(ctrl), load(run2), load(ctrl2)
    t, t2 = float(exj['thickness_nm']), float(ej2['thickness_nm']); res, src, _ = resolution([exj, ej2], given, source)
    lab, _, note = status((exj['label'], ejc['label'], ej2['label'], ejc2['label']), 'hc_worst', smoke, (exj['run_id'], ejc['run_id'], ej2['run_id'], ejc2['run_id']))
    fm, fm2 = pc.floor_metrics(d, t, dc), pc.floor_metrics(d2, t2, dc2)
    s, lim = fm.get('floor_slope_dec_per_V'), fm['slope_limit_dec_per_V']
    flat = 'unresolved (fewer than 3 valid floor points)' if s is None else ('fails flatness' if abs(s) > lim else 'flat (within the registered limit)')
    r1, r2 = fm.get('d_floor_ratio_dec'), fm2.get('d_floor_ratio_dec')
    thick = ('unresolved (one film: thickness scaling needs two)' if abs(t - t2) < 1e-6 else
             'unresolved (d_floor_ratio not computable: no window point with dI_D above the 7.1 KCL limit)' if r1 is None or r2 is None else
             'fails thickness scaling' if abs(r1 - r2) > TS_DEC else 'holds (d_floor_ratios within 0.5 dec)')
    return {'test': 'H-C worst-case leakage fails flatness OR thickness scaling', 'label': lab, 'run': exj['run_id'], 'control': ejc['run_id'],
            'run_2p0': ej2['run_id'], 'control_2p0': ejc2['run_id'], **({'label_note': note} if note else {}),
            'flatness': {'quantity': 'slope of log10 total I_D over [-2, -0.5] V (CAMPAIGN_DESIGN 7.1 floor_slope)', 'floor_slope_dec_per_V': s,
                         'slope_limit_dec_per_V': lim, 'valid_fraction': fm['valid_fraction'], 'sub_result': flat},
            'thickness_scaling': {'d_floor_ratio_dec': {t: r1, t2: r2}, 'tolerance_dec': TS_DEC, 'sub_result': thick,
                                  'note': 'S2-07 (6.3 nm worst) is kept out by the register; the two films are S2-08 and S0-02 (run_0067)'},
            'leakage_slopes_reported': {t: leak_slopes(c, cc, t, res), t2: leak_slopes(c2, cc2, t2, res)}, 'resolution_A_per_um': res, 'resolution_source': src,
            'verdict': worst_verdict(flat, thick)}


def explains_verdict(crit, conv, why):
    """register H-C falsification: a CONVERGED mechanism passing all four 7.2 floor criteria falsifies H-C"""
    if not all(crit.values()): return 'does not explain the floor (no falsification from this mechanism)'
    if conv is True: return 'FALSIFIES H-C (converged mechanism passes all four 7.2 floor criteria)'
    return 'unresolved (passes all four 7.2 floor criteria; ' + ('not converged' if conv is False else 'convergence not demonstrated') + f': {why})'


def hc_explains(run, ctrl, mesh_score=None, smoke=False):
    d, exj, c = load(run); dc, ejc, cc = load(ctrl); t = float(exj['thickness_nm'])
    lab, _, note = status((exj['label'], ejc['label']), 'hc_explains', smoke, (exj['run_id'], ejc['run_id']))
    fm = pc.floor_metrics(d, t, dc); vi = fm['verdict_inputs']; w, wc = window(c['vg_V']), window(cc['vg_V'])
    crit = {'valid_ge_80pct': bool(vi['valid_ge_80pct']), 'd_floor_within_0p5dec': bool(vi['d_floor_within_0p5dec']), 'slope_ok': bool(vi['slope_ok']),
            'kcl_pass_window_run_and_control': bool(np.all(c['kcl_pass'][w] > 0) and np.all(cc['kcl_pass'][wc] > 0))}
    if gt_on(exj, 'oxide_tat'):
        conv, why = None, 'ITAT: TAT.SLICEPTS = 12 (default) untested (5.28 PDF p.322: chosen so the currents are largely unchanged for a slightly higher or lower value); needs a logged amendment, e.g. a TAT.SLICEPTS sensitivity launch'
    elif gt_on(exj):
        try: m = json.loads(Path(mesh_score).read_text()) if mesh_score else None
        except Exception: m = None
        ok = m is not None and m.get('label', '').startswith('registered test') and m.get('test', '').startswith('H-C S2-11')
        conv = (True if m['verdict'] == 'PASS' else False if m['verdict'].startswith('FAIL') else None) if ok else None
        why = f'QTNLSC: registered S2-11 hc_mesh {m["run"]} vs {m["ref"]}: {m["verdict"]} (taken for every QTNLSC deck)' if ok else 'QTNLSC: needs the registered S2-11 hc_mesh score (--mesh-score)'
    else:
        conv, why = None, 'generation/SRH: no mechanism-specific refinement run in the diagnostic set (baseline numerics only: S1-03 mesh x0.7, S1-04 DOS x2)'
    out = {'test': 'H-C falsification: converged mechanism passing all CAMPAIGN_DESIGN 7.2 floor criteria', 'label': lab, 'run': exj['run_id'], 'control': ejc['run_id'],
           **({'label_note': note} if note else {}), 'floor_metrics': {k: fm.get(k) for k in ('valid_fraction', 'floor_ratio_dec', 'd_floor_ratio_dec', 'floor_slope_dec_per_V', 'slope_limit_dec_per_V')},
           'criteria': crit, 'converged': conv, 'convergence_evidence': why, 'verdict': explains_verdict(crit, conv, why)}
    if abs(t - 2.0) < 1e-6 and fm.get('d_floor_ratio_dec') is not None and fm['d_floor_ratio_dec'] < -HB_DEC:
        out['note_2p0'] = 'underprediction at 2.0 nm: the floor may be instrument-limited; an underprediction does not falsify a mechanism (CAMPAIGN_DESIGN 7.2)'
    return out


# ---------------------------------------------------------------- self-test (synthetic curves, no run data)
def selftest():
    vg = np.round(np.arange(-3.0, 3.0 + 1e-9, 0.05), 6); res = 1e-17; ok = []
    def curve(v0, slope=4.0, tail=None):   # pure exponential (exact under log-linear interpolation) up to 1e-6 A/um
        i = np.minimum(10.0 ** (-9 + slope * (vg - v0)), 1e-6) if tail is None else tail(vg - v0)
        return i, np.ones_like(i, bool)
    ia, oa = curve(0.5 - 0.2816); ib, ob = curve(0.5); dv = 1e3 * (vth_cc(vg, ia, oa) - vth_cc(vg, ib, ob))
    r = aff_core(vg, ia, oa, vg, ib, ob, res, dv); ok.append(('rigid exponential shift -281.6 mV', abs(dv + 281.6) < 1e-6 and r['rigidity'].startswith('RIGID') and r['qualifying_levels'] >= 3))
    ok.append(('masked V_th,cc = registered extraction.crossing when nothing is censored', abs(vth_cc(vg, ia, oa) - ce.ex.crossing(vg, ia, I_CC, True)['v']) < 1e-12))
    tb = lambda x: 10.0 ** (-9 + 4.0 * x + 0.8 * np.minimum(x, 0) ** 2)   # curvature + a 0.63-dec subthreshold scale at fixed V_G
    ib2 = np.minimum(tb(vg - 0.5), 1e-6); ia2 = np.minimum(tb(vg - 0.5) * np.where(vg < 0.5, 10 ** -0.63, 1.0), 1e-6); o2 = np.ones_like(ia2, bool)
    r2 = aff_core(vg, ia2, o2, vg, ib2, o2, res, 1e3 * (vth_cc(vg, ia2, o2) - vth_cc(vg, ib2, o2)))
    ok.append(('non-rigid scale detected', r2['rigidity'].startswith('NOT RIGID')))
    o3 = oa.copy(); o3[:] = False; o3[-5:] = True
    r3 = aff_core(vg, ia, o3, vg, ib, ob, res, dv); ok.append(('< 3 levels -> unresolved', r3['rigidity'].startswith('unresolved')))
    r4 = aff_core(vg, ia, oa, vg, ib, ob, 1e-12, dv); ok.append(('level floor = 10 x resolution', abs(r4['level_floor_A_per_um'] - 1e-11) < 1e-24))
    ok.append(('levels stop at min(Imax)/1.5', all(x['I_A_per_um'] <= 1e-6 / 1.5 * (1 + 1e-9) for x in r['levels'])))
    iu = 10.0 ** (-9 + 1.0 * (vg - 0.5)); o4 = np.ones_like(iu, bool); o4[-1] = False   # maximum only at +3 V, and censored there
    ok.append(('top level from all positive points (curve maximum, censored or not)', abs(aff_core(vg, iu, o4, vg, iu, o4, res, 0.0)['level_top_A_per_um'] - 10 ** -6.5 / 1.5) < 1e-15))
    o5 = ob.copy(); k5 = int(np.argmin(abs(vg - 0.5))); o5[k5] = False   # one excluded point at the 1e-9 bracket of the baseline
    r5 = aff_core(vg, ia, oa, vg, ib, o5, res, dv); lv5 = {round(math.log10(x['I_A_per_um']), 3): x['dV_mV'] for x in r5['levels']}
    ok.append(('no interpolation across an excluded point', lv5[-9.0] is None and lv5[-10.0] is not None and abs(lv5[-10.0] + 281.6) < 1e-6))
    ok.append(('censored V_th,cc bracket -> None (shift and rigidity unresolved)', vth_cc(vg, ib, o5) is None
               and aff_core(vg, ia, oa, vg, ib, o5, res, None)['rigidity'].startswith('unresolved') and band(None, -281.6, 5).startswith('unresolved')))
    v6 = np.array([-2., -1., 0., 1., 2.]); i6 = np.array([5e-14, 2e-13, 5e-14, 5e-14, 1e-12]); o6 = np.array([True, True, True, True, False])
    ok.append(('censored LAST crossing -> unsupported, no fall-back to an earlier (floor) crossing', v_at(v6, i6, o6, 1e-13) is None and v_at(v6, i6, np.ones(5, bool), 1e-13) > 1.0))
    ok.append(('censoring: below res, res < bound -> consistent', censored_upper(1e-30, 1e-20, 1e-25, True).startswith('below resolution')))
    ok.append(('censoring: below res, res > bound -> unresolved', censored_upper(1e-30, 1e-20, 1e-17, True).startswith('unresolved')))
    ok.append(('censoring: PROXY never passes', censored_upper(1e-19, 1e-18, 1e-20, False).startswith('unresolved')))
    ok.append(('censoring: resolved above bound -> FAIL', censored_upper(1e-12, 4.6e-17, 1e-17, True) == 'FAIL'))
    ok.append(('band edges inclusive', band(-0.272 + 0.010, -0.272, 0.010) == 'PASS' and band(-0.2821, -0.272, 0.010) == 'FAIL'))
    ok.append(('a resolution without a source is not demonstrated', resolution([{}], 1e-18, None)[2] is False and resolution([{}], 1e-18, 'DOS x2 pair')[2] is True))
    ok.append(('I_G ceiling from free text is not demonstrated', ig_resolution([{}], 1e-18, 'DOS x2 I_D pair, run_0071 vs run_0061')[2] is False))
    # S2-11 (mesh_core) on a run_0067-like I_G profile, resolution 3.3e-18
    vm = np.round(np.arange(-3.0, -0.95, 0.2), 6); ig0 = -np.array([2.7e-12, 4.3e-13, 6e-14, 8e-15, 1e-15, 1.4e-16, 2e-17, 1.2e-17, 4.2e-18, 3.4e-19, 1e-19])
    C = lambda ig, kcl=None: {'vg_V': vm, 'ig_raw_A': np.asarray(ig, float), 'kcl_pass': np.ones(len(vm)) if kcl is None else np.asarray(kcl, float)}
    m = lambda ig, kcl=None: mesh_core(C(ig, kcl), C(ig0), 3.3e-18, True)['verdict']
    j = lambda k, x: np.where(np.arange(len(vm)) == k, x, ig0)
    ok.append(('S2-11 identical profile -> PASS', m(ig0) == 'PASS'))
    ok.append(('S2-11 below res -> resolved (-3.44e-19 -> -1e-17, >= 1.5 dec) -> FAIL', m(j(9, -1e-17)) == 'FAIL'))
    ok.append(('S2-11 resolved -> below res (-1e-12 -> -1e-19 at -3 V) -> FAIL', m(j(0, -1e-19)) == 'FAIL'))
    ok.append(('S2-11 one-sided within 0.1 dec of res -> unresolved, not dropped', mesh_core(C(j(8, -1e-19)), C(j(8, -3.5e-18)), 3.3e-18, True)['verdict'].startswith('unresolved')))
    ok.append(('S2-11 sign change at a resolved point -> FAIL', m(j(3, 8e-15)) == 'FAIL'))
    ok.append(('S2-11 KCL-censored point -> unresolved', m(ig0, np.where(np.arange(len(vm)) == 2, 0, 1)).startswith('unresolved')))
    ok.append(('S2-11 fewer than 3 points resolved in both -> unresolved', mesh_core(C(ig0), C(ig0), 1e-13, True)['verdict'].startswith('unresolved')))
    # generation (gen_core) in the [-2, -0.5] V window
    vw = np.round(np.arange(-2.0, -0.45, 0.1), 6); n = len(vw)
    G = lambda i, kcl=None, ab=None: {'vg_V': vw, 'id_A_per_um': np.asarray(i, float), 'kcl_pass': np.ones(n) if kcl is None else np.asarray(kcl, float),
                                      'above_abs_floor': np.zeros(n) if ab is None else np.asarray(ab, float)}
    nz_a = np.where(np.arange(n) % 2, 2.08e-18, -3.29e-18); nz_b = np.where(np.arange(n) % 2, -3.29e-18, 2.08e-18)
    ok.append(('generation: noise pair at the resolution -> not FAIL (unresolved)', gen_core(G(nz_a), G(nz_b), 3.29e-18, True)['verdict'].startswith('unresolved')))
    k1 = np.where(np.arange(n) == 5, 0, 1); i1 = np.where(np.arange(n) == 5, 5e-15, 1e-16)
    ok.append(('generation: KCL-censored point -> unresolved, not FAIL', gen_core(G(i1, k1), G(np.full(n, 1e-16)), 1e-21, True)['verdict'].startswith('unresolved (KCL')))
    ok.append(('generation: one-sided resolved 1e-15 vs 1e-19 -> FAIL', gen_core(G(np.full(n, 1e-15)), G(np.full(n, 1e-19)), 3e-18, True)['verdict'] == 'FAIL'))
    ok.append(('generation: all below res < bound -> consistent', gen_core(G(np.full(n, 1e-23)), G(np.full(n, 2e-23)), 1e-21, True)['verdict'].startswith('below resolution')))
    ok.append(('generation: within the 0.1 dec spread above the bound -> unresolved', gen_core(G(np.full(n, 1.1e-16)), G(np.full(n, 1e-16)), 1e-21, True)['verdict'].startswith('unresolved')))
    ok.append(('worst case: fails one criterion -> PASS; both hold -> FAIL; else unresolved',
               worst_verdict('fails flatness', 'unresolved (x)').startswith('PASS') and worst_verdict('unresolved (x)', 'fails thickness scaling').startswith('PASS')
               and worst_verdict('flat (within)', 'holds (x)').startswith('FAIL') and worst_verdict('flat (within)', 'unresolved (x)').startswith('unresolved')))
    cr = {'a': True, 'b': True}
    ok.append(('H-C falsified only by a converged explaining mechanism', explains_verdict(cr, True, '').startswith('FALSIFIES') and explains_verdict(cr, None, 'x').startswith('unresolved')
               and explains_verdict(cr, False, 'x').startswith('unresolved') and explains_verdict({'a': True, 'b': False}, True, '').startswith('does not explain')))
    ok.append(('labels: pinned run, sensitivity and design pairs',
               status(('c10_s2_11_2p0', 'c10_s0_02_2p0'), 'hc_mesh', False, ('run_0080', 'run_0065'))[0] == SMOKE
               and status(('c10_s2_11_2p0', 'c10_s0_02_2p0'), 'hc_mesh', False, ('run_0080', 'run_0067'))[0].startswith('registered test')
               and prefix(status(('c10_s2_16_13p2', None, 'c10_s2_17_2p0'), 'hb_transfer', False, ('a', None, 'b'))[0]) == 'sensitivity_'
               and prefix(status(('c10_s2_03_2p0', 'c10_s0_01_2p0'), 'hc_generation', False, ('a', 'b'))[0]) == 'design_'
               and prefix(status(('c10_s2_01_13p2', 'c10_s2_02_13p2'), 'hc_generation', False, ('a', 'b'))[0]) == ''
               and ('c10_s2_01_13p2', 'c10_s1_06_13p2') not in REG['hc_generation']))
    for nm, p in ok: print(('ok   ' if p else 'FAIL ') + nm)
    print(f'{sum(p for _, p in ok)}/{len(ok)} ok')
    return 0 if all(p for _, p in ok) else 1


def main(argv):
    if not argv or argv[0] in ('-h', '--help'): print(__doc__); return 2
    if argv[0] == 'selftest': return selftest()
    VAL = ('--resolution', '--resolution-source', '--resolution-ig', '--resolution-ig-source', '--mesh-score')
    opt = {f: argv[argv.index(f) + 1] for f in VAL if f in argv}
    for a, b in (('--resolution', '--resolution-source'), ('--resolution-ig', '--resolution-ig-source')):
        if a in opt and not opt.get(b): print(f'{a} needs {b}: a demonstrated resolution states its source (register section 0)'); return 2
    smoke = '--smoke' in argv
    kw = {'given': float(opt['--resolution']) if '--resolution' in opt else None, 'source': opt.get('--resolution-source')}
    kig = {'ig_given': float(opt['--resolution-ig']) if '--resolution-ig' in opt else None, 'ig_source': opt.get('--resolution-ig-source')}
    pos = [a for i, a in enumerate(argv[1:], 1) if not a.startswith('--') and argv[i - 1] not in VAL]
    cmd = argv[0]
    if cmd == 'aff': r = aff(pos[0], pos[1], smoke=smoke, **kw)
    elif cmd == 'he_alloff': r = he_alloff(pos[0], pos[1], smoke)
    elif cmd == 's3_minus_s105': r = s3_minus_s105(pos[0], pos[1], smoke)
    elif cmd == 'hb_ratio': r = hb_ratio(pos[0], smoke=smoke, **kw)
    elif cmd == 'hb_transfer': r = hb_transfer(*[None if p == 'none' else p for p in pos[:3]], smoke=smoke, **kw)
    elif cmd == 'hc_nominal': r = hc_nominal(pos[0], smoke=smoke, **kig)
    elif cmd == 'hc_generation': r = hc_generation(pos[0], pos[1], smoke=smoke, **kw)
    elif cmd == 'hc_mesh': r = hc_mesh(pos[0], pos[1], smoke=smoke, **kw, **kig)
    elif cmd == 'hc_worst':
        if len(pos) < 4: print('hc_worst S2-08_RUN S1-02_RUN S0-02_RUN(run_0067) S0-01_RUN'); return 2
        r = hc_worst(*pos[:4], smoke=smoke, **kw)
    elif cmd == 'hc_explains': r = hc_explains(pos[0], pos[1], opt.get('--mesh-score'), smoke)
    elif cmd == 'resolution_pair': r = resolution_pair(pos[0], pos[1], *(pos[2:3] or []))
    else: print(__doc__); return 2
    r = {'register_tag': TAG, 'scorer': 'analysis_2026-10-10_campaign/score_register.py', **r}
    OUT.mkdir(exist_ok=True)
    ids = '_'.join(x for x in [r.get(k) for k in ('run', 'ref', 'control', 'run_2p0', 'control_2p0')] if isinstance(x, str)) or '_'.join(str(v) for v in (r.get('runs') or {}).values())
    (OUT / (prefix(r['label']) + f'{cmd}_{ids}.json')).write_text(json.dumps(r, indent=1, default=float))
    print(json.dumps(r, indent=1, default=float)); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
