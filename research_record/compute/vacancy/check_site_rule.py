#!/usr/bin/env python3
"""H-L site-rule check: apply the frozen near/far rules to a relaxed In31WO48 and compare with the staged sites.

usage: python check_site_rule.py <relax.out of In31WO48> [build_facts.json]

The staged near and far cells (make_vac.py) were cut from the stage-4 relaxation of iwo_W24d (mv 0.01 Ry,
QE 7.5 CPU). The H-L In31WO48 relaxation (Gaussian 0.005 Ry, QE 7.3.1 GPU) runs with the same settings as the
vacancy cells. This script re-applies the H-L rules to that geometry once it has converged:
  near = the O with the shortest W-O bond; far = the O with the largest minimum-image distance to W.
Ties are distances within 1e-3 A (the same tolerance as make_vac.py); the atom order of In31WO48 is the
order of the staged relax.in, so index0 and QE numbers refer to the same atoms as in BUILD_REPORT.md.

Index conventions: index0 = 0-based (Python); qe1 = index0 + 1 = the atom number QE prints.
Exit code: 0 = both staged sites are still what the rule selects; 3 = near differs; 4 = far differs; 5 = both.
Needs only numpy.
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

TIE = 1e-3
IMG = np.array(list(itertools.product((-1, 0, 1), repeat=3)), float)


def read_relaxed(path):
    """Cell (A) and final crystal coordinates of a converged QE fixed-cell relax.

    The cell comes from CELL_PARAMETERS angstrom of the relax.in next to relax.out when present (exact);
    otherwise from the printed alat and crystal axes (alat has 4 decimals: ~2e-5 A on distances).
    """
    lines = Path(path).read_text(errors='replace').splitlines()
    if not any('Begin final coordinates' in l for l in lines):
        sys.exit(f'{path}: no "Begin final coordinates" block (relaxation not converged)')
    rin = Path(path).with_name('relax.in')
    cell = None
    if rin.exists():
        L = rin.read_text().splitlines()
        i = next((n for n, l in enumerate(L) if l.strip().startswith('CELL_PARAMETERS') and 'angstrom' in l), None)
        if i is not None:
            cell = np.array([[float(x) for x in L[i + k].split()[:3]] for k in (1, 2, 3)])
    if cell is None:
        alat = next(float(l.split('=')[1].split()[0]) for l in lines if 'lattice parameter (alat)' in l)
        i = next(n for n, l in enumerate(lines) if l.strip().startswith('crystal axes:'))
        cell = np.array([[float(x) for x in lines[i + k].split('(')[2].split(')')[0].split()] for k in (1, 2, 3)])
        cell *= alat * 0.529177210903                   # alat units -> bohr -> A (CODATA 2018 bohr)
    i = next(n for n, l in enumerate(lines) if 'Begin final coordinates' in l)
    j = next(n for n in range(i, len(lines)) if lines[n].strip().startswith('ATOMIC_POSITIONS'))
    if 'crystal' not in lines[j]:
        sys.exit(f'{path}: final ATOMIC_POSITIONS not in crystal units: {lines[j]}')
    sym, frac = [], []
    for l in lines[j + 1:]:
        s = l.split()
        if not s or s[0] == 'End':
            break
        sym.append(s[0])
        frac.append([float(x) for x in s[1:4]])
    return cell, sym, np.array(frac)


def dmic(cell, fi, fj):
    d = (fj - fi) - np.round(fj - fi)
    return min(float(np.linalg.norm((d + t) @ cell)) for t in IMG)


def main(out, facts_path):
    cell, sym, frac = read_relaxed(out)
    iW = sym.index('W')
    iO = [k for k, s in enumerate(sym) if s == 'O']
    d = {k: dmic(cell, frac[iW], frac[k]) for k in iO}
    order = sorted(iO, key=lambda k: d[k])
    dmin, dmax = d[order[0]], d[order[-1]]
    near_ties = [k for k in iO if d[k] - dmin < TIE]
    far_ties = [k for k in iO if dmax - d[k] < TIE]
    next_near = min(d[k] for k in iO if k not in near_ties)
    next_far = max(d[k] for k in iO if k not in far_ties)
    staged = json.loads(Path(facts_path).read_text())['selection']
    s_near, s_far = set(staged['near']['ties_index0']), set(staged['far']['ties_index0'])
    res = {
        'source': str(out),
        'a_A': round(float(cell[0, 0]), 7),
        'near_rule': {'index0': min(near_ties), 'qe1': min(near_ties) + 1, 'd_WO_A': round(dmin, 4),
                      'ties_index0': near_ties, 'ties_qe1': [k + 1 for k in near_ties],
                      'margin_A': round(next_near - dmin, 4)},
        'far_rule': {'index0': min(far_ties), 'qe1': min(far_ties) + 1, 'd_WO_A': round(dmax, 4),
                     'ties_index0': far_ties, 'ties_qe1': [k + 1 for k in far_ties],
                     'margin_A': round(dmax - next_far, 4)},
        'first_shell_index0_qe1_A': [[k, k + 1, round(d[k], 4)] for k in order[:6]],
        'staged_near_index0_qe1': [[k, k + 1] for k in sorted(s_near)],
        'staged_far_index0_qe1': [[k, k + 1] for k in sorted(s_far)],
        'near_same_as_staged': bool(set(near_ties) & s_near),
        'far_same_as_staged': bool(set(far_ties) & s_far),
    }
    print(json.dumps(res, indent=1))
    code = (0 if res['near_same_as_staged'] else 3) + (0 if res['far_same_as_staged'] else 4)
    return 5 if code == 7 else code


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    facts = sys.argv[2] if len(sys.argv) > 2 else Path(__file__).resolve().parent / 'build_facts.json'
    sys.exit(main(sys.argv[1], facts))
