"""Read-only: run run_atlas.strict_xy (new) and read_xy over every real DeckBuild export under results/runs; no writes."""
import sys
from pathlib import Path
PKG = Path(r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1')
sys.path.insert(0, str(PKG / 'scripts'))
import run_atlas as ra

ok = bad = 0; counts = {}; fails = []
for f in sorted((PKG / 'results' / 'runs').glob('run_*/*.dat')):
    if not __import__('re').match(r'^i[dgs]v[gd]', f.name): continue
    lines = f.read_text(errors='replace').splitlines()
    if len(lines) < 2 or len(lines[1].split()) != 3: counts['no_count_line'] = counts.get('no_count_line', 0) + 1
    try:
        xs, ys = ra.strict_xy(f); ok += 1
    except Exception as e:
        bad += 1; fails.append(f'{f.parent.name}/{f.name}: {e}')
print('strict_xy ok', ok, 'failed', bad, counts)
for x in fails[:40]: print('  ', x)
# the old nested logic, reproduced, on the file the review named
old_fail = None
f = PKG / 'results/runs/run_0041_2p0_pred_idvd_2p0/idvd_vg1.dat'
for line in f.read_text().splitlines():
    w = line.split()
    try: vals = [float(z) for z in w]
    except ValueError: continue
    if len(vals) != 2: old_fail = line.strip(); break
print('old logic on run_0041 idvd_vg1.dat raises on:', repr(old_fail))
xs, ys = ra.strict_xy(f); print('new strict_xy on it:', len(xs), 'rows, first', xs[:3], ys[:3])

