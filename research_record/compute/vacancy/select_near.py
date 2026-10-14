#!/usr/bin/env python3
"""H-L near-site selection (register amendment A19), frozen before any H-L job was submitted.

usage: python select_near.py <relax.out of the H-L-relaxed In31WO48>

A19: both near candidates are computed, In31WO47_near (O index0 30 removed) and In31WO47_near72 (O index0 72
removed). The registered DeltaE_local uses whichever candidate is the shortest W-O bond in the H-L-relaxed
In31WO48. This script applies that rule to the converged relax.out and also reports the far ordering.

Geometry: the 'Begin final coordinates' block (crystal coordinates). Distances: minimum image in the fixed cubic
cell a = 10.3060902 A (H-L: the cell is fixed; the alat and crystal axes printed by QE are checked against it).
The relaxation counts only if QE printed 'bfgs converged' (A19: QE prints final coordinates after a BFGS failure too).

Rule, applied as written:
  - the global shortest W-O distance over all 48 O, dmin; tied O = those within 1e-3 A of dmin (the tie tolerance of
    make_vac.py and check_site_rule.py); the lowest index among the tied O is selected;
  - selected O in {30, 69} (C2 pair of the near cell)   -> registered = In31WO47_near   (O index0 30, QE #31);
  - selected O in {72, 73} (C2 pair of the near72 cell) -> registered = In31WO47_near72 (O index0 72, QE #73);
  - anything else -> no computed candidate is the registered site (exit 3).
  The other candidate is the sensitivity. A within-pair split > 1e-3 A (broken C2) is flagged.
Far (A19): the far site stays O32 (pair O32/O33); if the pair O29/O70 (or any other O) is now farther, the far result
carries a flag; no extra run.

Index conventions: index0 = 0-based position in the 80-atom list (Python); QE # = index0 + 1 (QE's atom number).
Exit codes: 0 = a registered candidate was selected; 2 = input not usable (not converged, wrong cell or atoms);
3 = the shortest W-O bond is neither candidate pair. Standard library only.
"""
import hashlib
import math
import sys

A = 10.3060902                     # A, fixed cubic cell of all H-L cells (stage-2 PBE host)
BOHR_A = 0.529177210903
TIE = 1e-3                         # A
W_INDEX0 = 4                       # W on 24d, QE #5
NEAR_PAIR, NEAR72_PAIR = (30, 69), (72, 73)
FAR_PAIR, FAR_NEXT_PAIR = (32, 33), (29, 70)
REPORT = (30, 69, 72, 73)
CELLS = {30: 'In31WO47_near', 72: 'In31WO47_near72'}


def die(msg):
    print('INVALID INPUT: ' + msg)
    sys.exit(2)


def q(k):
    return f'O index0 {k} (QE #{k + 1})'


def read(path):
    raw = open(path, 'rb').read()
    text = raw.decode(errors='replace')
    lines = text.splitlines()
    if 'bfgs converged' not in text:
        die("no 'bfgs converged' in relax.out: the H-L In31WO48 relaxation has not converged (A19)")
    if 'Begin final coordinates' not in text or 'End final coordinates' not in text:
        die("no complete 'Begin/End final coordinates' block")
    alat = [float(l.split('=')[1].split()[0]) for l in lines if 'lattice parameter (alat)' in l]
    if alat and abs(alat[0] * BOHR_A - A) > 1e-4:
        die(f'alat {alat[0]} bohr = {alat[0] * BOHR_A:.6f} A differs from the fixed cell a = {A} A')
    ax = next((n for n, l in enumerate(lines) if l.strip().startswith('crystal axes:')), None)
    if ax is not None:
        rows = [[float(x) for x in lines[ax + k].split('(')[2].split(')')[0].split()] for k in (1, 2, 3)]
        if any(abs(rows[i][j] - (1.0 if i == j else 0.0)) > 1e-6 for i in range(3) for j in range(3)):
            die(f'crystal axes are not the cubic identity: {rows}')
    i = next(n for n, l in enumerate(lines) if 'Begin final coordinates' in l)
    j = next(n for n in range(i, len(lines)) if lines[n].strip().startswith('ATOMIC_POSITIONS'))
    if 'crystal' not in lines[j]:
        die(f'final ATOMIC_POSITIONS not in crystal units: {lines[j].strip()}')
    sym, frac = [], []
    for l in lines[j + 1:]:
        s = l.split()
        if not s or s[0] == 'End':
            break
        sym.append(s[0])
        frac.append([float(x) for x in s[1:4]])
    if len(sym) != 80 or sym.count('W') != 1 or sym.count('O') != 48 or sym.count('In') != 31:
        die(f'expected In31 W1 O48 (80 atoms), got {len(sym)} atoms')
    if sym[W_INDEX0] != 'W':
        die(f'W is not at index0 {W_INDEX0}')
    for k in REPORT + FAR_PAIR + FAR_NEXT_PAIR:
        if sym[k] != 'O':
            die(f'index0 {k} is {sym[k]}, not O')
    bfgs = [l.strip() for l in lines if 'bfgs converged' in l][-1]
    efin = [l.strip() for l in lines if 'Final energy' in l]
    return sym, frac, bfgs, (efin[-1] if efin else 'n/a'), hashlib.sha256(raw).hexdigest()


def d_mic(f1, f2):
    v = [(b - a) - round(b - a) for a, b in zip(f1, f2)]     # cubic cell: rounding gives the minimum image
    return A * math.sqrt(sum(x * x for x in v))


def main(path):
    sym, frac, bfgs, efin, digest = read(path)
    iO = [k for k, s in enumerate(sym) if s == 'O']
    d = {k: d_mic(frac[W_INDEX0], frac[k]) for k in iO}
    print(f'file: {path}')
    print(f'sha256: {digest}')
    print(f'{bfgs}; {efin}')
    print(f'cell: cubic, a = {A} A (fixed); W = index0 {W_INDEX0} (QE #{W_INDEX0 + 1}); index0 = 0-based, QE # = index0+1')
    print('W-O distances of the candidates:')
    for k in REPORT:
        print(f'  {q(k):24s} {d[k]:.5f} A')
    order = sorted(iO, key=lambda k: (d[k], k))
    dmin = d[order[0]]
    tied = [k for k in iO if d[k] - dmin < TIE]
    sel = min(tied)
    print('shortest W-O bonds: ' + ', '.join(f'{k}/#{k + 1} {d[k]:.5f}' for k in order[:6]) + ' (index0/QE#, A)')
    print(f'global shortest: {q(order[0])} {dmin:.5f} A; tied within {TIE} A: index0 {tied} = QE # {[k + 1 for k in tied]}')
    for name, pair in (('near', NEAR_PAIR), ('near72', NEAR72_PAIR)):
        split = abs(d[pair[0]] - d[pair[1]])
        if split > TIE:
            print(f'FLAG: {name} pair index0 {pair} split by {split:.5f} A (> {TIE} A): C2 equivalence broken')
    gap = min(d[k] for k in NEAR72_PAIR) - min(d[k] for k in NEAR_PAIR)
    print(f'gap d(O72 pair) - d(O30 pair) = {gap:+.5f} A (stage-4 value +0.0104)')
    if any(k in NEAR_PAIR for k in tied) and any(k in NEAR72_PAIR for k in tied):
        print(f'FLAG: TIE between the O30 and O72 pairs within {TIE} A; lowest index rule selects index0 {sel}')
    # A20: a symmetry partner (69 for 30, 73 for 72) stands for the computed cell only while the pair is unsplit
    # (|d1 - d2| <= TIE); if the C2 equivalence broke and the uncomputed partner is the shortest, nothing is substituted.
    reg = None
    for pair, r, o in ((NEAR_PAIR, 30, 72), (NEAR72_PAIR, 72, 30)):
        if sel == r or (sel in pair and abs(d[pair[0]] - d[pair[1]]) <= TIE):
            reg, other = r, o
    if reg is None and (sel in NEAR_PAIR or sel in NEAR72_PAIR):
        print(f'FLAG: the shortest bond is the uncomputed partner {q(sel)} of a split pair: no substitution (A20)')
    # far ordering
    far_order = sorted(iO, key=lambda k: (-d[k], k))
    dmax = d[far_order[0]]
    far_tied = [k for k in iO if dmax - d[k] < TIE]
    print('far: ' + ', '.join(f'{q(k)} {d[k]:.5f} A' for k in FAR_PAIR + FAR_NEXT_PAIR))
    print('largest W-O: ' + ', '.join(f'{k}/#{k + 1} {d[k]:.5f}' for k in far_order[:6]) + ' (index0/QE#, A)')
    dfar, dnext = min(d[k] for k in FAR_PAIR), max(d[k] for k in FAR_NEXT_PAIR)
    if min(far_tied) in FAR_PAIR:
        print(f'FAR_ORDER = kept: O32/O33 (QE #33/#34) {dfar:.5f} A > O29/O70 (QE #30/#71) {dnext:.5f} A, '
              f'margin {dfar - dnext:+.5f} A')
    else:
        print(f'FAR_ORDER = REVERSED (A19 flag, no extra run): largest is {q(min(far_tied))} {dmax:.5f} A; '
              f'O32/O33 {dfar:.5f} A, O29/O70 {dnext:.5f} A')
    if reg is None:
        print(f'REGISTERED_NEAR = NONE: the shortest W-O bond is {q(sel)}, neither computed candidate (exit 3)')
        sys.exit(3)
    print(f'REGISTERED_NEAR = {CELLS[reg]} ({q(reg)}, W-O {d[reg]:.5f} A); '
          f'sensitivity = {CELLS[other]} ({q(other)}, W-O {d[other]:.5f} A)')
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
