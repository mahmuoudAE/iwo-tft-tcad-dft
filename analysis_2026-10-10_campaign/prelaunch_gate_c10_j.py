"""C10 pre-launch gate J, S6 / S7 (register A59, 2026-10-16; no Codex review, D-63; Claude go under D-59). NO launch, NO file written,
nothing sealed opened. Run it immediately before EVERY invocation of an S6 / S7 route plan (config/campaign_C10_S6_b1..b8.json,
config/campaign_C10_S7.json), in the same PowerShell session and working directory (the package root):

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check]

It loads prelaunch_gate_c10_i.py v2 (sha256 pinned below; A54) and, through it, the H, G2, G, F, D/E and C10 gates (all unchanged, pins checked)
as modules for constants and helpers only (their run() functions are not used).

Exit codes (ONLY 0 is a pass): 0 the next batch is launchable (prints the ONE command); 1 a check failed or an input is unreadable (fail closed);
3 STOP: a started run without a finish row (other than the registered interruptions run_0150 and run_0160); 4 nothing to launch (S6 / S7
complete, or the A59 (f) cutoff: a launch of the next batch could start at or after 2026-10-16T10:00Z); not a pass.

Checks
  interpreter/cwd/env  -I, project venv, package root, IWO_MODEL_FILE V3, IWO_ATLAS_VIEWERS / IWO_ATLAS_JOB unset
  files        the I gate (pinned) and its chain; scripts/ file set and sha256; the C10 gate's OTHER files and the I gate's FILES; the S5 driver
               and the A53 generator unchanged; the A59 generator s6s7_plans.py and its tests (pinned); the sealed A59 record (file sha256, seal,
               committed in git HEAD); every route plan == the generator's plan of the record and committed in git HEAD; the generator's
               own pin check (inputs as pinned); the S5 terminal records (H6p3 score, H2p0 / H13p2 stop records, S5 report: sha256 pinned,
               sealed, committed) and the S4c PASS record
  amendments   A49..A54 as the I gate, and A59 (register heading naming S6, S7, s6s7_plans.py, prelaunch_gate_c10_j.py and PA-19, not draft;
               IN FORCE decision row naming A59, S6, S7 and prelaunch_gate_c10_j.py)
  processes    no Silvaco process, no runner python, every python command line readable
  RUN_INDEX    run_0181 is the last S5 run (label c10_s5_h13p2_2_6p3_6p3); every started run above run_0077 (the C10 gates' scope) and up to run_0181 has a finish row
               except run_0150 and run_0160; every run above run_0181 carries an A59 label, one run id per label, STARTED sequence == a prefix of the registered
               batch order, STARTED-row deck / model sha256 == the record dry build and the model note present; a started A59 run without a
               finish row: STOP (exit 3)
  budget       max_launches 260 and C10 cap 200 unchanged; distinct run ids + k <= 260 and c10 run ids + k <= 200 (k = unlaunched entries of
               the next batch); fit (PA-19 v3 section 4): c10 used + unlaunched A59 entries + the other never-cut need 32 (A41(d) 6, 3-D NC 17,
               l = 0 triple 3, six repairs) <= 200
  cutoff       A59 (f): now + the timeouts of every unlaunched entry of the batch but its last + 120 s per launch < 2026-10-16T10:00Z
"""
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
HERE = PKG / 'analysis_2026-10-10_campaign'
CFG = PKG / 'config'
I_GATE = HERE / 'prelaunch_gate_c10_i.py'
I_GATE_SHA = '2f4d74d869186911fe506a1c39bace33279ac0f748f97c1d360ab7189dae4f16'   # A54 / D-77
GEN = HERE / 's6s7_plans.py'
GEN_SHA = 'f0c6ecd545d525c38cede1843de243b2757b8503c1c1a8d4bfca4bb934f12e83'
TESTS = HERE / 'test_s6s7_plans.py'
TESTS_SHA = 'da6293af6d7f63cd915ae2e52e2259d8777b7b10a183d5cb9ea1d7153a960fc5'
RECORD_REL = 'analysis_2026-10-10_campaign/profile/s6s7_record_A59.json'
RECORD_SHA = '57e4bd3097a4b1faccdf240217c0e67fdccee0ead731f7c236d7bcc92333310d'
RECORD_SEAL = 'a2f6759245f8b13dbb04fa270b9e530f4b909f6813addfaedebbc7ef75a84fd6'
S5_FILES = {'analysis_2026-10-10_campaign/profile/s5_A53/H6p3_score.json': '3f7a61d979404385b9f5086b163756f0370ee5ef39b8674a41f9a27cc3f0ea41',
            'analysis_2026-10-10_campaign/profile/s5_A53/H2p0_stop.json': '3bcd9539cdec876811194cd1b5f04684b99e8fb8c885ae619fa206eb67c71e61',
            'analysis_2026-10-10_campaign/profile/s5_A53/H13p2_stop.json': '8c107e61d0b26fddba31c4ca628f56cce9e55122559546652ed35d978540fbf7',
            'analysis_2026-10-10_campaign/profile/s5_A53/s5_report_A53.json': '2ffabb454ccd236d0bb2bde2effcf165733c254b8156c04c6e9c2a197cc73d80'}
LAST_S5 = 'run_0181'
LAST_S5_LABEL = 'c10_s5_h13p2_2_6p3_6p3'
INTERRUPTED = ('run_0150', 'run_0160')   # A51, A54: STARTED rows only, kept, never opened
A59_HEADING = ['S6', 'S7', 's6s7_plans.py', 'prelaunch_gate_c10_j.py', 'PA-19']
A59_ROW = ['A59', 'S6', 'S7', 'prelaunch_gate_c10_j.py']
OTHER_NEVER_CUT = 6 + 17 + 3 + 6   # A41(d) + 3-D NC + l = 0 triple + six repairs (PA-19 v3; S6 / S7 counted from the record)
CUTOFF = datetime(2026, 10, 16, 10, 0, 0, tzinfo=timezone.utc)
PER_LAUNCH_S = 120


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def i_module(): return _load(I_GATE, 'prelaunch_gate_c10_i_pinned')


def gen_module():
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    return _load(GEN, 's6s7_plans_pinned')


def now(): return datetime.now(timezone.utc)


def chain():
    """(modules, failure text): the pinned I gate and its chain, each loaded only after its sha256 matched"""
    if fsha(I_GATE) != I_GATE_SHA: return None, f'prelaunch_gate_c10_i.py sha256 == {I_GATE_SHA[:8]}...'
    I = i_module()
    if fsha(I.H_GATE) != I.H_GATE_SHA: return None, f'prelaunch_gate_c10_h.py sha256 == {I.H_GATE_SHA[:8]}...'
    H = I.h_module()
    if fsha(H.G2_GATE) != H.G2_GATE_SHA: return None, f'prelaunch_gate_c10_g2.py sha256 == {H.G2_GATE_SHA[:8]}...'
    G2 = H.g2_module()
    if fsha(G2.G_GATE) != G2.G_GATE_SHA: return None, f'prelaunch_gate_c10_g.py sha256 == {G2.G_GATE_SHA[:8]}...'
    G = G2.g_module()
    if fsha(G.F_GATE) != G.F_GATE_SHA: return None, f'prelaunch_gate_c10_f.py sha256 == {G.F_GATE_SHA[:8]}...'
    FG = G.f_module()
    if fsha(FG.DE_GATE) != FG.DE_GATE_SHA: return None, f'prelaunch_gate_c10_de.py sha256 == {FG.DE_GATE_SHA[:8]}...'
    DE = FG.de_module()
    if fsha(DE.C10_GATE) != DE.C10_GATE_SHA: return None, f'prelaunch_gate_c10.py sha256 == {DE.C10_GATE_SHA[:8]}...'
    return (I, H, G2, G, FG, DE, DE.c10_module()), ''


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    mods, why = chain()
    if mods is None:
        print(f'[FAIL] {why}\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    C = mods[-1]; g = C.Gate()
    try:
        return run(*mods, g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def run(I, H, G2, G, FG, DE, C, g, argv):
    check_mode = '--check' in argv
    print('C10 pre-launch gate J, S6 / S7 (register A59; route plans campaign_C10_S6_b1..b8, campaign_C10_S7; no launch, nothing written)'
          + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10_i.py sha256 == {I_GATE_SHA[:8]}... (loaded with the H, G2, G, F, D/E and C10 gates for pins and helpers; run() unused)')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    # ---------------------------------------------------------------- files
    files_ok = True
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)',
                        '' if have == set(C.SCRIPTS) else f'extra {sorted(have - set(C.SCRIPTS))}, missing {sorted(set(C.SCRIPTS) - have)}')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 as pinned (build_iwo_decks.py {C.SCRIPTS["build_iwo_decks.py"][:8]})', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, **I.FILES, **S5_FILES}.items(): files_ok &= g.check((PKG / f).is_file() and fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')
    files_ok &= g.check(fsha(I.DRIVER) == I.DRIVER_SHA, f's5_loo_driver.py sha256 == {I.DRIVER_SHA[:8]}... (A53 driver, unchanged)')
    files_ok &= g.check(fsha(I.GENERATOR) == I.GENERATOR_SHA, f'make_campaign_configs.py sha256 == {I.GENERATOR_SHA[:8]}... (A53 generator, unchanged)')
    files_ok &= g.check(GEN.is_file() and fsha(GEN) == GEN_SHA, f's6s7_plans.py sha256 == {GEN_SHA[:8]}... (A59 generator)')
    files_ok &= g.check(TESTS.is_file() and fsha(TESTS) == TESTS_SHA, f'test_s6s7_plans.py sha256 == {TESTS_SHA[:8]}... (A59 tests)')
    conf = json.loads((PKG / I.CONFIRM_REL).read_text()) if (PKG / I.CONFIRM_REL).is_file() else {}
    files_ok &= g.check(str(conf.get('verdict', '')).startswith('PASS'), 'S4c verdict PASS (sealed wrapper record, A52 (e))', str(conf.get('verdict'))[:60])
    S = I.driver_module() if fsha(I.DRIVER) == I.DRIVER_SHA else None
    for f in S5_FILES:
        d = json.loads((PKG / f).read_text()) if (PKG / f).is_file() else {}; cok, cdet = I.committed_in_git(f)
        files_ok &= g.check(S is not None and S.seal_ok(d) and cok, f'{f}: sealed S5 record committed in git HEAD (S5 terminal, D-84)', cdet)
    rec = None
    if (PKG / RECORD_REL).is_file():
        rec = json.loads((PKG / RECORD_REL).read_text()); cok, cdet = I.committed_in_git(RECORD_REL)
        files_ok &= g.check(fsha(PKG / RECORD_REL) == RECORD_SHA and rec.get('sha256') == RECORD_SEAL and S is not None and S.seal_ok(rec)
                            and rec.get('generator_sha256') == GEN_SHA and cok,
                            f'{RECORD_REL}: sha256 == {RECORD_SHA[:8]}..., seal {RECORD_SEAL[:8]}..., made by the pinned generator, committed in git HEAD', cdet)
    else:
        files_ok &= g.check(False, f'{RECORD_REL} exists')
    P = None
    if files_ok:
        P = gen_module(); pb = P.pin_problems()
        files_ok &= g.check(not pb, 'generator pin check: matrix, S4c record / confirm / plan, templates, model, solver, builder, runner as pinned', '; '.join(pb))
    for words, row, what in ((G.A49_HEADING, G.A49_ROW, 'A49'), (G.A50_HEADING, G.A50_ROW, 'A50'), (G2.A51_HEADING, G2.A51_ROW, 'A51'),
                             (H.A52_HEADING, H.A52_ROW, 'A52'), (I.A53_HEADING, I.A53_ROW, 'A53'), (I.A54_HEADING, I.A54_ROW, 'A54'),
                             (A59_HEADING, A59_ROW, 'A59')):
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
    if not files_ok or rec is None or P is None:
        print(f'GATE FAILED ({len(g.fails) or 1}): nothing may be invoked (file / pin checks failed)', flush=True); return 1

    # route plans == the generator's plans of the record
    want = P.plans(rec); order = [i for _, ids in rec['batches'] for i in ids]
    g.check([[s, ids] for s, ids in P.BATCHES] == rec['batches'], 'record batches == the generator batch order')
    for stem, p in want.items():
        rel = f'config/{stem}.json'; have_p = json.loads((PKG / rel).read_text()) if (PKG / rel).is_file() else None
        cok, cdet = I.committed_in_git(rel) if have_p is not None else (False, 'missing')
        g.check(have_p == p and cok, f'{rel}: == the generator plan of the record (runnable, no gates, not state-only), committed in git HEAD', cdet)
    sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
    import run_campaign as rc
    bad_d = [i for i in order if C.tsha(rc.current_deck_text(rec['entries'][i], rec['entries'][i]['overrides'])) != rec['dry_build'][i]['deck_sha256']]
    bad_m = [i for i in order if C.tsha(rc.current_material_text(rec['entries'][i]['overrides'])) != rec['dry_build'][i]['model_sha256']]
    g.check(not bad_d, 'dry-built deck text sha256 == the record dry build (all A59 entries)', f'differ: {bad_d}' if bad_d else '')
    g.check(not bad_m, 'dry-built material text sha256 == the record dry build (all A59 entries)', f'differ: {bad_m}' if bad_m else '')

    # ---------------------------------------------------------------- RUN_INDEX (state columns only)
    lab_of_id = {rec['entries'][i]['label']: i for i in order}
    rows, pairs = {}, []
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            keep = {k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'exit_code')}; keep['started'] = str(r.get('notes', '')).startswith('STARTED')
            keep['model_note'] = f'model={C.MODEL_ENV}' in str(r.get('notes', '')).split() if keep['started'] else None
            rows.setdefault(r['run_id'], []).append(keep)
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}' if all_ids else 'run_0001'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    g.check(LAST_S5 in rows and rows[LAST_S5][0]['label'] == LAST_S5_LABEL, f'RUN_INDEX: {LAST_S5} is the last S5 run ({LAST_S5_LABEL})')
    fin = {rid: any(x['exit_code'] != '' and not x['started'] for x in v) for rid, v in rows.items()}
    open_old = [rid for rid in all_ids if C.rid_n(C.LAST_PRE) < C.rid_n(rid) <= C.rid_n(LAST_S5) and any(x['started'] for x in rows[rid]) and not fin[rid]
                and rid not in INTERRUPTED]
    g.check(not open_old, f'every started run {C.LAST_PRE}..{LAST_S5} (exclusive..inclusive) has a finish row (registered interruptions '
            f'{", ".join(INTERRUPTED)} excepted)', str(open_old))
    for rid in INTERRUPTED:
        g.check(rid in rows and not fin[rid], f'{rid}: the registered interrupted launch, STARTED row only (A51 / A54)')
    after = [rid for rid in all_ids if C.rid_n(rid) > C.rid_n(LAST_S5)]
    other = [f'{rid} {rows[rid][0]["label"]}' for rid in after if rows[rid][0]['label'] not in lab_of_id]
    g.check(not other, f'RUN_INDEX: every run above {LAST_S5} carries an A59 label', ', '.join(other))
    st, seq = {}, []
    for rid in after:
        i = lab_of_id.get(rows[rid][0]['label'])
        if i is None: continue
        g.check(i not in st, f'RUN_INDEX: one run id per A59 label ({rows[rid][0]["label"]})', f'{st.get(i)} and {rid}' if i in st else '')
        if i not in st: st[i] = rid; seq.append(i)
        f0 = rows[rid][0]; pin = rec['dry_build'][i]
        g.check(f0['started'] and f0['model_note'] and f0['deck_sha256'] == pin['deck_sha256'] and f0['model_sha256'] == pin['model_sha256'],
                f'{rid} ({i}): STARTED-row inputs == the A59 record dry build (deck, material, model note)')
    g.check(seq == order[:len(seq)], 'order: STARTED A59 runs == a prefix of the registered batch order', ' -> '.join(f'{i} {st[i]}' for i in seq) or 'none')
    unfinished = [f'{st[i]} ({i})' for i in seq if not fin[st[i]]]
    if unfinished: g.stop(f'started S6 / S7 run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')

    # ---------------------------------------------------------------- the next batch
    todo = [i for i in order if i not in st]; nb = next(((s, ids) for s, ids in rec['batches'] if any(i in todo for i in ids)), None)
    msg4, k_next, plan_rel = None, [], None
    if nb is None: msg4 = 'S6 / S7: every A59 entry has started and finished; next: the A59 read-out (0 launches)'
    else:
        stem, ids = nb; plan_rel = f'config/{stem}.json'; k_next = [rec['entries'][i] for i in ids if i in todo]
        earlier = [i for s, ids_ in rec['batches'][:[s for s, _ in rec['batches']].index(stem)] for i in ids_]
        g.check(all(i in st for i in earlier), f'{stem}: every earlier batch has started (register order)')
        t_now = now(); latest = t_now + timedelta(seconds=sum(int(e['timeout']) for e in k_next[:-1]) + PER_LAUNCH_S * len(k_next))
        print(f'[INFO] cutoff (A59 (f)): now {t_now:%Y-%m-%dT%H:%M:%SZ}; latest possible start of the last launch of {stem} {latest:%H:%M:%SZ} '
              f'(timeouts of the unlaunched entries but the last + {PER_LAUNCH_S} s each); cutoff {CUTOFF:%Y-%m-%dT%H:%M:%SZ}', flush=True)
        if latest >= CUTOFF: msg4 = f'A59 (f) cutoff: a launch of {stem} could start at or after {CUTOFF:%Y-%m-%dT%H:%M}Z; record where S6 / S7 stopped and commit'

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (not raised)', f'found {ms}')
    rc_cap = getattr(rc, 'C10_CAP', None)
    g.check(C.C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; not raised)', f'gate {C.C10_CAP}, runner {rc_cap}')
    n = len(k_next) if msg4 is None else 0
    g.check(cap > 0 and len(all_ids) + n <= cap, f'global budget: {len(all_ids)} used + {n} <= max_launches {cap}')
    g.check(c10 + n <= 200, f'C10 cap: {c10} used + {n} <= 200')
    g.check(c10 + len(todo) + OTHER_NEVER_CUT <= 200, f'A59 fit: c10 {c10} + unlaunched S6 / S7 {len(todo)} + other never-cut need {OTHER_NEVER_CUT} '
            f'= {c10 + len(todo) + OTHER_NEVER_CUT} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1] if all_ids else "none"}), c10 {c10}/200; A59 started {len(seq)}/{len(order)}; '
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
