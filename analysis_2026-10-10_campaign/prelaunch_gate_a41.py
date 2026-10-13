"""A41 pre-launch gate for config/campaign_C10_DIAGb.json (register A41 revision 3; Codex GO-WITH-CHANGES, work chat 2026-10-13T01:32Z, item 2).
NO launch, NO file written, nothing sealed opened. Run it immediately before EVERY invocation of the plan (the first one and any resume), in the
same PowerShell session and working directory (the package root) as the invocation:

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"
    & "<venv>\\Scripts\\python.exe" -I -B "<this file>"

Exit 0 only if every check below holds by explicit equality; then it prints the ONE command to use. Exit 1 on any mismatch, exit 4 when both
A41 runs have already started (nothing left to launch). Any unexpected error also exits 1 (fail closed).
  interpreter  isolated mode (-I) and the project venv (sys.prefix)
  cwd/env      working directory = package root; IWO_MODEL_FILE = config/iwo_material_model_v3.yaml; IWO_ATLAS_VIEWERS and IWO_ATLAS_JOB unset
  files        sha256 of the plan file; exact file set and sha256 of scripts/ (working-tree bytes of public-repo 1375164; three files carry CRLF
               endings, content equal to the commit); score_register.py, regress_all_decks.py, regress_sealed_aware.py
  plan         runnable, state_only results/sealed/campaigns, no gates, ids in order S2-11, S0-02-DOS2 with the registered labels
  dry build    run_campaign.current_deck_text / current_material_text for BOTH entries (the runner's own code, imported after the file check):
               deck text sha256 3034b7e2... (S2-11) and 09bb893d... (S0-02-DOS2), material text sha256 974b23ea... for both
  processes    no deckbuild/dbascii/atlas*/tonyplot*/athena*/devedit process (tasklist image names and CIM) and no python process whose command
               line names run_atlas or run_campaign (CIM Win32_Process; any python*.exe image, since the venv launcher python.exe
               starts the Store interpreter python3.13.exe); the process lists must be readable, otherwise fail. The two lists are
               reconciled by PID: every python process other than the gate itself must have a readable CIM command line; a PID missing
               from CIM, a null/empty CommandLine or a tasklist/CIM image-name conflict stops the gate as UNVERIFIABLE (Codex 2026-10-13,
               A41 record-note review: a waiting campaign wrapper could otherwise hide behind an unreadable command line)
  RUN_INDEX    columns run_id and label of every row; for a started A41 run only, the input columns of its first (STARTED) row: deck_sha256,
               model_sha256, notes (STARTED, model=config/iwo_material_model_v3.yaml). --retry S2-11 iff no c10_s2_11_2p0 row above run_0075
               (STARTED-row rule, unchanged). Fails on: a S0-02-DOS2 row without a rerun row (order), more than one rerun or DOS2 id, any
               other run after run_0075, run ids other than the expected run_0076 (rerun) / run_0077 (DOS2), a next free id that is not the
               expected one, a started A41 run missing from config/sealed_runs.json or with inventory values other than the registered ones
  budget       distinct run ids + launches of this invocation <= config/solver.yaml max_launches; c10 run ids + launches <= 200
State files results/campaigns/campaign_C10_DIAGb.json and results/sealed/campaigns/campaign_C10_DIAGb.full.json / .console.log are tested for
existence only (never opened) and reported for information.
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # importing scripts/ must not write __pycache__

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
VENV_PY = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe")
INDEX = PKG / 'results' / 'RUN_INDEX.csv'
INVENTORY = PKG / 'config' / 'sealed_runs.json'
PLAN_REL = 'config/campaign_C10_DIAGb.json'
PLAN_SHA = '662fd6628b350fc2fa9a968d7934f96f38fff27d242837a71621674eeca563aa'
ORDER = ['S2-11', 'S0-02-DOS2']
LABEL = {'S2-11': 'c10_s2_11_2p0', 'S0-02-DOS2': 'c10_s0_02_dos2_2p0'}
DECK = {'S2-11': '3034b7e276d40f8f8e3587219cbafe82c97c9db43ce23706938e18b4285ee956',
        'S0-02-DOS2': '09bb893d3254c9f0de24238e5b6f5eca3fa99c549c8d3f9456709eec95ff8e85'}
MATERIAL = '974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204'
MODEL_ENV = 'config/iwo_material_model_v3.yaml'
EXPECTED_ID = {'S2-11': 'run_0076', 'S0-02-DOS2': 'run_0077'}
OLD = 'run_0075'            # run_0075 holds c10_s2_11_2p0 (timed out, sealed, never substituted)
C10_CAP = 200
UNSET = ('IWO_ATLAS_VIEWERS', 'IWO_ATLAS_JOB')
SCRIPTS = {   # every file of scripts/ (outside __pycache__), working-tree bytes; equal to public-repo 1375164 (git diff empty)
    'build_iwo_decks.py': '97e3199294cd9bf9ad5670b820c52833627bafd0566df65c0a856347540a5190',
    'campaign_gates.py': 'c5e2fd5bb5711f7ab366d85fd8c13cb6bd3efcad387460308ea309e6348c0ceb',
    'campaign_sealed.py': '09d374d220efb17995d12d611aba13c9617ad1f761d3fb8dec95ae1fdbf8608c',
    'compare_experiment_simulation.py': 'b0a1c2ab6778e689d8275c1310c78af505d62f7d6b2d7ac3dd181148ec2c109c',
    'export_report_pdf.py': '9cfb4b364e10d09c2dde0010de436fc366d358c1052bbde5543fad3ddf3696ce',
    'extract_metrics.py': 'a7d0b236ecfa4f67433fc842a2b9cebeb295e4a5946f38ea72643139678edf63',
    'make_provenance_tables.py': '7ec8fc43f3be5006d62c6a89607f9cc072d1c74691e18a00c6aa2dcda527a81b',
    'material_laws.py': '748c2a287ad32b75c733f36b711ab91791aac16b3a3f376c4721ab8f8d261711',
    'plot_results.py': 'bd5c6fa39e157c3659a0fb52fbb4c350bb36942877e7123e8103988cc4f28a77',
    'plot_sensitivity.py': '858834ba2f288d3518d4e68a22250103967cc62e86da5dc51d6bf9e0714b6f69',
    'proc_guard.py': '6ac38ea89e0735d167c4df85e7b3efaeca83427970d172f4dd8b7b9fc48e7d80',
    'qe_build_inputs.py': '35bcbc15875471a80bf4387e72de6ab6d2440762ae6af70ed3f6f2c6fe1e0107',
    'run_atlas.py': 'b7927ac5b9747d5531ac827d220da6004e4a144d672ae16ab9bca2a28f46e6ae',
    'run_campaign.py': 'fb6e802f8c1cb71b56e153ed99504cc8e7e83d4c8eb7af8f13dc421d0fd125ac',
    'sensitivity_analysis.py': 'bb003c6563573f95d98cfdd9c8ca2360c1d318eb34dc4dc2d1009b513fbe88ee',
    'sensitivity_from_stage_runs.py': '81735baba71d06da10a86e5af8c00bb3b10444697da735c49fb9bc871ac1c95f'}
OTHER = {'analysis_2026-10-10_campaign/score_register.py': 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a',
         'analysis_2026-10-10_campaign/regress_all_decks.py': 'd7f26e9bb44e976c173131c627e7cd7bc7a9e9dcbed6de189d7b26b50ad64603',
         'analysis_2026-10-10_campaign/regress_sealed_aware.py': '9c06581434762a12d1426b9b2333d3b8ffc7191bc6b2117c66b721bd8f1bb41d'}
SILVACO = {'deckbuild.exe', 'dbascii.exe', 'atlas.exe', 'atlas2.exe', 'atlas3.exe', 'atlasm.exe', 'atlasmc.exe', 'tonyplot.exe',
           'tonyplot3d.exe', 'athena.exe', 'athena1d.exe', 'devedit.exe'}
def is_python(name):   # venv launcher python.exe AND the Store interpreter it starts (python3.13.exe, verified 2026-10-13), pythonw*, py/pyw
    return name.startswith('python') and name.endswith('.exe') or name in ('py.exe', 'pyw.exe')


RUNNER_RE = re.compile(r'run_(atlas|campaign)', re.I)
SYS32 = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32'


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsha(s): return hashlib.sha256(s.encode()).hexdigest()


def rid_n(rid): return int(rid[4:])


class Gate:
    def __init__(self): self.fails = []; self.info = []

    def check(self, ok, what, detail=''):
        print(f"[{'OK' if ok else 'FAIL'}] {what}" + (f'  ({detail})' if detail else ''), flush=True)
        if not ok: self.fails.append(what)
        return ok


def merge_processes(tl_rows, cim_data):
    """Reconcile tasklist rows ([image, pid, ...]) and CIM Win32_Process records by PID. Returns [(pid, image lower-case, command line or None)],
    one tuple per (PID, image name). The command line comes from CIM only; None means UNVERIFIABLE: the PID is missing from CIM, CIM gave a
    null/empty CommandLine, or tasklist and CIM disagree on the image name of the PID."""
    names, cmds = {}, {}
    for r in tl_rows:
        pid = int(r[1]) if r[1].isdigit() else -1
        names.setdefault(pid, set()).add(r[0].lower())
    for d in cim_data:
        pid = int(d.get('ProcessId') or -1)
        names.setdefault(pid, set()).add(str(d.get('Name') or '').lower())
        c = d.get('CommandLine')
        cmds[pid] = c if isinstance(c, str) and c.strip() else None
    out = []
    for pid, ns in names.items():
        ns.discard('')
        cmd = cmds.get(pid) if len(ns) <= 1 else None
        out += [(pid, n, cmd) for n in sorted(ns)]
    return out


def list_processes():
    """merge_processes(tasklist, CIM Win32_Process); raises if either list cannot be read (the gate then fails closed)"""
    tl = subprocess.run([str(SYS32 / 'tasklist.exe'), '/FO', 'CSV', '/NH'], capture_output=True, text=True, errors='replace', timeout=120)
    rows = [r for r in csv.reader(tl.stdout.splitlines()) if len(r) >= 2]
    if tl.returncode != 0 or not rows: raise RuntimeError(f'tasklist failed (exit {tl.returncode})')
    ps = SYS32 / 'WindowsPowerShell' / 'v1.0' / 'powershell.exe'
    cim = subprocess.run([str(ps), '-NoProfile', '-NonInteractive', '-Command',
                          '[Console]::OutputEncoding = [Text.Encoding]::UTF8; Get-CimInstance Win32_Process | '
                          'Select-Object ProcessId, Name, CommandLine | ConvertTo-Json -Compress'],
                         capture_output=True, timeout=180)
    if cim.returncode != 0: raise RuntimeError(f'CIM process query failed (exit {cim.returncode})')
    data = json.loads(cim.stdout.decode('utf-8', errors='replace'))
    data = data if isinstance(data, list) else [data]
    if not data: raise RuntimeError('CIM process query returned nothing')
    return merge_processes(rows, data)


def main():
    g = Gate()
    try:
        return run(g)
    except Exception as ex:   # fail closed
        g.check(False, f'unexpected error: {type(ex).__name__}: {ex}')
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked', flush=True)
        return 1


def run(g):
    print('A41 pre-launch gate, campaign_C10_DIAGb (no launch, nothing written)', flush=True)
    # interpreter, working directory, environment
    g.check(sys.flags.isolated == 1, 'interpreter in isolated mode (python -I)')
    g.check(Path(sys.prefix).resolve() == VENV_PY.parents[1].resolve(), 'interpreter is the project venv', sys.prefix)
    g.check(Path.cwd().resolve() == PKG.resolve(), 'working directory is the package root', str(Path.cwd()))
    g.check(os.environ.get('IWO_MODEL_FILE') == MODEL_ENV, f'IWO_MODEL_FILE == {MODEL_ENV}', repr(os.environ.get('IWO_MODEL_FILE')))
    for k in UNSET: g.check(k not in os.environ, f'{k} unset', repr(os.environ.get(k)) if k in os.environ else '')

    # frozen files (before anything is imported from scripts/)
    files_ok = g.check(fsha(PKG / PLAN_REL) == PLAN_SHA, f'{PLAN_REL} sha256 == {PLAN_SHA[:8]}...')
    have = {p.relative_to(PKG / 'scripts').as_posix() for p in (PKG / 'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    files_ok &= g.check(have == set(SCRIPTS), 'scripts/ file set == public-repo 1375164', f'extra {sorted(have - set(SCRIPTS))}, missing {sorted(set(SCRIPTS) - have)}' if have != set(SCRIPTS) else '')
    bad = sorted(f for f in SCRIPTS if f in have and fsha(PKG / 'scripts' / f) != SCRIPTS[f])
    files_ok &= g.check(not bad, 'scripts/ file sha256 == public-repo 1375164 (working-tree bytes)', f'differ: {bad}' if bad else '')
    for f, h in OTHER.items(): files_ok &= g.check(fsha(PKG / f) == h, f'{f} sha256 == {h[:8]}...')

    # plan
    plan = json.loads((PKG / PLAN_REL).read_text())
    g.check(plan.get('runnable') is True and 'gates' not in plan and plan.get('state_only') == {'sealed_dir': 'results/sealed/campaigns'},
            'plan runnable, state_only results/sealed/campaigns, no gates')
    ids = [e['id'] for e in plan['runs']]
    g.check(ids == ORDER and all(e['label'] == LABEL[e['id']] for e in plan['runs'] if e['id'] in LABEL),
            'plan order S2-11 then S0-02-DOS2 with the registered labels', str(ids))

    # dry build with the runner's own functions (only after the file check: scripts/ goes on sys.path)
    if files_ok and ids == ORDER:
        sys.path.insert(0, str(PKG / 'scripts')); os.chdir(PKG)
        import run_campaign as rc
        for e in plan['runs']:
            d = tsha(rc.current_deck_text(e, e['overrides'])); m = tsha(rc.current_material_text(e['overrides']))
            g.check(d == DECK[e['id']], f"{e['id']}: dry-built deck text sha256 == {DECK[e['id']][:8]}...", f'got {d[:8]}...' if d != DECK[e['id']] else '')
            g.check(m == MATERIAL, f"{e['id']}: material text sha256 == {MATERIAL[:8]}...", f'got {m[:8]}...' if m != MATERIAL else '')
    else:
        g.check(False, 'dry build not run (file or plan check failed)')

    # processes
    try:
        procs = list_processes()
    except Exception as ex:
        procs = None; g.check(False, f'process list readable ({type(ex).__name__}: {ex})')
    if procs is not None:
        me = os.getpid()
        sil = sorted({f'{n} pid {p}' for p, n, _ in procs if n in SILVACO})
        pyp = [(p, n, c) for p, n, c in procs if p != me and is_python(n)]
        unver = sorted({f'{n} pid {p}' for p, n, c in pyp if not (isinstance(c, str) and c.strip())})
        runners = sorted({f'{n} pid {p}' for p, n, c in pyp if isinstance(c, str) and RUNNER_RE.search(c)})
        g.check(not sil, 'no DeckBuild/ATLAS/TonyPlot/Athena/DevEdit process running', ', '.join(sil))
        g.check(not unver, 'every other python process has a readable command line (else UNVERIFIABLE)', ', '.join(unver))
        g.check(not runners, 'no python process running run_atlas / run_campaign', ', '.join(runners))

    # RUN_INDEX state (run_id and label of every row; input columns of the first row of a started A41 run only)
    rows = list(csv.DictReader(INDEX.open(newline='')))
    pairs = [(r['run_id'], r['label']) for r in rows]
    all_ids = sorted({rid for rid, _ in pairs}, key=rid_n); nxt = f'run_{rid_n(all_ids[-1]) + 1:04d}'
    c10 = len({rid for rid, lab in pairs if lab.startswith('c10_')})
    rerun = sorted({rid for rid, lab in pairs if lab == LABEL['S2-11'] and rid_n(rid) > rid_n(OLD)}, key=rid_n)
    dos2 = sorted({rid for rid, lab in pairs if lab == LABEL['S0-02-DOS2']}, key=rid_n)
    others = sorted({rid for rid, _ in pairs if rid_n(rid) > rid_n(OLD)} - set(rerun) - set(dos2), key=rid_n)
    g.check((OLD, LABEL['S2-11']) in pairs, f'RUN_INDEX: {OLD} holds {LABEL["S2-11"]}')
    g.check(len(rerun) <= 1, 'RUN_INDEX: at most one S2-11 rerun after run_0075', str(rerun))
    g.check(len(dos2) <= 1, 'RUN_INDEX: at most one S0-02-DOS2 run', str(dos2))
    g.check(not (dos2 and not rerun), 'RUN_INDEX: no S0-02-DOS2 row without a rerun row (order S2-11 first)')
    g.check(not others, 'RUN_INDEX: no other launch after run_0075 (expected ids unshifted)', str(others))
    for rid, eid in [(x, 'S2-11') for x in rerun[:1]] + [(x, 'S0-02-DOS2') for x in dos2[:1]]:
        g.check(rid == EXPECTED_ID[eid], f'RUN_INDEX: {eid} run id == expected {EXPECTED_ID[eid]}', rid)
        first = next(r for r in rows if r['run_id'] == rid)   # the STARTED row (rows are appended in launch order)
        notes = first['notes']
        g.check(first['label'] == LABEL[eid] and notes.startswith('STARTED') and f'model={MODEL_ENV}' in notes.split()
                and first['deck_sha256'] == DECK[eid] and first['model_sha256'] == MATERIAL,
                f'{rid}: STARTED-row input columns as registered (label, deck_sha256, model_sha256, model note)')
    inv = {r['run_id']: r for r in json.loads(INVENTORY.read_text())['runs']}
    g.check(OLD in inv, f'config/sealed_runs.json lists {OLD}')
    for rid, eid in [(x, 'S2-11') for x in rerun] + [(x, 'S0-02-DOS2') for x in dos2]:
        s = inv.get(rid, {})
        g.check(s.get('label') == LABEL[eid] and s.get('entry') == eid and s.get('deck_sha256') == DECK[eid] and s.get('model_sha256') == MATERIAL
                and s.get('model_file') == MODEL_ENV, f'config/sealed_runs.json lists started {rid} ({eid}) with the registered values')

    if not rerun:
        retry, todo = True, ORDER[:]
    elif not dos2:
        retry, todo = False, ORDER[1:]
    else:
        retry, todo = False, []
    if todo:
        g.check(nxt == EXPECTED_ID[todo[0]], f'next free run id == expected {EXPECTED_ID[todo[0]]} for {todo[0]}', nxt)
    m = re.search(r'^\s*max_launches:\s*(\d+)', (PKG / 'config' / 'solver.yaml').read_text(), re.M)
    cap = int(m.group(1)) if m else -1
    g.check(m is not None and len(all_ids) + len(todo) <= cap, f'global budget: {len(all_ids)} used + {len(todo)} <= max_launches {cap}')
    g.check(c10 + len(todo) <= C10_CAP, f'C10 cap: {c10} used + {len(todo)} <= {C10_CAP}')
    st = [PKG / 'results' / 'campaigns' / 'campaign_C10_DIAGb.json', PKG / 'results' / 'sealed' / 'campaigns' / 'campaign_C10_DIAGb.full.json',
          PKG / 'results' / 'sealed' / 'campaigns' / 'campaign_C10_DIAGb.console.log']
    print('[INFO] DIAGb state files present (existence only, not opened): '
          + (', '.join(p.relative_to(PKG).as_posix() for p in st if p.exists()) or 'none (no earlier invocation recorded)'), flush=True)
    print(f'[INFO] RUN_INDEX: {len(all_ids)} distinct run ids (max {all_ids[-1]}), c10 {c10}; S2-11 rerun rows {rerun or "none"}; '
          f'S0-02-DOS2 rows {dos2 or "none"}', flush=True)

    if g.fails:
        print(f'GATE FAILED ({len(g.fails)}): nothing may be invoked. Report the failure; a running DeckBuild/ATLAS process is not killed '
              'without the user\'s decision.', flush=True)
        return 1
    if not todo:
        print('NOTHING TO LAUNCH: both A41 runs have started (rerun ' + rerun[0] + ', S0-02-DOS2 ' + dos2[0] + '). Do not invoke the plan again.',
              flush=True)
        return 4
    cmd = f'& "{VENV_PY}" scripts/run_campaign.py {PLAN_REL}' + (' --retry S2-11' if retry else '')
    exp = ', then '.join(f'{e} -> {EXPECTED_ID[e]}' for e in todo)
    print(f'GATE PASSED. --retry S2-11: {"PASS IT (no c10_s2_11_2p0 row above run_0075)" if retry else "NEVER (the rerun already has a RUN_INDEX row)"}.'
          f'\nThis invocation launches: {exp} (only with the user\'s go for THIS launch; the hook asks).'
          f'\nCommand (same PowerShell session, package root, IWO_MODEL_FILE as set):\n{cmd}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
