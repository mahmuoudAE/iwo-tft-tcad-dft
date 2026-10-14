"""Pilot A15 (aIO_0p8_s1): pick the restart geometry of a relax segment.

usage: python geomsel.py <relax.in> <relax.out>
Writes relax_next.in (relax.in with ATOMIC_POSITIONS = the chosen geometry) and prints one summary line.

A geometry is "electronically validated" only if its SCF converged (QE printed a '!' total energy for it).
Geometry 0 is the segment's input; geometry k >= 1 is the k-th ATOMIC_POSITIONS block QE printed (a BFGS trial
until its own SCF converges). The restart geometry is the validated geometry with the lowest energy, never an
unevaluated trial (Codex re-check, 2026-10-11). best_new=yes only if that geometry is not the input one.
"""
import sys

from qeio import replace_card

STOP = ('End', 'ATOMIC', 'CELL', 'Writing', 'number', 'new', 'Begin')


def main(inp, out):
    lines = open(out, errors='replace').read().splitlines()
    geoms = [None]          # index 0 = input geometry
    energy = {}
    cur, final, i = 0, False, 0
    while i < len(lines):
        s = lines[i].strip()
        if 'Begin final coordinates' in s:
            final = True
        if lines[i].startswith('!') and 'total energy' in s:
            energy[cur] = float(s.split('=')[1].split()[0])
        elif s.startswith('ATOMIC_POSITIONS') and not final:
            body, j = [], i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith(STOP):
                body.append('  ' + lines[j].strip())
                j += 1
            unit = s.replace('(', ' ').replace(')', ' ').replace('{', ' ').replace('}', ' ').split()
            unit = unit[1] if len(unit) > 1 else 'alat'
            geoms.append(['ATOMIC_POSITIONS ' + unit] + body)
            cur = len(geoms) - 1
            i = j
            continue
        i += 1
    text = open(out, errors='replace').read()
    scf_fail = text.count('convergence NOT achieved')
    fermi_warn = text.count('failed to find Fermi energy')
    iters = [l.split('in')[-1].split()[0] for l in lines if 'convergence has been achieved in' in l]
    if not energy:
        print(f'n_scf=0 n_geom={len(geoms)} best=none best_new=no scf_fail={scf_fail} fermi_warn={fermi_warn}')
        return
    best = min(energy, key=energy.get)
    e0 = energy.get(0)
    tin = open(inp).read()
    with open('relax_next.in', 'w') as f:
        f.write(tin if best == 0 else replace_card(tin, 'ATOMIC_POSITIONS', geoms[best]))
    print(f'n_scf={len(energy)} n_geom={len(geoms)} best={best} best_new={"yes" if best > 0 else "no"} '
          f'E0={e0} Ebest={energy[best]} scf_iters={",".join(iters)} scf_fail={scf_fail} fermi_warn={fermi_warn}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
