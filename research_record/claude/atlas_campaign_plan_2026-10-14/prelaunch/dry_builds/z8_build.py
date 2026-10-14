"""Z8 dry builds (no launch): branch-D decks through campaign_tools.entry_deck (= run_atlas.execute deck path) + mesh-line emulator."""
import json, sys, difflib, re
from pathlib import Path
PKG = Path(r'C:/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG / 'analysis_2026-10-10_campaign')); sys.path.insert(0, str(OUT))
import campaign_tools as ct, grade
RUNS = PKG / 'results' / 'runs'
ex67 = json.loads((RUNS / 'run_0067_2p0_c10_s0_02_2p0' / 'execution.json').read_text())
ex66 = json.loads((RUNS / 'run_0066_2p0_c10_s0_02_2p0' / 'execution.json').read_text())
diagb = {r['id']: r for r in json.loads((PKG / 'config' / 'campaign_C10_DIAGb.json').read_text())['runs']}
GT = 'solver.physics_options.gate_tunnelling.'
b67 = ex67['overrides']; b66 = ex66['overrides'] + [GT + 'qt_mesh=1', GT + 'exclude_near_sd=0']
s211 = diagb['S2-11']['overrides']
mb = 'newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-21'
decks = {
 'REF_run0067': b67, 'REF_run0066': b66, 'REF_S2-11_run0076form': s211,
 'T1a': [o for o in s211 if 'oxide_mesh_factor' not in o] + [GT + 'oxide_mesh_factor=0.25'],
 'T2a': b66 + [GT + 'qt_point_nm=0.25'],
 'T2b': b66 + [GT + 'qt_point_nm=0.25', GT + 'qt_slice_um=0.1'],
 'T0r_tol': b67 + ['solver.method_base=' + mb, 'solver.strict_acceptance.cr_toler_A=1e-19'],
}
texts = {}
for k, ov in decks.items():
    texts[k], _ = ct.entry_deck({'id': k, 'thickness': 2.0, 'overrides': ov}, ct.V3)
    (OUT / f'{k}.in').write_text(texts[k], encoding='ascii'); (OUT / f'{k}_overrides.json').write_text(json.dumps(ov, indent=1))
# T2a-E: generator output with the run_0066 enclosure restored (HAND EDIT, not generator output; proposal only)
t2e = texts['T2a'].replace('qty.mesh loc=-0.00025 spac=0.00025', 'qty.mesh loc=-0.0005 spac=0.00025').replace('qty.mesh loc=0.01725 spac=0.00025', 'qty.mesh loc=0.0175 spac=0.00025')
texts['T2a-E_handedit'] = t2e; (OUT / 'T2a-E_handedit.in').write_text(t2e, encoding='ascii')
# regression of the reference rebuilds against the launched decks (statements only)
reg = {}
for k, r in (('REF_run0067', 'run_0067_2p0_c10_s0_02_2p0'), ('REF_run0066', 'run_0066_2p0_c10_s0_02_2p0')):
    a = ct.statements((RUNS / r / 'device.in').read_text()); b = ct.statements(texts[k]); reg[k] = (a == b, len(a), [l for l in difflib.unified_diff(a, b, lineterm='', n=0)][:20])
pairs = {'T1a': 'REF_S2-11_run0076form', 'REF_S2-11_run0076form': 'REF_run0067', 'T2a': 'REF_run0066', 'T2b': 'REF_run0066', 'T2a-E_handedit': 'REF_run0066', 'T0r_tol': 'REF_run0067'}
diffs = {}
for k, ref in pairs.items():
    d = list(difflib.unified_diff(texts[ref].splitlines(), texts[k].splitlines(), f'{ref}.in', f'{k}.in', lineterm='', n=0))
    (OUT / f'diff_{k}_vs_{ref}.diff').write_text('\n'.join(d) + '\n'); diffs[k] = d
    sd = list(difflib.unified_diff(ct.statements(texts[ref]), ct.statements(texts[k]), lineterm='', n=0))
    diffs[k + '__stmts'] = [l for l in sd if l[:1] in '+-' and l[:3] not in ('+++', '---')]
# mesh statistics (emulator CALCULATED; validated on run_0067 82 y / 117 x lines and run_0062 117 x 117)
LAY = {'Air': (-0.072, -0.002), 'IWO': (-0.002, 0.0), 'Al2O3': (0.0, 0.002), 'HfO2': (0.002, 0.017), 'Conductor': (0.017, 0.067)}
stats = {}
for k, t in texts.items():
    y = grade.lines(grade.parse(t, 'y'), 'A'); x = grade.lines(grade.parse(t, 'x'), 'A')
    st = {'x_lines': len(x), 'y_lines': len(y), 'nodes': len(x) * len(y), 'layers': {}}
    for n, (lo, hi) in LAY.items():
        yy = [v for v in y if lo - 1e-12 <= v <= hi + 1e-12]; dy = [b - a for a, b in zip(yy, yy[1:])]
        st['layers'][n] = {'y_lines_incl_faces': len(yy), 'y_intervals': len(dy), 'nodes_incl_faces': len(yy) * len(x),
                           'dy_min_nm': round(min(dy) * 1e3, 4), 'dy_max_nm': round(max(dy) * 1e3, 4)}
    st['interfaces_um'] = {'air/IWO(top)': -0.002, 'IWO r1/r2': -0.00025, 'IWO/Al2O3': 0.0, 'Al2O3/HfO2': 0.002, 'HfO2/Conductor(gate)': 0.017}
    st['interfaces_on_mesh'] = all(any(abs(v - c) < 1e-12 for v in y) for c in (-0.002, -0.00025, 0.0, 0.002, 0.017))
    st['mesh_lines'] = [l for l in t.splitlines() if re.match(r'(x|y|qtx|qty)\.mesh', l)]
    qy = [float(v) for v in re.findall(r'^qty\.mesh loc=(\S+)', t, re.M)]; qx = [float(v) for v in re.findall(r'^qtx\.mesh loc=(\S+)', t, re.M)]
    qs = re.findall(r'^qt([xy])\.mesh loc=\S+ spac=(\S+)', t, re.M)
    if qy:
        sx = float([s for a, s in qs if a == 'x'][0]); sy = float([s for a, s in qs if a == 'y'][0])
        st['qt'] = {'y_range_um': [min(qy), max(qy)], 'x_range_um': [min(qx), max(qx)], 'encloses_oxide_strictly': min(qy) < 0 and max(qy) > 0.017 and min(qx) <= 0 and max(qx) >= 24,
                    'overextension_nm': [round(-min(qy) * 1e3, 4), round((max(qy) - 0.017) * 1e3, 4)],
                    'qt_points': (round((max(qx) - min(qx)) / sx) + 1) * (round((max(qy) - min(qy)) / sy) + 1), 'grid': f'{round((max(qx)-min(qx))/sx)+1} x {round((max(qy)-min(qy))/sy)+1}'}
    else: st['qt'] = None
    st['checks'] = {'qtnlsc.el': 'qtnlsc.el' in t, 'qtnl.derivs': 'qtnl.derivs' in t, 'exclude_near_SD': t.count('exclude_near\n') + t.count(' exclude_near') >= 2 and 'contact name=source exclude_near' in t,
                    'oxide_barriers': re.findall(r'^material region=[34] affinity.*$', t, re.M), 'method': re.findall(r'^method .*\n.*$', t, re.M)}
    stats[k] = st
(OUT / 'z8_stats.json').write_text(json.dumps({'regression': reg, 'stats': stats, 'stmt_diffs': {k: v for k, v in diffs.items() if k.endswith('__stmts')}}, indent=1))
for k, st in stats.items():
    print(k, st['x_lines'], 'x', st['y_lines'], '=', st['nodes'], {n: (v['y_intervals'], v['dy_min_nm'], v['dy_max_nm']) for n, v in st['layers'].items()}, st['qt'], st['interfaces_on_mesh'])
print('REG', {k: v[:2] for k, v in reg.items()})
for k in pairs: print('==', k, diffs[k + '__stmts'])
