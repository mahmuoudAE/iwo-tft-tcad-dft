"""Sealed-aware deck regression gate (register amendment A41 (e); Codex GO-WITH-CHANGES, work chat 2026-10-13T01:32Z, item 5).
NO simulator call, NO file written.

  <venv python> analysis_2026-10-10_campaign/regress_sealed_aware.py          (from the package root; no arguments)

The committed gate regress_all_decks.py is imported UNCHANGED; this wrapper only keeps it away from sealed runs. Inventory:
config/sealed_runs.json, an explicit list of sealed run ids (run id, label, matrix entry, model file, registered deck_sha256 and model_sha256).
  0. Inventory guard, before anything else is read: every RUN_INDEX run id whose label is the label of an entry of a state-only plan
     (config/campaign_C10_*.json with "state_only") must be in the inventory; otherwise the wrapper STOPS (exit 2) and names the ids to add.
     Only the RUN_INDEX columns run_id and label are read for this.
  1. regress_all_decks.main over every run directory EXCEPT the inventoried ids. RUN_INDEX rows of an inventoried id are dropped by run_id
     before any other column is accessed (model_files below = regress_all_decks.model_files with that filter added; the committed one would
     regex-search their notes), and their run directories are skipped by name before anything inside them is opened.
  2. For each inventoried id: its RUN_INDEX label, deck_sha256 and model_sha256 (input columns, written at launch; a run that has only its
     STARTED row is enough) must equal the inventory, and the deck and material texts that the CURRENT generator gives for its matrix entry
     (scripts/run_campaign.current_deck_text / current_material_text, model file from the inventory) must hash to the inventory values.
     Only equalities are printed.
Final line as in the committed gate: 'identical N; unexpected differences K' (K = regress_all_decks unexpected + sealed mismatches); exit 1 if
K > 0, exit 2 if the inventory guard stops.
Rule (A41 (e); campaign_C10_DIAGb stop rules): each run of a state-only plan is appended to the inventory as soon as its RUN_INDEX STARTED row
exists and before any later regression check; removing an entry (unsealing) needs a logged decision.
Successor of the reviewed scratchpad wrapper regress_unsealed_a41.py (sha256 60f8bb07...411a): same regression logic, explicit inventory added.
"""
import contextlib
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'analysis_2026-10-10_campaign')); sys.path.insert(0, str(PKG / 'scripts'))
INDEX = PKG / 'results' / 'RUN_INDEX.csv'
INVENTORY = PKG / 'config' / 'sealed_runs.json'
KEYS = ('run_id', 'label', 'entry', 'model_file', 'deck_sha256', 'model_sha256')


def sha(s): return hashlib.sha256(s.encode()).hexdigest()


def inventory():
    runs = json.loads(INVENTORY.read_text())['runs']
    bad = [r.get('run_id') for r in runs if any(not isinstance(r.get(k), str) or not r.get(k) for k in KEYS)]
    ids = [r['run_id'] for r in runs]
    if bad or len(ids) != len(set(ids)): raise SystemExit(f'{INVENTORY.name}: incomplete entries {bad} or duplicate run ids; nothing checked')
    return {r['run_id']: r for r in runs}


def state_only_labels():
    out = {}
    for p in sorted((PKG / 'config').glob('campaign_C10_*.json')):
        plan = json.loads(p.read_text())
        if 'state_only' in plan:
            for e in plan['runs']: out.setdefault(e['label'], p.stem)
    return out


def main():
    inv = inventory(); sealed = set(inv); sol = state_only_labels()
    labels = {}
    for r in csv.DictReader(INDEX.open(newline='')): labels.setdefault(r['run_id'], set()).add(r['label'])   # run_id and label only
    missing = sorted(rid for rid, ls in labels.items() if rid not in sealed and ls & set(sol))
    if missing:
        print('STOP: RUN_INDEX runs with a state-only plan label are not in config/sealed_runs.json: '
              + ', '.join(f'{rid} ({", ".join(sorted(labels[rid]))})' for rid in missing)
              + '. Add them first (A41 (e)); no run directory and no other RUN_INDEX column was read.')
        return 2

    import regress_all_decks as rd  # noqa: E402  (committed gate, unchanged)

    def model_files():   # regress_all_decks.model_files, with the sealed rows dropped by run_id before any other column is read
        out = {}
        for r in csv.DictReader(INDEX.open(newline='')):
            if r['run_id'] in sealed: continue
            m = re.search(r'model=(\S+)', r.get('notes', ''))
            if r['notes'].startswith('STARTED'):
                out[r['run_id']] = (m.group(1) if m else 'config/iwo_material_model.yaml', r['notes'])
        return out

    rd.model_files = model_files
    ids = sorted({d.name[:8] for d in (PKG / 'results' / 'runs').glob('run_*')} - sealed)
    if not ids: raise SystemExit('no unsealed run directory found; regress_all_decks.main(set()) would scan every run, so nothing is run')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): rd.main(set(ids))
    txt = buf.getvalue(); print(txt, end='')
    m = re.search(r'identical (\d+); unexpected differences (\d+)\s*$', txt); n_ok, n_bad = int(m.group(1)), int(m.group(2))

    import build_iwo_decks as bd  # noqa: E402  (the module object regress_all_decks and run_campaign use)
    import run_campaign as rc     # noqa: E402
    mx = {r['id']: r['campaign_entry'] for r in json.loads((PKG / 'analysis_2026-10-10_campaign' / 'campaign_matrix.json').read_text())['runs']}
    cols = {rid: [] for rid in sealed}
    for r in csv.DictReader(INDEX.open(newline='')):
        if r['run_id'] in sealed: cols[r['run_id']].append((r['label'], r['deck_sha256'], r['model_sha256']))   # input columns only
    for rid in sorted(sealed):
        s = inv[rid]; rows = cols[rid]
        idx_ok = (bool(rows) and {x[0] for x in rows} == {s['label']} and {x[1] for x in rows if x[1]} == {s['deck_sha256']}
                  and {x[2] for x in rows if x[2]} == {s['model_sha256']})
        e = mx.get(s['entry'])
        if e is None or e['label'] != s['label']:
            print(f'{rid}: SEALED, NOT CHECKED (matrix entry {s["entry"]} missing or its label differs from the inventory)'); n_bad += 1; continue
        bd.MODEL_FILE = s['model_file']
        gen_ok = sha(rc.current_deck_text(e, e['overrides'])) == s['deck_sha256'] and sha(rc.current_material_text(e['overrides'])) == s['model_sha256']
        print(f'{rid}: SEALED (directory not opened); RUN_INDEX label/deck_sha256/model_sha256 == inventory: {idx_ok}; current rebuild of '
              f'{s["entry"]} ({s["label"]}, {s["model_file"]}) == inventory deck/model sha256: {gen_ok}')
        ok = idx_ok and gen_ok; n_ok += ok; n_bad += (not ok)
    print(f'identical {n_ok}; unexpected differences {n_bad}')
    return 1 if n_bad else 0


if __name__ == '__main__':
    sys.exit(main())
