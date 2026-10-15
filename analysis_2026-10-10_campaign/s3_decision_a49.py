#!/usr/bin/env python3
"""Register A49 (2026-10-15; no Codex review, D-63; Claude under D-59): the 0-LAUNCH S3 decision before S4a. NO simulator call.

It only wires the registered roles to FROZEN code (sha256 checked before import) and writes three JSON files:
  1. profile/s4s5_confirm_<role>_<native>_vs_<reference>.json: sealed native-confirmation records S1-07 (run_0074 vs run_0061) and
     S3-27 (run_0103 vs run_0102) by profile_s4s5.native_confirmation (unchanged profile_shared.check, 0.01 dec on every J-window point);
  2. register_scores/hf_v4_A49.json: the H-F v4 score (hf_score_draft.py 96a2147e): D1 two-film reference, D2 baseline shape, D3 IGZO.TOKYO
     (S3-27 gated), D4 contact trigger (S1-01, S3-10, S3-12), D5 falsification (baseline routes + IGZO triple; contacts UNKNOWN), S5 note.
     Written BEFORE step 3 runs (register order: the registered prediction is scored by its frozen code first);
  3. profile/s3_adoption_A49.json: the S3 adoption decision (CAMPAIGN_DESIGN section 6, S3 block, frozen): profile_shared.adopt (958c3605,
     the design-named tool) for the four branch triples against the base triple S0-01/S1-01/S1-02, the caller flags (converged, activation,
     not a pure shift/scale effect), the group choice, and the S4a form it selects (A49 (c): N / T / I / TI), sealed with profile_s4s5.seal.

Every number in the outputs is computed by the frozen functions; this file computes only the decision logic of A49 (b) (decide(),
pure_shift_or_scale()) and the form mapping of A49 (c) (s4a_form()). Tests: test_s3_decision_a49.py (synthetic rows only).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B analysis_2026-10-10_campaign/s3_decision_a49.py run        (package root; the one registered invocation)
    & "<venv>\\Scripts\\python.exe" -I -B analysis_2026-10-10_campaign/s3_decision_a49.py pins       (pin check only, nothing read)
Exit codes: 0 done; 1 a pin, role or input check failed (nothing scored); 2 usage.
"""
import csv
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
RUNS = PKG / 'results' / 'runs'
INDEX = PKG / 'results' / 'RUN_INDEX.csv'
INVENTORY = PKG / 'config' / 'sealed_runs.json'
F_GATE = HERE / 'prelaunch_gate_c10_f.py'
OUT_HF = HERE / 'register_scores' / 'hf_v4_A49.json'
OUT_ADOPT = HERE / 'profile' / 's3_adoption_A49.json'
FILMS = (2.0, 6.3, 13.2)
TAG = {2.0: '2p0', 6.3: '6p3', 13.2: '13p2'}

PINS = {   # frozen code (A49 (a) 1); checked before any import of these modules
    'score_register.py': 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a',
    'hf_score_draft.py': '96a2147eae6a07a2ea0afbed2d63476283c2d5bca3ffdfd7f829f248af3a1c81',
    'profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',
    'profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
    'post_run_checks.py': '39d3d51d3b2470b1396196bcfce34dc4a8f0a6acd3bcb2a213001dc5ec3ed91f',
    'campaign_extract.py': '1f6f324a0841d50bb20baf7f94b6444d688aaf4cbdf71707594a06f26e3e63ba',
    'campaign_tools.py': '3b0403d9c5cc5423cb80dabc3765f9a781b7a06b512082b6f210971a9417ab0d',
    'prelaunch_gate_c10_f.py': 'd0baaca36b77cbe95c598a641f0a89366d4e2d496cf59a4935aa0ead4de1741d',   # A48 (b) block reader only
}

# registered roles -> (run id, label, film); run ids from RUN_INDEX (checked: first row of each id carries this label)
ROLE = {'S0-01': ('run_0061', 'c10_s0_01_2p0', 2.0), 'S1-01': ('run_0068', 'c10_s1_01_6p3', 6.3), 'S1-02': ('run_0069', 'c10_s1_02_13p2', 13.2),
        'S1-07': ('run_0074', 'c10_s1_07_2p0', 2.0),
        'S3-12': ('run_0102', 'c10_s3_12_6p3', 6.3), 'S3-27': ('run_0103', 'c10_s3_27_6p3', 6.3), 'S3-11': ('run_0104', 'c10_s3_11_2p0', 2.0),
        'S3-13': ('run_0105', 'c10_s3_13_13p2', 13.2), 'S3-15': ('run_0106', 'c10_s3_15_6p3', 6.3), 'S3-14': ('run_0107', 'c10_s3_14_2p0', 2.0),
        'S3-16': ('run_0108', 'c10_s3_16_13p2', 13.2), 'S3-10': ('run_0109', 'c10_s3_10_6p3', 6.3), 'S3-05': ('run_0110', 'c10_s3_05_6p3', 6.3),
        'S3-06': ('run_0111', 'c10_s3_06_13p2', 13.2), 'S3-08': ('run_0112', 'c10_s3_08_6p3', 6.3), 'S3-09': ('run_0113', 'c10_s3_09_13p2', 13.2)}
SEALED_ROLES = ('S3-12', 'S3-27', 'S3-11', 'S3-13', 'S3-15', 'S3-14', 'S3-16', 'S3-10', 'S3-05', 'S3-06', 'S3-08', 'S3-09')
BASE = ('S0-01', 'S1-01', 'S1-02')
# A49 (b): branch triples (2.0, 6.3, 13.2); S3-04 and S3-07 are statement-identical to S0-01 and were not launched (A45 (k)): run_0061
BRANCHES = [
    {'name': 'tail bulk (S3-04=S0-01, S3-05, S3-06)', 'group': 'tail', 'form': 'bulk', 'roles': ('S0-01', 'S3-05', 'S3-06'), 'g0': None},
    {'name': 'tail 50:50 (S3-07=S0-01, S3-08, S3-09)', 'group': 'tail', 'form': 'mixed50', 'roles': ('S0-01', 'S3-08', 'S3-09'), 'g0': None},
    {'name': 'IGZO.TOKYO GAMMA0 -0.31 (S3-11, S3-12, S3-13)', 'group': 'mobility', 'form': 'igzo', 'roles': ('S3-11', 'S3-12', 'S3-13'), 'g0': -0.31},
    {'name': 'IGZO.TOKYO GAMMA0 +0.30 (S3-14, S3-15, S3-16)', 'group': 'mobility', 'form': 'igzo', 'roles': ('S3-14', 'S3-15', 'S3-16'), 'g0': 0.30}]
PURE_TOL_DEC = 0.01   # A49 (b) (4): pure shift/scale iff the per-film shape-only residual changes by <= 0.01 dec at all three films
EQ_TOL_DEC = 1e-9     # A49 (b): profile_shared.adopt and profile_s4s5.adopt_films must agree on the IGZO -0.31 triple
S4A_LAUNCHES = {'N': 42, 'T': 43, 'I': 42, 'TI': 45}   # A49 (c)


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_pins():
    bad = [f'{f}: {fsha(HERE / f)[:8]} != {h[:8]}' for f, h in PINS.items() if fsha(HERE / f) != h]
    return bad


def run_dir(role):
    rid, lab, t = ROLE[role]; return RUNS / f'{rid}_{TAG[t]}_{lab}'


def check_inputs():
    """RUN_INDEX run_id/label columns only (first row per id); run directories exist; sealed roles are in config/sealed_runs.json"""
    bad, first = [], {}
    with INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh): first.setdefault(r['run_id'], r['label'])
    for k, (rid, lab, t) in ROLE.items():
        if first.get(rid) != lab: bad.append(f'{k}: RUN_INDEX {rid} label {first.get(rid)!r} != {lab}')
        if not run_dir(k).is_dir(): bad.append(f'{k}: run directory {run_dir(k).name} missing')
    inv = {x['run_id']: x for x in json.loads(INVENTORY.read_text())['runs']}
    for k in SEALED_ROLES:
        rid, lab, _ = ROLE[k]; x = inv.get(rid) or {}
        if x.get('label') != lab or x.get('entry') != k: bad.append(f'{k}: {rid} not in config/sealed_runs.json as {lab} / {k}')
    return bad


# ------------------------------------------------------------------------------------------------ A49 (b) decision logic (tested)
def pure_shift_or_scale(branch_profile, base_profile, tol=PURE_TOL_DEC):
    """A49 (b) (4): True iff, at all three films, the per-film free shift + scale (shape-only) residual of the branch equals the base's within
    tol dec (profile_shared.profile 'diagnostic_shape_only'); None if a value is missing (then the flag is not established)"""
    a, b = branch_profile.get('diagnostic_shape_only') or {}, base_profile.get('diagnostic_shape_only') or {}
    d = []
    for t in FILMS:
        x, y = (a.get(t) or a.get(str(t)) or {}).get('shape_only_sqrtJ_dec'), (b.get(t) or b.get(str(t)) or {}).get('shape_only_sqrtJ_dec')
        if x is None or y is None or not (math.isfinite(x) and math.isfinite(y)): return None, d
        d.append(abs(x - y))
    return all(v <= tol for v in d), d


def candidate_ok(row):
    """A49 (b) (1)-(4): adoption candidate iff ARITHMETIC PASS (no UNVERIFIED/APPROXIMATE prefix), converged, activation confirmed and
    not a pure shift/scale effect (each flag must be established True / False as required; None never passes)"""
    return (str(row.get('arithmetic', '')).startswith('ARITHMETIC PASS') and row.get('converged') is True
            and row.get('activation_ok') is True and row.get('pure_shift_or_scale') is False)


def decide(rows):
    """group choice (CAMPAIGN_DESIGN S3 block): per group the candidate with the lowest profiled sqrt(J); at most two branches (tail law,
    mobility); returns {'tail': row or None, 'mobility': row or None}"""
    chosen = {}
    for r in rows:
        if not candidate_ok(r): continue
        g = r['group']
        if g not in ('tail', 'mobility'): raise SystemExit(f'unknown group {g}')
        if g not in chosen or r['sqrtJ_dec'] < chosen[g]['sqrtJ_dec'] - 1e-15 or (
                abs(r['sqrtJ_dec'] - chosen[g]['sqrtJ_dec']) <= 1e-15 and r['name'] < chosen[g]['name']):
            chosen[g] = r
    return {'tail': chosen.get('tail'), 'mobility': chosen.get('mobility')}


def s4a_form(choice):
    """A49 (c): the S4a form selected by the decision"""
    t, m = choice.get('tail'), choice.get('mobility')
    code = 'TI' if (t and m) else 'T' if t else 'I' if m else 'N'
    return {'form': code, 'tail_law': t['form'] if t else 'surface', 'mobility': 'igzo_tokyo' if m else 'constant',
            'gamma0_seed': m['g0'] if m else None, 'lhs': '3-D seed 20261011 (if_igzo_branch_adopted)' if m else '2-D seed 20261010',
            'launches': S4A_LAUNCHES[code],
            's4a_01': {'N': 'reused: run_0061 / run_0068 / run_0069 (PA-12)',
                       'T': 'S4A-01-2p0 launched; 6.3 / 13.2 nm reused from the adopted tail triple (PA-12)',
                       'I': 'reused: the better-GAMMA0 S3 triple (PA-12)',
                       'TI': 'launched at (4e12 cm^-2, 0.040 eV, the better GAMMA0) with the adopted tail law'}[code]}


# ------------------------------------------------------------------------------------------------ the registered invocation
def _jsonable(x):
    if isinstance(x, dict): return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [_jsonable(v) for v in x]
    if hasattr(x, 'item') and not isinstance(x, (str, bytes)):
        try: return x.item()
        except (ValueError, AttributeError): return [_jsonable(v) for v in x.tolist()]
    return x


def _default(o):
    try: return float(o)
    except (TypeError, ValueError): return str(o)


def load_f_gate():
    spec = importlib.util.spec_from_file_location('prelaunch_gate_c10_f_pinned', F_GATE); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


def run():
    bad = check_pins()
    if bad: print('REFUSED: frozen-code pins differ:', bad); return 1
    bad = check_inputs()
    if bad: print('REFUSED: inputs:', bad); return 1
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    import campaign_extract as ce
    import profile_shared as ps
    import profile_s4s5 as P
    import hf_score_draft as H
    import post_run_checks as prc
    if P.CODE_SHA != PINS['profile_s4s5.py']: print('REFUSED: profile_s4s5.CODE_SHA differs'); return 1
    FG = load_f_gate()
    info, _ = ce.measured()
    R = {k: P.load(str(run_dir(k))) for k in ROLE}
    elig = {k: {'run_id': R[k]['run_id'], 'label': R[k]['label'], **{x: R[k]['eligibility'].get(x) for x in
                ('eligible', 'problems', 'status', 'returncode', 'timed_out', 'finished', 'simulator_errors', 'convergence_flags',
                 'requested_points', 'exported_points')}} for k in ROLE}

    # ---- step 1: sealed native-confirmation records
    rec = {}
    for role, nat, ref in (('S1-07', 'S1-07', 'S0-01'), ('S3-27', 'S3-27', 'S3-12')):
        try: rec[role] = P.native_confirmation(R[nat], R[ref], role)
        except SystemExit as e: rec[role] = None; print(f'[confirmation {role}] refused: {e}')
        if rec[role] is not None:
            fn = P.OUT / f's4s5_confirm_{role}_{ROLE[nat][0]}_vs_{ROLE[ref][0]}.json'; P.OUT.mkdir(exist_ok=True)
            fn.write_text(json.dumps(rec[role], indent=1, default=_default))
    # ---- step 2: H-F v4 (frozen definitions), written before step 3
    def guard(f, *a):
        try: return f(*a)
        except SystemExit as e: return {'verdict': f'unresolved (refused: {str(e)[:300]})'}
    base = {2.0: R['S0-01'], 6.3: R['S1-01'], 13.2: R['S1-02']}; igzo = {2.0: R['S3-11'], 6.3: R['S3-12'], 13.2: R['S3-13']}
    hf = {'driver': 'analysis_2026-10-10_campaign/s3_decision_a49.py (register A49 (a))', 'driver_sha256': fsha(__file__), 'frozen_pins': PINS,
          'roles': {k: ROLE[k][0] for k in ROLE}, 'run_eligibility': elig}
    hf['D1'] = guard(H.two_film_reference, R['S0-01'], R['S1-02'], R['S1-01'], info)
    hf['D2'] = guard(H.baseline_shape, R['S1-01'], info)
    hf['D3'] = guard(H.igzo_prediction, base, igzo, rec['S3-27'], info)
    shapes = {}
    for k in ('S1-01', 'S3-10', 'S3-12'):
        try: shapes[k] = H.shape_fit(R[k], info[6.3])
        except SystemExit as e: shapes[k] = {'film_nm': 6.3, 'label': R[k].get('label'), 'valid': False, 'why_invalid': f'refused: {e}'}
    hf['D4_shape_fits'] = shapes
    hf['D4'] = guard(H.contact_trigger, shapes, rec['S3-27'])
    presc = H.prescribed_branches(hf['D4'])
    bt = guard(H.profiled_triple_acceptance, [base[t] for t in FILMS], info, rec['S1-07'], 'baseline')
    it = guard(H.profiled_triple_acceptance, [igzo[t] for t in FILMS], info, rec['S3-27'], 'IGZO')
    hf['D5_baseline_triple'] = bt; hf['D5_igzo_triple'] = it
    brs = [{'name': H.IGZO_BRANCH, 'triple': it if 'kind' in it else None}]
    if presc and H.CONTACT_BRANCH in presc: brs.append({'name': H.CONTACT_BRANCH, 'native_acceptance': None})
    hf['D5'] = guard(H.falsification, hf['D2'], bt if 'kind' in bt else None, brs, presc)
    hf['S5_fold_6p3'] = H.s5_fold_6p3()
    hf['confirmations'] = rec
    OUT_HF.parent.mkdir(exist_ok=True); OUT_HF.write_text(json.dumps(_jsonable(hf), indent=1, default=_default))
    print(f'[H-F v4] written {OUT_HF.relative_to(PKG)} sha256 {fsha(OUT_HF)[:12]}')

    # ---- step 3: S3 adoption (profile_shared.adopt) and caller flags
    rows = []
    base_dirs = [str(run_dir(k)) for k in BASE]
    for b in BRANCHES:
        dirs = [str(run_dir(k)) for k in b['roles']]
        row = {'name': b['name'], 'group': b['group'], 'form': b['form'], 'g0': b['g0'], 'roles': list(b['roles']),
               'runs': [ROLE[k][0] for k in b['roles']]}
        try:
            a = ps.adopt(dirs, base_dirs)
        except SystemExit as e:
            row.update(arithmetic=f'REFUSED: {e}', sqrtJ_dec=None, converged=None, activation_ok=None, pure_shift_or_scale=None); rows.append(row); continue
        row.update(arithmetic=a['verdict'], sqrtJ_dec=a['branch']['profiled']['sqrtJ_dec'], base_sqrtJ_dec=a['base']['profiled']['sqrtJ_dec'],
                   gain_dec=a['sqrtJ_gain_dec'], worsening_dec=a['per_film_worsening_dec'],
                   profiled={k: a['branch']['profiled'][k] for k in ('Qf_cm2', 'dV0_V', 'mu_inf_cm2Vs', 'ell_nm', 'coverage_ok_95pct', 'per_film')},
                   branch_verdict=a['branch']['verdict'], base_verdict=a['base']['verdict'], warnings=a['branch']['warnings'] + a['base']['warnings'])
        row['converged'] = all(P.is_eligible(R[k]) for k in b['roles'])
        act = {}
        for k in b['roles']:
            d = run_dir(k); ex = json.loads((d / 'execution.json').read_text()); ex['model_file'] = prc.model_file_of(ex['run_id'])
            txt = (d / 'deckbuild.out').read_text(errors='replace') if (d / 'deckbuild.out').exists() else ''
            st = prc.activation(d, ex, txt); act[k] = {'status': st['status'], 'missing': st['missing']}
            if b['form'] == 'igzo':
                s2, lines = FG.activation(d / 'deckbuild.out'); act[k]['regions_1_2'] = {'state': s2, 'lines': lines}
        row['activation'] = act
        row['activation_ok'] = all(v['status'] == 'ACTIVE_AS_REQUESTED' and v.get('regions_1_2', {'state': 'ACTIVE'})['state'] == 'ACTIVE' for v in act.values())
        pure, dev = pure_shift_or_scale(a['branch'], a['base'])
        row['pure_shift_or_scale'] = pure; row['shape_only_change_dec'] = dev
        row['shape_only'] = {'branch': a['branch']['diagnostic_shape_only'], 'base': a['base']['diagnostic_shape_only']}
        if b['form'] == 'igzo' and b['g0'] == -0.31:   # cross-check against the H-F v4 adoption profile (profile_s4s5.adopt_films)
            try:
                a2 = P.adopt_films([R[k] for k in b['roles']], [R[k] for k in BASE], info)
                row['cross_check_adopt_films'] = {'gain_dec': a2['sqrtJ_gain_dec'], 'abs_diff_gain_dec': abs(a2['sqrtJ_gain_dec'] - a['sqrtJ_gain_dec']),
                                                  'agree': abs(a2['sqrtJ_gain_dec'] - a['sqrtJ_gain_dec']) <= EQ_TOL_DEC}
            except SystemExit as e: row['cross_check_adopt_films'] = {'agree': None, 'refused': str(e)}
        rows.append(row)
    choice = decide(rows)
    s327, why327 = P.confirmation_status(rec['S3-27'], 'S3-27', P.run_digest(R['S3-12'])) if rec['S3-27'] else (None, 'missing')
    form = s4a_form(choice)
    xc = next((r.get('cross_check_adopt_films') for r in rows if r.get('cross_check_adopt_films') is not None), None)
    unresolved = xc is not None and xc.get('agree') is False
    dec = {'record': 'S3 adoption decision (register A49 (b); CAMPAIGN_DESIGN section 6 S3 block); data-selected model choice',
           'driver_sha256': fsha(__file__), 'frozen_pins': PINS, 'base_runs': [ROLE[k][0] for k in BASE], 'branches': rows,
           'chosen': {g: (r['name'] if r else None) for g, r in choice.items()},
           'S3_27': {'status': s327, 'why': why327,
                     'consequence': ('exact IGZO profiling' if s327 is True else 'IGZO profiling APPROXIMATE: every IGZO S4b candidate run natively (design 5.2)')},
           's4a_form': form, 'hf_v4_file_sha256': fsha(OUT_HF),
           'verdict': ('UNRESOLVED: profile_shared.adopt and profile_s4s5.adopt_films disagree on the IGZO -0.31 triple (stop; main-session item)'
                       if unresolved else f'DECIDED: S4a form {form["form"]} ({form["tail_law"]} tail, {form["mobility"]} mobility, LHS {form["lhs"]})'),
           'labels': 'profiled sqrt(J), gains and worsening: COMPUTED (ATLAS) curves profiled offline (FITTED shared Q_f, mu_inf, ell); '
                     'branch choice: data-selected model choice (reported as such)'}
    dec = P.seal(_jsonable(dec))
    OUT_ADOPT.write_text(json.dumps(dec, indent=1, default=_default))
    print(f'[S3 adoption] written {OUT_ADOPT.relative_to(PKG)} sha256 {fsha(OUT_ADOPT)[:12]} (record seal {dec["sha256"][:12]})')
    summ = {'H-F': {k: (hf[k].get('verdict') if isinstance(hf[k], dict) else None) for k in ('D1', 'D2', 'D3', 'D4', 'D5')},
            'S1-07': (rec['S1-07'] or {}).get('verdict'), 'S3-27': (rec['S3-27'] or {}).get('verdict'),
            'branches': [{k: r.get(k) for k in ('name', 'arithmetic', 'sqrtJ_dec', 'base_sqrtJ_dec', 'gain_dec', 'converged', 'activation_ok',
                                                  'pure_shift_or_scale')} for r in rows],
            'chosen': dec['chosen'], 'verdict': dec['verdict']}
    print(json.dumps(_jsonable(summ), indent=1, default=_default))
    return 0


def main(argv):
    if argv[:1] == ['pins']:
        bad = check_pins(); print('pins OK' if not bad else f'pins differ: {bad}'); return 0 if not bad else 1
    if argv[:1] == ['run']: return run()
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
