"""C10 pre-launch gate for the S4a RESUME after the interrupted launch run_0150 (S4A-14-2p0) (register A51, 2026-10-15; no Codex review, D-63;
Claude go under D-59). NO launch, NO file written, nothing sealed opened. It replaces prelaunch_gate_c10_g.py (A50; unchanged, pinned here) for
the remaining invocations of config/campaign_C10_S4a_b3.json only. Run it immediately before EVERY such invocation (the first resume and any
re-invocation after an interruption, a crash, sleep or a declined hook), in the same PowerShell session and working directory (the package root):

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check]

Why a new gate: run_0150 (S4A-14-2p0, c10_s4a_14_2p0_2p0) has its RUN_INDEX STARTED row only. The batch 3 invocation ended with the launching
agent session (~2026-10-15T14:53Z) and left no Silvaco or runner process; the A50 gate therefore stops (exit 3, "a started run has no finish row").
A51 records run_0150 as an interrupted launch (kept, sealed, never opened, never scored or substituted; it counts as a launch) and admits ONE
infrastructure retry of S4A-14-2p0 under its registered label, through run_campaign's own exception `--retry S4A-14-2p0` (the C10 label rule
never re-launches a label that already has a RUN_INDEX row; run_campaign.py earlier_launch / --retry), with the identical registered deck.

--retry rule (RUN_INDEX run_id and label only): the printed command carries `--retry S4A-14-2p0` if and only if no c10_s4a_14_2p0_2p0 row with
a run id above run_0150 exists; once the retry has a STARTED row it is never passed again (a third S4A-14-2p0 launch is never made; a failed or
interrupted retry is recorded invalid and kept, and S4A-14 is then UNKNOWN in the S4a inventory, A49 (d) / B3).

It loads prelaunch_gate_c10_g.py (sha256 pinned below; 75a22c4d, A50) and, through it, the F, D/E and C10 gates (all unchanged, their pins
checked) as modules for constants and helpers (Gate, process functions, amendment_logged, scripts/ and frozen-file pins, labels, decks, order).

Exit codes (ONLY 0 is a pass): 0 the next invocation is launchable (prints the ONE command); 1 a check failed or an input is unreadable (fail
closed); 3 STOP: a started run other than run_0150 has no finish row; 4 nothing to launch (every S4a entry has a non-interrupted run); not a pass.

Checks (as the A50 gate, with the A51 changes marked *)
  interpreter/cwd/env  -I, project venv, package root, IWO_MODEL_FILE V3, IWO_ATLAS_VIEWERS / IWO_ATLAS_JOB unset
  files        * the A50 gate file (pinned); the F, D/E and C10 gate files; scripts/ file set and sha256; the C10 gate's OTHER files; the frozen
               H-F v4 files and profile_shared.py; campaign_matrix.json; the generator; the A49 driver and decision record (form N); the three S4a
               route plans and the held stage plan
  plans / dry build / PA-12 reuse   as the A50 gate (42 pinned decks and materials; S4A-01 = run_0061 / run_0068 / run_0069)
  amendments   A49, A50 and * A51 (register heading naming the interrupted launch, run_0150, S4A-14-2p0, --retry S4A-14-2p0 and this gate, not
               draft; IN FORCE decision-log row naming A51, run_0150, --retry S4A-14-2p0 and this gate)
  processes    no Silvaco process, no runner python, every python command line readable
  RUN_INDEX    as the A50 gate, except: * run_0150 must exist with label c10_s4a_14_2p0_2p0, its STARTED-row inputs as pinned and NO finish row
               (a finish row = not the registered interrupted launch: fail); * S4A-14-2p0 may hold two run ids, run_0150 and one retry above it;
               every other label one run id; * order: the STARTED sequence == S4A-02-2p0 ... S4A-13-13p2, run_0150 (S4A-14-2p0), then a prefix of
               S4A-14-2p0 ... S4A-15-13p2; * a finish row for every started S4a run except run_0150 (else STOP, exit 3); every started S4a run,
               run_0150 included, listed in config/sealed_runs.json with the pinned values (A41 (e))
  budget       max_launches 260 and C10 cap 200 unchanged; distinct run ids + k <= 260 and c10 run ids + k <= 200 (k = launches of the next
               invocation, the retry included while pending); * A51 fit (PA-19 v3 section 4 item 4): c10 used + unlaunched S4a (retry included) +
               the never-cut need after S4a 100 (six repairs included and still reserved) <= 200
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
G_GATE = PKG / 'analysis_2026-10-10_campaign' / 'prelaunch_gate_c10_g.py'
G_GATE_SHA = '75a22c4d678ab46fd2825516e8765efa0e6e8984474af2718bf4734909c78e61'   # A50 / D-70
INTERRUPTED = 'run_0150'          # A51: the interrupted launch (STARTED row only)
RETRY_K = 'S4A-14-2p0'            # A51: the one admitted infrastructure retry
A51_HEADING = ['interrupted launch', 'run_0150', 'S4A-14-2p0', '--retry S4A-14-2p0', 'prelaunch_gate_c10_g2.py']
A51_ROW = ['A51', 'run_0150', '--retry S4A-14-2p0', 'prelaunch_gate_c10_g2.py']
NEED_AFTER_S4A = 6 + 17 + 18 + 6 + 3 + 30 + 12 + 2 + 6   # A49 (h): never-cut need after S4a = 100 (six repairs included, reserved)


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def g_module():
    spec = importlib.util.spec_from_file_location('prelaunch_gate_c10_g_pinned', G_GATE); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if fsha(G_GATE) != G_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_g.py sha256 == {G_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    G = g_module()
    if fsha(G.F_GATE) != G.F_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_f.py sha256 == {G.F_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    FG = G.f_module()
    if fsha(FG.DE_GATE) != FG.DE_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_de.py sha256 == {FG.DE_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    DE = FG.de_module()
    if fsha(DE.C10_GATE) != DE.C10_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10.py sha256 == {DE.C10_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    C = DE.c10_module(); g = C.Gate()
    try:
        return run(G, FG, DE, C, g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def run(G, FG, DE, C, g, argv):
    check_mode = '--check' in argv
    ORDER, LABEL, DECK, MATERIAL, B3 = G.ORDER, G.LABEL, G.DECK, G.MATERIAL, G.B3
    print('C10 pre-launch gate, S4a RESUME after the interrupted launch run_0150 (campaign_C10_S4a_b3; register A49 / A50 / A51; no launch, '
          'nothing written)' + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10_g.py sha256 == {G_GATE_SHA[:8]}... (loaded with the F, D/E and C10 gates for pins and helpers)')
    g.check(G.NEED_AFTER_S4A == 100, 'A50 gate: never-cut need after S4a == 100 (A49 (h))', f'{G.NEED_AFTER_S4A}')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    files_ok = g.check(fsha(G.F_GATE) == G.F_GATE_SHA and fsha(FG.DE_GATE) == FG.DE_GATE_SHA and fsha(DE.C10_GATE) == DE.C10_GATE_SHA,
                       f'prelaunch_gate_c10_f.py {G.F_GATE_SHA[:8]}..., prelaunch_gate_c10_de.py {FG.DE_GATE_SHA[:8]}..., prelaunch_gate_c10.py '
                       f'{DE.C10_GATE_SHA[:8]}... as pinned')
    for rel, h in G.PLAN_SHA.items(): files_ok &= g.check(fsha(PKG / rel) == h, f'{rel} sha256 == {h[:8]}...')
    files_ok &= g.check(fsha(PKG / G.STAGE) == G.STAGE_SHA, f'{G.STAGE} sha256 == {G.STAGE_SHA[:8]}... (held stage plan, A50 hold text)')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)',
                        '' if have == set(C.SCRIPTS) else f'extra {sorted(have - set(C.SCRIPTS))}, missing {sorted(set(C.SCRIPTS) - have)}')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 as pinned (build_iwo_decks.py {C.SCRIPTS["build_iwo_decks.py"][:8]})', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, **G.FROZEN}.items(): files_ok &= g.check(fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')
    dok, ddet = G.decision_ok(PKG / G.DECISION)
    files_ok &= g.check(dok, 'A49 decision record: S4a form N (nothing adopted; 2-D LHS seed 20261010; 42 launches)', ddet)

    plans = {rel: json.loads((PKG / rel).read_text()) for rel in G.PLAN_SHA}
    plans_ok = True
    for rel, p in plans.items():
        ids = [e['id'] for e in p['runs']]; labs = {e['id']: e['label'] for e in p['runs']}; tos = {e['id']: e['timeout'] for e in p['runs']}
        plans_ok &= g.check(p.get('runnable') is True and 'gates' not in p and p.get('state_only') == {'sealed_dir': G.SEALED_DIR}
                            and ids == G.PLAN_IDS[rel] and labs == {k: LABEL[k] for k in G.PLAN_IDS[rel]}
                            and tos == {k: G.TIMEOUT[k.split('-')[-1]] for k in G.PLAN_IDS[rel]},
                            f'{rel}: runnable, no gates, state_only {G.SEALED_DIR}, ids {G.PLAN_IDS[rel][0]}..{G.PLAN_IDS[rel][-1]} with the registered '
                            'labels and timeouts', f'{ids[:2]}...')
    stage = json.loads((PKG / G.STAGE).read_text())
    plans_ok &= g.check(stage.get('runnable') is False and [e['id'] for e in stage['runs']][:3] == list(G.REUSE), f'{G.STAGE}: held, starts with S4A-01-*')
    plans_ok &= g.check(RETRY_K in G.PLAN_IDS[B3], f'{RETRY_K} is an entry of {B3}')
    rc_cap = None
    if files_ok and plans_ok:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        rc_cap = getattr(rc, 'C10_CAP', None)
        ent = {k: next(e for rel in G.PLAN_SHA for e in plans[rel]['runs'] if e['id'] == k) for k in ORDER}
        bad_d = [k for k, e in ent.items() if C.tsha(rc.current_deck_text(e, e['overrides'])) != DECK[k]]
        bad_m = [k for k, e in ent.items() if C.tsha(rc.current_material_text(e['overrides'])) != MATERIAL[k]]
        g.check(not bad_d, 'dry-built deck text sha256 == pinned for the 42 S4a entries (the retry deck == the registered S4A-14-2p0 deck)',
                f'differ: {bad_d}' if bad_d else '')
        g.check(not bad_m, 'dry-built material text sha256 == pinned', f'differ: {bad_m}' if bad_m else '')
        reuse_dry = {e['id']: (C.tsha(rc.current_deck_text(e, e['overrides'])), C.tsha(rc.current_material_text(e['overrides']))) for e in stage['runs'][:3]}
    else:
        g.check(False, 'dry build not run (file or plan check failed)'); reuse_dry = {}

    for words, row, what in ((G.A49_HEADING, G.A49_ROW, 'A49'), (G.A50_HEADING, G.A50_ROW, 'A50'), (A51_HEADING, A51_ROW, 'A51')):
        h, d = C.amendment_logged(words, row)
        g.check(h, f'{what} logged: register heading "### A<n>: ..." naming {", ".join(words)} (not draft)')
        g.check(d, f'{what} logged: decision-log row naming {", ".join(row)}, IN FORCE')

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

    # RUN_INDEX: run_id/label of every row; for sealed rows only the STARTED-row input columns and finish-row presence
    c10_labels = set(C.LABEL.values()); de_of = {v: k for k, v in DE.LABEL.items()}; f_of = {v: k for k, v in FG.LABEL.items()}
    s_of = {v: k for k, v in LABEL.items()}
    pairs, rows_s, fin_f, reuse_rows = [], {}, {}, {}
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            if r['run_id'] in {v[0] for v in G.REUSE.values()} and r.get('notes', '').startswith('STARTED'):
                reuse_rows.setdefault(r['run_id'], (r['label'], r['deck_sha256'], r['model_sha256']))
            if C.rid_n(r['run_id']) <= C.rid_n(C.LAST_PRE): continue
            if r['label'] in s_of:
                rows_s.setdefault(r['run_id'], []).append({k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'notes', 'exit_code')})
            elif r['label'] in f_of:
                fin_f[r['run_id']] = fin_f.get(r['run_id'], False) or r.get('exit_code', '') != ''
    for k, (rid, lab, dk, mk) in G.REUSE.items():
        got = reuse_rows.get(rid); dry = reuse_dry.get(k)
        g.check(got is not None and got[0] == lab and got[1] == dk and got[2] == mk and dry is not None and dry == (dk, mk),
                f'PA-12: {k} reused as {rid} ({lab}): dry-built deck/material == its STARTED-row deck_sha256/model_sha256')
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    after = sorted({rid for rid, _ in pairs if C.rid_n(rid) > C.rid_n(C.LAST_PRE)}, key=C.rid_n)
    lab_of = {}
    for rid, lab in pairs: lab_of.setdefault(rid, lab)
    other = [rid for rid in after if lab_of[rid] not in c10_labels and lab_of[rid] not in de_of and lab_of[rid] not in f_of and lab_of[rid] not in s_of]
    g.check(not other, f'RUN_INDEX: every run above {C.LAST_PRE} is S1-06R, a DIAG, D/E, stage F or S4a entry', str(other))
    early = sorted({rid for rid, lab in pairs if lab in s_of and C.rid_n(rid) <= C.rid_n(G.LAST_F)}, key=C.rid_n)
    g.check(not early, f'RUN_INDEX: no S4a label at or below {G.LAST_F}', str(early))
    f_started = {}
    for rid in after:
        if lab_of[rid] in f_of: f_started.setdefault(f_of[lab_of[rid]], rid)
    miss = [k for k in FG.ORDER if k not in f_started]; unfin = [f'{f_started[k]} ({k})' for k in FG.ORDER if k in f_started and not fin_f.get(f_started[k])]
    g.check(not miss, 'every stage F entry has started (stage F exhausted before S4a)', f'not started: {miss}' if miss else '')
    g.check(not unfin, 'every started stage F run has a finish row (presence only)', ', '.join(unfin))
    s_ids = [rid for rid in after if rid in rows_s]
    last_f = max([C.rid_n(r) for r in f_started.values()], default=0)
    g.check(all(C.rid_n(r) > last_f for r in s_ids), 'every S4a run id is above the last stage F run id', str(s_ids))

    # A51: the interrupted launch run_0150 and the one admitted retry of S4A-14-2p0
    int_rows = rows_s.get(INTERRUPTED)
    int_ok = g.check(int_rows is not None and int_rows[0]['label'] == LABEL[RETRY_K],
                     f'A51: {INTERRUPTED} exists in RUN_INDEX with label {LABEL[RETRY_K]} (this gate serves only the A51 resume)',
                     '' if int_rows else 'missing')
    if int_ok:
        n0 = int_rows[0]['notes']
        g.check(len(int_rows) == 1 and n0.startswith('STARTED') and all(x['exit_code'] == '' for x in int_rows),
                f'A51: {INTERRUPTED} has its STARTED row only (no finish row): the registered interrupted launch',
                f'{len(int_rows)} row(s)' + ('' if all(x['exit_code'] == '' for x in int_rows) else ', a finish row exists: decide by hand'))
    by_k = {}
    for rid in s_ids: by_k.setdefault(s_of[rows_s[rid][0]['label']], []).append(rid)
    for k, rids in by_k.items():
        if k == RETRY_K:
            g.check(rids[0] == INTERRUPTED and len(rids) <= 2,
                    f'RUN_INDEX: {LABEL[k]}: {INTERRUPTED} (interrupted) and at most ONE retry run id above it (A51; never a third launch)', str(rids))
        else:
            g.check(len(rids) == 1, f'RUN_INDEX: one run id per label ({LABEL[k]})', str(rids))
    for rid in s_ids:
        k = s_of[rows_s[rid][0]['label']]; first = rows_s[rid][0]; n = first['notes']
        g.check(n.startswith('STARTED') and f'model={C.MODEL_ENV}' in n.split() and first['deck_sha256'] == DECK[k] and first['model_sha256'] == MATERIAL[k],
                f'{rid} ({k}): STARTED-row input columns as pinned (deck_sha256, model_sha256, model note)')
    finished = {rid: any(x['exit_code'] != '' for x in rows_s[rid][1:]) for rid in s_ids}
    inv = {x['run_id']: x for x in json.loads(C.INVENTORY.read_text())['runs']}
    for rid in s_ids:
        k = s_of[rows_s[rid][0]['label']]; x = inv.get(rid) or {}
        g.check(x.get('label') == LABEL[k] and x.get('entry') == k and x.get('deck_sha256') == DECK[k] and x.get('model_sha256') == MATERIAL[k]
                and x.get('model_file') == C.MODEL_ENV, f'{rid} ({k}) listed in config/sealed_runs.json with the pinned values (A41 (e), A49 (d))')
    launched = [s_of[rows_s[rid][0]['label']] for rid in s_ids]
    i_int = ORDER.index(RETRY_K)
    want = ORDER[:i_int] + [RETRY_K] + ORDER[i_int:i_int + max(0, len(launched) - i_int - 1)]
    pos_ok = INTERRUPTED in s_ids and s_ids.index(INTERRUPTED) == i_int
    g.check(launched == want and pos_ok, f'order: STARTED S4a runs == S4A-02-2p0 ... S4A-13-13p2, {INTERRUPTED} ({RETRY_K}, interrupted), then a '
            f'prefix of {RETRY_K} ... S4A-15-13p2 (A50 order with the A51 retry)', ' -> '.join(f'{k} {r}' for k, r in list(zip(launched, s_ids))[-6:]) or 'none')
    unfinished = [f'{rid} ({s_of[rows_s[rid][0]["label"]]})' for rid in s_ids if rid != INTERRUPTED and not finished[rid]]
    done_k = {s_of[rows_s[rid][0]['label']] for rid in s_ids if rid != INTERRUPTED}
    todo = [k for k in ORDER if k not in done_k]
    if unfinished: g.stop(f'started S4a run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; '
                          'decide by hand (A51: run_0150 is the only admitted interrupted record)')
    plan_rel = G.PLAN_OF[todo[0]] if todo else None
    g.check(plan_rel in (None, B3), f'the next plan is {B3} (batches 1 and 2 complete)', str(plan_rel))
    nxt_k = [k for k in todo if G.PLAN_OF[k] == plan_rel] if plan_rel else []
    retry = RETRY_K in todo

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (D-58 (4): not raised)', f'found {ms}')
    g.check(C.C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; D-58 (4): not raised)', f'gate {C.C10_CAP}, runner {rc_cap}')
    g.check(cap > 0 and len(all_ids) + len(nxt_k) <= cap, f'global budget: {len(all_ids)} used + {len(nxt_k)} <= max_launches {cap}')
    g.check(c10 + len(nxt_k) <= 200, f'C10 cap: {c10} used + {len(nxt_k)} <= 200')
    g.check(c10 + len(todo) + NEED_AFTER_S4A <= 200, f'A51 fit (PA-19 v3 section 4 item 4): c10 {c10} + unlaunched S4a {len(todo)} (retry '
            f'{"included" if retry else "done"}) + never-cut need after S4a {NEED_AFTER_S4A} = {c10 + len(todo) + NEED_AFTER_S4A} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/200; S4a entries with a non-interrupted run: '
          f'{len(done_k)}/42; interrupted: {INTERRUPTED} ({RETRY_K}); retry {"pending" if retry else "started: " + str(by_k.get(RETRY_K, [])[1:])}; '
          f'next free id {nxt}', flush=True)

    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True); return 1
    if g.stops:
        print(f'GATE STOP ({len(g.stops)}): a main-session decision is needed; nothing may be invoked.', flush=True); return 3
    if not todo:
        print('NOTHING TO LAUNCH: every S4a entry has a non-interrupted run. Do not invoke the S4a route plans again. (Exit 4 is not a pass.)', flush=True); return 4
    cmd = f'& "{C.VENV_PY}" scripts/run_campaign.py {plan_rel}' + (f' --retry {RETRY_K}' if retry else '')
    print(f'GATE PASSED. Next plan {plan_rel}: {nxt_k[0]} ({LABEL[nxt_k[0]]}) ... {nxt_k[-1]}, first run id {nxt}; the invocation runs these '
          f'{len(nxt_k)} entr{"y" if len(nxt_k) == 1 else "ies"} in order and stops'
          + (f' (--retry {RETRY_K}: the one A51 retry of the interrupted {INTERRUPTED}; never pass it again once its STARTED row exists)' if retry
             else f' (no --retry: the A51 retry of {RETRY_K} has started)')
          + '. Only with the go for THIS launch. '
          + ('Would-be command (check mode, not an instruction)' if check_mode else 'Command (same PowerShell session, package root, IWO_MODEL_FILE as set)')
          + f':\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
