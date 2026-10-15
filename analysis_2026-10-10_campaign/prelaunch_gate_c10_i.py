"""C10 pre-launch gate for stage H of the plan = S5 leave-one-film-out (register A53, 2026-10-16; no Codex review, D-63; Claude under D-59 for the
registration; every launch only with the user's own go for THAT launch in the conversation, and the hook). NO launch, NO file written, nothing
sealed opened. Run it immediately before EVERY invocation of an S5 route plan config/campaign_C10_S5_<fold>_<t1..t4|pred>.json, in the same
PowerShell session and working directory (the package root) as the invocation:

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check] [--s4d]

It loads prelaunch_gate_c10_h.py (sha256 pinned; 3e96b825, A52) and, through it, the G2, G, F, D/E and C10 gates (all unchanged, their pins checked)
as modules for constants and helpers only (Gate, process functions, amendment_logged, scripts/ pins, labels, S4a / S4c / S4d pins); the H gate's own
run() is NOT used (its generator pin and its RUN_INDEX label set predate A53). It loads the S5 driver s5_loo_driver.py (pinned) for its pin check,
its constants and seal check, and the plan generator make_campaign_configs.py (pinned) for the S5 plan form.

--s4d: offer config/campaign_C10_S4d.json instead (A52 (g); held for the user's own go): the H-gate S4d checks (record, plan pin, dry builds,
STARTED order) with this gate's RUN_INDEX accounting. Default: the next S5 invocation.

Exit codes (ONLY 0 is a pass): 0 the next plan is launchable (prints the ONE command); 1 a check failed or an input is unreadable (fail closed);
3 STOP: a started S4d/S5 run has no finish row; 4 nothing to launch (S5 complete, or the next step is a 0-launch driver step: the gate names it);
not a pass.

Checks
  interpreter/cwd/env  -I, project venv, package root, IWO_MODEL_FILE V3, IWO_ATLAS_VIEWERS / IWO_ATLAS_JOB unset
  files        the H, G2, G, F, D/E and C10 gate files (pinned); scripts/ file set and sha256 (public-repo 1375164 + builder 734125a8); the C10 gate's
               OTHER files; the frozen files (profile_s4s5 429b3a3f, profile_shared 958c3605, hf_score_draft 96a2147e, score_register via OTHER);
               campaign_matrix.json f06e8d77; the A49 driver and record; the PA-18 wrapper, its tests and records (S4c variable reference and the S4c
               PASS verdict, logged before the first S5 launch, A52 (e)); the A51 archive; the plan generator (A53 pin); the S5 driver and its
               tests (A53 pins); the S4c / S4d plans (A52 pins)
  driver       its own pin check (frozen code, helpers, model file, solver.yaml, runner/builder, sources) passes
  amendments   A49, A50, A51, A52 and A53 register headings (not draft) and IN FORCE decision-log rows (A53: D-76)
  processes    no Silvaco process, no runner python, every python command line readable
  RUN_INDEX    run_id/label of every row (STARTED-row input columns and finish-row presence only): every run above run_0077 is S1-06R/DIAG, D/E,
               stage F, S4a, S4c, S4d or S5; S4a complete (run_0150 the only unfinished S4a run); S4c complete (three finished runs, STARTED rows as
               pinned); S4d: STARTED runs a prefix of S4D-2p0..13p2 with pinned STARTED rows; S5: one run id per label, every S5 run id above
               run_0159, STARTED order == a prefix of the registered sequence (fold H6p3, H2p0, H13p2; t1..t4, pred; a fold with a committed stop
               record keeps only the entries started before its stop), STARTED-row deck/material == the invocation record's dry build; a finish
               row for every started S4d/S5 run (else STOP, exit 3)
  next S5      its sealed driver record exists (seal, made by the pinned driver and the frozen profile_s4s5 429b3a3f, committed in git HEAD byte
               for byte); the fold decision is committed and is the record's decision; training step k: the record's fold candidates == the runs of
               steps 1..k-1 as in RUN_INDEX; pred: both frozen records committed in git HEAD, seals valid and == the record's binding; the plan
               file == the generator's i_plan of the record (runnable, no gates, not state-only, matrix ids / labels / timeouts); the dry-built
               deck / material text sha256 == the record's dry build
  budget       config/solver.yaml exactly one max_launches == 260; C10 cap 200 (gate constant and run_campaign.C10_CAP); distinct run ids + k <= 260
               and c10 run ids + k <= 200 (k = launches of the next invocation); A53 fit: c10 used + unlaunched S5 entries (stopped folds excluded)
               + unlaunched S4d + the never-cut need after S5 46 (A41(d) 6 + 3-D NC 17 + l = 0 triple 3 + S6 core 12 + S7 2 + repairs 6) <= 200
"""
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
HERE = PKG / 'analysis_2026-10-10_campaign'
CFG = PKG / 'config'
H_GATE = HERE / 'prelaunch_gate_c10_h.py'
H_GATE_SHA = '3e96b825ac0aeec7e34593e63a07bffc1b3879c06f9c7405e5bb08f7f39f59c2'   # A52 / D-75
DRIVER = HERE / 's5_loo_driver.py'
DRIVER_SHA = '1e7c42d976408cd1bd09474277dadab0dd1f175cfb14f37888d33bdc3c4132fc'     # A53 driver
GENERATOR = HERE / 'make_campaign_configs.py'
GENERATOR_SHA = '3cccb2a02c1719925541ba8b245760010ed66e33fa2db6105d9800183a2c34ed'  # A53 generator (S5 route plans)
FILES = {'analysis_2026-10-10_campaign/hf_score_draft.py': '96a2147eae6a07a2ea0afbed2d63476283c2d5bca3ffdfd7f829f248af3a1c81',      # H-F v4 (frozen)
         'analysis_2026-10-10_campaign/profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',        # S4b/S5 v4 (frozen)
         'analysis_2026-10-10_campaign/profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
         'analysis_2026-10-10_campaign/campaign_matrix.json': 'f06e8d7721f75aec3f78da06de1c1686c59307c33725bd8822c3ec3e0f0a443c',     # unchanged
         'analysis_2026-10-10_campaign/s3_decision_a49.py': '72fb4295ac7d624e2a2d0c63394da651bf845b0b28cab2362108bcd6a3308a42',
         'analysis_2026-10-10_campaign/profile/s3_adoption_A49.json': '9ad43a88451082422e7b4faeaa710122aff28f44a94cff5562eeeb33f05b4993',
         'analysis_2026-10-10_campaign/s4c_confirm_wrapper.py': '17d86c67d4d71e8d5b661aa44424d9cc4b98f2917b7c6f24450595b503e9e7c4',
         'analysis_2026-10-10_campaign/test_s4c_confirm_wrapper.py': '3dafc48a70a234e9fc12deda4fb607ec6bf3e7f96be52307dedd3b8a14688a23',
         'analysis_2026-10-10_campaign/profile/s4a_archive_A51.json': '44de96df4bc0b2731e01b8b49c6fe2b06f4bf2295f2ff40141c7a283420df0f0',
         'analysis_2026-10-10_campaign/profile/s4s5_surrogate_s4a_archive_A51.json': 'ef10e8d4771e4c153bf230ff6b56cae52b5959dfcd71f4a5eeae36b6ebf3df42',
         'analysis_2026-10-10_campaign/profile/s4c_record_A52.json': '821867bcd6751da22dfc1be3501f119338ed50ed85119b745c8709370284255a',
         'analysis_2026-10-10_campaign/profile/s4c_confirm_A52.json': '91d0f3cb18307d313b994220de57a4bd46d07410c29912807f1354aa09140b3f',   # S4c PASS (A52 (e))
         'analysis_2026-10-10_campaign/test_s5_loo_driver.py': '42a4dbc55d7d2add4b136847ed751fe2ab6a571f6e214a34967a6d56b847125b',          # A53 driver tests
         'config/campaign_C10_S4c.json': '0809527954bc97be56667c8a151837ae4f61c474a9307599962f55eb049dc0e4',
         'config/campaign_C10_S4d.json': '61b0df8342100c4626f709bbc8dc2f98fe7deedd48bcf7645b216d2825a0ac6a'}
CONFIRM_REL = 'analysis_2026-10-10_campaign/profile/s4c_confirm_A52.json'
A53_HEADING = ['S5', 'leave-one-film-out', 's5_loo_driver.py', 'prelaunch_gate_c10_i.py']
A53_ROW = ['A53', 'S5', 's5_loo_driver.py', 'prelaunch_gate_c10_i.py']
LAST_S4C = 'run_0159'      # last S4c run; every S5 run id is above it
NEED_AFTER_S5 = 6 + 17 + 3 + 12 + 2 + 6   # A41(d) + 3-D NC + l = 0 triple + S6 core + S7 + repairs = 46 (S4b 18 returned, PA-19 v3 4 item 5)
S5_TOTAL = 30


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsha(s): return hashlib.sha256(s.encode()).hexdigest()


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def h_module(): return _load(H_GATE, 'prelaunch_gate_c10_h_pinned')


def driver_module(): return _load(DRIVER, 's5_loo_driver_pinned')


def generator_module():
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    return _load(GENERATOR, 'make_campaign_configs_pinned')


def committed_in_git(relp):
    """(ok, detail): the working-tree file equals its git HEAD blob (LF-normalised: core.autocrlf=input)"""
    try: out = subprocess.run(['git', '-C', str(PKG), 'cat-file', '-p', f'HEAD:{relp}'], capture_output=True, timeout=60)
    except Exception as ex: return False, f'git not runnable ({type(ex).__name__})'
    if out.returncode != 0: return False, 'not in HEAD'
    norm = lambda b: hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()
    same = norm(out.stdout) == norm((PKG / relp).read_bytes())
    return same, f'HEAD blob LF-normalised content {"equal" if same else "DIFFERENT"}'


def s5_labels(mx_runs):
    """S5 matrix id -> label"""
    return {r['id']: r['campaign_entry']['label'] for r in mx_runs if r['stage'] == 'S5_leave_one_film_out'}


def expected_sequence(S, stopped_started):
    """the registered S5 launch sequence [(held, step, id)]: fold order, steps t1..t4, pred, entries in film order; for a stopped fold only the
    entries that had started before its stop (stopped_started: held -> set of ids)"""
    out = []
    for h, st in S.invocation_order():
        for i in S.entry_ids(h, st):
            if h in stopped_started and i not in stopped_started[h]: continue
            out.append((h, st, i))
    return out


def next_invocation(S, started_ids, stopped):
    """(held, step, remaining ids) of the first invocation (registered order) with an unstarted entry; stopped folds skipped; None = S5 done"""
    for h, st in S.invocation_order():
        if h in stopped: continue
        rem = [i for i in S.entry_ids(h, st) if i not in started_ids]
        if rem: return h, st, rem
    return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if fsha(H_GATE) != H_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_h.py sha256 == {H_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    H = h_module()
    if fsha(H.G2_GATE) != H.G2_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_g2.py sha256 == {H.G2_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    G2 = H.g2_module()
    if fsha(G2.G_GATE) != G2.G_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_g.py sha256 == {G2.G_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    G = G2.g_module()
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
        return run(H, G2, G, FG, DE, C, g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def run(H, G2, G, FG, DE, C, g, argv):
    check_mode = '--check' in argv; s4d_mode = '--s4d' in argv
    print('C10 pre-launch gate, S5 leave-one-film-out (register A53; route plans campaign_C10_S5_*; no launch, nothing written)'
          + (' [S4D MODE: campaign_C10_S4d]' if s4d_mode else '') + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10_h.py sha256 == {H_GATE_SHA[:8]}... (loaded with the G2, G, F, D/E and C10 gates for pins and helpers; its run() unused)')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    files_ok = g.check(fsha(H.G2_GATE) == H.G2_GATE_SHA and fsha(G2.G_GATE) == G2.G_GATE_SHA and fsha(G.F_GATE) == G.F_GATE_SHA
                       and fsha(FG.DE_GATE) == FG.DE_GATE_SHA and fsha(DE.C10_GATE) == DE.C10_GATE_SHA,
                       f'gate chain as pinned: _g2.py {H.G2_GATE_SHA[:8]}..., _g.py {G2.G_GATE_SHA[:8]}..., _f.py {G.F_GATE_SHA[:8]}..., _de.py {FG.DE_GATE_SHA[:8]}..., '
                       f'prelaunch_gate_c10.py {DE.C10_GATE_SHA[:8]}...')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)',
                        '' if have == set(C.SCRIPTS) else f'extra {sorted(have - set(C.SCRIPTS))}, missing {sorted(set(C.SCRIPTS) - have)}')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 as pinned (build_iwo_decks.py {C.SCRIPTS["build_iwo_decks.py"][:8]})', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, **FILES}.items(): files_ok &= g.check((PKG / f).is_file() and fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')
    files_ok &= g.check(fsha(DRIVER) == DRIVER_SHA, f's5_loo_driver.py sha256 == {DRIVER_SHA[:8]}... (A53 driver)')
    files_ok &= g.check(fsha(GENERATOR) == GENERATOR_SHA, f'make_campaign_configs.py sha256 == {GENERATOR_SHA[:8]}... (A53 generator)')
    dok, ddet = G.decision_ok(PKG / G.DECISION)
    files_ok &= g.check(dok, 'A49 decision record: S4a form N (nothing adopted)', ddet)
    conf = json.loads((PKG / CONFIRM_REL).read_text()) if (PKG / CONFIRM_REL).is_file() else {}
    files_ok &= g.check(str(conf.get('verdict', '')).startswith('PASS'), 'S4c verdict PASS (sealed wrapper record, A52 (e); logged before the first S5 launch)',
                        str(conf.get('verdict'))[:80])
    S = driver_module() if fsha(DRIVER) == DRIVER_SHA else None
    if S is not None:
        wp = S.pin_problems()
        files_ok &= g.check(not wp, 'driver pin check: frozen code, helpers, model file, solver.yaml, runner/builder and sources as pinned (A53 (g))', '; '.join(wp))
    else:
        files_ok &= g.check(False, 'driver not loaded (sha256 differs)')

    for words, row, what in ((G.A49_HEADING, G.A49_ROW, 'A49'), (G.A50_HEADING, G.A50_ROW, 'A50'), (G2.A51_HEADING, G2.A51_ROW, 'A51'),
                             (H.A52_HEADING, H.A52_ROW, 'A52'), (A53_HEADING, A53_ROW, 'A53')):
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

    if not files_ok or S is None:
        print(f'GATE FAILED ({len(g.fails) or 1}): nothing may be invoked (file / pin checks failed)', flush=True); return 1

    mx_runs = json.loads((HERE / 'campaign_matrix.json').read_text())['runs']
    L5 = s5_labels(mx_runs); id5 = {v: k for k, v in L5.items()}
    # ---------------------------------------------------------------- RUN_INDEX
    c10_labels = set(C.LABEL.values()); de_of = {v: k for k, v in DE.LABEL.items()}; f_of = {v: k for k, v in FG.LABEL.items()}
    a_of = {v: k for k, v in G.LABEL.items()}; h_of = {v: k for k, v in H.LABEL.items()}
    pairs, rows_h, rows_5, fin_a = [], {}, {}, {}
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            if C.rid_n(r['run_id']) <= C.rid_n(C.LAST_PRE): continue
            keep = {k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'exit_code')}; keep['started'] = str(r.get('notes', '')).startswith('STARTED')
            keep['model_note'] = f'model={C.MODEL_ENV}' in str(r.get('notes', '')).split() if keep['started'] else None
            if r['label'] in h_of: rows_h.setdefault(r['run_id'], []).append(keep)
            elif r['label'] in id5: rows_5.setdefault(r['run_id'], []).append(keep)
            elif r['label'] in a_of:
                fin_a.setdefault(r['run_id'], [r['label'], False]); fin_a[r['run_id']][1] = fin_a[r['run_id']][1] or r.get('exit_code', '') != ''
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    after = sorted({rid for rid, _ in pairs if C.rid_n(rid) > C.rid_n(C.LAST_PRE)}, key=C.rid_n)
    lab_of = {}
    for rid, lab in pairs: lab_of.setdefault(rid, lab)
    other = [rid for rid in after if not any(lab_of[rid] in s for s in (c10_labels, de_of, f_of, a_of, h_of, id5))]
    g.check(not other, f'RUN_INDEX: every run above {C.LAST_PRE} is S1-06R, a DIAG, D/E, stage F, S4a, S4c, S4d or S5 entry', str(other))
    fin_labels = {lab for rid, (lab, f) in fin_a.items() if f}
    miss_a = [k for k in G.ORDER if G.LABEL[k] not in fin_labels]
    unfin_a = sorted(rid for rid, (lab, f) in fin_a.items() if not f)
    g.check(not miss_a, 'S4a inventory complete: every S4a entry has a finished run (A51 (d))', f'missing: {miss_a}' if miss_a else '')
    g.check(unfin_a == [H.INTERRUPTED], f'the only S4a run without a finish row is the A51 interrupted {H.INTERRUPTED}', str(unfin_a))

    def started_of(rows, key_of):
        st, fin, ids = {}, {}, []
        for rid in [x for x in after if x in rows]:
            k = key_of[rows[rid][0]['label']]
            g.check(k not in st, f'RUN_INDEX: one run id per label ({rows[rid][0]["label"]})', f'{st.get(k)} and {rid}' if k in st else '')
            if k not in st: st[k] = rid; ids.append((k, rid))
            fin[k] = any(x['exit_code'] != '' and not x['started'] for x in rows[rid][1:])
        return st, fin, ids
    st_h, fin_h, seq_h = started_of(rows_h, h_of)
    for k in H.ORDER[:3]:
        ok = k in st_h and fin_h.get(k)
        if ok:
            f0 = rows_h[st_h[k]][0]
            ok = f0['started'] and f0['model_note'] and f0['deck_sha256'] == H.DECK[k] and f0['model_sha256'] == H.MATERIAL[k]
        g.check(bool(ok), f'S4c complete: {k} started and finished with the pinned STARTED-row inputs ({st_h.get(k)})')
    seq_hk = [k for k, _ in seq_h]
    g.check(seq_hk == H.ORDER[:len(seq_hk)], 'order: STARTED S4c/S4d runs == a prefix of S4C-2p0 .. S4D-13p2', ' -> '.join(f'{k} {r}' for k, r in seq_h) or 'none')
    for k in [x for x in H.ORDER[3:] if x in st_h]:
        f0 = rows_h[st_h[k]][0]
        g.check(f0['started'] and f0['model_note'] and f0['deck_sha256'] == H.DECK[k] and f0['model_sha256'] == H.MATERIAL[k],
                f'{st_h[k]} ({k}): STARTED-row input columns as pinned (deck_sha256, model_sha256, model note)')
    unfinished = [f'{st_h[k]} ({k})' for k in st_h if not fin_h[k]]

    # ---------------------------------------------------------------- S5 state
    st_5, fin_5, seq_5 = started_of(rows_5, id5)
    g.check(all(C.rid_n(r) > C.rid_n(LAST_S4C) for _, r in seq_5), f'every S5 run id is above {LAST_S4C} (S4c complete first)', str([r for _, r in seq_5]))
    stopped, stopped_started = [], {}
    for h in S.FOLDS:
        sp = S.path(h, 'stop')
        if sp.is_file():
            relp = S.rel(sp); srec = json.loads(sp.read_text()); cok, cdet = committed_in_git(relp)
            ok = g.check(S.seal_ok(srec) and srec.get('driver_sha256') == DRIVER_SHA and cok, f'{relp}: fold stop record sealed, made by the pinned driver, '
                         'committed in git HEAD (A53 (h))', cdet)
            if ok: stopped.append(h); stopped_started[h] = set(srec.get('started_entries') or {})
    exp = expected_sequence(S, stopped_started); exp_ids = [i for _, _, i in exp]; got = [k for k, _ in seq_5]
    g.check(got == exp_ids[:len(got)], 'order: STARTED S5 runs == a prefix of the registered sequence (H6p3, H2p0, H13p2; t1..t4, pred; stopped folds '
            'keep only their pre-stop entries)', ' -> '.join(f'{k} {r}' for k, r in seq_5) or 'none')
    inv_of = {i: (h, st) for h, st, i in exp}
    recs = {}
    for k, rid in seq_5:
        h, st = inv_of.get(k, (None, None))
        if h is None: g.check(False, f'{rid} ({k}): not in the registered sequence'); continue
        if (h, st) not in recs:
            p = S.path(h, st); recs[(h, st)] = json.loads(p.read_text()) if p.is_file() else None
        rec = recs[(h, st)]; f0 = rows_5[rid][0]
        pin = (rec or {}).get('dry_build', {}).get(k) or {}
        g.check(rec is not None and S.seal_ok(rec) and f0['started'] and f0['model_note'] and f0['deck_sha256'] == pin.get('deck_sha256')
                and f0['model_sha256'] == pin.get('model_sha256'), f'{rid} ({k}): STARTED-row inputs == the sealed record {h}/{st} dry build')
    unfinished += [f'{st_5[k]} ({k})' for k in st_5 if not fin_5[k]]
    if unfinished: g.stop(f'started S4d/S5 run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')

    # ---------------------------------------------------------------- the next invocation
    started5 = set(st_5); nx = next_invocation(S, started5, stopped)
    todo5 = [i for i in exp_ids if i not in started5]
    todo_d = [k for k in H.ORDER[3:] if k not in st_h]
    plan_rel, k_next, msg4 = None, [], None
    rc_cap = None
    if files_ok:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        rc_cap = getattr(rc, 'C10_CAP', None)
    if s4d_mode:
        if not todo_d: msg4 = 'S4d: every S4d entry has started and finished'
        else:
            plan_rel = H.P_D; pd = json.loads((PKG / H.P_D).read_text()); k_next = [e for e in pd['runs'] if e['id'] in todo_d]
            W = H.wrapper_module(); rec = json.loads((PKG / H.RECORD_REL).read_text())
            pb, _ = W.plan_problems('S4d', rec)
            g.check(W.seal_ok(rec) and rec.get('sha256') == H.RECORD_SEAL and not pb, f'{H.P_D}: carries exactly the sealed A52 record entries', '; '.join(pb))
            bad_d = [e['id'] for e in pd['runs'] if C.tsha(rc.current_deck_text(e, e['overrides'])) != H.DECK[e['id']]
                     or C.tsha(rc.current_material_text(e['overrides'])) != H.MATERIAL[e['id']]]
            g.check(not bad_d, 'dry-built S4d deck / material text sha256 == the A52 pins', f'differ: {bad_d}' if bad_d else '')
    elif nx is None:
        msg4 = 'S5: every registered entry has started and finished (stopped folds excluded); run s5_loo_driver.py score / report'
    else:
        h, st, rem = nx; p = S.path(h, st); relp = S.rel(p) if p.exists() else str(p)
        dec_p = S.path(h, 'branch')
        if not dec_p.is_file(): msg4 = f'next step is 0-launch: s5_loo_driver.py branch --held {h} (fold {S.FID[h]} decision)'
        elif not p.is_file():
            msg4 = (f'next step is 0-launch: s5_loo_driver.py {"next" if st != "pred" else "freeze"} --held {h} (fold {S.FID[h]}, {st}); then commit '
                    'the record, regenerate the plan (make_campaign_configs.py) and run this gate again')
        else:
            rec = json.loads(p.read_text()); dec = json.loads(dec_p.read_text())
            dcok, dcdet = committed_in_git(S.rel(dec_p))
            g.check(S.seal_ok(dec) and dcok, f'{S.rel(dec_p)}: fold decision sealed and committed in git HEAD', dcdet)
            cok, cdet = committed_in_git(relp)
            g.check(S.seal_ok(rec) and rec.get('driver_sha256') == DRIVER_SHA and rec.get('code_sha256') == FILES['analysis_2026-10-10_campaign/profile_s4s5.py']
                    and rec.get('decision_sha256') == dec.get('sha256') and cok,
                    f'{relp}: sealed, made by the pinned driver and the frozen profile_s4s5, bound to the fold decision, committed in git HEAD', cdet)
            ids = S.entry_ids(h, st)
            g.check(sorted(rec.get('entries', {})) == sorted(ids), f'{relp}: entries == {ids}')
            if st != 'pred':
                kk = int(st[1:]); state = S.index_state(S.read_index(C.INDEX))
                cands, cb = S.fold_candidates(h, kk - 1, state)
                g.check(not cb and rec.get('k') == kk and rec.get('fold_candidates_before') == cands,
                        f'{relp}: training step {kk}: the record was built on the finished runs of steps 1..{kk - 1} as in RUN_INDEX', '; '.join(cb))
            else:
                for rk in S.RANKS:
                    fp = S.path(h, f'frozen_{rk}'); fr = json.loads(fp.read_text()) if fp.is_file() else {}
                    fok, fdet = committed_in_git(S.rel(fp)) if fp.is_file() else (False, 'missing')
                    g.check(S.seal_ok(fr) and fr.get('sha256') == rec.get('frozen', {}).get(rk, {}).get('sha256') and fok,
                            f'{S.rel(fp)}: frozen {rk} record sealed, bound in the held-out record, committed in git HEAD (external commitment before the launch)', fdet)
            stem = f'campaign_C10_S5_{S.FID[h].lower()}_{st}'; plan_rel = f'config/{stem}.json'; pp = CFG / f'{stem}.json'
            GEN = generator_module()
            try: want = GEN.i_plan(h, st, p)
            except SystemExit as e: want = None; g.check(False, f'generator i_plan refused: {e}')
            have_p = json.loads(pp.read_text()) if pp.is_file() else None
            g.check(have_p is not None and have_p == want and have_p.get('runnable') is True and 'gates' not in have_p and 'state_only' not in have_p,
                    f'{plan_rel}: == the generator plan of the record (runnable, no gates, not state-only)')
            if have_p:
                mxi = {r['id']: r['campaign_entry'] for r in mx_runs}
                g.check(all(all(e.get(x) == mxi[e['id']].get(x) for x in ('id', 'thickness', 'label', 'timeout')) for e in have_p['runs']),
                        f'{plan_rel}: matrix ids, labels and timeouts')
                k_next = [e for e in have_p['runs'] if e['id'] in rem]
                bad_d = [e['id'] for e in have_p['runs'] if C.tsha(rc.current_deck_text(e, e['overrides'])) != rec['dry_build'][e['id']]['deck_sha256']]
                bad_m = [e['id'] for e in have_p['runs'] if C.tsha(rc.current_material_text(e['overrides'])) != rec['dry_build'][e['id']]['model_sha256']]
                g.check(not bad_d, 'dry-built deck text sha256 == the record dry build', f'differ: {bad_d}' if bad_d else '')
                g.check(not bad_m, 'dry-built material text sha256 == the record dry build', f'differ: {bad_m}' if bad_m else '')

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (not raised)', f'found {ms}')
    g.check(C.C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; not raised)', f'gate {C.C10_CAP}, runner {rc_cap}')
    n = len(k_next)
    g.check(cap > 0 and len(all_ids) + n <= cap, f'global budget: {len(all_ids)} used + {n} <= max_launches {cap}')
    g.check(c10 + n <= 200, f'C10 cap: {c10} used + {n} <= 200')
    g.check(c10 + len(todo5) + len(todo_d) + NEED_AFTER_S5 <= 200, f'A53 fit: c10 {c10} + unlaunched S5 {len(todo5)} + unlaunched S4d {len(todo_d)} + never-cut '
            f'need after S5 {NEED_AFTER_S5} = {c10 + len(todo5) + len(todo_d) + NEED_AFTER_S5} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/200; S4d started {len([k for k in st_h if k in H.ORDER[3:]])}/3; '
          f'S5 started {len(st_5)}/{S5_TOTAL} (stopped folds: {[S.FID[h] for h in stopped] or "none"}); next free id {nxt}', flush=True)

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
