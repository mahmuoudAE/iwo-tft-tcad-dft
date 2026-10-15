"""C10 pre-launch gate for stage G4/G5 = S4c (native confirmation) and S4d (runner-up branch) (register A52, 2026-10-15; no Codex review, D-63;
Claude go under D-59; the hook asks the user before every launch). NO launch, NO file written, nothing sealed opened. Run it immediately before
EVERY invocation of config/campaign_C10_S4c.json (S4C-2p0, -6p3, -13p2) and config/campaign_C10_S4d.json (S4D-2p0, -6p3, -13p2), in the same
PowerShell session and working directory (the package root) as the invocation:

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>" [--check]

It loads prelaunch_gate_c10_g2.py (sha256 pinned below; 144fff2f, A51) and, through it, the A50, F, D/E and C10 gates (all unchanged, their pins
checked) as modules for constants and helpers (Gate, process functions, amendment_logged, scripts/ pins, labels, S4a order); and the PA-18
wrapper s4c_confirm_wrapper.py (pinned) for its pin check and its plan-binding check.

Exit codes (ONLY 0 is a pass): 0 the next plan is launchable (prints the ONE command); 1 a check failed or an input is unreadable (fail closed);
3 STOP: a started S4c/S4d run has no finish row; 4 nothing to launch (all six entries have started and finished); not a pass.

Checks
  interpreter/cwd/env  -I, project venv, package root, IWO_MODEL_FILE V3, IWO_ATLAS_VIEWERS / IWO_ATLAS_JOB unset
  files        the G2, G, F, D/E and C10 gate files (pinned); scripts/ file set and sha256 (public-repo 1375164 + builder 734125a8); the C10 gate's
               OTHER files (frozen scorer c0f28bb9, post_run_checks, regress wrappers, campaign_extract/tools, A41 gate, V3 model); the frozen H-F v4
               files and profile_shared.py; campaign_matrix.json f06e8d77 (unchanged); the A49 driver and decision record; the plan generator (A52);
               the PA-18 wrapper and its tests; the frozen-tool outputs that carry the variable reference (A51 archive, surrogate output with the
               ABORT verdict, the S4A-04 profile_n record); the sealed variable-reference record (file sha256, seal, record sha256, committed in git
               HEAD byte for byte); the two route plans
  record       seal valid; candidate S4A-04; wrapper_sha256 == the pinned wrapper; code_sha256 == profile_s4s5 429b3a3f; the wrapper's own pin check
               (frozen code, helpers, model file, solver.yaml, runner/builder) passes; each route plan carries exactly the record's entries
  plans        runnable, no gates, NOT state-only, ids S4C-*/S4D-* in film order with the matrix labels and timeouts
  dry build    run_campaign.current_deck_text / current_material_text for the six entries == the record's pinned dry builds (== pinned here)
  amendments   A49, A50, A51 and A52 register headings (not draft) and IN FORCE decision-log rows (A52: D-75)
  processes    no Silvaco process, no runner python, every python command line readable
  RUN_INDEX    run_id/label of every row; for runs above run_0077: the label is S1-06R/DIAG, D/E, stage F, S4a, S4c or S4d; the S4a inventory is
               complete (every S4a label has a finished run; the only unfinished S4a run is the A51 interrupted run_0150); every S4c/S4d run id is
               above run_0156; one run id per S4c/S4d label; STARTED order == a prefix of S4C-2p0, S4C-6p3, S4C-13p2, S4D-2p0, S4D-6p3, S4D-13p2;
               STARTED-row input columns (deck_sha256, model_sha256, model note) as pinned; a finish row for every started S4c/S4d run (presence
               only; else STOP, exit 3). S4d is offered only after all three S4c runs have finished.
  budget       config/solver.yaml exactly one max_launches == 260; C10 cap 200 (gate constant and run_campaign.C10_CAP); distinct run ids + k <= 260 and
               c10 run ids + k <= 200 (k = launches of the next invocation); A52 fit: c10 used + unlaunched S4c/S4d + the never-cut need after S4d
               76 (A41(d) 6 + 3-D NC 17 + l = 0 triple 3 + S5 30 + S6 core 12 + S7 2 + repairs 6; S4b 18 returned under PA-19 v3 4 item 5) <= 200
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
G2_GATE = HERE / 'prelaunch_gate_c10_g2.py'
G2_GATE_SHA = '144fff2fc17343679df79002b81876a3a5626fb9795f52b0f32137f7c5a2fcf1'   # A51 / D-71
WRAPPER = HERE / 's4c_confirm_wrapper.py'
WRAPPER_SHA = '17d86c67d4d71e8d5b661aa44424d9cc4b98f2917b7c6f24450595b503e9e7c4'   # PA-18 wrapper (A52)
RECORD_REL = 'analysis_2026-10-10_campaign/profile/s4c_record_A52.json'
RECORD_FILE_SHA = '821867bcd6751da22dfc1be3501f119338ed50ed85119b745c8709370284255a'
RECORD_SEAL = 'd49ab722714eb294d46fc9458e2b781e353487e7853f9e6359873b4bfecac1fd'    # sealed variable reference (A52 (c))
P_C, P_D = 'config/campaign_C10_S4c.json', 'config/campaign_C10_S4d.json'
PLAN_SHA = {P_C: '0809527954bc97be56667c8a151837ae4f61c474a9307599962f55eb049dc0e4', P_D: '61b0df8342100c4626f709bbc8dc2f98fe7deedd48bcf7645b216d2825a0ac6a'}
FILES = {'analysis_2026-10-10_campaign/hf_score_draft.py': '96a2147eae6a07a2ea0afbed2d63476283c2d5bca3ffdfd7f829f248af3a1c81',      # H-F v4 (frozen)
         'analysis_2026-10-10_campaign/profile_s4s5.py': '429b3a3f3f5c1e650d17760e11665ddbce140ef434b5f80f29e7cd2f4fcf0a4e',        # S4b/S5 v4 (frozen)
         'analysis_2026-10-10_campaign/profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
         'analysis_2026-10-10_campaign/campaign_matrix.json': 'f06e8d7721f75aec3f78da06de1c1686c59307c33725bd8822c3ec3e0f0a443c',     # unchanged
         'analysis_2026-10-10_campaign/make_campaign_configs.py': '6aebbfdd28eb16db6922f155372dc0d4047d2b4b64b55b81583b6dd2af0c5fd7',  # A52
         'analysis_2026-10-10_campaign/s3_decision_a49.py': '72fb4295ac7d624e2a2d0c63394da651bf845b0b28cab2362108bcd6a3308a42',
         'analysis_2026-10-10_campaign/profile/s3_adoption_A49.json': '9ad43a88451082422e7b4faeaa710122aff28f44a94cff5562eeeb33f05b4993',
         'analysis_2026-10-10_campaign/test_s4c_confirm_wrapper.py': '3dafc48a70a234e9fc12deda4fb607ec6bf3e7f96be52307dedd3b8a14688a23',
         'analysis_2026-10-10_campaign/profile/s4a_archive_A51.json': '44de96df4bc0b2731e01b8b49c6fe2b06f4bf2295f2ff40141c7a283420df0f0',
         'analysis_2026-10-10_campaign/profile/s4s5_surrogate_s4a_archive_A51.json': 'ef10e8d4771e4c153bf230ff6b56cae52b5959dfcd71f4a5eeae36b6ebf3df42',
         'analysis_2026-10-10_campaign/profile/s4s5_profile_n_S4A-04.json': '043aa0078fe2374d76bf01e086c8cddb1f60e8845c3488ebad2fa38d08c7fc34',
         RECORD_REL: RECORD_FILE_SHA}
TAGS = ('2p0', '6p3', '13p2')
FILM = {'2p0': 2.0, '6p3': 6.3, '13p2': 13.2}
TIMEOUT = {'2p0': 1600, '6p3': 2000, '13p2': 3100}
ORDER = [f'S4C-{t}' for t in TAGS] + [f'S4D-{t}' for t in TAGS]
PLAN_IDS = {P_C: ORDER[:3], P_D: ORDER[3:]}
PLAN_OF = {k: rel for rel, ids in PLAN_IDS.items() for k in ids}
LABEL = {k: f'c10_{k[:3].lower()}_{k[4:]}_{k[4:]}' for k in ORDER}
DECK = {'S4C-2p0': '024224a3ceaf24adcd51f9d33b3d748aa7ed07a1bb5ea8a0314a6ef85433fe63', 'S4C-6p3': 'c00c1c542802fd813ce691c785f90f840154ac3cc48de14604b887b492d0f026',
        'S4C-13p2': 'a1ac856fbc5e9440e7e30d5354e2c380fdd1f8723db1bd8fb9c3baebe5bde83d', 'S4D-2p0': '0f0a212acf4c827450a5461a2d1a9bd11686cd0cc8d9086796531623125e8f45',
        'S4D-6p3': '2f866255fbe94c737caf4c555b8d57402c817a7364c012e02398b0a6b6ab2589', 'S4D-13p2': '3e6b5285de89dc38b58499580ebfff3c19a53a3474c2433885962c28b50e27f7'}
_M2, _M6, _M13 = ('b948563e0fe80479c5fde41cd6c243820b1fbfec0c0bbaae1e49be24379c73b2', '5f8b2373766cd1fc14757c2e35609f89a44d6967c0f7d8b2ec4acf05909724b3',
                  'e8ff9b2d1912a711ba9e7e03d995ceba14fb520db9864224cc981f4bf23132f1')
MATERIAL = {'S4C-2p0': _M2, 'S4C-6p3': _M6, 'S4C-13p2': _M13, 'S4D-2p0': _M2, 'S4D-6p3': _M6, 'S4D-13p2': _M13}   # IGZO options are solver-side
A52_HEADING = ['PA-18', 'S4c confirmation wrapper', 's4c_confirm_wrapper.py', 'S4d', 'prelaunch_gate_c10_h.py', RECORD_SEAL[:16]]
A52_ROW = ['A52', 'PA-18', 's4c_confirm_wrapper.py', 'prelaunch_gate_c10_h.py', RECORD_SEAL[:16]]
LAST_S4A = 'run_0156'      # last S4a run (S4A-15-13p2); every S4c/S4d run id is above it
INTERRUPTED = 'run_0150'   # A51: the only S4a run without a finish row
NEED_AFTER_S4CD = 6 + 17 + 3 + 30 + 12 + 2 + 6   # A41(d) + 3-D NC + l = 0 triple + S5 + S6 core + S7 + repairs = 76 (S4b 18 returned, PA-19 v3 4 item 5)


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def g2_module():
    spec = importlib.util.spec_from_file_location('prelaunch_gate_c10_g2_pinned', G2_GATE); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def wrapper_module():
    spec = importlib.util.spec_from_file_location('s4c_confirm_wrapper_pinned', WRAPPER); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def committed_in_git(rel, want_sha):
    """(ok, detail): the working-tree file hashes to want_sha AND its content is the git HEAD blob (compared with CRLF normalised to LF: this
    repository commits with core.autocrlf=input, so the blob holds LF while the Windows working tree holds CRLF); the record is committed before
    the native launch, A52 (c)"""
    try:
        out = subprocess.run(['git', '-C', str(PKG), 'cat-file', '-p', f'HEAD:{rel}'], capture_output=True, timeout=60)
    except Exception as ex:
        return False, f'git not runnable ({type(ex).__name__})'
    if out.returncode != 0: return False, 'not in HEAD'
    wt = (PKG / rel).read_bytes(); norm = lambda b: hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()
    ok = hashlib.sha256(wt).hexdigest() == want_sha and norm(out.stdout) == norm(wt)
    return ok, f'HEAD blob sha256 {hashlib.sha256(out.stdout).hexdigest()[:8]}, LF-normalised content {"equal" if norm(out.stdout) == norm(wt) else "DIFFERENT"}'


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if fsha(G2_GATE) != G2_GATE_SHA:
        print(f'[FAIL] prelaunch_gate_c10_g2.py sha256 == {G2_GATE_SHA[:8]}...\nGATE FAILED (1): nothing may be invoked', flush=True); return 1
    G2 = g2_module()
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
        return run(G2, G, FG, DE, C, g, argv)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True); return 1


def run(G2, G, FG, DE, C, g, argv):
    check_mode = '--check' in argv
    print('C10 pre-launch gate, stage G4/G5 = S4c / S4d (campaign_C10_S4c, campaign_C10_S4d; register A52, PA-18; no launch, nothing written)'
          + ('  [CHECK MODE: no invocation follows from this output]' if check_mode else ''), flush=True)
    g.check(True, f'prelaunch_gate_c10_g2.py sha256 == {G2_GATE_SHA[:8]}... (loaded with the G, F, D/E and C10 gates for pins and helpers)')
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == C.VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == C.MODEL_ENV, f'IWO_MODEL_FILE == {C.MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in C.UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    files_ok = g.check(fsha(G.F_GATE) == G.F_GATE_SHA and fsha(FG.DE_GATE) == FG.DE_GATE_SHA and fsha(DE.C10_GATE) == DE.C10_GATE_SHA
                       and fsha(G2.G_GATE) == G2.G_GATE_SHA, f'prelaunch_gate_c10_g.py {G2.G_GATE_SHA[:8]}..., _f.py {G.F_GATE_SHA[:8]}..., _de.py '
                       f'{FG.DE_GATE_SHA[:8]}..., prelaunch_gate_c10.py {DE.C10_GATE_SHA[:8]}... as pinned')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(C.SCRIPTS), 'scripts/ file set == public-repo 1375164 (+ pinned builder)',
                        '' if have == set(C.SCRIPTS) else f'extra {sorted(have - set(C.SCRIPTS))}, missing {sorted(set(C.SCRIPTS) - have)}')
    bad = sorted(f for f in C.SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != C.SCRIPTS[f])
    files_ok &= g.check(not bad, f'scripts/ sha256 as pinned (build_iwo_decks.py {C.SCRIPTS["build_iwo_decks.py"][:8]})', f'differ: {bad}' if bad else '')
    for f, h in {**C.OTHER, **FILES}.items(): files_ok &= g.check(fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')
    files_ok &= g.check(fsha(WRAPPER) == WRAPPER_SHA, f's4c_confirm_wrapper.py sha256 == {WRAPPER_SHA[:8]}... (PA-18 wrapper)')
    for rel, h in PLAN_SHA.items(): files_ok &= g.check(fsha(PKG / rel) == h, f'{rel} sha256 == {h[:8]}...')
    dok, ddet = G.decision_ok(PKG / G.DECISION)
    files_ok &= g.check(dok, 'A49 decision record: S4a form N (nothing adopted)', ddet)
    cok, cdet = committed_in_git(RECORD_REL, RECORD_FILE_SHA)
    files_ok &= g.check(cok, f'variable-reference record committed in git HEAD byte for byte (A52 (c): sha256 {RECORD_SEAL[:12]}... committed before launch)', cdet)

    rec = json.loads((PKG / RECORD_REL).read_text()) if (PKG / RECORD_REL).is_file() else {}
    W = wrapper_module() if fsha(WRAPPER) == WRAPPER_SHA else None
    rec_ok = W is not None and g.check(W.seal_ok(rec) and rec.get('sha256') == RECORD_SEAL, f'record seal valid and == {RECORD_SEAL[:12]}...')
    if W is not None and rec_ok:
        rec_ok &= g.check(rec.get('candidate') == 'S4A-04' and rec.get('wrapper_sha256') == WRAPPER_SHA and rec.get('code_sha256') == W.FROZEN['profile_s4s5.py'],
                          'record: candidate S4A-04 (frozen surrogate best), made by the pinned wrapper and the frozen profile_s4s5 429b3a3f')
        wp = W.pin_problems()
        rec_ok &= g.check(not wp, 'wrapper pin check: frozen code, helpers, model file, solver.yaml, runner/builder as pinned (PA-18 (b)/(e))', '; '.join(wp))
        rec_ok &= g.check(rec.get('dry_build') == {k: {'deck_sha256': DECK[k], 'model_sha256': MATERIAL[k]} for k in ORDER},
                          'record dry builds == the deck/material pins of this gate')
        for stage, rel in (('S4c', P_C), ('S4d', P_D)):
            pb, _ = W.plan_problems(stage, rec)
            rec_ok &= g.check(not pb, f'{rel}: carries exactly the record entries (ids, labels, overrides, timeouts; runnable, no gates, not state-only)', '; '.join(pb))
    elif W is None:
        g.check(False, 'wrapper not loaded (sha256 differs)')

    plans = {rel: json.loads((PKG / rel).read_text()) for rel in PLAN_SHA}
    plans_ok = True
    for rel, p in plans.items():
        ids = [e['id'] for e in p['runs']]; labs = {e['id']: e['label'] for e in p['runs']}; tos = {e['id']: e['timeout'] for e in p['runs']}
        plans_ok &= g.check(p.get('runnable') is True and 'gates' not in p and 'state_only' not in p and ids == PLAN_IDS[rel]
                            and labs == {k: LABEL[k] for k in PLAN_IDS[rel]} and tos == {k: TIMEOUT[k[4:]] for k in PLAN_IDS[rel]},
                            f'{rel}: runnable, no gates, not state-only, ids {PLAN_IDS[rel][0]}..{PLAN_IDS[rel][-1]} with the registered labels and timeouts',
                            f'{ids}')
    rc_cap = None
    if files_ok and plans_ok and rec_ok:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        rc_cap = getattr(rc, 'C10_CAP', None)
        ent = {k: next(e for rel in PLAN_SHA for e in plans[rel]['runs'] if e['id'] == k) for k in ORDER}
        bad_d = [k for k, e in ent.items() if C.tsha(rc.current_deck_text(e, e['overrides'])) != DECK[k]]
        bad_m = [k for k, e in ent.items() if C.tsha(rc.current_material_text(e['overrides'])) != MATERIAL[k]]
        g.check(not bad_d, 'dry-built deck text sha256 == pinned for the six S4c/S4d entries', f'differ: {bad_d}' if bad_d else '')
        g.check(not bad_m, 'dry-built material text sha256 == pinned', f'differ: {bad_m}' if bad_m else '')
    else:
        g.check(False, 'dry build not run (file, record or plan check failed)')

    for words, row, what in ((G.A49_HEADING, G.A49_ROW, 'A49'), (G.A50_HEADING, G.A50_ROW, 'A50'), (G2.A51_HEADING, G2.A51_ROW, 'A51'),
                             (A52_HEADING, A52_ROW, 'A52')):
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

    # RUN_INDEX: run_id/label of every row; STARTED-row input columns and finish-row presence only
    c10_labels = set(C.LABEL.values()); de_of = {v: k for k, v in DE.LABEL.items()}; f_of = {v: k for k, v in FG.LABEL.items()}
    a_of = {v: k for k, v in G.LABEL.items()}; h_of = {v: k for k, v in LABEL.items()}
    pairs, rows_h, fin_a = [], {}, {}
    with C.INDEX.open(newline='') as fh:
        for r in csv.DictReader(fh):
            pairs.append((r['run_id'], r['label']))
            if C.rid_n(r['run_id']) <= C.rid_n(C.LAST_PRE): continue
            if r['label'] in h_of:
                rows_h.setdefault(r['run_id'], []).append({k: r.get(k, '') for k in ('label', 'deck_sha256', 'model_sha256', 'notes', 'exit_code')})
            elif r['label'] in a_of:
                fin_a.setdefault(r['run_id'], [r['label'], False])
                fin_a[r['run_id']][1] = fin_a[r['run_id']][1] or r.get('exit_code', '') != ''
    all_ids = sorted({rid for rid, _ in pairs}, key=C.rid_n); nxt = f'run_{C.rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    after = sorted({rid for rid, _ in pairs if C.rid_n(rid) > C.rid_n(C.LAST_PRE)}, key=C.rid_n)
    lab_of = {}
    for rid, lab in pairs: lab_of.setdefault(rid, lab)
    other = [rid for rid in after if not any(lab_of[rid] in s for s in (c10_labels, de_of, f_of, a_of, h_of))]
    g.check(not other, f'RUN_INDEX: every run above {C.LAST_PRE} is S1-06R, a DIAG, D/E, stage F, S4a, S4c or S4d entry', str(other))
    # the S4a inventory is complete (A51 (d)): every S4a label has a finished run; the only unfinished S4a run is run_0150
    fin_labels = {lab for rid, (lab, f) in fin_a.items() if f}
    miss_a = [k for k in G.ORDER if G.LABEL[k] not in fin_labels]
    unfin_a = sorted(rid for rid, (lab, f) in fin_a.items() if not f)
    g.check(not miss_a, 'S4a inventory complete: every S4a entry has a finished run (A51 (d))', f'missing: {miss_a}' if miss_a else '')
    g.check(unfin_a == [INTERRUPTED], f'the only S4a run without a finish row is the A51 interrupted {INTERRUPTED}', str(unfin_a))
    h_ids = [rid for rid in after if rid in rows_h]
    g.check(all(C.rid_n(r) > C.rid_n(LAST_S4A) for r in h_ids), f'every S4c/S4d run id is above {LAST_S4A} (S4a complete first)', str(h_ids))
    started = {}
    for rid in h_ids:
        k = h_of[rows_h[rid][0]['label']]
        g.check(k not in started, f'RUN_INDEX: one run id per label ({LABEL[k]})', f'{started.get(k)} and {rid}' if k in started else '')
        started.setdefault(k, rid)
    finished = {}
    for k, rid in started.items():
        first = rows_h[rid][0]; n = first['notes']
        g.check(n.startswith('STARTED') and f'model={C.MODEL_ENV}' in n.split() and first['deck_sha256'] == DECK[k] and first['model_sha256'] == MATERIAL[k],
                f'{rid} ({k}): STARTED-row input columns as pinned (deck_sha256, model_sha256, model note)')
        finished[k] = any(x['exit_code'] != '' for x in rows_h[rid][1:])
    launched = [h_of[rows_h[rid][0]['label']] for rid in h_ids]
    g.check(launched == ORDER[:len(launched)], 'order: STARTED S4c/S4d runs == a prefix of S4C-2p0, S4C-6p3, S4C-13p2, S4D-2p0, S4D-6p3, S4D-13p2',
            ' -> '.join(f'{k} {r}' for k, r in zip(launched, h_ids)) or 'none')
    unfinished = [f'{started[k]} ({k})' for k in started if not finished[k]]
    todo = [k for k in ORDER if k not in started]
    if unfinished: g.stop(f'started S4c/S4d run(s) without a finish row: {unfinished} (a launch in progress, or a runner crash): nothing is invoked; decide by hand')
    plan_rel = PLAN_OF[todo[0]] if todo else None
    if plan_rel == P_D:
        g.check(all(k in started and finished[k] for k in ORDER[:3]), 'S4d only after all three S4c runs have started and finished (A52 (g))')
    nxt_k = [k for k in todo if PLAN_OF[k] == plan_rel] if plan_rel else []

    ms = re.findall(r'^\s*max_launches:\s*(\d+)', C.SOLVER.read_text(), re.M); cap = int(ms[0]) if len(ms) == 1 else -1
    g.check(cap == C.MAX_LAUNCHES == 260, 'config/solver.yaml: exactly one max_launches and it == 260 (not raised)', f'found {ms}')
    g.check(C.C10_CAP == 200 and rc_cap == 200, 'C10 cap == 200 (gate constant and run_campaign.C10_CAP; not raised)', f'gate {C.C10_CAP}, runner {rc_cap}')
    g.check(cap > 0 and len(all_ids) + len(nxt_k) <= cap, f'global budget: {len(all_ids)} used + {len(nxt_k)} <= max_launches {cap}')
    g.check(c10 + len(nxt_k) <= 200, f'C10 cap: {c10} used + {len(nxt_k)} <= 200')
    g.check(c10 + len(todo) + NEED_AFTER_S4CD <= 200, f'A52 fit: c10 {c10} + unlaunched S4c/S4d {len(todo)} + never-cut need after S4d {NEED_AFTER_S4CD} = '
            f'{c10 + len(todo) + NEED_AFTER_S4CD} <= 200 (six repairs reserved)')
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}/200; S4c/S4d started: {len(started)}/6'
          + (f' (last {launched[-1]} {h_ids[-1]})' if launched else '') + f'; next free id {nxt}', flush=True)

    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True); return 1
    if g.stops:
        print(f'GATE STOP ({len(g.stops)}): a main-session decision is needed; nothing may be invoked.', flush=True); return 3
    if not todo:
        print('NOTHING TO LAUNCH: every S4c/S4d entry has started and finished. Do not invoke these plans again. (Exit 4 is not a pass.)', flush=True); return 4
    cmd = f'& "{C.VENV_PY}" scripts/run_campaign.py {plan_rel}'
    print(f'GATE PASSED. Next plan {plan_rel}: {nxt_k[0]} ({LABEL[nxt_k[0]]}) ... {nxt_k[-1]}, first run id {nxt}; the invocation runs these '
          f'{len(nxt_k)} entr{"y" if len(nxt_k) == 1 else "ies"} in order and stops. Only with the go for THIS launch (the hook asks the user). '
          + ('Would-be command (check mode, not an instruction)' if check_mode else 'Command (same PowerShell session, package root, IWO_MODEL_FILE as set)')
          + f':\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
