"""Build V2 decks without launching and show every line that differs from the V1 run deck of the same film."""
import difflib
import os
import sys
from pathlib import Path

os.environ['IWO_MODEL_FILE'] = 'config/iwo_material_model_v2.yaml'
PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'scripts'))
import numpy as np  # noqa: E402
from build_iwo_decks import load_configs, set_dotted, build_deck, read_meas  # noqa: E402

DOS = ['solver.dos_levels.numa=384', 'solver.dos_levels.numd=192']
CASES = {2.0: ('run_0038', DOS), 13.2: ('run_0040', DOS),
         6.3: ('run_0039', DOS + [f'thickness_laws.mu0_cm2Vs.mu_band_fitted[6.3]={sys.argv[1] if len(sys.argv) > 1 else 38.3893}'])}
for t, (rid, ov) in CASES.items():
    m, g, s = load_configs()
    for o in ov:
        k, v = o.split('=', 1)
        set_dotted(s, k[7:], v) if k.startswith('solver.') else set_dotted(m, k, v)
    vg, meas = read_meas(t)
    segs = [tuple(x) for x in s['sweep']['segments']]
    pts = [float(vg[0])]; a = float(vg[0])
    for e, st in segs:
        n = int(round((e - a) / st)); pts += [round(a + i * st, 6) for i in range(1, n + 1)]; a = float(e)
    targets = np.array(sorted(set(pts) & set(np.round(vg, 6).tolist())))
    text, meta = build_deck(t, m, g, s, meas=(vg, meas), targets=targets, full=True, segments=segs)
    old = next((PKG / 'results' / 'runs').glob(rid + '_*')) / 'device.in'
    print(f'===== {t} nm: V2 deck vs {rid}')
    for line in difflib.unified_diff(old.read_text().splitlines(), text.splitlines(), lineterm='', n=0):
        if not line.startswith(('---', '+++', '@@')):
            print(line[:170])
