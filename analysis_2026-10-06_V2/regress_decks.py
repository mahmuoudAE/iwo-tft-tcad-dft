"""Regression check (no launch): rebuild the decks of finished runs with the current generator and the overrides
recorded in each run's execution.json; the text must be byte-identical to the stored device.in.
Usage: python regress_decks.py run_0038 run_0039 run_0040"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'scripts'))
from build_iwo_decks import load_configs, set_dotted, build_deck, read_meas  # noqa: E402

ok = True
for rid in sys.argv[1:]:
    d = next((PKG / 'results' / 'runs').glob(rid + '_*'))
    ex = json.loads((d / 'execution.json').read_text())
    m, g, s = load_configs()
    for o in ex['overrides']:
        k, v = o.split('=', 1)
        set_dotted(s, k[7:], v) if k.startswith('solver.') else set_dotted(g, k[9:], v) if k.startswith('geometry.') else set_dotted(m, k, v)
    t = float(ex['thickness_nm'])
    vg, meas = read_meas(t)
    segs = [tuple(x) for x in s['sweep']['segments']]
    pts = [float(vg[0])]; a = float(vg[0])
    for e, st in segs:
        n = int(round((e - a) / st)); pts += [round(a + i * st, 6) for i in range(1, n + 1)]; a = float(e)
    targets = np.array(sorted(set(pts) & set(np.round(vg, 6).tolist())))
    text, _ = build_deck(t, m, g, s, meas=(vg, meas), targets=targets, full=str(g.get('structure')).lower() == 'full', segments=segs)
    old = (d / 'device.in').read_text()
    same = text == old
    ok &= same
    print(f'{rid}: {"IDENTICAL" if same else "DIFFERENT"}  sha new {hashlib.sha256(text.encode()).hexdigest()[:16]} old {hashlib.sha256(old.encode()).hexdigest()[:16]}')
    if not same:
        import difflib
        print('\n'.join(list(difflib.unified_diff(old.splitlines(), text.splitlines(), lineterm='', n=0))[:30]))
sys.exit(0 if ok else 1)
