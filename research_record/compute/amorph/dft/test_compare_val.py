#!/usr/bin/env python3
"""Self-test of compare_val.py on synthetic data only (no val output is read). Run: python3 -I test_compare_val.py

Synthetic frames: a skewed periodic cell with one W next to the x = 0 face, six O inside 2.60 A (two of them only
through the periodic images), one O at 2.65 A and one H at 2.25 A (both outside S), 31 far In/O atoms (nat 40).
QE-format scf.out text (QE 7.5 / 7.3.1 layouts of the summary and forces blocks); scf.in from make_dft.qe_input,
the generator of the real val inputs. MACE forces = DFT forces - a chosen error pattern, so every metric has a
closed form. Cases: pass, each limit failing alone, the 2.45 A INFO shell never scored, no-W frame, melt frame,
out-of-plan frame, split labels with
three label-map formats, split labels without a map, invalid maps, non-converged SCF, 'Maximum CPU time', missing /
short / doubled forces block, QE error banner, nat mismatch, tarball faults, geometry mismatch, the roll-up of the
eight plan frames, the 2 nm stop rule and the command line (python -I).
"""
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)   # python -I leaves the script directory out of sys.path

import compare_val as CV   # noqa: E402
import make_dft            # noqa: E402

BOHR = CV.BOHR_A
CELL = [[10.0, 0.0, 0.0], [1.0, 11.0, 0.0], [0.0, 0.0, 12.0]]
W0 = [0.5, 0.5, 6.0]
SHELL_VECS = [(1.9, 0, 0), (-1.9, 0, 0), (0, 0, 1.95), (0, 0, -2.0), (0, -1.9, 0), (0, 2.55, 0)]
S_EXPECTED = [1, 2, 3, 4, 5, 6, 7]            # 1-based: W + the six O above
NAT = 40


def _add(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def wrap(r):
    inv, _ = CV.cell_inverse(CELL)
    f = [r[0] * inv[0][k] + r[1] * inv[1][k] + r[2] * inv[2][k] for k in range(3)]
    f = [x - math.floor(x) for x in f]
    return [f[0] * CELL[0][q] + f[1] * CELL[1][q] + f[2] * CELL[2][q] for q in range(3)]


def structure(with_w=True):
    atoms = [('W' if with_w else 'In', list(W0))]
    atoms += [('O', wrap(_add(W0, v))) for v in SHELL_VECS]
    atoms.append(('O', wrap(_add(W0, (-1.874, -1.874, 0.0)))))   # 2.650 A: outside the cutoff
    atoms.append(('H', wrap(_add(W0, (1.3, 1.3, 1.3)))))          # 2.252 A: H, never in S
    mi = CV.MinImage(CELL, 5.0)
    k = 0
    cands = [((i + 0.1) / 5, (j + 0.3) / 5, (l + 0.2) / 5) for i in range(5) for j in range(5) for l in range(5)]
    for f in cands:
        r = [f[0] * CELL[0][q] + f[1] * CELL[1][q] + f[2] * CELL[2][q] for q in range(3)]
        if mi.distance(W0, r) > 3.2 and all(mi.distance(p, r) > 1.2 for _, p in atoms):
            atoms.append(('In' if k % 2 == 0 else 'O', r))
            k += 1
            if k == NAT - 9:
                break
    assert len(atoms) == NAT, len(atoms)
    return atoms


def split_labels(species):
    """A25 alternating rule: In -> In1/In2, O -> O1/O2 in order of appearance; W and H unchanged."""
    n, out = {}, []
    for e in species:
        if e in ('In', 'O'):
            n[e] = n.get(e, 0) + 1
            out.append(f'{e}{1 + (n[e] - 1) % 2}')
        else:
            out.append(e)
    return out


def dft_forces(seed=7):
    rng = random.Random(seed)
    return [[rng.randint(-5000000, 5000000) / 1e8 for _ in range(3)] for _ in range(NAT)]


def errors(d0, dW, shell=S_EXPECTED, override=None):
    """DF = F_DFT - F_MACE per atom/component, alternating sign; |DF| = dW on S, d0 elsewhere (or override)."""
    out = []
    for i in range(NAT):
        mag = (override or {}).get(i + 1, dW if (i + 1) in shell else d0)
        out.append([(-1) ** (i + c) * mag for c in range(3)])
    return out


def scf_out_text(labels, pos, forces_ry, version='7.5', converged=True, max_cpu=False, forces='full',
                 banner=False, positions=True):
    alat_a = math.sqrt(sum(x * x for x in CELL[0]))
    alat_b = alat_a / BOHR
    L = [f'     Program PWSCF v.{version} starts on 12Oct2026 at  5:00: 0 ', '',
         '     bravais-lattice index     =            0',
         f'     lattice parameter (alat)  = {alat_b:12.4f}  a.u.',
         f'     unit-cell volume          = {1320.0 / BOHR ** 3:12.4f} (a.u.)^3',
         f'     number of atoms/cell      = {len(labels):12d}',
         f'     number of atomic types    = {len(set(labels)):12d}', '',
         '     crystal axes: (cart. coord. in units of alat)']
    L += ['               a(%d) = (%11.6f%11.6f%11.6f )  ' % (r + 1, *[x / alat_a for x in CELL[r]]) for r in range(3)]
    if positions:
        L += ['', '   Cartesian axes', '', '     site n.     atom                  positions (alat units)']
        L += ['      %5d        %-6s tau(%5d) = (%12.7f%12.7f%12.7f  )' % (i + 1, lab, i + 1, *[x / alat_a for x in p])
              for i, (lab, p) in enumerate(zip(labels, pos))]
    L += ['', '     total energy              =   -9999.00000000 Ry']
    if converged:
        L += ['', '     convergence has been achieved in  15 iterations']
    else:
        L += ['', '     convergence NOT achieved after 200 iterations: stopping']
    if max_cpu:
        L += ['', '     Maximum CPU time exceeded']
    if banner:
        L += ['', ' %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',
              '     Error in routine c_bands (1):', '     too many bands are not converged']
    if forces != 'missing':
        rows = ['     atom %4d type %2d   force = %14.8f%14.8f%14.8f' % (i + 1, 1, *f) for i, f in enumerate(forces_ry)]
        if forces == 'short':
            rows = rows[:-1]
        block = ['', '     Forces acting on atoms (cartesian axes, Ry/au):', ''] + rows
        block += ['', '     Total force =     0.123456     Total SCF correction =     0.000123']
        L += block
        if forces == 'double':
            L += block
    L += ['', '     JOB DONE.', '']
    return '\n'.join(L)


def scf_in_text(atoms, labels, shift=None):
    pos = [list(p) for _, p in atoms]
    if shift:
        i, v = shift
        pos[i] = _add(pos[i], v)
    txt = make_dft.qe_input('scf', 'val', CELL, [(e, p) for (e, _), p in zip(atoms, pos)], 60, (2, 2, 2), False)
    if labels == [e for e, _ in atoms]:
        return txt
    lines = txt.split('\n')
    pi = lines.index('ATOMIC_POSITIONS angstrom')
    for k, lab in enumerate(labels):
        f = lines[pi + 1 + k].split()
        lines[pi + 1 + k] = '  ' + ' '.join([lab] + f[1:])
    si, ci = lines.index('ATOMIC_SPECIES'), lines.index('CELL_PARAMETERS angstrom')
    spec = []
    for ln in lines[si + 1:ci]:
        f = ln.split()
        spec += [f'  {f[0]}{k} {f[1]} {f[2]}' for k in (1, 2)] if f[0] in ('In', 'O') else [ln]
    lines[si + 1:ci] = spec
    return '\n'.join(lines).replace(f'ntyp = {len(set(e for e, _ in atoms))}', f'ntyp = {len(set(labels))}')


def write_map(path, labels, elements, mode):
    if mode == 'atom_header':
        rows = ['index\telement\tsplit_label'] + [f'{i + 1}\t{e}\t{l}' for i, (e, l) in enumerate(zip(elements, labels))]
    elif mode == 'atom_noheader0':   # 0-based, columns index, split, element (column roles inferred)
        rows = ['# a30 label map, 0-based'] + [f'{i}\t{l}\t{e}' for i, (e, l) in enumerate(zip(elements, labels))]
    elif mode == 'label':
        rows = ['In1\tIn', 'In2\tIn', 'O1\tO', 'O2\tO']
    elif mode == 'bad_element':
        els = list(elements)
        els[2] = 'In'                # atom 3 is O1
        rows = ['index\telement\tsplit_label'] + [f'{i + 1}\t{e}\t{l}' for i, (e, l) in enumerate(zip(els, labels))]
    elif mode == 'bad_count':
        rows = ['index\telement\tsplit_label'] + [f'{i + 1}\t{e}\t{l}' for i, (e, l) in
                                                  enumerate(zip(elements[:-1], labels[:-1]))]
    elif mode == 'bad_split':
        labs = list(labels)
        labs[4] = 'O2' if labs[4] == 'O1' else 'O1'
        rows = ['index\telement\tsplit_label'] + [f'{i + 1}\t{e}\t{l}' for i, (e, l) in enumerate(zip(elements, labs))]
    elif mode == 'garbage':
        rows = ['a\tb\tc', 'x\ty\tz']
    else:
        raise ValueError(mode)
    with open(path, 'w', newline='\n') as f:
        f.write('\n'.join(rows) + '\n')


def make_job(root, name, tag, d0=0.05, dW=0.12, with_w=True, split=False, map_mode=None, map_in_job=True,
             override=None, scf_kw=None, scf_in=True, shift=None, nref=None, tar='normal', ref_tag=None):
    """Synthetic val job directory <root>/<name>_<tag>; returns (job_dir, expected metrics)."""
    atoms = structure(with_w)
    elements = [e for e, _ in atoms]
    labels = split_labels(elements) if split else elements
    shell = S_EXPECTED if with_w else []
    fry = dft_forces()
    fry = [[float('%.8f' % x) for x in r] for r in fry]
    df = errors(d0, dW, shell, override)
    mace = [[fry[i][c] * CV.RYBOHR_TO_EV_A - df[i][c] for c in range(3)] for i in range(NAT)]
    job = os.path.join(root, f'{name}_{tag}')
    os.makedirs(job)
    with open(os.path.join(job, 'mace_ref.json'), 'w') as f:
        json.dump({'tag': ref_tag or tag, 'energy_eV': -1234.5, 'forces_eV_A': mace[:nref] if nref else mace}, f)
    tp = os.path.join(job, CV.TARBALL)
    if tar == 'empty':
        open(tp, 'wb').close()
    elif tar != 'absent':
        tmp = os.path.join(root, f'_build_{name}_{tag}')
        os.makedirs(tmp)
        with open(os.path.join(tmp, 'scf.out'), 'w', newline='\n') as f:
            f.write(scf_out_text(labels, [p for _, p in atoms], fry, **(scf_kw or {})))
        with open(os.path.join(tmp, 'scf.in'), 'w', newline='\n') as f:
            f.write(scf_in_text(atoms, labels, shift))
        with open(os.path.join(tmp, 'driver.log'), 'w') as f:
            f.write('synthetic\n')
        with tarfile.open(tp, 'w:gz') as tf:
            tf.add(os.path.join(tmp, 'scf.out'), arcname='scf.out')
            if scf_in:
                tf.add(os.path.join(tmp, 'scf.in'), arcname='scf.in')
            tf.add(os.path.join(tmp, 'driver.log'), arcname='driver.log')
            if tar == 'two_scf_out':
                tf.add(os.path.join(tmp, 'scf.out'), arcname='old/scf.out')
        shutil.rmtree(tmp)
    if map_mode:
        mp = os.path.join(job if map_in_job else root, CV.MAP_NAME if map_in_job else f'{name}_{tag}.tsv')
        write_map(mp, labels, elements, map_mode)
    n_s = len(shell)
    mags = [abs(df[i][0]) for i in range(NAT)]
    exp = {'rmse_all': math.sqrt(sum(m * m for m in mags) / NAT), 'mae_all': sum(mags) / NAT,
           'rmse_W1': (math.sqrt(sum(mags[i - 1] ** 2 for i in shell) / n_s) if n_s else None)}
    return job, exp


class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='iwo_cmpval_')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def frame(self, name='aIWO_bulk_s1', tag='final', map_path=None, sub='', **kw):
        job, exp = make_job(os.path.join(self.root, sub), name, tag, **kw)
        return CV.evaluate_job(job, None, map_path), exp

    def assertMetrics(self, fr, exp):
        m = fr['metrics']
        self.assertAlmostEqual(m['rmse_all_eV_A'], exp['rmse_all'], places=12)
        self.assertAlmostEqual(m['mae_all_eV_A'], exp['mae_all'], places=12)
        if exp['rmse_W1'] is None:
            self.assertIsNone(m['rmse_W1_eV_A'])
        else:
            self.assertAlmostEqual(m['rmse_W1_eV_A'], exp['rmse_W1'], places=12)

    def assertNotScored(self, fr, code):
        self.assertEqual(fr['status'], 'FAIL_NOT_SCORED', fr['reasons'])
        self.assertIn(code, [c for c, _ in fr['reasons']], fr['reasons'])
        self.assertIsNone(fr['metrics'])
        self.assertIsNone(fr['verdict'])


class TestDefinitions(unittest.TestCase):
    def test_unit_conversion(self):
        self.assertEqual(CV.RYBOHR_TO_EV_A, 13.605693122994 / 0.529177210903)
        self.assertAlmostEqual(CV.RYBOHR_TO_EV_A, 25.711033738162943, places=12)

    def test_frozen_limits(self):
        self.assertEqual((CV.LIMIT_RMSE, CV.LIMIT_MAE, CV.LIMIT_W1, CV.STOP_RMSE, CV.W_SHELL_CUTOFF_A),
                         (0.15, 0.10, 0.25, 0.30, 2.60))
        self.assertEqual(len(CV.PLAN_FRAMES), 8)
        self.assertEqual(sum(t in CV.SCORED_TAGS for _, t in CV.PLAN_FRAMES), 7)

    def test_minimum_image(self):
        atoms = structure()
        mi = CV.MinImage(CELL, 4.1)
        d = [mi.distance(atoms[0][1], atoms[k][1]) for k in range(9)]
        for k, want in zip(range(1, 9), (1.9, 1.9, 1.95, 2.0, 1.9, 2.55, math.hypot(1.874, 1.874),
                                         math.sqrt(3 * 1.3 ** 2))):
            self.assertAlmostEqual(d[k], want, places=9)
        # atoms 3 and 6 sit across the cell faces: the plain Cartesian distance is far larger
        for k in (2, 5):
            self.assertGreater(math.dist(atoms[0][1], atoms[k][1]), 5.0)

    def test_minimum_image_strongly_skewed_cell(self):
        """Against brute force over images -4..4 in a cell where rounding the fractional vector is not enough."""
        cell = [[10.0, 0.0, 0.0], [8.5, 5.0, 0.0], [0.0, 3.0, 9.0]]
        mi = CV.MinImage(cell, CV.INFO_RADIUS_A)
        rng = random.Random(3)
        hits = 0
        for _ in range(300):
            p, q = ([sum(rng.random() * cell[r][k] for r in range(3)) for k in range(3)] for _ in range(2))
            brute = min(math.dist(p, [q[k] + i * cell[0][k] + j * cell[1][k] + l * cell[2][k] for k in range(3)])
                        for i in range(-4, 5) for j in range(-4, 5) for l in range(-4, 5))
            if brute <= CV.INFO_RADIUS_A:
                hits += 1
                self.assertAlmostEqual(mi.distance(p, q), brute, places=9)
        self.assertGreater(hits, 50)


class TestFrames(Base):
    def test_pass_unsplit(self):
        fr, exp = self.frame()
        self.assertEqual((fr['status'], fr['verdict']), ('SCORED', 'PASS'), fr['reasons'])
        self.assertMetrics(fr, exp)
        self.assertEqual(fr['criteria'], {'rmse_all': True, 'mae_all': True, 'rmse_W1': True})
        ws = fr['W_shell']
        self.assertEqual(ws['W_atoms'], [1])
        self.assertEqual(ws['S_atoms'], S_EXPECTED)               # O at 2.65 A (atom 8) and H (atom 9) excluded
        self.assertEqual(ws['per_W'][1]['CN_O'], 6)
        self.assertAlmostEqual(ws['per_W'][1]['nearest_O_beyond_cutoff_A'], 2.6503, places=3)
        self.assertEqual(fr['metrics']['n_W1_atoms'], 7)
        self.assertEqual(ws['S_atoms_at_2p45_info'], [1, 2, 3, 4, 5, 6])   # the O at 2.55 A is outside 2.45 A
        self.assertAlmostEqual(fr['metrics']['rmse_W1_at_2p45_info_eV_A'], 0.12, places=12)
        self.assertEqual(fr['composition'], {'H': 1, 'In': 16, 'O': 22, 'W': 1})
        self.assertTrue(fr['geometry_source'].startswith('scf.out (cross-checked'))
        self.assertEqual(fr['qe']['qe_version'], '7.5')
        self.assertAlmostEqual(fr['qe']['total_scf_correction_ry_bohr'], 0.000123)

    def test_qe_731_gpu_layout(self):
        fr, exp = self.frame(tag='slab_annealed', name='aIWO_2p0_s1', scf_kw={'version': '7.3.1'},
                             split=True, map_mode='atom_header')
        self.assertEqual((fr['status'], fr['verdict']), ('SCORED', 'PASS'), fr['reasons'])
        self.assertEqual(fr['qe']['qe_version'], '7.3.1')
        self.assertMetrics(fr, exp)

    def test_each_limit_alone(self):
        fr, exp = self.frame(sub='w', d0=0.01, dW=0.27)                         # W shell only
        self.assertEqual(fr['verdict'], 'FAIL')
        self.assertEqual(fr['criteria'], {'rmse_all': True, 'mae_all': True, 'rmse_W1': False})
        self.assertMetrics(fr, exp)
        fr, exp = self.frame(sub='mae', d0=0.12, dW=0.12)                       # MAE only
        self.assertEqual(fr['criteria'], {'rmse_all': True, 'mae_all': False, 'rmse_W1': True})
        self.assertEqual(fr['verdict'], 'FAIL')
        self.assertMetrics(fr, exp)
        fr, exp = self.frame(sub='rmse', d0=0.0, dW=0.0, override={20: 0.5, 25: 0.5, 30: 0.5, 35: 0.5})   # RMSE only
        self.assertEqual(fr['criteria'], {'rmse_all': False, 'mae_all': True, 'rmse_W1': True})
        self.assertAlmostEqual(fr['metrics']['rmse_all_eV_A'], math.sqrt(4 * 0.25 / 40), places=12)
        self.assertEqual(fr['verdict'], 'FAIL')

    def test_info_cutoff_never_scored(self):
        """RMSE_W1 at 2.45 A above the limit while the frozen 2.60 A shell passes: the verdict stays PASS."""
        fr, exp = self.frame(d0=0.01, dW=0.26, override={7: 0.0})
        self.assertAlmostEqual(fr['metrics']['rmse_W1_eV_A'], 0.26 * math.sqrt(6 / 7), places=12)
        self.assertAlmostEqual(fr['metrics']['rmse_W1_at_2p45_info_eV_A'], 0.26, places=12)
        self.assertGreater(fr['metrics']['rmse_W1_at_2p45_info_eV_A'], CV.LIMIT_W1)
        self.assertEqual((fr['status'], fr['verdict']), ('SCORED', 'PASS'))
        self.assertEqual(fr['criteria'], {'rmse_all': True, 'mae_all': True, 'rmse_W1': True})
        self.assertMetrics(fr, exp)

    def test_no_w_frame(self):
        fr, exp = self.frame(name='aIO_bulk_s1', with_w=False)
        self.assertEqual((fr['status'], fr['verdict']), ('SCORED', 'PASS'))
        self.assertIsNone(fr['criteria']['rmse_W1'])
        self.assertEqual(fr['W_shell']['S_atoms'], [])
        self.assertIsNone(fr['metrics']['rmse_W1_at_2p45_info_eV_A'])
        self.assertMetrics(fr, exp)

    def test_melt_reported_not_scored(self):
        fr, exp = self.frame(tag='melt_3000K', d0=0.6, dW=0.9)
        self.assertEqual(fr['status'], 'REPORTED')
        self.assertIsNone(fr['verdict'])
        self.assertIsNone(fr['criteria'])
        self.assertMetrics(fr, exp)

    def test_out_of_plan(self):
        fr, _ = self.frame(name='aIWO_2p0_HfO2_s1', tag='final')
        self.assertEqual((fr['status'], fr['in_plan'], fr['verdict']), ('OUT_OF_PLAN', False, None))

    def test_split_labels_three_map_formats(self):
        ref, exp = self.frame()
        for mode in ('atom_header', 'atom_noheader0', 'label'):
            fr, _ = self.frame(name='aIWO_2p0_s1', sub=mode, split=True, map_mode=mode)
            self.assertEqual((fr['status'], fr['verdict']), ('SCORED', 'PASS'), (mode, fr['reasons']))
            self.assertIn('label map', fr['elements_source'])
            self.assertEqual(fr['W_shell']['S_atoms'], ref['W_shell']['S_atoms'])
            self.assertEqual(fr['composition'], ref['composition'])
            for k in ('rmse_all_eV_A', 'mae_all_eV_A', 'rmse_W1_eV_A'):
                self.assertEqual(fr['metrics'][k], ref['metrics'][k], (mode, k))

    def test_split_map_given_on_command_line(self):
        job, exp = make_job(self.root, 'aIWO_2p0_s1', 'final', split=True, map_mode='atom_header', map_in_job=False)
        fr = CV.evaluate_job(job, None, os.path.join(self.root, 'aIWO_2p0_s1_final.tsv'))
        self.assertEqual(fr['status'], 'SCORED', fr['reasons'])
        self.assertMetrics(fr, exp)

    def test_split_without_map_fails(self):
        fr, _ = self.frame(name='aIWO_2p0_s1', split=True)
        self.assertNotScored(fr, 'R11')

    def test_invalid_maps_fail(self):
        for mode in ('bad_element', 'bad_count', 'bad_split', 'garbage'):
            fr, _ = self.frame(name='aIWO_2p0_s1', sub=mode, split=True, map_mode=mode)
            self.assertNotScored(fr, 'R11')

    def test_not_converged_fails(self):
        fr, _ = self.frame(scf_kw={'converged': False})
        self.assertNotScored(fr, 'R1')
        self.assertIn('R5', [c for c, _ in fr['reasons']])

    def test_not_converged_split_fails(self):
        fr, _ = self.frame(name='aIWO_2p0_s1', split=True, map_mode='atom_header', scf_kw={'converged': False})
        self.assertNotScored(fr, 'R1')

    def test_max_cpu_time_fails(self):
        fr, _ = self.frame(scf_kw={'max_cpu': True})
        self.assertNotScored(fr, 'R2')

    def test_forces_block_missing(self):
        fr, _ = self.frame(scf_kw={'forces': 'missing'})
        self.assertNotScored(fr, 'R3')

    def test_forces_block_short(self):
        fr, _ = self.frame(scf_kw={'forces': 'short'})
        self.assertNotScored(fr, 'R4')

    def test_forces_block_twice(self):
        fr, _ = self.frame(scf_kw={'forces': 'double'})
        self.assertNotScored(fr, 'R6')

    def test_qe_error_banner(self):
        fr, _ = self.frame(scf_kw={'banner': True})
        self.assertNotScored(fr, 'R8')

    def test_nat_differs_from_mace(self):
        fr, _ = self.frame(nref=NAT - 1)
        self.assertNotScored(fr, 'R7')

    def test_tarball_faults(self):
        fr, _ = self.frame(tar='empty')
        self.assertNotScored(fr, 'R9')
        fr, _ = self.frame(tag='quenched_300K', tar='two_scf_out')
        self.assertNotScored(fr, 'R9')
        fr, _ = self.frame(tag='slab_annealed', tar='absent')
        self.assertEqual(fr['status'], 'MISSING')

    def test_mace_ref_faults(self):
        fr, _ = self.frame(tag='weird')
        self.assertNotScored(fr, 'R10')
        fr, _ = self.frame(tag='final', ref_tag='quenched_300K')
        self.assertNotScored(fr, 'R10')

    def test_geometry_mismatch(self):
        fr, _ = self.frame(shift=(12, (0.01, 0.0, 0.0)))
        self.assertNotScored(fr, 'R12')

    def test_geometry_sources(self):
        fr, exp = self.frame(scf_in=False)
        self.assertEqual(fr['status'], 'SCORED')
        self.assertTrue(fr['geometry_source'].startswith('scf.out (no usable scf.in'))
        self.assertMetrics(fr, exp)
        fr, exp = self.frame(tag='quenched_300K', scf_kw={'positions': False})
        self.assertEqual(fr['status'], 'SCORED', fr['reasons'])
        self.assertTrue(fr['geometry_source'].startswith('scf.in'))
        self.assertEqual(fr['W_shell']['S_atoms'], S_EXPECTED)
        self.assertMetrics(fr, exp)
        fr, _ = self.frame(tag='slab_annealed', scf_in=False, scf_kw={'positions': False})
        self.assertNotScored(fr, 'R12')

    def test_scf_in_crystal_positions(self):
        atoms = structure()
        txt = scf_in_text(atoms, [e for e, _ in atoms])
        inv, _ = CV.cell_inverse(CELL)
        lines = txt.split('\n')
        pi = lines.index('ATOMIC_POSITIONS angstrom')
        lines[pi] = 'ATOMIC_POSITIONS crystal'
        for k, (e, p) in enumerate(atoms):
            f = [sum(p[j] * inv[j][q] for j in range(3)) for q in range(3)]
            lines[pi + 1 + k] = f'  {e} {f[0]:.10f} {f[1]:.10f} {f[2]:.10f}'
        g_cr, g_a = CV.scf_in_geometry('\n'.join(lines)), CV.scf_in_geometry(txt)
        self.assertEqual(CV._geom_agree(g_cr, g_a), (True, ''))
        self.assertIsNone(CV.scf_in_geometry(txt.replace('ATOMIC_POSITIONS angstrom', 'ATOMIC_POSITIONS bohr')))


def build_plan(root, over=None):
    """The eight plan frames; the 2 nm frames are split-label runs with a30_label_map.tsv, as on CERN."""
    over = over or {}
    for name, tag in CV.PLAN_FRAMES:
        kw = {'with_w': name != 'aIO_bulk_s1'}
        if name == 'aIWO_2p0_s1':
            kw.update(split=True, map_mode='atom_header')
        kw.update(over.get(f'{name}_{tag}', {}))
        make_job(root, name, tag, **kw)


def plan_specs(root):
    return [(os.path.join(root, f'{n}_{t}'), (n, t)) for n, t in CV.PLAN_FRAMES]


class TestRollup(Base):
    def run_plan(self, over=None):
        build_plan(self.root, over)
        return CV.run(plan_specs(self.root), {})

    def test_all_pass(self):
        r = self.run_plan({'aIWO_bulk_s1_melt_3000K': {'d0': 0.6, 'dW': 0.9}})   # melt errors never count
        self.assertEqual(r['rollup']['overall'], 'PASS', CV.report_text(r))
        self.assertEqual(set(r['rollup']['structures'].values()), {'PASS'})
        self.assertEqual(r['rollup']['stop_rule_aIWO_2p0_s1'], 'NOT_TRIGGERED')
        st = {f['job']: f['status'] for f in r['frames']}
        self.assertEqual(st['aIWO_bulk_s1_melt_3000K'], 'REPORTED')
        self.assertEqual(sum(s == 'SCORED' for s in st.values()), 7)

    def test_missing_frame_incomplete(self):
        r = self.run_plan({'aIWO_0p7_s1_final': {'tar': 'absent'}})
        self.assertEqual(r['rollup']['overall'], 'INCOMPLETE')
        self.assertEqual(r['rollup']['structures']['aIWO_0p7_s1'], 'INCOMPLETE')

    def test_unscored_frame_incomplete(self):
        r = self.run_plan({'aIO_bulk_s1_quenched_300K': {'scf_kw': {'converged': False}}})
        self.assertEqual(r['rollup']['overall'], 'INCOMPLETE')
        self.assertEqual(r['rollup']['structures']['aIO_bulk_s1'], 'INCOMPLETE')

    def test_limit_failure_dominates(self):
        r = self.run_plan({'aIWO_bulk_s1_quenched_300K': {'d0': 0.01, 'dW': 0.27},
                           'aIWO_0p7_s1_final': {'tar': 'absent'}})
        self.assertEqual(r['rollup']['overall'], 'FAIL')
        self.assertEqual(r['rollup']['structures']['aIWO_bulk_s1'], 'FAIL')

    def test_stop_rule_triggered(self):
        r = self.run_plan({'aIWO_2p0_s1_final': {'d0': 0.31, 'dW': 0.31}})
        self.assertEqual(r['rollup']['stop_rule_aIWO_2p0_s1'], 'TRIGGERED')
        self.assertEqual(r['rollup']['overall'], 'FAIL')

    def test_stop_rule_undetermined(self):
        r = self.run_plan({'aIWO_2p0_s1_slab_annealed': {'scf_kw': {'converged': False}}})
        self.assertEqual(r['rollup']['stop_rule_aIWO_2p0_s1'], 'UNDETERMINED')
        self.assertEqual(r['rollup']['overall'], 'INCOMPLETE')

    def test_duplicate_plan_frame_refused(self):
        build_plan(self.root)
        specs = plan_specs(self.root) + [(os.path.join(self.root, 'aIWO_0p7_s1_final'), None)]
        with self.assertRaises(ValueError):
            CV.run(specs, {})


class TestCommandLine(Base):
    def cli(self, *args):
        out = os.path.join(self.root, 'result.json')
        p = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'compare_val.py'), *args, '--out', out],
                           capture_output=True, text=True)
        res = None
        if os.path.exists(out):
            with open(out) as f:
                res = json.load(f)
            os.remove(out)
        return p, res

    def test_cli_pass_fail_incomplete(self):
        build_plan(os.path.join(self.root, 'val'))
        p, res = self.cli('--val-root', os.path.join(self.root, 'val'))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(res['rollup']['overall'], 'PASS')
        self.assertEqual(res['definitions']['RYBOHR_TO_EV_A'], 13.605693122994 / 0.529177210903)
        self.assertEqual(len(res['comparator_sha256']), 64)
        self.assertIn('OVERALL: PASS', p.stdout)
        os.remove(os.path.join(self.root, 'val', 'aIWO_0p7_s1_final', CV.TARBALL))
        p, res = self.cli('--val-root', os.path.join(self.root, 'val'))
        self.assertEqual((p.returncode, res['rollup']['overall']), (3, 'INCOMPLETE'), p.stdout)
        extra, _ = make_job(self.root, 'aIWO_2p0_HfO2_s1', 'final')
        p, res = self.cli('--val-root', os.path.join(self.root, 'val'), extra)
        self.assertEqual([f['status'] for f in res['frames']][-1], 'OUT_OF_PLAN')

    def test_cli_label_map_option(self):
        job, _ = make_job(self.root, 'aIWO_2p0_s1', 'final', split=True, map_mode='atom_header', map_in_job=False)
        mp = os.path.join(self.root, 'aIWO_2p0_s1_final.tsv')
        p, res = self.cli(job, '--label-map', f'aIWO_2p0_s1_final={mp}')
        self.assertEqual(res['frames'][0]['status'], 'SCORED', p.stdout)
        self.assertEqual(p.returncode, 3)    # one plan frame only: the plan is INCOMPLETE
        p, res = self.cli(job)
        self.assertEqual(res['frames'][0]['status'], 'FAIL_NOT_SCORED')
        p, _ = self.cli(job, '--label-map', 'nojob=x.tsv')
        self.assertEqual(p.returncode, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
