#!/usr/bin/env python3
"""C13, second part (CAMPAIGN_DESIGN.md 5.2, 5.4 and the S4/S5 rows and stop rules of section 6): the parts that profile_shared.py
discloses as missing. DRAFT v4 (2026-10-13), revised after Codex's reviews of 2026-10-13 ~01:55Z ("NO to freezing the current
profiling/H-F code. GO-WITH-CHANGES on the definitions": blocking fixes B1-B5, rulings A1-A10), ~03:10Z (v2: FIX_FIRST; fixes 1-3
here, fix 4 in hf_score_draft.py; rulings (a)-(f)) and the v3 review (FIX_FIRST; fix 2 and rulings (iii)-(iv) here, fix 1 in
hf_score_draft.py). All are listed below.
Written before any S4a launch. NO simulator call. Reads finished run directories (profile_shared.run_info and score_register.load /
run_problems, both unchanged) and the measured curves (campaign_extract.measured, unchanged; a fold reads its training films only);
writes only JSON files into analysis_2026-10-10_campaign/profile/ (prefix s4s5_) or into --out DIR. profile_shared.py is imported, never
edited (profile_films reproduces profile_shared.profile bit for bit for a triple launched at the anchor Q_f; test_profile_s4s5.py).

Design text implemented (quoted; CAMPAIGN_DESIGN.md line numbers as of 2026-10-13):
  C13 (l.481)  "Exact shift/scale profiling, surrogate for S4b, LOO selection, Jacobian. ... the S4b surrogate, S5 LOO selection and
               the Jacobian do not yet (needed only from S4b on)."
  S4b (l.276)  "6 candidates x 3 films from a quadratic surrogate of J (trust region half the S4a spacing)."
     matrix S4B-* purpose: "next candidate from a quadratic surrogate of the equal-film objective over the S4a archive (trust region =
               half the S4a spacing around the best). Stop early if 3 successive candidates improve by < 0.01 dec."; params_rule:
               "surrogate minimum of J over (Ns, WT[, GAMMA0]); Qf, mu_inf, ell re-profiled exactly".
  S4 (l.325)   "After S4a: if the best sqrt(J) > 0.30 dec (twice the acceptance) and the residuals are systematic (same-sign on-state
               error at 6.3 nm for >= 80 % of candidates), skip S4b. Run S4c on the best candidate, go to S5, and report the shared
               model as failed. No per-film rescue parameters, ever."
  S4 (l.326)   "S4b stops early when 3 successive candidates improve sqrt(J) by < 0.01 dec; the unused launches return to the reserve."
  S4c (l.69)   "The S4c tolerance is 0.01 dec, not 0.005" (S4C_TOL_DEC; the matrix S4C-* purpose text still says 0.005: documented
               mismatch, campaign_matrix.json is not edited here).
  5.2 (l.235)  "... every S4b candidate carries the profiled Q_f and MUN natively." (the S4B template carries {fit:Qf}, {fit:mu_band_*})
  S5 (l.279)   "3 folds x (4 adaptive training candidates x 2 training films + 2 frozen held-out predictions: best and runner-up).
               Branches are re-selected inside each fold."
  D6 (l.55)    "The S4a design was fixed before any data, so its archive is shared legitimately by all folds. Per fold: 4 adaptive
               candidates on the training films only, plus 2 frozen held-out predictions. S4b is excluded from LOO because it saw all
               films."
  S5 (l.330-332) "The S3 adoption rule is re-applied inside each fold, using the two training films' S3 results only (no launches). If
               a fold picks a different branch than the full data, its 8 training launches use that branch, and its candidates come
               from around the S3 start instead of the S4a archive." / "The held-out film is never tuned. The best-training candidate
               is the primary prediction; the runner-up only measures optimiser uncertainty." / "Any held-out film that fails 5.3
               falsifies transferability of this model form. That is reported, not repaired."
  5.4 (l.259-261) Jacobian in (log N_s, W_T[, GAMMA0], dV0, log mu_inf, ell); "A condition number above 100 or |corr| > 0.95 (ASSUMED
               thresholds) means a parameter *combination* is reported, not individual values."; S6 profiles re-profile exactly.
  5.3 (l.248-253) acceptance per film: active log-RMSE <= 0.15 dec; |dV_th,cc| <= 0.10 V; I_D(3 V) within +-30 %; SS (A1 normalised
               window) within +-20 %; mu_FE at 1.5, 2 and 3 V within +-20 %.
  5.2 (l.237-240) no extrapolation; J on covered window points only; coverage < 95 % -> flagged, confirm natively.

The surrogate only RANKS candidate parameter points. Every selected candidate is launched natively, its curves are re-profiled exactly
(profile_films), and that native, profiled sqrt(J) is the number that enters the archive, the stop rules and any report.

Codex blocking fixes (2026-10-13 ~01:55Z), as implemented:
  B1 Eligibility before fitting; non-fitted settings bound. load() keeps every eligibility fact of a run (score_register.run_problems,
     the C3 run-validity rule, with the transfer-profiling statuses PROFILE_STATUSES: status, return code, timeout, simulator error,
     completion banner, every requested point exported, finite, no duplicate bias point). An ineligible run (e.g. TIMEOUT run_0073) is a
     record WITHOUT a curve; profile_films refuses it before any fit; in an archive it makes its candidate UNKNOWN (never profiled, never
     a value). Inside one archive every non-fitted setting must be identical film by film WITH VALUES (overrides, material model and
     effective physics options, C_ox, tunnelling/Schottky options); only the launched coordinates (Nt_cm3.Nt2 = N_s, WTA_eV.value,
     mobility.gamma0) and the profiled values (Q_f, mu_band_fitted[t]) may differ. Two NC300 values cannot share an archive.
  B2 Fold loading and binding. The CLI loads only the training films' measured rows for loo_branch / loo_select (measured_training; the
     held-out rows are skipped before their currents are parsed); the functions refuse a measured set that contains the held-out film
     (Blind then wraps the training set). A fold needs the sealed branch decision of loo_branch for the same held-out film; the archive
     must carry the fold's branch. Freezing needs exactly four distinct fold candidates (A6). Each frozen record binds the decision
     sha256, the exact inventory (every S4a and fold candidate, its state and the content digests of its run files), the non-fitted
     settings, the mode (S4a archive / A7) and this file's sha256; it is sealed (sha256) and loo_score scores it only against the hash
     committed externally (--committed), so an edited and re-hashed record is refused.
  B3 Unknown results in the stopping rules. s4a_abort counts the complete S4a inventory (15): missing or invalid candidates are unknown,
     never given a sign or a J; ABORT needs both conditions established with every unknown counted against them; an unknown candidate may
     be the best, so any unknown keeps the abort UNRESOLVED unless an evaluated candidate already has sqrt(J) <= 0.30 (then NO ABORT) or
     the sign fraction cannot reach 80 % even with every unknown on the majority side. s4b_stop: an unresolved attempt has an unknown
     improvement and never helps establish "< 0.01 dec"; exhaustion of distinct points is an OPTIMIZER STALL, never three invented
     non-improvements.
  B4 (hf_score_draft.py) qualification(): a profile carries an acceptance only if valid, OK (not APPROXIMATE) and not at a range bound.
  B5 Jacobian: full numerical column rank (full SVD; omitted null directions are padded as zero singular values) is required before
     individual values may be reported; otherwise combinations are reported and individual values are UNRESOLVED.

Codex rulings 2026-10-13 on the ambiguities (as implemented):
  A1 trust box half-width = range/28 per dimension (half the S4a stratum width; no nn alternative, no later switching); the proposal is the
     lowest-ranked DISTINCT feasible point in the box (ranking: refined surrogate minimum, then grid points by surrogate value, ties by
     coordinates); distinct = ruling (a) below, against every archive candidate, unknown results included; none -> OPTIMIZER STALL.
  A2 the surrogate and "the best" use S4a plus the completed S4b candidates (no S4a-only alternative).
  A3 full quadratic in J (not sqrt J) by least squares; the design matrix must have full rank (and n >= p + 1), else refused. Fit and
     leave-one-out errors are diagnostics only.
  A4 improvement = running-best native sqrt(J) improvement; unresolved attempts do not establish < 0.01.
  A5 sign = mean signed on-window (1..3 V) log10 residual at 6.3 nm at each candidate's own optimum; complete S4a inventory; unknown
     potentially-best candidates prevent the abort conclusion.
  A6 S5: two-film J; pool = S4a + that fold's S5 candidates only; four distinct candidates, then distinct best / runner-up; no early
     freeze (--freeze-now removed).
  A7 branch re-selection enforced: a fold whose branch differs from the full data uses four REGISTERED local points around the S3 start of
     its branch (2-D box corners or 3-D tetrahedral points at the A1 half-width, clipped to the design ranges), ranked on training data
     only; eight training launches retained. This AMENDS the adaptive-generation rule: implemented but DRAFT - no fold launch and no frozen
     record without a logged register amendment and the user's go (loo_select needs --amendment REF to freeze in this mode).
  A8 frozen scales (design ranges) and neighbour variants (k = 2d, 2d + 2, all) kept with conservative flagging; rank deficiency ->
     combinations / UNRESOLVED; the launched columns are approximate archive derivatives (diagnostics, not confidence intervals).
  A9 S6: same-film comparisons; filling from the base only for a designated film-local perturbation (FILM_LOCAL: S6-23, the 6.3 nm NC300
     x1.467), explicitly labelled.
  A10 5.3 on a profiled curve: interpolation only inside the covered range, labelled; a native curve (S5 held-out scoring) keeps native
     sampling (mu_FE at 1.5 / 2 / 3 V and I_D(3 V) on native points, as campaign_extract; else unresolved). S4c tolerance 0.01 dec.
  Nuisance range: |dV0| <= 0.5 V is anchored to ONE baseline Q_f (QF_ANCHOR = the S0/S1 start value); a re-profiled launch (S4b at a
     profiled Q_f) gains no additional range.

Codex v2 review (2026-10-13 ~03:10Z), fixes as implemented:
  1 profile_films itself enforces one shared model (require_shared_model, also used by candidate()): same launched coordinates (Nt2 -> N_s,
     W_T, GAMMA0), branch, material model apart from Q_f / mu_band, shared overrides and tunnelling/Schottky options.
  2 every frozen record carries an INPUT-ONLY expected non-fitted signature of the held-out native run (expected_signature: the training
     runs' shared settings + the registered film-keyed inputs FILM_KEYED[held]), in the S4a and the A7 mode; loo_score always checks it.
  3 native_confirmation: a sealed record around the unchanged profile_shared.check with both endpoints' eligibility, the designated roles
     (S1-07 vs S0-01, S3-27 vs S3-12) and both digests; confirmation_status accepts it only for its role and its reference run.
Codex rulings (2026-10-13 ~03:10Z):
  (a) ASSUMED spending rule: a proposal / fold candidate is distinct iff its unit separation from every occupied point is >= 1/56 (h/2)
      AND its deck-rounded inputs (N_s 4 significant figures, W_T 1e-4 eV, GAMMA0 1e-3; make_campaign_matrix.py S4A) differ; equality to
      a registered A7 point is decided by the deck rounding alone.
  (b) a missing or UNKNOWN S4a candidate blocks the unconditional best / runner-up freeze (a conditional ranking is reported as a
      DIAGNOSTIC); a terminal ineligible candidate leaves the ranking only through a prospective, explicit exclusion record
      (--exclusions: rule, logged reference, ids) and the inventory stays complete.
  (c) KCL_FAILED stays excluded; other convergence flags remain visible (warnings), eligibility = the frozen C3 conditions.
  (d) A7: range/28 accepted; for two selected branches all four combined-branch points launch at the frozen original nuisance starts
      (Q_f 1.38345e12, mu_inf 100.005, ell 7.248) and are profiled on the training films only; eight training launches; no proposal
      without centre launch values. The A7 amendment is drafted separately (not logged).
  (e) (hf_score_draft.py) a valid evaluated confirmation FAIL counts as evaluated and cannot falsify; missing, timed-out or unevaluable is
      UNKNOWN.
  (f) bound-limited objective values are used in the search with warnings; they stay unqualified for acceptance, falsification, D1, D3d.

Codex v3 review (2026-10-13, FIX_FIRST), as implemented:
  fix 2 loo_score refuses a frozen record whose code_sha256 is missing or differs from this file's sha256 BEFORE scoring (no warning-only
     path; no migration route exists - a reviewed migration would need its own logged rule). The same rule applies to native-confirmation
     records: confirmation_status gives UNKNOWN (None) for a record made by other code.
  (i) an eligible but UNVERIFIED training profile keeps blocking the unconditional selection (intended; the conditional diagnostic stays).
  (iii) the S4c confirmation route is explicitly DISABLED (S4C_ROUTE_AVAILABLE = False; native_confirmation refuses role S4c): an
     execution gate until a wrapper binds the variable reference, the settings, both endpoints' eligibility and both digests.
  (iv) the IGZO expected held-out signature is tested on the registered S3-11/12/13 input decks with synthetic records (test_profile_s4s5.py
     cases_regressions_v4); no IGZO output is needed or read.

  python analysis_2026-10-10_campaign/profile_s4s5.py profile_n RUN [RUN ...] [--tag T] [--allow-approximate]   N-film (2 or 3) profile
  python analysis_2026-10-10_campaign/profile_s4s5.py surrogate ARCHIVE.json                                     S4a abort, S4b stop, next S4b candidate
  python analysis_2026-10-10_campaign/profile_s4s5.py loo_branch BRANCHES.json --held T                          sealed fold branch decision
  python analysis_2026-10-10_campaign/profile_s4s5.py loo_select ARCHIVE.json --held T --decision D.json [--amendment REF] [--exclusions X.json]
  python analysis_2026-10-10_campaign/profile_s4s5.py confirm NATIVE_RUN REFERENCE_RUN --role S1-07|S3-27           sealed native confirmation (S4c: disabled)
  python analysis_2026-10-10_campaign/profile_s4s5.py loo_score FROZEN.json NATIVE_RUN --committed SHA256         held-out 5.3 acceptance
  python analysis_2026-10-10_campaign/profile_s4s5.py jacobian ARCHIVE.json [--best ID]                          identifiability (5.4)
  python analysis_2026-10-10_campaign/profile_s4s5.py sensitivity RUN ... -- BASE ... [--fill-from-base]         S6 movement of the fitted values
  every command also takes --out DIR (default analysis_2026-10-10_campaign/profile). Exit codes: 0 done / PASS, 1 FAIL, 2 usage (also the
  removed options --trust, --s4a-only, --freeze-now), 3 refused, unresolved or awaiting a decision (A7).
ARCHIVE.json: {"candidates": [{"id": "S4A-01", "stage": "S4a"|"S4b"|"S5", "fold": 6.3 (S5 only), "runs": {"2.0": DIR, "6.3": DIR, "13.2": DIR}}]}
  (an S5 fold candidate lists its two training films only). Launched coordinates are read from each run's own files.
BRANCHES.json: {"base": {"2.0": DIR, ...}, "full_data_choice": [NAME, ...], "branches": [{"name": N, "group": "tail"|"mobility"|"contacts",
  "runs": {...}, "converged": true, "activation_ok": true, "pure_shift_or_scale": false}]}
"""
import csv
import hashlib
import itertools
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import campaign_tools as ct
import campaign_extract as ce
import profile_shared as ps
import score_register as sr   # unchanged (c0f28bb9): load / run_problems = the C3 run-validity rule

OUT = ps.OUT
Q = ps.Q
FILMS = (2.0, 6.3, 13.2)
DIMS = ('lNs', 'WT', 'g0')
RANGE = {'lNs': (12.0, 13.0), 'WT': (0.025, 0.060), 'g0': (-0.6, 0.6)}   # CAMPAIGN_DESIGN 4.3 = the S4a LHS map (make_campaign_matrix.py:388)
N_LHS = 14                                                                # S4a LHS points (qmc.LatinHypercube(...).random(14))
N_S4A = 15                                                                # S4a inventory: the start point + 14 LHS points (matrix "candidate k/15")
S4A_IDS = tuple(f'S4A-{k:02d}' for k in range(1, N_S4A + 1))
NUIS = ('dV0', 'lmu', 'ell')
SCALE = {'lNs': 1.0, 'WT': 0.035, 'g0': 1.2, 'dV0': 1.0, 'lmu': math.log10(300 / 10), 'ell': 50.0}   # design ranges (4.3), frozen (A8)
S4B_MAX, STOP_N, STOP_DEC = 6, 3, 0.01
ABORT_SQRTJ, ABORT_FRAC = 0.30, 0.80
LOO_N = 4
COND_MAX, CORR_MAX = 100.0, 0.95
ACC = {'rmse_dec': 0.15, 'dvth_V': 0.10, 'id3_pct': 30.0, 'ss_pct': 20.0, 'mufe_pct': 20.0}
MUFE_V = (1.5, 2.0, 3.0)
TINY = 1e-12
STARTS = np.linspace(-0.4, 0.4, 9)   # profile_shared.profile's dV0 starts (tests may use fewer)
DUP_SEP = 0.5 * 0.5 / N_LHS          # Codex ruling (a), ASSUMED spending rule: minimum normalised separation h/2 = 1/56 from every occupied point ...
DECK = {'lNs': lambda v: float(f'{10 ** v:.4g}'), 'WT': lambda v: round(float(v), 4), 'g0': lambda v: None if v is None else round(float(v), 3)}
#   ... plus distinct deck-rounded inputs (make_campaign_matrix.py S4A: N_s 4 significant figures, W_T 4 decimals (eV), GAMMA0 3 decimals);
#   the same deck rounding (not DUP_SEP) decides equality to a registered A7 point
FILM_KEYED = {2.0: ('solver.physics_options.nc300_override_cm3[2.0]=1.373e+19',), 6.3: (), 13.2: ()}
#   registered film-keyed inputs (CAMPAIGN_DESIGN D14; every matrix S4A-* entry): quasi-2D NC300 at 2.0 nm only; the input-only expected
#   signature of a held-out native run is built from the training runs' shared settings plus FILM_KEYED[held] (Codex v2 fix 2)
CONFIRM_ROLES = {'S1-07': {'native': ('c10_s1_07_2p0', 2.0), 'reference': ('c10_s0_01_2p0', 2.0)},
                 'S3-27': {'native': ('c10_s3_27_6p3', 6.3), 'reference': ('c10_s3_12_6p3', 6.3)}}   # designated endpoints (labels, film)
S4C_ROUTE_AVAILABLE = False          # Codex v3 ruling (iii): the S4c confirmation route is disabled (execution gate) until its wrapper is bound
QF_ANCHOR = 1.38345e12               # campaign_matrix shared_start_values Qf_cm2 (S0/S1 start, V2 anchor): the +-0.5 V nuisance range is anchored here
DV_RANGE_V = 0.5
START_X = {'lNs': math.log10(4e12), 'WT': 0.040, 'g0': None}              # S0-01 / S1-01 / S1-02 start parameters (shared_start_values)
START_LAW = {'mu_inf_cm2Vs': 100.005, 'ell_nm': 7.248}
START_BRANCH = {'tail_alpha': 1.0, 'nt_bulk_cm3': 0.0, 'mobility': 'constant', 'schottky_barrier_eV': None}
S4C_TOL_DEC = 0.01                   # CAMPAIGN_DESIGN l.69 (A10 ruling); campaign_matrix S4C-* purpose text says 0.005 (mismatch, documented)
PROFILE_STATUSES = ('REAL_ATLAS_SCORED', 'REAL_ATLAS_PREDICTION')   # complete transfer sweeps; KCL_FAILED has no pointwise censoring here
FIT_KEYS = (r'^traps\.fixed_interface_charge_Qf_cm2\.value$', r'^thickness_laws\.mu0_cm2Vs\.mu_band_fitted\[')       # profiled (S4B {fit:..})
COORD_KEYS = (r'^thickness_laws\.Nt_cm3\.Nt2$', r'^thickness_laws\.WTA_eV\.value$', r'^solver\.physics_options\.mobility\.gamma0$')   # launched
FILM_LOCAL = {'c10_s6_23_6p3': 6.3}  # A9: designated film-local S6 perturbation (6.3 nm quasi-2D NC300 x1.467); every other S6 input acts on all films
TEXT_KEY = re.compile(r'^(label|labels|note|notes)$|_label$')
A7_NOTE = ('A7 local design (Codex ruling 2026-10-13) AMENDS the S5 adaptive-generation rule: DRAFT until a logged register amendment and the '
           "user's go; no fold launch and no frozen record before that")
RULE_ELIG = ('score_register.run_problems (C3 run validity) with statuses ' + '/'.join(PROFILE_STATUSES) + '; read from the run files')
CODE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------ hashing / sealing
def _canon(d): return json.dumps(d, sort_keys=True, default=float, separators=(',', ':'))


def _sha(s): return hashlib.sha256(s.encode()).hexdigest()


def seal(d):
    """canonical JSON copy of d with its sha256 (records that are committed externally before use)"""
    d = json.loads(_canon({k: v for k, v in d.items() if k != 'sha256'})); d['sha256'] = _sha(_canon(d)); return d


def verify_seal(d, what):
    if not isinstance(d, dict) or d.get('sha256') != _sha(_canon({k: v for k, v in d.items() if k != 'sha256'})):
        raise SystemExit(f'refused: the {what} does not match its sha256 (edited after sealing)')
    return d


# ------------------------------------------------------------------------------------------------ runs, eligibility (B1)
def _sealed(run):
    s = str(run).replace('\\', '/')
    if '/sealed/' in s or s.startswith('sealed/') or 'results/sealed' in s:
        raise SystemExit(f'refused: {run} is under results/sealed (sealed outputs are never read by this tool)')


def file_digest(d):
    h = hashlib.sha256()
    for f in ('execution.json', 'material_model_used.json', 'terminal_currents.csv'):
        p = Path(d) / f; h.update(f.encode()); h.update(p.read_bytes() if p.is_file() else b'<missing>')
    return h.hexdigest()


def run_digest(r):
    """content digest of a run (files for a loaded run; curve and inputs for an in-memory one)"""
    if r.get('digest'): return r['digest']
    h = hashlib.sha256()
    for a in (r.get('vg'), r.get('i')): h.update(np.ascontiguousarray(a if a is not None else [], float).tobytes())
    h.update(_canon({k: r.get(k) for k in ('run_id', 't', 'qf', 'mu_band', 'cox', 'x', 'branch', 'overrides', 'breakers')}).encode())
    return h.hexdigest()


def eligibility(exj, cols):
    p = sr.run_problems(exj, cols, statuses=PROFILE_STATUSES); sc = exj.get('scan') or {}
    return {'eligible': not p, 'problems': p, 'status': exj.get('status'), 'returncode': exj.get('returncode'), 'timed_out': exj.get('timed_out'),
            'finished': sc.get('finished'), 'simulator_errors': len(sc.get('errors') or []), 'convergence_flags': len(sc.get('convergence_flags') or []),
            'requested_points': exj.get('requested_points'), 'exported_points': int(len(next(iter(cols.values())))) if cols else 0, 'rule': RULE_ELIG}


def _meta(d, exj):
    """run_info without a curve (ineligible run): the inputs needed to bind coordinates and settings"""
    t = float(exj['thickness_nm']); ov = list(exj.get('overrides', []))
    mf = d / 'material_model_used.json'; m = json.loads(mf.read_text()) if mf.is_file() else None
    p = ct.bd.material_at(m, t) if m is not None else {}
    _, g, s = ct.configs(ct.V3, [o for o in ov if o.startswith(('solver.', 'geometry.'))])
    po = s.get('physics_options') or {}
    breakers = [k for k in ('gate_tunnelling', 'oxide_tat', 'schottky_sd') if ct.bd.on((po.get(k) or {}).get('enabled'))]
    return dict(dir=d, run_id=exj.get('run_id'), t=t, vg=None, i=None, m=m, p=p, cox=ct.bd.cox(g), overrides=ov, breakers=breakers,
                mstar=p.get('mstar_m0'), mu_band=p.get('mu_band'), mun=p.get('mu0'), qf=p.get('Qf_cm2'))


def load(run):
    """B1: an ELIGIBLE run = profile_shared.run_info (unchanged); an ineligible one (timeout, simulator error, incomplete or non-finite
    export, status outside PROFILE_STATUSES) = a record without a curve. Both keep every eligibility fact, the label, the effective
    physics options and a content digest of the run files: nothing is lost on loading."""
    _sealed(run)
    try: d, exj, cols = sr.load(run)
    except FileNotFoundError as e: raise SystemExit(f'refused: {run} is not a run directory ({e})')
    el = eligibility(exj, cols)
    r = ps.run_info(run) if el['eligible'] else _meta(d, exj)
    _, _, s = ct.configs(ct.V3, [o for o in r['overrides'] if o.startswith(('solver.', 'geometry.'))])
    r['po'] = s.get('physics_options') or {}
    r.update(eligibility=el, label=exj.get('label'), digest=file_digest(d))
    return r


def is_eligible(r):
    el = r.get('eligibility'); return isinstance(el, dict) and el.get('eligible') is True


def require_eligible(R, what='profiling'):
    """B1: validated before any fit or acceptance; a run without an eligibility record is refused too"""
    bad = []
    for r in R:
        el = r.get('eligibility')
        if not isinstance(el, dict): bad.append(f'{r.get("run_id")}: no eligibility record (load runs through profile_s4s5.load)')
        elif el.get('eligible') is not True: bad.append(f'{r.get("run_id")}: ' + '; '.join(el.get('problems') or ['ineligible']))
    if bad: raise SystemExit(f'refused: run(s) not eligible for {what} (validated before fitting, Codex B1): ' + ' | '.join(bad))


def coords(r):
    """launched coordinates of a run from its own files: N_s = integrated tail of a 2.0 nm film = (Nt2 + nt_bulk) x 2 nm (equals the
    design N_s for the surface, bulk and 50:50 tails, which are normalised to the same total at 2.0 nm), W_T, GAMMA0 (IGZO only)"""
    if 'x' in r: return dict(r['x']), dict(r.get('branch', {}))
    if r.get('m') is None: raise SystemExit(f'refused: {r.get("run_id")}: no material model, the launched coordinates are unknown')
    L = r['m']['thickness_laws']; po = r.get('po') or {}
    nb = float(po.get('nt_bulk_cm3') or 0.0); ns = (float(L['Nt_cm3']['Nt2']) + nb) * 2e-7
    mob = po.get('mobility') or {}; igzo = str(mob.get('model', 'constant')).lower() == 'igzo_tokyo'
    sch = po.get('schottky_sd') or {}
    x = {'lNs': math.log10(ns) if ns > 0 else float('-inf'), 'WT': float(ct.bd.val(L['WTA_eV'])), 'g0': float(mob['gamma0']) if igzo else None}
    br = {'tail_alpha': float(L['Nt_cm3']['alpha']), 'nt_bulk_cm3': nb, 'mobility': 'igzo_tokyo' if igzo else 'constant',
          'schottky_barrier_eV': float(sch.get('barrier_eV')) if ct.bd.on(sch.get('enabled')) else None}
    return x, br


def at_start(r, mobility='constant', g0=None, rel=5e-4):
    """[] if the run is at the S1-01 start parameters (coordinates, branch, anchor Q_f and the start mu law) - with mobility='igzo_tokyo'
    and g0 the IGZO.TOKYO S3 seed instead - else the reasons"""
    x, b = coords(r); why = []
    if abs(x['lNs'] - START_X['lNs']) > 1e-6 or abs(x['WT'] - START_X['WT']) > 1e-9: why.append(f'coordinates {x} are not the start {START_X}')
    if (x['g0'] is None) != (g0 is None) or (g0 is not None and abs(x['g0'] - g0) > 1e-9): why.append(f'GAMMA0 {x["g0"]} (expected {g0})')
    exp_b = dict(START_BRANCH, mobility=mobility)
    if b != exp_b: why.append(f'branch {b} (expected {exp_b})')
    if r.get('qf') is None or abs(r['qf'] - QF_ANCHOR) > 1e-9 * QF_ANCHOR: why.append(f'Q_f {r.get("qf")} is not the anchor {QF_ANCHOR}')
    mb = ps.mu_law(START_LAW['mu_inf_cm2Vs'], START_LAW['ell_nm'], r['t'], r['mstar']) if r.get('mstar') else None
    if mb is None or r.get('mu_band') is None or abs(r['mu_band'] / mb - 1) > rel: why.append(f'mu_band {r.get("mu_band")} is not the start law {mb}')
    return why


def film_props(r, t):
    """(m*(t), roughness(t)) at any thickness from the run's material model (synthetic runs: r['props'](t))"""
    if 'props' in r: return r['props'](t)
    p = ct.bd.material_at(r['m'], t); return float(p['mstar_m0']), float(p['rough'])


# ------------------------------------------------------------------------------------------------ non-fitted settings (B1)
def _okey(o): return o.split('=', 1)[0]


def _matches(o, pats): return any(re.search(p, _okey(o)) for p in pats)


def fixed_overrides(r):
    """overrides with values, except the launched coordinates and the profiled values"""
    return sorted(o for o in (r.get('overrides') or []) if not _matches(o, FIT_KEYS + COORD_KEYS))


def shared_overrides(r):
    """fixed overrides that are not film-keyed ([t]): the same at every film"""
    return sorted(o for o in fixed_overrides(r) if not re.search(r'\[\d+(\.\d+)?\]$', _okey(o)))


def _strip_text(x):
    if isinstance(x, dict): return {k: _strip_text(v) for k, v in x.items() if not TEXT_KEY.search(str(k))}
    if isinstance(x, list): return [_strip_text(v) for v in x]
    return x


def fixed_model(r):
    """material model without the profiled inputs (profile_shared.strip_keys), the launched coordinates and free-text labels"""
    if r.get('m') is None: return None
    m = ps.strip_keys(r['m'], r['t']); L = m.get('thickness_laws') or {}
    if isinstance(L.get('Nt_cm3'), dict): L['Nt_cm3']['Nt2'] = None; L['Nt_cm3'].pop('Ns_cm2', None)
    if isinstance(L.get('WTA_eV'), dict): L['WTA_eV']['value'] = None
    return _strip_text(m)


def fixed_po(r):
    po = json.loads(json.dumps(r.get('po') or {}, default=str)); mob = po.get('mobility')
    if isinstance(mob, dict): mob.pop('gamma0', None)
    return po


def fixed_signature(r):
    sig = {'film_nm': float(r['t']), 'overrides': fixed_overrides(r), 'cox': f'{float(r["cox"]):.12e}', 'breakers': sorted(r.get('breakers') or []),
           'model_sha256': _sha(_canon(fixed_model(r))), 'physics_options_sha256': _sha(_canon(fixed_po(r)))}
    sig['sha256'] = _sha(_canon(sig)); return sig


def archive_settings(C, films=FILMS):
    """B1: film by film, every candidate of one archive carries the same non-fitted settings (with values); refused otherwise"""
    out = {}
    for t in films:
        groups = {}
        for c in C:
            for r in c['R']:
                if abs(r['t'] - t) < 1e-9: s = fixed_signature(r); groups.setdefault(s['sha256'], (s, []))[1].append(c['id'])
        if len(groups) > 1:
            (s1, a), (s2, b) = list(groups.values())[:2]
            dif = sorted(set(s1['overrides']) ^ set(s2['overrides'])); oth = [k for k in ('cox', 'breakers', 'model_sha256', 'physics_options_sha256') if s1[k] != s2[k]]
            raise SystemExit(f'refused: non-fitted settings differ between candidates at {t} nm (inside one archive only N_s, W_T, GAMMA0 and the '
                             f'profiled Q_f / mu_band may differ; Codex B1): {a[:3]} vs {b[:3]}; overrides {dif[:4]}; other {oth}')
        if groups: out[str(t)] = next(iter(groups))
    sh = {json.dumps(shared_overrides(r)) for c in C for r in c['R'] if any(abs(r['t'] - t) < 1e-9 for t in films)}
    if len(sh) > 1: raise SystemExit(f'refused: shared (not film-keyed) settings differ inside the archive: {sorted(sh)[:2]}')
    return {'per_film_sha256': out, 'shared_overrides': json.loads(next(iter(sh))) if sh else [], 'sha256': _sha(_canon(out))}


def require_shared_model(R, who='refused: the profiled runs are not one shared model (Codex v2 fix 1)'):
    """Codex v2 fix 1: the films of one profile / candidate are ONE shared model: same launched coordinates (N_s from Nt2, W_T, GAMMA0),
    branch, material model apart from Q_f / mu_band (profile_shared.strip_keys), shared (not film-keyed) overrides and tunnelling/Schottky
    options. Called by candidate() AND profile_films, so a direct caller cannot bypass it. Returns (coordinates, branch)."""
    xs = [coords(r) for r in R]; x0, b0 = xs[0]
    for (x, b), r in zip(xs[1:], R[1:]):
        if b != b0: raise SystemExit(f'{who}: branch differs between films ({b0} vs {b} at {r["t"]} nm)')
        for d in DIMS:
            if (x[d] is None) != (x0[d] is None) or (x[d] is not None and abs(x[d] - x0[d]) > 1e-6 * max(1.0, abs(x0[d]))):
                raise SystemExit(f'{who}: {d} differs between films ({x0[d]} vs {x[d]} at {r["t"]} nm)')
    if all(r.get('m') is not None for r in R):
        other = [d for r in R[1:] for d in ps.diff_dicts(ps.strip_keys(R[0]['m'], R[0]['t']), ps.strip_keys(r['m'], r['t']))]
        if other: raise SystemExit(f'{who}: material models differ beyond Q_f / mu_band: {other[:4]}')
    sh = [shared_overrides(r) for r in R]
    if any(s != sh[0] for s in sh[1:]): raise SystemExit(f'{who}: shared overrides differ between films: {sorted({o for s in sh for o in s} - set(sh[0]))[:4]}')
    if len({tuple(sorted(r.get('breakers') or [])) for r in R}) > 1: raise SystemExit(f'{who}: tunnelling/Schottky options differ between films')
    return x0, b0


def film_keyed(r):
    """the run's film-keyed non-fitted overrides ([t]), with values"""
    return sorted(o for o in fixed_overrides(r) if re.search(r'\[\d+(\.\d+)?\]$', _okey(o)))


def expected_signature(R_train, held):
    """Codex v2 fix 2: the INPUT-ONLY expected non-fitted signature of a native run at the held-out film, in every mode: the training runs'
    shared settings (overrides with values, material model, C_ox, tunnelling/Schottky options) plus the registered film-keyed inputs of
    the held film (FILM_KEYED); the effective physics options are recomputed from those overrides (campaign_tools.configs, as load).
    The training runs must carry exactly the registered film-keyed inputs of their own films."""
    bad = [f'{r.get("run_id")} at {r["t"]} nm: {film_keyed(r)} vs registered {sorted(FILM_KEYED.get(r["t"], ()))}' for r in R_train
           if film_keyed(r) != sorted(FILM_KEYED.get(r['t'], ()))]
    if bad: raise SystemExit('refused: training runs without the registered film-keyed inputs (FILM_KEYED): ' + ' | '.join(bad))
    require_shared_model(R_train, 'refused: the training runs are not one shared model')
    r0 = R_train[0]; ov = shared_overrides(r0) + list(FILM_KEYED[held])
    v = {'t': held, 'overrides': ov, 'cox': r0['cox'], 'breakers': list(r0.get('breakers') or []), 'm': r0.get('m')}
    if r0.get('m') is not None:
        _, _, s = ct.configs(ct.V3, [o for o in ov if o.startswith(('solver.', 'geometry.'))]); v['po'] = s.get('physics_options') or {}
    else: v['po'] = r0.get('po') or {}
    sig = fixed_signature(v); sig['built_from'] = {'training_runs': [r.get('run_id') for r in R_train], 'film_keyed_held': list(FILM_KEYED[held]),
                                                   'rule': 'input-only: training shared settings + FILM_KEYED[held] (Codex v2 fix 2)'}
    return sig


# ------------------------------------------------------------------------------------------------ candidates and archives
def candidate(c, loader=None):
    """{'id', 'stage', 'fold', 'R', 'x', 'branch', 'eligible', 'problems'}; the runs of one candidate must share every input except the
    film-specific ones (Q_f, C_ox, coordinates, branch, material model without Q_f / mu_band); an ineligible run makes the candidate
    UNKNOWN (B1), it is never dropped silently"""
    loader = loader or load
    vals = list(c['runs'].values()) if isinstance(c['runs'], dict) else list(c['runs'])
    R = [v if isinstance(v, dict) else loader(v) for v in vals]
    R.sort(key=lambda r: r['t'])
    if len({r['t'] for r in R}) != len(R): raise SystemExit(f'{c["id"]}: two runs of one film')
    q0 = R[0]['qf']
    if q0 is None or any(r['qf'] is None or abs(r['qf'] - q0) > 1e-9 * max(abs(q0), 1.0) for r in R): raise SystemExit(f'{c["id"]}: Q_f differs between films')
    if len({round(r['cox'], 15) for r in R}) > 1: raise SystemExit(f'{c["id"]}: C_ox differs between films')
    x0, b0 = require_shared_model(R, c['id'])
    probs =[f'{r.get("run_id")}: ' + '; '.join((r.get('eligibility') or {}).get('problems') or ['no eligibility record']) for r in R if not is_eligible(r)]
    return {'id': c['id'], 'stage': c.get('stage', 'S4a'), 'fold': c.get('fold'), 'R': R, 'x': x0, 'branch': b0, 'eligible': not probs, 'problems': probs}


def load_archive(path, loader=None):
    a = json.loads(Path(path).read_text()) if not isinstance(path, dict) else path
    C = [candidate(c, loader) for c in a['candidates']]
    if len({c['id'] for c in C}) != len(C): raise SystemExit('duplicate candidate ids in the archive')
    br = {json.dumps(c['branch'], sort_keys=True) for c in C}
    if len(br) > 1: raise SystemExit(f'archive mixes branches: {sorted(br)}')
    archive_settings(C)   # B1: non-fitted settings bound (with values), film by film
    return C


def dims_of(C):
    g = {c['x']['g0'] is None for c in C}
    if len(g) > 1: raise SystemExit('archive mixes IGZO (GAMMA0) and constant-mobility candidates')
    return ('lNs', 'WT') if g == {True} else DIMS


# ------------------------------------------------------------------------------------------------ measured curves
class Blind(dict):
    """measured curves of the training films only: any access to a held-out film raises (S5: the held-out film is never tuned)"""
    def __init__(self, info, films):
        super().__init__({t: v for t, v in info.items() if t in films}); self.hidden = sorted(set(FILMS) - set(films))

    def __missing__(self, k):
        raise PermissionError(f'held-out film {k} nm: its measured curve is not visible to this fold')


def measured_training(train):
    """B2: the fold's targets, loaded BEFORE Blind from the registered file, training films only: rows of any other film are skipped
    before their currents are parsed. vg / i / floor / sig_floor / ion as campaign_extract.measured (run_extraction.load_measured and
    floor_with_sigma, unchanged). No A1 SS window: it needs every film, and no acceptance is computed inside a fold."""
    train = sorted(float(t) for t in train); rows = {t: [] for t in train}
    with open(ce.rx.PKG / 'data' / 'experimental_clean.csv', newline='') as f:
        for r in csv.DictReader(f):
            k = next((t for t in train if abs(float(r['thickness_nm']) - t) < 1e-6), None)
            if k is not None: rows[k].append((float(r['vg_V']), float(r['id_A_per_um'])))
    info = {}
    for t in train:
        a = np.array(rows[t]); a = a[np.argsort(a[:, 0])]; vg, i = a[:, 0], a[:, 1]; fl, sfl = ce.rx.floor_with_sigma(vg, i)
        info[t] = dict(vg=vg, i=i, floor=fl, sig_floor=sfl, ion=float(i[-1]))
    return info


def _training_only(info, held):
    if any(abs(float(t) - held) < 1e-9 for t in info.keys()):
        raise SystemExit(f'refused: the measured set given to this fold contains the held-out film {held} nm; load the training films only '
                         '(measured_training) before Blind (Codex B2)')


# ------------------------------------------------------------------------------------------------ N-film exact profiling
def mean_signed_on(r, Mt, dQf, s):
    lt = ps.transformed_log(r, dQf, s, Mt['vg']); lm = np.log10(Mt['i'])
    on = (Mt['vg'] >= 1 - 1e-9) & (Mt['vg'] <= 3 + 1e-9) & np.isfinite(lt)
    return float(np.mean(lt[on] - lm[on])) if on.any() else None


def qualification(prof):
    """B4: why a profile cannot carry an acceptance or a falsification ([] = qualified): not valid (coverage < 95 % / optimizer), not OK
    (APPROXIMATE), or a profiled value at a range bound"""
    q = []
    if not prof.get('valid'): q.append(f'profile not valid ({prof.get("verdict")})')
    elif prof.get('verdict') != 'OK': q.append(f'profile {prof.get("verdict")} (not OK)')
    ab = (prof.get('profiled') or {}).get('at_bound') or {}
    if any(ab.values()): q.append('profiled value at a range bound: ' + ', '.join(k for k, v in ab.items() if v))
    return q


def profile_films(R, info, allow_approximate=False, starts=None, tag=None, qf_anchor=QF_ANCHOR):
    """profile_shared.profile generalised to 2 or 3 films (same objective, bounds, optimiser and starts). B1: every run must be eligible.
    The |dV0| <= 0.5 V range is anchored to qf_anchor (one baseline Q_f), not to the launched Q_f: a re-profiled launch gains no range. For
    a triple launched at the anchor the result equals profile_shared.profile exactly (test_profile_s4s5.py)."""
    ts = [r['t'] for r in R]
    if len(set(ts)) != len(ts) or len(ts) < 2: raise SystemExit('profile_films needs one run per film and at least two films')
    require_eligible(R)
    for t in ts: info[t]   # noqa: B018  (Blind raises here for a held-out film)
    q0 = R[0]['qf']
    if any(abs(r['qf'] - q0) > 1e-9 * max(abs(q0), 1.0) for r in R): raise SystemExit(f'refused: the runs do not share one Q_f ({[r["qf"] for r in R]})')
    if len({round(r['cox'], 15) for r in R}) > 1: raise SystemExit('refused: different C_ox in the set')
    require_shared_model(R)   # Codex v2 fix 1: no direct caller bypasses the shared-model consistency
    warn = []; brk = [f'{r["run_id"]}: {r["breakers"]}' for r in R if r.get('breakers')]
    cf = [f'{r.get("run_id")}: {r["eligibility"].get("convergence_flags")}' for r in R if (r.get('eligibility') or {}).get('convergence_flags')]
    if cf: warn.append(f'convergence flags present (visible; not an exclusion under the frozen C3 rule, Codex ruling (c)): {cf}')
    if brk and not allow_approximate: raise SystemExit(f'refused: tunnelling/Schottky option on, the shift/scale profiling is not exact: {brk}')
    if brk: warn.append(f'APPROXIMATE profiling (tunnelling/Schottky option on): {brk}; confirm natively before any adoption')
    sl = ((R[0].get('m') or {}).get('thickness_laws', {}).get('mu0_cm2Vs', {}).get('shared_law') or {})
    mu0, ell0 = float(sl.get('mu_inf_cm2Vs', 100.005)), float(sl.get('ell_nm', 7.248))
    terms0 = {}
    for r in R:
        Mt = info[r['t']]; w = ce.window_rmse(Mt['vg'], Mt['i'], Mt['floor'], r['vg'], r['i'])
        terms0[r['t']] = {'rmse_sub': w['sub']['rmse_dec'], 'rmse_on': w['on']['rmse_dec'], 'J_term': w['J_term']}
    J0 = float(np.mean([v['J_term'] for v in terms0.values()])) if all(v['J_term'] is not None for v in terms0.values()) else float('nan')
    cox = R[0]['cox']; dq_max = DV_RANGE_V * cox / Q; off = qf_anchor - q0   # bound: |q0 + dQf - anchor| <= dq_max

    def obj(x):
        dQf, lmu, ell = x[0] * 1e12, x[1], x[2]
        if abs(dQf - off) > dq_max or not (np.log(10) <= lmu <= np.log(300)) or not (0 <= ell <= 50): return 1e3
        J, _ = ps.triple_J(R, info, dQf, float(np.exp(lmu)), ell)
        return J if np.isfinite(J) else 1e3
    best = None
    for dv in (STARTS if starts is None else starts):
        r_ = minimize(obj, [off / 1e12 + dv * cox / Q / 1e12, np.log(mu0), ell0], method='Nelder-Mead', options={'xatol': 1e-6, 'fatol': 1e-10, 'maxiter': 4000})
        if best is None or r_.fun < best.fun: best = r_
    dQf, mu_inf, ell = best.x[0] * 1e12, float(np.exp(best.x[1])), float(best.x[2])
    J, per = ps.triple_J(R, info, dQf, mu_inf, ell)
    cov_ok = all(min(f['sub']['coverage'], f['on']['coverage']) >= 0.95 for f in per.values())
    at_bound = {'dV0': abs(abs(dQf - off) - dq_max) < 1e-3 * dq_max, 'mu_inf': min(abs(mu_inf - 10), abs(mu_inf - 300)) < 1e-3, 'ell': min(abs(ell), abs(ell - 50)) < 1e-3}
    res = {'tag': tag, 'films': ts, 'runs': [r['run_id'] for r in R], 'run_digests': [run_digest(r) for r in R], 'warnings': warn,
           'start': {'sqrtJ_dec': float(np.sqrt(J0)) if np.isfinite(J0) else None, 'per_film': terms0},
           'profiled': {'sqrtJ_dec': float(np.sqrt(J)) if np.isfinite(J) else None, 'J': float(J), 'Qf_cm2': q0 + dQf, 'dQf_cm2': dQf,
                        'dV0_V': -Q * dQf / cox, 'qf_anchor_cm2': qf_anchor, 'dV0_from_anchor_V': -Q * (q0 + dQf - qf_anchor) / cox,
                        'mu_inf_cm2Vs': mu_inf, 'ell_nm': ell, 'at_bound': at_bound,
                        'per_film': {str(t): {'rmse_sub_dec': f['sub']['rmse_dec'], 'rmse_on_dec': f['on']['rmse_dec'], 'coverage_sub': f['sub']['coverage'],
                                              'coverage_on': f['on']['coverage'], 'mun_scale': f['mun_scale'], 'J_term': f['J_term'],
                                              'mean_signed_on_dec': mean_signed_on(r, info[r['t']], dQf, f['mun_scale'])}
                                     for (t, f), r in zip(per.items(), R)},
                        'coverage_ok_95pct': cov_ok, 'optimizer': {'fun': float(best.fun), 'nit': int(best.nit), 'success': bool(best.success)}},
           'labels': ('APPROXIMATE (tunnelling/Schottky run) ' if brk else '') + 'Q_f, mu_inf, ell: FITTED (shared, exact-transformation profiling of '
                     'launched curves); calibration, not validation. dV0 range +-0.5 V anchored to one baseline Q_f.'}
    if not cov_ok: warn.append('window coverage < 95 %: confirm the optimum natively (CAMPAIGN_DESIGN 5.2)')
    if any(at_bound.values()): warn.append(f'profiled value at a range bound: {[k for k, v in at_bound.items() if v]}')
    ok = cov_ok and best.success and np.isfinite(J)
    res['valid'] = bool(ok)
    res['verdict'] = 'UNVERIFIED (coverage < 95 % or optimizer not converged: confirm natively)' if not ok else ('APPROXIMATE' if brk else 'OK')
    res['qualification'] = qualification(res); res['qualified'] = not res['qualification']
    return res


def nuisance_at(c, prof, films=FILMS):
    """the native launch values that carry a profile (S4b template {fit:Qf}, {fit:mu_band_*}; S5 frozen predictions): Q_f and, per film,
    mu_band = mu_inf (m_ref/m*(t)) / (1 + ell/t) and MUN = mu_band x roughness(t)"""
    p = prof['profiled']; r0 = c['R'][0]; out = {'Qf_cm2': p['Qf_cm2'], 'mu_inf_cm2Vs': p['mu_inf_cm2Vs'], 'ell_nm': p['ell_nm'], 'per_film': {}}
    for t in films:
        m, rough = film_props(r0, t); mb = ps.mu_law(p['mu_inf_cm2Vs'], p['ell_nm'], t, m)
        out['per_film'][str(t)] = {'mstar_m0': m, 'mu_band_cm2Vs': mb, 'MUN_cm2Vs': mb * rough,
                                   'overrides': [f'traps.fixed_interface_charge_Qf_cm2.value={p["Qf_cm2"]:.6g}',
                                                 f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{t}]={mb:.6g}']}
    return out


# ------------------------------------------------------------------------------------------------ S4b surrogate and stop rules
def unit(x, dims): return np.array([(x[d] - RANGE[d][0]) / (RANGE[d][1] - RANGE[d][0]) for d in dims], float)


def from_unit(u, dims): return {d: RANGE[d][0] + float(v) * (RANGE[d][1] - RANGE[d][0]) for d, v in zip(dims, u)}


def quad_design(U):
    U = np.atleast_2d(U); n, d = U.shape
    cols = [np.ones(n)] + [U[:, i] for i in range(d)] + [U[:, i] * U[:, j] for i in range(d) for j in range(i, d)]
    return np.column_stack(cols)


def fit_quadratic(U, y):
    """A3: full quadratic by least squares; 'full_rank' = numerical rank of the design matrix == number of terms and n >= p + 1"""
    X = quad_design(U); n, p = X.shape
    rank = int(np.linalg.matrix_rank(X))
    coef, _, _, sv = np.linalg.lstsq(X, y, rcond=None)
    yh = X @ coef; H = X @ np.linalg.pinv(X); h = np.clip(np.diag(H), 0, 1 - 1e-12)
    loo = (y - yh) / (1 - h)
    return {'coef': coef, 'n': int(n), 'p': int(p), 'rank': rank, 'full_rank': bool(rank == p and n >= p + 1),
            'rms_J': float(np.sqrt(np.mean((y - yh) ** 2))), 'loo_rms_J': float(np.sqrt(np.mean(loo ** 2))),
            'cond_X': float(sv[0] / sv[-1]) if sv.size and sv[-1] > 0 else float('inf'), 'note': 'fit and leave-one-out errors: diagnostics only (A3)'}


def trust_halfwidth(d, mode='stratum'):
    """A1 ruling: half the S4a LHS stratum width (range/28) in every dimension; no nn alternative and no later switching"""
    if mode != 'stratum': raise SystemExit(f'refused: trust mode {mode!r}: the trust region is fixed at half the S4a stratum width (Codex ruling A1)')
    return np.full(int(d), 0.5 / N_LHS)


def deck_inputs(x, dims):
    """the launched physical inputs as the deck writes them (DECK rounding of make_campaign_matrix.py)"""
    return tuple(DECK[d](x[d]) for d in dims)


def deck_point(x, dims):
    """x moved to its deck-rounded values (coordinates as the runs will report them)"""
    v = dict(zip(dims, deck_inputs(x, dims)))
    out = {'lNs': math.log10(v['lNs']), 'WT': v['WT'], 'g0': v.get('g0')}
    return out


def select_distinct(cands, occupied, tol, dims=None, occupied_deck=()):
    """A1 + Codex ruling (a): index of the lowest-ranked candidate whose unit distance to every occupied point (every archive candidate,
    unknown results included) is >= tol (DUP_SEP = 1/56) AND whose deck-rounded inputs differ from every occupied point's; None =
    exhaustion (optimizer stall)"""
    O = np.asarray(occupied, float); used = set(occupied_deck)
    for k, (_, u, _) in enumerate(cands):
        far = O.size == 0 or float(np.min(np.linalg.norm(O.reshape(len(O), -1) - u, axis=1))) >= tol - 1e-12
        if far and (dims is None or deck_inputs(from_unit(u, dims), dims) not in used): return k
    return None


def propose(pool, dims, key='sqrtJ', grid_n=None):
    """next candidate: the lowest-ranked distinct feasible point of the quadratic surrogate of J (= key^2) inside the A1 trust box around
    the best valid archive point. pool: [{'id', 'stage', 'x', key: native profiled value or None}] - every archive candidate, the ones
    without a value occupy their point. The surrogate value is a ranking device only."""
    pts = sorted([p for p in pool if p.get(key) is not None and np.isfinite(p[key])], key=lambda p: (p[key], str(p['id'])))
    d = len(dims); pq = 1 + d + d * (d + 1) // 2
    if len(pts) < pq + 1:
        return {'verdict': f'REFUSED: {len(pts)} archive points with a valid profile; a full quadratic in {d}-D has {pq} terms and needs at least {pq + 1} (A3)'}
    U = np.array([unit(p['x'], dims) for p in pts]); y = np.array([p[key] ** 2 for p in pts])
    fit = fit_quadratic(U, y); sfit = {k_: v for k_, v in fit.items() if k_ != 'coef'}
    if not fit['full_rank']:
        return {'verdict': f'REFUSED: the quadratic design matrix has rank {fit["rank"]} < {fit["p"]} terms (A3: full rank required; no proposal '
                           'from an underdetermined surrogate)', 'surrogate_fit': sfit}
    ub = U[0]; h = trust_halfwidth(d); lo, hi = np.clip(ub - h, 0, 1), np.clip(ub + h, 0, 1)
    g = grid_n or (41 if d <= 2 else 21)
    G = np.array(list(itertools.product(*[np.linspace(lo[i], hi[i], g) for i in range(d)])))
    qv = quad_design(G) @ fit['coef']
    order = np.lexsort(tuple(G[:, i] for i in reversed(range(d))) + (qv,))   # surrogate value, then coordinates (deterministic ties)
    k0 = int(order[0])
    r = minimize(lambda u: float((quad_design(u) @ fit["coef"])[0]), G[k0], method='L-BFGS-B', bounds=list(zip(lo, hi)))
    cands = ([(float(r.fun), np.clip(r.x, lo, hi), 'refined surrogate minimum')] if r.fun <= qv[k0] else []) + [(float(qv[i]), G[i], 'grid') for i in order]
    occ = [unit(p['x'], dims) for p in pool]; occ_deck = {deck_inputs(p['x'], dims) for p in pool}; tol = DUP_SEP
    out = {'centre': {'id': pts[0]['id'], key: float(pts[0][key])}, 'trust_mode': 'stratum (A1 ruling: half-width range/28, fixed)',
           'trust_halfwidth_unit': h.tolist(), 'trust_box': {dd: [from_unit(lo, dims)[dd], from_unit(hi, dims)[dd]] for dd in dims},
           'surrogate_fit': sfit, 'surrogate_coef_unit': fit['coef'].tolist(), 'distinct_tolerance_unit': tol, 'occupied_points': len(occ),
           'distinct_rule': ('ASSUMED spending rule (Codex ruling a): unit separation >= 1/56 (h/2) from every archive candidate AND distinct '
                             'deck-rounded inputs (N_s 4 significant figures, W_T 1e-4 eV, GAMMA0 1e-3)'),
           'labels': 'surrogate value = ranking device only; the candidate is launched natively and its re-profiled native sqrt(J) is the result'}
    k = select_distinct(cands, occ, tol, dims, occ_deck)
    if k is None:
        out['verdict'] = ('OPTIMIZER STALL: no distinct feasible point in the trust region (A1); reported as a stall, never as native '
                          'non-improvements'); return out
    f, u, how = cands[k]; dist = np.linalg.norm(np.array(occ) - u, axis=1); j = int(np.argmin(dist))
    out.update({'proposal': from_unit(u, dims), 'proposal_unit': [float(v) for v in u], 'surrogate_J_rank_only': f, 'selected_rank': int(k),
                'selected_how': how, 'nearest_archive_point': {'id': pool[j]['id'], 'unit_distance': float(dist[j])},
                'ranked_top5_rank_only': [{'x': from_unit(uu, dims), 'surrogate_J_rank_only': ff, 'how': hw} for ff, uu, hw in cands[:5]]})
    prop = out['proposal']
    out['proposal_natural'] = {'Ns_cm2': 10 ** prop['lNs'], 'WT_eV': prop['WT'], **({'gamma0': prop['g0']} if 'g0' in prop else {})}
    dk = dict(zip(dims, deck_inputs(prop, dims)))
    out['proposal_deck'] = {'Ns_cm2': dk['lNs'], 'WT_eV': dk['WT'], **({'gamma0': dk['g0']} if 'g0' in dk else {}), 'label': 'deck-rounded launch inputs'}
    out['verdict'] = 'PROPOSAL (launch natively, then re-profile)'
    return out


def s4b_stop(sqrtJ_s4a_best, s4b_sqrtJ):
    """A4 + B3: running-best native improvements of the S4b candidates in launch order; an unresolved attempt has an UNKNOWN improvement
    (None) and never helps establish the stop; STOP when the last 3 attempts are all resolved and < 0.01 dec"""
    best = sqrtJ_s4a_best; imp = []
    for v in s4b_sqrtJ:
        if v is None or not np.isfinite(v): imp.append(None); continue
        imp.append(max(0.0, best - v)); best = min(best, v)
    last = imp[-STOP_N:]
    stop = len(imp) >= STOP_N and all(x is not None and x < STOP_DEC for x in last)
    left = S4B_MAX - len(s4b_sqrtJ); unk = [k + 1 for k, x in enumerate(imp) if x is None]
    v = ('STOP: 3 successive resolved candidates improved sqrt(J) by < 0.01 dec; unused launches return to the reserve' if stop else
         'DONE: 6 S4b candidates used' if left <= 0 else
         'CONTINUE (the stop is not established: unresolved attempt(s) among the last three)' if len(imp) >= STOP_N and any(x is None for x in last) else
         'CONTINUE')
    return {'improvements_dec': imp, 'unresolved_attempts': unk, 'best_sqrtJ_dec': best, 'launched': len(s4b_sqrtJ), 'remaining': max(0, left), 'verdict': v}


def s4a_abort(profiles, n_expected=N_S4A):
    """CAMPAIGN_DESIGN l.325 (A5 + B3): best sqrt(J) > 0.30 dec AND >= 80 % of the S4a candidates (the complete inventory, n_expected)
    with the same sign of the mean on-state residual at 6.3 nm. Missing and invalid candidates are unknown: never a sign, never a J."""
    n = len(profiles)
    if n > n_expected: raise SystemExit(f'refused: {n} S4a profiles for an inventory of {n_expected}')
    v = [p for p in profiles if p.get('valid')]; n_inv = n - len(v); n_miss = n_expected - n; unknown = n_inv + n_miss
    sg = [p['profiled']['per_film'].get('6.3', {}).get('mean_signed_on_dec') for p in v]
    pos, neg = sum(s is not None and s > 0 for s in sg), sum(s is not None and s < 0 for s in sg); unk_sign = unknown + sum(s is None for s in sg)
    best = min((p['profiled']['sqrtJ_dec'] for p in v), default=None)
    lo, hi = max(pos, neg) / n_expected, (max(pos, neg) + unk_sign) / n_expected
    c_best = ('no' if best is not None and best <= ABORT_SQRTJ else 'unresolved' if unknown or best is None else 'yes')
    c_sign = 'yes' if lo >= ABORT_FRAC - TINY else 'no' if hi < ABORT_FRAC - TINY else 'unresolved'
    if 'no' in (c_best, c_sign): verdict = 'NO ABORT: S4b may proceed'
    elif c_best == c_sign == 'yes': verdict = 'ABORT S4b: run S4c on the best candidate, go to S5, report the shared model as failed (no per-film rescue parameters)'
    else: verdict = (f'UNRESOLVED (abort not established: {unknown} unknown S4a result(s) - an unknown candidate may be the best or change the sign '
                     'fraction; A5). S4b is not skipped on this basis and the shared model is not reported as failed')
    return {'best_sqrtJ_dec_evaluated': best, 'best_sqrtJ_dec': best, 'n_expected': n_expected, 'n_valid': len(v), 'n_invalid': n_inv, 'n_missing': n_miss,
            'on_6p3_sign_counts': {'positive': pos, 'negative': neg, 'unknown': unk_sign}, 'same_sign_fraction': lo, 'same_sign_fraction_upper': hi,
            'conditions': {'best_above_0p30': c_best, 'same_sign_80pct': c_sign}, 'verdict': verdict}


_CACHE = {}


def _fingerprint(R, info):
    h = hashlib.sha256()
    for r in R:
        Mt = info[r['t']]
        for a in (r['vg'], r['i'], Mt['vg'], Mt['i']): h.update(np.ascontiguousarray(a, float).tobytes())
        h.update(repr((r['t'], r['qf'], r['mu_band'], r['mstar'], r['cox'], tuple(r.get('breakers') or ()), Mt['floor'])).encode())
    h.update(np.asarray(STARTS, float).tobytes()); return h.hexdigest()


def profile_pool(C, info, films=None, allow_approximate=False):
    """profile every candidate on the given films (cached by content); a candidate with an ineligible run on those films is UNKNOWN
    (validated before fitting, B1), never profiled"""
    out = []
    for c in C:
        R = [r for r in c['R'] if films is None or r['t'] in films]
        if films is not None and sorted(r['t'] for r in R) != sorted(films):
            out.append((c, None, f'{c["id"]}: films {[r["t"] for r in c["R"]]} do not cover {sorted(films)}')); continue
        bad = [r for r in R if not is_eligible(r)]
        if bad:
            out.append((c, None, 'UNKNOWN (ineligible run, validated before fitting): ' + ' | '.join(
                f'{r.get("run_id")}: ' + '; '.join((r.get('eligibility') or {}).get('problems') or ['no eligibility record']) for r in bad))); continue
        key = (_fingerprint(R, info), bool(allow_approximate))
        if key not in _CACHE:
            try: _CACHE[key] = (profile_films(R, info, allow_approximate), None)
            except SystemExit as e: _CACHE[key] = (None, f'{c["id"]}: {e}')
        p, err = _CACHE[key]; out.append((c, p, err))
    return out


def _state(p, err):
    if p is None: return err if str(err).startswith('UNKNOWN') else f'REFUSED: {err}'
    return 'valid' if p['valid'] else f'invalid profile: {p["verdict"]}'


def _bounds(p):
    return [k for k, v in ((p or {}).get('profiled') or {}).get('at_bound', {}).items() if v] if p else []


def _bound_warn(rows, key):
    b = [f'{r["id"]}: {r["bound_limited"]}' for r in rows if r.get('bound_limited') and r.get(key) is not None]
    return ([f'bound-limited objective values used in the search (Codex ruling f; unqualified for acceptance, falsification, D1 and D3d): {b}']
            if b else [])


def surrogate(C, info, allow_approximate=False):
    for c in C:
        if c['stage'] not in ('S4a', 'S4b'): raise SystemExit(f'{c["id"]}: stage {c["stage"]} is not part of the S4 archive')
        if sorted(r['t'] for r in c['R']) != list(FILMS): raise SystemExit(f'{c["id"]}: an S4 candidate needs all three films')
    ids4a = [c['id'] for c in C if c['stage'] == 'S4a']; odd = [i for i in ids4a if i not in S4A_IDS]
    if odd: raise SystemExit(f'refused: S4a ids outside the registered inventory {S4A_IDS[0]}..{S4A_IDS[-1]}: {odd}')
    dims = dims_of(C); settings = archive_settings(C); PP = profile_pool(C, info, allow_approximate=allow_approximate)
    rows = [{'id': c['id'], 'stage': c['stage'], 'x': c['x'], 'sqrtJ': p['profiled']['sqrtJ_dec'] if p and p['valid'] else None,
             'bound_limited': _bounds(p), 'state': _state(p, err), 'run_digests': [run_digest(r) for r in c['R']]} for c, p, err in PP]
    s4a = [(c, p) for c, p, _ in PP if c['stage'] == 'S4a']; s4b = sorted([(c, p) for c, p, _ in PP if c['stage'] == 'S4b'], key=lambda z: z[0]['id'])
    res = {'dims': list(dims), 'archive_settings': settings, 'archive': rows, 'n_S4a': len(s4a), 'n_S4b': len(s4b),
           'S4a_missing': [i for i in S4A_IDS if i not in ids4a], 'code_sha256': CODE_SHA, 'warnings': _bound_warn(rows, 'sqrtJ')}
    res['s4a_abort'] = s4a_abort([p if p is not None else {'valid': False} for _, p in s4a], N_S4A)
    best4a = min((r['sqrtJ'] for r in rows if r['stage'] == 'S4a' and r['sqrtJ'] is not None), default=None)
    if best4a is None: res['verdict'] = 'UNRESOLVED: no valid S4a profile'; return res
    res['s4b_stop'] = s4b_stop(best4a, [p['profiled']['sqrtJ_dec'] if p and p['valid'] else None for _, p in s4b])
    if res['s4a_abort']['verdict'].startswith('ABORT') and not s4b:
        res['verdict'] = res['s4a_abort']['verdict']; return res
    if not res['s4b_stop']['verdict'].startswith('CONTINUE'):
        res['verdict'] = res['s4b_stop']['verdict']; return res
    prop = propose(rows, dims, 'sqrtJ')
    res['proposal'] = prop
    if prop['verdict'].startswith('OPTIMIZER STALL'):
        res['verdict'] = ('STOP S4b: OPTIMIZER STALL (no distinct feasible point in the trust region; A1). Unused launches return to the reserve; '
                          'not counted as native non-improvements'); return res
    if 'centre' in prop:
        cc, pc = next((c, p) for c, p, _ in PP if c['id'] == prop['centre']['id'])
        res['native_launch_values'] = nuisance_at(cc, pc)
        res['native_launch_values']['note'] = ('S4B template: {fit:Qf} and {fit:mu_band_*} = the profiled values at the trust-region centre '
                                               '(CAMPAIGN_DESIGN 5.2 l.235); the new curves are re-profiled exactly afterwards (range anchored)')
    res['verdict'] = prop['verdict'] + ('' if not res['s4a_abort']['verdict'].startswith('UNRESOLVED') else ' [S4a abort UNRESOLVED: see s4a_abort]')
    return res


# ------------------------------------------------------------------------------------------------ S5 leave-one-film-out
def adopt_films(branch_R, base_R, info, allow_approximate=False):
    """S3 adoption arithmetic on the films of the runs given (two training films inside a fold): sqrt(J) gain >= 0.03 dec and no
    film's RMSE_sub / RMSE_on worse by > 0.03 dec (profile_shared.adopt, generalised to N films)"""
    a, b = profile_films(branch_R, info, allow_approximate), profile_films(base_R, info, allow_approximate)
    gain = b['profiled']['sqrtJ_dec'] - a['profiled']['sqrtJ_dec']
    worse = {t: {k: a['profiled']['per_film'][t][k] - b['profiled']['per_film'][t][k] for k in ('rmse_sub_dec', 'rmse_on_dec')} for t in a['profiled']['per_film']}
    ok = gain >= 0.03 and all(v <= 0.03 for dd in worse.values() for v in dd.values())
    pre = 'UNVERIFIED: ' if 'UNVERIFIED' in a['verdict'] + b['verdict'] else 'APPROXIMATE: ' if 'APPROXIMATE' in (a['verdict'], b['verdict']) else ''
    return {'branch': a, 'base': b, 'sqrtJ_gain_dec': gain, 'per_film_worsening_dec': worse, 'arithmetic_pass': bool(ok and not pre.startswith('UNVERIFIED')),
            'verdict': pre + ('ARITHMETIC PASS' if ok else 'ARITHMETIC FAIL')}


def _nuis(prof):
    p = prof['profiled']; return {'Qf_cm2': p['Qf_cm2'], 'mu_inf_cm2Vs': p['mu_inf_cm2Vs'], 'ell_nm': p['ell_nm'], 'dV0_from_anchor_V': p['dV0_from_anchor_V'],
                                  'sqrtJ_train_dec': p['sqrtJ_dec'], 'verdict': prof['verdict']}


def loo_branch(spec, held, info, loader=None):
    """S5 l.330: the S3 adoption rule re-applied on the two training films (training-only measured set, B2); groups: lowest training sqrt(J)
    among the passing members; at most two; IGZO and Schottky both passing -> the larger gain. Returns the SEALED fold decision (bound into
    every frozen record of the fold): choice, fold branch, full-data branch, the S3 centre of the fold's branch and its launch values."""
    loader = loader or load
    train = [t for t in FILMS if t != held]; _training_only(info, held); I = Blind(info, train)
    def sel(runs): return sorted([v if isinstance(v, dict) else loader(v) for k, v in runs.items() if float(k) in train], key=lambda r: r['t'])
    base = sel(spec['base'])
    if [r['t'] for r in base] != train: raise SystemExit(f'refused: the base runs do not cover the training films {train}')
    bprof = profile_films(base, I)
    rows, runs_of, prof_of = [], {}, {}
    for b in spec['branches']:
        R = sel(b['runs']); runs_of[b['name']] = R
        rr = [{'run_id': r.get('run_id'), 'film_nm': r['t'], 'digest': run_digest(r)} for r in R]
        try: a = adopt_films(R, base, I, allow_approximate=b.get('group') == 'contacts')
        except SystemExit as e: rows.append({'name': b['name'], 'group': b.get('group'), 'runs': rr, 'verdict': f'REFUSED: {e}', 'adopted_candidate': False}); continue
        prof_of[b['name']] = a['branch']
        flags = {k: b.get(k) for k in ('converged', 'activation_ok', 'pure_shift_or_scale')}
        okf = flags['converged'] is True and flags['activation_ok'] is True and flags['pure_shift_or_scale'] is False
        rows.append({'name': b['name'], 'group': b.get('group'), 'runs': rr, 'gain_dec': a['sqrtJ_gain_dec'], 'sqrtJ_dec': a['branch']['profiled']['sqrtJ_dec'],
                     'worsening_dec': a['per_film_worsening_dec'], 'arithmetic': a['verdict'], 'caller_flags': flags,
                     'adopted_candidate': bool(a['arithmetic_pass'] and okf)})
    chosen = {}
    for r in rows:
        if r['adopted_candidate'] and (r['group'] not in chosen or r['sqrtJ_dec'] < chosen[r['group']]['sqrtJ_dec']): chosen[r['group']] = r
    if 'mobility' in chosen and 'contacts' in chosen:
        drop = 'contacts' if chosen['mobility']['gain_dec'] >= chosen['contacts']['gain_dec'] else 'mobility'; chosen.pop(drop)
    pick = sorted(chosen.values(), key=lambda r: -r['gain_dec'])[:2]
    fold = sorted(r['name'] for r in pick); full = sorted(spec.get('full_data_choice') or [])
    miss = [n for n in full if n not in runs_of]
    if miss: raise SystemExit(f'refused: the full-data choice names branches without runs in the spec: {miss}')
    xb, bb = coords(base[0])
    def merged(names):
        out = dict(bb)
        for n in names: out.update({k: v for k, v in coords(runs_of[n][0])[1].items() if v != bb.get(k)})
        return out
    xc = dict(xb)
    for n in fold:
        xn, bn = coords(runs_of[n][0])
        if bn.get('mobility') != bb.get('mobility'): xc['g0'] = xn['g0']
    if len(fold) <= 1:
        cprof = bprof if not fold else prof_of[fold[0]]; cruns = base if not fold else runs_of[fold[0]]
        csrc = 'two-film profile of the ' + ('base' if not fold else f'{fold[0]} S3') + ' runs on the training films'
    else:   # Codex ruling (d): two selected branches -> the frozen original nuisance starts for all four combined-branch points
        cprof = {'profiled': {'Qf_cm2': QF_ANCHOR, 'mu_inf_cm2Vs': START_LAW['mu_inf_cm2Vs'], 'ell_nm': START_LAW['ell_nm'], 'dV0_from_anchor_V': 0.0,
                              'sqrtJ_dec': None}, 'verdict': 'frozen original starts (not a profile)'}
        cruns = base; csrc = 'frozen original nuisance starts (Q_f 1.38345e12, mu_inf 100.005, ell 7.248; Codex ruling d), training films only'
    same = fold == full
    res = {'record': 'S5 fold branch decision (CAMPAIGN_DESIGN l.330); bound into every frozen record of the fold (Codex B2)',
           'held_out_nm': held, 'training_films': train, 'blind': f'measured curves visible: {train}; hidden: {I.hidden}',
           'base_runs': [{'run_id': r.get('run_id'), 'film_nm': r['t'], 'digest': run_digest(r)} for r in base], 'base_profile': _nuis(bprof),
           'branches': rows, 'fold_choice': fold, 'full_data_choice': full, 'same_as_full_data': same,
           'fold_branch': merged(fold), 'full_data_branch': merged(full), 'centre_x': xc,
           'centre_profile': _nuis(cprof), 'centre_source': csrc,
           'centre_launch_values': nuisance_at({'R': cruns}, cprof, films=train), 'code_sha256': CODE_SHA,
           'verdict': ('SAME BRANCH CHOICE as the full data: the fold uses the S4a archive' if same else
                       'DIFFERENT BRANCH CHOICE: the fold uses its own branch with the A7 local design (four registered S3-centred points); ' + A7_NOTE)}
    return seal(res)


def a7_points(dec):
    """A7 (Codex ruling 2026-10-13; DRAFT, see A7_NOTE): the four registered local points of a changed-branch fold around the S3 start of
    its branch (centre_x of the sealed decision): 2-D box corners or 3-D tetrahedral points at the A1 half-width, clipped to the design ranges"""
    xc = dec['centre_x']; dims = ('lNs', 'WT') if xc.get('g0') is None else DIMS; d = len(dims); h = float(trust_halfwidth(d)[0]); uc = unit(xc, dims)
    S = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if d == 2 else [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    U = [np.clip(uc + h * np.array(s, float), 0, 1) for s in S]
    pts = [deck_point(dict(from_unit(u, dims), **({'g0': None} if d == 2 else {})), dims) for u in U]   # registered as deck-rounded inputs
    if len({deck_inputs(x, dims) for x in pts}) < 4 or min(float(np.linalg.norm(unit(a, dims) - unit(b, dims))) for a, b in itertools.combinations(pts, 2)) < DUP_SEP:
        raise SystemExit('refused: the A7 points are not distinct after clipping to the design ranges (decision needed)')
    return dims, pts


def _distinct_pair(a, b, dims):
    """Codex ruling (a): unit separation >= 1/56 AND distinct deck-rounded inputs"""
    return float(np.linalg.norm(unit(a, dims) - unit(b, dims))) >= DUP_SEP - 1e-12 and deck_inputs(a, dims) != deck_inputs(b, dims)


def _exclusions(ex, rows):
    """Codex ruling (b): a terminal ineligible S4a candidate leaves the ranking only through a prospective, explicit exclusion record
    {'rule': text, 'ref': logged reference, 'ids': [...]} naming candidates that ARE in the inventory and are UNKNOWN by ineligibility"""
    if not ex: return {'ids': [], 'rule': None, 'ref': None}
    if not isinstance(ex, dict) or not ex.get('ref') or not ex.get('rule') or not isinstance(ex.get('ids'), list):
        raise SystemExit('refused: an exclusion record needs a prospective rule, a logged reference and the excluded ids (Codex ruling b)')
    state = {r['id']: r['state'] for r in rows if r['stage'] == 'S4a'}
    bad = [i for i in ex['ids'] if not str(state.get(i, '')).startswith('UNKNOWN (ineligible')]
    if bad: raise SystemExit(f'refused: only terminal ineligible S4a candidates of the inventory can be excluded (Codex ruling b): {bad}')
    return {'ids': sorted(ex['ids']), 'rule': ex['rule'], 'ref': ex['ref']}


def loo_select(C, held, info, decision, amendment_ref=None, exclusions=None):
    """S5 selection for one fold (A6 + B2). info: the training films' measured curves ONLY (refused if it holds the held-out film).
    decision: the sealed loo_branch result for the same held-out film. Same branch as the full data: pool = S4a archive + the fold's own S5
    candidates (never S4b); otherwise (A7, DRAFT): only the fold's four registered local points. Freezes only with exactly four distinct,
    resolved fold candidates and (ruling b) the complete, resolved S4a inventory - a terminal ineligible S4a candidate only through an
    explicit exclusion record; otherwise the ranking is a DIAGNOSTIC. Frozen records bind decision, inventory, settings and the
    input-only expected held-out signature (v2 fix 2) and are sealed for external commitment."""
    train = [t for t in FILMS if t != held]; _training_only(info, held); I = Blind(info, train)
    dec = verify_seal(decision, 'fold branch decision (loo_branch)')
    if abs(float(dec['held_out_nm']) - held) > 1e-9: raise SystemExit(f'refused: the branch decision is for the {dec["held_out_nm"]} nm fold, not {held} nm')
    bad = [c['id'] for c in C if c['stage'] == 'S4b' or (c['stage'] == 'S5' and (c.get('fold') is None or abs(float(c['fold']) - held) > 1e-9))]
    if bad: raise SystemExit(f'refused: S4b or other-fold candidates are not part of this fold: {bad}')
    mode = 'S4a archive' if dec['same_as_full_data'] else 'A7 local design (DRAFT)'
    s4a = [c for c in C if c['stage'] == 'S4a']; fold = sorted([c for c in C if c['stage'] == 'S5'], key=lambda c: c['id'])
    if not dec['same_as_full_data'] and s4a: raise SystemExit('refused: a changed-branch fold does not use the S4a archive (other branch); A7: its four registered points only')
    wrong = [c['id'] for c in C if c['branch'] != dec['fold_branch']]
    if wrong: raise SystemExit(f'refused: candidates whose branch is not the branch of the fold decision {dec["fold_branch"]}: {wrong[:4]}')
    odd = [c['id'] for c in s4a if c['id'] not in S4A_IDS]
    if odd: raise SystemExit(f'refused: S4a ids outside the registered inventory: {odd}')
    if len(fold) > LOO_N: raise SystemExit(f'refused: {len(fold)} fold candidates; the design fixes {LOO_N}')
    dims = ('lNs', 'WT') if dec['fold_branch'].get('mobility') == 'constant' else DIMS
    if C and dims_of(C) != dims: raise SystemExit('refused: candidate dimensions do not match the fold branch')
    settings = archive_settings(C, films=train) if C else None
    PP = profile_pool(C, I, films=train)
    rows = [{'id': c['id'], 'stage': c['stage'], 'x': c['x'], 'sqrtJ_train': p['profiled']['sqrtJ_dec'] if p and p['valid'] else None,
             'bound_limited': _bounds(p), 'state': _state(p, err),
             'runs': [{'run_id': r.get('run_id'), 'film_nm': r['t'], 'digest': run_digest(r)} for r in c['R'] if r['t'] in train]} for c, p, err in PP]
    res = {'held_out_nm': held, 'training_films': train, 'mode': mode, 'decision_sha256': dec['sha256'], 'dims': list(dims), 'pool': rows,
           'fold_candidates_done': len(fold), 'blind': f'measured curves visible: {train}; hidden: {I.hidden}', 'settings': settings,
           'warnings': _bound_warn(rows, 'sqrtJ_train')}
    dup = [(a['id'], b['id']) for a, b in itertools.combinations(C, 2) if 'S5' in (a['stage'], b['stage']) and not _distinct_pair(a['x'], b['x'], dims)]
    if dup: res['verdict'] = f'UNRESOLVED: fold candidates are not distinct (A6; ruling a: separation >= 1/56 and distinct deck inputs): {dup}'; return res
    if not dec['same_as_full_data']:
        _, pts7 = a7_points(dec)
        mis = [c['id'] for c, x in zip(fold, pts7) if deck_inputs(c['x'], dims) != deck_inputs(x, dims)]
        if mis: raise SystemExit(f'refused: fold candidates that are not the registered A7 points at deck rounding (in id order): {mis}')
        res['a7'] = {'points': pts7, 'note': A7_NOTE, 'amendment_ref': amendment_ref, 'centre_source': dec.get('centre_source')}
        if not dec.get('centre_launch_values'):
            res['verdict'] = 'UNRESOLVED: the fold decision carries no centre launch values (Codex ruling d): no A7 proposal'; return res
    if len(fold) < LOO_N:
        if dec['same_as_full_data']:
            prop = propose([{**r, 'sqrtJ': r['sqrtJ_train']} for r in rows], dims, 'sqrtJ'); res['next_training_candidate'] = prop
            if 'centre' in prop and 'proposal' in prop:
                cc, pc = next((c, p) for c, p, _ in PP if c['id'] == prop['centre']['id']); res['native_launch_values'] = nuisance_at(cc, pc, films=train)
            res['verdict'] = (f'TRAINING: {len(fold)}/{LOO_N} fold candidates done; launch the proposed candidate at {train} nm' if prop['verdict'].startswith('PROPOSAL')
                              else f'UNRESOLVED: no fold proposal ({prop["verdict"][:120]}); decision needed')
        else:
            res['next_training_candidate'] = {'proposal': res['a7']['points'][len(fold)], 'verdict': 'A7 REGISTERED POINT (not adaptive; deck-rounded inputs)'}
            res['native_launch_values'] = dec['centre_launch_values']
            res['verdict'] = (f'A7 LOCAL DESIGN (DRAFT): {len(fold)}/{LOO_N} registered points done; ' + A7_NOTE)
        return res
    unk = [r['id'] for r in rows if r['stage'] == 'S5' and r['sqrtJ_train'] is None]
    if unk: res['verdict'] = f'UNRESOLVED: fold inventory incomplete (unknown or invalid fold candidates: {unk}); no frozen record'; return res
    if not dec['same_as_full_data'] and not amendment_ref:
        res['verdict'] = 'REFUSED: A7 fold complete, but no frozen record without a logged register amendment (--amendment REF) and the go of the user'; return res
    ex = _exclusions(exclusions, rows)
    resolved = sorted([(r['sqrtJ_train'], r['id']) for r in rows if r['sqrtJ_train'] is not None])
    if dec['same_as_full_data']:   # Codex ruling (b): complete, resolved S4a inventory (or an explicit exclusion of terminal ineligible candidates)
        missing = [i for i in S4A_IDS if i not in {c['id'] for c in s4a}]
        block = missing + [r['id'] for r in rows if r['stage'] == 'S4a' and r['sqrtJ_train'] is None and r['id'] not in ex['ids']]
        if block:
            res['conditional_ranking_diagnostic'] = {'label': 'DIAGNOSTIC: ranking conditional on the resolved candidates; NOT a frozen prediction (Codex ruling b)',
                                                     'top2': [{'id': i, 'sqrtJ_train': v} for v, i in resolved[:2]]}
            res['verdict'] = (f'UNRESOLVED: S4a inventory missing or unresolved {block}; no unconditional best/runner-up freeze (Codex ruling b; a terminal '
                              'ineligible candidate needs a prospective exclusion record)'); return res
    if len(resolved) < 2: res['verdict'] = 'UNRESOLVED: fewer than two valid training profiles'; return res
    best_c = next(c for c, _, _ in PP if c['id'] == resolved[0][1])
    exp = expected_signature([r for r in best_c['R'] if r['t'] in train], held)   # v2 fix 2: input-only, every mode
    if s4a:
        act = archive_settings(s4a, films=[held])['per_film_sha256'].get(str(held))
        if act is not None and act != exp['sha256']: raise SystemExit('refused: the S4a runs at the held-out film do not carry the input-only expected settings (v2 fix 2)')
    inv = {'S4a': [{k: r[k] for k in ('id', 'state', 'sqrtJ_train', 'runs')} for r in rows if r['stage'] == 'S4a'],
           'S4a_missing': [i for i in S4A_IDS if i not in {c['id'] for c in s4a}] if dec['same_as_full_data'] else [],
           'fold': [{k: r[k] for k in ('id', 'state', 'sqrtJ_train', 'runs')} for r in rows if r['stage'] == 'S5'], 'excluded': ex}
    res['frozen'] = []
    for rank, (v, cid) in zip(('best', 'runner_up'), resolved[:2]):
        c, p = next((c, p) for c, p, _ in PP if c['id'] == cid)
        nv = nuisance_at(c, p, films=[held])
        rec = {'record': 'S5 frozen held-out prediction (CAMPAIGN_DESIGN l.279/l.331; matrix S5-H*-PRED-*)', 'status': 'DRAFT code (profile_s4s5 v4)',
               'fold_held_out_nm': held, 'training_films': train, 'rank': rank, 'candidate': cid, 'stage': c['stage'], 'coords': c['x'],
               'coords_natural': {'Ns_cm2': 10 ** c['x']['lNs'], 'WT_eV': c['x']['WT'], 'gamma0': c['x']['g0']}, 'branch': c['branch'],
               'training_sqrtJ_dec': v, 'bound_limited': next(r['bound_limited'] for r in rows if r['id'] == cid),
               'dV0_V': p['profiled']['dV0_V'], 'dV0_from_anchor_V': p['profiled']['dV0_from_anchor_V'],
               'Qf_cm2': nv['Qf_cm2'], 'mu_inf_cm2Vs': nv['mu_inf_cm2Vs'], 'ell_nm': nv['ell_nm'], 'held_out': nv['per_film'][str(held)],
               'mode': mode, 'decision_sha256': dec['sha256'], 'fold_choice': dec['fold_choice'], 'fold_branch': dec['fold_branch'], 'inventory': inv,
               'settings': {'training_per_film_sha256': settings['per_film_sha256'], 'shared_overrides': settings['shared_overrides'],
                            'held_out_expected_sha256': exp['sha256'], 'held_out_expected_signature': exp},
               'amendment_ref': amendment_ref, 'code_sha256': CODE_SHA,
               'role': 'primary prediction' if rank == 'best' else 'optimiser uncertainty only (not a second prediction)',
               'commit_rule': 'commit this sha256 externally (git / work chat) BEFORE the native held-out launch; loo_score scores only the committed record'}
        res['frozen'].append(seal(rec))
    res['verdict'] = ('FROZEN: commit both sha256 externally before the native held-out launches, then loo_score --committed SHA256'
                      + (f' (explicitly excluded: {ex["ids"]}, ref {ex["ref"]})' if ex['ids'] else ''))
    return res


def loo_score(rec, run, info, committed_sha256, loader=None):
    """held-out 5.3 acceptance of the native frozen prediction (B2): the record must match its seal AND the externally committed hash;
    the native run must be eligible and carry the frozen values, the shared settings and (v2 fix 2, every mode) the input-only expected
    non-fitted signature of the held-out film"""
    loader = loader or load
    verify_seal(rec, 'frozen record')
    if not committed_sha256: raise SystemExit('refused: no externally committed hash (Codex B2): commit the sha256 of the frozen record before the native launch and pass --committed')
    if str(committed_sha256).strip().lower() != rec['sha256']: raise SystemExit('refused: this frozen record is not the externally committed one (sha256 differs from --committed)')
    if rec.get('code_sha256') != CODE_SHA:
        raise SystemExit(f'refused: the frozen record was made by profile_s4s5.py {str(rec.get("code_sha256"))[:16]}..., this is {CODE_SHA[:16]}...: mismatched '
                         'code is refused before scoring (Codex v3 fix 2; no reviewed migration rule exists)')
    if str(rec.get('mode', '')).startswith('A7') and not rec.get('amendment_ref'): raise SystemExit('refused: an A7 record without a register amendment reference')
    st = rec.get('settings') or {}
    if not st.get('held_out_expected_sha256'): raise SystemExit('refused: the record carries no input-only expected held-out settings signature (v2 fix 2)')
    r = run if isinstance(run, dict) else loader(run); require_eligible([r], 'held-out scoring'); held = float(rec['fold_held_out_nm'])
    if abs(r['t'] - held) > 1e-9: raise SystemExit(f'refused: run is at {r["t"]} nm, the fold holds out {held} nm')
    x, b = coords(r); mism = []
    if abs(r['qf'] - rec['Qf_cm2']) > 1e-5 * abs(rec['Qf_cm2']): mism.append(f'Q_f {r["qf"]} vs frozen {rec["Qf_cm2"]}')
    if abs(r['mu_band'] - rec['held_out']['mu_band_cm2Vs']) > 1e-5 * rec['held_out']['mu_band_cm2Vs']: mism.append(f'mu_band {r["mu_band"]} vs frozen {rec["held_out"]["mu_band_cm2Vs"]}')
    for d in DIMS:
        a, f = x[d], rec['coords'][d]
        if (a is None) != (f is None) or (a is not None and abs(a - f) > 1e-5 * max(1.0, abs(f))): mism.append(f'{d} {a} vs frozen {f}')
    if b != rec['branch']: mism.append(f'branch {b} vs frozen {rec["branch"]}')
    if shared_overrides(r) != st.get('shared_overrides'): mism.append(f'shared settings {shared_overrides(r)[:3]} vs bound {(st.get("shared_overrides") or [])[:3]}')
    sig = fixed_signature(r)
    if sig['sha256'] != st['held_out_expected_sha256']:
        e = st.get('held_out_expected_signature') or {}
        mism.append(f'non-fitted settings at the held-out film differ from the input-only expected signature (film-keyed {film_keyed(r)} vs '
                    f'{(e.get("built_from") or {}).get("film_keyed_held")}; other: {[k for k in ("cox", "breakers", "model_sha256", "physics_options_sha256") if e.get(k) != sig[k]]})')
    if mism: raise SystemExit('refused: the native run does not carry the frozen prediction: ' + '; '.join(mism))
    acc = acceptance(r['vg'], r['i'], held, info, kind='native')
    v = acc['verdict']
    return {'fold_held_out_nm': held, 'rank': rec['rank'], 'candidate': rec['candidate'], 'frozen_sha256': rec['sha256'], 'run': r['run_id'], 'run_digest': run_digest(r),
            'acceptance_5_3': acc, 'labels': 'retrospective transferability within already-seen devices, not validation',
            'code_note': 'same code as at freezing (checked before scoring, Codex v3 fix 2)',
            'verdict': (('FAIL: the held-out film fails 5.3 -> transferability of this model form is falsified (reported, not repaired)'
                         if v.startswith('FAIL') else 'PASS: the held-out film passes every 5.3 criterion' if v.startswith('PASS') else v)
                        + ('' if rec['rank'] == 'best' else ' [runner-up: optimiser uncertainty only]'))}


# ------------------------------------------------------------------------------------------------ 5.3 acceptance
def _mfe_at(vg, mu, v, kind):
    k = int(np.argmin(np.abs(vg - v)))
    if abs(vg[k] - v) < 1e-6: return float(mu[k]), 'native point' if kind == 'native' else 'grid point of the profiled curve'
    if kind == 'native': return None, f'no native point at {v} V (native sampling required for a native curve, A10)'
    if not (vg[0] <= v <= vg[-1]): return None, 'not covered (no extrapolation)'
    return float(np.interp(v, vg, mu)), 'INTERPOLATED between gm points of the covered profiled curve (labelled, A10)'


def acceptance(vg, i, t, info, kind='native', active_mult=5.0):
    """CAMPAIGN_DESIGN 5.3 for one film, with the registered extraction functions (campaign_extract conventions) and the runner's active
    RMSE (run_atlas.regions/score). kind 'native' (native sampling: I_D(3 V) and mu_FE on native points, as campaign_extract) or
    'profiled' (A10: interpolation inside the covered range, labelled). Returns per-criterion values and PASS / FAIL / unresolved."""
    if kind not in ('native', 'profiled'): raise SystemExit(f'unknown acceptance kind {kind}')
    ex, rx = ce.ex, ce.rx
    vg = np.asarray(vg, float); i = np.asarray(i, float); M = info[t]; vm, im = M['vg'], M['i']
    o = float(np.median(im[(vm >= -2) & (vm <= -0.5)])); act = im > active_mult * o if t < 20 else np.ones(len(im), bool)
    cov = (vm >= vg[0] - 1e-9) & (vm <= vg[-1] + 1e-9)
    pred = np.interp(vm, vg, i); le = np.log10(np.maximum(pred, 1e-40)) - np.log10(im); m = act & cov
    c = {}
    covfrac = float(m.sum()) / max(1, int(act.sum()))
    c['active_rmse_dec'] = {'value': float(np.sqrt(np.mean(le[m] ** 2))) if m.any() else None, 'coverage': covfrac, 'limit': ACC['rmse_dec']}
    c['active_rmse_dec']['ok'] = None if c['active_rmse_dec']['value'] is None or covfrac < 0.95 else c['active_rmse_dec']['value'] <= ACC['rmse_dec'] + TINY
    vs = ex.crossing(vg, i, rx.I_CC, True)['v']; vmc = ex.crossing(vm, im, rx.I_CC, False)['v']
    dv = (vs - vmc) if (vs is not None and vmc is not None) else None
    c['dVth_cc_V'] = {'value': dv, 'limit': ACC['dvth_V'], 'ok': None if dv is None else abs(dv) <= ACC['dvth_V'] + TINY}
    k3 = int(np.argmin(np.abs(vg - 3.0)))
    if kind == 'native': i3, how3 = (float(np.interp(3.0, vg, i)), 'native point') if abs(vg[k3] - 3.0) < 1e-6 else (None, 'no native point at 3 V (A10)')
    else: i3, how3 = (float(np.interp(3.0, vg, i)), 'profiled curve, covered') if vg[0] - 1e-9 <= 3.0 <= vg[-1] + 1e-9 else (None, 'not covered (no extrapolation)')
    m3 = float(im[int(np.argmin(np.abs(vm - 3.0)))])
    e3 = 100 * (i3 / m3 - 1) if i3 is not None else None
    c['Id3V_err_pct'] = {'value': e3, 'how': how3, 'limit': ACC['id3_pct'], 'ok': None if e3 is None else abs(e3) <= ACC['id3_pct'] + TINY}
    lo, hi = M['a1_window']
    ss_s = ex.ss_window(vg, i, lo, hi, True)['ss']; ss_m = ex.ss_window(vm, im, lo, hi, False)['ss']
    es = 100 * (ss_s / ss_m - 1) if (ss_s is not None and ss_m) else None
    c['SS_a1_err_pct'] = {'value': es, 'sim_mV_dec': ss_s, 'meas_mV_dec': ss_m, 'limit': ACC['ss_pct'], 'ok': None if es is None else abs(es) <= ACC['ss_pct'] + TINY}
    mus = ex.MU_FACTOR * ex.gm(vg, i); mum = ex.MU_FACTOR * ex.gm(vm, im); mfe = {}
    for v in MUFE_V:
        a, how = _mfe_at(vg, mus, v, kind); b = float(mum[int(np.argmin(np.abs(vm - v)))])
        e = 100 * (a / b - 1) if a is not None and b else None
        mfe[f'{v:.1f}'] = {'value': e, 'sim': a, 'meas': b, 'how': how, 'ok': None if e is None else abs(e) <= ACC['mufe_pct'] + TINY}
    c['mu_FE_err_pct'] = {'per_V': mfe, 'limit': ACC['mufe_pct'], 'ok': (None if any(x['ok'] is None for x in mfe.values()) else all(x['ok'] for x in mfe.values()))}
    oks = [c[k]['ok'] for k in ('active_rmse_dec', 'dVth_cc_V', 'Id3V_err_pct', 'SS_a1_err_pct', 'mu_FE_err_pct')]
    verdict = ('FAIL: ' + ', '.join(k for k in c if c[k]['ok'] is False) if any(o is False for o in oks) else
               'PASS' if all(o is True for o in oks) else 'unresolved (a criterion could not be evaluated: ' + ', '.join(k for k in c if c[k]['ok'] is None) + ')')
    return {'film_nm': t, 'kind': kind, 'criteria': c, 'verdict': verdict,
            'labels': 'CAMPAIGN_DESIGN 5.3 (ASSUMED engineering limits); active RMSE as run_atlas.score; extraction as campaign_extract'
                      + ('; profiled curve: values between gm points are INTERPOLATED (labelled per criterion)' if kind == 'profiled' else '; native sampling')}


def transformed_points(r, dQf, scale):
    """the native points of a run moved by dV = -q dQf / C_ox and scaled: exactly the transformed curve, on its own (shifted) grid"""
    return np.asarray(r['vg'], float) - Q * dQf / r['cox'], scale * np.asarray(r['i'], float)


# ------------------------------------------------------------------------------------------------ native confirmation (Codex v2 fix 3)
def _endpoint(r):
    el = r.get('eligibility') or {}
    return {'run_id': r.get('run_id'), 'label': r.get('label'), 'film_nm': r.get('t'), 'digest': run_digest(r), 'eligible': el.get('eligible') is True,
            'problems': list(el.get('problems') or ([] if el else ['no eligibility record']))}


def _ps_check(native, reference):
    return ps.check(str(native['dir']), str(reference['dir']))   # profile_shared.check, unchanged


def native_confirmation(native, reference, role, checker=None, loader=None):
    """Codex v2 fix 3: a SEALED native-confirmation record around the unchanged profile_shared.check (0.01 dec on every J-window point).
    Both endpoints must be the designated runs of the role (CONFIRM_ROLES: S1-07 vs S0-01 at 2.0 nm, S3-27 vs S3-12 at 6.3 nm; label and
    film), else refused. Both must be eligible (B1), else the record is UNKNOWN and the check is not run. PASS / FAIL only from a check
    of two eligible endpoints; any other check outcome is UNKNOWN. The record carries both endpoints' digests: a consumer accepts it only
    for this role AND for the reference run it actually uses (confirmation_status)."""
    if str(role).upper().startswith('S4C') and not S4C_ROUTE_AVAILABLE:
        raise SystemExit('refused: the S4c confirmation route is disabled (Codex v3 ruling iii, execution gate): no wrapper yet binds the variable '
                         'reference, the settings, both endpoints\' eligibility and both digests')
    if role not in CONFIRM_ROLES: raise SystemExit(f'refused: unknown confirmation role {role}; designated: {sorted(CONFIRM_ROLES)}')
    loader = loader or load
    n = native if isinstance(native, dict) else loader(native); ref = reference if isinstance(reference, dict) else loader(reference)
    bad = [f'{w} {r.get("run_id")} is {(r.get("label"), r.get("t"))}, the {role} role needs {CONFIRM_ROLES[role][w]}'
           for w, r in (('native', n), ('reference', ref)) if (r.get('label'), r.get('t')) != CONFIRM_ROLES[role][w]]
    if bad: raise SystemExit(f'refused: not the designated {role} endpoints (role check, Codex v2 fix 3): ' + ' | '.join(bad))
    en, er = _endpoint(n), _endpoint(ref); chk = None
    if not (en['eligible'] and er['eligible']):
        v = 'UNKNOWN (endpoint not eligible: ' + ' | '.join(f'{e["run_id"]}: {"; ".join(e["problems"])}' for e in (en, er) if not e['eligible']) + ')'
    else:
        chk = (checker or _ps_check)(n, ref); cv = str(chk.get('verdict'))
        v = 'PASS' if cv.startswith('PASS') else 'FAIL' if cv.startswith('FAIL') else f'UNKNOWN (check: {cv[:100]})'
    keep = ('verdict', 'dQf_cm2', 'dV_shift_V', 'mun_scale', 'J_window_sub', 'J_window_on', 'max_abs_dev_native_grid_above_1e-14_dec',
            'other_material_differences', 'solver_geometry_override_differences', 'exactness_breakers')
    rec = {'record': 'native confirmation (Codex v2 fix 3; profile_shared.check unchanged)', 'status': 'DRAFT code (profile_s4s5 v4)', 'role': role,
           'film_nm': CONFIRM_ROLES[role]['native'][1], 'native': en, 'reference': er, 'tolerance_dec': ps.TOL_DEC,
           'check': None if chk is None else {k: chk.get(k) for k in keep}, 'verdict': v, 'code_sha256': CODE_SHA}
    return seal(rec)


def confirmation_status(rec, role, reference_digest):
    """(True | False | None, why): True = a sealed record of this role, bound to this reference run, with a PASS of two eligible endpoints;
    False = a valid evaluated FAIL (evaluated, cannot confirm); None = missing, unknown, not sealed, made by other code (v3 fix 2), other role
    or other reference run"""
    if not rec: return None, 'confirmation missing'
    try: verify_seal(rec, 'native confirmation record')
    except SystemExit as e: return None, f'not a sealed confirmation record ({str(e)[:60]})'
    if rec.get('code_sha256') != CODE_SHA: return None, f'{role} record made by other profile_s4s5.py code (code_sha256 differs; Codex v3 fix 2)'
    if rec.get('role') != role: return None, f'record of role {rec.get("role")}, not {role}'
    if (rec.get('reference') or {}).get('digest') != reference_digest: return None, f'{role} record bound to another reference run (digest differs)'
    v = str(rec.get('verdict'))
    if v == 'PASS' and rec['native'].get('eligible') and rec['reference'].get('eligible'): return True, f'{role} PASS'
    if v == 'FAIL' and rec['native'].get('eligible') and rec['reference'].get('eligible'): return False, f'{role} FAIL (valid evaluated)'
    return None, f'{role} {v[:80]}'


# ------------------------------------------------------------------------------------------------ identifiability Jacobian (5.4)
def _windows(Mt):
    return {'sub': (Mt['i'] >= 10 * Mt['floor']) & (Mt['i'] <= 1e-9), 'on': (Mt['vg'] >= 1 - 1e-9) & (Mt['vg'] <= 3 + 1e-9)}


def resid_vec(R, info, qf_abs, mu_inf, ell):
    """J-window log10 residuals of every film at an ABSOLUTE target Q_f (each run transformed from its own Q_f) and the mu law; NaN where
    not covered. Returns (vector, per-point (film, window) keys)."""
    v, keys = [], []
    for r in R:
        Mt = info[r['t']]; s = ps.mu_law(mu_inf, ell, r['t'], r['mstar']) / r['mu_band']
        lt = ps.transformed_log(r, qf_abs - r['qf'], s, Mt['vg']); lm = np.log10(Mt['i'])
        for k, msk in _windows(Mt).items():
            v.append(lt[msk] - lm[msk]); keys += [(r['t'], k)] * int(msk.sum())
    return np.concatenate(v), keys


def jac_analysis(Jm, names):
    """scaled Jacobian -> FULL singular spectrum (B5: with fewer residuals than parameters, or an exact null direction, the omitted / zero
    singular values are kept as 0 and their right singular vectors reported), numerical column rank, condition numbers (range-scaled and
    equilibrated), correlations (only at full column rank) and weak combinations"""
    Js = Jm * np.array([SCALE[n] for n in names])[None, :]; n, p = Js.shape
    _, s, Vt = np.linalg.svd(Js, full_matrices=n < p)   # Vt always p x p: every right singular vector, null directions included
    tol = max(n, p) * np.finfo(float).eps * (float(s[0]) if s.size else 0.0)
    rank = int(np.sum(s > tol)); full = rank == p
    sf = np.concatenate([s, np.zeros(p - len(s))]); sf = np.where(sf > tol, sf, 0.0)
    cond = float(sf[0] / sf[-1]) if sf[-1] > 0 else float('inf')
    nrm = np.linalg.norm(Js, axis=0); Je = Js / np.where(nrm > 0, nrm, 1.0)
    se = np.linalg.svd(Je, compute_uv=False); se = np.concatenate([se, np.zeros(p - len(se))]); te = max(n, p) * np.finfo(float).eps * float(se[0] if se.size else 0.0)
    cond_e = float(se[0] / se[-1]) if se[-1] > te else float('inf')
    if full:
        C = np.linalg.inv(Js.T @ Js); dg = np.sqrt(np.clip(np.diag(C), 1e-300, None)); corr = C / np.outer(dg, dg)
        pairs = [{'a': names[a], 'b': names[b], 'corr': float(corr[a, b])} for a in range(p) for b in range(a + 1, p)]
        mx = max((abs(q['corr']) for q in pairs), default=0.0)
    else:
        pairs, mx = None, None
    weak = [{'singular_value': float(sf[k]), 's_max_over_s': float(sf[0] / sf[k]) if sf[k] > 0 else float('inf'),
             'combination_scaled_units': {nm: float(x) for nm, x in zip(names, Vt[k])}} for k in range(p) if sf[k] == 0 or sf[0] / sf[k] > COND_MAX]
    return {'n_rows': int(n), 'column_rank': rank, 'full_column_rank': bool(full), 'singular_values_scaled': sf.tolist(),
            'condition_number_range_scaled': cond, 'condition_number_equilibrated': cond_e, 'correlations': pairs, 'max_abs_corr': None if mx is None else float(mx),
            'weak_combinations': weak, 'flag': bool((not full) or cond > COND_MAX or cond_e > COND_MAX or (mx is not None and mx > CORR_MAX)),
            'note': None if full else f'rank deficient ({rank} < {p}): correlations undefined; individual values UNRESOLVED (B5)'}


def jacobian(C, info, best_id=None, ks=None):
    for c in C:
        if c['stage'] not in ('S4a', 'S4b'): raise SystemExit(f'{c["id"]}: the identifiability archive is S4a + S4b only (5.4)')
    dims = dims_of(C); archive_settings(C); P_ = profile_pool(C, info)
    valid = [(c, p) for c, p, _ in P_ if p is not None and p['valid']]
    if not valid: return {'verdict': 'UNRESOLVED: no valid profile'}
    cb, pb = (min(valid, key=lambda z: (z[1]['profiled']['sqrtJ_dec'], z[0]['id'])) if best_id is None else next(z for z in valid if z[0]['id'] == best_id))
    if len({round(c['R'][0]['cox'], 15) for c, _ in valid}) > 1: raise SystemExit('refused: different C_ox across the archive')
    p = pb['profiled']; qf, mu, ell = p['Qf_cm2'], p['mu_inf_cm2Vs'], p['ell_nm']; cox = cb['R'][0]['cox']
    r0, keys = resid_vec(cb['R'], info, qf, mu, ell)
    # weights: |r|^2 = J at the best point (covered points per film window; J = (1/n_films) sum_t (mean_sub + mean_on) / 2)
    nf = len(cb['R']); cnt = {}
    for k_, ok in zip(keys, np.isfinite(r0)): cnt[k_] = cnt.get(k_, 0) + int(ok)
    w = np.array([1.0 / math.sqrt(nf * 2 * cnt[k_]) if cnt[k_] else 0.0 for k_ in keys])
    hN = {'dV0': 1e-3, 'lmu': 1e-3, 'ell': 1e-2}
    def at(dv0=0.0, lmu=0.0, dl=0.0, R=None):
        return resid_vec(R or cb['R'], info, qf - dv0 * cox / Q, mu * 10 ** lmu, ell + dl)[0]
    cols = {'dV0': (at(dv0=hN['dV0']) - at(dv0=-hN['dV0'])) / (2 * hN['dV0']), 'lmu': (at(lmu=hN['lmu']) - at(lmu=-hN['lmu'])) / (2 * hN['lmu']),
            'ell': (at(dl=hN['ell']) - at(dl=-hN['ell'])) / (2 * hN['ell'])}
    others = [(c, unit(c['x'], dims), resid_vec(c['R'], info, qf, mu, ell)[0]) for c, _ in valid if c['id'] != cb['id']]
    ub = unit(cb['x'], dims); xb = np.array([cb['x'][d] for d in dims])
    others.sort(key=lambda z: (float(np.linalg.norm(z[1] - ub)), z[0]['id']))
    fin = np.isfinite(r0) & np.all([np.isfinite(v) for v in cols.values()], axis=0)
    for _, _, rv in others: fin &= np.isfinite(rv)
    d = len(dims); ks = sorted({k for k in (ks or (2 * d, 2 * d + 2, len(others))) if d + 1 <= k <= len(others)})
    if not ks: return {'verdict': f'UNRESOLVED: {len(others)} neighbours; the launched columns need at least {d + 1}'}
    names = list(dims) + list(NUIS); variants = []
    for k in ks:
        nb = others[:k]
        dX = np.array([[c['x'][dd] for dd in dims] for c, _, _ in nb]) - xb
        dR = np.array([(rv - r0)[fin] * w[fin] for _, _, rv in nb])
        JL, res_, rank, sv = np.linalg.lstsq(dX, dR, rcond=None)
        lin = float(np.linalg.norm(dR - dX @ JL) / max(np.linalg.norm(dR), 1e-300))
        Jm = np.column_stack([JL.T] + [cols[n][fin] * w[fin] for n in NUIS])
        a = jac_analysis(Jm, names)
        variants.append({'k_neighbours': k, 'neighbours': [c['id'] for c, _, _ in nb], 'rank_dX': int(rank), 'relative_nonlinearity': lin, **a})
    prim = variants[0]
    deficient = any(not v['full_column_rank'] or v['rank_dX'] < d for v in variants)
    flag = deficient or any(v['flag'] for v in variants)
    return {'best': {'id': cb['id'], 'sqrtJ_dec': p['sqrtJ_dec'], 'x': cb['x'], 'dV0_V': p['dV0_V'], 'mu_inf_cm2Vs': mu, 'ell_nm': ell},
            'parameters': names, 'scales': {n: SCALE[n] for n in names}, 'residual_points': int(fin.sum()), 'dropped_points': int((~fin).sum()),
            'primary': prim, 'variants': variants,
            'labels': ('launched columns: approximate finite differences from scattered archive points - diagnostics, NOT confidence intervals (A8); '
                       'profiled columns: exact transformation; scales frozen at the design ranges'),
            'verdict': ('REPORT PARAMETER COMBINATIONS; individual values UNRESOLVED (rank deficient in at least one variant: column or launched-step rank; B5)'
                        if deficient else
                        'REPORT PARAMETER COMBINATIONS (condition number > 100 or |corr| > 0.95 in at least one variant; 5.4)' if flag else
                        'individual values may be reported (every variant: full column rank, condition number <= 100 and |corr| <= 0.95)')}


# ------------------------------------------------------------------------------------------------ S6 sensitivity (5.4)
def sensitivity(pert, base, info, fill_from_base=False, allow_approximate=False):
    """A9: perturbed and base sets profiled on the SAME films; a missing film is filled from the base only for a designated film-local
    perturbation (FILM_LOCAL), explicitly labelled"""
    require_eligible(list(pert) + list(base), 'S6 profiling')
    tp = {r['t'] for r in pert}; label = []
    if fill_from_base:
        nd = [r.get('run_id') for r in pert if r.get('label') not in FILM_LOCAL or abs(r['t'] - FILM_LOCAL[r.get('label')]) > 1e-9]
        if nd: raise SystemExit(f'refused: filling from the base is allowed only for a designated film-local perturbation {sorted(FILM_LOCAL)} (A9); not: {nd}')
        add = [r for r in base if r['t'] not in tp]; pert = sorted(list(pert) + add, key=lambda r: r['t'])
        if add: label.append(f'FILLED FROM BASE (designated film-local perturbation {sorted({r.get("label") for r in pert if r.get("label") in FILM_LOCAL})}): '
                             f'{[r["run_id"] for r in add]}')
    films = sorted({r['t'] for r in pert}); bset = sorted([r for r in base if r['t'] in films], key=lambda r: r['t'])
    if sorted(r['t'] for r in bset) != films: raise SystemExit(f'base runs do not cover the perturbed films {films}')
    a, b = profile_films(sorted(pert, key=lambda r: r['t']), info, allow_approximate), profile_films(bset, info, allow_approximate)
    pa, pb = a['profiled'], b['profiled']
    mv = {k: pa[k] - pb[k] for k in ('dV0_V', 'Qf_cm2', 'mu_inf_cm2Vs', 'ell_nm', 'sqrtJ_dec')}
    mv['log10_mu_inf'] = math.log10(pa['mu_inf_cm2Vs'] / pb['mu_inf_cm2Vs'])
    return {'films': films, 'perturbed': a, 'base': b, 'movement': mv, 'labels': label + ['S6 profile: movement of the re-profiled (dV0, mu_inf, ell) on the '
            'same films; dV0 is relative to each set\'s own launched Q_f, Q_f_cm2 is absolute'],
            'verdict': 'UNVERIFIED (a profile is not valid)' if not (a['valid'] and b['valid']) else 'OK'}


# ------------------------------------------------------------------------------------------------ CLI
def _opt(argv, k, default=None):
    return argv[argv.index(k) + 1] if k in argv else default


REMOVED = {'--trust': 'A1 ruling (fixed trust region)', '--s4a-only': 'A2 ruling (S4a + completed S4b)', '--freeze-now': 'A6 ruling (no early primary freeze)'}


def main(argv):
    if not argv or argv[0] in ('-h', '--help'): print(__doc__); return 2
    rm = [k for k in REMOVED if k in argv]
    if rm: print('removed options: ' + '; '.join(f'{k} ({REMOVED[k]})' for k in rm)); return 2
    cmd = argv[0]; out = Path(_opt(argv, '--out', OUT)); out.mkdir(parents=True, exist_ok=True)
    VAL = ('--out', '--tag', '--held', '--best', '--decision', '--committed', '--amendment', '--exclusions', '--role')
    pos = [a for i, a in enumerate(argv[1:], 1) if not a.startswith('--') and argv[i - 1] not in VAL]
    approx = '--allow-approximate' in argv
    try:
        if cmd in ('loo_branch', 'loo_select'):   # B2: the fold's targets are the training films only, loaded before Blind
            held = float(_opt(argv, '--held')); info = measured_training([t for t in FILMS if abs(t - held) > 1e-9])
        elif cmd != 'confirm':
            info, _ = ce.measured()
        if cmd == 'profile_n':
            res = profile_films([load(x) for x in pos], info, approx, tag=_opt(argv, '--tag')); fn = f'profile_n_{_opt(argv, "--tag") or "_".join(res["runs"])}'
        elif cmd == 'surrogate':
            res = surrogate(load_archive(pos[0]), info, approx); fn = f'surrogate_{Path(pos[0]).stem}'
        elif cmd == 'loo_branch':
            res = loo_branch(json.loads(Path(pos[0]).read_text()), held, info); fn = f'loo_branch_{held}'
        elif cmd == 'loo_select':
            if not _opt(argv, '--decision'): print('loo_select needs --decision DECISION.json (the sealed loo_branch result)'); return 2
            dec = json.loads(Path(_opt(argv, '--decision')).read_text())
            exf = _opt(argv, '--exclusions'); exr = json.loads(Path(exf).read_text()) if exf else None
            res = loo_select(load_archive(pos[0]), held, info, dec, _opt(argv, '--amendment'), exr); fn = f'loo_select_{held}'
            for rec in res.get('frozen', []): (out / f's4s5_loo_frozen_{held}_{rec["rank"]}.json').write_text(json.dumps(rec, indent=1, default=float))
        elif cmd == 'loo_score':
            rec = json.loads(Path(pos[0]).read_text()); res = loo_score(rec, pos[1], info, _opt(argv, '--committed'))
            fn = f'loo_score_{rec["fold_held_out_nm"]}_{rec["rank"]}_{res["run"]}'
        elif cmd == 'confirm':
            res = native_confirmation(pos[0], pos[1], _opt(argv, '--role')); fn = f'confirm_{res["role"]}_{res["native"]["run_id"]}'
        elif cmd == 'jacobian':
            res = jacobian(load_archive(pos[0]), info, _opt(argv, '--best')); fn = f'jacobian_{Path(pos[0]).stem}'
        elif cmd == 'sensitivity':
            if '--' not in argv: print('sensitivity RUN ... -- BASE ...'); return 2
            k = argv.index('--')
            def plain(seq, off): return [a for j, a in enumerate(seq) if not a.startswith('--') and argv[off + j - 1] not in VAL]
            pa, pb = plain(argv[1:k], 1), plain(argv[k + 1:], k + 1)
            res = sensitivity([load(x) for x in pa], [load(x) for x in pb], info, '--fill-from-base' in argv, approx); fn = 'sensitivity_' + '_'.join(res['perturbed']['runs'])
        else:
            print(__doc__); return 2
    except SystemExit as e:
        print(f'REFUSED: {e}'); return 3
    (out / f's4s5_{fn}.json').write_text(json.dumps(res, indent=1, default=float)); print(json.dumps(res, indent=1, default=float))
    v = str(res.get('verdict', ''))
    return 1 if v.startswith('FAIL') else 3 if v.startswith(('REFUSED', 'UNRESOLVED', 'UNVERIFIED', 'unresolved', 'A7', 'DIFFERENT')) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
