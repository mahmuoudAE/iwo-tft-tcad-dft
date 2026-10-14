#!/usr/bin/env python3
"""A23 (ii)/(iii) dry check of an NC package (standard library only; reads, never writes).

usage: python3 check_nc.py --pkg DIR --nel N_el --k K --nbnd NB --src relax.in [--preview]
Checks scf_pbe.in / scf_hse.in (or preview_*): nat and species order = --src, NC electrons, nbnd, k, Gaussian 0.005,
80/320 Ry, nspin 1, conv_thr 1e-9, the HSE line only in the hse input (nqx 1, ecutfock 160), identical geometry and
otherwise identical text in both, minimum-image distances; the pseudopotential directories (pristine SG15 md5 = the
2026-10-01 files; projection copies with PP_CHI); nc.sub (executable, every transfer input exists, the outputs).
"""
import argparse
import hashlib
import itertools
import math
import re
import sys
from pathlib import Path

SG15_MD5 = {'In_ONCV_PBE-1.2.upf': '2123f823f6143602c63cd302e3a0bdd6', 'O_ONCV_PBE-1.2.upf': 'e36c48deb68f4e355fffe4602be2c42c',
            'W_ONCV_PBE-1.2.upf': 'b6096f31a98cdd82a46cfdcd1f902baf'}
NC_VAL = {'In': 13, 'O': 6, 'W': 28}
HSE = "  input_dft = 'hse', nqx1 = 1, nqx2 = 1, nqx3 = 1, ecutfock = 160"
fails = []


def ok(c, m):
    print(('  ok   ' if c else '  FAIL ') + m)
    if not c:
        fails.append(m)


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
    ap.add_argument('--pkg', required=True)
    ap.add_argument('--nel', type=int, required=True)
    ap.add_argument('--k', type=int, required=True)
    ap.add_argument('--nbnd', type=int, required=True)
    ap.add_argument('--src', required=True)
    ap.add_argument('--preview', action='store_true')
    a = ap.parse_args()
    pkg = Path(a.pkg)
    hse_dir = pkg.parent
    pre = 'preview_' if a.preview else ''
    src = Path(a.src).read_text().splitlines()
    src_order = [l.split()[0] for l in card(src, 'ATOMIC_POSITIONS')[1]]
    src_species = [l.split()[0] for l in card(src, 'ATOMIC_SPECIES')[1]]
    src_cell = [[float(x) for x in l.split()] for l in card(src, 'CELL_PARAMETERS')[1][:3]]
    texts = {}
    for tag in ('pbe', 'hse'):
        p = pkg / f'{pre}scf_{tag}.in'
        t = p.read_text()
        texts[tag] = t
        lines = t.splitlines()
        nl = {k.lower(): v.strip().strip("'") for k, v in re.findall(r'(\w+)\s*=\s*([^,\n/]+)', t.split('ATOMIC_SPECIES')[0])}
        sp = card(lines, 'ATOMIC_SPECIES')[1]
        species = [l.split()[0] for l in sp]
        pph, pos = card(lines, 'ATOMIC_POSITIONS')
        order = [l.split()[0] for l in pos]
        cellh, cellb = card(lines, 'CELL_PARAMETERS')
        cell = [[float(x) for x in l.split()] for l in cellb[:3]]
        kh, kb = card(lines, 'K_POINTS')
        nel = sum(NC_VAL[s] for s in order)
        print(f'== {p}')
        ok(nl['calculation'] == 'scf' and nl['prefix'] == tag, f"calculation {nl['calculation']}, prefix {nl['prefix']}")
        ok(int(nl['nat']) == len(order) == len(src_order) and order == src_order, f"nat {nl['nat']}, atom order = source ({len(src_order)})")
        ok(species == src_species and int(nl['ntyp']) == len(species), f'species {species}')
        ok(all(l.split()[2] in SG15_MD5 for l in sp), 'SG15 ONCV 1.2 files named')
        ok(nel == a.nel, f'NC valence electrons {nel} (expected {a.nel})')
        ok(int(nl['nbnd']) == a.nbnd and a.nbnd >= math.ceil(0.6 * nel), f"nbnd {nl['nbnd']} (>= 1.2 N_el/2 = {math.ceil(0.6 * nel)})")
        ok(int(nl['ecutwfc']) == 80 and int(nl['ecutrho']) == 320, f"ecut {nl['ecutwfc']}/{nl['ecutrho']}")
        ok(nl['occupations'] == 'smearing' and nl['smearing'] == 'gaussian' and float(nl['degauss']) == 0.005,
           f"smearing {nl['smearing']} {nl['degauss']}")
        ok('nspin' not in nl and 'starting_magnetization' not in t, 'spin-unpolarised')
        ok(nl['conv_thr'] == '1.0d-9' and nl['mixing_beta'] == '0.3' and nl['electron_maxstep'] == '150', 'electrons as 2026-10-01')
        ok(nl.get('verbosity') == 'high' and 'tstress' not in t, 'verbosity high, no stress')
        ok(kh == 'K_POINTS automatic' and kb == [f'{a.k} {a.k} {a.k} 0 0 0'], f'K_POINTS {kh} {kb}')
        ok(cellh == 'CELL_PARAMETERS angstrom' and all(abs(cell[i][j] - src_cell[i][j]) < 1e-6 for i in range(3) for j in range(3)),
           'cell = source cell (fixed-cell relaxation)')
        if tag == 'hse':
            ok(HSE in t, 'HSE06 line: nqx 1x1x1, ecutfock 160')
        else:
            ok('input_dft' not in t and 'ecutfock' not in t, 'no hybrid keywords in the PBE input')
        # minimum-image distances (cubic cells; crystal or angstrom positions)
        unit = pph.replace('(', ' ').replace(')', ' ').split()[1]
        xyz = []
        for l in pos:
            s, x, y, z = l.split()[:4]
            f = [float(x), float(y), float(z)]
            xyz.append((s, [f[0] * cell[0][0], f[1] * cell[1][1], f[2] * cell[2][2]] if unit == 'crystal' else f))
        cub = all(abs(cell[i][j]) < 1e-8 for i in range(3) for j in range(3) if i != j)
        dmin = {}
        for (s1, p1), (s2, p2) in itertools.combinations(xyz, 2):
            d = [p1[i] - p2[i] for i in range(3)]
            d = [x - cell[i][i] * round(x / cell[i][i]) for i, x in enumerate(d)]
            r = math.sqrt(sum(x * x for x in d))
            kk = '-'.join(sorted((s1, s2)))
            dmin[kk] = min(dmin.get(kk, 99.0), r)
        ok(cub and min(dmin.values()) > 1.7, 'min distances: ' + ', '.join(f'{k} {v:.3f}' for k, v in sorted(dmin.items())))
    strip = lambda t: t.replace(HSE + '\n', '').replace("prefix = 'hse'", "prefix = 'pbe'")
    ok(strip(texts['hse']) == texts['pbe'], 'pbe and hse inputs identical apart from the HSE line and prefix')
    print('== pseudopotentials')
    for f, m in SG15_MD5.items():
        p = hse_dir / 'pseudo' / f
        ok(p.is_file() and hashlib.md5(p.read_bytes()).hexdigest() == m, f'pseudo/{f} md5 {m} (2026-10-01 file)')
        q = hse_dir / 'pseudo_proj' / f
        n = re.search(r'number_of_wfc="\s*(\d+)"', q.read_text()).group(1) if q.is_file() else '0'
        ok(int(n) > 0, f'pseudo_proj/{f}: {n} PP_CHI')
    print('== nc.sub')
    s = (pkg / 'nc.sub').read_text()
    kv = dict(re.findall(r'^([+\w]+)\s*=\s*(.*)$', s, re.M))
    exe = Path(kv['executable'])
    ok(exe.is_file() and exe.stat().st_mode & 0o111, f'executable {exe}')
    ins = [x.strip() for x in kv['transfer_input_files'].split(',')]
    for tag in ('pbe', 'hse'):
        miss = [x for x in (i.replace('$(nc_tag)', tag) for i in ins)
                if not (Path(x) if x.startswith('/') else pkg / (pre + x if x.startswith('scf_') else x)).exists()]
        ok(not miss, f'{tag}: every transfer input exists {miss if miss else ""}')
    outs = [x.strip() for x in kv['transfer_output_files'].split(',')]
    ok(outs == ['$(nc_name)_$(nc_tag)_results.tar.gz', 'scf_$(nc_tag).out', 'projwfc_$(nc_tag).out',
                'atomic_proj_$(nc_tag).xml', 'data-file-schema_$(nc_tag).xml', 'STATUS_$(nc_tag)'], f'outputs {outs}')
    ok(kv['request_gpus'] == '0' and kv['request_cpus'] == '32', 'CPU 32, no GPU')
    ok((pkg / 'logs').is_dir(), 'logs/ exists')
    print('RESULT: ' + ('PASS' if not fails else f'{len(fails)} FAIL(S)'))
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
