import sys, json, hashlib, difflib
from pathlib import Path
PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
sys.dont_write_bytecode = True
sys.path.insert(0, str(PKG/'scripts')); sys.path.insert(0, str(PKG/'analysis_2026-10-10_campaign'))
import build_iwo_decks as bd, run_campaign as rc
bd.MODEL_FILE = sys.argv[1]
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
mx = {r['id']: r for r in json.loads((PKG/'analysis_2026-10-10_campaign'/'campaign_matrix.json').read_text())['runs']}
H = lambda s: hashlib.sha256(s.encode()).hexdigest()
d = {}
for i in ('S0-01', 'S3-04', 'S3-07'):
    r = mx[i]; e = r['campaign_entry']
    t = rc.current_deck_text(e, e['overrides']); m = rc.current_material_text(e['overrides'])
    d[i] = t; (out/f'{i}_device.in').write_text(t, newline='\n')
    print(i, e['label'], 'thickness', e['thickness'], 'overrides', e['overrides'], 'dup_of', r.get('duplicate_of'), 'deck', H(t), 'material', H(m))
for i in ('S3-04', 'S3-07'):
    diff = list(difflib.unified_diff(d['S0-01'].splitlines(), d[i].splitlines(), 'S0-01', i, lineterm='', n=0))
    print(i, 'diff lines vs S0-01:', len(diff)); print('\n'.join(diff[:40]))
