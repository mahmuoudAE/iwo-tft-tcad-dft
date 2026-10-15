"""C10 pre-launch gate for branches D and E (register A47, 2026-10-15; A45 (c) = PA-4 tunnelling-mesh branch, A45 (d) = PA-5 FNORD; no Codex
review, D-63; Claude go under D-59). NO launch, NO file written, nothing sealed opened. Run it immediately before EVERY invocation of
config/campaign_C10_Dmesh.json (T0r, T2a), config/campaign_C10_Dmesh_T2b.json (T2b) and config/campaign_C10_Efnord.json (S2-09, S2-10), in the
same PowerShell session and working directory (the package root) as the invocation:

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check]

It loads prelaunch_gate_c10.py (sha256 pinned below; c173598d, A46) as a module for its constants and helpers (Gate, process functions,
amendment_logged, the scripts/ and frozen-file pins, the S1-06R/DIAG labels and launch order); that gate itself is unchanged and exits 4
("nothing to launch") once DIAG is exhausted.

Exit codes (ONLY 0 is a pass): 0 the next plan is launchable (prints the ONE command); 1 a check failed or an input is unreadable (fail
closed); 3 STOP: a started run has no finish row; 4 nothing to launch (every admitted D/E entry has started or is skipped); not a pass.

Checks
  interpreter/cwd/env  as the C10 gate (-I, project venv, package root, IWO_MODEL_FILE V3, IWO_ATLAS_VIEWERS / IWO_ATLAS_JOB unset)
  files        the C10 gate file (pinned); scripts/ file set and sha256 (the C10 gate's SCRIPTS: public-repo 1375164 + builder 734125a8);
               the C10 gate's OTHER files (frozen scorer c0f28bb9, post_run_checks, regress wrappers, campaign_extract/tools, A41 gate, V3 model);
               the S1R and DIAG plan files (C10 gate pins, unchanged); the three D/E plan files and branch_d_readout.py (pinned here)
  plans        each D/E plan: runnable, no gates, not state-only, ids and labels as registered (A47)
  dry build    run_campaign.current_deck_text / current_material_text for the 5 entries == pinned (T0r 11128b7b, T2a ab87682c, T2b 81f78eea:
               = the A45 (c) dry builds; S2-09 084840e0, S2-10 037b69a8; material 974b23ea)
  amendments   register heading '### A<n>: ...' naming PA-4, PA-5, T0r, T2a, T2b, S2-09 and S2-10 (not draft) and a decision-log row naming
               PA-4, PA-5, T0r, S2-09 and branch_d_readout.py, IN FORCE (A47 / its D row)
  processes    as the C10 gate (no Silvaco process, no runner python, every python command line readable)
  RUN_INDEX    run_id/label of every row; for runs above run_0077: the label is S1-06R/DIAG or D/E; every S1-06R/DIAG entry of the C10 launch
               order has started and has a finish row (presence only: no other column of these sealed rows is read) BEFORE the first D/E
               run id; D/E labels never at or below run_0077, one run id per label, STARTED order == a prefix of T0r -> T2a -> T2b -> S2-09 ->
               S2-10 (T2b absent when T2a ran out of memory); STARTED-row input columns (deck_sha256, model_sha256, model note) as pinned;
               a finish row for every started D/E run (else STOP, exit 3)
  T2b rule     T2b runs only if T2a finished without "Error: Memory allocation failure" in its (unsealed) deckbuild.out (A45 (c): "T2b does not
               run if T2a runs out of memory"; no repeat, no factor change). Otherwise T2b is skipped (UNRESOLVED) and E follows.
  budget       config/solver.yaml exactly one max_launches == 260; C10 cap 200 (gate constant and run_campaign.C10_CAP); distinct run ids + k
               <= 260 and c10 run ids + k <= 200 (k = launches of the next invocation); PA-19 v3 D/E fit check: c10 used + unlaunched D/E
               (PA-19 counts E as 3) + the remaining worst-case never-cut need 158 (A41(d) 6 + F 13 + G 89 + H 30 + S6 core 12 + S7 2 +
               repairs 6) <= 200
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
C10_GATE = PKG / 'analysis_2026-10-10_campaign' / 'prelaunch_gate_c10.py'
C10_GATE_SHA = 'c173598d731730fbbb78abd9793c1b7917b037e1140769f753863166d9382594'   # A46 / D-65
READOUT = 'analysis_2026-10-10_campaign/branch_d_readout.py'
READOUT_SHA = 'e368603f6ffd4f4cf346c9697d8ec9ed0c614bbd2d97e35eaaf6fc1c075a689c'
D1_REL, D2_REL, E_REL = 'config/campaign_C10_Dmesh.json', 'config/campaign_C10_Dmesh_T2b.json', 'config/campaign_C10_Efnord.json'
PLAN_SHA = {D1_REL: '68ffaac02db389149c31cac92d4c3d37fa19417d01266a0d63b34abbeeb2dd98', D2_REL: '6d475f7acc07cce79a0268b6da33422a1759821fba8a59ebe280c5cd1cd5700b', E_REL: '51cdeb26e418f283daeb66bec630264c0ead2a716d8e2cccbe7ed52440b3ce7f'}
PLAN_IDS = {D1_REL: ['S0-02-TOLX001', 'S0-02-QTM2'], D2_REL: ['S0-02-QTM3'], E_REL: ['S2-09', 'S2-10']}
ORDER = ['T0r', 'T2a', 'T2b', 'S2-09', 'S2-10']
ENTRY = {'T0r': 'S0-02-TOLX001', 'T2a': 'S0-02-QTM2', 'T2b': 'S0-02-QTM3', 'S2-09': 'S2-09', 'S2-10': 'S2-10'}
PLAN_OF = {'T0r': D1_REL, 'T2a': D1_REL, 'T2b': D2_REL, 'S2-09': E_REL, 'S2-10': E_REL}
LABEL = {'T0r': 'c10_s0_02_tolx001_2p0', 'T2a': 'c10_s0_02_qtm2_2p0', 'T2b': 'c10_s0_02_qtm3_2p0', 'S2-09': 'c10_s2_09_2p0', 'S2-10': 'c10_s2_10_13p2'}
DECK = {'T0r': '11128b7baf739201d99dee1ed7bbd985e4946f1b6be599b7fdd634acfecf97c6', 'T2a': 'ab87682cca051e873399c90c494d9fa3acd5ab52d6aee55cb74164e9125b00aa',
        'T2b': '81f78eea15b9bac177540f73ded7d5325fdce575666950cfccbfb3434e122664', 'S2-09': '084840e0b040bb324a4d27a6571cf72fcd90c877e3c61a4eb48c1cd9a9d09f78',
        'S2-10': '037b69a887106a3da9994a920565423a94f159729c0ace766263e77305c5ef28'}
MATERIAL = {k: '974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204' for k in ORDER}
AMEND_HEADING = ['PA-4', 'PA-5', 'T0r', 'T2a', 'T2b', 'S2-09', 'S2-10']
AMEND_ROW = ['PA-4', 'PA-5', 'T0r', 'S2-09', 'branch_d_readout.py']
OOM_RE = re.compile(r'^\s*Error:\s*Memory allocation failure', re.I | re.M)
NEED_AFTER_DE = 6 + 13 + 89 + 30 + 12 + 2 + 6   # PA-19 v3 worst case after D/E: A41(d) C 6, F 13, G 89, H 30, S6 core 12, S7 2, repairs 6 = 158
DE_PA19 = 6                                     # PA-19 v3 counts D 3 + E 3 (E3 S2-12-TSP24 not admitted here: S2-12 run_0085 invalid)


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def c10_module():
    spec = importlib.util.spec_from_file_location('prelaunch_gate_c10_pinned', C10_GATE); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if fsha(C10_GATE) != C10_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10.py sha256 == {C10_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    C = c10_module(); g = C.Gate()
    try:
        return run(C, g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def list_processes(C): return C.list_processes()


def run(C, g, argv):
    check_mode = '--check' in argv
    print('C10 pre-launch gate, branches D and E (campaign_C10_Dmesh, campaign_C10_Dmesh_T2b, campaign_C10_Efnord; register A47; no launch, '
          'nothing written)' + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10.py sha256 == {C10_GATE_SHA[:8]}... (loaded for its pins and helpers)')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    files_ok = True
    for rel, h in {**C.PLAN_SHA, **PLAN_SHA}.items(): files_ok &= g.check(fsha(PKG / rel) == h, f'{rel} sha256 == {h[:8]}...')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)', '' if have == set(C.SCRIPTS) else f'extra {sorted(have - set(C.SCRIPTS))}, missing {sorted(set(C.SCRIPTS) - have)}')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 as pinned (build_iwo_decks.py {C.SCRIPTS["build_iwo_decks.py"][:8]})', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, READOUT: READOUT_SHA}.items(): files_ok &= g.check(fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')

    plans = {rel: json.loads((PKG / rel).read_text()) for rel in PLAN_SHA}
    plans_ok = True
    for rel, p in plans.items():
        ids = [e['id'] for e in p['runs']]; labs = {e['id']: e['label'] for e in p['runs']}
        want = {ENTRY[k]: LABEL[k] for k in ORDER if PLAN_OF[k] == rel}
        plans_ok &= g.check(p.get('runnable') is True and 'gates' not in p and 'state_only' not in p and ids == PLAN_IDS[rel] and labs == want,
                            f'{rel}: runnable, no gates, not state-only, ids {PLAN_IDS[rel]} with the registered labels', str(ids))
    rc_cap = None
    if files_ok and plans_ok:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        rc_cap = getattr(rc, 'C10_CAP', None)
        ent = {k: next(e for rel in PLAN_SHA for e in plans[rel]['runs'] if e['id'] == ENTRY[k]) for k in ORDER}
        bad_d = [k for k, e in ent.items() if C.tsha(rc.current_deck_text(e, e['overrides'])) != DECK[k]]
        bad_m = [k for k, e in ent.items() if C.tsha(rc.current_material_text(e['overrides'])) != MATERIAL[k]]
        g.check(not bad_d, 'dry-built deck text sha256 == pinned for T0r, T2a, T2b, S2-09, S2-10', f'differ: {bad_d}' if bad_d else '')
        g.check(not bad_m, 'dry-built material text sha256 == pinned (974b23ea)', f'differ: {bad_m}' if bad_m else '')
    else:
        g.check(False, 'dry build not run (file or plan check failed)')

    h, d = C.amendment_logged(AMEND_HEADING, AMEND_ROW)
    g.check(h, f'A47 logged: register heading "### A<n>: ..." naming {", ".join(AMEND_HEADING)} (not draft)')
    g.check(d, f'A47 logged: decision-log row naming {", ".join(AMEND_ROW)}, IN FORCE')

    try:
        procs = list_processes(C) if files_ok else None
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

    # RUN_INDEX
    c10_labels = set(C.LABEL.values()); de_of = {v: k for k, v in LABEL.items()}
    pairs, rows_de, fin_c10 = [], {}, {}
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            if C.rid_n(r['run_id']) <= C.rid_n(C.LAST_PRE): continue
            if r['label'] in de_of:
                rows_de.setdefault(r['run_id'], []).append({k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'notes', 'exit_code', 'output_dir')})
            elif r['label'] in c10_labels:   # sealed S1-06R/DIAG rows: presence of a finish row only
                fin_c10[r['run_id']] = fin_c10.get(r['run_id'], False) or r.get('exit_code', '') != ''
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    after = sorted({rid for rid, _ in pairs if C.rid_n(rid) > C.rid_n(C.LAST_PRE)}, key=C.rid_n)
    lab_of = {}
    for rid, lab in pairs: lab_of.setdefault(rid, lab)
    other = [rid for rid in after if lab_of[rid] not in c10_labels and lab_of[rid] not in de_of]
    g.check(not other, f'RUN_INDEX: every run above {C.LAST_PRE} is S1-06R, a DIAG entry or a D/E entry', str(other))
    early = sorted({rid for rid, lab in pairs if lab in de_of and C.rid_n(rid) <= C.rid_n(C.LAST_PRE)}, key=C.rid_n)
    g.check(not early, f'RUN_INDEX: no D/E label at or below {C.LAST_PRE}', str(early))
    eid_c10 = {v: k for k, v in C.LABEL.items()}
    c10_started = {}
    for rid in after:
        if lab_of[rid] in c10_labels: c10_started.setdefault(eid_c10[lab_of[rid]], rid)
    miss = [e for e in C.LAUNCH_ORDER if e not in c10_started]
    unfin = [f'{c10_started[e]} ({e})' for e in C.LAUNCH_ORDER if e in c10_started and not fin_c10.get(c10_started[e])]
    g.check(not miss, 'every S1-06R/DIAG entry of the C10 launch order has started (DIAG exhausted before D/E)', f'not started: {miss}' if miss else '')
    g.check(not unfin, 'every started S1-06R/DIAG run has a finish row (presence only)', ', '.join(unfin))
    de_ids = [rid for rid in after if rid in rows_de]
    last_c10 = max((C.rid_n(r) for r in c10_started.values()), default=0)
    g.check(all(C.rid_n(r) > last_c10 for r in de_ids), 'every D/E run id is above the last S1-06R/DIAG run id', str(de_ids))
    started = {}
    for rid in de_ids:
        k = de_of[rows_de[rid][0]['label']]
        g.check(k not in started, f'RUN_INDEX: one run id per label ({LABEL[k]})', f'{started.get(k)} and {rid}' if k in started else '')
        started.setdefault(k, rid)
    finished = {}
    for k, rid in started.items():
        first = rows_de[rid][0]; n = first['notes']
        g.check(n.startswith('STARTED') and f'model={C.MODEL_ENV}' in n.split() and first['deck_sha256'] == DECK[k] and first['model_sha256'] == MATERIAL[k],
                f'{rid} ({k}): STARTED-row input columns as pinned (deck_sha256, model_sha256, model note)')
        fin = [x for x in rows_de[rid][1:] if x['exit_code'] != '']
        finished[k] = fin[-1] if fin else None
    # T2b rule: skipped if T2a ran out of memory (T2a is not sealed: its deckbuild.out is read for the OOM line only)
    t2a_oom = None
    if 'T2a' in started and finished.get('T2a') is not None:
        od = next((x['output_dir'] for x in reversed(rows_de[started['T2a']]) if x['output_dir']), '')
        dbo = PKG / od / 'deckbuild.out' if od else None
        t2a_oom = bool(dbo is not None and dbo.is_file() and OOM_RE.search(dbo.read_text(errors='replace')))
        print(f'[INFO] T2a {started["T2a"]}: ' + ('OUT OF MEMORY ("Error: Memory allocation failure" in deckbuild.out): T2b is not run (A45 (c)); UNRESOLVED'
                                                  if t2a_oom else 'no memory-allocation failure in deckbuild.out: T2b may run'), flush=True)
    order = [k for k in ORDER if not (k == 'T2b' and t2a_oom)]
    launched = [de_of[rows_de[rid][0]['label']] for rid in de_ids]
    g.check(launched == order[:len(launched)], 'order: STARTED D/E runs == a prefix of T0r -> T2a -> T2b -> S2-09 -> S2-10 (T2b skipped after a T2a OOM)',
            ' -> '.join(f'{k} {r}' for k, r in zip(launched, de_ids)) or 'none')
    unfinished = [f'{started[k]} ({k})' for k in started if finished[k] is None]
    todo = [k for k in order if k not in started]
    if unfinished: g.stop(f'started D/E run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')
    plan_rel = PLAN_OF[todo[0]] if todo else None
    k_next = len([k for k in todo if PLAN_OF[k] == plan_rel]) if plan_rel else 0

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (D-58 (4): not raised)', f'found {ms}')
    g.check(C.C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; D-58 (4): not raised)', f'gate {C.C10_CAP}, runner {rc_cap}')
    g.check(cap > 0 and len(all_ids) + k_next <= cap, f'global budget: {len(all_ids)} used + {k_next} <= max_launches {cap}')
    g.check(c10 + k_next <= 200, f'C10 cap: {c10} used + {k_next} <= 200')
    de_left = DE_PA19 - len(started)
    g.check(c10 + de_left + NEED_AFTER_DE <= 200, f'PA-19 v3 D/E fit: c10 {c10} + unlaunched D/E {de_left} (E counted as 3) + worst-case never-cut need '
            f'{NEED_AFTER_DE} = {c10 + de_left + NEED_AFTER_DE} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/200; D/E started: '
          + (', '.join(f'{k} {r}' for k, r in started.items()) or 'none') + f'; next free id {nxt}', flush=True)

    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True); return 1
    if g.stops:
        print(f'GATE STOP ({len(g.stops)}): a main-session decision is needed; nothing may be invoked.', flush=True); return 3
    if not todo:
        print('NOTHING TO LAUNCH: every admitted D/E entry has started' + (' (T2b skipped after the T2a OOM)' if t2a_oom else '')
              + '. Do not invoke the D/E plans again. (Exit 4 is not a pass.)', flush=True); return 4
    cmd = f'& "{C.VENV_PY}" scripts/run_campaign.py {plan_rel}'
    nxt_k = [k for k in todo if PLAN_OF[k] == plan_rel]
    print(f'GATE PASSED. Next plan {plan_rel}: {" -> ".join(f"{k} ({LABEL[k]})" for k in nxt_k)}, first run id {nxt}; the invocation runs these '
          f'{len(nxt_k)} entr{"y" if len(nxt_k) == 1 else "ies"} in order and stops. Only with the go for THIS launch (the hook asks). '
          + ('Would-be command (check mode, not an instruction)' if check_mode else 'Command (same PowerShell session, package root, IWO_MODEL_FILE as set)')
          + f':\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
