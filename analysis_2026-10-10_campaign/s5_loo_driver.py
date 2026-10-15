#!/usr/bin/env python3
"""S5 leave-one-film-out driver (register A53, 2026-10-16; implements CAMPAIGN_DESIGN l.279 / l.330-332 and PA-13 = A45 (e); no Codex review,
D-63; Claude under the delegation D-59 for the registration only). NO simulator call. It wires the registered S5 roles to the FROZEN code
(profile_s4s5.py 429b3a3f: loo_branch, load_archive, loo_select, loo_score, measured_training, seal; profile_shared.py 958c3605; score_register.py
c0f28bb9), checks every pin before importing, and writes only JSON records into analysis_2026-10-10_campaign/profile/s5_A53/. Every number in a
record is computed by the frozen functions; this file computes only (i) the caller flags of loo_branch restricted to the training films, (ii) the
fold archive (input list), (iii) the execution entries that carry a frozen proposal or a frozen held-out record into a deck, (iv) the dry builds
(run_campaign.current_deck_text / current_material_text, unchanged) and (v) the LOO-1/2/3 arithmetic on frozen outputs.

Fold order (register section 3 step 7 "the 6.3 nm fold first"; plan 2.8, the order of the last two ASSUMED): H6p3, H2p0, H13p2.
Per fold (A53 (b)-(f)):
  branch --held T   the S3 adoption rule on the two training films (frozen loo_branch) over the four A49 branch triples, base S0-01/S1-01/S1-02;
                    caller flags restricted to the training films (converged = frozen eligibility; activation = the A49 record; pure shift/scale =
                    the A49 rule (4) on the training films' single-film shape-only residuals); full-data choice = A49 (nothing adopted)
                    -> <F>_branch_spec.json (input list) and <F>_branch.json (the sealed frozen decision)
  next --held T     the k-th training candidate (k = 1..4): frozen loo_select on the fold archive (same branch: S4a archive A51 + the fold's
                    finished S5 candidates; changed branch: the A7 local design, the fold's candidates only); the proposal is launched at its
                    deck-rounded inputs and at the frozen native launch values (trust-region centre's profiled Q_f and mu_band on the training
                    films); STOP (no record) if the verdict is not a proposal, if an S4a candidate's training profile is not valid (the freeze
                    would be blocked, ruling b), if a fold candidate run is ineligible, or if the deck-rounded point is not distinct (frozen
                    _distinct_pair) -> <F>_t<k>.json (sealed): proposal, entries S5-<F>-<k>-<t>, dry builds
  freeze --held T   frozen loo_select with the four fold candidates -> the frozen best / runner-up records (sealed by the frozen code) and
                    <F>_pred.json (sealed): entries S5-<F>-PRED-best / -runner_up at the held-out film carrying exactly the frozen values
  score --held T    frozen loo_score of both native held-out runs against the frozen records whose files are committed in git HEAD (the
                    external commitment, made before the PRED launch) -> <F>_score.json (sealed) with the LOO-1 quantities
  report            LOO-1 table, LOO-2 floor, LOO-3 jackknife (diagnostic), early-exit evaluation -> s5_report_A53.json (sealed)
  stop --held T --reason R   a registered fold stop (A53 (h)) -> <F>_stop.json (sealed): no further launch in this fold
  pins | status     pin check only | per-fold state (records present, RUN_INDEX run ids and finish flags; nothing else read)

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"      (package root, project venv)
    & <venv python> -I -B analysis_2026-10-10_campaign/s5_loo_driver.py <command> [--held 6.3|2.0|13.2]
Exit codes: 0 done; 2 usage; 3 refused / STOP / unresolved (nothing written, or a STOP record only where stated).
Labels: native curves COMPUTED (ATLAS 5.28); profiled Q_f, mu_inf, ell FITTED (training films only); N_s, W_T [GAMMA0] FITTED by the frozen
surrogate selection (training films only); held-out errors COMPUTED against MEASURED curves; retrospective transferability within already-seen
devices (n = 3, one device per film), never validation or prediction (PA-13).
"""
import csv
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
RUNS = PKG / 'results' / 'runs'
INDEX = PKG / 'results' / 'RUN_INDEX.csv'
OUTD = HERE / 'profile' / 's5_A53'
AMENDMENT = 'A53 (D-76)'

FROZEN = {'profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',
          'profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
          'score_register.py': 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a'}
HELPERS = {'campaign_extract.py': '1f6f324a0841d50bb20baf7f94b6444d688aaf4cbdf71707594a06f26e3e63ba',
           'campaign_tools.py': '3b0403d9c5cc5423cb80dabc3765f9a781b7a06b512082b6f210971a9417ab0d',
           'post_run_checks.py': '39d3d51d3b2470b1396196bcfce34dc4a8f0a6acd3bcb2a213001dc5ec3ed91f',
           's3_decision_a49.py': '72fb4295ac7d624e2a2d0c63394da651bf845b0b28cab2362108bcd6a3308a42'}   # A49 roles / branch triples only
SETTINGS = {'config/iwo_material_model_v3.yaml': '51b184e8728c4e4ce5ed4110c56d4b1083b5d12f1d4d6b45aef52816ba63961c',
            'config/solver.yaml': 'd5a9101219d1238923da096766443fd021751fad1a9f55770b3851301481d583',
            'scripts/run_atlas.py': 'b7927ac5b9747d5531ac827d220da6004e4a144d672ae16ab9bca2a28f46e6ae',
            'scripts/run_campaign.py': 'fb6e802f8c1cb71b56e153ed99504cc8e7e83d4c8eb7af8f13dc421d0fd125ac',
            'scripts/build_iwo_decks.py': '734125a8915e2a7790b2794db0c7bf429c477a83238b638a200af2b5fbeeca3c'}
SOURCES = {'archive': ('analysis_2026-10-10_campaign/profile/s4a_archive_A51.json', '44de96df4bc0b2731e01b8b49c6fe2b06f4bf2295f2ff40141c7a283420df0f0'),
           'adoption': ('analysis_2026-10-10_campaign/profile/s3_adoption_A49.json', '9ad43a88451082422e7b4faeaa710122aff28f44a94cff5562eeeb33f05b4993'),
           'matrix': ('analysis_2026-10-10_campaign/campaign_matrix.json', 'f06e8d7721f75aec3f78da06de1c1686c59307c33725bd8822c3ec3e0f0a443c'),
           's4c_confirm': ('analysis_2026-10-10_campaign/profile/s4c_confirm_A52.json', '91d0f3cb18307d313b994220de57a4bd46d07410c29912807f1354aa09140b3f')}
MODEL_ENV = 'config/iwo_material_model_v3.yaml'

FILMS = (2.0, 6.3, 13.2)
FOLDS = (6.3, 2.0, 13.2)                     # A53 (a): H6p3 first (register), then H2p0, H13p2 (plan 2.8; ASSUMED)
FID = {6.3: 'H6p3', 2.0: 'H2p0', 13.2: 'H13p2'}
TAG = {2.0: '2p0', 6.3: '6p3', 13.2: '13p2'}
TIMEOUT = {2.0: 1600, 6.3: 2000, 13.2: 3100}   # matrix S5-* timeouts (CAMPAIGN_DESIGN; plan 3.8)
STEPS = ('t1', 't2', 't3', 't4', 'pred')
RANKS = ('best', 'runner_up')
LOO_N = 4
PURE_TOL_DEC = 0.01                          # A49 (b) (4), restricted to the training films (A53 (b))
COORD_TOL = 1e-9

# override keys carried from a proposal / frozen record into a deck (everything else is the registered template entry, verbatim)
NT2 = 'thickness_laws.Nt_cm3.Nt2'
NTB = 'solver.physics_options.nt_bulk_cm3'
WTA = 'thickness_laws.WTA_eV.value'
QF = 'traps.fixed_interface_charge_Qf_cm2.value'
G0 = 'solver.physics_options.mobility.gamma0'
def MU(t): return f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{t}]'


# A49 branch name -> matrix template ids per film (S3-04 / S3-07 are the registered 2.0 nm tail entries, statement-identical to S0-01, A45 (k));
# the S4a-archive mode uses the S4A-01 entries (the start point of form N, PA-12)
TEMPLATE = {None: {2.0: 'S4A-01-2p0', 6.3: 'S4A-01-6p3', 13.2: 'S4A-01-13p2'},
            'tail bulk (S3-04=S0-01, S3-05, S3-06)': {2.0: 'S3-04', 6.3: 'S3-05', 13.2: 'S3-06'},
            'tail 50:50 (S3-07=S0-01, S3-08, S3-09)': {2.0: 'S3-07', 6.3: 'S3-08', 13.2: 'S3-09'},
            'IGZO.TOKYO GAMMA0 -0.31 (S3-11, S3-12, S3-13)': {2.0: 'S3-11', 6.3: 'S3-12', 13.2: 'S3-13'},
            'IGZO.TOKYO GAMMA0 +0.30 (S3-14, S3-15, S3-16)': {2.0: 'S3-14', 6.3: 'S3-15', 13.2: 'S3-16'}}
MOBILITY_KEYS = ('solver.physics_options.mobility.model', G0, 'solver.physics_options.mobility.tgamma', 'solver.physics_options.mobility.ncrit')


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsha(s): return hashlib.sha256(s.encode()).hexdigest()


def driver_sha(): return fsha(Path(__file__).resolve())


def _okey(o): return o.split('=', 1)[0]


def _canon(d): return json.dumps(d, sort_keys=True, default=float, separators=(',', ':'))


def seal_ok(d): return isinstance(d, dict) and d.get('sha256') == tsha(_canon({k: v for k, v in d.items() if k != 'sha256'}))


def train_of(held): return [t for t in FILMS if abs(t - held) > 1e-9]


def held_of(arg):
    try: v = float(arg)
    except (TypeError, ValueError): raise SystemExit(f'refused: --held {arg!r} is not one of {list(FOLDS)}')
    for t in FOLDS:
        if abs(v - t) < 1e-9: return t
    raise SystemExit(f'refused: --held {arg!r} is not one of {list(FOLDS)}')


def entry_ids(held, step):
    """S5 matrix ids of one invocation (training films ascending; PRED best then runner-up)"""
    f = FID[held]
    if step == 'pred': return [f'S5-{f}-PRED-{r}' for r in RANKS]
    k = int(step[1:]); return [f'S5-{f}-{k}-{TAG[t]}' for t in train_of(held)]


def invocation_order():
    return [(h, s) for h in FOLDS for s in STEPS]


def path(held, what): return OUTD / f'{FID[held]}_{what}.json'


def rel(p): return str(Path(p).resolve().relative_to(PKG.resolve())).replace('\\', '/')


# ------------------------------------------------------------------------------------------------ pins
def pin_problems(root=HERE, pkg=PKG):
    bad = []
    for f, h in {**FROZEN, **HELPERS}.items():
        p = Path(root) / f
        if not p.is_file() or fsha(p) != h: bad.append(f'{f} (expected {h[:8]})')
    for f, h in SETTINGS.items():
        p = Path(pkg) / f
        if not p.is_file() or fsha(p) != h: bad.append(f'{f} (expected {h[:8]})')
    for k, (f, h) in SOURCES.items():
        p = Path(pkg) / f
        if not p.is_file() or fsha(p) != h: bad.append(f'{f} (expected {h[:8]})')
    return bad


def frozen_modules():
    bad = pin_problems()
    if bad: raise SystemExit('refused: frozen-code / settings / source pins differ (A53 (g)): ' + '; '.join(bad))
    import profile_s4s5 as P
    import campaign_extract as ce
    import campaign_tools as ct
    if P.CODE_SHA != FROZEN['profile_s4s5.py']: raise SystemExit('refused: profile_s4s5.CODE_SHA differs from the frozen pin')
    if P.LOO_N != LOO_N: raise SystemExit('refused: profile_s4s5.LOO_N differs')
    return P, ce, ct


def a49_module():
    p = HERE / 's3_decision_a49.py'
    if fsha(p) != HELPERS['s3_decision_a49.py']: raise SystemExit('refused: s3_decision_a49.py pin differs')
    spec = importlib.util.spec_from_file_location('s3_decision_a49_pinned', p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def matrix_by_id():
    mx = json.loads((PKG / SOURCES['matrix'][0]).read_text()); return {r['id']: r for r in mx['runs']}


# ------------------------------------------------------------------------------------------------ RUN_INDEX (run_id, label, exit_code, notes prefix)
def index_state(rows):
    """label -> {'run_ids': [...], 'first': run id, 'finished': bool (a non-STARTED row with an exit code for the first run id)}"""
    out = {}
    for r in rows:
        lab = r.get('label', ''); rid = r.get('run_id', '')
        if not lab.startswith('c10_s5_'): continue
        s = out.setdefault(lab, {'run_ids': [], 'first': rid, 'finished': False})
        if rid not in s['run_ids']: s['run_ids'].append(rid)
        if rid == s['first'] and r.get('exit_code', '') != '' and not r.get('started'): s['finished'] = True
    return out


def read_index(path_=INDEX):
    """run_id, label, exit_code and whether the row is a STARTED row; no other column is kept (the finish-row notes carry runner metrics)"""
    with Path(path_).open(newline='') as fh:
        return [{'run_id': r.get('run_id', ''), 'label': r.get('label', ''), 'exit_code': r.get('exit_code', ''),
                 'started': str(r.get('notes', '')).startswith('STARTED')} for r in csv.DictReader(fh)]


def run_dir_of(label, t, state, runs=None):
    runs = runs or RUNS; s = state.get(label)
    if not s: return None, f'{label}: no RUN_INDEX row (not launched)'
    if len(s['run_ids']) != 1: return None, f'{label}: {len(s["run_ids"])} run ids {s["run_ids"]} (one expected)'
    if not s['finished']: return None, f'{label}: {s["first"]} has no finish row'
    d = Path(runs) / f'{s["first"]}_{TAG[t]}_{label}'
    if not d.is_dir(): return None, f'{label}: run directory {d.name} missing'
    return d, None


# ------------------------------------------------------------------------------------------------ records
def write_once(p, rec):
    """never overwrite a record with different content (records are committed; a changed record is a new registration)"""
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True); txt = json.dumps(rec, indent=1, default=float)
    if p.exists():
        old = json.loads(p.read_text())
        if _canon(old) != _canon(json.loads(txt)): raise SystemExit(f'refused: {rel(p)} exists with other content; never overwritten')
        return False
    p.write_text(txt); return True


def read_sealed(p, what):
    p = Path(p)
    if not p.is_file(): raise SystemExit(f'refused: {what} {rel(p)} missing')
    d = json.loads(p.read_text())
    if not seal_ok(d): raise SystemExit(f'refused: {what} {rel(p)} does not match its sha256 (edited after sealing)')
    return d


def committed_in_git(p, pkg=PKG):
    """(ok, detail): the working-tree file equals the git HEAD blob (LF-normalised; core.autocrlf=input)"""
    relp = rel(p)
    try: out = subprocess.run(['git', '-C', str(pkg), 'cat-file', '-p', f'HEAD:{relp}'], capture_output=True, timeout=60)
    except Exception as ex: return False, f'git not runnable ({type(ex).__name__})'
    if out.returncode != 0: return False, 'not in HEAD'
    norm = lambda b: hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()
    same = norm(out.stdout) == norm(Path(p).read_bytes())
    return same, f'HEAD blob LF-normalised content {"equal" if same else "DIFFERENT"}'


# ------------------------------------------------------------------------------------------------ (b) fold branch decision: caller flags
def pure_on(shape, films, tol=PURE_TOL_DEC):
    """A49 (b) (4) on the given films: True iff the single-film shape-only residual (free shift + scale of that film alone, profile_shared.profile
    'diagnostic_shape_only', A49 record) of the branch equals the base's within tol dec at every given film; None if a value is missing"""
    a, b = (shape or {}).get('branch') or {}, (shape or {}).get('base') or {}; d = []
    for t in films:
        x = (a.get(str(t)) or {}).get('shape_only_sqrtJ_dec'); y = (b.get(str(t)) or {}).get('shape_only_sqrtJ_dec')
        if x is None or y is None or not (math.isfinite(x) and math.isfinite(y)): return None, d
        d.append(abs(x - y))
    return all(v <= tol for v in d), d


def activation_on(act, roles, films):
    """A49 activation record at the training-film roles: ACTIVE_AS_REQUESTED and (IGZO) regions 1 and 2 ACTIVE; None if a role is missing"""
    out = []
    for t in films:
        v = (act or {}).get(roles[t])
        if not isinstance(v, dict): return None
        out.append(v.get('status') == 'ACTIVE_AS_REQUESTED' and (v.get('regions_1_2') or {'state': 'ACTIVE'}).get('state') == 'ACTIVE')
    return all(out)


def branch_spec(held, A, adoption, eligible):
    """the loo_branch input (BRANCHES.json form of profile_s4s5 l.139-140) for one fold. eligible: role -> bool (frozen eligibility)"""
    train = train_of(held); rows = {r['name']: r for r in adoption['branches']}
    base = {str(t): rel(A.run_dir(k)) for k, t in zip(A.BASE, FILMS)}
    out = []
    for b in A.BRANCHES:
        roles = dict(zip(FILMS, b['roles'])); r49 = rows.get(b['name'])
        if r49 is None: raise SystemExit(f'refused: A49 record has no branch {b["name"]}')
        pure, dev = pure_on(r49.get('shape_only'), train)
        out.append({'name': b['name'], 'group': b['group'], 'runs': {str(t): rel(A.run_dir(roles[t])) for t in FILMS},
                    'converged': all(eligible.get(roles[t]) is True for t in train),
                    'activation_ok': activation_on(r49.get('activation'), roles, train),
                    'pure_shift_or_scale': pure,
                    'flag_provenance': {'training_roles': [roles[t] for t in train], 'converged': 'frozen profile_s4s5.load eligibility (C3) of the '
                                        'training-film runs', 'activation_ok': 'A49 record activation (post_run_checks ACTIVE_AS_REQUESTED; IGZO regions 1 '
                                        'and 2) at the training-film roles', 'pure_shift_or_scale': f'A49 rule (4) on the training films: single-film '
                                        f'shape-only changes {[round(x, 6) for x in dev]} dec vs {PURE_TOL_DEC}'}})
    full = sorted(n for n in (adoption.get('chosen') or {}).values() if n)
    return {'record': 'S5 fold branch spec (register A53 (b)); input list for the frozen profile_s4s5.loo_branch', 'held_out_nm': held,
            'training_films': train, 'base': base, 'full_data_choice': full, 'branches': out,
            'sources': {k: {'file': f, 'sha256': h} for k, (f, h) in SOURCES.items() if k in ('adoption',)}}


# ------------------------------------------------------------------------------------------------ (c)-(e) execution entries
def _replace(base, new):
    """the template overrides with exactly the keys of new replaced (each must occur exactly once); keys absent from the template are refused"""
    hit = {k: 0 for k in new}; out = []
    for o in base:
        k = _okey(o)
        if k in new: out.append(f'{k}={new[k]}'); hit[k] += 1
        else: out.append(o)
    if any(v != 1 for v in hit.values()): raise SystemExit(f'refused: the template does not carry each replaced key exactly once ({hit})')
    return out


def tail_values(template, ns):
    """Nt2 (and nt_bulk) strings for an integrated 2.0 nm tail N_s under the template's tail law (make_campaign_matrix.base_overrides)"""
    keys = {_okey(o): o.split('=', 1)[1] for o in template}
    if NTB in keys: return {NT2: f'{ns / 2 / 2e-7:.6g}', NTB: f'{ns / 2 / 2e-7:.6g}'}
    return {NT2: f'{ns / 2e-7:.6g}'}


def coords_of_overrides(ov):
    """(lNs, WT, g0) the frozen coords() would read from a run launched with these overrides (N_s = (Nt2 + nt_bulk) x 2 nm)"""
    k = {_okey(o): o.split('=', 1)[1] for o in ov}
    ns = (float(k[NT2]) + float(k.get(NTB, 0) or 0)) * 2e-7
    return {'lNs': math.log10(ns) if ns > 0 else float('-inf'), 'WT': float(k[WTA]), 'g0': float(k[G0]) if G0 in k else None}


def launch_entry(mx, eid, t, template_id, xdeck, nuis_ov, purpose_add, params_rule):
    """one S5 entry: the matrix S5 id / label / timeout / stage, the registered template overrides with only the launched coordinates (tail law
    strings, W_T, GAMMA0) and the two written nuisance values (Q_f, mu_band_fitted[t]) replaced"""
    r = mx[eid]; ce_ = r['campaign_entry']; tpl = mx[template_id]['campaign_entry']['overrides']
    if abs(float(ce_['thickness']) - t) > 1e-9 or ce_['timeout'] != TIMEOUT[t]: raise SystemExit(f'refused: matrix {eid} thickness/timeout differ')
    nk = {_okey(o): o.split('=', 1)[1] for o in nuis_ov}
    if set(nk) != {QF, MU(t)}: raise SystemExit(f'refused: launch values at {t} nm are not exactly Q_f and mu_band_fitted[{t}]: {sorted(nk)}')
    new = {**tail_values(tpl, xdeck['Ns_cm2']), WTA: f'{xdeck["WT_eV"]}', **nk}
    if xdeck.get('gamma0') is not None:
        if not any(_okey(o) == G0 for o in tpl): raise SystemExit(f'refused: GAMMA0 given but template {template_id} has no IGZO mobility')
        new[G0] = f'{xdeck["gamma0"]}'
    elif any(_okey(o) == G0 for o in tpl): raise SystemExit(f'refused: template {template_id} is IGZO but no GAMMA0 was given')
    ov = _replace(tpl, new)
    return {'id': eid, 'thickness': t, 'label': ce_['label'], 'overrides': ov, 'timeout': TIMEOUT[t],
            'purpose': ce_['purpose'] + ' ' + purpose_add, 'stage': r['stage'], 'matrix_status': r['status'],
            'requires_code': r.get('requires_code', []), 'depends_on': r.get('depends_on'), 'params_rule': params_rule}


def template_for(fold_choice, t):
    """template id: S4A-01 (S4a-archive mode / nothing adopted) or the adopted branch's S3 entry; two branches: tail template + IGZO keys"""
    names = sorted(fold_choice or [])
    if not names: return TEMPLATE[None][t], None
    tails = [n for n in names if n.startswith('tail')]; mob = [n for n in names if n.startswith('IGZO')]
    if len(tails) > 1 or len(mob) > 1 or len(names) > 2: raise SystemExit(f'refused: fold choice {names} is not a registered combination')
    if tails and mob: return TEMPLATE[tails[0]][t], TEMPLATE[mob[0]][t]
    return TEMPLATE[names[0]][t], None


def combined_template(mx, fold_choice, t):
    """(template id, overrides): a two-branch fold (Codex ruling (d)) takes the tail template and adds the IGZO mobility overrides"""
    a, b = template_for(fold_choice, t)
    tpl = list(mx[a]['campaign_entry']['overrides'])
    if b is None: return a, tpl
    add = [o for o in mx[b]['campaign_entry']['overrides'] if _okey(o) in MOBILITY_KEYS]
    if len(add) != len(MOBILITY_KEYS): raise SystemExit(f'refused: {b} does not carry the four IGZO mobility overrides')
    return f'{a}+{b}', tpl + add


def deck_of(x, dims, P):
    """natural deck inputs of a (deck-rounded) coordinate point (frozen DECK rounding)"""
    v = dict(zip(dims, P.deck_inputs(x, dims)))
    return {'Ns_cm2': v['lNs'], 'WT_eV': v['WT'], 'gamma0': v.get('g0')}


def dry_build(entries):
    """deck and material text sha256 that run_atlas would write now (run_campaign.current_deck_text / current_material_text, V3)"""
    os.environ['IWO_MODEL_FILE'] = MODEL_ENV
    if str(PKG / 'scripts') not in sys.path: sys.path.insert(0, str(PKG / 'scripts'))
    import build_iwo_decks as bd
    import run_campaign as rc
    bd.MODEL_FILE = MODEL_ENV
    return {k: {'deck_sha256': tsha(rc.current_deck_text(e, e['overrides'])), 'model_sha256': tsha(rc.current_material_text(e['overrides']))}
            for k, e in entries.items()}


# ------------------------------------------------------------------------------------------------ fold archive
def fold_candidates(held, upto, state, runs=None):
    """the fold's S5 candidates 1..upto from their sealed records and RUN_INDEX (input list); ([...], problems)"""
    out, bad = [], []; runs = runs or RUNS
    for k in range(1, upto + 1):
        p = path(held, f't{k}')
        try: rec = read_sealed(p, f'training record t{k}')
        except SystemExit as e: bad.append(str(e)); continue
        runs_ = {}
        for eid in entry_ids(held, f't{k}'):
            e = rec['entries'][eid]; d, why = run_dir_of(e['label'], float(e['thickness']), state, runs)
            if why: bad.append(why)
            else: runs_[str(float(e['thickness']))] = rel(d)
        out.append({'id': f'S5-{FID[held]}-{k}', 'stage': 'S5', 'fold': held, 'runs': runs_})
    return out, bad


def fold_archive(held, dec, cands):
    if dec['same_as_full_data']:
        arch = json.loads((PKG / SOURCES['archive'][0]).read_text())
        return {'candidates': list(arch['candidates']) + list(cands), 'mode': 'S4a archive (A51) + fold candidates',
                'source': {'file': SOURCES['archive'][0], 'sha256': SOURCES['archive'][1]}}
    return {'candidates': list(cands), 'mode': 'A7 local design: fold candidates only'}


def last_record(held):
    k = 0
    while k < LOO_N and path(held, f't{k + 1}').is_file(): k += 1
    return k


# ------------------------------------------------------------------------------------------------ commands
def cmd_branch(held):
    P, ce, ct = frozen_modules(); A = a49_module(); os.chdir(PKG)
    if path(held, 'branch').exists():
        dec = read_sealed(path(held, 'branch'), 'fold decision'); print(f'[{FID[held]}] decision exists: {dec["verdict"]}'); return 0
    adoption = json.loads((PKG / SOURCES['adoption'][0]).read_text())
    if not seal_ok(adoption): raise SystemExit('refused: A49 adoption record does not match its seal')
    train = train_of(held); roles = sorted({b['roles'][FILMS.index(t)] for b in A.BRANCHES for t in train} | {A.BASE[FILMS.index(t)] for t in train})
    eligible = {k: P.is_eligible(P.load(rel(A.run_dir(k)))) for k in roles}
    spec = branch_spec(held, A, adoption, eligible)
    info = P.measured_training(train)
    dec = P.loo_branch(spec, held, info)
    write_once(path(held, 'branch_spec'), spec); write_once(path(held, 'branch'), dec)
    print(json.dumps({'fold': FID[held], 'fold_choice': dec['fold_choice'], 'full_data_choice': dec['full_data_choice'],
                      'branches': [{k: r.get(k) for k in ('name', 'gain_dec', 'sqrtJ_dec', 'arithmetic', 'adopted_candidate', 'verdict')} for r in dec['branches']],
                      'base_profile': dec['base_profile'], 'verdict': dec['verdict'], 'sha256': dec['sha256']}, indent=1, default=float))
    return 0 if dec['same_as_full_data'] else 3


def _select(P, held, dec, cands):
    arch = fold_archive(held, dec, cands)
    C = P.load_archive({'candidates': arch['candidates']})
    info = P.measured_training(train_of(held))
    res = P.loo_select(C, held, info, dec, amendment_ref=None if dec['same_as_full_data'] else AMENDMENT)
    return arch, C, json.loads(json.dumps(res, default=float))


def cmd_next(held):
    P, ce, ct = frozen_modules(); os.chdir(PKG)
    dec = P.verify_seal(json.loads(path(held, 'branch').read_text()), 'fold branch decision') if path(held, 'branch').is_file() else None
    if dec is None: raise SystemExit(f'refused: no fold decision for {FID[held]} (run branch first)')
    k = last_record(held) + 1
    if k > LOO_N: raise SystemExit(f'refused: {FID[held]} has {LOO_N} training records; use freeze')
    state = index_state(read_index()); cands, bad = fold_candidates(held, k - 1, state)
    if bad: raise SystemExit('STOP: the earlier fold candidates are not complete: ' + ' | '.join(bad))
    arch, C, res = _select(P, held, dec, cands)
    stop = []
    fold_rows = [r for r in res.get('pool', []) if r['stage'] == 'S5']
    inel = [r['id'] for r in fold_rows if str(r.get('state', '')).startswith('UNKNOWN')]
    if inel: stop.append(f'fold candidate(s) ineligible {inel} (A53 (h) 2: the fold is held for a logged decision)')
    if dec['same_as_full_data']:
        nv = [r['id'] for r in res.get('pool', []) if r['stage'] == 'S4a' and r.get('state') != 'valid']
        if nv: stop.append(f'S4a candidate(s) without a valid training profile {nv}: the frozen freeze would be blocked (ruling b); the fold is UNRESOLVED '
                           'before any further training launch (A53 (h) 3)')
        ok = str(res.get('verdict', '')).startswith('TRAINING') and 'proposal_deck' in (res.get('next_training_candidate') or {})
    else:
        ok = str(res.get('verdict', '')).startswith('A7 LOCAL DESIGN') and 'proposal' in (res.get('next_training_candidate') or {})
    if not ok: stop.append(f'frozen loo_select verdict is not a launchable proposal: {str(res.get("verdict"))[:200]}')
    dims = tuple(res.get('dims') or ())
    if not stop:
        ntc = res['next_training_candidate']
        if dec['same_as_full_data']:
            pd = ntc['proposal_deck']; xdeck = {'Ns_cm2': pd['Ns_cm2'], 'WT_eV': pd['WT_eV'], 'gamma0': pd.get('gamma0')}
        else:
            xdeck = deck_of(ntc['proposal'], dims, P)
        xl = {'lNs': math.log10(xdeck['Ns_cm2']), 'WT': xdeck['WT_eV'], 'g0': xdeck['gamma0']}
        near = [c['id'] for c in C if not P._distinct_pair(xl, c['x'], dims)]
        if near: stop.append(f'deck-rounded proposal {xdeck} is not distinct (frozen _distinct_pair) from {near} (A53 (h) 3)')
    if stop:
        print(json.dumps({'fold': FID[held], 'k': k, 'verdict': 'STOP: ' + ' | '.join(stop), 'loo_select_verdict': res.get('verdict')}, indent=1, default=float))
        return 3
    mx = matrix_by_id(); nl = res['native_launch_values']; entries = {}
    cid = (ntc.get('centre') or {}).get('id') if dec['same_as_full_data'] else 'A7 centre (' + str(dec.get('centre_source')) + ')'
    for eid, t in zip(entry_ids(held, f't{k}'), train_of(held)):
        tid, tpl = combined_template(mx, dec['fold_choice'], t)
        mx_t = dict(mx); mx_t[tid] = {'campaign_entry': {'overrides': tpl}}
        add = (f'Register A53: fold {FID[held]} training candidate {k}/4 = frozen loo_select proposal ({res["mode"]}; deck inputs N_s {xdeck["Ns_cm2"]:.4g} '
               f'cm^-2, W_T {xdeck["WT_eV"]} eV' + (f', GAMMA0 {xdeck["gamma0"]}' if xdeck['gamma0'] is not None else '') + f') at the native launch values of '
               f'{cid} (training films only).')
        entries[eid] = launch_entry(mx_t, eid, t, tid, xdeck, nl['per_film'][str(t)]['overrides'], add,
                                    f'resolved from the sealed record analysis_2026-10-10_campaign/profile/s5_A53/{FID[held]}_t{k}.json (register A53)')
        cx = coords_of_overrides(entries[eid]['overrides'])
        if any(abs(cx[d] - xl[d]) > COORD_TOL * max(1.0, abs(xl[d])) for d in ('lNs', 'WT')) or (cx['g0'] is None) != (xl['g0'] is None):
            raise SystemExit(f'refused: entry {eid} coordinates {cx} differ from the deck-rounded proposal {xl}')
    rec = {'record': f'S5 training record (register A53 (c)): fold {FID[held]}, candidate {k}/4; sealed; committed before its launch',
           'fold': FID[held], 'held_out_nm': held, 'training_films': train_of(held), 'k': k, 'step': f't{k}', 'mode': res['mode'],
           'decision_sha256': dec['sha256'], 'archive': arch, 'fold_candidates_before': cands,
           'loo_select': res, 'loo_select_sha256': tsha(_canon(res)), 'proposal_deck': xdeck, 'launch_coords': xl, 'native_launch_values': nl,
           'entries': entries, 'dry_build': dry_build(entries), 'driver_sha256': driver_sha(), 'code_sha256': P.CODE_SHA,
           'pins': {'frozen': FROZEN, 'helpers': HELPERS, 'settings': SETTINGS, 'sources': {k_: h for k_, (f, h) in SOURCES.items()}},
           'labels': ('proposal: frozen quadratic surrogate of the two-film J (ranking device only); launch values FITTED on the training films only; '
                      'the held-out film is never tuned; retrospective transferability, never validation')}
    rec = P.seal(rec); write_once(path(held, f't{k}'), rec)
    print(json.dumps({'fold': FID[held], 'k': k, 'record': rel(path(held, f't{k}')), 'sha256': rec['sha256'], 'proposal_deck': xdeck,
                      'centre': ntc.get('centre'), 'entries': {i: {'label': e['label'], 'timeout': e['timeout']} for i, e in entries.items()},
                      'dry_build': rec['dry_build'], 'loo_select_verdict': res['verdict']}, indent=1, default=float))
    return 0


def source_strings(mx, held, rec, k_records):
    """the launched-coordinate override strings of the frozen candidate (tail law strings, W_T, GAMMA0) from its own registered entry: an S4a
    candidate's matrix entry, or the fold record of an S5 candidate"""
    cid = rec['candidate']; t0 = train_of(held)[0]
    if rec['stage'] == 'S4a': ov = mx[f'{cid}-{TAG[t0]}']['campaign_entry']['overrides']
    else:
        k = int(cid.rsplit('-', 1)[1]); ov = k_records[k]['entries'][f'S5-{FID[held]}-{k}-{TAG[t0]}']['overrides']
    keys = {_okey(o): o.split('=', 1)[1] for o in ov}
    out = {NT2: keys[NT2], WTA: keys[WTA]}
    if NTB in keys: out[NTB] = keys[NTB]
    if G0 in keys: out[G0] = keys[G0]
    return out


def pred_entry(mx, held, rank, rec, k_records, dec):
    eid = f'S5-{FID[held]}-PRED-{rank}'; r = mx[eid]; ce_ = r['campaign_entry']
    tid, tpl = combined_template(mx, dec['fold_choice'], held)
    strings = source_strings(mx, held, rec, k_records)
    nk = {_okey(o): o.split('=', 1)[1] for o in rec['held_out']['overrides']}
    if set(nk) != {QF, MU(held)}: raise SystemExit(f'refused: frozen held-out overrides are not exactly Q_f and mu_band_fitted[{held}]')
    ov = _replace(tpl, {**strings, **nk})
    cx = coords_of_overrides(ov); fx = rec['coords']
    if any(abs(cx[d] - fx[d]) > COORD_TOL * max(1.0, abs(fx[d])) for d in ('lNs', 'WT')) or ((cx['g0'] is None) != (fx.get('g0') is None)) or (
            cx['g0'] is not None and abs(cx['g0'] - fx['g0']) > COORD_TOL):
        raise SystemExit(f'refused: {eid} coordinates {cx} differ from the frozen record {fx}')
    if abs(float(ce_['thickness']) - held) > 1e-9 or ce_['timeout'] != TIMEOUT[held]: raise SystemExit(f'refused: matrix {eid} thickness/timeout differ')
    add = (f'Register A53: frozen {rank} record {rec["sha256"][:12]} (candidate {rec["candidate"]}, training sqrt(J) {rec["training_sqrtJ_dec"]:.4f} dec, '
           f'{rec["role"]}); Q_f and mu_band_fitted[{held}] from the training-film profile; nothing tuned to this film.')
    return {'id': eid, 'thickness': held, 'label': ce_['label'], 'overrides': ov, 'timeout': TIMEOUT[held], 'purpose': ce_['purpose'] + ' ' + add,
            'stage': r['stage'], 'matrix_status': r['status'], 'requires_code': r.get('requires_code', []), 'depends_on': r.get('depends_on'),
            'params_rule': f'resolved from the sealed record analysis_2026-10-10_campaign/profile/s5_A53/{FID[held]}_pred.json (register A53)'}


def cmd_freeze(held):
    P, ce, ct = frozen_modules(); os.chdir(PKG)
    dec = P.verify_seal(json.loads(path(held, 'branch').read_text()), 'fold branch decision')
    if last_record(held) != LOO_N: raise SystemExit(f'refused: {FID[held]} has {last_record(held)} of {LOO_N} training records')
    if path(held, 'pred').exists(): raise SystemExit(f'refused: {rel(path(held, "pred"))} exists; never overwritten')
    state = index_state(read_index()); cands, bad = fold_candidates(held, LOO_N, state)
    if bad: raise SystemExit('STOP: the fold candidates are not complete: ' + ' | '.join(bad))
    arch, C, res = _select(P, held, dec, cands)
    if not str(res.get('verdict', '')).startswith('FROZEN') or len(res.get('frozen') or []) != 2:
        print(json.dumps({'fold': FID[held], 'verdict': 'STOP: no frozen records: ' + str(res.get('verdict'))[:300]}, indent=1)); return 3
    fz = {r['rank']: r for r in res['frozen']}
    for r_ in fz.values(): P.verify_seal(r_, 'frozen record')
    kr = {k: read_sealed(path(held, f't{k}'), f'training record t{k}') for k in range(1, LOO_N + 1)}
    mx = matrix_by_id(); entries = {f'S5-{FID[held]}-PRED-{rk}': pred_entry(mx, held, rk, fz[rk], kr, dec) for rk in RANKS}
    sel = {k: v for k, v in res.items() if k != 'frozen'}
    rec = {'record': f'S5 held-out record (register A53 (d)): fold {FID[held]}; sealed; it and both frozen records are committed in git HEAD (the '
                     'external commitment) before the PRED launch', 'fold': FID[held], 'held_out_nm': held, 'training_films': train_of(held),
           'step': 'pred', 'mode': res['mode'], 'decision_sha256': dec['sha256'], 'archive': arch, 'loo_select': sel, 'loo_select_sha256': tsha(_canon(sel)),
           'frozen': {rk: {'file': rel(path(held, f'frozen_{rk}')), 'sha256': fz[rk]['sha256'], 'candidate': fz[rk]['candidate'],
                           'training_sqrtJ_dec': fz[rk]['training_sqrtJ_dec']} for rk in RANKS},
           'entries': entries, 'dry_build': dry_build(entries), 'driver_sha256': driver_sha(), 'code_sha256': P.CODE_SHA,
           'labels': 'frozen best = primary held-out prediction; runner-up = optimiser uncertainty only; retrospective transferability, never validation'}
    rec = P.seal(rec)
    for rk in RANKS: write_once(path(held, f'frozen_{rk}'), fz[rk])
    write_once(path(held, 'pred'), rec)
    print(json.dumps({'fold': FID[held], 'pred_record': rel(path(held, 'pred')), 'sha256': rec['sha256'],
                      'frozen': rec['frozen'], 'entries': {i: {'label': e['label'], 'timeout': e['timeout']} for i, e in entries.items()},
                      'dry_build': rec['dry_build'], 'verdict': res['verdict']}, indent=1, default=float))
    return 0


def loo1(acc):
    """LOO-1 quantities from the frozen 5.3 acceptance of a native held-out run (COMPUTED vs MEASURED; arithmetic only)"""
    c = acc['criteria']; e3 = c['Id3V_err_pct']['value']; ss = c['SS_a1_err_pct']; mu2 = c['mu_FE_err_pct']['per_V'].get('2.0') or {}
    return {'dVth_cc_V': c['dVth_cc_V']['value'], 'dlog10_Id3V_dec': (math.log10(1 + e3 / 100) if e3 is not None and e3 > -100 else None),
            'Id3V_err_pct': e3, 'dSS_mV_dec': (ss['sim_mV_dec'] - ss['meas_mV_dec']) if ss.get('sim_mV_dec') is not None and ss.get('meas_mV_dec') is not None else None,
            'SS_err_pct': ss['value'], 'dmuFE_2V_cm2Vs': (mu2['sim'] - mu2['meas']) if mu2.get('sim') is not None and mu2.get('meas') is not None else None,
            'muFE_2V_err_pct': mu2.get('value'), 'active_rmse_dec': c['active_rmse_dec']['value'], 'verdict': acc['verdict']}


def cmd_score(held):
    P, ce, ct = frozen_modules(); os.chdir(PKG)
    pr = read_sealed(path(held, 'pred'), 'held-out record')
    ok, det = committed_in_git(path(held, 'pred'))
    if not ok: raise SystemExit(f'refused: {rel(path(held, "pred"))} is not committed in git HEAD ({det})')
    state = index_state(read_index()); info, _ = ce.measured(); out = {}
    for rk in RANKS:
        fp = path(held, f'frozen_{rk}'); fr = json.loads(fp.read_text())
        okf, detf = committed_in_git(fp)
        if not okf: raise SystemExit(f'refused: {rel(fp)} is not committed in git HEAD ({detf})')
        if fr.get('sha256') != pr['frozen'][rk]['sha256']: raise SystemExit(f'refused: {rel(fp)} is not the frozen record bound in the held-out record')
        e = pr['entries'][f'S5-{FID[held]}-PRED-{rk}']; d, why = run_dir_of(e['label'], held, state)
        if why: out[rk] = {'verdict': f'UNKNOWN (no scorable held-out run: {why})'}; continue
        try: s = json.loads(json.dumps(P.loo_score(fr, rel(d), info, pr['frozen'][rk]['sha256']), default=float))
        except SystemExit as ex: out[rk] = {'verdict': f'REFUSED: {ex}'}; continue
        s['loo1'] = loo1(s['acceptance_5_3']); out[rk] = s
    spread = {}
    if all('loo1' in out.get(rk, {}) for rk in RANKS):
        for q in ('dVth_cc_V', 'dlog10_Id3V_dec', 'dSS_mV_dec', 'dmuFE_2V_cm2Vs', 'active_rmse_dec'):
            a, b = out['best']['loo1'][q], out['runner_up']['loo1'][q]; spread[q] = (abs(a - b) if a is not None and b is not None else None)
    v = out.get('best', {}).get('verdict', 'UNKNOWN')
    rec = P.seal({'record': f'S5 held-out score (register A53 (e)); fold {FID[held]}', 'fold': FID[held], 'held_out_nm': held, 'pred_record_sha256': pr['sha256'],
                  'scores': out, 'best_minus_runner_up_abs': spread, 'driver_sha256': driver_sha(), 'code_sha256': P.CODE_SHA,
                  'verdict': v, 'labels': 'retrospective transferability within already-seen devices (n = 3), never validation or prediction (PA-13)'})
    write_once(path(held, 'score'), rec)
    print(json.dumps({'fold': FID[held], 'verdict_best': v, 'verdict_runner_up': out.get('runner_up', {}).get('verdict'),
                      'loo1_best': out.get('best', {}).get('loo1'), 'loo1_runner_up': out.get('runner_up', {}).get('loo1'), 'spread': spread,
                      'sha256': rec['sha256']}, indent=1, default=float))
    return 0


def jackknife(vals):
    """LOO-3: var_JK = ((n - 1) / n) sum (theta_i - theta_bar)^2 (diagnostic, not a confidence interval)"""
    v = [x for x in vals if x is not None and math.isfinite(x)]; n = len(v)
    if n < 2: return {'n': n, 'var_JK': None, 'sd_JK': None}
    m = sum(v) / n; var = (n - 1) / n * sum((x - m) ** 2 for x in v)
    return {'n': n, 'mean': m, 'var_JK': var, 'sd_JK': math.sqrt(var)}


def cmd_report():
    P, ce, ct = frozen_modules(); os.chdir(PKG); folds = {}
    for h in FOLDS:
        f = {'branch': None, 'frozen_best': None, 'score': None}
        if path(h, 'branch').is_file(): d = json.loads(path(h, 'branch').read_text()); f['branch'] = {'fold_choice': d['fold_choice'], 'verdict': d['verdict']}
        if path(h, 'frozen_best').is_file():
            r = json.loads(path(h, 'frozen_best').read_text())
            f['frozen_best'] = {'candidate': r['candidate'], 'Ns_cm2': r['coords_natural']['Ns_cm2'], 'WT_eV': r['coords_natural']['WT_eV'],
                                'gamma0': r['coords_natural']['gamma0'], 'Qf_cm2': r['Qf_cm2'], 'dV0_from_anchor_V': r['dV0_from_anchor_V'],
                                'mu_inf_cm2Vs': r['mu_inf_cm2Vs'], 'ell_nm': r['ell_nm'], 'training_sqrtJ_dec': r['training_sqrtJ_dec'],
                                'bound_limited': r['bound_limited']}
        if path(h, 'score').is_file():
            s = read_sealed(path(h, 'score'), 'score record')
            f['score'] = {'verdict_best': s['verdict'], 'loo1_best': (s['scores'].get('best') or {}).get('loo1'),
                          'loo1_runner_up': (s['scores'].get('runner_up') or {}).get('loo1'), 'spread': s['best_minus_runner_up_abs']}
        folds[FID[h]] = f
    fails = [k for k, f in folds.items() if f['score'] and str(f['score']['verdict_best']).startswith('FAIL')]
    passes = [k for k, f in folds.items() if f['score'] and str(f['score']['verdict_best']).startswith('PASS')]
    th = {q: [((folds[FID[h]]['frozen_best'] or {}).get(q)) for h in FOLDS] for q in ('dV0_from_anchor_V', 'mu_inf_cm2Vs', 'ell_nm', 'WT_eV')}
    th['log10_Ns'] = [math.log10(x) if x else None for x in [((folds[FID[h]]['frozen_best'] or {}).get('Ns_cm2')) for h in FOLDS]]
    e20 = (folds['H2p0']['score'] or {}).get('loo1_best') if folds['H2p0']['score'] else None
    rep = {'record': 'S5 report (register A53 (f)): LOO-1 per fold, LOO-2 floor, LOO-3 jackknife (diagnostic), early exit (design l.338)', 'folds': folds,
           'LOO2_floor_below_2nm': ({q: (abs(e20[q]) if e20 and e20.get(q) is not None else None) for q in ('dVth_cc_V', 'dlog10_Id3V_dec', 'dSS_mV_dec', 'dmuFE_2V_cm2Vs',
                                                                                                         'active_rmse_dec')} if e20 else None),
           'LOO2_note': 'a prediction below 2.0 nm carries a band no narrower than |e_2.0| of fold H2p0; a calibrated film under new conditions no narrower '
                        'than its S4c residual (A45 (e))',
           'LOO3_jackknife': {q: jackknife(v) for q, v in th.items()},
           'held_out_fail_folds': fails, 'held_out_pass_folds': passes,
           'early_exit': ('S4 failed (S4a abort) and S5 confirms the failure on >= 2 folds: S6 is cut to the DFT-input profiles (10 launches; design l.338)'
                          if len(fails) >= 2 else 'not established (fewer than 2 folds with a held-out FAIL)'),
           'provenance': ('N_D 2.5e17 cm^-3 from the all-film V1 law (bracketed only by S6-13/S6-15); Delta_sr 0.287 nm FITTED (Januar et al., same devices), '
                          'fixed in every fold; V1 start values of N_s and W_T; S4a design data-independent, its archive shared by all folds; all four '
                          'curves seen before S5 (retrospective)'),
           'driver_sha256': driver_sha(), 'code_sha256': P.CODE_SHA,
           'labels': 'retrospective transferability within already-seen devices (n = 3, one device per film, anomalous 6.3 nm on-current); never validation'}
    rep = P.seal(rep); (OUTD / 's5_report_A53.json').write_text(json.dumps(rep, indent=1, default=float))
    print(json.dumps({k: rep[k] for k in ('held_out_fail_folds', 'held_out_pass_folds', 'early_exit', 'LOO3_jackknife', 'LOO2_floor_below_2nm')}, indent=1, default=float))
    return 0


def cmd_stop(held, reason):
    """A53 (h): a registered fold stop (the remaining invocations of this fold are not launched); sealed; committed before the next invocation"""
    P, ce, ct = frozen_modules()
    if not reason or len(reason) < 20: raise SystemExit('refused: a stop record needs the registered rule and the reason (--reason "...")')
    state = index_state(read_index()); mx = matrix_by_id(); started = {}
    for s in STEPS:
        for eid in entry_ids(held, s):
            st = state.get(mx[eid]['campaign_entry']['label'])
            if st: started[eid] = {'run_ids': st['run_ids'], 'finished': st['finished']}
    rec = P.seal({'record': f'S5 fold stop (register A53 (h)); fold {FID[held]}', 'fold': FID[held], 'held_out_nm': held, 'reason': reason,
                  'training_records': last_record(held), 'pred_record': path(held, 'pred').is_file(), 'started_entries': started,
                  'consequence': 'no further launch in this fold; the fold is reported UNRESOLVED (or as scored so far); the next fold proceeds',
                  'driver_sha256': driver_sha(), 'code_sha256': P.CODE_SHA})
    write_once(path(held, 'stop'), rec); print(json.dumps(rec, indent=1, default=float)); return 0


def cmd_status():
    state = index_state(read_index()); mx = matrix_by_id(); out = {}
    for h in FOLDS:
        f = {'branch': path(h, 'branch').is_file(), 'training_records': last_record(h), 'pred': path(h, 'pred').is_file(), 'score': path(h, 'score').is_file(),
             'stop': path(h, 'stop').is_file(), 'runs': {}}
        for s in STEPS:
            for eid in entry_ids(h, s):
                st = state.get(mx[eid]['campaign_entry']['label']); f['runs'][eid] = None if not st else {'run_ids': st['run_ids'], 'finished': st['finished']}
        out[FID[h]] = f
    print(json.dumps(out, indent=1)); return 0


def main(argv):
    if not argv or argv[0] in ('-h', '--help'): print(__doc__); return 2
    cmd = argv[0]
    try:
        if cmd == 'pins':
            bad = pin_problems(); print('pins OK' if not bad else f'pins differ: {bad}'); return 0 if not bad else 3
        if cmd == 'status': return cmd_status()
        if cmd == 'report': return cmd_report()
        if cmd in ('branch', 'next', 'freeze', 'score', 'stop'):
            if '--held' not in argv: print(f'{cmd} needs --held 6.3|2.0|13.2'); return 2
            held = held_of(argv[argv.index('--held') + 1])
            if cmd == 'stop': return cmd_stop(held, argv[argv.index('--reason') + 1] if '--reason' in argv else '')
            return {'branch': cmd_branch, 'next': cmd_next, 'freeze': cmd_freeze, 'score': cmd_score}[cmd](held)
    except SystemExit as e:
        print(f'REFUSED: {e}'); return 3
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
