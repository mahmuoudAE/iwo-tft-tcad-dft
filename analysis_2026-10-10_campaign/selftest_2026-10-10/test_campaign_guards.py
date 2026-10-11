"""No-launch test of the C10 guards in scripts/run_campaign.py: execute / execute_strip and run_atlas.rows are patched, ROOT
points to the scratchpad (summaries and fake run dirs go there). Real plan file config/campaign_C10_MIN10.json is only read.
Run with IWO_MODEL_FILE=config/iwo_material_model_v3.yaml (as the campaign)."""
import json, shutil, sys, hashlib
from pathlib import Path
PKG = Path(r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1')
SCR = Path(__file__).resolve().parent / 'guard_test'
sys.path.insert(0, str(PKG / 'scripts'))
import run_atlas, run_campaign as rc
idx_hash = hashlib.sha256((PKG / 'results/RUN_INDEX.csv').read_bytes()).hexdigest()
plan = json.loads((PKG / 'config/campaign_C10_MIN10.json').read_text()); E = {e['id']: e for e in plan['runs']}; BYLABEL = {e['label']: e for e in plan['runs']}
FAIL_LABELS = set()

def write_run(d, rid, e, status, ov, thick=None, deck=True):
    (d / 'execution.json').write_text(json.dumps({'run_id': rid, 'status': status, 'overrides': ov, 'thickness_nm': e['thickness'] if thick is None else thick,
                                                  **({'mode': 'strip'} if e.get('mode') == 'strip' else {})}))
    (d / 'material_model_used.json').write_text(rc.current_material_text(ov))
    (d / 'device.in').write_text(rc.current_deck_text(e, ov) if deck else 'stale deck')

def setup(index_rows):
    if SCR.exists(): shutil.rmtree(SCR)
    (SCR / 'results/runs').mkdir(parents=True); rc.ROOT = SCR
    run_atlas.rows = lambda: list(index_rows)
    launched = []
    def fake(t, label, ov, *a, **k):
        launched.append(label); rid = f'run_{1000 + len(index_rows) + 1:04d}'; d = SCR / 'results/runs' / f'{rid}_{label}'; d.mkdir()
        index_rows.append({'run_id': rid, 'label': label, 'output_dir': f'results/runs/{d.name}', 'notes': 'fake'})
        if label in FAIL_LABELS:
            write_run(d, rid, BYLABEL[label], 'TIMEOUT', ov); raise RuntimeError(f'{rid}: mock timeout')
        write_run(d, rid, BYLABEL[label], 'REAL_ATLAS_SCORED', ov); return d
    rc.execute = fake; rc.execute_strip = fake; rc.execute_output = fake
    return launched

def prior(index_rows, e, status, overrides=None, thick=None, deck=True):
    rid = f'run_{100 + len(index_rows):04d}'; d = SCR / 'results/runs' / f'{rid}_{e["label"]}'; d.mkdir()
    write_run(d, rid, e, status, overrides if overrides is not None else e['overrides'], thick, deck)
    index_rows += [{'run_id': rid, 'label': e['label'], 'output_dir': f'results/runs/{d.name}', 'notes': 'STARTED'},
                   {'run_id': rid, 'label': e['label'], 'output_dir': f'results/runs/{d.name}', 'notes': status}]

def run(args):
    sys.argv = ['run_campaign.py', str(PKG / 'config/campaign_C10_MIN10.json')] + args
    try: rc.main(); return 'ok'
    except SystemExit as e: return f'SystemExit: {e}'

def rec(i): s = json.loads((SCR / 'results/campaigns/campaign_C10_MIN10.json').read_text()); return [x for x in s['runs'] if x['id'] == i]

rows = []; L = setup(rows); print('1 --workers 2:', run(['--workers', '2']), '| launched', L)
rows = []; L = setup(rows)
prior(rows, E['S0-01'], 'REAL_ATLAS_SCORED'); prior(rows, E['S0-02'], 'SIMULATOR_ERROR'); prior(rows, E['S1-01'], 'REAL_ATLAS_SCORED', overrides=['x=1'])
prior(rows, E['S1-02'], 'REAL_ATLAS_SCORED', thick=6.3); prior(rows, E['S2-01'], 'REAL_ATLAS_SCORED', deck=False)
r = run([]); print('2 resume with earlier launches:', r, '| launched', len(L), L)
for i in ('S0-01', 'S0-02', 'S1-01', 'S1-02', 'S2-01', 'S2-08'):
    x = rec(i)[-1]; print('    ', i, 'run_dir' in x, x.get('reused_earlier_launch'), (x.get('error') or '')[:100])
n0 = len(L); r = run([]); print('3 second resume:', r, '| new launches', len(L) - n0)
n0 = len(L); r = run(['--retry', 'S0-02']); print('4 --retry S0-02:', r, '| new launches', L[n0:])
FAIL_LABELS.add('c10_s2_08_13p2'); n0 = len(L); r = run(['--retry', 'S2-08']); x = rec('S2-08')
print('4b failed --retry of the finished S2-08:', r, '| new launches', L[n0:], '| records', len(x), '| latest has run_dir:', 'run_dir' in x[-1], '| earlier kept:', len(x[-1].get('earlier_records', [])))
FAIL_LABELS.clear(); n0 = len(L); r = run([]); print('4c resume after the failed retry:', r, '| new launches', L[n0:], '|', (rec('S2-08')[-1].get('error') or '')[:70])
rows = [{'run_id': f'run_{i:04d}', 'label': f'c10_fake_{i}', 'output_dir': '', 'notes': 'x'} for i in range(61, 261)]; L = setup(rows)
r = run([]); print('5 cap reached:', r, '| launched', L)
print('RUN_INDEX unchanged:', idx_hash == hashlib.sha256((PKG / 'results/RUN_INDEX.csv').read_bytes()).hexdigest(),
      '| real results/campaigns untouched:', not (PKG / 'results/campaigns/campaign_C10_MIN10.json').exists())
