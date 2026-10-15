#!/usr/bin/env python3
"""PA-18 S4c confirmation wrapper (register A52, 2026-10-15; design registration A45 (PA-18), codex_changes/amendments_v2.md l.187-198;
no Codex review, D-63; Claude go under D-59). NO simulator call. It reads finished run directories ONLY through the frozen helpers of
profile_s4s5.py (429b3a3f: load, _endpoint, _ps_check = profile_shared.check unchanged, profile_films, nuisance_at, adopt_films, acceptance,
seal) and writes only sealed JSON records into analysis_2026-10-10_campaign/profile/ (prefix s4c_ / s4d_).

The frozen file is NOT changed: profile_s4s5.S4C_ROUTE_AVAILABLE stays False and native_confirmation still refuses role S4c (Codex v3 ruling
(iii)). This separate file is the confirmation wrapper that the ruling asks for; it binds (PA-18 (a)-(f)):
  (a) eligibility of both endpoints through the frozen _endpoint (C3 run validity, score_register.run_problems); either endpoint ineligible
      gives UNKNOWN, never PASS, and the check is not run;
  (b) settings: the native deck (device.in text sha256) and material (material_model_used.json text sha256) equal the dry builds pinned in
      the sealed variable-reference record; the native overrides equal the registered S4c entry; the S4c route plan entries equal the
      record's entries (plan sha256 reported); the model file, solver.yaml and the runner/builder files (public-repo 1375164 + builder
      734125a8) as pinned; the overrides that differ from the reference run are ONLY the written variables (Q_f value and mu_band_fitted[t]),
      checked by key here AND through the frozen check's exactness_breakers / other_material_differences / solver_geometry_override_differences
      (all three must be empty);
  (c) both digests: the sealed variable-reference record (its sha256 must equal --committed, the value committed externally before the
      native launch) and the native run (deck_sha256 + terminal_currents.csv sha256 + the frozen file_digest); the reference run's frozen
      file_digest must equal the one sealed at freezing;
  (d) variable reference: candidate id (the best S4a candidate of the frozen surrogate output, S4A-04), Q_f (-> dV0) and the per-film MUN
      scale written natively, with the record they come from (the frozen profile_n record of that candidate, re-profiled at freezing with the
      frozen profile_films and required to be equal);
  (e) frozen code: refuses unless profile_s4s5.py, profile_shared.py and score_register.py (and the helpers they import) match their pins and
      profile_s4s5.CODE_SHA is the pinned 429b3a3f;
  (f) 0.01-dec comparison: the unchanged profile_shared.check (0.01 dec on every J-window point), through profile_s4s5._ps_check; asserts
      profile_shared.TOL_DEC == profile_s4s5.S4C_TOL_DEC == S4C_TOL_DEC == 0.01.
Every record carries wrapper_sha256 (this file) and code_sha256 (frozen profile_s4s5.CODE_SHA) and is sealed (profile_s4s5.seal).

S4d (register A52 (g)): the runner-up S3 branch at the calibrated parameters = IGZO.TOKYO GAMMA0 -0.31 written on top of the S4c entries.
The read-out uses the frozen profile_s4s5.adopt_films (the S3 adoption arithmetic) of the S4d triple against the S4A-04 triple (same N_s,
W_T): ARITHMETIC PASS of an eligible, activated, verified triple = the branch choice made at the start values does NOT survive calibration;
otherwise it survives (reported; no re-calibration, no change of the S5 branch rule).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"      (package root, project venv)
    python -I -B analysis_2026-10-10_campaign/s4c_confirm_wrapper.py pins
    python -I -B analysis_2026-10-10_campaign/s4c_confirm_wrapper.py freeze                      -> profile/s4c_record_A52.json (sealed)
    python -I -B analysis_2026-10-10_campaign/s4c_confirm_wrapper.py confirm RUN_2p0 RUN_6p3 RUN_13p2 --committed SHA256
                                                                                                -> profile/s4c_confirm_A52.json (sealed)
    python -I -B analysis_2026-10-10_campaign/s4c_confirm_wrapper.py s4d RUN_2p0 RUN_6p3 RUN_13p2 --committed SHA256
                                                                                                -> profile/s4d_readout_A52.json (sealed)
Exit codes: 0 done / PASS (confirm) / verdict reached (s4d); 1 FAIL (confirm); 2 usage; 3 refused, UNKNOWN or unresolved.
Labels: native curves COMPUTED (ATLAS 5.28); profiled Q_f, mu_inf, ell FITTED (shared, exact-transformation profiling); N_s, W_T = ASSUMED
LHS design point S4A-04 selected by the profiled objective (FITTED in effect); calibration, retrospective, never validation.
"""
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))

# (e) frozen code (the three frozen hashes) and the helpers they import
FROZEN = {'profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',
          'profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
          'score_register.py': 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a'}
HELPERS = {'campaign_extract.py': '1f6f324a0841d50bb20baf7f94b6444d688aaf4cbdf71707594a06f26e3e63ba',
           'campaign_tools.py': '3b0403d9c5cc5423cb80dabc3765f9a781b7a06b512082b6f210971a9417ab0d',
           'post_run_checks.py': '39d3d51d3b2470b1396196bcfce34dc4a8f0a6acd3bcb2a213001dc5ec3ed91f',
           'prelaunch_gate_c10_f.py': 'd0baaca36b77cbe95c598a641f0a89366d4e2d496cf59a4935aa0ead4de1741d'}   # its IGZO block reader only (S4d)
# (b) settings: model file, solver.yaml, runner (public-repo 1375164) and builder (734125a8)
SETTINGS = {'config/iwo_material_model_v3.yaml': '51b184e8728c4e4ce5ed4110c56d4b1083b5d12f1d4d6b45aef52816ba63961c',
            'config/solver.yaml': 'd5a9101219d1238923da096766443fd021751fad1a9f55770b3851301481d583',
            'scripts/run_atlas.py': 'b7927ac5b9747d5531ac827d220da6004e4a144d672ae16ab9bca2a28f46e6ae',
            'scripts/run_campaign.py': 'fb6e802f8c1cb71b56e153ed99504cc8e7e83d4c8eb7af8f13dc421d0fd125ac',
            'scripts/build_iwo_decks.py': '734125a8915e2a7790b2794db0c7bf429c477a83238b638a200af2b5fbeeca3c'}
MODEL_ENV = 'config/iwo_material_model_v3.yaml'
# (d) the variable reference comes from these frozen-tool outputs (A51 (d) archive, frozen surrogate verdict, frozen profile_n record)
SOURCES = {'surrogate': ('analysis_2026-10-10_campaign/profile/s4s5_surrogate_s4a_archive_A51.json',
                         'ef10e8d4771e4c153bf230ff6b56cae52b5959dfcd71f4a5eeae36b6ebf3df42'),
           'archive': ('analysis_2026-10-10_campaign/profile/s4a_archive_A51.json',
                       '44de96df4bc0b2731e01b8b49c6fe2b06f4bf2295f2ff40141c7a283420df0f0'),
           'profile': ('analysis_2026-10-10_campaign/profile/s4s5_profile_n_S4A-04.json',
                       '043aa0078fe2374d76bf01e086c8cddb1f60e8845c3488ebad2fa38d08c7fc34')}
S4C_TOL_DEC = 0.01
REL_TOL = 1e-5                     # written value vs record (6-significant-figure deck rounding of nuisance_at; as loo_score)
FILMS = (2.0, 6.3, 13.2)
TAG = {2.0: '2p0', 6.3: '6p3', 13.2: '13p2'}
TIMEOUT = {2.0: 1600, 6.3: 2000, 13.2: 3100}   # matrix S4C-* / S4D-* timeouts
QF_KEY = 'traps.fixed_interface_charge_Qf_cm2.value'
def MU_KEY(t): return f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{t}]'
IGZO_OVERRIDES = ['solver.physics_options.mobility.model=igzo_tokyo', 'solver.physics_options.mobility.gamma0=-0.31',
                  'solver.physics_options.mobility.tgamma=178.4', 'solver.physics_options.mobility.ncrit=1e20']   # = S3-11/12/13 (A52 (g))
S4D_BRANCH = 'IGZO.TOKYO GAMMA0 -0.31 (S3-11/S3-12/S3-13 mobility overrides; surface tail as the matrix S4D template)'
RECORD = HERE / 'profile' / 's4c_record_A52.json'
CONFIRM_OUT = HERE / 'profile' / 's4c_confirm_A52.json'
S4D_OUT = HERE / 'profile' / 's4d_readout_A52.json'
PLANS = {'S4c': 'config/campaign_C10_S4c.json', 'S4d': 'config/campaign_C10_S4d.json'}
KEEP = ('verdict', 'dQf_cm2', 'dV_shift_V', 'mun_scale', 'J_window_sub', 'J_window_on', 'max_abs_dev_native_grid_above_1e-14_dec',
        'native_points_covered_above_1e-14', 'native_points', 'other_material_differences', 'solver_geometry_override_differences',
        'exactness_breakers')


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsha(s): return hashlib.sha256(s.encode()).hexdigest()


def wrapper_sha(): return fsha(Path(__file__).resolve())


def label(stage, t): return f'c10_{stage.lower()}_{TAG[t]}_{TAG[t]}'


def entry_id(stage, t): return f'{stage.upper()}-{TAG[t]}'


def _okey(o): return o.split('=', 1)[0]


# ------------------------------------------------------------------------------------------------ (e) pins
def pin_problems(root=HERE, pkg=PKG):
    bad = []
    for f, h in {**FROZEN, **HELPERS}.items():
        p = Path(root) / f
        if not p.is_file() or fsha(p) != h: bad.append(f'{f} (expected {h[:8]})')
    for f, h in SETTINGS.items():
        p = Path(pkg) / f
        if not p.is_file() or fsha(p) != h: bad.append(f'{f} (expected {h[:8]})')
    return bad


def frozen_modules():
    """the frozen modules, imported only after their pins are checked; (f) tolerance assertions"""
    bad = pin_problems()
    if bad: raise SystemExit('refused: frozen-code / settings pins differ (PA-18 (e)): ' + '; '.join(bad))
    import profile_shared as ps
    import profile_s4s5 as pss
    import campaign_extract as ce
    if pss.CODE_SHA != FROZEN['profile_s4s5.py']: raise SystemExit('refused: profile_s4s5.CODE_SHA differs from the frozen pin')
    if not (ps.TOL_DEC == pss.S4C_TOL_DEC == S4C_TOL_DEC == 0.01):
        raise SystemExit(f'refused: tolerance mismatch (profile_shared.TOL_DEC {ps.TOL_DEC}, profile_s4s5.S4C_TOL_DEC {pss.S4C_TOL_DEC})')
    if pss.S4C_ROUTE_AVAILABLE is not False:
        raise SystemExit('refused: profile_s4s5.S4C_ROUTE_AVAILABLE is not False (the frozen file must stay unchanged)')
    return ps, pss, ce


# ------------------------------------------------------------------------------------------------ sealing helpers (same canon as the frozen seal)
def _canon(d): return json.dumps(d, sort_keys=True, default=float, separators=(',', ':'))


def seal_ok(d):
    return isinstance(d, dict) and d.get('sha256') == tsha(_canon({k: v for k, v in d.items() if k != 'sha256'}))


def committed_record(rec, committed):
    """(c) the sealed variable-reference record must match its seal AND the externally committed hash"""
    if not seal_ok(rec): raise SystemExit('refused: the S4c variable-reference record does not match its sha256 (edited after sealing)')
    if not committed or str(committed).strip().lower() != rec['sha256']:
        raise SystemExit('refused: the record is not the externally committed one (--committed differs or missing; PA-18 (c))')
    if rec.get('code_sha256') != FROZEN['profile_s4s5.py']: raise SystemExit('refused: the record was made by other profile_s4s5.py code')
    if rec.get('wrapper_sha256') != wrapper_sha(): raise SystemExit('refused: the record was made by another version of this wrapper')
    return rec


# ------------------------------------------------------------------------------------------------ entries (variable reference -> native decks)
def s4c_overrides(base_overrides, t, nuis):
    """the S4A-04 matrix overrides with ONLY the two written variables replaced by the profiled launch values (nuisance_at strings)"""
    new = {_okey(o): o for o in nuis['per_film'][str(t)]['overrides']}
    if set(new) != {QF_KEY, MU_KEY(t)}: raise SystemExit(f'refused: nuisance overrides at {t} nm are not exactly Q_f and mu_band_fitted[{t}]')
    out, hit = [], {k: 0 for k in new}
    for o in base_overrides:
        k = _okey(o)
        if k in new: out.append(new[k]); hit[k] += 1
        else: out.append(o)
    if any(v != 1 for v in hit.values()): raise SystemExit(f'refused: the base entry at {t} nm does not carry each written variable exactly once ({hit})')
    return out


def make_entries(mx_runs, cand, nuis, record_rel):
    """S4C-* and S4D-* route-plan entries from the matrix (S4A-<cand>-* overrides; S4C-*/S4D-* id, label, timeout, stage) and the profiled
    launch values"""
    by_id = {r['id']: r for r in mx_runs}; out = {}
    for t in FILMS:
        base = by_id[f'{cand}-{TAG[t]}']['campaign_entry']
        ov = s4c_overrides(base['overrides'], t, nuis)
        for stage, extra in (('S4c', []), ('S4d', IGZO_OVERRIDES)):
            r = by_id[entry_id(stage, t)]; ce_ = r['campaign_entry']
            if ce_['label'] != label(stage, t) or ce_['timeout'] != TIMEOUT[t]: raise SystemExit(f'refused: matrix {r["id"]} label/timeout differ')
            purpose = (ce_['purpose'].replace('within 0.005 dec', 'within 0.01 dec (PA-0 / CAMPAIGN_DESIGN l.69)')
                       + f' Register A52: best S4a candidate {cand} (frozen surrogate, ABORT S4b) at the profiled Q_f and mu_band_fitted[{t}].'
                       if stage == 'S4c' else
                       ce_['purpose'] + f' Register A52 (g): runner-up = {S4D_BRANCH}, at the S4c launch values ({cand}, profiled Q_f and mu_band).')
            out[entry_id(stage, t)] = {'id': entry_id(stage, t), 'thickness': t, 'label': label(stage, t), 'overrides': ov + list(extra),
                                       'timeout': TIMEOUT[t], 'purpose': purpose, 'stage': r['stage'], 'matrix_status': r['status'],
                                       'requires_code': r.get('requires_code', []), 'depends_on': r.get('depends_on'),
                                       'params_rule': f'resolved from the sealed record {record_rel} (register A52)'}
    return out


def dry_build(entries):
    """deck and material text sha256 that run_atlas would write now (run_campaign.current_deck_text / current_material_text, V3)"""
    os.environ['IWO_MODEL_FILE'] = MODEL_ENV
    if str(PKG / 'scripts') not in sys.path: sys.path.insert(0, str(PKG / 'scripts'))
    import build_iwo_decks as bd
    import run_campaign as rc
    bd.MODEL_FILE = MODEL_ENV
    return {k: {'deck_sha256': tsha(rc.current_deck_text(e, e['overrides'])), 'model_sha256': tsha(rc.current_material_text(e['overrides']))}
            for k, e in entries.items()}


# ------------------------------------------------------------------------------------------------ freeze (variable reference record)
def best_of_surrogate(sur):
    """(d) the best S4a candidate = the lowest valid profiled sqrt(J) of the frozen surrogate output (ties by id), after an ABORT verdict"""
    if sur.get('code_sha256') != FROZEN['profile_s4s5.py']: raise SystemExit('refused: the surrogate output was made by other profile_s4s5.py code')
    if not str(sur.get('verdict', '')).startswith('ABORT S4b'): raise SystemExit(f'refused: surrogate verdict is not the S4a abort: {sur.get("verdict")}')
    ab = sur.get('s4a_abort') or {}
    if ab.get('n_valid') != 15 or ab.get('n_missing') != 0 or ab.get('n_invalid') != 0: raise SystemExit('refused: the S4a inventory is not complete and valid')
    rows = [r for r in sur['archive'] if r.get('stage') == 'S4a' and r.get('sqrtJ') is not None and r.get('state') == 'valid']
    if len(rows) != 15: raise SystemExit(f'refused: {len(rows)} valid S4a rows (expected 15)')
    b = min(rows, key=lambda r: (r['sqrtJ'], r['id']))
    if abs(b['sqrtJ'] - ab['best_sqrtJ_dec']) > 1e-12: raise SystemExit('refused: best row and s4a_abort best differ')
    return b


def freeze(out=RECORD, force=False):
    ps, pss, ce = frozen_modules()
    src = {}
    for k, (rel, h) in SOURCES.items():
        if fsha(PKG / rel) != h: raise SystemExit(f'refused: {rel} sha256 differs from {h[:8]} (frozen-tool output changed)')
        src[k] = {'file': rel, 'sha256': h}
    sur = json.loads((PKG / SOURCES['surrogate'][0]).read_text()); b = best_of_surrogate(sur); cid = b['id']
    arch = json.loads((PKG / SOURCES['archive'][0]).read_text()); c0 = next(c for c in arch['candidates'] if c['id'] == cid)
    prof_rel = f'analysis_2026-10-10_campaign/profile/s4s5_profile_n_{cid}.json'
    if prof_rel != SOURCES['profile'][0]: raise SystemExit(f'refused: the best candidate {cid} is not the pinned profile record {SOURCES["profile"][0]}')
    stored = json.loads((PKG / prof_rel).read_text())
    R = [pss.load(c0['runs'][str(t)]) for t in FILMS]
    pss.require_eligible(R, 'the S4c variable reference')
    if [pss.run_digest(r) for r in R] != b['run_digests'] or stored.get('run_digests') != b['run_digests']:
        raise SystemExit('refused: the reference runs\' frozen digests differ from the surrogate / profile record')
    info, _ = ce.measured()
    prof = pss.profile_films(R, info, tag=cid)
    P, S = prof['profiled'], stored['profiled']
    same = all(abs(P[k] - S[k]) <= 1e-9 * max(1.0, abs(S[k])) for k in ('Qf_cm2', 'mu_inf_cm2Vs', 'ell_nm', 'sqrtJ_dec', 'dV0_V'))
    if not same or prof['verdict'] != stored['verdict']: raise SystemExit('refused: the frozen re-profile differs from the stored profile_n record')
    c = pss.candidate({'id': cid, 'stage': 'S4a', 'runs': {str(r['t']): r for r in R}})
    nuis = pss.nuisance_at(c, prof)
    import campaign_tools as ct
    mx = ct.matrix()
    rec_rel = str(out.relative_to(PKG)).replace('\\', '/') if Path(out).is_absolute() and PKG in Path(out).parents else str(out)
    entries = make_entries(mx['runs'], cid, nuis, rec_rel)
    pins = dry_build(entries)
    ref = {}
    for r in R:
        en = pss._endpoint(r); ref[str(r['t'])] = {**en, 'dir': str(Path(r['dir']).relative_to(PKG)).replace('\\', '/'), 'qf': r['qf'], 'mu_band': r['mu_band'],
                                                   'mun': r['mun'], 'overrides': list(r['overrides'])}
    rec = {'record': 'S4c variable reference (register A52; PA-18 (c)/(d)): sealed; its sha256 is committed externally before the native S4c launch',
           'candidate': cid, 'candidate_sqrtJ_dec_profiled': P['sqrtJ_dec'], 'sources': src, 'profile_record': {'file': prof_rel, 'sha256': fsha(PKG / prof_rel)},
           'reprofile_equal_to_record': True, 'surrogate_verdict': sur['verdict'],
           'profiled': {k: P[k] for k in ('Qf_cm2', 'dQf_cm2', 'dV0_V', 'qf_anchor_cm2', 'dV0_from_anchor_V', 'mu_inf_cm2Vs', 'ell_nm', 'at_bound',
                                         'sqrtJ_dec', 'J', 'per_film', 'coverage_ok_95pct')},
           'profile_verdict': prof['verdict'], 'qualification': prof['qualification'], 'reference': ref, 'native_launch_values': nuis,
           'written_variables': [QF_KEY] + [MU_KEY(t) for t in FILMS], 'entries': entries, 'dry_build': pins,
           's4d': {'branch': S4D_BRANCH, 'overrides_added': IGZO_OVERRIDES,
                   'rule': ('A52 (g): the matrix S4D template keeps the surface tail and selects the mobility/contact runner-up; contacts were not run '
                            '(H-F v4 D4 DO NOT FIRE, Option A); of the two IGZO members only GAMMA0 -0.31 has a valid (OK) S3 adoption profile and a '
                            'native profiling check (S3-27 PASS); GAMMA0 +0.30 is UNVERIFIED (on-window coverage 92.7 %). Data-selected, reported as such.')},
           'tolerance_dec': S4C_TOL_DEC, 'frozen': dict(FROZEN), 'helpers': dict(HELPERS), 'settings': dict(SETTINGS),
           'wrapper_sha256': wrapper_sha(), 'code_sha256': pss.CODE_SHA,
           'labels': ('native curves COMPUTED (ATLAS 5.28); Q_f, mu_inf, ell FITTED (shared, exact-transformation profiling); N_s, W_T = ASSUMED LHS '
                      'design point selected by the profiled objective; ell at the 50 nm range bound (bound-limited, unqualified for acceptance, B4); '
                      'calibration, retrospective, never validation')}
    rec = pss.seal(rec)
    if Path(out).exists() and not force:
        old = json.loads(Path(out).read_text())
        if old.get('sha256') != rec['sha256']: raise SystemExit(f'refused: {out} exists with another seal ({str(old.get("sha256"))[:12]}); never overwritten')
    Path(out).write_text(json.dumps(rec, indent=1, default=float))
    return rec


# ------------------------------------------------------------------------------------------------ confirm (S4c)
def native_files(d):
    """(b)/(c) native digests: device.in and material_model_used.json text sha256 (= RUN_INDEX deck_sha256 / model_sha256 convention),
    terminal_currents.csv byte sha256"""
    d = Path(d); dk, mm, tc = d / 'device.in', d / 'material_model_used.json', d / 'terminal_currents.csv'
    return {'deck_sha256': tsha(dk.read_text()) if dk.is_file() else None, 'model_sha256': tsha(mm.read_text()) if mm.is_file() else None,
            'terminal_currents_sha256': fsha(tc) if tc.is_file() else None}


def override_difference(native_ov, ref_ov):
    """keys of the overrides that differ between the native and the reference run (symmetric difference of 'key=value' strings)"""
    return sorted({_okey(o) for o in set(native_ov) ^ set(ref_ov)})


def plan_problems(stage, rec, root=PKG):
    """(b) the route plan of this stage carries exactly the record's entries (verbatim keys); (problems, plan sha256)"""
    p = Path(root) / PLANS[stage]
    if not p.is_file(): return [f'{PLANS[stage]} missing'], None
    plan = json.loads(p.read_text()); want = [rec['entries'][entry_id(stage, t)] for t in FILMS]; bad = []
    got = plan.get('runs', [])
    if [e.get('id') for e in got] != [e['id'] for e in want]: bad.append(f'{PLANS[stage]} ids {[e.get("id") for e in got]}')
    for e, w in zip(got, want):
        for k in ('id', 'thickness', 'label', 'overrides', 'timeout'):
            if e.get(k) != w[k]: bad.append(f'{PLANS[stage]} {w["id"]}: {k} differs from the record')
    if plan.get('runnable') is not True or 'gates' in plan or 'state_only' in plan: bad.append(f'{PLANS[stage]}: runnable / gates / state_only not as registered')
    return bad, fsha(p)


def confirm_film(native, reference, rec, t, checker=None, files=None):
    """one film: (a) eligibility (frozen _endpoint), (b) settings, (c) digests, (d) variable reference, (f) the frozen check. native and
    reference are records of profile_s4s5.load (or synthetic dicts in tests). Returns a dict with verdict PASS / FAIL / UNKNOWN (...)."""
    import profile_s4s5 as pss
    k = entry_id('S4c', t); e = rec['entries'][k]; why = []
    en, er = pss._endpoint(native), pss._endpoint(reference)
    # role / film / reference binding
    if native.get('label') != e['label'] or abs(float(native.get('t', -1)) - t) > 1e-9: why.append(f'native is {native.get("label")} at {native.get("t")} nm, not {e["label"]}')
    rr = rec['reference'][str(t)]
    if reference.get('run_id') != rr['run_id'] or reference.get('label') != rr['label'] or er['digest'] != rr['digest']:
        why.append(f'reference {reference.get("run_id")} is not the sealed reference {rr["run_id"]} (label or frozen digest differs)')
    nf = (files or native_files)(native.get('dir', ''))
    out = {'film_nm': t, 'entry': k, 'native': {**en, **nf}, 'reference': er, 'settings': {}, 'variable_reference': {}, 'check': None}
    if why: out['verdict'] = 'REFUSED: ' + '; '.join(why); return out
    if not (en['eligible'] and er['eligible']):
        out['verdict'] = 'UNKNOWN (endpoint not eligible: ' + ' | '.join(f'{x["run_id"]}: {"; ".join(x["problems"])}' for x in (en, er) if not x['eligible']) + ')'
        return out
    # (b) settings
    pin = rec['dry_build'][k]; st = out['settings']
    st['deck_sha256_equal_pin'] = nf['deck_sha256'] == pin['deck_sha256']
    st['model_sha256_equal_pin'] = nf['model_sha256'] == pin['model_sha256']
    st['overrides_equal_entry'] = list(native.get('overrides') or []) == e['overrides']
    diff = override_difference(native.get('overrides') or [], reference.get('overrides') or [])
    st['override_keys_differing_from_reference'] = diff
    st['only_written_variables'] = set(diff) <= {QF_KEY, MU_KEY(t)}
    bad = [x for x in ('deck_sha256_equal_pin', 'model_sha256_equal_pin', 'overrides_equal_entry', 'only_written_variables') if not st[x]]
    # (d) variable reference: the values actually written equal the sealed profiled values (6-significant-figure rounding)
    P = rec['profiled']; nv = rec['native_launch_values']['per_film'][str(t)]
    vr = out['variable_reference']; vr['candidate'] = rec['candidate']; vr['record_sha256'] = rec['sha256']
    vr['Qf_written_cm2'] = native.get('qf'); vr['Qf_profiled_cm2'] = P['Qf_cm2']
    vr['mu_band_written_cm2Vs'] = native.get('mu_band'); vr['mu_band_profiled_cm2Vs'] = nv['mu_band_cm2Vs']
    vr['mun_scale_written'] = native['mu_band'] / reference['mu_band'] if native.get('mu_band') and reference.get('mu_band') else None
    vr['mun_scale_profiled'] = P['per_film'][str(t)]['mun_scale']
    vr['dQf_written_cm2'] = (native['qf'] - reference['qf']) if native.get('qf') is not None and reference.get('qf') is not None else None
    vr['dQf_profiled_cm2'] = P['Qf_cm2'] - reference['qf'] if reference.get('qf') is not None else None
    ok_v = (vr['Qf_written_cm2'] is not None and abs(vr['Qf_written_cm2'] - P['Qf_cm2']) <= REL_TOL * abs(P['Qf_cm2'])
            and vr['mu_band_written_cm2Vs'] is not None and abs(vr['mu_band_written_cm2Vs'] - nv['mu_band_cm2Vs']) <= REL_TOL * abs(nv['mu_band_cm2Vs'])
            and vr['mun_scale_written'] is not None and abs(vr['mun_scale_written'] - vr['mun_scale_profiled']) <= REL_TOL * abs(vr['mun_scale_profiled']))
    vr['written_equal_profiled_rel_1e-5'] = bool(ok_v)
    if not ok_v: bad.append('variable reference (written Q_f / mu_band differ from the sealed profiled values)')
    if bad: out['verdict'] = 'REFUSED: native run does not carry the registered S4c settings: ' + ', '.join(bad); return out
    # (f) the unchanged profile_shared.check through the frozen _ps_check (0.01 dec on every J-window point)
    chk = (checker or pss._ps_check)(native, reference)
    out['check'] = {kk: chk.get(kk) for kk in KEEP}
    ex = [x for x in ('other_material_differences', 'solver_geometry_override_differences', 'exactness_breakers') if chk.get(x)]
    cv = str(chk.get('verdict'))
    if ex: out['verdict'] = f'UNKNOWN (not a pure written-variable pair: {ex}; check verdict {cv[:80]})'
    elif not (chk.get('dQf_cm2') is not None and vr['dQf_written_cm2'] is not None and abs(chk['dQf_cm2'] - vr['dQf_written_cm2']) <= 1e-6 * max(1.0, abs(vr['dQf_written_cm2']))
              and chk.get('mun_scale') is not None and abs(chk['mun_scale'] - vr['mun_scale_written']) <= 1e-9 * abs(vr['mun_scale_written'])):
        out['verdict'] = 'UNKNOWN (the frozen check used other dQf / MUN scale than the written values)'
    else:
        out['verdict'] = 'PASS' if cv.startswith('PASS') else 'FAIL' if cv.startswith('FAIL') else f'UNKNOWN (check: {cv[:100]})'
    return out


def overall(films):
    v = [f['verdict'] for f in films]
    if v and all(x == 'PASS' for x in v): return 'PASS: profiled and native agree within 0.01 dec on every J-window point at all three films'
    if any(x == 'FAIL' for x in v):
        return ('FAIL: profiled vs native > 0.01 dec on a J-window point at ' + ', '.join(f'{f["film_nm"]} nm' for f in films if f['verdict'] == 'FAIL')
                + ' -> the native result is reported and the profiling is audited before S5 (CAMPAIGN_DESIGN l.327)')
    return 'UNKNOWN (' + '; '.join(f'{f["film_nm"]} nm: {f["verdict"][:120]}' for f in films if f['verdict'] != 'PASS') + ')'


def confirm(native_dirs, committed, out=CONFIRM_OUT, loader=None, checker=None):
    ps, pss, ce = frozen_modules()
    rec = committed_record(json.loads(RECORD.read_text()), committed)
    pb, psha = plan_problems('S4c', rec)
    if pb: raise SystemExit('refused: S4c route plan: ' + '; '.join(pb))
    loader = loader or pss.load
    N = [loader(d) for d in native_dirs]; N.sort(key=lambda r: r['t'])
    if [r['t'] for r in N] != list(FILMS): raise SystemExit(f'refused: the native runs are not one per film 2.0 / 6.3 / 13.2 nm ({[r["t"] for r in N]})')
    REF = {t: loader(rec['reference'][str(t)]['dir']) for t in FILMS}
    films = [confirm_film(n, REF[n['t']], rec, n['t'], checker) for n in N]
    res = {'record': 'S4c native confirmation (register A52; PA-18 wrapper around the unchanged profile_shared.check)', 'candidate': rec['candidate'],
           'variable_reference_sha256': rec['sha256'], 'plan': {'file': PLANS['S4c'], 'sha256': psha}, 'films': films, 'verdict': overall(films),
           'tolerance_dec': S4C_TOL_DEC, 'settings_pins': dict(SETTINGS), 'frozen': dict(FROZEN), 'wrapper_sha256': wrapper_sha(), 'code_sha256': pss.CODE_SHA}
    # native result (reported in every case; CAMPAIGN_DESIGN 5.2 / l.327): frozen profile_films on the native triple (start = as launched)
    # and the 5.3 acceptance on native sampling (frozen acceptance, kind 'native')
    if all(pss.is_eligible(r) for r in N):   # report only: an error here never changes or hides the verdict above
        info, _ = ce.measured()
        try:
            pn = pss.profile_films(N, info, tag='S4C'); s0 = pn['start']['sqrtJ_dec']
            res['native_profile'] = {'start_sqrtJ_dec_native_as_launched': s0, 'start_per_film': pn['start']['per_film'],
                                     'reprofiled': {k: pn['profiled'][k] for k in ('sqrtJ_dec', 'Qf_cm2', 'dV0_V', 'mu_inf_cm2Vs', 'ell_nm', 'at_bound', 'per_film')},
                                     'verdict': pn['verdict'], 'qualification': pn['qualification'], 'warnings': pn['warnings'],
                                     'sqrtJ_native_minus_profiled_dec': None if s0 is None else s0 - rec['profiled']['sqrtJ_dec']}
        except (SystemExit, Exception) as e: res['native_profile'] = {'verdict': f'REFUSED or failed: {type(e).__name__}: {str(e)[:300]}'}
        acc = {}
        for r in N:
            try: acc[str(r['t'])] = pss.acceptance(r['vg'], r['i'], r['t'], info, kind='native')
            except (SystemExit, Exception) as e: acc[str(r['t'])] = {'verdict': f'unresolved (extraction failed: {type(e).__name__}: {str(e)[:200]})'}
        res['acceptance_5_3_native'] = acc
        res['acceptance_note'] = ('CAMPAIGN_DESIGN 5.3 (ASSUMED engineering limits) on the native S4c curves; the S4a abort already reports the shared model '
                                  'as failed; ell is at its 50 nm bound (the profile is bound-limited, B4); calibration, retrospective')
    res['labels'] = rec['labels']
    res = pss.seal(res)
    if out is not None: Path(out).write_text(json.dumps(res, indent=1, default=float))
    return res


# ------------------------------------------------------------------------------------------------ S4d read-out
def load_f_gate():
    p = HERE / 'prelaunch_gate_c10_f.py'
    if fsha(p) != HELPERS['prelaunch_gate_c10_f.py']: raise SystemExit('refused: prelaunch_gate_c10_f.py differs from its pin')
    spec = importlib.util.spec_from_file_location('prelaunch_gate_c10_f_pinned', p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def activation_of(r):
    """S4d: post_run_checks.activation (ACTIVE_AS_REQUESTED) and IGZO.TOKYO in regions 1 and 2 (the A48 (b) block reader)"""
    import post_run_checks as prc
    d = Path(r['dir']); ex = json.loads((d / 'execution.json').read_text()); ex['model_file'] = prc.model_file_of(ex['run_id'])
    txt = (d / 'deckbuild.out').read_text(errors='replace') if (d / 'deckbuild.out').exists() else ''
    st = prc.activation(d, ex, txt); s2, lines = load_f_gate().activation(d / 'deckbuild.out')
    return {'status': st['status'], 'missing': st['missing'], 'regions_1_2': s2, 'lines': lines,
            'ok': st['status'] == 'ACTIVE_AS_REQUESTED' and s2 == 'ACTIVE'}


def s4d_verdict(eligible, active, settings_ok, adopt):
    """registered S4d read-out (A52 (g))"""
    if not settings_ok: return 'REFUSED: an S4d run does not carry the registered entry (deck, material or overrides)'
    if not eligible: return 'UNKNOWN (an S4d run or a reference run is not eligible: C3 run validity)'
    if not active: return 'UNKNOWN (IGZO.TOKYO not shown ACTIVE in regions 1 and 2, or an option not ACTIVE_AS_REQUESTED)'
    if adopt is None: return 'UNKNOWN (adoption arithmetic refused)'
    v = str(adopt.get('verdict'))
    if v.startswith('UNVERIFIED'): return 'UNRESOLVED (a profile is UNVERIFIED: coverage < 95 % or optimizer not converged)'
    if adopt.get('arithmetic_pass'):
        return ('DOES NOT SURVIVE: the runner-up IGZO.TOKYO GAMMA0 -0.31 passes the S3 adoption arithmetic at the calibrated (N_s, W_T) (sqrt(J) gain >= 0.03 dec, '
                'no film worse by > 0.03 dec): reported as a model-form finding; no re-calibration; S5 branch rule unchanged')
    return ('SURVIVES: the runner-up IGZO.TOKYO GAMMA0 -0.31 does not pass the S3 adoption arithmetic at the calibrated (N_s, W_T): the branch choice '
            'made at the start values (nothing adopted) survives calibration')


def s4d(native_dirs, committed, out=S4D_OUT, loader=None, act=None, adopt_fn=None):
    ps, pss, ce = frozen_modules()
    rec = committed_record(json.loads(RECORD.read_text()), committed)
    pb, psha = plan_problems('S4d', rec)
    if pb: raise SystemExit('refused: S4d route plan: ' + '; '.join(pb))
    loader = loader or pss.load
    N = [loader(d) for d in native_dirs]; N.sort(key=lambda r: r['t'])
    if [r['t'] for r in N] != list(FILMS): raise SystemExit('refused: the S4d runs are not one per film')
    REF = [loader(rec['reference'][str(t)]['dir']) for t in FILMS]
    rows, settings_ok = [], True
    for r in N:
        t = r['t']; k = entry_id('S4d', t); e = rec['entries'][k]; nf = native_files(r.get('dir', '')) if loader is pss.load else (r.get('files') or {})
        st = {'label': r.get('label') == e['label'], 'overrides_equal_entry': list(r.get('overrides') or []) == e['overrides'],
              'deck_sha256_equal_pin': nf.get('deck_sha256') == rec['dry_build'][k]['deck_sha256'],
              'model_sha256_equal_pin': nf.get('model_sha256') == rec['dry_build'][k]['model_sha256']}
        settings_ok &= all(st.values())
        rows.append({'film_nm': t, 'entry': k, 'endpoint': pss._endpoint(r), 'files': nf, 'settings': st})
    elig = all(pss.is_eligible(r) for r in N + REF)
    acts = {}
    if elig and settings_ok:
        for r in N: acts[str(r['t'])] = (act or activation_of)(r)
    active = bool(acts) and all(a['ok'] for a in acts.values())
    adopt = None
    if elig and settings_ok and active:
        info, _ = ce.measured()
        try: adopt = (adopt_fn or pss.adopt_films)(N, REF, info)
        except (SystemExit, Exception) as e: adopt = None; rows.append({'adopt_refused': f'{type(e).__name__}: {str(e)[:300]}'})
    res = {'record': 'S4d runner-up branch read-out (register A52 (g); frozen profile_s4s5.adopt_films = the S3 adoption arithmetic)',
           'branch': S4D_BRANCH, 'candidate': rec['candidate'], 'variable_reference_sha256': rec['sha256'], 'plan': {'file': PLANS['S4d'], 'sha256': psha},
           'runs': rows, 'activation': acts,
           'adoption': None if adopt is None else {'sqrtJ_gain_dec': adopt['sqrtJ_gain_dec'], 'per_film_worsening_dec': adopt['per_film_worsening_dec'],
                                                   'arithmetic_pass': adopt['arithmetic_pass'], 'verdict': adopt['verdict'],
                                                   'branch_profiled': {k: adopt['branch']['profiled'][k] for k in ('sqrtJ_dec', 'Qf_cm2', 'dV0_V', 'mu_inf_cm2Vs', 'ell_nm', 'at_bound', 'per_film')},
                                                   'branch_verdict': adopt['branch']['verdict'], 'branch_qualification': adopt['branch'].get('qualification'),
                                                   'base_sqrtJ_dec': adopt['base']['profiled']['sqrtJ_dec'], 'base_verdict': adopt['base']['verdict'],
                                                   'base_equals_record': abs(adopt['base']['profiled']['sqrtJ_dec'] - rec['profiled']['sqrtJ_dec']) <= 1e-9},
           'verdict': s4d_verdict(elig, active, settings_ok, adopt), 'wrapper_sha256': wrapper_sha(), 'code_sha256': pss.CODE_SHA,
           'labels': ('S4d native curves COMPUTED (ATLAS 5.28); re-profiled Q_f, mu_inf, ell FITTED (exact IGZO profiling, S3-27 PASS); branch choice '
                      'data-selected; calibration, retrospective, never validation')}
    res = pss.seal(res)
    if out is not None: Path(out).write_text(json.dumps(res, indent=1, default=float))
    return res


# ------------------------------------------------------------------------------------------------ CLI
def _opt(argv, k):
    return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else None


def main(argv):
    if not argv or argv[0] in ('-h', '--help'): print(__doc__); return 2
    cmd = argv[0]; pos = [a for i, a in enumerate(argv[1:], 1) if not a.startswith('--') and argv[i - 1] != '--committed']
    try:
        if cmd == 'pins':
            bad = pin_problems(); print('PINS OK' if not bad else 'PINS DIFFER: ' + '; '.join(bad)); return 0 if not bad else 3
        if cmd == 'freeze':
            rec = freeze(); print(json.dumps({'record': str(RECORD.relative_to(PKG)), 'sha256': rec['sha256'], 'candidate': rec['candidate'],
                                               'Qf_cm2': rec['profiled']['Qf_cm2'], 'dry_build': rec['dry_build']}, indent=1)); return 0
        if cmd in ('confirm', 's4d'):
            if len(pos) != 3: print(f'{cmd} needs three run directories (2.0, 6.3, 13.2 nm) and --committed SHA256'); return 2
            res = (confirm if cmd == 'confirm' else s4d)(pos, _opt(argv, '--committed'))
            print(json.dumps({'verdict': res['verdict'], 'sha256': res['sha256'],
                              **({'films': {f['film_nm']: f['verdict'] for f in res['films']}} if cmd == 'confirm' else {})}, indent=1))
            v = res['verdict']
            if cmd == 'confirm': return 0 if v.startswith('PASS') else 1 if v.startswith('FAIL') else 3
            return 0 if v.startswith(('SURVIVES', 'DOES NOT SURVIVE')) else 3
    except SystemExit as e:
        print(f'REFUSED: {e}'); return 3
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
