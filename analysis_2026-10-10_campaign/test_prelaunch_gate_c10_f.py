"""Tests of prelaunch_gate_c10_f.py (register A48; NO launch; no repo file written except the temporary ./test_tmp_c10_f, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_f.py
In-process cases import the gate and give it the pinned D/E and C10 gate modules with patched inputs: synthetic register / decision log,
synthetic RUN_INDEX (run_id/label of the real rows up to run_0077 only; synthetic S1-06R/DIAG rows run_0078..run_0096, D/E rows run_0097..run_0101
and stage F rows above: no real row content beyond run_id and label is copied), a synthetic sealed-run inventory, a fake process list and
synthetic S3-12 deckbuild.out files (mobility summary only).
"""
import contextlib, csv, importlib.util, io, json, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; GATE = HERE / 'prelaunch_gate_c10_f.py'; DEG = HERE / 'prelaunch_gate_c10_de.py'; C10 = HERE / 'prelaunch_gate_c10.py'
TMP = HERE / 'test_tmp_c10_f'; PKG = HERE.parent
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G0 = load(GATE, 'gf_constants'); D0 = load(DEG, 'gde_constants'); C0 = load(C10, 'c10_constants')


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def logs(tag, heading=True, row=True, draft=False):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'
    h = ['### A47: PA-4 and PA-5 entries: T0r, T2a, T2b, S2-09, S2-10']
    if heading: h.append('### A48: stage F: PA-8 activation rule; S3-12, S3-27, S3-11, S3-13, S3-15, S3-14, S3-16, S3-10, S3-05, S3-06, S3-08, S3-09'
                         + (' (draft)' if draft else ''))
    r = ['| D-67 | x | A47 | x | x | IN FORCE |']
    if row: r.append('| D-68 | x | Register A48: PA-8, S3-12, S3-15, prelaunch_gate_c10_f.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(h) + '\n'); dec.write_text('\n'.join(r) + '\n'); return reg, dec


def prev_rows(drop_last=False):
    rows = []
    for k, e in enumerate(C0.LAUNCH_ORDER):
        rid = f'run_{78 + k:04d}'; lab = C0.LABEL[e]
        rows += [{'run_id': rid, 'label': lab, 'notes': 'STARTED synthetic'}, {'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}]
    for k, e in enumerate(D0.ORDER):
        rid = f'run_{97 + k:04d}'; lab = D0.LABEL[e]
        rows += [{'run_id': rid, 'label': lab, 'notes': 'STARTED synthetic'}, {'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}]
    return rows[:-2] if drop_last else rows


def f_row(rid, k, finish=True, deck=None):
    lab = G0.LABEL[k]; s = {'run_id': rid, 'label': lab, 'deck_sha256': deck or G0.DECK[k], 'model_sha256': G0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'}
    return [s] + ([{'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}] if finish else [])


def seq(keys, start=102, finish_last=True):
    out = []
    for i, k in enumerate(keys):
        out += f_row(f'run_{start + i:04d}', k, finish=finish_last or i < len(keys) - 1)
    return out


def index(tag, extra, drop_last=False, inv_skip=()):
    TMP.mkdir(exist_ok=True); p = TMP / f'idx_{tag}.csv'
    real = [(r['run_id'], r['label']) for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline='')) if int(r['run_id'][4:]) <= 77]
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for rid, lab in real: w.writerow({'run_id': rid, 'label': lab, 'notes': 'SYNTHETIC'})
        for row in prev_rows(drop_last) + extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    inv = {'runs': []}; of = {v: k for k, v in G0.LABEL.items()}
    for row in extra:
        if row.get('notes', '').startswith('STARTED') and row['label'] in of and row['run_id'] not in inv_skip:
            k = of[row['label']]
            inv['runs'].append({'run_id': row['run_id'], 'label': row['label'], 'entry': k, 'model_file': MODEL, 'deck_sha256': G0.DECK[k],
                                'model_sha256': G0.MATERIAL[k], 'reason': 'synthetic'})
    ip = TMP / f'inv_{tag}.json'; ip.write_text(json.dumps(inv)); return p, ip


SUMMARY = ('REGIONAL MOBILITY MODEL SUMMARY:\n\n  Region #1:\n\n    Model for Electrons:\n\n      {r1}\n        gamma0 = -0.31\n\n'
           '    Model for Holes:\n\n      Concentration Independent Mobility\n        mu  = 0.01\n\n  Region #2:\n\n    Model for Electrons:\n\n'
           '      {r2}\n\n    Model for Holes:\n\n      Concentration Independent Mobility\n\nContacts:\n{tail}Name  Num  Work fn\n'
           'ATLAS> solve init\n')
IG = 'Using IGZO.TOKYO low field mobility model.'
CI = 'Concentration Independent Mobility'


def s312_dir(runs, rid, r1=IG, r2=IG, tail='', write=True, heading=True):
    d = runs / f'{rid}_6p3_c10_s3_12_6p3'; d.mkdir(parents=True, exist_ok=True)
    if write:
        txt = SUMMARY.format(r1=r1, r2=r2, tail=tail)
        (d / 'deckbuild.out').write_text(('ATLAS> go atlas\n' + txt) if heading else 'ATLAS> go atlas\nnothing\n')
    return d


def case(name, want, idx_inv, reg_dec, runs, show=('GATE PASSED', 'NOTHING', 'GATE STOP', '[FAIL]', '[STOP]', '[INFO] S3-12')):
    g = load(GATE, 'gf_under_test'); D = load(DEG, 'gde_under_test'); C = load(C10, 'c10_under_test'); C.list_processes = lambda: []
    C.INDEX, C.INVENTORY = idx_inv; C.REGISTER, C.DECISIONS = reg_dec; D.c10_module = lambda: C; g.de_module = lambda: D; g.RUNS = runs
    os.chdir(PKG); buf = io.StringIO()
    with contextlib.redirect_stdout(buf): rc = g.main(['--check'])
    out = buf.getvalue(); [print('       ' + l) for l in out.splitlines() if l.startswith(show) or 'Next plan' in l]
    expect(name, rc, want); return out


def main():
    IGZO = ['S3-12', 'S3-27', 'S3-11', 'S3-13', 'S3-15', 'S3-14', 'S3-16']; TAILS = ['S3-10', 'S3-05', 'S3-06', 'S3-08', 'S3-09']
    try:
        L = logs('ok')
        ra = TMP / 'runs_active'; s312_dir(ra, 'run_0102')
        rn = TMP / 'runs_inactive'; s312_dir(rn, 'run_0102', r2=CI)
        rm = TMP / 'runs_missing'; s312_dir(rm, 'run_0102', write=False)
        rh = TMP / 'runs_nohead'; s312_dir(rh, 'run_0102', heading=False)
        rt = TMP / 'runs_tail'; dt = s312_dir(rt, 'run_0102', write=False)
        (dt / 'deckbuild.out').write_text('REGIONAL MOBILITY MODEL SUMMARY:\n  Region #1:\n    Model for Electrons:\n      ' + IG + '\nContacts:\n'
                                          '  Region #2:\n    Model for Electrons:\n      ' + IG + '\n')
        out = case('logged, no F run -> 0, campaign_C10_S3a_act', 0, index('none', []), L, ra)
        expect('  names S3a', 'Next plan config/campaign_C10_S3a_act.json: S3-12 (c10_s3_12_6p3), first run id run_0102' in out, True)
        case('not logged -> 1', 1, index('nolog', []), logs('no', heading=False, row=False), ra)
        case('draft heading -> 1', 1, index('draft', []), logs('draft', draft=True), ra)
        case('S3-12 unfinished -> 3', 3, index('unfin', seq(['S3-12'], finish_last=False)), L, ra)
        out = case('S3-12 ACTIVE -> 0, campaign_C10_S3b_igzo', 0, index('act', seq(['S3-12'])), L, ra)
        expect('  names S3b with 6 entries', 'Next plan config/campaign_C10_S3b_igzo.json: S3-27' in out and 'these 6 entries' in out, True)
        expect('  prints ACTIVE', 'activation (A48 (b); REGIONAL MOBILITY MODEL SUMMARY, electrons): ACTIVE' in out, True)
        out = case('S3-12 NOT_ACTIVE (region 2) -> 0, tails plan', 0, index('inact', seq(['S3-12'])), L, rn)
        expect('  names S3c (IGZO skipped)', 'Next plan config/campaign_C10_S3c_tails.json: S3-10' in out and 'NOT_ACTIVE' in out, True)
        out = case('S3-12 deckbuild.out missing -> UNVERIFIED -> tails plan', 0, index('miss', seq(['S3-12'])), L, rm)
        expect('  UNVERIFIED', ': UNVERIFIED' in out and 'campaign_C10_S3c_tails.json' in out, True)
        out = case('S3-12 summary heading absent -> UNVERIFIED -> tails plan', 0, index('nohead', seq(['S3-12'])), L, rh)
        expect('  UNVERIFIED (no heading)', ': UNVERIFIED' in out, True)
        out = case('reading stops at Contacts: (region 2 after it ignored) -> UNVERIFIED', 0, index('tail', seq(['S3-12'])), L, rt)
        expect('  UNVERIFIED kept', ': UNVERIFIED' in out and 'campaign_C10_S3c_tails.json' in out, True)
        case('S3-27 started although S3-12 NOT_ACTIVE -> 1', 1, index('bad27', seq(['S3-12', 'S3-27'])), L, rn)
        out = case('IGZO set done (ACTIVE) -> 0, tails plan with 5 entries', 0, index('igdone', seq(IGZO)), L, ra)
        expect('  names S3c with 5 entries', 'Next plan config/campaign_C10_S3c_tails.json: S3-10' in out and 'these 5 entries' in out, True)
        out = case('partial S3b (S3-27, S3-11 done) -> 0, S3b again for 4', 0, index('part', seq(['S3-12', 'S3-27', 'S3-11'])), L, ra)
        expect('  S3b names S3-13 first, 4 entries', 'campaign_C10_S3b_igzo.json: S3-13' in out and 'these 4 entries' in out, True)
        case('all done (ACTIVE) -> 4', 4, index('all', seq(IGZO + TAILS)), L, ra)
        case('all done (NOT_ACTIVE, IGZO skipped) -> 4', 4, index('alli', seq(['S3-12'] + TAILS)), L, rn)
        case('S3-11 before S3-27 -> 1', 1, index('ord', seq(['S3-12', 'S3-11'])), L, ra)
        case('S3-10 before S3-12 -> 1', 1, index('ord2', seq(['S3-10'])), L, ra)
        case('D/E not exhausted (S2-10 missing) -> 1', 1, index('de', [], drop_last=True), L, ra)
        case('wrong STARTED deck sha -> 1', 1, index('deck', f_row('run_0102', 'S3-12', deck='0' * 64)), L, ra)
        case('started F run missing from the inventory -> 1', 1, index('inv', seq(['S3-12']), inv_skip=('run_0102',)), L, ra)
        case('two run ids for S3-12 -> 1', 1, index('dup', seq(['S3-12', 'S3-12'])), L, ra)
        case('unknown label above run_0077 -> 1', 1, index('unk', [{'run_id': 'run_0102', 'label': 'c10_s3_24_2p0', 'notes': 'STARTED'}]), L, ra)
        # parser units
        expect('unit: activation ACTIVE', G0.activation(ra / 'run_0102_6p3_c10_s3_12_6p3' / 'deckbuild.out')[0], 'ACTIVE')
        expect('unit: region 2 Concentration Independent -> NOT_ACTIVE', G0.activation(rn / 'run_0102_6p3_c10_s3_12_6p3' / 'deckbuild.out')[0], 'NOT_ACTIVE')
        ru = TMP / 'runs_r2missing'; d = ru / 'x'; d.mkdir(parents=True, exist_ok=True)
        (d / 'deckbuild.out').write_text('REGIONAL MOBILITY MODEL SUMMARY:\n  Region #1:\n    Model for Electrons:\n      ' + IG + '\nContacts:\n')
        expect('unit: region 2 absent -> UNVERIFIED', G0.activation(d / 'deckbuild.out')[0], 'UNVERIFIED')
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
