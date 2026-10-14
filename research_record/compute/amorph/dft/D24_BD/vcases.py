"""Independent D-24 B cases cut from real QE 7.3.1 outputs (verifier, not the builder's generator).

usage: python3 vcases.py <slab2.out> <aIO_0p7_s1_s0.out or -> <outdir>
Writes <outdir>/<case>.out and <outdir>/expect.tsv: case status guard expected_geometry_rows_file|-
Geometry bookkeeping is done here by splitting the text on ATOMIC_POSITIONS headers (different code path from geomsel).
"""
import os
import re
import sys

EN = re.compile(r'^!+\s+total energy\s+=\s+(-?[0-9.]+) Ry', re.M)


def parse(text):
    """-> list of (rows, energy|None): index 0 = input geometry (rows None)."""
    body = text.split('Begin final coordinates')[0]
    parts = re.split(r'^ATOMIC_POSITIONS.*$', body, flags=re.M)
    geoms = []
    for k, p in enumerate(parts):
        rows = None
        if k > 0:
            rows = []
            for l in p.splitlines()[1:] if p.startswith('\n') else p.splitlines():
                if not l.strip():
                    if rows:
                        break
                    continue
                if not re.match(r'^\s*[A-Z][a-z]?\d*\s+-?\d', l):
                    break
                rows.append(l.split()[:4])
        e = EN.findall(p)
        geoms.append((rows, float(e[0]) if e else None))
    return geoms


def best(geoms):
    v = [(e, k) for k, (r, e) in enumerate(geoms) if e is not None]
    return min(v)[1] if v else None


def lines_upto(lines, pred, nth):
    n = 0
    for i, l in enumerate(lines):
        if pred(l):
            n += 1
            if n == nth:
                return i
    raise SystemExit('cut point not found')


def block_end(lines, i):
    j = i + 1
    while j < len(lines) and lines[j].strip():
        j += 1
    return j


def main(slab, real07, out):
    os.makedirs(out, exist_ok=True)
    L = open(slab).read().splitlines()
    ex = open(os.path.join(out, 'expect.tsv'), 'w')

    def write(name, lines, status, guard, rows):
        open(os.path.join(out, name + '.out'), 'w').write('\n'.join(lines) + '\n')
        rf = '-'
        if rows is not None:
            rf = os.path.join(out, name + '.rows')
            open(rf, 'w').write('\n'.join(' '.join(r) for r in rows) + '\n')
        ex.write(f'{name}\t{status}\t{guard}\t{rf}\n')

    is_pos = lambda l: l.startswith('ATOMIC_POSITIONS')
    is_bang = lambda l: l.startswith('!')
    scf_tail = ['', '     iteration #  1     ecut=    60.00 Ry     beta= 0.20',
                '     total energy              =  -27385.00000000 Ry']
    # C1: full real converged output -> CONVERGED, final coordinates
    t = '\n'.join(L)
    fin = t.split('Begin final coordinates')[1].split('End final coordinates')[0]
    frows = [l.split()[:4] for l in fin.splitlines() if re.match(r'^\s*[A-Z][a-z]?\d*\s+-?\d', l)]
    write('C1_full_converged', L, 'CONVERGED', 'empty', frows)
    # C2: SCF NOT converged on geometry 5 (g0..g4 validated) -> FAILED, guard; relax.in unchanged (rows '-' = input)
    i = block_end(L, lines_upto(L, is_pos, 5))
    c2 = L[:i] + scf_tail + ['', '     convergence NOT achieved after 200 iterations: stopping', '', '   JOB DONE.']
    g = parse('\n'.join(c2)); b = best(g)
    write('C2_scffail_g5', c2, 'FAILED', 'armed', None)
    open(os.path.join(out, 'C2_scffail_g5.bestrows'), 'w').write('\n'.join(' '.join(r) for r in g[b][0]) + '\n')
    # C3: time limit while computing g1 (only the input validated) -> FAILED, guard
    i = block_end(L, lines_upto(L, is_pos, 1))
    c3 = L[:i] + scf_tail + ['', '     Maximum CPU time exceeded', '', '   JOB DONE.']
    write('C3_timelimit_g1', c3, 'FAILED', 'armed', None)
    # C4: time limit while computing g2 (g0, g1 validated) -> CONTINUE from argmin
    i = block_end(L, lines_upto(L, is_pos, 2))
    c4 = L[:i] + scf_tail + ['', '     Maximum CPU time exceeded', '', '   JOB DONE.']
    g = parse('\n'.join(c4)); b = best(g)
    write('C4_timelimit_g2', c4, 'CONTINUE' if b > 0 else 'FAILED', 'empty' if b > 0 else 'armed', g[b][0] if b > 0 else None)
    # C5: BFGS failure printed with final coordinates = the unvalidated trial g15 -> CONTINUE from argmin(g0..g14)
    i = block_end(L, lines_upto(L, is_pos, 15))
    trial = L[lines_upto(L, is_pos, 15):i]
    c5 = L[:i] + ['', '     bfgs failed after  15 scf cycles and  14 bfgs steps, convergence not achieved',
                  '     (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr)', '',
                  '     End of BFGS Geometry Optimization', '', 'Begin final coordinates'] + trial + \
        ['End final coordinates', '', '   JOB DONE.']
    g = parse('\n'.join(c5)); b = best(g)
    assert b != 15 and g[15][1] is None
    write('C5_bfgsfail_trial', c5, 'CONTINUE', 'empty', g[b][0])
    # C6: converged text but output cut before 'End final coordinates' -> qeio converged fails -> CONTINUE argmin
    i = lines_upto(L, lambda l: 'End final coordinates' in l, 1)
    c6 = L[:i]
    g = parse('\n'.join(c6)); b = best(g)
    write('C6_converged_no_end', c6, 'CONTINUE', 'empty', g[b][0])
    # C7: 'Maximum number of steps' variant of C5 (QE text for nstep reached)
    c7 = [l.replace('bfgs failed after  15 scf cycles and  14 bfgs steps, convergence not achieved',
                    'The maximum number of steps has been reached.') for l in c5]
    write('C7_maxsteps_trial', c7, 'CONTINUE', 'empty', g[best(parse('\n'.join(c5)))][0])
    # C8: real aIO_0p7_s1 s0 -> FAILED, guard, bestvalid = argmin validated
    if real07 != '-':
        R = open(real07).read().splitlines()
        g = parse('\n'.join(R)); b = best(g)
        write('C8_real_aIO_0p7_s1_s0', R, 'FAILED', 'armed', None)
        open(os.path.join(out, 'C8_real_aIO_0p7_s1_s0.bestrows'), 'w').write('\n'.join(' '.join(r) for r in g[b][0]) + '\n')
        print('C8 independent: n_geom', len(g), 'validated', [k for k, (r, e) in enumerate(g) if e is not None],
              'best', b, 'E', g[b][1])
    ex.close()


if __name__ == '__main__':
    main(*sys.argv[1:4])
