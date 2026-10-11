"""Mock test of run_atlas.execute_strip with COPIES OF REAL DeckBuild exports (run_0041 idvd_vg1.dat / isvd_vg1.dat, which
carry the '36 2 2' count line). Popen, reserve and append are patched: no simulator, no run ID, no RUN_INDEX write; all
outputs go to the scratchpad. Prints one status per case. RUN_INDEX hash is checked before/after by the caller."""
import json, os, shutil, sys, hashlib
from pathlib import Path
SCR = Path(__file__).resolve().parent / 'mock_strip'
PKG = Path(r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1')
os.environ['IWO_MODEL_FILE'] = 'config/iwo_material_model_v3.yaml'
sys.path.insert(0, str(PKG / 'scripts'))
import run_atlas as ra
import subprocess

REAL = PKG / 'results/runs/run_0041_2p0_pred_idvd_2p0'
ID_TXT = (REAL / 'idvd_vg1.dat').read_text(); IS_TXT = (REAL / 'isvd_vg1.dat').read_text()
plan = json.loads((PKG / 'config/campaign_C10_S2_offfloor.json').read_text())
E = [x for x in plan['runs'] if x['id'] == 'S2-14'][0]
idx_hash = hashlib.sha256((PKG / 'results/RUN_INDEX.csv').read_bytes()).hexdigest()

def mutate_rows(txt, fn):
    """apply fn to the list of data rows (x, y strings); keep title/count/labels exactly as DeckBuild wrote them"""
    L = txt.splitlines(); head, rows = L[:4], [l.split() for l in L[4:] if l.strip()]
    return '\n'.join(head + [' '.join(r) for r in fn(rows)]) + '\n'
def recount(txt):
    L = txt.splitlines(); n = len([l for l in L[4:] if l.strip()]); L[1] = f'{n} 2 2'; return '\n'.join(L) + '\n'

FIN = 'ATLAS version 5.28.1.R finished\n'
CASES = {
    'real_exports_verbatim': dict(id=ID_TXT, is_=IS_TXT),
    'truncated_count_mismatch': dict(id=mutate_rows(ID_TXT, lambda r: r[:10]), is_=mutate_rows(IS_TXT, lambda r: r[:10])),
    'truncated_recounted_no_0p7V': dict(id=recount(mutate_rows(ID_TXT, lambda r: r[:10])), is_=recount(mutate_rows(IS_TXT, lambda r: r[:10]))),
    'wrong_sign': dict(id=mutate_rows(ID_TXT, lambda r: [[a, str(-float(b))] for a, b in r]), is_=mutate_rows(IS_TXT, lambda r: [[a, str(-float(b))] for a, b in r])),
    'kcl_violation': dict(id=ID_TXT, is_=mutate_rows(IS_TXT, lambda r: [[a, str(0.5 * float(b))] for a, b in r])),
    'missing_source_export': dict(id=ID_TXT, is_=None),
    'conflicting_duplicate': dict(id=recount(mutate_rows(ID_TXT, lambda r: r + [[r[5][0], str(2 * float(r[5][1]) + 1e-12)]])), is_=IS_TXT),
    'malformed_row': dict(id=mutate_rows(ID_TXT, lambda r: r[:5] + [r[5] + ['1.0']] + r[6:]), is_=IS_TXT),
    'exit_code_1': dict(id=ID_TXT, is_=IS_TXT, rc=1),
    'popen_failure': dict(popen_error=True),
    'timeout': dict(id=ID_TXT, is_=IS_TXT, timeout=True),
}

class FakeP:
    def __init__(self, argv, cwd, case, **kw):
        if case.get('popen_error'): raise OSError('mock: cannot start deckbuild')
        self.cwd = Path(cwd); self.case = case; self.pid = 0; self.returncode = case.get('rc', 0); self.calls = 0
        if case.get('id') is not None: (self.cwd / 'idvd_strip.dat').write_text(case['id'])
        if case.get('is_') is not None: (self.cwd / 'isvd_strip.dat').write_text(case['is_'])
        (self.cwd / 'deckbuild.out').write_text('ATLAS> go atlas\n' + FIN)
    def communicate(self, timeout=None):
        self.calls += 1
        if self.case.get('timeout') and self.calls == 1: raise subprocess.TimeoutExpired('deckbuild', timeout)
        return '', ''

rows = []; results = {}
if SCR.exists(): shutil.rmtree(SCR)
SCR.mkdir()
orig_run = subprocess.run
ra.ROOT = SCR   # only used for the relative output_dir of the (patched) RUN_INDEX row
for name, case in CASES.items():
    dest = SCR / name; dest.mkdir()
    ra.reserve = lambda r, t, label, d=dest: ('run_9999', d)
    ra.append = lambda row: rows.append(row)
    ra.subprocess.Popen = lambda argv, cwd=None, case=case, **kw: FakeP(argv, cwd, case)
    ra.subprocess.run = lambda *a, **k: None   # taskkill in the timeout path
    try:
        ra.execute_strip(13.2, E['label'], E['overrides'], E['timeout'])
        st = json.loads((dest / 'execution.json').read_text())['status']
    except Exception as e:
        st = json.loads((dest / 'execution.json').read_text())['status'] if (dest / 'execution.json').exists() else f'EXC {type(e).__name__}'
        st += f'  ({str(e)[:90]})'
    results[name] = st
ra.subprocess.run = orig_run
# drain grid without 0.7 V: must raise before any reservation
called = []
ra.reserve = lambda *a, **k: called.append(1) or ('run_9999', SCR / 'never')
try:
    ra.execute_strip(13.2, E['label'], E['overrides'] + ['solver.physics_options.strip.vd_segments[1][0]=0.6'], 900); results['grid_without_0p7V'] = 'NO ERROR (unexpected)'
except Exception as e:
    results['grid_without_0p7V'] = f'{type(e).__name__} before reservation: {not called} ({str(e)[:60]})'
for k, v in results.items(): print(f'{k:30s} {v}')
ok_strip = json.loads((SCR / 'real_exports_verbatim' / 'execution.json').read_text())
print('real-export case strip block:', json.dumps(ok_strip.get('strip'), default=float)[:300])
print('closing RUN_INDEX rows written (patched):', sum(1 for r in rows if not str(r.get('notes', '')).startswith('STARTED')), 'of', len(CASES) - 0)
print('RUN_INDEX unchanged:', idx_hash == hashlib.sha256((PKG / 'results/RUN_INDEX.csv').read_bytes()).hexdigest())

