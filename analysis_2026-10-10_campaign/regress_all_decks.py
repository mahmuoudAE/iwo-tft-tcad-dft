"""Deck regression gate for the 2026-10-10 campaign (NO simulator call, NO file written outside stdout).

Rebuilds the device.in of every finished run with the CURRENT generator (scripts/build_iwo_decks.build_deck), the
model file recorded in RUN_INDEX.csv (V1 default, V2 when the STARTED row says 'model=...'), and the overrides
recorded in the run's execution.json, then compares the text with the stored deck (newline-normalised read, the
same text the RUN_INDEX deck_sha256 was computed on). Covers transfer runs (stepped sweep, structure from
geometry.yaml) and ID-VD output runs. Pointwise/reduced runs 0001-0011 and partial/smoke/predict runs are SKIPPED.

Use: every new physics option must leave this script at 'all IDENTICAL' (except the known run_0027) while the option
is OFF.  python analysis_2026-10-10_campaign/regress_all_decks.py [run_0038 run_0058 ...]
Verified 2026-10-10: the generator module contains no subprocess / deckbuild call.
"""
import csv, hashlib, json, re, sys
from pathlib import Path
import numpy as np

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'scripts'))
import build_iwo_decks as bd  # noqa: E402

KNOWN_DIFF = {'run_0027': 'mesh-follows-contacts fix of 2026-09-27 (run_0027 had a fixed 24 um x-mesh; documented)'}
# 2026-10-11: the S0-02 repair launches before run_0067 (CODEX_WORK_CHAT A, table "S0-02"). Their decks were written by intermediate
# QTNLSC code that is not override-switchable today (0.25 nm HfO2 line in 0062; QTX/QTY mesh comment/loc forms in 0063-0066); the
# current default (automatic slicing + S/D exclude_near) rebuilds them as the run_0067 deck. Differences verified line by line 2026-10-11.
KNOWN_DIFF.update({r: 'S0-02 repair history (intermediate QTNLSC deck form, superseded by run_0067)' for r in
                   ('run_0062', 'run_0063', 'run_0064', 'run_0065', 'run_0066')})


def model_files():
    out = {}
    for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline='')):
        m = re.search(r'model=(\S+)', r.get('notes', ''))
        if r['notes'].startswith('STARTED'):
            out[r['run_id']] = (m.group(1) if m else 'config/iwo_material_model.yaml', r['notes'])
    return out


def apply(m, g, s, overrides):
    for o in overrides:
        k, v = o.split('=', 1)
        if k.startswith('solver.'): bd.set_dotted(s, k[7:], v)
        elif k.startswith('geometry.'): bd.set_dotted(g, k[9:], v)
        else: bd.set_dotted(m, k, v)


def rebuild(d, mf):
    ex = json.loads((d / 'execution.json').read_text())
    bd.MODEL_FILE = mf
    m, g, s = bd.load_configs(); apply(m, g, s, ex.get('overrides', []))
    t = float(ex['thickness_nm']); full = str(g.get('structure', 'reduced')).lower() == 'full'
    if ex.get('mode') == 'strip':   # 2026-10-10 ungated strip deck (run_atlas.execute_strip)
        text, _ = bd.build_deck(t, m, g, s, meas=bd.read_meas(t), full=full, strip=True)
        return text
    if ex.get('mode') == 'output_prediction':
        meta = json.loads((d / 'metadata.json').read_text())
        text, _ = bd.build_deck(t, m, g, s, meas=bd.read_meas(t), full=full, output_vgs=meta['output_vgs'],
                                vd_segments=[tuple(x) for x in meta['vd_segments']])
        return text
    vg, meas = bd.read_meas(t)
    segs = [tuple(x) for x in s['sweep']['segments']] if str(s.get('sweep', {}).get('mode')) == 'stepped' else None
    if segs is None: return None
    pts = [float(vg[0])]; a = float(vg[0])
    for e, st in segs:
        n = int(round((e - a) / st)); pts += [round(a + i * st, 6) for i in range(1, n + 1)]; a = float(e)
    targets = np.array(sorted(set(pts) & set(np.round(vg, 6).tolist())))
    text, _ = bd.build_deck(t, m, g, s, meas=(vg, meas), targets=targets, full=full, segments=segs)
    return text


def main(ids):
    mfs = model_files(); bad = 0; n_ok = 0
    for d in sorted((PKG / 'results' / 'runs').glob('run_*')):
        rid = d.name[:8]
        if ids and rid not in ids: continue
        if not (d / 'execution.json').exists() or rid not in mfs or int(rid[4:]) < 12:
            print(f'{rid}: SKIPPED (pre-final form or no record)'); continue
        notes = mfs[rid][1]
        if 'PREDICTION (no measurement)' in notes or 'partial' in notes:
            print(f'{rid}: SKIPPED (predict/partial mode)'); continue
        text = rebuild(d, mfs[rid][0])
        if text is None: print(f'{rid}: SKIPPED (pointwise sweep)'); continue
        old = (d / 'device.in').read_text()
        same = text == old
        tag = 'IDENTICAL' if same else ('DIFFERENT (known: ' + KNOWN_DIFF[rid] + ')' if rid in KNOWN_DIFF else 'DIFFERENT')
        print(f'{rid}: {tag}  model={mfs[rid][0]}  sha {hashlib.sha256(text.encode()).hexdigest()[:16]}')
        n_ok += same; bad += (not same) and rid not in KNOWN_DIFF
    print(f'identical {n_ok}; unexpected differences {bad}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(set(sys.argv[1:])))
