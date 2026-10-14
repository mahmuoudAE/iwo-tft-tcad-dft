#!/usr/bin/env python3
"""A23 (i) dry check of runs/aIO_bulk_s1 and runs/aIWO_bulk_s1 (standard library only; reads, never writes).

usage: python3 check_bulkref.py [<root>]   (default ~/iwo_amorph)
Checks relax.in / final.tmpl (nat, species, PP files, electrons, nbnd, k, smearing, cutoffs, no dipole correction,
geometry identical in both, minimum-image distances), the two submit files (every transfer_input exists, executable,
outputs listed, GPU/CPU requests), the DAG text and the copied scripts (byte-identical to their sources).
"""
import hashlib
import itertools
import math
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / 'iwo_amorph'
VAL = {'In': 13, 'W': 14, 'O': 6}
PP = {'In': 'In.pbe-dn-kjpaw_psl.1.0.0.UPF', 'W': 'W.pbe-spn-kjpaw_psl.1.0.0.UPF', 'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF'}
EXPECT = {'aIO_bulk_s1': {'In': 50, 'O': 75}, 'aIWO_bulk_s1': {'In': 49, 'W': 1, 'O': 76}}
DAG = ('JOB RELAX relax.sub\nVARS RELAX seg="$(RETRY)"\nRETRY RELAX 8 UNLESS-EXIT 2\nJOB FINAL final.sub\n'
       'RETRY FINAL 1\nPARENT RELAX CHILD FINAL\n')
fails = []


def ok(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)


def parse(path):
    t = path.read_text()
    nl = {k.lower(): v.strip().strip("'") for k, v in re.findall(r'(\w+)\s*=\s*([^,\n/]+)', t.split('ATOMIC_SPECIES')[0])}
    lines = t.splitlines()
    i = next(n for n, l in enumerate(lines) if l.startswith('ATOMIC_SPECIES'))
    species = {}
    for l in lines[i + 1:]:
        if not l.strip() or l.strip().startswith(('CELL', 'K_POINTS', 'ATOMIC')):
            break
        s, m, f = l.split()
        species[s] = f
    i = next(n for n, l in enumerate(lines) if l.startswith('CELL_PARAMETERS'))
    cell = [[float(x) for x in lines[i + k].split()] for k in (1, 2, 3)]
    i = next(n for n, l in enumerate(lines) if l.startswith('K_POINTS'))
    kp = (lines[i].split()[1], tuple(int(x) for x in lines[i + 1].split()))
    i = next(n for n, l in enumerate(lines) if l.startswith('ATOMIC_POSITIONS'))
    unit = lines[i].split()[1]
    atoms = []
    for l in lines[i + 1:]:
        if not l.strip():
            break
        p = l.split()
        atoms.append((p[0], [float(x) for x in p[1:4]]))
    return t, nl, species, cell, kp, unit, atoms


def min_dists(cell, atoms):
    a = [cell[k][k] for k in range(3)]
    ok_cubic = all(abs(cell[i][j]) < 1e-8 for i in range(3) for j in range(3) if i != j)
    out = {}
    for (s1, p1), (s2, p2) in itertools.combinations(atoms, 2):
        d = [p1[k] - p2[k] for k in range(3)]
        d = [x - a[k] * round(x / a[k]) for k, x in enumerate(d)]
        r = math.sqrt(sum(x * x for x in d))
        key = '-'.join(sorted((s1, s2)))
        out[key] = min(out.get(key, 99), r)
    return ok_cubic, out


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


for name, comp in EXPECT.items():
    run = ROOT / 'runs' / name
    print(f'== {name}')
    nel = sum(VAL[s] * n for s, n in comp.items())
    nat = sum(comp.values())
    geo = {}
    for f, calc, ecut, nbnd in (('relax.in', 'relax', 60, None), ('final.tmpl', 'scf', 71, math.ceil(1.3 * nel / 2))):
        t, nl, sp, cell, kp, unit, atoms = parse(run / f)
        geo[f] = (cell, atoms)
        got = {s: sum(1 for x, _ in atoms if x == s) for s in sp}
        ok(nl['calculation'] == calc, f'{f}: calculation {nl["calculation"]}')
        ok(int(nl['nat']) == nat == len(atoms), f'{f}: nat {nl["nat"]}, positions {len(atoms)}, expected {nat}')
        ok(int(nl['ntyp']) == len(sp) and got == comp, f'{f}: species {sp and list(sp)} composition {got}')
        ok(all(sp[s] == PP[s] and (ROOT / 'common' / 'pseudo' / PP[s]).is_file() for s in sp), f'{f}: PAW files present')
        ok(int(nl['ecutwfc']) == ecut and int(nl['ecutrho']) == 8 * ecut, f'{f}: ecut {nl["ecutwfc"]}/{nl["ecutrho"]}')
        ok(nl['occupations'] == 'smearing' and nl['smearing'] == 'gaussian' and float(nl['degauss']) == 0.005,
           f'{f}: smearing {nl["smearing"]} {nl["degauss"]}')
        ok(kp == ('automatic', (2, 2, 2, 0, 0, 0)), f'{f}: K_POINTS {kp}')
        ok('tefield' not in t and 'dipfield' not in t and 'cell_dofree' not in t, f'{f}: no dipole/cell dof (bulk, fixed cell)')
        ok(nl.get('verbosity') == 'high', f'{f}: verbosity {nl.get("verbosity")}')
        if nbnd:
            ok(int(nl.get('nbnd', 0)) == nbnd, f'{f}: nbnd {nl.get("nbnd")} = ceil(1.3*{nel}/2) = {nbnd}')
        else:
            ok('nbnd' not in nl, f'{f}: nbnd default (N_el {nel})')
            ok(nl.get('mixing_beta') == '0.1' and nl.get('mixing_ndim') == '12' and nl.get('electron_maxstep') == '300',
               f'{f}: pilot electrons beta {nl.get("mixing_beta")} ndim {nl.get("mixing_ndim")} maxstep {nl.get("electron_maxstep")}')
            ok(nl.get('forc_conv_thr') == '1.0d-3' and nl.get('ion_dynamics') == 'bfgs', f'{f}: BFGS, forc_conv_thr 1e-3')
        ok(unit == 'angstrom', f'{f}: positions in {unit}')
    ok(geo['relax.in'] == geo['final.tmpl'], 'relax.in and final.tmpl hold the same cell and positions')
    cubic, dmin = min_dists(*geo['relax.in'])
    ok(cubic, 'cubic cell (minimum image valid)')
    print('       min distances (A): ' + ', '.join(f'{k} {v:.3f}' for k, v in sorted(dmin.items())))
    ok(dmin.get('In-O', 0) > 1.85 and dmin.get('O-O', 0) > 2.2 and dmin.get('In-In', 0) > 2.7, 'no short contacts')
    # submit files
    for sub, exe_rel in (('relax.sub', run / 'relax_node_bulk.sh'), ('final.sub', ROOT / 'common' / 'final_node.sh')):
        s = (run / sub).read_text()
        kv = dict(re.findall(r'^([+\w]+)\s*=\s*(.*)$', s, re.M))
        exe = Path(kv['executable'])
        ok(exe == exe_rel.resolve() or exe == exe_rel, f'{sub}: executable {exe}')
        ok(exe.is_file() and exe.stat().st_mode & 0o111, f'{sub}: executable exists and is executable')
        ins = [x.strip() for x in kv['transfer_input_files'].split(',')]
        miss = [x for x in ins if not (Path(x) if x.startswith('/') else run / x).exists()]
        ok(not miss, f'{sub}: all {len(ins)} transfer inputs exist {miss if miss else ""}')
        outs = [x.strip() for x in kv['transfer_output_files'].split(',')]
        if sub == 'relax.sub':
            ok(outs == ['relax_s$(seg)_results.tar.gz', 'relax.in', 'RELAX_STATUS', 'relax.out', 'SEGMENT_SUMMARY'],
               f'{sub}: outputs {outs}')
            ok('geomsel.py' in ins and 'steps_relax.sh' in ins and 'relax.in' in ins, f'{sub}: geomsel.py, steps, relax.in sent')
            ok(kv['request_gpus'] == '1' and 'H100|H200|A100' in kv['requirements'] and kv['request_memory'] == '64 GB',
               f'{sub}: 1 GPU H100|H200|A100, 64 GB')
            ok('!regexp("MIG", TARGET.GPUs_DeviceName)' in kv['requirements'], f'{sub}: MIG slices excluded (D-24)')
            ok(kv['arguments'] == '$(seg) 72000', f'{sub}: arguments {kv["arguments"]}')
        else:
            ok(outs == ['final_results.tar.gz'], f'{sub}: outputs {outs}')
            ok(kv.get('hold') == 'True' and kv['request_gpus'] == '0' and kv['request_cpus'] == '32', f'{sub}: CPU 32, hold = True')
        ok(f'"{name}_' in kv['+IWOJob'], f'{sub}: +IWOJob {kv["+IWOJob"]}')
    ok((run / f'{name}.dag').read_text() == DAG, 'DAG text (RETRY RELAX 8 UNLESS-EXIT 2, FINAL child)')
    pilot = ROOT / 'runs' / 'aIO_0p8_s1'
    for dst, src in (('relax_node_bulk.sh', pilot / 'relax_node_pilot.sh'), ('steps_relax.sh', pilot / 'steps_relax.sh'),
                     ('geomsel.py', pilot / 'geomsel.py'), ('steps_final.sh', ROOT / 'common' / 'steps_final.sh')):
        ok(md5(run / dst) == md5(src), f'{dst} byte-identical to {src}')
    ok((run / 'logs').is_dir(), 'logs/ exists')
    st = (run / 'steps_relax.sh').read_text()
    ok("grep -q 'bfgs converged' relax.out" in st, "steps_relax.sh: CONVERGED requires 'bfgs converged' (A19)")

print('\nRESULT: ' + ('PASS' if not fails else f'{len(fails)} FAIL(S)'))
sys.exit(1 if fails else 0)
