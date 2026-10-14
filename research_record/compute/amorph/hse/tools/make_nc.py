#!/usr/bin/env python3
"""A23 (ii)/(iii): NC (SG15) single-point inputs, HSE06 and PBE, at identical settings (standard library only).

usage: python3 make_nc.py --src <relax.in> [--relax-out <relax.out>] --k N --nbnd NB --out DIR [--prefix-file P]

--src        the relaxation input that defines the cell, the species and the atom order (fixed-cell relaxation)
--relax-out  the converged relaxation output; its 'Begin final coordinates' block gives the positions. Refused unless
             it contains 'bfgs converged' and 'End final coordinates'. Without it, preview inputs at the --src geometry
             are written (preview_scf_pbe.in / preview_scf_hse.in) for dry checks only.
Writes DIR/scf_pbe.in and DIR/scf_hse.in (or the preview_ files).

Settings = the 2026-10-01 HSE check (RESULTS_LOG): SG15 ONCV 1.2, ecutwfc 80 / ecutrho 320 Ry, HSE06 with
nqx 1x1x1 and ecutfock 160 Ry, conv_thr 1e-9, beta 0.3, electron_maxstep 150, verbosity 'high'; A23: Gaussian
0.005 Ry, spin-unpolarised, k as given (Gamma = 1). Declared difference from 2026-10-01: tstress off (the stress
took 3.3 of the 4.0 h of the 96-atom slab HSE run and is not used here).
"""
import argparse
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ.get('IWO_COMMON', str(Path.home() / 'iwo_amorph' / 'common')))
import qeio  # noqa: E402  (final_geometry, replace_card)

NC_PP = {'In': 'In_ONCV_PBE-1.2.upf', 'O': 'O_ONCV_PBE-1.2.upf', 'W': 'W_ONCV_PBE-1.2.upf'}
NC_VAL = {'In': 13, 'O': 6, 'W': 28}          # SG15 z_valence (W includes 4f14 5s2 5p6 -> 28)
MASS = {'In': 114.818, 'O': 15.999, 'W': 183.84}
HSE = "  input_dft = 'hse', nqx1 = 1, nqx2 = 1, nqx3 = 1, ecutfock = 160"

TEMPLATE = """&CONTROL
  calculation = 'scf', prefix = '{tag}', outdir = './tmp', pseudo_dir = './pseudo'
  verbosity = 'high', tprnfor = .true., max_seconds = 1.0d8
/
&SYSTEM
  ibrav = 0, nat = {nat}, ntyp = {ntyp}, ecutwfc = 80, ecutrho = 320
  occupations = 'smearing', smearing = 'gaussian', degauss = 0.005
  nbnd = {nbnd}
{hse}/
&ELECTRONS
  conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 150
/
ATOMIC_SPECIES
{species}
{cell}

K_POINTS automatic
  {k} {k} {k} 0 0 0

{positions}

"""


def card(lines, key):
    i = next(n for n, l in enumerate(lines) if l.strip().startswith(key))
    body = []
    for l in lines[i + 1:]:
        s = l.strip()
        if not s or s.startswith(('ATOMIC_', 'CELL_', 'K_POINTS', '&', '/')):
            break
        body.append(s)
    return lines[i].strip(), body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--relax-out')
    ap.add_argument('--k', type=int, required=True)
    ap.add_argument('--nbnd', type=int, required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    lines = Path(a.src).read_text().splitlines()
    _, sp_body = card(lines, 'ATOMIC_SPECIES')
    species = [l.split()[0] for l in sp_body]
    head, cell_body = card(lines, 'CELL_PARAMETERS')
    if 'angstrom' not in head:
        raise SystemExit(f'{a.src}: CELL_PARAMETERS must be in angstrom ({head})')
    cell = ['CELL_PARAMETERS angstrom'] + ['  ' + l for l in cell_body[:3]]
    pos_head, pos_body = card(lines, 'ATOMIC_POSITIONS')
    order = [l.split()[0] for l in pos_body]
    pos = [pos_head] + ['  ' + l for l in pos_body]
    prefix = 'preview_'
    if a.relax_out:
        text = Path(a.relax_out).read_text(errors='replace')
        if 'bfgs converged' not in text or 'End final coordinates' not in text:
            raise SystemExit(f"REFUSED: {a.relax_out} lacks 'bfgs converged' / 'End final coordinates'")
        new_cell, new_pos = qeio.final_geometry(text)
        if new_cell is not None:
            cell = new_cell
        got = [l.split()[0] for l in new_pos[1:]]
        if got != order:
            raise SystemExit(f'REFUSED: atom order/species in {a.relax_out} differ from {a.src}')
        if new_pos[0].split()[1] != pos_head.replace('(', ' ').replace(')', ' ').replace('{', ' ').replace('}', ' ').split()[1]:
            print(f'note: position unit {new_pos[0]} (source {pos_head})')
        pos = new_pos
        prefix = ''
    missing = sorted(set(order) - set(NC_PP))
    if missing:
        raise SystemExit(f'no NC pseudopotential mapped for {missing}')
    nel = sum(NC_VAL[s] for s in order)
    sp_lines = '\n'.join(f'  {s} {MASS[s]} {NC_PP[s]}' for s in species)
    out = Path(a.out)
    for tag in ('pbe', 'hse'):
        txt = TEMPLATE.format(tag=tag, nat=len(order), ntyp=len(species), nbnd=a.nbnd,
                              hse=(HSE + '\n') if tag == 'hse' else '', species=sp_lines, cell='\n'.join(cell),
                              k=a.k, positions='\n'.join(pos))
        (out / f'{prefix}scf_{tag}.in').write_text(txt)
    print(f'{out}/{prefix}scf_{{pbe,hse}}.in: nat {len(order)}, species {species}, NC electrons {nel}, '
          f'nbnd {a.nbnd} (>= 1.2 x N_el/2 = {math.ceil(0.6 * nel)}), k {a.k}x{a.k}x{a.k}'
          + ('' if a.relax_out else ' [PREVIEW at the source geometry]'))


if __name__ == '__main__':
    main()
