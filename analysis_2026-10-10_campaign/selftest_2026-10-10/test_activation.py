"""Read-only test of the fixed activation parser: real run_0040 / run_0058 outputs, with requested options injected through
fake execution.json overrides in scratchpad copies. Shows the four review cases (a)-(d) and the true-negative baseline."""
import csv, json, shutil, sys
from pathlib import Path
PKG = Path(r'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1')
sys.path.insert(0, str(PKG / 'analysis_2026-10-10_campaign'))
import post_run_checks as pc
SCR = Path(__file__).resolve().parent / 'act_test'
if SCR.exists(): shutil.rmtree(SCR)
SCR.mkdir()
R40 = PKG / 'results/runs/run_0040_13p2_recal_dos384_13p2'; R58 = PKG / 'results/runs/run_0058_2p0_v2_anchor_2p0'
OUT40 = (R40 / 'deckbuild.out').read_text(errors='replace'); OUT58 = (R58 / 'deckbuild.out').read_text(errors='replace')
P = 'solver.physics_options.'

def mk(name, src, overrides, ig_scale=None, ig_add=None):
    d = SCR / name; d.mkdir()
    ex = json.loads((src / 'execution.json').read_text()); ex['overrides'] = list(ex.get('overrides', [])) + overrides
    (d / 'execution.json').write_text(json.dumps(ex)); shutil.copy(src / 'material_model_used.json', d / 'material_model_used.json'); shutil.copy(src / 'device.in', d / 'device.in')
    rows = list(csv.DictReader((src / 'terminal_currents.csv').open()))
    for r in rows:
        if ig_add is not None: r['ig_raw_A'] = str(float(r['ig_raw_A']) + ig_add(float(r['vg_V'])))
    with (d / 'terminal_currents.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return d, ex

def show(label, run, ex, out, gc=None, mf='config/iwo_material_model.yaml'):
    ex['model_file'] = mf; a = pc.activation(run, ex, out, gc)
    print(f'{label:58s} -> {a["status"]:20s}', {k: v['state'] for k, v in a['evidence'].items()})
    return a

d, ex = mk('base40', R40, []); show('baseline run_0040 (V1, no option)', d, ex, OUT40)
d, ex = mk('base58', R58, ['solver.tmun=0']); show('baseline run_0058 (V2, tmun=0 expected?)', d, ex, OUT58, mf='config/iwo_material_model_v2.yaml')
# (a) BQP requested; the header comment '# [B] OPTION BQP' is repeated before 'go atlas' without the ATLAS> prefix
outA = OUT40.replace('#==============================================================================\ngo atlas', '# [B] OPTION BQP = ngamma 1.2 | bqp | PDF p.835\n#==============================================================================\ngo atlas', 1)
assert '# [B] OPTION BQP' in outA
d, ex = mk('bqp', R40, [P + 'quantum.model=bqp'])
show('(a) BQP requested, only the header comment mentions BQP', d, ex, outA)
outA2 = outA.replace('REGIONAL MODEL FLAGS:', 'Bohm Quantum Potential model: ngamma 1.2 alpha 0.5\nREGIONAL MODEL FLAGS:', 1)
show('(a2) same + a solver-printed Bohm line (synthetic)', d, ex, outA2)
# (b) in-solver strip requested on the baseline output (regions 8-10 are its electrodes)
d, ex = mk('strip', R40, [P + 'strip.mode=in_solver'])
show('(b) in-solver strip requested, regions 8-10 are electrodes', d, ex, OUT40)
# (c) IGZO.TOKYO requested: summary missing / real summary (Concentration Independent)
d, ex = mk('igzo', R40, [P + 'mobility.model=igzo_tokyo'])
i0 = OUT40.index('REGIONAL MOBILITY MODEL SUMMARY'); i1 = OUT40.index('Contacts:')
show('(c) IGZO requested, mobility summary missing', d, ex, OUT40[:i0] + OUT40[i1:])
show('(c2) IGZO requested, summary says Concentration Independent', d, ex, OUT40)
# (d) QTNLSC + ITAT in one deck, gate currents synthetic (the real run has I_G = 0)
q = [P + 'gate_tunnelling.enabled=1', P + 'gate_tunnelling.model=qtnlsc', P + 'gate_tunnelling.set=nominal']
dc, exc = mk('ctrl_qtnlsc', R40, q, ig_add=lambda v: -1e-22 * (abs(v) + 1))
d, ex = mk('qt_itat', R40, q + [P + 'oxide_tat.enabled=1', P + 'oxide_tat.poisson=0'], ig_add=lambda v: -1e-22 * (abs(v) + 1))
show('(d) QTNLSC+ITAT, no --gate-control', d, ex, OUT40)
show('(d2) QTNLSC+ITAT, control I_G identical (ITAT adds nothing)', d, ex, OUT40, dc)
d3, ex3 = mk('qt_itat2', R40, q + [P + 'oxide_tat.enabled=1', P + 'oxide_tat.poisson=0'], ig_add=lambda v: -1e-22 * (abs(v) + 1) - 1e-15 * abs(v))
show('(d3) QTNLSC+ITAT, I_G larger than the control', d3, ex3, OUT40, dc)
show('(d4) single model QTNLSC with nonzero I_G', dc, exc, OUT40)
dz, exz = mk('qt_zero', R40, q)
show('(d5) single model QTNLSC with I_G exactly 0', dz, exz, OUT40)

dt, ext = mk('ctrl_with_tat', R40, q + [P + 'oxide_tat.enabled=1'], ig_add=lambda v: -1e-22 * (abs(v) + 1))
show('(d6) QTNLSC+ITAT, control also has TAT ON (invalid control)', d3, ex3, OUT40, dt)
import json as _j; m=_j.loads((dc / 'material_model_used.json').read_text()); m['traps']['fixed_interface_charge_Qf_cm2']['value']=0; (dc / 'material_model_used.json').write_text(_j.dumps(m))
show('(d7) QTNLSC+ITAT, control with a different material model', d3, ex3, OUT40, dc)
