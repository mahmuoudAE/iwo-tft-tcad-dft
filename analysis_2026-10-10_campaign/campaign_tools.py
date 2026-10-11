"""Deck-text helpers for the 2026-10-10 campaign. NO simulator call: imports only scripts/build_iwo_decks.py (no subprocess /
deckbuild in that module) and never imports run_atlas / run_campaign. Builds the device.in of a campaign entry exactly as
scripts/run_atlas.execute (transfer) or execute_strip ("mode": "strip") would write it, so decks can be checked before launch.
"""
import json
import sys
from pathlib import Path

import numpy as np

PKG = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG / 'scripts'))
import build_iwo_decks as bd  # noqa: E402

MATRIX = HERE / 'campaign_matrix.json'
V2 = 'config/iwo_material_model_v2.yaml'
V3 = 'config/iwo_material_model_v3.yaml'


def matrix():
    return json.loads(MATRIX.read_text())


def configs(model_file, overrides):
    """load the three configs with model_file and route the overrides like run_atlas.execute (same prefixes)"""
    bd.MODEL_FILE = model_file
    m, g, s = bd.load_configs()
    for o in overrides:
        k, v = o.split('=', 1)
        if k.startswith('solver.'): bd.set_dotted(s, k[7:], v)
        elif k.startswith('geometry.'): bd.set_dotted(g, k[9:], v)
        else: bd.set_dotted(m, k, v)
    return m, g, s


def entry_deck(entry, model_file):
    """(text, meta) of a campaign entry {thickness, overrides, mode}; mirrors run_atlas.execute / execute_strip"""
    m, g, s = configs(model_file, entry.get('overrides', []))
    t = float(entry['thickness']); full = str(g.get('structure', 'reduced')).lower() == 'full'
    vg, meas = bd.read_meas(t)
    if entry.get('mode') == 'strip':
        return bd.build_deck(t, m, g, s, meas=(vg, meas), full=full, strip=True)
    if entry.get('mode') not in (None, 'transfer'): raise ValueError(f'{entry["id"]}: mode {entry.get("mode")} not handled here')
    segs = [tuple(x) for x in s['sweep']['segments']] if str(s.get('sweep', {}).get('mode', 'pointwise')) == 'stepped' else None
    if segs:
        pts = [float(vg[0])]; a = float(vg[0])
        for e, st in segs:
            n = int(round((e - a) / st)); pts += [round(a + i * st, 6) for i in range(1, n + 1)]; a = float(e)
        targets = np.array(sorted(set(pts) & set(np.round(vg, 6).tolist())))
    else:
        targets = vg
    return bd.build_deck(t, m, g, s, meas=(vg, meas), targets=targets, full=full, segments=segs)


def statements(text):
    """non-comment deck lines (the solver input), comments and blank lines removed"""
    return [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith('#')]
