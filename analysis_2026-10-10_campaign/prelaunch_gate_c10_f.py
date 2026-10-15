"""C10 pre-launch gate for stage F = register section 3 steps 3-5 (S3: IGZO.TOKYO with S3-27, the GAMMA0 +0.30 entries, S3-10, tail runs;
register A48, 2026-10-15; no Codex review, D-63; Claude go under D-59). NO launch, NO file written, nothing sealed opened except the A48 (b)
activation read below. Run it immediately before EVERY invocation of config/campaign_C10_S3a_act.json (S3-12), config/campaign_C10_S3b_igzo.json
(S3-27, S3-11, S3-13, S3-15, S3-14, S3-16) and config/campaign_C10_S3c_tails.json (S3-10, S3-05, S3-06, S3-08, S3-09), in the same PowerShell
session and working directory (the package root) as the invocation:

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check]

It loads prelaunch_gate_c10_de.py (sha256 pinned below; 1b67776c, A47) and, through it, prelaunch_gate_c10.py (c173598d, A46) as modules for
their constants and helpers (Gate, process functions, amendment_logged, scripts/ and frozen-file pins, S1-06R/DIAG and D/E labels and order);
both gates are unchanged and exit 4 ("nothing to launch") for their own plans.

Exit codes (ONLY 0 is a pass): 0 the next plan is launchable (prints the ONE command); 1 a check failed or an input is unreadable (fail closed);
3 STOP: a started run has no finish row; 4 nothing to launch (every admitted stage F entry has started or is skipped); not a pass.

Checks
  interpreter/cwd/env  as the C10 gate (-I, project venv, package root, IWO_MODEL_FILE V3, IWO_ATLAS_VIEWERS / IWO_ATLAS_JOB unset)
  files        the D/E gate file (pinned) and the C10 gate file (pinned there); scripts/ file set and sha256 (public-repo 1375164 + builder
               734125a8); the C10 gate's OTHER files (frozen scorer c0f28bb9, post_run_checks, regress wrappers, campaign_extract/tools, A41 gate,
               V3 model); the frozen H-F v4 files (hf_score_draft.py 96a2147e, profile_s4s5.py 429b3a3f) and profile_shared.py 958c3605; the
               campaign matrix f06e8d77 and the plan generator; the three stage F plan files (pinned here)
  plans        each F plan: runnable, no gates, state_only results/sealed/campaigns, ids and labels as registered (A48), in A48 launch order
  dry build    run_campaign.current_deck_text / current_material_text for the 12 entries == pinned
  amendments   register heading '### A<n>: ...' naming PA-8, S3-12, S3-27, S3-15, S3-10, S3-05, S3-09 and 'stage F' (not draft) and an IN FORCE
               decision-log row naming A48, PA-8, S3-12, S3-15 and prelaunch_gate_c10_f.py
  processes    as the C10 gate (no Silvaco process, no runner python, every python command line readable)
  RUN_INDEX    run_id/label of every row; for runs above run_0077: the label is S1-06R/DIAG, D/E or stage F; every S1-06R/DIAG and every D/E
               entry has started and has a finish row (presence only for the sealed S1-06R/DIAG rows) BEFORE the first F run id; F labels never
               at or below run_0101, one run id per label, STARTED order == a prefix of the A48 order (the IGZO entries absent when S3-12 is not
               ACTIVE); STARTED-row input columns (deck_sha256, model_sha256, model note) as pinned; a finish row for every started F run (presence
               only; else STOP, exit 3); every started F run listed in config/sealed_runs.json with the pinned values (A41 (e))
  activation   A48 (b) / PA-8: once S3-12 has a finish row, its deckbuild.out (path results/runs/<run id>_6p3_c10_s3_12_6p3/deckbuild.out, no
               directory listing) is read line by line ONLY from the line 'REGIONAL MOBILITY MODEL SUMMARY' up to the next 'Contacts:' (or
               'ATLAS>') line, where reading stops; this block is printed before SOLVE INIT and holds no solution quantity. Per region the first
               electron-model line is taken. ACTIVE iff regions 1 and 2 both name IGZO.TOKYO (and neither says 'Concentration Independent');
               NOT_ACTIVE if either names another model; UNVERIFIED if the block or a region is missing. Only the per-region electron-model lines
               are printed. Not ACTIVE: the IGZO entries (S3-27, S3-11, S3-13, S3-15, S3-14, S3-16) are skipped in this stage and
               campaign_C10_S3c_tails follows (the PA-8 fallback needs a builder option and a role rule: main-session item).
  budget       config/solver.yaml exactly one max_launches == 260; C10 cap 200 (gate constant and run_campaign.C10_CAP); distinct run ids + k
               <= 260 and c10 run ids + k <= 200 (k = launches of the next invocation); PA-19 v3 F fit: c10 used + unlaunched F (PA-19 counts F as
               13: the 12 entries + the PA-8 S3-12 re-run slot) + the remaining worst-case never-cut need 145 (A41(d) 6 + G 89 + H 30 + S6 core 12 +
               S7 2 + repairs 6) <= 200
"""
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
DE_GATE = PKG / 'analysis_2026-10-10_campaign' / 'prelaunch_gate_c10_de.py'
DE_GATE_SHA = '1b67776ca5e5f167846b4246b4a4352fa5ec7ea4ccac7e2730783f48494cfd98'   # A47 / D-67
A_REL, B_REL, C_REL = 'config/campaign_C10_S3a_act.json', 'config/campaign_C10_S3b_igzo.json', 'config/campaign_C10_S3c_tails.json'
PLAN_SHA = {A_REL: 'b862d39b83093c21460bda3f52f4e26ae9ad23011b33440155e30250d5c11759', B_REL: 'be4af155e1b155877057698d39d307e9af909ad571777d53cb8a1881916fe77a',
            C_REL: '77affa8e02c063a68960f33ce388c001416769282953b6679f383957c2198aef'}
FROZEN = {'analysis_2026-10-10_campaign/hf_score_draft.py': '96a2147eae6a07a2ea0afbed2d63476283c2d5bca3ffdfd7f829f248af3a1c81',   # H-F v4 (frozen)
          'analysis_2026-10-10_campaign/profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',    # S4b/S5 v4 (frozen)
          'analysis_2026-10-10_campaign/profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
          'analysis_2026-10-10_campaign/campaign_matrix.json': 'f06e8d7721f75aec3f78da06de1c1686c59307c33725bd8822c3ec3e0f0a443c',
          'analysis_2026-10-10_campaign/make_campaign_configs.py': '3f266114081572580c7c1b5d373111fb77da0490f113502346130dba2c643536'}
ORDER = ['S3-12', 'S3-27', 'S3-11', 'S3-13', 'S3-15', 'S3-14', 'S3-16', 'S3-10', 'S3-05', 'S3-06', 'S3-08', 'S3-09']   # A48 launch order
IGZO_DEP = ('S3-27', 'S3-11', 'S3-13', 'S3-15', 'S3-14', 'S3-16')   # launched only after S3-12 showed IGZO.TOKYO ACTIVE in regions 1 and 2
PLAN_IDS = {A_REL: ['S3-12'], B_REL: ['S3-27', 'S3-11', 'S3-13', 'S3-15', 'S3-14', 'S3-16'], C_REL: ['S3-10', 'S3-05', 'S3-06', 'S3-08', 'S3-09']}
PLAN_OF = {k: rel for rel, ids in PLAN_IDS.items() for k in ids}
FILM = {'S3-12': 6.3, 'S3-27': 6.3, 'S3-11': 2.0, 'S3-13': 13.2, 'S3-15': 6.3, 'S3-14': 2.0, 'S3-16': 13.2, 'S3-10': 6.3, 'S3-05': 6.3, 'S3-06': 13.2,
        'S3-08': 6.3, 'S3-09': 13.2}
TAG = {2.0: '2p0', 6.3: '6p3', 13.2: '13p2'}
LABEL = {k: f'c10_{k.lower().replace("-", "_")}_{TAG[FILM[k]]}' for k in ORDER}
DECK = {'S3-12': 'c8b76ba9a76396df77fcf595ad0fe6570275cafe3153cbdfddd02a22331905a5', 'S3-27': '0b85b5d885f45c11d214c9809e4d6f2b013a76b50eaf9059a59fca39cd7c0a62',
        'S3-11': '98ce0ce374149b4316c300d0a205256a06d4e1b5188c6065a3f04430ce132837', 'S3-13': '1a549da18a0497b6a46dda07b5c366f8bf0f5096dbcff0412eb934c6fcac566b',
        'S3-15': '9dfbd0ffa58bab1ffb7f0ccfe9d6865e30d7bd2135c1ba34e3ce97b81b4804b8', 'S3-14': '1fc11c5cad2b0f5e250c05fe9f24c0097dd6f4dd5808775184ab31b47e0dfa9c',
        'S3-16': '61eb5eb5130473c28eebad899c3dbacc450c4555fd5884734cf89d93619e64d2', 'S3-10': 'a4073fec7f998f91522f259fe067b6ae4c8be43fa12fa54883192b86523e33b0',
        'S3-05': '60be25751092de10ceb65092554ba30fb44f7e2eb0ec03dd9f15284a6b07c04d', 'S3-06': 'cd9a91a1ad1be7849f9816bb2f4a4d2c8fe94dfc4195db01d29fe838e4e44930',
        'S3-08': '67ff5b49467beba59d1d9eea6fd27fbb9a09eccb0f03e121e58e90e94e75c357', 'S3-09': '18f64f0dc83e3f07010741b8df49cbfa35185eacb9bb4940d3515fa70ec8320f'}
_M0 = '974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204'
_BULK, _HALF = '71463208640439495a93ff0d9bb8be71dede890cee22288905992f9ca0310942', '81a8887f09b9055d755bb6bb3d984888be81a298f1e71ad6bc3fb181defc0472'
MATERIAL = {'S3-12': _M0, 'S3-27': 'ef593f4df70a3c18ffd967d62b303c192bd769470b22bf5a4a8b42e1b9cbcfee', 'S3-11': _M0, 'S3-13': _M0, 'S3-15': _M0,
            'S3-14': _M0, 'S3-16': _M0, 'S3-10': '6d83e34bdb5d079f4d2c0ef67036a35e51abfdc77ac57bd90b40e4e945675cb6', 'S3-05': _BULK, 'S3-06': _BULK,
            'S3-08': _HALF, 'S3-09': _HALF}
AMEND_HEADING = ['PA-8', 'S3-12', 'S3-27', 'S3-15', 'S3-10', 'S3-05', 'S3-09', 'stage F']
AMEND_ROW = ['A48', 'PA-8', 'S3-12', 'S3-15', 'prelaunch_gate_c10_f.py']
LAST_DE = 'run_0101'   # last D/E run (S2-10); every F run id is above it
SEALED_DIR = 'results/sealed/campaigns'
NEED_AFTER_F = 6 + 89 + 30 + 12 + 2 + 6   # PA-19 v3 worst case after F: A41(d) C 6, G 89, H 30, S6 core 12, S7 2, repairs 6 = 145
F_PA19 = 13                               # PA-19 v3 counts F (pre-S4) as 13 at most: 12 entries + the PA-8 S3-12 re-run slot
MOB_HEAD = 'REGIONAL MOBILITY MODEL SUMMARY'
RUNS = PKG / 'results' / 'runs'   # run directories: <run id>_<film tag>_<label>


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def de_module():
    spec = importlib.util.spec_from_file_location('prelaunch_gate_c10_de_pinned', DE_GATE); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def mobility_block(path):
    """lines of the REGIONAL MOBILITY MODEL SUMMARY block of a deckbuild.out, read line by line from its heading up to the next 'Contacts:' or
    'ATLAS>' line (reading stops there); None if the heading is absent. Nothing else of the file is kept."""
    out, inside = [], False
    with open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            s = raw.strip()
            if not inside:
                inside = s.startswith(MOB_HEAD); continue
            if s.startswith('Contacts:') or s.startswith('ATLAS>'): break
            out.append(s)
    return out if inside else None


def electron_models(block):
    """{region number: first non-empty line under 'Model for Electrons:'} from the block lines"""
    reg, mode, out = None, None, {}
    for s in block:
        m = re.match(r'Region\s*#\s*(\d+)\s*:', s)
        if m: reg, mode = m.group(1), None; continue
        if s.startswith('Model for Electrons'): mode = 'e'; continue
        if s.startswith('Model for Holes'): mode = 'h'; continue
        if reg and mode == 'e' and s and reg not in out: out[reg] = s
    return out


def activation(path):
    """('ACTIVE' | 'NOT_ACTIVE' | 'UNVERIFIED', {region: electron model line}) for regions 1 and 2 (A48 (b))"""
    if not Path(path).is_file(): return 'UNVERIFIED', {}
    blk = mobility_block(path)
    if blk is None: return 'UNVERIFIED', {}
    em = electron_models(blk); got = {r: em.get(r) for r in ('1', '2')}
    if any(v is None for v in got.values()): return 'UNVERIFIED', got
    igzo = [bool(re.search(r'IGZO\.TOKYO', v, re.I)) and 'Concentration Independent' not in v for v in got.values()]
    return ('ACTIVE' if all(igzo) else 'NOT_ACTIVE'), got


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if fsha(DE_GATE) != DE_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_de.py sha256 == {DE_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    DE = de_module(); C = DE.c10_module(); g = C.Gate()
    try:
        return run(DE, C, g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def run(DE, C, g, argv):
    check_mode = '--check' in argv
    print('C10 pre-launch gate, stage F = S3 steps 3-5 (campaign_C10_S3a_act, campaign_C10_S3b_igzo, campaign_C10_S3c_tails; register A48; no launch, '
          'nothing written)' + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10_de.py sha256 == {DE_GATE_SHA[:8]}... and prelaunch_gate_c10.py sha256 == {DE.C10_GATE_SHA[:8]}... (loaded for pins and helpers)')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    files_ok = True
    for rel, h in PLAN_SHA.items(): files_ok &= g.check(fsha(PKG / rel) == h, f'{rel} sha256 == {h[:8]}...')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)', '' if have == set(C.SCRIPTS) else f'extra {sorted(have - set(C.SCRIPTS))}, missing {sorted(set(C.SCRIPTS) - have)}')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 as pinned (build_iwo_decks.py {C.SCRIPTS["build_iwo_decks.py"][:8]})', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, **FROZEN}.items(): files_ok &= g.check(fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')

    plans = {rel: json.loads((PKG / rel).read_text()) for rel in PLAN_SHA}
    plans_ok = True
    for rel, p in plans.items():
        ids = [e['id'] for e in p['runs']]; labs = {e['id']: e['label'] for e in p['runs']}
        plans_ok &= g.check(p.get('runnable') is True and 'gates' not in p and p.get('state_only') == {'sealed_dir': SEALED_DIR} and ids == PLAN_IDS[rel]
                            and labs == {k: LABEL[k] for k in PLAN_IDS[rel]},
                            f'{rel}: runnable, no gates, state_only {SEALED_DIR}, ids {PLAN_IDS[rel]} with the registered labels', str(ids))
    rc_cap = None
    if files_ok and plans_ok:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        rc_cap = getattr(rc, 'C10_CAP', None)
        ent = {k: next(e for rel in PLAN_SHA for e in plans[rel]['runs'] if e['id'] == k) for k in ORDER}
        bad_d = [k for k, e in ent.items() if C.tsha(rc.current_deck_text(e, e['overrides'])) != DECK[k]]
        bad_m = [k for k, e in ent.items() if C.tsha(rc.current_material_text(e['overrides'])) != MATERIAL[k]]
        g.check(not bad_d, 'dry-built deck text sha256 == pinned for the 12 stage F entries', f'differ: {bad_d}' if bad_d else '')
        g.check(not bad_m, 'dry-built material text sha256 == pinned', f'differ: {bad_m}' if bad_m else '')
    else:
        g.check(False, 'dry build not run (file or plan check failed)')

    h, d = C.amendment_logged(AMEND_HEADING, AMEND_ROW)
    g.check(h, f'A48 logged: register heading "### A<n>: ..." naming {", ".join(AMEND_HEADING)} (not draft)')
    g.check(d, f'A48 logged: decision-log row naming {", ".join(AMEND_ROW)}, IN FORCE')

    try:
        procs = C.list_processes() if files_ok else None
        if procs is None: g.check(False, 'process check not run (file check failed)')
    except Exception as ex:
        procs = None; g.check(False, f'process list readable ({type(ex).__name__}: {ex})')
    if procs is not None:
        a = C.a41_module(); me = os.getpid()
        sil = sorted({f'{n} pid {p}' for p, n, _ in procs if n in a.SILVACO})
        pyp = [(p, n, c) for p, n, c in procs if p != me and a.is_python(n)]
        unver = sorted({f'{n} pid {p}' for p, n, c in pyp if not (isinstance(c, str) and c.strip())})
        runners = sorted({f'{n} pid {p}' for p, n, c in pyp if isinstance(c, str) and a.RUNNER_RE.search(c)})
        g.check(not sil, 'no DeckBuild/ATLAS/TonyPlot/Athena/DevEdit process running', ', '.join(sil))
        g.check(not unver, 'every other python process has a readable command line (else UNVERIFIABLE)', ', '.join(unver))
        g.check(not runners, 'no python process running run_atlas / run_campaign', ', '.join(runners))

    # RUN_INDEX: run_id/label of every row; for sealed rows (S1-06R/DIAG, stage F) only the STARTED-row input columns and finish-row presence
    c10_labels = set(C.LABEL.values()); de_of = {v: k for k, v in DE.LABEL.items()}; f_of = {v: k for k, v in LABEL.items()}
    pairs, rows_f, fin_c10, fin_de = [], {}, {}, {}
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            if C.rid_n(r['run_id']) <= C.rid_n(C.LAST_PRE): continue
            if r['label'] in f_of:
                rows_f.setdefault(r['run_id'], []).append({k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'notes', 'exit_code')})
            elif r['label'] in de_of:
                fin_de[r['run_id']] = fin_de.get(r['run_id'], False) or r.get('exit_code', '') != ''
            elif r['label'] in c10_labels:
                fin_c10[r['run_id']] = fin_c10.get(r['run_id'], False) or r.get('exit_code', '') != ''
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    after = sorted({rid for rid, _ in pairs if C.rid_n(rid) > C.rid_n(C.LAST_PRE)}, key=C.rid_n)
    lab_of = {}
    for rid, lab in pairs: lab_of.setdefault(rid, lab)
    other = [rid for rid in after if lab_of[rid] not in c10_labels and lab_of[rid] not in de_of and lab_of[rid] not in f_of]
    g.check(not other, f'RUN_INDEX: every run above {C.LAST_PRE} is S1-06R, a DIAG entry, a D/E entry or a stage F entry', str(other))
    early = sorted({rid for rid, lab in pairs if lab in f_of and C.rid_n(rid) <= C.rid_n(LAST_DE)}, key=C.rid_n)
    g.check(not early, f'RUN_INDEX: no stage F label at or below {LAST_DE}', str(early))
    eid_c10 = {v: k for k, v in C.LABEL.items()}; c10_started, de_started = {}, {}
    for rid in after:
        if lab_of[rid] in c10_labels: c10_started.setdefault(eid_c10[lab_of[rid]], rid)
        elif lab_of[rid] in de_of: de_started.setdefault(de_of[lab_of[rid]], rid)
    miss = [e for e in C.LAUNCH_ORDER if e not in c10_started] + [k for k in DE.ORDER if k not in de_started]
    unfin = ([f'{c10_started[e]} ({e})' for e in C.LAUNCH_ORDER if e in c10_started and not fin_c10.get(c10_started[e])]
             + [f'{de_started[k]} ({k})' for k in DE.ORDER if k in de_started and not fin_de.get(de_started[k])])
    g.check(not miss, 'every S1-06R/DIAG and D/E entry has started (DIAG, D and E exhausted before F)', f'not started: {miss}' if miss else '')
    g.check(not unfin, 'every started S1-06R/DIAG and D/E run has a finish row (presence only)', ', '.join(unfin))
    f_ids = [rid for rid in after if rid in rows_f]
    last_prev = max([C.rid_n(r) for r in list(c10_started.values()) + list(de_started.values())], default=0)
    g.check(all(C.rid_n(r) > last_prev for r in f_ids), 'every stage F run id is above the last S1-06R/DIAG/D/E run id', str(f_ids))
    started = {}
    for rid in f_ids:
        k = f_of[rows_f[rid][0]['label']]
        g.check(k not in started, f'RUN_INDEX: one run id per label ({LABEL[k]})', f'{started.get(k)} and {rid}' if k in started else '')
        started.setdefault(k, rid)
    finished = {}
    for k, rid in started.items():
        first = rows_f[rid][0]; n = first['notes']
        g.check(n.startswith('STARTED') and f'model={C.MODEL_ENV}' in n.split() and first['deck_sha256'] == DECK[k] and first['model_sha256'] == MATERIAL[k],
                f'{rid} ({k}): STARTED-row input columns as pinned (deck_sha256, model_sha256, model note)')
        finished[k] = any(x['exit_code'] != '' for x in rows_f[rid][1:])
    # sealed-run inventory (A41 (e)): every started F run listed with the pinned values
    inv = {x['run_id']: x for x in json.loads(C.INVENTORY.read_text())['runs']}
    for k, rid in started.items():
        x = inv.get(rid) or {}
        g.check(x.get('label') == LABEL[k] and x.get('entry') == k and x.get('deck_sha256') == DECK[k] and x.get('model_sha256') == MATERIAL[k]
                and x.get('model_file') == C.MODEL_ENV, f'{rid} ({k}) listed in config/sealed_runs.json with the pinned values (A41 (e))')
    # A48 (b) / PA-8 activation of IGZO.TOKYO from S3-12 (regions 1 and 2, electrons; the mobility summary block only)
    act = None
    if 'S3-12' in started and finished.get('S3-12'):
        dbo = RUNS / f'{started["S3-12"]}_6p3_{LABEL["S3-12"]}' / 'deckbuild.out'
        act, lines = activation(dbo)
        print(f'[INFO] S3-12 {started["S3-12"]} IGZO.TOKYO activation (A48 (b); REGIONAL MOBILITY MODEL SUMMARY, electrons): {act}; '
              + '; '.join(f'region {r}: {v}' for r, v in lines.items()) + ('' if act == 'ACTIVE' else
              ' -> the IGZO entries S3-27, S3-11, S3-13, S3-15, S3-14, S3-16 are skipped in this stage (PA-8 fallback: main-session item); S3-10 and the tails follow'),
              flush=True)
    order = [k for k in ORDER if not (k in IGZO_DEP and act is not None and act != 'ACTIVE')]
    launched = [f_of[rows_f[rid][0]['label']] for rid in f_ids]
    g.check(launched == order[:len(launched)], 'order: STARTED stage F runs == a prefix of the A48 order (IGZO entries skipped unless S3-12 is ACTIVE)',
            ' -> '.join(f'{k} {r}' for k, r in zip(launched, f_ids)) or 'none')
    if any(k in IGZO_DEP for k in launched) and act != 'ACTIVE':
        g.check(False, 'an IGZO entry started although S3-12 is not ACTIVE (or has no finish row)')
    unfinished = [f'{started[k]} ({k})' for k in started if not finished[k]]
    todo = [k for k in order if k not in started]
    if unfinished: g.stop(f'started stage F run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')
    plan_rel = PLAN_OF[todo[0]] if todo else None
    nxt_k = [k for k in todo if PLAN_OF[k] == plan_rel] if plan_rel else []
    if plan_rel == A_REL: nxt_k = ['S3-12']

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (D-58 (4): not raised)', f'found {ms}')
    g.check(C.C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; D-58 (4): not raised)', f'gate {C.C10_CAP}, runner {rc_cap}')
    g.check(cap > 0 and len(all_ids) + len(nxt_k) <= cap, f'global budget: {len(all_ids)} used + {len(nxt_k)} <= max_launches {cap}')
    g.check(c10 + len(nxt_k) <= 200, f'C10 cap: {c10} used + {len(nxt_k)} <= 200')
    f_left = F_PA19 - len(started)
    g.check(c10 + f_left + NEED_AFTER_F <= 200, f'PA-19 v3 F fit: c10 {c10} + unlaunched F {f_left} (F counted as 13) + worst-case never-cut need '
            f'{NEED_AFTER_F} = {c10 + f_left + NEED_AFTER_F} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/200; stage F started: '
          + (', '.join(f'{k} {r}' for k, r in started.items()) or 'none') + f'; next free id {nxt}', flush=True)

    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True); return 1
    if g.stops:
        print(f'GATE STOP ({len(g.stops)}): a main-session decision is needed; nothing may be invoked.', flush=True); return 3
    if not todo:
        print('NOTHING TO LAUNCH: every admitted stage F entry has started' + ('' if act in (None, 'ACTIVE') else f' (IGZO entries skipped: S3-12 {act})')
              + '. Do not invoke the stage F plans again. (Exit 4 is not a pass.)', flush=True); return 4
    cmd = f'& "{C.VENV_PY}" scripts/run_campaign.py {plan_rel}'
    print(f'GATE PASSED. Next plan {plan_rel}: {" -> ".join(f"{k} ({LABEL[k]})" for k in nxt_k)}, first run id {nxt}; the invocation runs these '
          f'{len(nxt_k)} entr{"y" if len(nxt_k) == 1 else "ies"} in order and stops. Only with the go for THIS launch (the hook asks). '
          + ('Would-be command (check mode, not an instruction)' if check_mode else 'Command (same PowerShell session, package root, IWO_MODEL_FILE as set)')
          + f':\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
