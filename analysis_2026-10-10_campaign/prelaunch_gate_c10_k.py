"""C10 pre-launch gate K, F13-F15 and P1 (register A60, 2026-10-16; no Codex review, D-63; Claude go under D-59). NO launch, NO file
written, nothing sealed opened. Run it immediately before EVERY invocation of config/campaign_C10_F13_F15.json and
config/campaign_C10_P1_2p0 / _6p3 / _13p2.json, in the same PowerShell session and working directory (the package root):

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check]

It loads prelaunch_gate_c10_j.py (sha256 pinned; A59) and, through it, gate I v2 and its chain for constants and helpers only.

Exit codes (ONLY 0 is a pass): 0 the next plan is launchable (prints the ONE command); 1 a check failed (fail closed); 3 STOP: a started run
without a finish row (other than run_0150 / run_0160); 4 nothing to launch (S6 / S7 not complete yet, F13-F15 and P1 complete, or the cutoff:
a launch of the next plan could start at or after 2026-10-16T10:00Z, or the plan could end after 2026-10-16T11:30Z; v2 (A62, 2026-10-17): no end-by
window while the user is online, registered timeouts govern; F13-F15 run one entry per invocation through config/campaign_C10_F13_F15__<id>.json); not a pass.

Checks: as gate J for interpreter, files (gate J and its pinned A59 package unchanged, scripts/, the I gate's files, the S5 terminal records),
amendments (A49..A54, A59) and processes; plus the pinned generator fp_plans.py, the frozen P1 floor procedure p1_floor.py and its tests, the
sealed record fp_record_A60.json (sha256, seal, generator, committed), every plan == the generator plan of the record and committed, the
dry builds (output decks exactly as run_atlas.execute_output builds them), A60 logged, and for a P1 plan: REG-001 present in the private
repo predictions/registered/ naming p1_floor.py and the record seal, and the model tag model-c10-s4c-frozen-20261016 on a commit holding the record.
RUN_INDEX: every A59 entry started and finished before any K entry; above the last A59 run only K labels, one run id each, STARTED order a
prefix of F13-F15 (S3-26, S3-24, S3-25) then P1 (2.0, 6.3, 13.2), STARTED-row deck / model sha256 == the record dry build (model note for
the transfer entries). Budget: caps unchanged; fit c10 + unlaunched K entries + other never-cut need 32 <= 200.
"""
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
PRIVATE = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private")
HERE = PKG / 'analysis_2026-10-10_campaign'
J_GATE = HERE / 'prelaunch_gate_c10_j.py'
J_GATE_SHA = '6d0b1ad6406fdadeac8637eea83e7415d4bbc35f559e9c4a6b6ba78b952f1e76'   # gate J v3 (A62; v1 5815b740 A59, v2 97e4e76e A61)
J_TESTS_SHA = 'a217b0acfe5bf770b2aaa73bf844ddc321e5108ddf987de535264c1fee70cb22'   # gate J v3 tests (v1 c4a0a1de)
AMEND = 'A60'
GEN = HERE / 'fp_plans.py'
GEN_SHA = 'deadd2cdbe7863ff3d9b2b46aee65040c7991ca3c6ce0966d9cefdc7c613343b'
P1F = {'analysis_2026-10-10_campaign/p1_floor.py': '6b8ba029258e275f49eb96103fa37cefc6c99276b773fd5ed1c451ec7503aa7a',
       'analysis_2026-10-10_campaign/test_p1_floor.py': '2c873bb43b003b08328e4be1e614af0731f3fb60a712c2c2821c8096ec029288'}
RECORD_REL = f'analysis_2026-10-10_campaign/profile/fp_record_{AMEND}.json'
RECORD_SHA = '0774404eaab2bc17bfb8e6027465e5226dcb681e1fe892dd51af8678fd9f14a5'
RECORD_SEAL = '0fb02610c07916448f43c93267ce4446b3915a2059ad3defd4ede12f0ad44d9f'
REG = PRIVATE / 'predictions' / 'registered' / 'REG-001.md'
TAG = 'model-c10-s4c-frozen-20261016'
K_HEADING = ['F13-F15', 'P1', 'PA-15', 'fp_plans.py', 'prelaunch_gate_c10_k.py']
K_ROW = [AMEND, 'F13-F15', 'P1', 'prelaunch_gate_c10_k.py']
CUTOFF = datetime(2026, 10, 16, 10, 0, 0, tzinfo=timezone.utc)
LID = datetime(2026, 10, 16, 11, 30, 0, tzinfo=timezone.utc)   # v1 only; v2 (A62): no end-by window
SINGLE_BATCHES_K = ('campaign_C10_F13_F15',)   # A62: F13-F15 one entry per invocation ('<batch>__<id>' derived plans)
PER_LAUNCH_S = 120


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def now(): return datetime.now(timezone.utc)


def git_ok(repo, args):
    try: return subprocess.run(['git', '-C', str(repo)] + args, capture_output=True, timeout=60).returncode == 0
    except Exception: return False


def reg_ok(seal):
    """REG-001 in predictions/registered/, committed in the private repo HEAD, naming p1_floor.py's sha256 and the record seal"""
    if not REG.is_file(): return False, 'missing'
    t = REG.read_text(encoding='utf-8', errors='replace'); rel = REG.relative_to(PRIVATE).as_posix()
    ok = P1F['analysis_2026-10-10_campaign/p1_floor.py'] in t and seal in t and git_ok(PRIVATE, ['cat-file', '-e', f'HEAD:{rel}'])
    return ok, 'names p1_floor.py, the record seal, committed' if ok else 'does not name the pins or not committed'


def tag_ok():
    ok = git_ok(PKG, ['rev-parse', '-q', '--verify', f'refs/tags/{TAG}']) and git_ok(PKG, ['cat-file', '-e', f'{TAG}:{RECORD_REL}'])
    return ok, f'tag {TAG} exists and its commit holds {RECORD_REL}' if ok else f'tag {TAG} missing or without the record'


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if fsha(J_GATE) != J_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_j.py sha256 == {J_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    J = _load(J_GATE, 'prelaunch_gate_c10_j_pinned'); mods, why = J.chain()
    if mods is None:
        print(f'[FAIL] {why}\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    C = mods[-1]; g = C.Gate()
    try:
        return run(J, *mods, g, argv)
    except Exception as ex:
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def run(J, I, H, G2, G, FG, DE, C, g, argv):
    check_mode = '--check' in argv
    print(f'C10 pre-launch gate K, F13-F15 and P1 (register {AMEND}; plans campaign_C10_F13_F15, campaign_C10_P1_*; no launch, nothing written)'
          + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10_j.py sha256 == {J_GATE_SHA[:8]}... (loaded with gate I v2 and its chain for pins and helpers; run() unused)')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    files_ok = True
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, 'scripts/ sha256 as pinned', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, **I.FILES, **J.S5_FILES, **P1F}.items(): files_ok &= g.check((PKG / f).is_file() and fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')
    files_ok &= g.check(fsha(J.TESTS) == J.TESTS_SHA and fsha(J.GEN) == J.GEN_SHA and fsha(HERE / 'test_prelaunch_gate_c10_j.py') == J_TESTS_SHA,
                        'A59 package unchanged (s6s7_plans.py, its tests, gate J tests)')
    jrec = json.loads((PKG / J.RECORD_REL).read_text()) if (PKG / J.RECORD_REL).is_file() else {}
    files_ok &= g.check(fsha(PKG / J.RECORD_REL) == J.RECORD_SHA and jrec.get('sha256') == J.RECORD_SEAL, f'{J.RECORD_REL} unchanged (A59 record)')
    files_ok &= g.check(GEN.is_file() and fsha(GEN) == GEN_SHA, f'fp_plans.py sha256 == {GEN_SHA[:8]}... ({AMEND} generator)')
    rec = json.loads((PKG / RECORD_REL).read_text()) if (PKG / RECORD_REL).is_file() else None
    S = I.driver_module() if fsha(I.DRIVER) == I.DRIVER_SHA else None
    cok, cdet = I.committed_in_git(RECORD_REL) if rec else (False, 'missing')
    files_ok &= g.check(rec is not None and fsha(PKG / RECORD_REL) == RECORD_SHA and rec.get('sha256') == RECORD_SEAL and S is not None and S.seal_ok(rec)
                        and rec.get('generator_sha256') == GEN_SHA and cok, f'{RECORD_REL}: sha256 {RECORD_SHA[:8]}..., seal {RECORD_SEAL[:8]}..., pinned generator, committed', cdet)
    P = None
    if files_ok:
        sys.path.insert(0, str(HERE)); P = _load(GEN, 'fp_plans_pinned'); pb = P.pin_problems()
        files_ok &= g.check(not pb, 'generator pin check (matrix, S4c record / confirm / plan, p1_floor, model, solver, builder, runner)', '; '.join(pb))
    for words, row, what in ((G.A49_HEADING, G.A49_ROW, 'A49'), (G.A50_HEADING, G.A50_ROW, 'A50'), (G2.A51_HEADING, G2.A51_ROW, 'A51'),
                             (H.A52_HEADING, H.A52_ROW, 'A52'), (I.A53_HEADING, I.A53_ROW, 'A53'), (I.A54_HEADING, I.A54_ROW, 'A54'),
                             (J.A59_HEADING, J.A59_ROW, 'A59'), (K_HEADING, K_ROW, AMEND), (J.A61_HEADING, J.A61_ROW, 'A61'), (J.A62_HEADING, J.A62_ROW, 'A62')):
        h, d = C.amendment_logged(words, row)
        g.check(h, f'{what} logged: register heading naming {", ".join(words)} (not draft)'); g.check(d, f'{what} logged: decision row naming {", ".join(row)}, IN FORCE')
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
    if not files_ok or rec is None or P is None:
        print(f'GATE FAILED ({len(g.fails) or 1}): nothing may be invoked (file / pin checks failed)', flush=True); return 1

    want = P.plans(rec); order = [i for _, ids in rec['batches'] for i in ids]
    for b in SINGLE_BATCHES_K:
        for e in list(want[b]['runs']): want[f"{b}__{e['id']}"] = J.single(want[b], e['id'])   # A62 derived single-entry plans
    g.check([[s, ids] for s, ids in P.BATCHES] == rec['batches'], 'record batches == the generator batch order')
    for stem, p in want.items():
        rel = f'config/{stem}.json'; have_p = json.loads((PKG / rel).read_text()) if (PKG / rel).is_file() else None
        cok, cdet = I.committed_in_git(rel) if have_p is not None else (False, 'missing')
        g.check(have_p == p and cok, f'{rel}: == the generator plan of the record (runnable, no gates, not state-only), committed in git HEAD', cdet)
    dry = P.dry(rec['entries'])
    g.check(dry == rec['dry_build'], f'dry-built deck / material text sha256 == the record dry build ({len(dry)} entries; output decks as execute_output)')
    sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
    import run_campaign as rc

    # ---------------------------------------------------------------- RUN_INDEX (state columns only)
    jorder = [i for _, ids in jrec['batches'] for i in ids]; jlab = {jrec['entries'][i]['label']: i for i in jorder}
    klab = {rec['entries'][i]['label']: i for i in order}
    rows, pairs = {}, []
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            keep = {k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'exit_code')}; keep['started'] = str(r.get('notes', '')).startswith('STARTED')
            keep['model_note'] = f'model={C.MODEL_ENV}' in str(r.get('notes', '')).split() if keep['started'] else None
            rows.setdefault(r['run_id'], []).append(keep)
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    fin = {rid: any(x['exit_code'] != '' and not x['started'] for x in v) for rid, v in rows.items()}
    after = [rid for rid in all_ids if C.rid_n(rid) > C.rid_n(J.LAST_S5)]
    jst = {jlab[rows[rid][0]['label']]: rid for rid in after if rows[rid][0]['label'] in jlab}
    jdone = all(i in jst and fin[jst[i]] for i in jorder)
    other = [f'{rid} {rows[rid][0]["label"]}' for rid in after if rows[rid][0]['label'] not in jlab and rows[rid][0]['label'] not in klab]
    g.check(not other, f'RUN_INDEX: every run above {J.LAST_S5} carries an A59 or {AMEND} label', ', '.join(other))
    for rid in J.INTERRUPTED: g.check(rid in rows and not fin[rid], f'{rid}: the registered interrupted launch, STARTED row only')
    open_old = [rid for rid in all_ids if C.rid_n(C.LAST_PRE) < C.rid_n(rid) and any(x['started'] for x in rows[rid]) and not fin[rid] and rid not in J.INTERRUPTED]
    st, seq = {}, []
    last_j = max([C.rid_n(r) for r in jst.values()] or [C.rid_n(J.LAST_S5)])
    for rid in after:
        i = klab.get(rows[rid][0]['label'])
        if i is None: continue
        g.check(C.rid_n(rid) > last_j and jdone, f'{rid} ({i}): above every A59 run, with S6 / S7 complete before it (register order)')
        g.check(i not in st, f'RUN_INDEX: one run id per {AMEND} label ({rows[rid][0]["label"]})', f'{st.get(i)} and {rid}' if i in st else '')
        if i not in st: st[i] = rid; seq.append(i)
        f0 = rows[rid][0]; pin = rec['dry_build'][i]; tr = rec['entries'][i].get('mode') != 'output'
        g.check(f0['started'] and (f0['model_note'] or not tr) and f0['deck_sha256'] == pin['deck_sha256'] and f0['model_sha256'] == pin['model_sha256'],
                f'{rid} ({i}): STARTED-row inputs == the {AMEND} record dry build')
    g.check(seq == order[:len(seq)], f'order: STARTED {AMEND} runs == a prefix of S3-26, S3-24, S3-25, P1-2p0, P1-6p3, P1-13p2', ' -> '.join(f'{i} {st[i]}' for i in seq) or 'none')
    if open_old: g.stop(f'started run(s) without a finish row: {open_old} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')

    todo = [i for i in order if i not in st]; nb = next(((s, ids) for s, ids in rec['batches'] if any(i in todo for i in ids)), None)
    msg4, k_next, plan_rel = None, [], None
    if not jdone: msg4 = 'S6 / S7 (A59) not complete: F13-F15 and P1 follow S7 (register order)'
    elif nb is None: msg4 = f'F13-F15 and P1: every {AMEND} entry has started and finished; next: p1_floor.py predict and the A55 bands (0 launches)'
    else:
        stem, ids = nb; k_next = [rec['entries'][i] for i in ids if i in todo]
        if stem in SINGLE_BATCHES_K: k_next = k_next[:1]; stem = f"{stem}__{k_next[0]['id']}"   # A62: one entry per invocation
        plan_rel = f'config/{stem}.json'
        if stem.startswith('campaign_C10_P1'):
            rok, rdet = reg_ok(rec['sha256']); tok, tdet = tag_ok()
            g.check(rok, f'REG-001 in predictions/registered/ ({rdet})'); g.check(tok, tdet)
        t_now = now(); to = sum(int(e['timeout']) for e in k_next)
        print(f'[INFO] timing (A62): no end-by window while the user is online; registered timeouts govern (now {t_now:%Y-%m-%dT%H:%M:%SZ}, '
              f'{stem} bounded by {to} s); stop at a clean boundary on any user shutdown message', flush=True)

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (not raised)', f'found {ms}')
    g.check(C.C10_CAP == 200 and getattr(rc, 'C10_CAP', None) == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; not raised)')
    n = len(k_next) if msg4 is None else 0
    g.check(len(all_ids) + n <= cap, f'global budget: {len(all_ids)} used + {n} <= max_launches {cap}')
    g.check(c10 + n <= 200, f'C10 cap: {c10} used + {n} <= 200')
    jtodo = len([i for i in jorder if i not in jst])
    g.check(c10 + jtodo + len(todo) + J.OTHER_NEVER_CUT <= 200, f'fit: c10 {c10} + unlaunched A59 {jtodo} + unlaunched {AMEND} {len(todo)} + other never-cut need '
            f'{J.OTHER_NEVER_CUT} = {c10 + jtodo + len(todo) + J.OTHER_NEVER_CUT} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/200; A59 complete {jdone}; {AMEND} started {len(seq)}/{len(order)}; '
          f'next free id {nxt}', flush=True)
    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True); return 1
    if g.stops:
        print(f'GATE STOP ({len(g.stops)}): a main-session decision is needed; nothing may be invoked.', flush=True); return 3
    if msg4:
        print(f'NOTHING TO LAUNCH: {msg4}. (Exit 4 is not a pass.)', flush=True); return 4
    cmd = f'& "{C.VENV_PY}" scripts/run_campaign.py {plan_rel}'
    print(f'GATE PASSED. Next plan {plan_rel}: {k_next[0]["id"]} ({k_next[0]["label"]}) ... {k_next[-1]["id"]}, first run id {nxt}; the invocation runs these '
          f'{n} entr{"y" if n == 1 else "ies"} in order and stops. Only with the user\'s own go for THIS launch in the conversation (the hook also asks). '
          + ('Would-be command (check mode, not an instruction)' if check_mode else 'Command (same PowerShell session, package root, IWO_MODEL_FILE as set)')
          + f':\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
