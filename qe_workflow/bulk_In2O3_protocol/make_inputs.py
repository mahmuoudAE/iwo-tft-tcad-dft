"""Write the convergence-test inputs for the 40-atom primitive bixbyite In2O3 cell taken from structure_primitive.json
(built and verified by build_structure.py; the earlier prepared 80-atom input was defective: 2 symmetry operations, forces 2.9 Ry/Bohr).
Primitive bcc vectors a/2(-1,1,1), a/2(1,-1,1), a/2(1,1,-1) (ibrav=3 convention of pw.x)."""
import re
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
import json
S = json.loads((H / 'structure_primitive.json').read_text())   # verified by build_structure.py (Ia-3, 24 ops, In-O 2.12-2.21 A)
a = 10.117
prim = [(sp, f) for sp, f in zip(S['species'], S['frac'])]
pos = '\n'.join(f'{s} {f[0]:.10f} {f[1]:.10f} {f[2]:.10f}' for s, f in prim)
cellp = '\n'.join(' '.join(f'{x:.10f}' for x in v) for v in S['lattice_A'])
def inp(calc, ecut, k, prefix, extra=''):
    return f"""&CONTROL
  calculation = '{calc}', prefix = '{prefix}', outdir = './tmp', pseudo_dir = '../pseudo',
  tstress = .true., tprnfor = .true., etot_conv_thr = 1.0d-5, forc_conv_thr = 1.0d-4 {extra}
/
&SYSTEM
  ibrav = 0, nat = 40, ntyp = 2,
  ecutwfc = {ecut}, ecutrho = {8 * ecut}, occupations = 'fixed', nbnd = 190
/
&ELECTRONS
  conv_thr = 1.0d-9, mixing_beta = 0.4
/
&IONS
/
&CELL
  press_conv_thr = 0.2
/
ATOMIC_SPECIES
In 114.818 In.pbe-dn-kjpaw_psl.1.0.0.UPF
O  15.999  O.pbe-n-kjpaw_psl.1.0.0.UPF
CELL_PARAMETERS angstrom
{cellp}
ATOMIC_POSITIONS crystal
{pos}
K_POINTS automatic
{k} {k} {k} 0 0 0
"""
for e in (50, 60, 71, 85):
    (H / f'scf_ecut{e}_k3.in').write_text(inp('scf', e, 3, f'ec{e}'))
for k in (2, 4):
    (H / f'scf_ecut71_k{k}.in').write_text(inp('scf', 71, k, f'k{k}'))
(H / 'template_vcrelax.in').write_text(inp('vc-relax', 'ECUT', 'KGRID', 'vcr'))
print('a =', a, 'A; primitive atoms:', len(prim))
