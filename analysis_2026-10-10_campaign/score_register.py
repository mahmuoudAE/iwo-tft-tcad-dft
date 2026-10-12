#!/usr/bin/env python3
"""Scoring code for the FROZEN hypothesis register, written and frozen BEFORE any S2/S3/AFF result (2026-10-11; review fixes 2026-10-11,
still before any S2/S3/AFF launch; fixes required by Codex's review of 2026-10-12T13:18Z, implemented 2026-10-12 while the S2-11 (DIAGa)
outputs were sealed and unread). NO simulator call; reads finished run directories only and writes analysis_2026-10-10_campaign/register_scores/*.json.

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

Definitions used to apply the rules (implementation choices, stated so they can be reviewed; none changes a registered number). Items
marked [C1]..[C5] implement Codex's review of 2026-10-12T13:18Z (work chat, item 5 of the reply); [C6]..[C8] and [Ruling a/b/c] implement
its re-review of ~15:28Z (GO-WITH-CHANGES); [C9]..[C11] and [Round 3 rulings] its round 3 of ~15:55Z; all done before any S2 output was read:
  * V_th,cc = registered extraction (analysis_2026-10-06_extraction/extraction.crossing at run_extraction.I_CC = 1e-9 A/um: last upward
    crossing over the whole curve, log-linear between adjacent points), via campaign_extract.load_run. A crossing whose bracket holds a
    censored point is unsupported (None -> the shift and rigidity are unresolved); there is no fall-back to an earlier crossing. AFF
    levels use the same rule. AFF top level = min over the two curves of max(I_D > 0) / 1.5 (register: "the curves' maximum current").
  * Point exclusions: non-positive I_D; censored = the runner's kcl_pass = 0 (terminal_currents.csv); below resolution = I_D < res.
    The runner's above_abs_floor (|I_D| > KCL absolute limit) censors only while the resolution is the KCL PROXY; with a demonstrated
    resolution it is a report flag (register 0: KCL is not an uncertainty estimate).
  * Resolution, one per quantity (the register does not define "demonstrated resolution" operationally; the method needs the user's
    sign-off as a logged amendment):
      I_D-type (I_D, dI_D, strip currents, AFF levels, 7.1 floor validity): --resolution R --resolution-source PAIR.json (id_A_per_um).
      I_G ceiling (hc_nominal): --resolution-ig R --resolution-ig-source PAIR.json (ig_raw_A, from two gate-tunnelling runs, neither of
        them under test).
      [C1] Either is demonstrated only by a resolution_pair JSON of this scorer that is re-computed from its two run directories at
        every use (the run-file sha256 and the candidate must match the JSON; paths and sha256 go into the output) and qualifies: two
        DISTINCT runs, both with an accepted runner status, complete and finite, differing only by a VERIFIED numerical intervention
        (execution.json overrides differ only in DOS levels, the mesh spacing factor or the oxide y-mesh factor; device.in statements
        differ only in the matching mesh spacings or numa/numd; same film and material model); candidate and R finite and positive,
        R >= candidate. Free text is never evidence. The CLI refuses anything else (exit 2); a function reports it as not demonstrated.
      [C7] Support and coverage (Codex re-review ~15:28Z fix 7; frozen values, part of the method sign-off): the pair qualifies only with
        >= RES_SUPPORT_MIN = 3 agreeing points whose two currents both exceed the candidate, at least one of them within RES_NEAR_DEC =
        1 decade of it, and bias coverage RES_BIAS_COVERAGE = 1.0 (every bias point of both runs compared). An entirely disagreeing pair
        demonstrates nothing. [C8] The intervention is verified from the ACTUAL deck values (fix 8): one kind of knob; exactly the lines
        it sets change (oxide factor: the y.mesh lines at OXIDE_LINES_UM only, never y = 0; mesh factor: every x/y.mesh line; DOS: every
        defects line), each by the ratio the overrides claim; the refined run is the one with the smaller spacing / more DOS levels.
      [Ruling c] Application scope, frozen: a resolution applies only to its quantity (id_A_per_um or ig_raw_A), its film, its physical
        model/settings (overrides other than the numerical knobs, material model, deck statements with knob values masked) and its compared
        V_G range, for every run it is applied to; no cross-film transfer. A pair containing a tested run is no independent ceiling
        evidence for an upper-bound test (hc_nominal, hc_generation); it may still serve a non-upper-bound use (AFF, hb_*, floor validity).
      hc_mesh uses an I_G ceiling in scope of both runs; the pair under test is never its own resolution (circular); an I_D-type
        resolution is out of scope for the I_G quantity (PROVISIONAL).
      [C9] Numerical-scope guard (Codex round 3 ~15:55Z): every scored run's ACTUAL numerical settings (device.in statements, values
        unmasked) must equal those of one pair endpoint, else a separate qualification is needed; only hc_mesh may instead use a target that
        is a verified, componentwise finer refinement of an endpoint; an unverified or coarser target grid is refused. [C10] 'mixed' DOS
        changes (one grid finer, one coarser) are never a verified refinement. [C11] Per-run (per-curve) resolutions for hc_generation
        (run, control), hc_explains (run, control) and hc_worst (run, control, run_2p0, control_2p0): --resolution-<role> R
        --resolution-<role>-source PAIR.json, each scope-checked on its own run; a set missing a role is refused (exit 2); R_a + R_b kept.
      [Round 3 rulings] The support values are an ASSUMED operational method (the one-decade value was chosen with the already-seen S1
        pairs: prospective for S2, not a blind validation of S1); pair agreement establishes numerical stability under the tested
        intervention, not an absolute error bound. hc_mesh: a DOS comparison and the oxide-mesh comparison may share run_0067; the shared
        baseline is recorded (resolution_pair_relation) and never called independent; the exact pair under test is never its own evidence.
    Without a value: the runner's KCL absolute limit as a PROXY; a proxy never passes an upper bound. [C4] Every verdict computed under
    it (or under any resolution that is not demonstrated) starts with 'PROVISIONAL (...)', through every aggregate: AFF shift and
    rigidity, hb_ratio, hb_transfer, hc_nominal, hc_generation, hc_mesh, hc_worst, hc_explains. The 7.1 floor criteria (hc_worst,
    hc_explains) count a point as valid above the 7.1 KCL limit, which is the proxy: they stay PROVISIONAL unless a demonstrated I_D-type
    resolution at or below that limit is given. he_alloff and s3_minus_s105 use no resolution (1e-9 brackets, KCL mask).
    For AFF the level floor max(1e-13, 10 x res) is independent of res whenever res <= 1e-14 A/um (reported).
  * [C3] Run validity: every run scored must have completed (execution.json status REAL_ATLAS_SCORED / _PREDICTION / _STRIP, or
    KCL_FAILED, whose failed points are censored point by point; return code 0; not timed out; no simulator error; ATLAS completion
    banner), exported every requested point, and hold only finite values without duplicate bias points. The status is read from the
    run files, not from RUN_INDEX. Otherwise every verdict is 'invalid (...)', never a pass. The core rules (gen_core, mesh_core) also
    return 'invalid' for a non-finite required value or a bias point present in one run only. A resolution pair needs accepted statuses.
    [Ruling a] completed KCL_FAILED runs are scored with pointwise censoring; SIGN_REVERSAL runs are invalid.
  * [C6] Floor metrics (hc_worst, hc_explains; re-review fix 6) = floor_metrics_masked: post_run_checks.floor_metrics (unchanged, for its
    other callers) with KCL censoring applied first: a KCL-failed run point is never valid and never enters a slope, ratio or control
    subtraction; the control value is its own KCL-passed point or a linear interpolation between two KCL-passed neighbours, never across a
    censored control point (else unsupported). Below the support minima (slope >= 3 valid points, ratio >= 1 supported point) the metric is
    None and its sub-result unresolved. hc_explains: with censored or unsupported window points the 7.2 criteria are not established ->
    'unresolved (insufficient support ...)', unless the valid fraction fails even with every censored point counted valid.
  * Leakage at -3 V = |I_G(V_G = -3 V)| (ig_raw_A, 1 um mesh width = A/um); KCL-censored at -3 V -> unresolved.
  * Generation (gen_core) = |I_D(run) - I_D(control)| over the CAMPAIGN_DESIGN 7.1 floor window V_G in [-2, -0.5] V at common bias points.
    A difference is resolved only if both currents are resolved and differ by > 0.1 dec (section 1 tolerance) or in sign, or if ONE is
    resolved more than 0.1 dec above res (lower bound |I| - res). Unresolved differences carry a ceiling ([C2] both below resolution:
    R_a + R_b = 2 res, since |I_a - I_b| < R_a + R_b; within the spread: (10^0.1 - 1) max|I|; one run resolved: |I| + res).
    FAIL if a resolved lower bound exceeds the bound; a KCL-censored window point makes the verdict at best unresolved. A one-sided point
    whose lower bound is within the bound but whose upper bound exceeds it is unresolved, never FAIL (code defect fixed in round 3).
  * S2-11 (mesh_core): per common V_G, both below res -> skipped; resolved in both -> |dlog10 |I_G|| (inf on a sign change); resolved in
    ONE run only -> change >= log10(|I_G|/res): > 0.1 dec is a resolved change (FAIL), otherwise an unresolved point (never dropped);
    KCL-censored -> unresolved point. PASS needs >= 3 points resolved in both runs (implementation definition, as the AFF 3-level rule).
    [C5] hc_mesh requires a verified oxide y-mesh refinement of the reference (the run is the refined one), else 'not demonstrated'
    (the comparison is kept as comparison_verdict, never a mesh pass). Its output names the run pair, the sha256 of both runs' files,
    its inputs and its scope: the physical settings of the pair (QTNLSC, 2.0 nm, worst oxide set for S2-11); it certifies nothing else.
  * Worst case (hc_worst): flatness = |floor_slope| of total log10 I_D over the window (7.1) of S2-08 against the 7.2 limit; thickness
    scaling = |d_floor_ratio(S2-08 vs S1-02) - d_floor_ratio(S0-02 = run_0067 vs S0-01)| > 0.5 dec (7.2; S2-07 at 6.3 nm is kept out by
    the register). Registered verdict: PASS if either criterion fails, FAIL only if both are evaluated and both hold, else unresolved.
    The slopes of |I_G| and of dI_D are reported, not scored.
  * hc_explains: the four 7.2 criteria for a mechanism run against its matched control; H-C is falsified only if they all hold AND the
    mechanism is converged: QTNLSC by a registered S2-11 hc_mesh PASS (--mesh-score), [C5] re-scored from its recorded inputs with
    unchanged run-file sha256 and taken only for a mechanism run with exactly the physical settings of the S2-11 reference ([Ruling b]:
    the same oxide parameter set, so the worst-set S2-11 does not certify the nominal S2-04; no other film), ITAT (S2-12/S2-13) never without a logged amendment
    (TAT.SLICEPTS = 12 default untested, 5.28 PDF p.322), generation by no mechanism-specific refinement run (unresolved).
  * Floors = post_run_checks.FLOORS (MEASURED/DERIVED).
  * Labels: 'registered test (tag)' only for the registered entry labels (REG), with labels shared by several launches pinned to their
    registered run (PIN: c10_s0_02_2p0 = run_0067); the no-Q_f H-B branch is 'sensitivity, not a registered prediction'; (S2-03, S0-01)
    is a 'design-defined pair (CAMPAIGN_DESIGN 7.1)', confounded by the carrier count; anything else (or --smoke) is a smoke test.
    Output files carry the prefix smoke_ / sensitivity_ / design_ accordingly (none for registered results).

  python analysis_2026-10-10_campaign/score_register.py aff RUN BASE [--resolution R --resolution-source PAIR.json] [--smoke]
  python analysis_2026-10-10_campaign/score_register.py he_alloff RUN BASE | s3_minus_s105 S3-01_RUN S1-05_RUN
  python analysis_2026-10-10_campaign/score_register.py hb_ratio STRIP_RUN | hb_transfer RUN_13p2 RUN_6p3|none RUN_2p0
  python analysis_2026-10-10_campaign/score_register.py hc_nominal RUN [--resolution-ig R --resolution-ig-source PAIR.json]
  python analysis_2026-10-10_campaign/score_register.py hc_generation RUN CONTROL | hc_mesh S2-11_RUN S0-02_RUN(run_0067)
  python analysis_2026-10-10_campaign/score_register.py hc_worst S2-08_RUN S1-02_RUN S0-02_RUN(run_0067) S0-01_RUN
  python analysis_2026-10-10_campaign/score_register.py hc_explains RUN CONTROL [--mesh-score register_scores/hc_mesh_*.json] [--resolution ...]
  python analysis_2026-10-10_campaign/score_register.py resolution_pair RUN_REFINED RUN_REF [column]   (PROPOSED resolution, not registered)
  python analysis_2026-10-10_campaign/score_register.py selftest          (synthetic curves and synthetic run directories only; no run data)
  The I_D-type options (--resolution R --resolution-source PAIR.json) apply to aff, hb_*, hc_generation, hc_mesh, hc_worst, hc_explains;
  per-run instead: hc_generation / hc_explains --resolution-run R --resolution-run-source PAIR.json --resolution-control R --resolution-control-source
  PAIR.json; hc_worst also --resolution-run-2p0 ... --resolution-control-2p0 ... (every role required).
"""
import contextlib
import csv
import difflib
import hashlib
import io
import json
import math
import re
import shutil
import sys
import tempfile
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
# ---- Codex review 2026-10-12T13:18Z (implementation; no registered number or rule text changed)
PROV_WHY = 'resolution not demonstrated'
PAIR_TEST = 'resolution proposal from a refinement pair (NOT registered)'
ACCEPTED = ('REAL_ATLAS_SCORED', 'REAL_ATLAS_PREDICTION', 'REAL_ATLAS_STRIP')   # runner statuses of a completed run that passed acceptance
SCORABLE = ACCEPTED + ('KCL_FAILED',)   # completed; KCL-failed points are censored point by point (register 0, KCL-censoring rules below)
EVID = ('execution.json', 'device.in', 'material_model_used.json', 'terminal_currents.csv', 'strip_iv.csv')   # run files bound by sha256
GT = 'solver.physics_options.gate_tunnelling.'
KNOBS = {'solver.dos_levels.numa': 'DOS grid', 'solver.dos_levels.numd': 'DOS grid', 'geometry.mesh.spacing_factor': 'mesh spacing factor',
         GT + 'oxide_mesh_factor': 'oxide y-mesh factor'}   # numerical-only overrides (S1-04, S1-03, S2-11): no physics change
KNOB_LINES = {'DOS grid': ('defects',), 'mesh spacing factor': ('x.mesh', 'y.mesh'), 'oxide y-mesh factor': ('y.mesh',)}   # deck statements each may change
KNOB_DEFAULT = {'geometry.mesh.spacing_factor': 1.0, GT + 'oxide_mesh_factor': 1.0}   # generator defaults when the override is absent
# ---- Codex re-review 2026-10-12 ~15:28Z (fixes 6-8, rulings a-c); the values below are part of the resolution-method sign-off
OXIDE_LINES_UM = (0.002, 0.017)   # y.mesh lines the oxide factor scales: y = t_Al2O3 and t_Al2O3 + t_HfO2 (build_iwo_decks.py:311-312); y = 0 is not one
RES_SUPPORT_MIN = 3               # agreeing points with both currents above the candidate R (fix 7)
RES_NEAR_DEC = 1.0                # at least one of them within this many decades above R (no evidence gap at the claimed ceiling)
RES_BIAS_COVERAGE = 1.0           # fraction of each run's bias points compared in the pair (full sweeps only; no partial pairs)
RATIO_RTOL = 1e-3                 # deck value ratio vs the claimed knob ratio (deck numbers are printed with 6 significant digits)
_MESH_RE = re.compile(r'^([xy])\.mesh\s+loc=(\S+)\s+spac=(\S+)\s*$', re.I)
_NUM_RE = re.compile(r'\bnum([ad])=(\S+)', re.I)


class Refused(Exception):
    """a resolution given on the command line that is not demonstrated: the CLI refuses it (exit 2; Codex 2026-10-12 item 1)"""


# ---------------------------------------------------------------- data
def _num(x):
    try: return float(x)
    except (TypeError, ValueError): return float('nan')


def read_cols(p):
    """numeric columns of a run CSV (an unparsable entry becomes NaN, so it is caught as non-finite); None if missing or without rows"""
    if not p.is_file(): return None
    with open(p, newline='') as f: rows = list(csv.DictReader(f))
    if not rows: return None
    return {k: np.array([_num(r.get(k)) for r in rows]) for k in rows[0] if k is not None}


def load(run):
    """(dir, execution.json, columns of terminal_currents.csv sorted by V_G, or None without an export) of a transfer run. Whether the
    run may be scored at all is decided by run_problems (Codex 2026-10-12 item 3), not by the presence of a CSV."""
    d = ce.resolve(run); exj = json.loads((d / 'execution.json').read_text()); c = read_cols(d / 'terminal_currents.csv')
    if c is not None and 'vg_V' in c: o = np.argsort(c['vg_V'], kind='stable'); c = {k: v[o] for k, v in c.items()}
    vg = c['vg_V'][np.isfinite(c['vg_V'])] if c is not None and 'vg_V' in c else np.array([])
    exj['__scope__'] = {'dir': str(d), 'bias_V': [float(vg.min()), float(vg.max())] if vg.size else None}   # for the application-scope check (ruling c)
    return d, exj, c


def run_problems(exj, c, statuses=SCORABLE):
    """why a run cannot be scored ([] = completed with a complete, finite export; Codex 2026-10-12 item 3): runner status, return code,
    timeout, simulator errors, ATLAS completion banner, every requested point exported, finite values, no duplicate bias point.
    Read from the run's own files (execution.json + CSV), not from RUN_INDEX."""
    p = []; sc = exj.get('scan') or {}
    if exj.get('status') not in statuses: p.append(f'runner status {exj.get("status")}')
    if exj.get('returncode') != 0: p.append(f'return code {exj.get("returncode")}')
    if exj.get('timed_out') is not False: p.append('timed out' if exj.get('timed_out') else 'no timeout flag')
    if sc.get('errors'): p.append('simulator error')
    if sc.get('finished') is not True: p.append('no ATLAS completion banner')
    if not c: return p + ['no exported currents']
    n = exj.get('requested_points', (exj.get('validation') or {}).get('requested_points')); m = len(next(iter(c.values())))
    if n is None or m != int(n): p.append(f'{m} exported of {n} requested points')
    nf = [k for k, v in c.items() if not np.all(np.isfinite(v))]
    if nf: p.append('non-finite values in ' + ', '.join(nf))
    x = c.get('vg_V', c.get('vd_V'))
    if x is not None and np.all(np.isfinite(x)) and len(np.unique(np.round(x, 6))) != len(x): p.append('duplicate bias points')
    return p


def usable(*runs):
    """None if every (execution.json, columns) is a scorable run, else the verdict 'invalid (...)', which is never a pass"""
    p = [f'{e.get("run_id")}: ' + '; '.join(q) for e, c in runs if (q := run_problems(e, c))]
    return ('invalid (not a completed run with a complete, finite export: ' + ' | '.join(p) + '); never a pass') if p else None


def bad_points(ca, cb, cols, win=False):
    """core-rule check (item 3): 'invalid (...)' if a V_G is non-finite, a bias point (in the 7.1 window if win) exists in one run only,
    or a required value at a scored point is non-finite; None otherwise"""
    m = [f'non-finite V_G in {n}' for n, c in (('run', ca), ('ref', cb)) if not np.all(np.isfinite(np.asarray(c['vg_V'], float)))]
    if not m:
        va, vb = (np.round(np.asarray(c['vg_V'], float), 6) for c in (ca, cb))
        if win: va, vb = va[window(va)], vb[window(vb)]
        miss = sorted(set(va.tolist()) ^ set(vb.tolist()))
        if miss: m.append(f'bias points in one run only: V_G {miss[:6]}')
        for n, c in (('run', ca), ('ref', cb)):
            vg = np.asarray(c['vg_V'], float); s = window(vg) if win else np.ones(len(vg), bool)
            for k in cols:
                x = np.asarray(c[k], float)[s]
                if not np.all(np.isfinite(x)): m.append(f'non-finite {k} in {n} at V_G {vg[s][~np.isfinite(x)].tolist()[:6]}')
    return ('invalid (' + '; '.join(m) + '); never a pass') if m else None


def sha256_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(d):
    d = Path(d); return str(d.relative_to(ce.ct.PKG)).replace('\\', '/') if d.is_relative_to(ce.ct.PKG) else str(d)


def evidence(d, exj):
    """file-bound evidence of one run (item 1/5): its directory and the sha256 of its run files"""
    return {'run_id': exj.get('run_id'), 'dir': rel(d), 'sha256': {f: sha256_file(Path(d) / f) for f in EVID if (Path(d) / f).is_file()}}


def src_path(s):
    """a cited JSON: absolute, else relative to the working directory if it exists there, else to the package root"""
    p = Path(str(s))
    if p.is_absolute(): return p
    q = Path.cwd() / p
    return q.resolve() if q.is_file() else ce.ct.PKG / p


def ovr(exj):
    """execution.json overrides as {key: value}; the last one wins, as in the runner (set_dotted applied in order)"""
    return {o.split('=', 1)[0].strip(): o.split('=', 1)[1].strip() for o in exj.get('overrides', []) if '=' in o}


def resolution(exjs, given, source, strict=False, independent=False, quantity='id_A_per_um', under_test=None):
    """I_D-type resolution (I_D, dI_D, strip currents, AFF levels, 7.1 floor validity): (value A/um, statement, demonstrated?, evidence).
    Demonstrated only by a qualifying resolution_pair JSON on id_A_per_um (qualify; Codex 2026-10-12 item 1) whose application scope
    covers every scored run in exjs (ruling c), including their actual numerical settings (round 3: equal to a pair endpoint);
    independent (upper-bound tests): the pair may not contain a tested run (under_test, default the runs in exjs). None given ->
    PROXY max(runner KCL absolute limit) of the runs (not demonstrated). strict (the CLI): a given value that does not qualify is refused."""
    px = max(float(e.get('validation', {}).get('kcl_abs_limit_applied_A', 1e-17)) for e in exjs)
    if given is None: return px, 'PROXY: runner KCL absolute limit (register 0: KCL is a sanity check, not a demonstrated resolution)', False, None
    ut = (set(under_test) if under_test is not None else {e.get('run_id') for e in exjs}) if independent else ()
    ok, why, ev = qualify(given, source, 'id_A_per_um', under_test=ut, runs=exjs, quantity=quantity)
    if ok: return float(given), why, True, ev
    if strict: raise Refused(f'--resolution {given} --resolution-source {source}: not a demonstrated resolution ({why})')
    g = _num(given); v = g if math.isfinite(g) and g > 0 else px
    return v, f'{source or "no source"}: NOT a demonstrated resolution ({why}); PROVISIONAL' + ('' if v == g else ' (PROXY value used)'), False, ev


def gt_on(exj, opt='gate_tunnelling'):
    """the run's overrides switch physics_options.<opt>.enabled on"""
    return any(o.split('=', 1)[0].strip() == f'solver.physics_options.{opt}.enabled' and ce.ct.bd.on(o.split('=', 1)[1]) for o in exj.get('overrides', []) if '=' in o)


def mechanism(exj):
    """gate-leakage mechanism of a run from its overrides: ITAT, the gate-tunnelling model (QTNLSC), or none"""
    if gt_on(exj, 'oxide_tat'): return 'ITAT'
    return str(ovr(exj).get(GT + 'model', 'unknown')).upper() if gt_on(exj) else 'none'


def ig_resolution(exjs, given, source, under_test=(), strict=False, forbid_pair=None, refine_ok=False):
    """I_G ceiling for H-C leakage (register H-C: 'only if a numerical ceiling below that bound is demonstrated'): demonstrated only by a
    qualifying resolution_pair JSON (qualify) on column ig_raw_A whose two runs both have gate tunnelling on, whose application scope
    covers the scored runs (ruling c; round 3: their actual numerical settings equal a pair endpoint, or for hc_mesh (refine_ok) are a
    verified finer refinement of one), that contains no run in under_test (upper-bound tests) and is not forbid_pair itself (hc_mesh:
    the pair under test cannot be its own resolution), with the value >= the pair's candidate. Otherwise PROVISIONAL (refused under
    strict); no value -> the KCL PROXY."""
    if given is None: return resolution(exjs, None, None)
    ok, why, ev = qualify(given, source, 'ig_raw_A', under_test, need_gt=True, runs=exjs, quantity='ig_raw_A', forbid_pair=forbid_pair, refine_ok=refine_ok)
    if ok: return float(given), why, True, ev
    if strict: raise Refused(f'--resolution-ig {given} --resolution-ig-source {source}: not a demonstrated I_G ceiling ({why})')
    px = resolution(exjs, None, None)[0]; g = _num(given); v = g if math.isfinite(g) and g > 0 else px
    return v, f'{source or "no source"}: NOT a demonstrated I_G ceiling ({why}); PROVISIONAL' + ('' if v == g else ' (PROXY value used)'), False, ev


def role_res(roles, given, source, per_run, strict, **kw):
    """per-run (per-curve) resolutions (Codex round 3, fix 11): {role: (value, statement, demonstrated?, evidence)} for roles = ((role,
    execution.json), ...). Each run takes its own input from per_run {role: (R, PAIR.json)}, else the single given/source; every run is
    scope-checked on its own (quantity, film, settings, bias range, numerical endpoint). Under strict (the CLI) a per-run input set that
    misses a role is refused: one source cannot match a gated mechanism and an ungated control, two generation settings or two films."""
    if per_run:
        miss = [r for r, _ in roles if r not in per_run]
        if miss and strict: raise Refused(f'per-run resolution input missing for {miss}: every run needs its own input (Codex round 3)')
    out = {}
    for r, e in roles:
        try: out[r] = resolution([e], *(per_run or {}).get(r, (given, source)), strict, **kw)
        except Refused as x: raise Refused(f'[{r} = {e.get("run_id")}' + (', per-run input' if per_run and r in per_run else '') + f'] {x}')
    return out


def numerics(d):
    """actual numerical settings of a run: sha256 of its device.in statements with every value (mesh spacings, numa/numd) unmasked"""
    st = _deck_statements(d); return hashlib.sha256('\n'.join(st).encode()).hexdigest() if st else None


def qualify(given, source, col, under_test=(), need_gt=False, runs=None, quantity=None, forbid_pair=None, refine_ok=False):
    """(demonstrated?, statement, evidence) for a resolution R cited with SOURCE (Codex 2026-10-12 item 1). SOURCE must be a
    resolution_pair JSON of this scorer on column col; the pair is re-computed now from its run directories and must carry the same
    run-file sha256 and candidate as the JSON, and qualify (distinct accepted complete finite runs, verified numerical intervention,
    agreement support and bias coverage, finite positive candidate). R finite, positive and >= the candidate; for an I_G ceiling both
    runs gate-tunnelling. Application scope (Codex ruling c, frozen): the scored quantity is the pair's column; every scored run (runs,
    as returned by load) has the pair's film and physical model/settings (settings) and lies inside its compared bias range; a pair
    containing a run in under_test is not independent ceiling evidence; forbid_pair (the pair under test) is circular. Numerical-scope
    guard (Codex round 3, fix 9): every scored run's ACTUAL numerical settings (numerics: unmasked deck) must equal those of one pair
    endpoint; only with refine_ok (hc_mesh) may a run instead be a verified, componentwise finer refinement of an endpoint (intervention);
    an unverified or coarser target grid is refused. A demonstrated value states numerical stability under the tested intervention, not an
    absolute error bound (ASSUMED operational method, Codex round 3 ruling)."""
    ev = {'source': None if source is None else str(source)}; g = _num(given)
    if not (math.isfinite(g) and g > 0): return False, f'value {given} is not finite and positive', ev
    if not source: return False, 'given WITHOUT a source', ev
    p = src_path(source)
    try: raw = p.read_bytes(); j = json.loads(raw)
    except Exception: return False, 'the source is not a readable resolution_pair JSON of this scorer (free text is not evidence)', ev
    ev.update(pair_json=rel(p), pair_json_sha256=hashlib.sha256(raw).hexdigest())
    if not isinstance(j, dict) or j.get('test') != PAIR_TEST or 'run_dir' not in j or 'ref_dir' not in j: return False, 'the source is not a resolution_pair JSON of this scorer', ev
    if j.get('column') != col: return False, f'pair column {j.get("column")}, not {col}', ev
    if quantity and quantity != col: return False, f'out of the application scope: a {col} resolution does not apply to the scored quantity {quantity} (ruling c)', ev
    try: f = resolution_pair(j['run_dir'], j['ref_dir'], col)
    except Exception as e: return False, f'the pair run directories are not readable ({type(e).__name__})', ev
    ev.update(pair_evidence=f['evidence'], pair_intervention=f['intervention'].get('kind'), pair_films_nm=f['thickness_nm'], application_scope=f['application_scope'])
    if j.get('evidence') != f['evidence']: return False, 'no file evidence in the JSON, or the run files changed since it was written (sha256 mismatch)', ev
    if not f['qualified']: return False, f'the pair does not qualify ({f["qualification"]})', ev
    c = f['candidate_resolution_A_per_um']; jc = _num(j.get('candidate_resolution_A_per_um'))
    if not (math.isfinite(jc) and abs(jc - c) <= 1e-9 * c): return False, 'the JSON candidate differs from the re-computed candidate', ev
    if need_gt and not (f['run_gate_tunnelling'] and f['ref_gate_tunnelling']): return False, 'the pair is not two gate-tunnelling runs', ev
    circ = {f['run'], f['ref']} & set(under_test)
    if circ: return False, f'not independent: the pair contains a run under test ({", ".join(sorted(circ))}); it may show that run\'s refinement stability but is no ceiling evidence for the same upper-bound test (ruling c)', ev
    if forbid_pair and {f['run'], f['ref']} == set(forbid_pair): return False, 'circular: the resolution pair is the pair under test', ev
    if runs is None: return False, 'the application scope of the scored runs was not checked', ev
    sc = f['application_scope']; rng = sc['bias_range_V']; routes = []
    for e in runs:
        s = e.get('__scope__') if isinstance(e, dict) else None
        if not s: return False, f'application scope of {e.get("run_id") if isinstance(e, dict) else e} not verifiable (run not loaded from its directory)', ev
        st = settings(Path(s['dir']), e)
        if st != sc['settings']: return False, f'{e.get("run_id")} is outside the application scope ({settings_diff(st, sc["settings"])}; ruling c: same quantity, film and physical model/settings, no cross-film transfer)', ev
        b = s.get('bias_V')
        if b is None or rng is None or b[0] < rng[0] - 1e-6 or b[1] > rng[1] + 1e-6: return False, f'{e.get("run_id")}: bias range {b} outside the supported bias range {rng} of the pair', ev
        num = numerics(Path(s['dir'])); hit = [x for x in sc['endpoints'] if num and x['numerics_sha256'] == num]
        if hit: routes.append(f'{e.get("run_id")}: numerical settings of endpoint {hit[0]["run_id"]}'); continue
        if not refine_ok:
            return False, (f'{e.get("run_id")}: its actual numerical settings (deck values) equal neither pair endpoint; a separate qualification is needed '
                           '(Codex round 3 numerical-scope guard)'), ev
        r = None
        for x in sc['endpoints']:
            dx, ex_, _ = load(x['dir']); iv = intervention(Path(s['dir']), e, dx, ex_)
            if iv['verified'] and iv.get('refined') == 'run': r = f'{e.get("run_id")}: verified {iv["kind"]} refinement (finer, deck ratio {iv["deck_ratio"]}) of endpoint {x["run_id"]}'; break
        if not r: return False, f'{e.get("run_id")}: numerical settings are neither a pair endpoint nor a verified finer refinement of one (unverified or coarser target grid; Codex round 3)', ev
        routes.append(r)
    ev['numerical_routes'] = routes
    if g < c * (1 - 1e-9): return False, f'value {g:.3g} below the pair candidate {c:.3g}', ev
    return True, (f'{rel(p)}: {col} refinement pair {f["run"]} vs {f["ref"]} ({f["intervention"]["kind"]}, film {f["thickness_nm"][0]} nm, '
                  f'{f["support_points_above_candidate"]} agreeing points above the candidate), candidate {c:.4g} A/um, scope = this quantity, film, '
                  f'physical settings, V_G {rng} and numerical settings ({"; ".join(routes)}); numerical stability under the tested intervention, '
                  'not an absolute error bound (ASSUMED operational method; file-bound)'), ev


def prov(v, ok, why=PROV_WHY):
    """Codex 2026-10-12 item 4: a verdict computed under the KCL PROXY (or any resolution that is not demonstrated) starts with
    'PROVISIONAL (...)', whatever it is; 'invalid' and 'not demonstrated' verdicts are final and stay as they are"""
    if ok or v.startswith(('invalid', 'not demonstrated')): return v
    v = v.replace(' (PROVISIONAL: resolution not demonstrated)', '')
    return v if v.startswith('PROVISIONAL') else f'PROVISIONAL ({why}): {v}'


def lim71(t): return max(1e-17, 0.1 * pc.FLOORS[t])   # CAMPAIGN_DESIGN 7.1 floor validity limit (post_run_checks.floor_metrics) = the KCL PROXY


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


def _deck_statements(d):
    p = Path(d) / 'device.in'
    if not p.is_file(): return None
    return [l.strip() for l in p.read_text(errors='replace').splitlines() if l.strip() and not l.lstrip().startswith('#')]


def _knob(k, v):
    x = _num(KNOB_DEFAULT.get(k) if v is None else v); return x if math.isfinite(x) and x > 0 else None


def _mask(s):
    """a deck statement with the values the numerical knobs set (mesh spacings, numa/numd) masked"""
    return re.sub(r'\bnum[ad]=\S+', 'num=*', re.sub(r'\bspac=\S+', 'spac=*', s.lower()))


def settings(d, exj):
    """physical model/settings of a run (Codex ruling c): film, mode, the execution.json overrides other than the numerical knobs,
    the material model, and the device.in statements with the knob-set values masked (sha256)"""
    st = _deck_statements(d); mm = Path(d) / 'material_model_used.json'
    return {'film_nm': _num(exj.get('thickness_nm')), 'mode': exj.get('mode', 'transfer'),
            'overrides': sorted(f'{k}={v}' for k, v in ovr(exj).items() if k not in KNOBS),
            'material_model_sha256': sha256_file(mm) if mm.is_file() else None,
            'deck_statements_sha256': hashlib.sha256('\n'.join(_mask(s) for s in st).encode()).hexdigest() if st else None}


def settings_diff(a, b):
    out = [f'{k} {a.get(k)} vs {b.get(k)}' for k in ('film_nm', 'mode') if a.get(k) != b.get(k)]
    oa, ob = set(a.get('overrides') or []), set(b.get('overrides') or [])
    if oa != ob: out.append('overrides [' + '; '.join(sorted(oa - ob)) + '] vs [' + '; '.join(sorted(ob - oa)) + ']')
    out += [k.replace('_sha256', '') + ' differs' for k in ('material_model_sha256', 'deck_statements_sha256') if a.get(k) != b.get(k)]
    return ', '.join(out) or 'identical'


def _close(x, y): return math.isfinite(x) and math.isfinite(y) and abs(x - y) <= RATIO_RTOL * abs(y)


def intervention(da, ea, db, eb):
    """verified numerical intervention between two runs (Codex 2026-10-12 item 1; re-review fix 8: from the ACTUAL deck values), checked
    from the run directories: distinct runs of the same film whose execution.json overrides differ only in ONE kind of numerical knob
    (KNOBS: DOS levels, mesh spacing factor, oxide y-mesh factor) with finite positive values, whose material models are identical and
    whose device.in statements (same count and order) differ exactly in the lines that knob sets, each by the claimed ratio:
      oxide y-mesh factor: exactly the y.mesh lines at OXIDE_LINES_UM (nothing else, not the y = 0 line), spac(run)/spac(ref) = f(run)/f(ref);
      mesh spacing factor: every x.mesh and y.mesh line, spac ratio = g(run)/g(ref);
      DOS grid: every defects statement with numa/numd, each ratio = the claimed numa/numd ratio, nothing else on the line.
    'refined' (the finer run) follows from the deck values: smaller spacing or more DOS levels."""
    oa, ob = ovr(ea), ovr(eb); ch = sorted(k for k in set(oa) | set(ob) if oa.get(k) != ob.get(k))
    out = {'verified': False, 'changed_overrides': {k: [oa.get(k), ob.get(k)] for k in ch}}
    def no(why): out['why'] = why; return out
    if ea.get('run_id') == eb.get('run_id') or Path(da).resolve() == Path(db).resolve(): return no('self-pair: the two runs are the same run')
    if not abs(_num(ea.get('thickness_nm')) - _num(eb.get('thickness_nm'))) <= 1e-6: return no('different films')
    if not ch: return no('no override differs: no numerical intervention')
    other = [k for k in ch if k not in KNOBS]
    if other: return no('non-numerical overrides differ: ' + ', '.join(other))
    kinds = sorted({KNOBS[k] for k in ch})
    if len(kinds) != 1: return no('more than one kind of numerical change: ' + ', '.join(kinds))
    kind = kinds[0]
    if kind == 'DOS grid':
        rho = {}
        for p in ('a', 'd'):
            k = f'solver.dos_levels.num{p}'; x, y = _knob(k, oa.get(k)), _knob(k, ob.get(k))
            if x is None or y is None: return no(f'DOS override {k} missing or not finite and positive in a run')
            rho[p] = x / y
    else:
        k = ch[0]; x, y = _knob(k, oa.get(k)), _knob(k, ob.get(k))
        if x is None or y is None or x == y: return no(f'{k}: missing, not finite and positive, or unchanged')
        rho = x / y
    sa, sb = _deck_statements(da), _deck_statements(db)
    if sa is None or sb is None: return no('device.in missing')
    if len(sa) != len(sb): return no(f'device.in statement counts differ ({len(sa)} vs {len(sb)}): statements added or removed')
    ratios = []; seen = set()
    for x, y in zip(sa, sb):
        if x == y:
            mx = _MESH_RE.match(x)
            if kind == 'mesh spacing factor' and mx: return no(f'mesh statement unchanged under the mesh spacing factor: {x!r}')
            if kind == 'DOS grid' and x.lower().startswith('defects') and _NUM_RE.search(x) and any(abs(r - 1) > RATIO_RTOL for r in rho.values()):
                return no(f'defects statement unchanged under the DOS change: {x!r}')
            continue
        if _mask(x) != _mask(y): return no(f'device.in statement outside the {kind} change: {x!r} vs {y!r}')
        mx, my = _MESH_RE.match(x), _MESH_RE.match(y)
        if kind in ('mesh spacing factor', 'oxide y-mesh factor'):
            if not (mx and my) or mx.group(1).lower() != my.group(1).lower() or _num(mx.group(2)) != _num(my.group(2)):
                return no(f'changed statement is not the same mesh line: {x!r} vs {y!r}')
            if kind == 'oxide y-mesh factor':
                loc = _num(mx.group(2))
                if mx.group(1).lower() != 'y' or not any(abs(loc - L) <= 1e-9 for L in OXIDE_LINES_UM):
                    return no(f'changed mesh line {x!r} is not one of the oxide lines y = {OXIDE_LINES_UM} um (the claimed intervention)')
                seen.add(round(loc, 9))
            r = _num(mx.group(3)) / _num(my.group(3))
            if not _close(r, rho): return no(f'deck spacing ratio {r:.4g} at {x!r} differs from the claimed {rho:.4g} (overrides)')
            ratios.append(r)
        else:
            if not x.lower().startswith('defects'): return no(f'changed statement is not a defects (DOS) line: {x!r}')
            va, vb = dict((m.group(1).lower(), _num(m.group(2))) for m in _NUM_RE.finditer(x)), dict((m.group(1).lower(), _num(m.group(2))) for m in _NUM_RE.finditer(y))
            for p in ('a', 'd'):
                if p in va or p in vb:
                    r = va.get(p, float('nan')) / vb.get(p, float('nan'))
                    if not _close(r, rho[p]): return no(f'deck num{p} ratio {r:.4g} at {x!r} differs from the claimed {rho[p]:.4g} (overrides)')
            ratios.append(rho['a'])
    if not ratios: return no('identical device.in statements: the intervention did not reach the deck')
    if kind == 'oxide y-mesh factor' and seen != {round(L, 9) for L in OXIDE_LINES_UM}: return no(f'not every oxide line {OXIDE_LINES_UM} um changed')
    ma, mb = Path(da) / 'material_model_used.json', Path(db) / 'material_model_used.json'
    if not (ma.is_file() and mb.is_file()) or sha256_file(ma) != sha256_file(mb): return no('material models differ or are missing')
    if kind == 'DOS grid': fin = 'run' if all(r >= 1 for r in rho.values()) else 'ref' if all(r <= 1 for r in rho.values()) else 'mixed'
    else: fin = 'run' if rho < 1 else 'ref'
    if fin == 'mixed':   # Codex round 3, fix 10: componentwise refinement; one grid finer and another coarser is no refinement evidence
        return no(f'not a componentwise refinement: DOS ratios numa {rho["a"]:.4g}, numd {rho["d"]:.4g} (one finer, one coarser)')
    out.update(verified=True, kind=kind, deck_statements_changed=len(ratios), deck_ratio=(rho if kind == 'DOS grid' else float(np.median(ratios))), refined=fin)
    return out


def resolution_pair(a, b, col='id_A_per_um', tol=MESH_DEC):
    """PROPOSAL, not a registered definition: candidate demonstrated resolution from a numerical-refinement pair (register section 1
    'Convergence': resolved currents within 0.1 dec under refinement). R = the largest max(|I_a|, |I_b|) over common V_G points that
    disagree by > tol dec, change sign or are zero; every point with both currents above R agrees within tol. With no disagreeing point,
    R = the smallest common same-sign current (lowest current at which agreement was shown). Cite it with --resolution-source; an I_G
    ceiling (--resolution-ig-source) needs this JSON on ig_raw_A from two gate-tunnelling runs. The JSON is the only accepted evidence
    (Codex 2026-10-12 item 1): it records both run directories with the sha256 of their files, the verified numerical intervention and
    whether the pair qualifies (distinct runs, accepted complete finite exports, verified intervention, finite positive candidate).
    Re-review fix 7 (frozen values, part of the method sign-off): the pair qualifies only with agreement SUPPORT above R (at least
    RES_SUPPORT_MIN agreeing points with both currents > R, one of them within RES_NEAR_DEC decade of R) and full BIAS COVERAGE (every
    bias point of both runs compared); an entirely disagreeing pair demonstrates nothing. Ruling c: the JSON states its application
    scope (quantity, film, physical settings, compared V_G range)."""
    da, ea, ca = load(a); db, eb, cb = load(b); bad, good = [], []
    have = bool(ca) and bool(cb) and col in ca and col in cb and 'vg_V' in ca and 'vg_V' in cb
    com = common(ca['vg_V'], cb['vg_V']) if have else np.array([])
    for v in com:
        x, y = float(ca[col][at(ca['vg_V'], v)]), float(cb[col][at(cb['vg_V'], v)])
        if not (math.isfinite(x) and math.isfinite(y)): continue   # a non-finite run never qualifies (run_problems)
        if x * y > 0 and abs(math.log10(abs(x)) - math.log10(abs(y))) <= tol: good.append(min(abs(x), abs(y)))
        else: bad.append(max(abs(x), abs(y)))
    R = max(bad) if bad else (min(good) if good else None)
    sup = [x for x in good if R is not None and x > R]; near = [x for x in sup if x <= R * 10 ** RES_NEAR_DEC]
    cov = (len(com) / max(len(ca['vg_V']), len(cb['vg_V']))) if have else 0.0
    iv = intervention(da, ea, db, eb)
    why = [f'{k} {e.get("run_id")}: ' + '; '.join(q) for k, e, c in (('run', ea, ca), ('ref', eb, cb)) if (q := run_problems(e, c, ACCEPTED))]
    if not have: why.append(f'column {col} missing')
    if not iv['verified']: why.append(f'no verified numerical intervention ({iv["why"]})')
    if not (R is not None and math.isfinite(R) and R > 0): why.append(f'candidate {R} is not finite and positive')
    if cov < RES_BIAS_COVERAGE - 1e-12: why.append(f'bias coverage {cov:.2f} < {RES_BIAS_COVERAGE:g} (every bias point of both runs must be compared)')
    if len(sup) < RES_SUPPORT_MIN: why.append(f'agreement support above the candidate: {len(sup)} points < {RES_SUPPORT_MIN} (an entirely or mostly disagreeing pair demonstrates nothing)')
    elif not near: why.append(f'no agreeing point within {RES_NEAR_DEC:g} decade above the candidate (nearest at {min(sup) / R:.3g} x R): the ceiling itself is not supported')
    rng = [float(com.min()), float(com.max())] if len(com) else None
    return {'test': PAIR_TEST, 'label': SMOKE, 'run': ea['run_id'], 'ref': eb['run_id'], 'column': col,
            'run_dir': rel(da), 'ref_dir': rel(db), 'thickness_nm': [ea.get('thickness_nm'), eb.get('thickness_nm')],
            'run_gate_tunnelling': gt_on(ea), 'ref_gate_tunnelling': gt_on(eb),
            'tolerance_dec': tol, 'common_points': int(len(com)), 'disagreeing_points': len(bad), 'candidate_resolution_A_per_um': None if R is None else float(R),
            'support_points_above_candidate': len(sup), 'support_points_within_1dec': len(near), 'bias_coverage': cov,
            'support_rule': {'min_points_above_candidate': RES_SUPPORT_MIN, 'near_decades': RES_NEAR_DEC, 'bias_coverage': RES_BIAS_COVERAGE},
            'intervention': iv, 'evidence': {'run': evidence(da, ea), 'ref': evidence(db, eb)},
            'application_scope': {'quantity': col, 'film_nm': _num(eb.get('thickness_nm')), 'settings': settings(db, eb), 'bias_range_V': rng,
                                  'endpoints': [{'run_id': x.get('run_id'), 'dir': rel(dx), 'numerics_sha256': numerics(dx)} for dx, x in ((da, ea), (db, eb))],
                                  'note': 'applies only to this quantity, film, physical model/settings and V_G range; no cross-film transfer; a pair containing a tested run is no independent ceiling evidence for an upper-bound test (ruling c)'},
            'qualified': not why,
            'qualification': '; '.join(why) if why else 'distinct accepted runs with complete finite exports, verified numerical intervention, agreement support and full bias coverage, finite positive candidate'}


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


def aff(run, base, given=None, source=None, smoke=False, strict=False):
    da, ea, ca = load(run); db, eb, cb = load(base); res, src, demo, rev = resolution([ea, eb], given, source, strict)
    lab, exp, note = status((ea['label'], eb['label']), 'aff', smoke, (ea['run_id'], eb['run_id']))
    out = {'test': 'H-E AFF (A16 frozen scoring)', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id'], 'run_label': ea['label'], 'ref_label': eb['label'],
           'resolution_A_per_um': res, 'resolution_source': src, 'resolution_evidence': rev, 'evidence': {'run': evidence(da, ea), 'ref': evidence(db, eb)}}
    if note: out['label_note'] = note
    inv = usable((ea, ca), (eb, cb))
    if inv:
        out['rigidity'] = inv
        if exp is not None: out['registered_shift_mV'] = exp; out['shift_verdict'] = inv
        return out
    oa, ob = valid_mask(ca, res, demo), valid_mask(cb, res, demo)
    va, vb = vth_cc(ca['vg_V'], ca['id_A_per_um'], oa), vth_cc(cb['vg_V'], cb['id_A_per_um'], ob)
    dv = 1e3 * (va - vb) if va is not None and vb is not None else None
    r = aff_core(ca['vg_V'], ca['id_A_per_um'], oa, cb['vg_V'], cb['id_A_per_um'], ob, res, dv)
    out.update({'level_floor_independent_of_resolution_if_res_le': AFF['floor_A'] / AFF['res_mult'], 'Vth_cc_run_V': va, 'Vth_cc_ref_V': vb, 'dVth_cc_mV': dv, **r})
    if exp is not None: out['registered_shift_mV'] = exp; out['shift_verdict'] = prov(band(dv, exp, AFF['shift_tol_mV']), demo)
    out['rigidity'] = prov(out['rigidity'], demo)
    return out


def he_alloff(run, base, smoke=False):
    da, ea, ca = load(run); db, eb, cb = load(base); lab, exp, note = status((ea['label'], eb['label']), 'he_alloff', smoke, (ea['run_id'], eb['run_id']))
    out = {'test': 'H-E all-inputs-off dV_th,cc', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id']}
    if note: out['label_note'] = note
    inv = usable((ea, ca), (eb, cb))
    if inv: out['verdict'] = inv
    else:
        va, vb = vth_cc(ca['vg_V'], ca['id_A_per_um'], kcl_mask(ca)), vth_cc(cb['vg_V'], cb['id_A_per_um'], kcl_mask(cb)); dv = (va - vb) if va is not None and vb is not None else None
        out.update({'Vth_cc_run_V': va, 'Vth_cc_ref_V': vb, 'dVth_cc_V': dv})
    if exp: out['bands'] = {k: {'band_V': f'{c:+.3f} +- {h:.3f}', 'verdict': inv or band(dv, c, h)} for k, (c, h) in exp.items()}
    out['evidence'] = {'run': evidence(da, ea), 'ref': evidence(db, eb)}
    return out


def s3_minus_s105(run, ref, smoke=False):
    da, ea, ca = load(run); db, eb, cb = load(ref); lab, exp, note = status((ea['label'], eb['label']), 's3_minus_s105', smoke, (ea['run_id'], eb['run_id']))
    out = {'test': 'H-E S3-01 - S1-05 (A13)', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id']}
    if note: out['label_note'] = note
    inv = usable((ea, ca), (eb, cb))
    if inv: out['verdict'] = inv; dv = None
    else:
        va, vb = vth_cc(ca['vg_V'], ca['id_A_per_um'], kcl_mask(ca)), vth_cc(cb['vg_V'], cb['id_A_per_um'], kcl_mask(cb)); dv = (va - vb) if va is not None and vb is not None else None
        out.update({'Vth_cc_run_V': va, 'Vth_cc_ref_V': vb, 'difference_V': dv})
    if exp: out.update({'band_V': f'{exp[0]:+.3f} +- {exp[1]:.3f}', 'verdict': inv or band(dv, *exp), 'note': 'not independent of the 2.0 nm all-off band (register A13/A16)'})
    out['evidence'] = {'run': evidence(da, ea), 'ref': evidence(db, eb)}
    return out


# ---------------------------------------------------------------- H-B
def strip_iv(run):
    """(dir, execution.json, columns of strip_iv.csv or None) of a strip run"""
    d = ce.resolve(run); exj = json.loads((d / 'execution.json').read_text()); exj['__scope__'] = {'dir': str(d), 'bias_V': None}   # V_D axis: no V_G range
    return d, exj, read_cols(d / 'strip_iv.csv')


def strip_point(c, v, res):
    k = int(np.argmin(np.abs(c['vd_V'] - v)))
    if abs(c['vd_V'][k] - v) > 1e-6: return None, 'no solved point at %.1f V' % v
    i = c['id_A_per_um'][k]
    if not math.isfinite(i): return None, f'non-finite current at {v} V'
    if not (c['kcl_pass'][k] > 0): return None, f'censored (KCL) at {v} V'
    if i <= 0 or i < res: return None, f'below resolution or non-positive at {v} V ({i:.3g} A/um, resolution {res:.3g})'
    return float(i), 'resolved'


def hb_ratio(run, given=None, source=None, smoke=False, strict=False):
    d, exj, c = strip_iv(run); res, src, demo, rev = resolution([exj], given, source, strict); lab, _, note = status(exj['label'], 'hb_ratio', smoke, (exj['run_id'],))
    out = {'test': 'H-B strip I(0.7)/I(0.1)', 'label': lab, 'run': exj['run_id'], 'run_label': exj['label'], 'band': '7.0 +- 0.5',
           'resolution_A_per_um': res, 'resolution_source': src, 'resolution_evidence': rev, 'evidence': evidence(d, exj), **({'label_note': note} if note else {})}
    inv = usable((exj, c))
    if inv: out['verdict'] = inv; return out
    i1, s1 = strip_point(c, 0.1, res); i7, s7 = strip_point(c, 0.7, res)
    r = (i7 / i1) if (i1 and i7) else None
    v = band(r, *HB) if r is not None else f'unresolved ({s1}; {s7})'
    out.update({'I_0p1V': i1, 'I_0p7V': i7, 'ratio': r, 'verdict': prov(v, demo, f'resolution {res:.3g} not demonstrated')})
    return out


def hb_transfer(r13, r63, r20, given=None, source=None, smoke=False, strict=False):
    """(W/L)_par fitted on 13.2 nm: I_floor,pred(t) = I_strip(t, 0.7 V) x L_p x (W/L)_par (CAMPAIGN_DESIGN 7.3) -> pred(t) = floor(13.2) I_strip(t)/I_strip(13.2)"""
    runs = {13.2: r13, 6.3: r63, 2.0: r20}; data = {t: (strip_iv(r) if r else None) for t, r in runs.items()}
    rs = {t: resolution([x[1]], given, source, strict) for t, x in data.items() if x}; demo = all(v[2] for v in rs.values())   # each run's own resolution
    labs = tuple(x[1]['label'] if x else None for x in data.values())
    lab, kind, note = status(labs, 'hb_transfer', smoke, tuple(x[1]['run_id'] if x else None for x in data.values()))
    lp = {x[1].get('strip', {}).get('L_p_um') for x in data.values() if x}
    out = {'test': 'H-B floor transfer, (W/L)_par fitted on 13.2 nm', 'label': lab, 'branch': kind, 'runs': {t: (x[1]['run_id'] if x else None) for t, x in data.items()},
           'L_p_um': sorted(lp, key=str), 'floors_measured': pc.FLOORS,
           'resolution_A_per_um': {t: x[0] for t, x in rs.items()}, 'resolution_source': {t: x[1] for t, x in rs.items()},
           'resolution_evidence': {t: x[3] for t, x in rs.items()}, 'evidence': {t: evidence(x[0], x[1]) for t, x in data.items() if x}}
    if note: out['label_note'] = note
    def fin(v): out['verdict'] = prov(v, demo); return out
    inv = usable(*[(x[1], x[2]) for x in data.values() if x])
    if inv: out['verdict'] = inv; return out
    I = {t: (strip_point(x[2], 0.7, rs[t][0]) if x else (None, 'no run')) for t, x in data.items()}
    out['I_strip_0p7V'] = {t: v[0] for t, v in I.items()}
    if len(lp) != 1 or None in lp: return fin('unresolved (strip decks with different or missing L_p)')
    if I[13.2][0] is None: return fin(f'unresolved (13.2 nm calibration strip: {I[13.2][1]})')
    wl = pc.FLOORS[13.2] / (I[13.2][0] * lp.pop()); out['WL_par_per_um'] = wl; per = {}
    for t in (6.3, 2.0):
        if I[t][0] is None: per[t] = {'verdict': f'unresolved ({I[t][1]})'}; continue
        e = math.log10(pc.FLOORS[13.2] * I[t][0] / I[13.2][0] / pc.FLOORS[t])
        per[t] = {'pred_floor_A_per_um': pc.FLOORS[13.2] * I[t][0] / I[13.2][0], 'log10_pred_over_meas': e, 'verdict': 'PASS' if abs(e) <= HB_DEC else 'FAIL'}
    out['films'] = per
    vs = [per[t]['verdict'] for t in per]
    return fin('FAIL' if 'FAIL' in vs else 'PASS' if all(v == 'PASS' for v in vs) else 'unresolved')


# ---------------------------------------------------------------- H-C
def hc_nominal(run, ig_given=None, ig_source=None, smoke=False, strict=False):
    d, exj, c = load(run); res, src, demo, rev = ig_resolution([exj], ig_given, ig_source, (exj['run_id'],), strict); t = float(exj['thickness_nm'])
    lab, _, note = status(exj['label'], 'hc_nominal', smoke, (exj['run_id'],)); b = NOM_FRAC * pc.FLOORS[t]
    out = {'test': 'H-C nominal leakage |I_G(-3 V)| <= 1e-2 x floor', 'label': lab, 'run': exj['run_id'], 'run_label': exj['label'], 'abs_IG_m3V_A_per_um': None,
           'bound_A_per_um': b, 'resolution_A_per_um': res, 'resolution_source': src, 'resolution_evidence': rev, 'evidence': evidence(d, exj), **({'label_note': note} if note else {})}
    inv = usable((exj, c))
    if inv: out['verdict'] = inv; return out
    k = at(c['vg_V'], -3.0); hit = abs(c['vg_V'][k] + 3.0) < 1e-6; cens = hit and not (c['kcl_pass'][k] > 0)
    x = abs(float(c['ig_raw_A'][k])) if hit else None
    out.update({'abs_IG_m3V_A_per_um': x, 'verdict': prov('unresolved (KCL-censored at -3 V)' if cens else censored_upper(x, b, res, demo), demo)})
    return out


def gen_core(ca, cb, res, demo, bound=GEN_BOUND, res_b=None):
    """H-C generation on two runs' columns (a = mechanism, b = control), common V_G of the 7.1 floor window (rules in the module docstring).
    Both currents below their resolutions: |I_a - I_b| < R_a + R_b, the ceiling (Codex 2026-10-12 item 2; R_b = R_a = res unless res_b).
    Non-finite required values or window points of one run only -> invalid (item 3)."""
    ra, rb = res, (res if res_b is None else res_b)
    inv = bad_points(ca, cb, ('id_A_per_um', 'kcl_pass', 'above_abs_floor'), win=True)
    if inv: return {'common_points': 0, 'resolved_points': 0, 'max_abs_dID_lower_A_per_um': None, 'max_abs_dID_upper_A_per_um': None,
                    'max_unresolved_ceiling_A_per_um': None, 'kcl_censored_vg': [], 'verdict': inv, 'points': []}
    pts = []
    rv = lambda c, k, r: abs(c['id_A_per_um'][k]) >= r and c['id_A_per_um'][k] != 0 and (demo or c['above_abs_floor'][k] > 0)
    for v in common(ca['vg_V'], cb['vg_V'], True):
        ka, kb = at(ca['vg_V'], v), at(cb['vg_V'], v); a, b = float(ca['id_A_per_um'][ka]), float(cb['id_A_per_um'][kb]); p = {'vg_V': float(v), 'I_run': a, 'I_ctrl': b}
        if not (ca['kcl_pass'][ka] > 0 and cb['kcl_pass'][kb] > 0): p['class'] = 'censored (KCL)'
        elif rv(ca, ka, ra) and rv(cb, kb, rb):
            if a * b > 0 and abs(math.log10(abs(a)) - math.log10(abs(b))) <= MESH_DEC: p.update({'class': 'not resolved: within the 0.1 dec numerical spread', 'ceiling': SPREAD * max(abs(a), abs(b))})
            else: p.update({'class': 'resolved', 'lower': abs(a - b), 'upper': abs(a - b)})
        elif rv(ca, ka, ra) or rv(cb, kb, rb):
            x, rx, ro = (abs(a), ra, rb) if rv(ca, ka, ra) else (abs(b), rb, ra)
            if math.log10(x / rx) > MESH_DEC: p.update({'class': 'resolved (one run only)', 'lower': x - ro, 'upper': x + ro})
            else: p.update({'class': 'not resolved: one run within 0.1 dec of the resolution', 'ceiling': x + ro})
        else: p.update({'class': 'below resolution', 'ceiling': ra + rb})
        pts.append(p)
    lo = [p['lower'] for p in pts if 'lower' in p]; up = [p['upper'] for p in pts if 'upper' in p]; cl = [p['ceiling'] for p in pts if 'ceiling' in p]
    cz = [p['vg_V'] for p in pts if p['class'].startswith('censored')]
    if not pts: v = 'unresolved (no common point in the window)'
    elif lo and max(lo) > bound: v = 'FAIL' if demo else 'FAIL (PROVISIONAL: resolution not demonstrated)'
    elif cz: v = f'unresolved (KCL-censored at V_G {cz}: never a pass, not a fail from those points)'
    else:
        # defect found 2026-10-12 (round 3; documented rule: FAIL only from a resolved LOWER bound above the bound): here every lower bound is
        # <= bound, so an upper bound above it (one-sided point, x + R) leaves the point unresolved, never a FAIL
        hi_up = [p['vg_V'] for p in pts if p.get('upper', 0) > bound]
        parts = (([f'unresolved (one-sided differences at V_G {hi_up}: lower bound <= {bound:.3g} < upper bound; neither a pass nor a fail)'] if hi_up
                  else [censored_upper(max(up), bound, max(ra, rb), demo)]) if up else []) + ([censored_upper(0.0, bound, max(cl), demo)] if cl else [])
        bad = [s for s in parts if not (s == 'PASS' or s.startswith('below resolution'))]
        v = bad[0] if bad else (parts[0] if len(parts) == 1 else 'PASS (resolved points); ' + parts[1])
    return {'common_points': len(pts), 'resolved_points': len(lo), 'max_abs_dID_lower_A_per_um': max(lo, default=None), 'max_abs_dID_upper_A_per_um': max(up, default=None),
            'max_unresolved_ceiling_A_per_um': max(cl, default=None), 'kcl_censored_vg': cz, 'verdict': v, 'points': pts}


def hc_generation(run, ctrl, given=None, source=None, smoke=False, strict=False, per_run=None):
    """upper-bound test: per-run resolutions R_a (run) and R_b (control) (Codex round 3, fix 11; per_run = {'run': (R, PAIR.json),
    'control': (R, PAIR.json)}, else the single given/source for both), each in scope of its own run; neither pair may contain the run
    or the control (ruling c). Subtraction ceilings use R_a + R_b (item 2)."""
    da, ea, ca = load(run); db, eb, cb = load(ctrl)
    rr = role_res((('run', ea), ('control', eb)), given, source, per_run, strict, independent=True, under_test=(ea['run_id'], eb['run_id']))
    demo = all(v[2] for v in rr.values())
    lab, _, note = status((ea['label'], eb['label']), 'hc_generation', smoke, (ea['run_id'], eb['run_id']))
    out = {'test': 'H-C generation max |dI_D| over V_G in [-2, -0.5] V <= 1e-20 A/um', 'label': lab, 'run': ea['run_id'], 'control': eb['run_id'],
           'bound_A_per_um': GEN_BOUND, 'resolution_A_per_um': {k: v[0] for k, v in rr.items()}, 'resolution_source': {k: v[1] for k, v in rr.items()},
           'resolution_evidence': {k: v[3] for k, v in rr.items()}, 'evidence': {'run': evidence(da, ea), 'control': evidence(db, eb)}, **({'label_note': note} if note else {})}
    inv = usable((ea, ca), (eb, cb))
    if inv: out['verdict'] = inv; return out
    g = gen_core(ca, cb, rr['run'][0], demo, res_b=rr['control'][0]); g['verdict'] = prov(g['verdict'], demo); out.update(g)
    return out


def mesh_core(ca, cb, res, demo):
    """S2-11 rule (module docstring) on two runs' columns: a = refined run, b = reference. Non-finite required values or bias points of
    one run only -> invalid (Codex 2026-10-12 item 3)"""
    inv = bad_points(ca, cb, ('ig_raw_A', 'kcl_pass'))
    if inv: return {'common_points': int(len(common(ca['vg_V'], cb['vg_V']))), 'scored_points': 0, 'resolved_both_points': 0, 'max_change_dec': None, 'verdict': inv, 'points': []}
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


def hc_mesh(run, ref, given=None, source=None, ig_given=None, ig_source=None, smoke=False, strict=False):
    """S2-11 (register H-C). Codex 2026-10-12 item 5: the verdict is bound to its run pair (sha256 of both runs' files, inputs recorded so
    hc_explains can re-score it) and to its scope (the physical settings of the pair: film, oxide set, overrides, material model, deck);
    a pair that is not a verified oxide y-mesh refinement of the reference (actual deck values, fix 8) is 'not demonstrated', never a
    mesh pass. Resolution (ruling c): an I_G ceiling in scope of both runs; the pair under test is never its own resolution; an I_D-type
    resolution is out of scope for this I_G quantity (PROVISIONAL)."""
    da, ea, ca = load(run); db, eb, cb = load(ref)
    lab, _, note = status((ea['label'], eb['label']), 'hc_mesh', smoke, (ea['run_id'], eb['run_id']))
    iv = intervention(da, ea, db, eb); mech = mechanism(ea); t = _num(ea.get('thickness_nm')); oxs = ovr(eb).get(GT + 'set')
    out = {'test': 'H-C S2-11: resolved |I_G| changes by <= 0.1 dec', 'label': lab, 'run': ea['run_id'], 'ref': eb['run_id'],
           'refinement': 'oxide y-mesh x0.5 at the 0.002/0.017 um lines, y = 0 line kept: Al2O3 about x1.5, HfO2 about x2 (QTNLSC only; not ITAT/TAT.SLICEPTS)',
           'inputs': {'run': rel(da), 'ref': rel(db), 'given': given, 'source': (rel(src_path(source)) if source else None), 'ig_given': ig_given,
                      'ig_source': (rel(src_path(ig_source)) if ig_source else None), 'smoke': smoke},
           'evidence': {'run': evidence(da, ea), 'ref': evidence(db, eb)}, 'intervention': iv,
           'scope': {'mechanism': mech, 'thickness_nm': t, 'oxide_set': oxs, 'run_pair': [ea['run_id'], eb['run_id']], 'settings': settings(db, eb),
                     'certifies': f'{mech} convergence under this oxide y-mesh refinement, only for runs with exactly the physical settings of {eb["run_id"]} '
                                  f'({t:g} nm film, oxide set {oxs}, same overrides, material model and deck statements)',
                     'does_not_certify': 'other films; another oxide parameter set (e.g. nominal S2-04 from the worst-set S2-11, ruling b); ITAT (S2-12/S2-13: TAT.SLICEPTS untested); generation/SRH'},
           **({'label_note': note} if note else {})}
    if ig_given is not None: res, src, demo, rev = ig_resolution([ea, eb], ig_given, ig_source, (), strict, forbid_pair=(ea['run_id'], eb['run_id']), refine_ok=True)
    else: res, src, demo, rev = resolution([ea, eb], given, source, strict, quantity='ig_raw_A'); src = 'current resolution (I_D-type; out of scope for I_G, ruling c): ' + src
    out.update({'resolution_A_per_um': res, 'resolution_source': src, 'resolution_evidence': rev})
    pe = (rev or {}).get('pair_evidence')
    if pe:   # Codex round 3 ruling: a DOS comparison and the oxide-mesh comparison may share run_0067; recorded, never called independent
        pr = {pe['run']['run_id'], pe['ref']['run_id']}; sh = sorted(pr & {ea['run_id'], eb['run_id']})
        out['resolution_pair_relation'] = {'resolution_pair': sorted(pr), 'mesh_pair': [ea['run_id'], eb['run_id']], 'shared_baseline': sh, 'independent': not sh,
                                           'note': (f'shares {", ".join(sh)} with the S2-11 comparison: numerical stability of that baseline under two interventions; '
                                                    'NOT independent evidence' if sh else 'no run shared with the S2-11 comparison')}
    inv = usable((ea, ca), (eb, cb))
    if inv: out['verdict'] = inv; return out
    core = mesh_core(ca, cb, res, demo); v = prov(core.pop('verdict'), demo); out.update(core)
    if iv['verified'] and iv.get('kind') == 'oxide y-mesh factor' and iv.get('refined') == 'run': out['verdict'] = v
    else:
        out['comparison_verdict'] = v
        out['verdict'] = ('not demonstrated (not a verified oxide y-mesh refinement of the reference: '
                          + (iv.get('why') or f'{iv.get("kind")}, refined {iv.get("refined")}') + '); never a mesh pass')
    return out


def ctrl_at(vg, cc):
    """control I_D at the bias points vg (Codex re-review fix 6): the control's own point if it exists and passed KCL; otherwise linear
    interpolation (as post_run_checks) only between two adjacent KCL-passed control points; across a KCL-censored control point or outside
    the control's range -> NaN (unsupported, never interpolated or extrapolated)"""
    cv = np.asarray(cc['vg_V'], float); o = np.argsort(cv, kind='stable'); cv = cv[o]; ci = np.asarray(cc['id_A_per_um'], float)[o]; ck = np.asarray(cc['kcl_pass'], float)[o] > 0
    out = np.full(len(vg), np.nan)
    for n, v in enumerate(np.asarray(vg, float)):
        k = np.flatnonzero(np.abs(cv - v) < 1e-6)
        if k.size: out[n] = ci[k[0]] if ck[k[0]] else np.nan; continue
        j = int(np.searchsorted(cv, v))
        if 0 < j < len(cv) and ck[j - 1] and ck[j]: out[n] = ci[j - 1] + (ci[j] - ci[j - 1]) * (v - cv[j - 1]) / (cv[j] - cv[j - 1])
    return out


def floor_metrics_masked(c, t, cc=None):
    """CAMPAIGN_DESIGN 7.1/7.2 floor metrics exactly as post_run_checks.floor_metrics (which is not changed and stays as it is for its other
    callers), but with KCL censoring applied first (Codex re-review fix 6): a KCL-failed run point is never a valid floor point and never
    enters the slope, the floor ratio or the control subtraction; the control comes from ctrl_at (own KCL-passed point, no interpolation
    across a censored control bracket). Support minima are those of post_run_checks (slope >= 3 valid points, ratios >= 1 point): below
    them the metric is None, i.e. its sub-result is unresolved. Identical to post_run_checks.floor_metrics when nothing is censored and the
    grids match (selftest and smoke check)."""
    vg, idv, ok = np.asarray(c['vg_V'], float), np.asarray(c['id_A_per_um'], float), np.asarray(c['kcl_pass'], float) > 0
    fl, kcl = pc.FLOORS[t], lim71(t); w = window(vg); nw = int(w.sum()); valid = w & ok & (idv > kcl)
    r = {'window_points': nw, 'valid_points': int(valid.sum()), 'valid_fraction': float(valid.sum() / max(nw, 1)),
         'kcl_censored_vg': [float(v) for v in vg[w & ~ok]], 'sign_reversals_vg': [float(v) for v in vg[w & ok & (idv < 0)]]}
    if valid.any():
        r['floor_ratio_dec'] = float(np.median(np.log10(idv[valid] / fl)))
        if valid.sum() >= 3: r['floor_slope_dec_per_V'], r['floor_slope_se'] = pc.slope(vg[valid], np.log10(idv[valid]))
    mv, mi = ce.ct.bd.read_meas(t); mw = (mv >= -2 - 1e-9) & (mv <= -0.5 + 1e-9) & (mi > 0)
    r['measured_slope_dec_per_V'], r['measured_slope_se'] = pc.slope(mv[mw], np.log10(mi[mw]))
    r['slope_limit_dec_per_V'] = 2 * abs(r['measured_slope_dec_per_V']) + 2 * r['measured_slope_se']
    if cc is not None:
        ci = ctrl_at(vg, cc); sup = w & ok & np.isfinite(ci); d = np.where(sup, idv - np.nan_to_num(ci), np.nan); dv = sup & (d > kcl)
        cw = window(np.asarray(cc['vg_V'], float))
        r.update({'control_kcl_censored_vg': [float(v) for v in np.asarray(cc['vg_V'], float)[cw & ~(np.asarray(cc['kcl_pass'], float) > 0)]],
                  'control_unsupported_vg': [float(v) for v in vg[w & ok & ~np.isfinite(ci)]], 'd_points': int(dv.sum()),
                  'd_floor_ratio_dec': float(np.median(np.log10(d[dv] / fl))) if dv.any() else None, 'd_valid_fraction': float(dv.sum() / max(nw, 1))})
    lim = r['slope_limit_dec_per_V']
    r['verdict_inputs'] = {'valid_ge_80pct': r['valid_fraction'] >= 0.8, 'slope_ok': ('floor_slope_dec_per_V' in r and abs(r['floor_slope_dec_per_V']) <= lim),
                           'd_floor_within_0p5dec': (r.get('d_floor_ratio_dec') is not None and abs(r['d_floor_ratio_dec']) <= 0.5) if cc is not None else None}
    return r


def leak_slopes(c, cc, t, res):
    """reported only (not scored): least-squares slopes over the 7.1 window of log10 |I_G| (points >= res, KCL passed) and of log10 dI_D
    (dI_D = I_D - control from ctrl_at, run and control KCL-passed, points above the 7.1 KCL limit; fix 6)"""
    w = window(c['vg_V']); ok = c['kcl_pass'] > 0; ig = np.abs(c['ig_raw_A']); m = w & (ig >= res) & (ig > 0) & ok
    ci = ctrl_at(c['vg_V'], cc); d = np.where(np.isfinite(ci), c['id_A_per_um'] - np.nan_to_num(ci), np.nan); md = w & ok & np.isfinite(d) & (d > lim71(t))
    return {'IG_slope_dec_per_V': pc.slope(c['vg_V'][m], np.log10(ig[m]))[0] if m.sum() >= 3 else None, 'IG_points': int(m.sum()),
            'dID_slope_dec_per_V': pc.slope(c['vg_V'][md], np.log10(d[md]))[0] if md.sum() >= 3 else None, 'dID_points': int(md.sum())}


def worst_verdict(flat, thick):
    """register H-C worst case: holds if the leakage FAILS flatness OR thickness scaling; FAIL only if both are evaluated and both hold"""
    f = [n for n, s in (('flatness', flat), ('thickness scaling', thick)) if s.startswith('fails')]
    if f: return 'PASS (worst-case leakage fails ' + ' and '.join(f) + ')'
    if flat.startswith('flat') and thick.startswith('holds'): return 'FAIL (flat within the registered limit and thickness scaling holds)'
    return 'unresolved (neither criterion fails and at least one could not be evaluated)'


def floor_qualification(items):
    """(ok, why) for the 7.1 floor criteria (Codex 2026-10-12 item 4; per run since round 3): items = [(role, demonstrated?, res, film)].
    Their validity limit is the KCL PROXY, so they are PROVISIONAL unless every run has a demonstrated I_D-type resolution at or below
    the 7.1 limit of its film"""
    nd = [r for r, dm, _, _ in items if not dm]
    if nd: return False, PROV_WHY + f' for {nd}; 7.1 floor validity rests on the KCL limit'
    hi = [f'{r} ({res:.3g} A/um at {t:g} nm)' for r, _, res, t in items if res > lim71(t) * (1 + 1e-9)]
    return (not hi), (f'demonstrated resolution above the 7.1 validity limit: {hi}' if hi else '')


def _res_out(rr): return {'resolution_A_per_um': {k: v[0] for k, v in rr.items()}, 'resolution_source': {k: v[1] for k, v in rr.items()}, 'resolution_evidence': {k: v[3] for k, v in rr.items()}}


def hc_worst(run, ctrl, run2, ctrl2, given=None, source=None, smoke=False, strict=False, per_run=None):
    """S2-08 (13.2 nm, control S1-02) with S0-02 = run_0067 (2.0 nm, control S0-01) for thickness scaling (module docstring); every metric
    on KCL-masked run and control points (fix 6); per-run resolutions (round 3, fix 11; roles run, control, run_2p0, control_2p0), each
    in scope of its own run (ruling c, numerical endpoint)"""
    L = [load(x) for x in (run, ctrl, run2, ctrl2)]; (d, exj, c), (dc, ejc, cc), (d2, ej2, c2), (dc2, ejc2, cc2) = L
    t, t2 = float(exj['thickness_nm']), float(ej2['thickness_nm']); roles = ('run', 'control', 'run_2p0', 'control_2p0')
    rr = role_res(tuple(zip(roles, (exj, ejc, ej2, ejc2))), given, source, per_run, strict)
    lab, _, note = status((exj['label'], ejc['label'], ej2['label'], ejc2['label']), 'hc_worst', smoke, (exj['run_id'], ejc['run_id'], ej2['run_id'], ejc2['run_id']))
    out = {'test': 'H-C worst-case leakage fails flatness OR thickness scaling', 'label': lab, 'run': exj['run_id'], 'control': ejc['run_id'],
           'run_2p0': ej2['run_id'], 'control_2p0': ejc2['run_id'], **({'label_note': note} if note else {}),
           'evidence': {k: evidence(x[0], x[1]) for k, x in zip(roles, L)}}
    inv = usable(*[(x[1], x[2]) for x in L])
    if inv: out.update({**_res_out(rr), 'verdict': inv}); return out
    fm, fm2 = floor_metrics_masked(c, t, cc), floor_metrics_masked(c2, t2, cc2)
    s, lim = fm.get('floor_slope_dec_per_V'), fm['slope_limit_dec_per_V']
    flat = (f'unresolved (insufficient support: {fm["valid_points"]} valid uncensored floor points < 3)' if s is None else
            ('fails flatness' if abs(s) > lim else 'flat (within the registered limit)'))
    r1, r2 = fm.get('d_floor_ratio_dec'), fm2.get('d_floor_ratio_dec')
    thick = ('unresolved (one film: thickness scaling needs two)' if abs(t - t2) < 1e-6 else
             'unresolved (d_floor_ratio not computable: no supported window point (run and control KCL-passed, no interpolation across a censored control point) with dI_D above the 7.1 KCL limit)' if r1 is None or r2 is None else
             'fails thickness scaling' if abs(r1 - r2) > TS_DEC else 'holds (d_floor_ratios within 0.5 dec)')
    ok, why = floor_qualification([(k, rr[k][2], rr[k][0], tt) for k, tt in zip(roles, (t, t, t2, t2))])
    out.update({'flatness': {'quantity': 'slope of log10 total I_D over [-2, -0.5] V (CAMPAIGN_DESIGN 7.1 floor_slope), KCL-censored points excluded', 'floor_slope_dec_per_V': s,
                             'slope_limit_dec_per_V': lim, 'valid_fraction': fm['valid_fraction'], 'valid_points': fm['valid_points'], 'kcl_censored_vg': fm['kcl_censored_vg'], 'sub_result': flat},
                'thickness_scaling': {'d_floor_ratio_dec': {t: r1, t2: r2}, 'd_points': {t: fm.get('d_points'), t2: fm2.get('d_points')}, 'tolerance_dec': TS_DEC, 'sub_result': thick,
                                      'censored_or_unsupported_vg': {t: sorted(set(fm['kcl_censored_vg'] + fm['control_kcl_censored_vg'] + fm['control_unsupported_vg'])),
                                                                     t2: sorted(set(fm2['kcl_censored_vg'] + fm2['control_kcl_censored_vg'] + fm2['control_unsupported_vg']))},
                                      'note': 'S2-07 (6.3 nm worst) is kept out by the register; the two films are S2-08 and S0-02 (run_0067)'},
                'leakage_slopes_reported': {t: leak_slopes(c, cc, t, rr['run'][0]), t2: leak_slopes(c2, cc2, t2, rr['run_2p0'][0])}, **_res_out(rr),
                'floor_validity_limit_A_per_um': {t: lim71(t), t2: lim71(t2)}, 'verdict': prov(worst_verdict(flat, thick), ok, why)})
    return out


def explains_verdict(crit, conv, why):
    """register H-C falsification: a CONVERGED mechanism passing all four 7.2 floor criteria falsifies H-C"""
    if not all(crit.values()): return 'does not explain the floor (no falsification from this mechanism)'
    if conv is True: return 'FALSIFIES H-C (converged mechanism passes all four 7.2 floor criteria)'
    return 'unresolved (passes all four 7.2 floor criteria; ' + ('not converged' if conv is False else 'convergence not demonstrated') + f': {why})'


def mesh_convergence(mesh_score, exj, d):
    """(converged?, evidence statement, record) of a QTNLSC mechanism run (directory d) from the registered S2-11 hc_mesh score (Codex
    2026-10-12 item 5): the score is re-computed from its recorded inputs, its run-file sha256 must be unchanged, and it counts only for a
    run with exactly the physical settings of the S2-11 reference (settings: film, oxide parameter set and every other non-numerical
    override, material model, deck; rulings b and c: S2-11 (worst set) does not certify the nominal S2-04, nor another film); a
    PROVISIONAL or not-demonstrated mesh verdict never counts"""
    if not mesh_score: return None, 'QTNLSC: needs the registered S2-11 hc_mesh score (--mesh-score)', None
    p = src_path(mesh_score)
    try: raw = p.read_bytes(); m = json.loads(raw)
    except Exception: return None, f'QTNLSC: mesh score {mesh_score} not readable', None
    rec = {'mesh_score': rel(p), 'mesh_score_sha256': hashlib.sha256(raw).hexdigest()}
    if not (isinstance(m, dict) and str(m.get('label', '')).startswith('registered test') and str(m.get('test', '')).startswith('H-C S2-11')):
        return None, 'QTNLSC: the mesh score is not a registered S2-11 hc_mesh score', rec
    inp = m.get('inputs')
    if not isinstance(inp, dict) or 'evidence' not in m: return None, 'QTNLSC: the mesh score carries no file-bound inputs/evidence (pre-fix format); re-score S2-11', rec
    try: f = hc_mesh(**{k: inp.get(k) for k in ('run', 'ref', 'given', 'source', 'ig_given', 'ig_source', 'smoke')})
    except Exception as e: return None, f'QTNLSC: re-scoring S2-11 from its run directories failed ({type(e).__name__}: {e})', rec
    if f['evidence'] != m.get('evidence'): return None, 'QTNLSC: S2-11 run files changed since the mesh score was written (sha256 mismatch)', rec
    if f.get('verdict') != m.get('verdict') or not f['label'].startswith('registered test'): return None, 'QTNLSC: the mesh score does not match its re-score', rec
    sc = f['scope']; t = _num(exj.get('thickness_nm')); rec.update(run=f['run'], ref=f['ref'], scope=sc, verdict=f['verdict'])
    st = settings(d, exj)
    if st != sc['settings']:
        return None, (f'{mechanism(exj)} run at {t:g} nm is outside the S2-11 scope (pair {f["run"]} vs {f["ref"]}): its physical settings differ '
                      f'({settings_diff(st, sc["settings"])}); convergence not demonstrated (ruling b: the same oxide parameter set is required; '
                      'ruling c: no cross-film or cross-model transfer)'), rec
    v = f['verdict']; conv = True if v == 'PASS' else False if v.startswith('FAIL') else None
    return conv, f'QTNLSC: registered S2-11 hc_mesh {f["run"]} vs {f["ref"]}: {v} (same physical settings: {sc["thickness_nm"]:g} nm film, oxide set {sc.get("oxide_set")})', rec


def hc_explains(run, ctrl, mesh_score=None, smoke=False, given=None, source=None, strict=False, per_run=None):
    """register H-C falsification test on KCL-masked floor metrics (fix 6). With KCL-censored or unsupported window points the 7.2
    criteria cannot be established: the verdict is 'unresolved (insufficient support ...)' unless a criterion fails on the uncensored
    points whatever the censored ones are (valid fraction < 80 % even if every censored point were valid); never a falsification"""
    d, exj, c = load(run); dc, ejc, cc = load(ctrl); t = float(exj['thickness_nm'])
    rr = role_res((('run', exj), ('control', ejc)), given, source, per_run, strict)   # per-run resolutions (round 3, fix 11)
    lab, _, note = status((exj['label'], ejc['label']), 'hc_explains', smoke, (exj['run_id'], ejc['run_id']))
    out = {'test': 'H-C falsification: converged mechanism passing all CAMPAIGN_DESIGN 7.2 floor criteria', 'label': lab, 'run': exj['run_id'], 'control': ejc['run_id'],
           **({'label_note': note} if note else {}), 'evidence': {'run': evidence(d, exj), 'control': evidence(dc, ejc)}, **_res_out(rr)}
    inv = usable((exj, c), (ejc, cc))
    if inv: out['verdict'] = inv; return out
    fm = floor_metrics_masked(c, t, cc); vi = fm['verdict_inputs']; w, wc = window(c['vg_V']), window(cc['vg_V'])
    crit = {'valid_ge_80pct': bool(vi['valid_ge_80pct']), 'd_floor_within_0p5dec': bool(vi['d_floor_within_0p5dec']), 'slope_ok': bool(vi['slope_ok']),
            'kcl_pass_window_run_and_control': bool(np.all(c['kcl_pass'][w] > 0) and np.all(cc['kcl_pass'][wc] > 0))}
    mev = None
    if gt_on(exj, 'oxide_tat'):
        conv, why = None, 'ITAT: TAT.SLICEPTS = 12 (default) untested (5.28 PDF p.322: chosen so the currents are largely unchanged for a slightly higher or lower value); needs a logged amendment, e.g. a TAT.SLICEPTS sensitivity launch'
    elif gt_on(exj): conv, why, mev = mesh_convergence(mesh_score, exj, d)
    else:
        conv, why = None, 'generation/SRH: no mechanism-specific refinement run in the diagnostic set (baseline numerics only: S1-03 mesh x0.7, S1-04 DOS x2)'
    v = explains_verdict(crit, conv, why)
    cz = sorted(set(fm['kcl_censored_vg']) | set(fm['control_kcl_censored_vg'])); un = fm['control_unsupported_vg']
    if not all(crit.values()) and (cz or un) and (fm['valid_points'] + len(fm['kcl_censored_vg'])) / max(fm['window_points'], 1) >= 0.8:
        v = (f'unresolved (insufficient support: KCL-censored window points at V_G {cz}' + (f', control unsupported at V_G {un}' if un else '')
             + '; the 7.2 criteria cannot be established on the uncensored points; no falsification from this run)')
    ok, qwhy = floor_qualification([(k, rr[k][2], rr[k][0], tt) for k, tt in (('run', t), ('control', float(ejc['thickness_nm'])))])
    out.update({'floor_metrics': {k: fm.get(k) for k in ('valid_fraction', 'valid_points', 'floor_ratio_dec', 'd_floor_ratio_dec', 'floor_slope_dec_per_V', 'slope_limit_dec_per_V',
                                                         'kcl_censored_vg', 'control_kcl_censored_vg', 'control_unsupported_vg')},
                'floor_validity_limit_A_per_um': lim71(t), 'criteria': crit, 'converged': conv, 'convergence_evidence': why, 'mesh_evidence': mev,
                'verdict': prov(v, ok, qwhy)})
    if abs(t - 2.0) < 1e-6 and fm.get('d_floor_ratio_dec') is not None and fm['d_floor_ratio_dec'] < -HB_DEC:
        out['note_2p0'] = 'underprediction at 2.0 nm: the floor may be instrument-limited; an underprediction does not falsify a mechanism (CAMPAIGN_DESIGN 7.2)'
    return out


# ---------------------------------------------------------------- self-test (synthetic curves and synthetic run directories, no run data)
_GRID = np.round(np.arange(-3.0, 3.0 + 1e-9, 0.2), 6)
_OV = ['thickness_laws.Nt_cm3.alpha=1', 'solver.dos_levels.numa=384', 'solver.dos_levels.numd=192']
_GTO = [GT + 'enabled=1', GT + 'model=qtnlsc', GT + 'set=worst']


def _st_deck(oxide=1.0, dos=1, affinity=1.6, iface=1.0, mesh=1.0, numa=None, numd=None):
    """synthetic deck text (selftest only): the y.mesh oxide lines scale with oxide, the y = 0 line with iface, every mesh line with mesh,
    numa/numd with dos (or are given explicitly)"""
    g = lambda x: f'{x:.6g}'; na = int(384 * dos) if numa is None else numa; nd = int(192 * dos) if numd is None else numd
    return '\n'.join(['# synthetic selftest deck (not a campaign run)', 'go atlas', 'mesh width=1', f'x.mesh loc=0 spac={g(0.3 * mesh)}', f'x.mesh loc=24 spac={g(0.3 * mesh)}',
                      f'y.mesh loc=0 spac={g(6.25e-05 * iface * mesh)}', f'y.mesh loc=0.002 spac={g(0.00025 * oxide * mesh)}', f'y.mesh loc=0.017 spac={g(0.001 * oxide * mesh)}',
                      f'material region=3 affinity={affinity} eg300=8.8 me.tunnel=0.3', f'defects region=1 continuous numa={na} numd={nd} \\',
                      '  nta=5e20 wta=0.04', 'solve init', 'quit']) + '\n'


def _st_run(root, name, run_id, label, t, i_d, i_g=None, vg=_GRID, status='REAL_ATLAS_SCORED', ov=(), deck=None, timed_out=False, rc=0, lim=4.60552e-16, kcl=None, req=None):
    """synthetic transfer-run directory (selftest only; never a campaign run): execution.json, device.in, material model, terminal_currents.csv"""
    d = Path(root) / name; d.mkdir(parents=True, exist_ok=True)
    i_d = np.asarray(i_d, float); i_g = np.zeros_like(i_d) if i_g is None else np.asarray(i_g, float); k = np.ones(len(i_d)) if kcl is None else np.asarray(kcl, float)
    err = status == 'SIMULATOR_ERROR'
    exj = {'run_id': run_id, 'thickness_nm': t, 'label': label, 'returncode': rc, 'timed_out': timed_out,
           'scan': {'errors': ['Error: synthetic'] if err else [], 'finished': not (timed_out or err)}, 'requested_points': int(len(_GRID) if req is None else req),
           'overrides': list(_OV) + list(ov), 'validation': {'kcl_abs_limit_applied_A': lim}, 'status': status}
    (d / 'execution.json').write_text(json.dumps(exj)); (d / 'device.in').write_text(deck or _st_deck()); (d / 'material_model_used.json').write_text('{"synthetic": true}\n')
    with open(d / 'terminal_currents.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['vg_V', 'id_raw_A', 'is_raw_A', 'ig_raw_A', 'id_A_per_um', 'kcl_abs_A', 'kcl_pass', 'above_abs_floor'])
        for v, a, g, kk in zip(vg, i_d, i_g, k): w.writerow([v, a, -(a + g), g, a, 0.0, int(kk), int(abs(a) > lim)])
    return str(d)


def _st_strip(root, name, run_id, label, t, vd, i_d, lim=4.60552e-16):
    """synthetic strip-run directory (selftest only)"""
    d = Path(root) / name; d.mkdir(parents=True, exist_ok=True)
    exj = {'run_id': run_id, 'thickness_nm': t, 'label': label, 'mode': 'strip', 'overrides': list(_OV), 'returncode': 0, 'timed_out': False,
           'scan': {'errors': [], 'finished': True}, 'validation': {'kcl_abs_limit_applied_A': lim, 'requested_points': len(vd)}, 'strip': {'L_p_um': 20.0},
           'status': 'REAL_ATLAS_STRIP'}
    (d / 'execution.json').write_text(json.dumps(exj)); (d / 'device.in').write_text(_st_deck())
    with open(d / 'strip_iv.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['vd_V', 'id_raw_A', 'is_raw_A', 'id_A_per_um', 'kcl_abs_A', 'kcl_pass'])
        for v, a in zip(vd, i_d): w.writerow([v, a, -a, a, 0.0, 1])
    return str(d)


def probes(M, root):
    """Codex review cases (2026-10-12T13:18Z items 1-5; re-review ~15:28Z fixes 6-8 and rulings b, c). Kind 'R' = rejection probe: a
    broken implementation answers it wrongly, so it must FAIL on the code it guards against (mutation check); kind 'P' = positive or
    regression control. M = the scorer module under test (this module, or an earlier copy for the mutation check); root = an empty
    scratch directory. Synthetic data only: every run directory here is written by _st_run/_st_strip, never a campaign run. Scored runs
    are passed as loaded by M.load, so the application-scope check (ruling c) sees their directories."""
    root = Path(root); res = []
    def case(name, kind, fn):
        try: res.append((name, kind, bool(fn()), None))
        except Exception as e: res.append((name, kind, False, f'{type(e).__name__}: {e}'))
    def jw(name, r): p = root / name; p.write_text(json.dumps(r, indent=1, default=float)); return str(p)
    L = lambda run: M.load(run)[1]
    R = lambda name, run_id, label, t, i_d, **k: _st_run(root, name, run_id, label, t, i_d, **k)
    idb = lambda v0=0.5: np.minimum(10.0 ** (-9 + 4.0 * (_GRID - v0)), 1e-6)
    igb = -10.0 ** (-11.6 - 1.5 * (_GRID + 3))
    dos2 = ['solver.dos_levels.numa=768', 'solver.dos_levels.numd=384']; ox = [GT + 'oxide_mesh_factor=0.5']
    # item 1: resolution qualification (I_D-type: DOS x2 pair at 2.0 nm)
    D1 = R('D1', 'run_9001', 'c10_st_dos_ref_2p0', 2.0, idb()); i2 = np.where(idb() < 1e-18, 3 * idb(), idb())
    D2 = R('D2', 'run_9002', 'c10_st_dos_x2_2p0', 2.0, i2, ov=dos2, deck=_st_deck(dos=2))
    dos = M.resolution_pair(D2, D1); RD = dos['candidate_resolution_A_per_um']; dosj = jw('pair_dos.json', dos)
    case('resolution: a free-text I_D source is not demonstrated (item 1)', 'R', lambda: M.resolution([L(D1)], 1e-18, 'DOS x2 pair, free text')[2] is False)
    case('resolution: a qualified DOS x2 pair JSON (distinct completed runs, verified intervention, file-bound, in scope) is demonstrated', 'P', lambda: M.resolution([L(D1), L(D2)], RD, dosj)[2] is True)
    P1 = R('P1', 'run_9003', 'c10_st_phys_2p0', 2.0, i2, ov=['traps.fixed_interface_charge_Qf_cm2.value=1e12'], deck=_st_deck(affinity=1.25))
    case('resolution: a pair without a verified numerical intervention (physics override and deck change) is not demonstrated', 'R',
         lambda: M.resolution([L(D1)], 1e-12, jw('pair_phys.json', M.resolution_pair(P1, D1)))[2] is False)
    case('resolution: a self-pair (one run twice) is not demonstrated', 'R', lambda: M.resolution([L(D1)], 1e-12, jw('pair_self.json', M.resolution_pair(D1, D1)))[2] is False)
    R('D1c', 'run_9005', 'c10_st_dos_ref_2p0', 2.0, idb()); R('D2c', 'run_9006', 'c10_st_dos_x2_2p0', 2.0, i2, ov=dos2, deck=_st_deck(dos=2))
    tj = jw('pair_tamper.json', M.resolution_pair(str(root / 'D2c'), str(root / 'D1c')))
    R('D2c', 'run_9006', 'c10_st_dos_x2_2p0', 2.0, i2 * np.where(np.arange(len(_GRID)) == 30, 1.01, 1.0), ov=dos2, deck=_st_deck(dos=2))   # changed after the JSON
    case('resolution: run files changed after the pair JSON was written (sha256 mismatch) are not demonstrated', 'R', lambda: M.resolution([L(D1)], 1e-12, tj)[2] is False)
    case('resolution: a value below the pair candidate, NaN or negative is not demonstrated', 'R',
         lambda: all(M.resolution([L(D1), L(D2)], g, dosj)[2] is False for g in (0.5 * RD, float('nan'), -RD)))
    DT = R('DT', 'run_9004', 'c10_st_dos_x2_2p0', 2.0, i2, ov=dos2, deck=_st_deck(dos=2), status='TIMEOUT', timed_out=True, rc=1)
    case('resolution: a pair containing a timed-out run is not demonstrated', 'R', lambda: M.resolution([L(D1)], 1e-12, jw('pair_to.json', M.resolution_pair(DT, D1)))[2] is False)
    # item 1: I_G ceiling (two gate-tunnelling runs, oxide y-mesh x0.5, worst set at 2.0 nm)
    G1 = R('G1', 'run_9101', 'c10_st_ig_ref_2p0', 2.0, idb(), i_g=igb, ov=_GTO)
    G2 = R('G2', 'run_9102', 'c10_st_ig_ox_2p0', 2.0, idb(), i_g=np.where(np.abs(igb) < 1e-19, 2 * igb, igb), ov=_GTO + ox, deck=_st_deck(oxide=0.5))
    igp = M.resolution_pair(G2, G1, 'ig_raw_A'); RG = igp['candidate_resolution_A_per_um']; igj = jw('pair_ig.json', igp)
    sp = M.resolution_pair(G1, G1, 'ig_raw_A'); spj = jw('pair_ig_self.json', sp)
    ign = -10.0 ** (-18 - 1.5 * (_GRID + 3)); idn = idb().copy(); idn[15] = np.nan
    N4 = R('N4', 'run_9204', 'c10_s2_04_2p0', 2.0, idb(), i_g=ign, ov=_GTO)
    case('I_G ceiling: a self-pair of a gate-tunnelling run is not demonstrated (item 1)', 'R', lambda: M.ig_resolution([L(N4)], sp['candidate_resolution_A_per_um'], spj, ('run_9204',))[2] is False)
    case('I_G ceiling: a qualified oxide-mesh pair of gate-tunnelling runs not under test, in scope, is demonstrated', 'P', lambda: M.ig_resolution([L(N4)], RG, igj, ('run_9204',))[2] is True)
    # item 3: invalid required data in hc_nominal (2.0 nm bound 4.61e-17; |I_G(-3 V)| = 1e-18 under the qualified ceiling RG ~ 1.6e-19)
    N1 = R('N1', 'run_9201', 'c10_s2_04_2p0', 2.0, [1e-20], i_g=[-1e-18], vg=[-3.0], ov=_GTO, status='TIMEOUT', timed_out=True, rc=1)
    N2 = R('N2', 'run_9202', 'c10_s2_04_2p0', 2.0, idb(), i_g=ign, ov=_GTO, status='SIMULATOR_ERROR')
    N3 = R('N3', 'run_9203', 'c10_s2_04_2p0', 2.0, idn, i_g=ign, ov=_GTO)
    nom = lambda run: M.hc_nominal(run, RG, igj)['verdict']
    case('nominal: a timed-out run with one exported -3 V point is invalid, never PASS (item 3)', 'R', lambda: nom(N1).startswith('invalid'))
    case('nominal: a failed run (simulator error) is invalid, never PASS', 'R', lambda: nom(N2).startswith('invalid'))
    case('nominal: a completed run with a NaN elsewhere in its export is invalid, never PASS', 'R', lambda: nom(N3).startswith('invalid'))
    case('nominal: a completed run under a qualified, independent, in-scope I_G ceiling -> PASS (positive control)', 'P', lambda: nom(N4) == 'PASS')
    def cli():
        o = M.OUT; M.OUT = root / 'out'
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                a = M.main(['hc_generation', D2, D1, '--resolution', '1e-18', '--resolution-source', 'DOS x2 pair, free text', '--smoke'])
                b = M.main(['hc_nominal', N4, '--resolution-ig', '1e-18', '--resolution-ig-source', 'free text', '--smoke'])
        finally: M.OUT = o
        return a == 2 and b == 2
    case('CLI: a resolution cited with free text exits 2 (I_D-type and I_G ceiling; item 1)', 'R', cli)
    # item 2: generation ceiling R_a + R_b; item 3 in the core rules
    vw = np.round(np.arange(-2.0, -0.45, 0.1), 6); n = len(vw)
    Gd = lambda i: {'vg_V': vw, 'id_A_per_um': np.asarray(i, float), 'kcl_pass': np.ones(n), 'above_abs_floor': np.zeros(n)}
    case('generation: +5.4e-21 vs -5.4e-21 at R = 6e-21 is not consistent with 1e-20 (ceiling R_a + R_b = 1.2e-20; item 2)', 'R',
         lambda: M.gen_core(Gd(np.full(n, 5.4e-21)), Gd(np.full(n, -5.4e-21)), 6e-21, True)['verdict'].startswith('unresolved'))
    case('generation: a one-sided point with lower bound 5e-21 <= 1e-20 < upper bound 2.5e-20 is unresolved, not FAIL (defect found in round 3)', 'R',
         lambda: M.gen_core(Gd(np.full(n, 1.5e-20)), Gd(np.full(n, 5e-21)), 1e-20, True)['verdict'].startswith('unresolved'))
    inan = np.full(n, 1e-23); inan[3] = np.nan
    case('generation: a NaN window current is invalid, never consistent (item 3)', 'R', lambda: M.gen_core(Gd(inan), Gd(np.full(n, 2e-23)), 1e-21, True)['verdict'].startswith('invalid'))
    v4 = [-3.0, -2.8, -2.6, -2.4]; C4 = lambda vg, ig: {'vg_V': np.asarray(vg, float), 'ig_raw_A': np.asarray(ig, float), 'kcl_pass': np.ones(4)}
    i4 = [-1e-12, -1e-13, -1e-14, np.nan]
    case('S2-11: three resolved points plus a NaN point are invalid, never PASS (item 3)', 'R', lambda: M.mesh_core(C4(v4, i4), C4(v4, i4), 3.3e-18, True)['verdict'].startswith('invalid'))
    vn = [-3.0, -2.8, -2.6, np.nan]; i4f = [-1e-12, -1e-13, -1e-14, -1e-15]
    case('S2-11: a NaN V_G is invalid, never PASS (item 3)', 'R', lambda: M.mesh_core(C4(vn, i4f), C4(vn, i4f), 3.3e-18, True)['verdict'].startswith('invalid'))
    vd = np.array([0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]); isn = 1e-12 * vd; isn[4] = np.nan
    S1 = _st_strip(root, 'S1', 'run_9401', 'c10_s2_15_2p0', 2.0, vd, isn)
    case('strip: a NaN in the export is invalid, never a ratio verdict (item 3)', 'R', lambda: M.hb_ratio(S1)['verdict'].startswith('invalid'))
    # item 4: PROVISIONAL through every aggregate
    W1 = R('W1', 'run_9501', 'c10_s2_08_13p2', 13.2, np.minimum(10.0 ** (-6 + 3 * _GRID), 1e-6), lim=6.6e-13)
    W2 = R('W2', 'run_9502', 'c10_s1_02_13p2', 13.2, np.minimum(10.0 ** (-8 + 3 * _GRID), 1e-6), lim=6.6e-13)
    W3 = R('W3', 'run_0067', 'c10_s0_02_2p0', 2.0, np.maximum(idb(), 1e-14), ov=_GTO)
    W4 = R('W4', 'run_9504', 'c10_s0_01_2p0', 2.0, np.maximum(idb(), 1e-15))
    case('hc_worst: a verdict under the KCL PROXY carries PROVISIONAL (item 4)', 'R', lambda: M.hc_worst(W1, W2, W3, W4)['verdict'].startswith('PROVISIONAL'))
    case('hc_explains: a verdict under the KCL PROXY carries PROVISIONAL (item 4)', 'R', lambda: M.hc_explains(W1, W2)['verdict'].startswith('PROVISIONAL'))
    A1 = R('A1', 'run_9601', 'c10_aff_2p0_2p0', 2.0, idb(0.5 - 0.2816)); A2 = R('A2', 'run_9602', 'c10_s0_01_2p0', 2.0, idb(0.5))
    case('AFF: the registered shift verdict under the KCL PROXY carries PROVISIONAL (item 4)', 'R', lambda: M.aff(A1, A2)['shift_verdict'].startswith('PROVISIONAL'))
    case('hc_nominal and hc_generation verdicts under the KCL PROXY start with PROVISIONAL (item 4)', 'R',
         lambda: M.hc_nominal(N4)['verdict'].startswith('PROVISIONAL') and M.hc_generation(D2, D1)['verdict'].startswith('PROVISIONAL'))
    # item 5 and ruling b: mesh evidence bound to its runs and to the physical settings of the S2-11 pair (I_G ceiling from G1/G2, in scope)
    S0 = R('S0', 'run_0067', 'c10_s0_02_2p0', 2.0, idb(), i_g=igb, ov=_GTO)
    S11 = R('S11', 'run_9911', 'c10_s2_11_2p0', 2.0, idb(), i_g=igb, ov=_GTO + ox, deck=_st_deck(oxide=0.5))
    mesh = M.hc_mesh(S11, S0, None, None, RG, igj); mj = jw('mesh.json', mesh)
    case('S2-11 hc_mesh names its run pair, scope (QTNLSC, 2.0 nm) and file evidence (item 5)', 'R',
         lambda: mesh.get('verdict') == 'PASS' and mesh.get('scope', {}).get('mechanism') == 'QTNLSC' and mesh['scope'].get('thickness_nm') == 2.0
         and mesh['scope'].get('run_pair') == ['run_9911', 'run_0067'] and bool(mesh.get('evidence', {}).get('run', {}).get('sha256'))
         and mesh.get('intervention', {}).get('verified') is True)
    case('S2-11 hc_mesh on a self-pair (no refinement) is not demonstrated, never PASS (items 1, 5)', 'R', lambda: M.hc_mesh(S0, S0, None, None, RG, igj)['verdict'].startswith('not demonstrated'))
    M20 = R('M20', 'run_9920', 'c10_s2_04_2p0', 2.0, idb(), i_g=igb, ov=_GTO + [GT + 'set=nominal'])
    MW = R('MW', 'run_9924', 'c10_st_qtnlsc_worst_2p0', 2.0, idb(), i_g=igb, ov=_GTO)
    C20 = R('C20', 'run_9921', 'c10_s0_01_2p0', 2.0, idb())
    M13 = R('M13', 'run_9932', 'c10_s2_06_13p2', 13.2, idb(), i_g=igb, ov=_GTO + [GT + 'set=nominal'], lim=6.6e-13)
    C13 = R('C13', 'run_9933', 'c10_s1_02_13p2', 13.2, idb(), lim=6.6e-13)
    IT = R('IT', 'run_9922', 'c10_s2_12_2p0', 2.0, idb(), i_g=igb, ov=_GTO + [GT + 'set=nominal', 'solver.physics_options.oxide_tat.enabled=1'])
    case('S2-11 mesh evidence does not certify another film (13.2 nm QTNLSC run; item 5)', 'R', lambda: M.hc_explains(M13, C13, mj)['converged'] is not True)
    case('S2-11 (worst oxide set) does not certify a nominal-set 2.0 nm QTNLSC run such as S2-04 (ruling b)', 'R', lambda: M.hc_explains(M20, C20, mj)['converged'] is not True)
    case('S2-11 mesh evidence certifies a 2.0 nm QTNLSC run with the same physical settings (positive control)', 'P', lambda: M.hc_explains(MW, C20, mj)['converged'] is True)
    case('S2-11 mesh evidence never certifies ITAT (S2-12/S2-13; regression)', 'P', lambda: M.hc_explains(IT, C20, mj)['converged'] is None)
    # ruling c: application scope of a resolution (quantity, film, physical settings, bias range) and independence for upper-bound tests
    X13 = R('X13', 'run_9934', 'c10_st_x_13p2', 13.2, idb(), lim=6.6e-13)
    case('scope: a 2.0 nm resolution is not applied to a 13.2 nm run (no cross-film transfer; ruling c)', 'R', lambda: M.resolution([L(X13)], RD, dosj)[2] is False)
    case('scope: a resolution is not applied to a run with other physical settings (gate tunnelling on; ruling c)', 'R', lambda: M.resolution([L(S0)], RD, dosj)[2] is False)
    case('scope: an I_D-type resolution is not applied to the I_G quantity of S2-11 (ruling c)', 'R', lambda: M.hc_mesh(S11, S0, RD, dosj)['verdict'].startswith('PROVISIONAL'))
    case('scope: a pair containing the tested runs is no independent ceiling evidence for the generation upper-bound test (ruling c)', 'R',
         lambda: 'NOT a demonstrated' in str(M.hc_generation(D2, D1, RD, dosj)['resolution_source']))
    vt = _GRID[_GRID >= -1.0 - 1e-9]; it = np.minimum(10.0 ** (-9 + 4.0 * (vt - 0.5)), 1e-6)
    T1 = R('T1', 'run_9007', 'c10_st_dos_ref_2p0', 2.0, it, vg=vt, req=len(vt))
    T2 = R('T2', 'run_9008', 'c10_st_dos_x2_2p0', 2.0, np.where(it < 1e-18, 3 * it, it), vg=vt, req=len(vt), ov=dos2, deck=_st_deck(dos=2))
    tpj = jw('pair_trunc.json', M.resolution_pair(T2, T1))
    case('scope: a resolution from a pair compared on V_G >= -1 V is not applied to a run swept from -3 V (supported bias range; ruling c)', 'R',
         lambda: M.resolution([L(D1)], 1e-12, tpj)[2] is False)
    # fix 7: agreement support above the candidate and bias coverage (frozen: >= 3 agreeing points above R, one within 1 decade; coverage 1.0)
    V1 = R('V1', 'run_9701', 'c10_st_dos_ref_2p0', 2.0, np.full(len(_GRID), 1e-23))
    V2 = R('V2', 'run_9702', 'c10_st_dos_x2_2p0', 2.0, np.full(len(_GRID), 1e-21), ov=dos2, deck=_st_deck(dos=2))
    case('pair: an entirely disagreeing verified pair (1e-23 vs 1e-21 at every bias) demonstrates nothing (fix 7)', 'R',
         lambda: M.resolution([L(V1)], 1e-21, jw('pair_vac.json', M.resolution_pair(V2, V1)))[2] is False)
    ij = np.where(_GRID < 0, 1e-20, 1e-8)
    J1 = R('J1', 'run_9703', 'c10_st_dos_ref_2p0', 2.0, ij); J2 = R('J2', 'run_9704', 'c10_st_dos_x2_2p0', 2.0, np.where(_GRID < 0, 3e-20, 1e-8), ov=dos2, deck=_st_deck(dos=2))
    case('pair: agreement only 12 decades above the candidate (no support within 1 decade) demonstrates nothing (fix 7)', 'R',
         lambda: M.resolution([L(J1)], 1e-12, jw('pair_gap.json', M.resolution_pair(J2, J1)))[2] is False)
    vh = _GRID[::2]; K2 = R('K2', 'run_9706', 'c10_st_dos_x2_2p0', 2.0, i2[::2], vg=vh, req=len(vh), ov=dos2, deck=_st_deck(dos=2))
    case('pair: a pair comparing only half of the bias points (coverage 0.52 < 1) demonstrates nothing (fix 7)', 'R',
         lambda: M.resolution([L(D1)], 1e-12, jw('pair_half.json', M.resolution_pair(K2, D1)))[2] is False)
    # fix 8: refinement verified from the actual deck values and locations
    S11c = R('S11c', 'run_9913', 'c10_s2_11_2p0', 2.0, idb(), i_g=igb, ov=_GTO + ox, deck=_st_deck(oxide=2.0))
    case('intervention: overrides claim oxide x0.5 but the deck spacings coarsen x2 -> not a refinement, never a mesh pass (fix 8)', 'R',
         lambda: M.hc_mesh(S11c, S0, None, None, RG, igj)['verdict'].startswith('not demonstrated'))
    S11i = R('S11i', 'run_9914', 'c10_s2_11_2p0', 2.0, idb(), i_g=igb, ov=_GTO + ox, deck=_st_deck(oxide=0.5, iface=0.5))
    case('intervention: the y = 0 IWO interface line also changed -> not the claimed oxide-line intervention (fix 8)', 'R',
         lambda: M.hc_mesh(S11i, S0, None, None, RG, igj)['verdict'].startswith('not demonstrated'))
    D4 = R('D4', 'run_9009', 'c10_st_dos_x2_2p0', 2.0, i2, ov=dos2, deck=_st_deck(dos=4))
    case('intervention: overrides claim DOS x2 but the deck numa/numd are x4 -> not verified (fix 8)', 'R',
         lambda: M.resolution([L(D1)], 1e-12, jw('pair_dos4.json', M.resolution_pair(D4, D1)))[2] is False)
    # fix 6: KCL censoring reaches the floor metrics of hc_worst and hc_explains (13.2 nm limit 6.6e-13, 2.0 nm 4.61e-16)
    fl13, fl2 = np.full(len(_GRID), 1e-11), np.full(len(_GRID), 6.9e-15); ke = np.where(np.abs(_GRID + 2.0) < 1e-9, 0, 1)
    E1 = R('E1', 'run_9801', 'c10_s2_08_13p2', 13.2, np.where(ke == 0, 1e-1, fl13), kcl=ke, status='KCL_FAILED', lim=6.6e-13)
    E2 = R('E2', 'run_9802', 'c10_s1_02_13p2', 13.2, np.full(len(_GRID), 1e-13), lim=6.6e-13)
    E3 = R('E3', 'run_0067', 'c10_s0_02_2p0', 2.0, fl2, ov=_GTO); E4 = R('E4', 'run_9804', 'c10_s0_01_2p0', 2.0, np.full(len(_GRID), 1e-17))
    case('hc_worst: a flat curve with one KCL-failed endpoint raised ten decades is flat, never a PASS (fix 6, Codex counterexample)', 'R',
         lambda: 'PASS' not in M.hc_worst(E1, E2, E3, E4)['verdict'])
    vo = np.round(_GRID + 0.1, 6); kc = np.where(np.isin(np.round(_GRID, 6), [-2.0, -1.6, -1.2, -0.8]), 0, 1)
    F1 = R('F1', 'run_9811', 'c10_s2_08_13p2', 13.2, np.full(len(vo), 1e-11), vg=vo, lim=6.6e-13)
    F2 = R('F2', 'run_9812', 'c10_s1_02_13p2', 13.2, np.where(kc == 0, 1e-20, 9.9e-12), kcl=kc, status='KCL_FAILED', lim=6.6e-13)
    F3 = R('F3', 'run_0067', 'c10_s0_02_2p0', 2.0, np.full(len(_GRID), 1e-13), ov=_GTO); F4 = R('F4', 'run_9814', 'c10_s0_01_2p0', 2.0, np.full(len(_GRID), 1e-17))
    case('hc_worst: no control subtraction across KCL-censored control brackets; insufficient support -> unresolved, never PASS (fix 6)', 'R',
         lambda: M.hc_worst(F1, F2, F3, F4)['verdict'].split(': ', 1)[-1].startswith('unresolved'))
    H1 = R('H1', 'run_9821', 'c10_st_mech_2p0', 2.0, np.full(len(_GRID), 4.61e-15), kcl=np.where(np.abs(_GRID + 1.0) < 1e-9, 0, 1), status='KCL_FAILED')
    case('hc_explains: a KCL-censored window point leaves the 7.2 criteria unestablished -> unresolved, not "does not explain" (fix 6)', 'R',
         lambda: 'unresolved (insufficient support' in M.hc_explains(H1, E4)['verdict'])
    case('masked floor metrics equal post_run_checks.floor_metrics when nothing is censored (regression)', 'P',
         lambda: (lambda o, a, b: abs(o['flatness']['floor_slope_dec_per_V'] - a['floor_slope_dec_per_V']) < 1e-12
                  and abs(o['thickness_scaling']['d_floor_ratio_dec'][13.2] - a['d_floor_ratio_dec']) < 1e-12
                  and abs(o['thickness_scaling']['d_floor_ratio_dec'][2.0] - b['d_floor_ratio_dec']) < 1e-12)(
             M.hc_worst(W1, W2, W3, W4), M.pc.floor_metrics(Path(W1), 13.2, Path(W2)), M.pc.floor_metrics(Path(W3), 2.0, Path(W4))))
    S11b = R('S11b', 'run_9912', 'c10_s2_11_2p0', 2.0, idb(), i_g=igb, ov=_GTO + ox, deck=_st_deck(oxide=0.5))
    mj2 = jw('mesh_b.json', M.hc_mesh(S11b, S0, None, None, RG, igj))
    R('S11b', 'run_9912', 'c10_s2_11_2p0', 2.0, idb(), i_g=igb * np.where(np.arange(len(_GRID)) == 0, 1.001, 1.0), ov=_GTO + ox, deck=_st_deck(oxide=0.5))   # changed after scoring
    case('S2-11 mesh score whose run files changed after scoring is not taken as convergence (item 5)', 'R', lambda: M.hc_explains(MW, C20, mj2)['converged'] is not True)
    # round 3, fix 9: numerical-scope guard (target numerics must equal a pair endpoint; hc_mesh: or be a verified finer refinement of one)
    d11 = ['solver.dos_levels.numa=1', 'solver.dos_levels.numd=1']
    T11 = R('T11', 'run_9010', 'c10_st_dos_1_2p0', 2.0, idb(), ov=d11, deck=_st_deck(numa=1, numd=1))
    case('numerics: a DOS 384/192 vs 768/384 pair does not qualify a target run with DOS 1/1 (fix 9, Codex counterexample)', 'R', lambda: M.resolution([L(T11)], RD, dosj)[2] is False)
    N11 = R('N11', 'run_9205', 'c10_s2_04_2p0', 2.0, idb(), i_g=ign, ov=_GTO + d11, deck=_st_deck(numa=1, numd=1))
    case('numerics: hc_nominal (upper bound) on a DOS 1/1 run is not demonstrated by the 384/192 vs 768/384 I_G pair, never PASS (fix 9)', 'R',
         lambda: M.hc_nominal(N11, RG, igj)['verdict'].startswith('PROVISIONAL'))
    case('numerics: the floor-validity (ceiling) use in hc_explains on a DOS 1/1 run is not demonstrated (fix 9)', 'R',
         lambda: M.hc_explains(T11, D1, None, False, RD, dosj)['verdict'].startswith('PROVISIONAL'))
    igd = np.where(np.abs(igb) < 1e-19, 2 * igb, igb)
    GF1 = R('GF1', 'run_9111', 'c10_st_ig_m07_2p0', 2.0, idb(), i_g=igb, ov=_GTO + ['geometry.mesh.spacing_factor=0.7'], deck=_st_deck(mesh=0.7))
    GF2 = R('GF2', 'run_9112', 'c10_st_ig_m07_dos_2p0', 2.0, idb(), i_g=igd, ov=_GTO + ['geometry.mesh.spacing_factor=0.7'] + dos2, deck=_st_deck(mesh=0.7, dos=2))
    gfp = M.resolution_pair(GF2, GF1, 'ig_raw_A'); gfj = jw('pair_ig_m07.json', gfp)
    case('numerics: hc_mesh refuses an I_G pair made on a finer global mesh (target S2-11/S0-02 grids coarser than both endpoints; fix 9)', 'R',
         lambda: M.hc_mesh(S11, S0, None, None, gfp['candidate_resolution_A_per_um'], gfj)['verdict'].startswith('PROVISIONAL'))
    SD2 = R('SD2', 'run_9115', 'c10_st_s002_dos_2p0', 2.0, idb(), i_g=igd, ov=_GTO + dos2, deck=_st_deck(dos=2))
    sdp = M.resolution_pair(SD2, S0, 'ig_raw_A'); sdj = jw('pair_ig_s002_dos.json', sdp); RSD = sdp['candidate_resolution_A_per_um']
    S0u = R('S0u', 'run_9116', 'c10_s0_02_2p0', 2.0, idb(), i_g=igb, ov=_GTO, deck=_st_deck(iface=0.5))
    S11u = R('S11u', 'run_9917', 'c10_s2_11_2p0', 2.0, idb(), i_g=igb, ov=_GTO + ox, deck=_st_deck(oxide=0.5, iface=0.5))
    case('numerics: hc_mesh refuses a target grid that differs from the pair endpoints by an unverified change (y = 0 line, no override; fix 9)', 'R',
         lambda: M.hc_mesh(S11u, S0u, None, None, RSD, sdj)['verdict'].startswith('PROVISIONAL'))
    msd = M.hc_mesh(S11, S0, None, None, RSD, sdj)
    case('hc_mesh: a DOS pair sharing run_0067 with the S2-11 comparison is accepted via the verified refinement route, recorded as a shared baseline, never independent (round 3 ruling)', 'R',
         lambda: msd['verdict'] == 'PASS' and msd.get('resolution_pair_relation', {}).get('shared_baseline') == ['run_0067'] and msd['resolution_pair_relation'].get('independent') is False)
    exj_ = jw('pair_ig_exact.json', M.resolution_pair(S11, S0, 'ig_raw_A'))
    case('hc_mesh: the exact pair under test cannot provide its own resolution evidence (regression)', 'P',
         lambda: M.hc_mesh(S11, S0, None, None, json.loads(Path(exj_).read_text())['candidate_resolution_A_per_um'], exj_)['verdict'].startswith('PROVISIONAL'))
    # round 3, fix 10: componentwise refinement ('mixed' is never refinement evidence)
    dmx = ['solver.dos_levels.numa=768', 'solver.dos_levels.numd=96']
    DM = R('DM', 'run_9011', 'c10_st_dos_mixed_2p0', 2.0, i2, ov=dmx, deck=_st_deck(numa=768, numd=96))
    case('intervention: DOS 768/96 vs 384/192 (one grid finer, one coarser) is not a verified refinement and demonstrates nothing (fix 10)', 'R',
         lambda: M.resolution([L(D1)], 1e-12, jw('pair_dos_mixed.json', M.resolution_pair(DM, D1)))[2] is False)
    # round 3, fix 11: per-run (per-curve) resolution inputs
    gip = M.resolution_pair(G2, G1, 'id_A_per_um'); gij = jw('pair_id_gt.json', gip); RGI = gip['candidate_resolution_A_per_um']
    Mg = R('Mg', 'run_9951', 'c10_st_gen_mech_2p0', 2.0, idb(), i_g=igb, ov=_GTO); Cg = R('Cg', 'run_9952', 'c10_st_gen_ctrl_2p0', 2.0, idb())
    prg = {'run': (RGI, gij), 'control': (RD, dosj)}
    def cli_missing():
        o = M.OUT; M.OUT = root / 'out'
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                a = M.main(['hc_generation', Mg, Cg, '--resolution-run', repr(RGI), '--resolution-run-source', gij, '--smoke'])
                b = M.main(['hc_worst', W1, W2, Mg, Cg, '--resolution-run', '1e-18', '--resolution-run-source', dosj, '--resolution-control', '1e-18',
                            '--resolution-control-source', dosj, '--resolution-run-2p0', repr(RGI), '--resolution-run-2p0-source', gij, '--smoke'])
        finally: M.OUT = o
        return a == 2 and b == 2
    case('CLI: per-run resolution inputs with a role missing (hc_generation control; hc_worst control_2p0) exit 2 (fix 11)', 'R', cli_missing)
    case('per-run: hc_generation with its own in-scope independent pair for a gated mechanism and an ungated control is demonstrated (R_a + R_b; fix 11)', 'P',
         lambda: (lambda o: not o['verdict'].startswith('PROVISIONAL') and set(o['resolution_A_per_um']) == {'run', 'control'})(M.hc_generation(Mg, Cg, per_run=prg)))
    case('per-run: hc_explains with per-run in-scope pairs has non-PROVISIONAL floor criteria (fix 11)', 'P',
         lambda: not M.hc_explains(Mg, Cg, None, False, per_run=prg)['verdict'].startswith('PROVISIONAL'))
    Y1 = R('Y1', 'run_9961', 'c10_st_y_13p2', 13.2, idb(), lim=6.6e-13); Y2 = R('Y2', 'run_9962', 'c10_st_y_dos_13p2', 13.2, i2, ov=dos2, deck=_st_deck(dos=2), lim=6.6e-13)
    ypj = jw('pair_dos_13p2.json', M.resolution_pair(Y2, Y1)); RY = json.loads(Path(ypj).read_text())['candidate_resolution_A_per_um']
    case('per-run: hc_worst with four per-run in-scope pairs across two films is non-PROVISIONAL (fix 11)', 'P',
         lambda: not M.hc_worst(Y1, Y2, D1, D2, per_run={'run': (RY, ypj), 'control': (RY, ypj), 'run_2p0': (RD, dosj), 'control_2p0': (RD, dosj)})['verdict'].startswith('PROVISIONAL'))
    return res


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
    # amended 2026-10-12 (Codex item 1): the second clause used to assert that free text WITH a source is demonstrated; that is now the
    # rejection probe 'resolution: a free-text I_D source is not demonstrated' below, and the positive path is the qualified-pair case
    ok.append(('a resolution without a source is not demonstrated', resolution([{}], 1e-18, None)[2] is False))
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
    with tempfile.TemporaryDirectory() as tmp:   # Codex 2026-10-12 review cases (synthetic run directories in a temporary folder)
        ok += [(f'[{k}] {nm}' + (f'  ({err})' if err else ''), p) for nm, k, p, err in probes(sys.modules[__name__], tmp)]
    for nm, p in ok: print(('ok   ' if p else 'FAIL ') + nm)
    print(f'{sum(p for _, p in ok)}/{len(ok)} ok')
    return 0 if all(p for _, p in ok) else 1


def main(argv):
    if not argv or argv[0] in ('-h', '--help'): print(__doc__); return 2
    if argv[0] == 'selftest': return selftest()
    RF = {r: '--resolution-' + r.replace('_', '-') for r in ('run', 'control', 'run_2p0', 'control_2p0')}   # per-run inputs (round 3, fix 11)
    VAL = ('--resolution', '--resolution-source', '--resolution-ig', '--resolution-ig-source', '--mesh-score') + tuple(f for r in RF.values() for f in (r, r + '-source'))
    opt = {f: argv[argv.index(f) + 1] for f in VAL if f in argv}
    for a, b in (('--resolution', '--resolution-source'), ('--resolution-ig', '--resolution-ig-source')) + tuple((f, f + '-source') for f in RF.values()):
        if a in opt and not opt.get(b): print(f'{a} needs {b}: a demonstrated resolution states its source (register section 0)'); return 2
    smoke = '--smoke' in argv
    cmd = argv[0]
    per = {r: (_num(opt[f]), opt[f + '-source']) for r, f in RF.items() if f in opt}
    ROLES = {'hc_generation': ('run', 'control'), 'hc_explains': ('run', 'control'), 'hc_worst': ('run', 'control', 'run_2p0', 'control_2p0')}
    if per:
        need = ROLES.get(cmd, ())
        miss, extra = [r for r in need if r not in per], [r for r in per if r not in need]
        if not need or miss or extra or '--resolution' in opt:
            print(f'REFUSED (Codex round 3 fix 11; exit 2): per-run resolution inputs for {cmd} need exactly the roles {list(need)} '
                  f'(missing {miss}, not applicable {extra}) and no single --resolution'); return 2
    kw = {'given': _num(opt['--resolution']) if '--resolution' in opt else None, 'source': opt.get('--resolution-source'), 'strict': True}
    kpr = {'per_run': per or None}
    kig = {'ig_given': _num(opt['--resolution-ig']) if '--resolution-ig' in opt else None, 'ig_source': opt.get('--resolution-ig-source')}
    pos = [a for i, a in enumerate(argv[1:], 1) if not a.startswith('--') and argv[i - 1] not in VAL]
    try:
        if cmd == 'aff': r = aff(pos[0], pos[1], smoke=smoke, **kw)
        elif cmd == 'he_alloff': r = he_alloff(pos[0], pos[1], smoke)
        elif cmd == 's3_minus_s105': r = s3_minus_s105(pos[0], pos[1], smoke)
        elif cmd == 'hb_ratio': r = hb_ratio(pos[0], smoke=smoke, **kw)
        elif cmd == 'hb_transfer': r = hb_transfer(*[None if p == 'none' else p for p in pos[:3]], smoke=smoke, **kw)
        elif cmd == 'hc_nominal': r = hc_nominal(pos[0], smoke=smoke, strict=True, **kig)
        elif cmd == 'hc_generation': r = hc_generation(pos[0], pos[1], smoke=smoke, **kw, **kpr)
        elif cmd == 'hc_mesh': r = hc_mesh(pos[0], pos[1], smoke=smoke, **kw, **kig)
        elif cmd == 'hc_worst':
            if len(pos) < 4: print('hc_worst S2-08_RUN S1-02_RUN S0-02_RUN(run_0067) S0-01_RUN'); return 2
            r = hc_worst(*pos[:4], smoke=smoke, **kw, **kpr)
        elif cmd == 'hc_explains': r = hc_explains(pos[0], pos[1], opt.get('--mesh-score'), smoke, **kw, **kpr)
        elif cmd == 'resolution_pair': r = resolution_pair(pos[0], pos[1], *(pos[2:3] or []))
        else: print(__doc__); return 2
    except Refused as e:
        print(f'REFUSED (Codex 2026-10-12 item 1; exit 2): {e}'); return 2
    r = {'register_tag': TAG, 'scorer': 'analysis_2026-10-10_campaign/score_register.py', **r}
    OUT.mkdir(exist_ok=True)
    ids = '_'.join(x for x in [r.get(k) for k in ('run', 'ref', 'control', 'run_2p0', 'control_2p0')] if isinstance(x, str)) or '_'.join(str(v) for v in (r.get('runs') or {}).values())
    (OUT / (prefix(r['label']) + f'{cmd}_{ids}.json')).write_text(json.dumps(r, indent=1, default=float))
    print(json.dumps(r, indent=1, default=float)); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
