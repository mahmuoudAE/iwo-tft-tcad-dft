"""rc3 regression tests: every reproducer of the rc2 review (scratchpad/rc2probe: false_pass FP, accounting_physics AP,
certs_provenance CP; merged defects A1-A26, B1-B7) as a test with the expected rejected / UNRESOLVED / INVALID
outcome. Genuine passing controls are in test_compare.py. Synthetic data only."""
import codecs
import contextlib
import io
import json
import math
import os
import shutil
import tarfile
import tempfile
import unittest

import numpy as np

from analysis.tests import builders as B
from analysis.tests import synth
from analysis.tests.helpers import QUALIFIED, analyse, manifest, qualification, result
from analysis.tests.synth import SynthCell, slab_structure
from analysis.tests.test_compare import series_inputs
from analysis import certify as CERT
from analysis import compare as C
from analysis import qeio
from analysis import register as R
from analysis.cli import main
from analysis.data import attach_lineage, from_tables, from_xml
from analysis.geometry import Structure, regions
from analysis.readout import gap_search, hh_cell, hi_cell
from analysis.report import cell_result
from analysis.section1 import Section1

U = {'scf_converged': False}


def rerun(rec, **edit):
    """A hand-edited copy of a sealed record (the seal is NOT recomputed)."""
    r = json.loads(json.dumps(rec))
    for k, v in edit.items():
        r[k] = v
    return r


# ---------------------------------------------------------------- end-to-end helpers (real CLI)
def run_cli(argv):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return code, buf.getvalue()


def manifest_for(st, seed=201):
    comp = st.composition()
    nh = comp.get('H', 0)
    return {'kind': 'W-doped', 'film': {'In': comp.get('In', 0), 'W': comp.get('W', 0), 'O': comp.get('O', 0) - nh // 2},
            'substrate': {}, 'passivation': 'dissociated-water', 'N_ex': st.formal_excess(), 'seed': seed}


def thick_donor(n_int=60, loc_w=False):
    st, idx = slab_structure(n_int=n_int)
    ALL = list(range(st.nat))
    sc = SynthCell(st)
    sc.add(-3.0, ALL).add(-2.5, ALL).add(-2.2, ALL).add(-2.0, idx['interior'])
    if loc_w:
        sc.add(-0.5, {idx['W']: 1.0}, w5d=0.9).add(0.0, ALL).add(0.5, ALL)
    else:
        sc.add(0.0, ALL).add(0.5, {idx['W']: 1.0}, w5d=0.9)
    sc.add(1.5, ALL)
    return sc, st, idx, (-0.5 if loc_w else 0.0)


def write_avg(d, st, value_ry=0.1, n=3001, pp=True, avg_in=True, keep_A=None):
    c = float(st.cell[2, 2])
    z = np.linspace(0, c / R.BOHR_A, n)[:-1]
    v = np.full_like(z, value_ry)
    if keep_A is not None:
        k = z * R.BOHR_A < keep_A
        z, v = z[k], v[k]
    np.savetxt(os.path.join(d, 'final_avg.dat'), np.c_[z, v, v])
    if avg_in:
        with open(os.path.join(d, 'avg_final.in'), 'w', newline='\n') as f:
            f.write('1\nfinal_v.pp\n1.0\n3000\n3\n4.0\n')
    if pp:
        with open(os.path.join(d, 'pp_final.in'), 'w', newline='\n') as f:
            f.write("&INPUTPP\n  prefix = 'slab', outdir = './tmp', filplot = 'final_v.pp', plot_num = 11\n/\n")


def xml_export(d, w_ry=0.001, fam='gaussian', settings=None, seed=201, loc_w=False, avg=True, lineage=True):
    os.makedirs(d, exist_ok=True)
    sc, st, idx, half = thick_donor(loc_w=loc_w)
    deg = w_ry * R.RY_EV
    data = sc.build(9.0, smearing=fam, degauss_ev=deg, ef=B._ef_for_half(fam, deg, half), settings=settings)
    synth.write_schema(os.path.join(d, 'data-file-schema.xml'), data, st)
    synth.write_atomic_proj(os.path.join(d, 'atomic_proj.xml'), data, st.species)
    smap = synth.state_map(st.species)
    with open(os.path.join(d, 'projwfc_map_final.dat'), 'w', newline='\n') as f:
        f.write('# map\n' + ''.join(f'{i} {a} {s} {w} {l} {m}\n' for i, (a, s, w, l, m) in enumerate(smap, 1)))
    if avg:
        write_avg(d, st)
    if lineage:
        synth.write_lineage(d, data)
    with open(os.path.join(d, 'manifest.json'), 'w', newline='\n') as f:
        json.dump(manifest_for(st, seed), f)
    ev = os.path.join(d, 'evidence.txt')
    with open(ev, 'w', newline='\n') as f:
        f.write('synthetic evidence\n')
    return d, ev, round(w_ry, 10), st


def certify(d, ev, width, name='aIWO_2p0_s1', out=None, smearing_width=True, extra=()):
    cert = out or os.path.join(d, 'cert.json')
    argv = ['certify', d, '--name', name, '--out', cert, '--manifest', os.path.join(d, 'manifest.json'),
            '--relaxation', 'converged', '--relaxation-evidence', ev, '--smearing', 'qualified',
            '--smearing-evidence', ev, '--geometry', 'polished', '--geometry-evidence', ev, '--compiled-by', 'test']
    if smearing_width:
        argv += ['--smearing-width', f'{width}']
    code, out_ = run_cli(argv + list(extra))
    return cert, code, out_


def gate(d, cert, name='aIWO_2p0_s1', extra=()):
    code, out = run_cli(['validate-cert', d, '--name', name, '--certificate', cert] + list(extra))
    return code, json.loads(out.split('GATE:')[0]), out


def cell(d, base, cert=None, name='aIWO_2p0_s1', extra=()):
    argv = ['cell', d, '--name', name, '--out', base] + (['--certificate', cert] if cert else []) + list(extra)
    code, out = run_cli(argv)
    return qeio.load_json(base + '.json'), out


class Tmp(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_rc3_')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def p(self, *a):
        return os.path.join(self.d, *a)


# ================================================================ Tier A
class TestA1SeriesControlBinding(unittest.TestCase):
    """A1: FP p02 / p02b / p02c / p25, CP p05."""

    @classmethod
    def setUpClass(cls):
        cls.cells, cls.ctrl = series_inputs()

    def outcome(self, ctrl):
        return C.hn_outcome({'cells': self.cells, 'controls': ctrl})

    def test_FP_p02_one_c3_report_in_every_slot(self):
        c3_20, c3_07 = self.ctrl['2.0']['C3'], self.ctrl['0.7']['C3']
        ctrl = {'2.0': {'C3': c3_20, 'C6': c3_20}, '0.7': {k: c3_07 for k in ('C3', 'C6', 'C1', 'C2', 'C5')}}
        r = self.outcome(ctrl)
        self.assertNotEqual(r['outcome'], 'CROSSOVER')
        for k in ('C6', 'C1', 'C2', 'C5'):
            self.assertIn('UNVERIFIED', r['controls']['0.7'][k])

    def test_FP_p02c_degenerate_c2_c5(self):
        t07 = self.cells['0.7']
        g07 = B.slab(0.05)
        self.assertIn(C.c2(t07, B.make(t07['cell'], geo=g07, loc_w=True, w_ry=0.005))['status'], ('INVALID', 'NOT A PASS'))
        _, nc, _ = B.c5_runs(t07['cell'], g07, loc_w=True)
        self.assertEqual(C.c5(t07, nc, nc)['status'], 'INVALID')
        ctrl = {l: dict(d) for l, d in self.ctrl.items()}
        ctrl['0.7']['C2'] = C.c2(t07, B.make(t07['cell'], geo=g07, loc_w=True, w_ry=0.005))
        ctrl['0.7']['C5'] = C.c5(t07, nc, nc)
        self.assertNotEqual(self.outcome(ctrl)['outcome'], 'CROSSOVER')

    def test_FP_p02c_genuine_c2_binds(self):
        r = self.outcome(self.ctrl)
        self.assertEqual(r['controls']['0.7']['C2'], 'ROBUST')
        self.assertEqual(r['outcome'], 'CROSSOVER')

    def test_FP_p25_stale_c1_binding(self):
        other = B.make('aIWO_0p7_s1', geo=B.slab(0.05), loc_w=True)          # another FINAL, same geometry
        _, parent, paired, maps = B.c1_set(main_geo=B.slab(0.05))
        stale = C.c1(other, paired, parent, maps)
        self.assertEqual(stale['status'], 'PASS')
        ctrl = {l: dict(d) for l, d in self.ctrl.items()}
        ctrl['0.7']['C1'] = stale
        r = self.outcome(ctrl)
        self.assertIn('UNVERIFIED', r['controls']['0.7']['C1'])
        self.assertNotIn(r['outcome'], ('CROSSOVER', 'NO CROSSOVER'))

    def test_CP_p05_inline_and_wrong_kind(self):
        t07 = self.cells['0.7']
        fake = {'status': 'PASS', 'kind': 'C6', 'provenance': {'inputs': [{'geometry_sha256': t07['geometry_sha256']}]}}
        ctrl = {l: dict(d) for l, d in self.ctrl.items()}
        ctrl['0.7']['C6'] = fake
        r = self.outcome(ctrl)
        self.assertIn('UNVERIFIED', r['controls']['0.7']['C6'])
        self.assertNotEqual(r['outcome'], 'CROSSOVER')
        ctrl['0.7']['C6'] = self.ctrl['0.7']['C1']                       # a genuine report of the wrong kind
        self.assertIn('UNVERIFIED', self.outcome(ctrl)['controls']['0.7']['C6'])

    def test_CP_p05_cli_inline_objects_refused(self):
        d = tempfile.mkdtemp(prefix='iwo_rc3_series_')
        try:
            paths = {}
            for lab, v in self.cells.items():
                for i, rec in enumerate(v if isinstance(v, list) else [v]):
                    p = os.path.join(d, f'cell_{lab}_{i}.json')
                    with open(p, 'w') as f:
                        json.dump(rec, f)
                    paths.setdefault(lab, []).append(p)
            ctrl_files = {}
            for lab, dd in self.ctrl.items():
                for k, v in dd.items():
                    for i, rep in enumerate(v if isinstance(v, list) else [v]):
                        p = os.path.join(d, f'ctrl_{lab}_{k}_{i}.json')
                        with open(p, 'w') as f:
                            json.dump(rep, f)
                        ctrl_files.setdefault(lab, {}).setdefault(k, []).append(p)
            spec_cells = {lab: (ps if lab == '2.0' else ps[0]) for lab, ps in paths.items()}
            sp = os.path.join(d, 'series.json')
            with open(sp, 'w') as f:
                json.dump({'cells': spec_cells, 'controls': ctrl_files}, f)
            code, out = run_cli(['series', sp, '--json', os.path.join(d, 'out.json')])
            res = qeio.load_json(os.path.join(d, 'out.json'))
            self.assertEqual(res['outcome'], 'CROSSOVER', res['controls'])
            n_reports = sum(len(v) for dd in ctrl_files.values() for v in dd.values())
            self.assertEqual(len(res['provenance']['inputs']), 6 + n_reports)            # controls are hashed inputs
            inline = dict(ctrl_files)
            inline['0.7'] = dict(inline['0.7'], C5={'status': 'PASS', 'kind': 'C5'})
            with open(sp, 'w') as f:
                json.dump({'cells': spec_cells, 'controls': inline}, f)
            code, out = run_cli(['series', sp, '--json', os.path.join(d, 'out2.json')])
            res = qeio.load_json(os.path.join(d, 'out2.json'))
            self.assertIn('UNVERIFIED', res['controls']['0.7']['C5'])
            self.assertNotEqual(res['outcome'], 'CROSSOVER')
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestA2Unconverged(Tmp):
    """A2: FP p01, p01b."""

    def test_FP_p01_unconverged_everywhere(self):
        g = B.slab(0.3)
        a, b = B.make(geo=g, settings=U), B.make(geo=g, w_ry=0.005, settings=U)
        self.assertEqual(a['H-N']['class'], 'UNRESOLVED')
        self.assertTrue(any('convergence not shown' in x for x in a['H-N']['unresolved_checks']))
        self.assertNotEqual(C.c3(a, b)['status'], 'PASS')
        self.assertNotEqual(C.c5(*B.c5_runs('aIWO_0p7_s1', g, common=U))['status'], 'PASS')
        _, parent, paired, _ = B.c1_set()
        geo, _ = B.c1_paired(B.c1_parent(), 0)
        full = B.make(paired[0]['cell'], geo=geo, loc_w=True, settings=U,
                      man_extra={'construction': paired[0]['run_qualification']['construction']})
        self.assertNotEqual(C.c2(full, B.diluted(geo, full, settings=U))['status'], 'ROBUST')
        s1, s2 = B.make('aIWO_2p0_s1', geo=B.slab(0.01), settings=U), B.make('aIWO_2p0_s2', geo=B.slab(0.02), settings=U)
        self.assertEqual(set(C.hg_score(s1, s2)['P2_f_ext'].values()), {'UNRESOLVED'})
        self.assertIsNone(a['alignment']['aligned_host_edge_eV'])
        for blk in ('host_gap', 'H-H', 'H-I', 'gap_states'):                              # every read-out
            self.assertTrue(a[blk]['unresolved'], blk)

    def test_FP_p01b_cli(self):
        e1, ev1, w1, _ = xml_export(self.p('w001'), settings=U)
        e5, ev5, w5, _ = xml_export(self.p('w005'), w_ry=0.005, settings=U)
        c1 = certify(e1, ev1, w1)[0]
        c5 = certify(e5, ev5, w5)[0]
        r1, txt = cell(e1, self.p('c1'), c1)
        self.assertFalse(r1['run_settings']['scf_converged'])
        self.assertEqual(r1['H-N']['class'], 'UNRESOLVED')
        cell(e5, self.p('c5'), c5)
        code, out = run_cli(['compare', 'c3', self.p('c1.json'), self.p('c5.json')])
        self.assertNotIn('STATUS: PASS', out)


class TestA3SmearingCertificate(Tmp):
    """A3: FP p19, AP p05, CP p03, CP p04."""

    def test_FP_p19_no_width_and_mv(self):
        e, ev, w, _ = xml_export(self.p('g5'), w_ry=0.005)
        cert = certify(e, ev, w, smearing_width=False)[0]
        code, q, out = gate(e, cert)
        self.assertEqual(code, 1)
        self.assertFalse(q['smearing_qualified'])
        e, ev, w, _ = xml_export(self.p('mv'), w_ry=0.01, fam='mv')
        cert = certify(e, ev, w)[0]
        code, q, out = gate(e, cert)
        self.assertEqual(code, 1)
        self.assertTrue(any('not Gaussian' in x for x in q['problems']))
        r, _ = cell(e, self.p('mvcell'), cert)
        self.assertEqual(r['H-N']['class'], 'UNRESOLVED')

    def test_AP_p05_api(self):
        for fam, w_ry, width in (('mv', 0.001, 0.001), ('mv', 0.001, None), ('gaussian', 0.002, None)):
            d = self.p(f'{fam}_{w_ry}_{width}')
            e, ev, _, _ = xml_export(d, w_ry=w_ry, fam=fam)
            data, st = from_xml(*(os.path.join(e, n) for n in ('data-file-schema.xml', 'atomic_proj.xml',
                                                                 'projwfc_map_final.dat')))
            attach_lineage(data, [e])
            cert = os.path.join(e, 'c.json')
            CERT.compile_certificate('aIWO_2p0_s1', data, st, cert, manifest=qeio.load_json(os.path.join(e, 'manifest.json')),
                                     relaxation=('converged', [ev], None),
                                     smearing=('qualified', [ev], {'width_Ry': width} if width is not None else None),
                                     geometry=('polished', [ev], None))
            q = CERT.validate(cert, 'aIWO_2p0_s1', data, st)
            self.assertFalse(q['smearing_qualified'], (fam, w_ry, width))
            self.assertFalse(CERT.gate_valid(q))

    def test_CP_p03_width_zero_stored(self):
        e, ev, w, _ = xml_export(self.p('x'), w_ry=0.005)
        cert = certify(e, ev, 0.0)[0]
        self.assertEqual(qeio.load_json(cert)['smearing']['width_Ry'], 0.0)
        code, q, _ = gate(e, cert)
        self.assertEqual(code, 1)

    def test_CP_p04_table_width_source(self):
        work = self.p('work')
        os.makedirs(work)
        sc, st, idx, _ = thick_donor()
        data = sc.build(9.0, smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        r = synth.run_d24_exporter(work, data, st)
        self.assertEqual(r.returncode, 0, r.stderr)
        exp = self.p('export')
        os.makedirs(exp)
        for n in ('occ_kw_final.dat', 'proj_atoms_final.dat'):
            shutil.copy(os.path.join(work, n), exp)
        synth.write_scf_in(os.path.join(exp, 'scf.in'), st)
        txt = open(os.path.join(exp, 'scf.in')).read().replace(
            '  ibrav = 0,', "  ibrav = 0, occupations = 'smearing', smearing = 'gaussian', degauss = 0.005,")
        with open(os.path.join(exp, 'scf.in'), 'w', newline='\n') as f:
            f.write(txt)
        with self.assertRaises(ValueError):
            from_tables(exp)
        synth.write_scf_in(os.path.join(exp, 'scf.in'), st)                   # scf.in without degauss
        d, _ = from_tables(exp)
        self.assertAlmostEqual(d.settings['degauss_Ry'], 0.001, places=9)    # the width actually used
        with open(os.path.join(exp, 'manifest.json'), 'w') as f:
            json.dump(manifest_for(st), f)
        ev = os.path.join(exp, 'ev.txt')
        with open(ev, 'w') as f:
            f.write('evidence\n')
        cert = certify(exp, ev, 0.02, extra=('--source', 'table'))[0]
        code, q, _ = gate(exp, cert, extra=('--source', 'table'))
        self.assertEqual(code, 1)
        self.assertFalse(q['smearing_qualified'])


class TestA4A5A6Constructions(unittest.TestCase):
    """A4 (FP p03, p17), A5 (FP p04, CP p13), A6 (FP p05)."""

    def test_FP_p03_c5_roles(self):
        g = B.slab(0.17)
        paw, nc, hse = B.c5_runs('aIWO_0p7_s1', g)
        self.assertEqual(C.c5(paw, nc, nc)['status'], 'INVALID')
        relabel = dict(nc, cell='aIWO_0p7_s1_HSE06')                        # edited record: seal broken
        self.assertEqual(C.c5(paw, nc, relabel)['status'], 'INVALID')
        self.assertEqual(C.c5(paw, B.make('x', geo=g), B.make('y', geo=g))['status'], 'INVALID')   # three PAW-PBE

    def test_FP_p17_spin_in_c3_c5(self):
        g = B.slab(0.17)
        ref = B.make(geo=g)
        s = B.make(geo=g, w_ry=0.005, nspin=2, settings={'lsda': True})
        self.assertEqual(C.c3(ref, s)['status'], 'INVALID')
        paw, nc, hse = B.c5_runs('aIWO_0p7_s1', g)
        hse2 = B.make('h', geo=g, nspin=2, settings=dict(hse['run_settings'], lsda=True))
        self.assertEqual(C.c5(paw, nc, hse2)['status'], 'INVALID')

    def test_FP_p04_CP_p13_c2_not_a_dilution(self):
        _, parent, paired, _ = B.c1_set()
        full = paired[0]
        geo, _ = B.c1_paired(B.c1_parent(), 0)
        self.assertIn(C.c2(full, B.make(full['cell'], geo=geo, w_ry=0.005, loc_w=True))['status'], ('INVALID', 'NOT A PASS'))
        self.assertEqual(C.c2(full, paired[1])['status'], 'INVALID')
        d = B.diluted(geo, full, loc_w=True, settings={'ecutwfc_Ry': 30.0})
        self.assertEqual(C.c2(full, d)['status'], 'INVALID')
        d = B.diluted(geo, full, loc_w=True, w_ry=0.005)
        self.assertEqual(C.c2(full, d)['status'], 'INVALID')
        d = B.diluted(geo, full, loc_w=True, settings={'functional': 'LDA'})
        self.assertEqual(C.c2(full, d)['status'], 'INVALID')

    def test_FP_p05_c1_sets(self):
        main, parent, paired, maps = B.c1_set()
        extra = B.make('aIWO_0p7_C1d', geo=B.c1_paired(B.c1_parent(), 3)[0], loc_w=False)
        self.assertEqual(C.c1(main, paired + [extra], parent, maps + [maps[0]])['status'], 'INVALID')
        mv = B.make('aIWO_0p7_s1', geo=B.slab(0.4), loc_w=True, seed=main['run_qualification']['seed'], geometry='mv')
        q1 = B.make('aIWO_0p7_s2', geo=B.slab(0.9), loc_w=True)
        q2 = B.make('aIWO_0p7_s3', geo=B.slab(1.1), loc_w=True)
        self.assertEqual(C.c1(main, [mv, q1, q2], parent, maps)['status'], 'INVALID')


class TestA7Alignment(Tmp):
    """A7: FP p18, CP p01, CP p14."""

    def test_FP_p18_CP_p01_avg_bound_and_plot_num(self):
        e, ev, w, st = xml_export(self.p('x'))
        cert = certify(e, ev, w)[0]
        self.assertTrue(any(k in qeio.load_json(cert)['run_files'] for k in ('final_avg.dat', 'avg_final.in',
                                                                             'pp_final.in')))
        code, q, _ = gate(e, cert)
        self.assertEqual(code, 0, q)
        r, _ = cell(e, self.p('before'), cert)
        self.assertTrue(r['alignment']['valid'], r['alignment'])
        self.assertIsNotNone(r['alignment']['aligned_host_edge_eV'])
        write_avg(e, st, value_ry=0.2)                                        # swapped after certification
        code, q, _ = gate(e, cert)
        self.assertEqual(code, 1)
        r, _ = cell(e, self.p('after'), cert)
        self.assertIsNone(r['alignment']['aligned_host_edge_eV'])
        write_avg(e, st, value_ry=0.1, pp=False)
        os.remove(os.path.join(e, 'pp_final.in'))
        r, _ = cell(e, self.p('nopp'), cert)
        self.assertFalse(r['alignment']['valid'])
        self.assertTrue(any('plot_num' in x for x in r['alignment']['unresolved']))

    def test_CP_p14_truncated_avg(self):
        e, ev, w, st = xml_export(self.p('x'))
        write_avg(e, st, keep_A=20.0)
        cert = certify(e, ev, w)[0]
        r, _ = cell(e, self.p('t'), cert)
        self.assertFalse(r['alignment']['valid'])
        self.assertTrue(any('truncated' in x for x in r['alignment']['unresolved']))
        self.assertIsNone(r['alignment']['aligned_host_edge_eV'])


class TestA8SearchOrder(Tmp):
    """A8: CP p16."""

    def test_CP_p16_tarball_then_neighbours(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))

        def build(loc_w):
            sc = SynthCell(st)
            sc.add(-3.0, ALL).add(-2.5, ALL).add(-2.2, ALL).add(-2.0, idx['interior'])
            if loc_w:
                sc.add(-0.5, {idx['W']: 1.0}, w5d=0.9).add(0.0, ALL).add(0.5, ALL)
                return sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=-0.5)
            sc.add(0.0, ALL).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
            return sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        X, Y = build(False), build(True)
        stage = self.p('stageX', 'tmp', 'slab.save')
        os.makedirs(stage)
        synth.write_schema(os.path.join(stage, 'data-file-schema.xml'), X, st)
        synth.write_atomic_proj(os.path.join(stage, 'atomic_proj.xml'), X, st.species)
        synth.write_projwfc_out(self.p('stageX', 'projwfc_final.out'), X, st.species)
        tgz = self.p('cellX_final_results.tar.gz')
        with tarfile.open(tgz, 'w:gz') as t:
            t.add(self.p('stageX', 'tmp'), arcname='tmp')
            t.add(self.p('stageX', 'projwfc_final.out'), arcname='projwfc_final.out')
        synth.write_schema(self.p('data-file-schema.xml'), Y, st)
        synth.write_atomic_proj(self.p('atomic_proj.xml'), Y, st.species)
        r, _ = cell(tgz, self.p('x'), name='cellX')
        self.assertEqual(r['H-N']['class_if_resolved'], 'DONOR')               # the tarball's own run X
        self.assertTrue(all(v['origin'].startswith('tarball:') for k, v in r['provenance']['files'].items()
                            if k.startswith(('data-file', 'atomic_proj'))))


class TestA9MissingW5dColumns(Tmp):
    """A9: FP p20."""

    def test_FP_p20(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL).add(-2.5, ALL).add(-2.2, ALL).add(-2.0, idx['interior'])
        sc.add(0.0, ALL).add(0.2, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        data = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        r = synth.run_d24_exporter(self.d, data, st)
        self.assertEqual(r.returncode, 0, r.stderr)
        p = self.p('proj_atoms_final.dat')
        L = open(p).read().splitlines()
        cols = next(l for l in L if l.startswith('# columns:')).split(':', 1)[1].split()
        nW = sum(1 for c in cols if c.startswith('d_W'))
        self.assertEqual(nW, 1)
        out = []
        for l in L:
            if l.startswith('# columns:'):
                l = '# columns: ' + ' '.join(c for c in cols if not c.startswith('d_W'))
            elif not l.startswith('#') and l.strip():
                l = ' '.join(l.split()[:len(l.split()) - nW])
            out.append(l)
        with open(p, 'w', newline='\n') as f:
            f.write('\n'.join(out) + '\n')
        with self.assertRaises(ValueError):
            from_tables(self.d)


class TestA10A11Series(unittest.TestCase):
    """A10 (FP p11, p21, CP p21), A11 (CP p12), A16 (AP p06)."""

    @classmethod
    def setUpClass(cls):
        cls.cells, cls.ctrl = series_inputs()

    def outcome(self, cells, ctrl=None):
        return C.hn_outcome({'cells': cells, 'controls': self.ctrl if ctrl is None else ctrl})

    def test_FP_p11_CP_p21_labels_and_modes(self):
        cells = dict(self.cells)
        cells['bulk'] = B.make('aIWO_2p0_s3', geo=B.slab(0.4))                     # slab in the bulk slot
        r = self.outcome(cells)
        self.assertEqual(r['outcome'], 'UNRESOLVED')
        self.assertTrue(any('mode' in x or 'thickness' in x for x in r['unresolved_checks']))
        cells = dict(self.cells)
        cells['0.7'], cells['2.0'] = self.cells['2.0'][0], [self.cells['0.7'], B.make('aIWO_0p7_s2', geo=B.slab(0.6))]
        self.assertEqual(self.outcome(cells)['outcome'], 'UNRESOLVED')
        cells = dict(self.cells)
        cells['1'] = B.make('aIWO_1p0_s2', geo=B.slab(0.7), loc_w=True)
        cells['0.70'] = B.make('aIWO_0p7_s2', geo=B.slab(0.8), loc_w=True)
        r = self.outcome(cells)
        self.assertEqual(r['outcome'], 'UNRESOLVED')
        self.assertTrue(any('not one of' in x for x in r['unresolved_checks']))

    def test_FP_p11d_optional_15_reversal_noted(self):
        cells, ctrl = series_inputs(t07_loc=False, w08=0.5)
        cells['1.5'] = B.make('aIWO_1p5_s1', geo=B.slab(0.9), loc_w=True)
        r = C.hn_outcome({'cells': cells, 'controls': ctrl})
        self.assertTrue(r['reversal'])
        self.assertTrue(any('non-monotonic' in n for n in r['notes']))

    def test_FP_p21_held_checks(self):
        cells = dict(self.cells)
        cells['2.0'] = [self.cells['2.0'][0], B.make('aIO_2p0_s2', geo=B.slab(0.2, w=False), kind='undoped')]
        self.assertEqual(self.outcome(cells)['outcome'], 'UNRESOLVED')
        cells = dict(self.cells)
        cells['2.0'] = self.cells['2.0'][:1]
        self.assertEqual(self.outcome(cells)['outcome'], 'UNRESOLVED')
        cells['2.0'] = [self.cells['2.0'][0], self.cells['2.0'][0]]
        self.assertEqual(self.outcome(cells)['outcome'], 'UNRESOLVED')
        cells = dict(self.cells)
        cells['0.7'] = B.make('aIWO_0p7_s1', geo=B.slab(0.05), loc_w=True, geometry='mv')
        self.assertNotEqual(self.outcome(cells)['outcome'], 'CROSSOVER')
        nc_cells, nc_ctrl = series_inputs(t07_loc=False, w08=0.5, polish_10=False)       # (ii) 1.0 nm on MV
        self.assertNotEqual(C.hn_outcome({'cells': nc_cells, 'controls': nc_ctrl})['outcome'], 'NO CROSSOVER')

    def test_CP_p12_unverified_nex_override(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL).add(-2.5, ALL).add(-2.2, ALL).add(-2.0, idx['interior'])
        sc.add(0.0, ALL).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        data = sc.build(9.0, smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        c = Section1(data, st, name='aIWO_0p7_s1', nex=0)
        r = cell_result(c, 'xml')
        self.assertEqual(r['H-N']['class'], 'UNRESOLVED')
        self.assertEqual(r['H-N']['class_if_resolved'], 'N/A')
        self.assertTrue(r['H-N']['unresolved_checks'])
        self.assertNotIn('P3_comp_no_occupied_localised_W_state_in_gap', r['H-G'])     # compensated branch unused
        cells = dict(self.cells, **{'0.7': r})
        self.assertEqual(self.outcome(cells)['outcome'], 'UNRESOLVED')

    def test_AP_p06_mixed_widths(self):
        cells = dict(self.cells)
        cells['1.0'] = B.make('aIWO_1p0_s1', geo=B.slab(0.03), w_ry=0.005)
        r = self.outcome(cells)
        self.assertEqual(r['outcome'], 'UNRESOLVED')
        self.assertEqual(len(r['widths']), 2)
        self.assertTrue(any('common width' in x for x in r['unresolved_checks']))


class TestA12HK(unittest.TestCase):
    """A12: FP p07, p23."""

    def setUp(self):
        self.t07 = B.make('aIWO_0p7_s1', geo=B.slab(0.03), vb=-3.0)
        self.s1 = B.make('aIWO_2p0_s1', geo=B.slab(0.01), vb=-2.0, V=1.0)
        self.s2 = B.make('aIWO_2p0_s2', geo=B.slab(0.02), vb=-2.1, V=0.95)

    def test_FP_p07(self):
        bad = B.make('aIWO_0p7_s1', geo=B.slab(0.03), vb=-3.0, ef=-0.05)                # accounting fails
        self.assertEqual(bad['excess_accounting']['check'], 'FAIL')
        self.assertEqual(C.hk(bad, self.s1, self.s2)['Eg_difference']['status'], 'UNRESOLVED')
        far = B.make('aIWO_2p0_s2', geo=B.slab(0.02), vb=-2.6)                          # spread 0.60 eV
        r = C.hk(self.t07, self.s1, far)['Eg_difference']
        self.assertFalse(r['spread_in_registered_range'])
        self.assertEqual(r['status'], 'FAIL')
        self.assertEqual(C.hk(self.t07, self.s1, None)['status'], 'INVALID')            # one seed
        same = B.make('aIWO_2p0_s2', geo=B.slab(0.025), vb=-2.1, seed=self.s1['run_qualification']['seed'],
                      geometry='mv')
        self.assertEqual(C.hk(self.t07, self.s1, same)['Eg_difference']['status'], 'UNRESOLVED')

    def test_FP_p23_seed_order(self):
        s2 = B.make('aIWO_2p0_s2', geo=B.slab(0.02), vb=-2.1, V=0.55)                   # rise 0.05 eV vs 0.50
        t10 = B.make('aIWO_1p0_s1', geo=B.slab(0.04), V=0.5)
        a = C.hk(self.t07, self.s1, s2, t10)['aligned_edge_rise']
        b = C.hk(self.t07, s2, self.s1, t10)['aligned_edge_rise']
        self.assertEqual(a['status'], b['status'])
        self.assertEqual(a['status'], 'UNRESOLVED')


class TestA13A18HIHH(unittest.TestCase):
    """A13 (AP p10), A18 (FP p09, p24), B7."""

    def test_AP_p10_outer_face_state(self):
        atoms = [('O', 10.0), ('Al', 10.5), ('O', 11.0), ('In', 11.5), ('Al', 12.0), ('In', 12.8), ('O', 13.0), ('Al', 14.0),
                 ('O', 15.0), ('Al', 16.0), ('O', 17.0), ('Al', 17.5), ('In', 19.0), ('O', 20.0), ('In', 21.0),
                 ('O', 22.0), ('In', 23.0), ('W', 24.0), ('In', 25.0), ('O', 26.0), ('In', 27.0), ('O', 28.0),
                 ('In', 29.0), ('O', 30.0), ('H', 31.0), ('H', 9.0)]
        sp, pos = [], []
        for rep in (0, 1):
            for i, (s, z) in enumerate(atoms):
                sp.append(s)
                pos.append([(i % 4) * 2.0 + 8.0 * rep, (i // 4 % 4) * 2.0, z])
        st = Structure(sp, pos, [[16, 0, 0], [0, 8, 0], [0, 0, 50.0]])
        ALL = list(range(st.nat))
        interior = [15, 16, 17, 18, 19, 41, 42, 43, 44, 45]
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1).add(-2.5, ALL, f=1).add(-2.2, ALL, f=1).add(-2.0, interior, f=1)
        sc.add(-0.1, {9: 0.40, 3: 0.60}, f=1)
        sc.add(0.0, ALL).add(1.5, ALL)
        c = Section1(sc.build(10.0), st, name='aIWO_2p0_Al2O3_s2', manifest={'kind': 'undoped', 'N_ex': 0})
        h = hi_cell(c)
        self.assertEqual(h['outer_face_states']['n_qualifying'], 1)
        self.assertEqual(h['n_qualifying'], 0)
        self.assertEqual(h['n_removed_as_outer_face_states'], 1)
        self.assertIn('outer_face_film_cations_per_nm2', c.reg)                          # B7

    def test_FP_p09_p24_roles(self):
        iface = B.make('aIWO_2p0_Al2O3_s2', geo=B.interface())
        v1 = B.make('aIWO_2p0_s1', geo=B.slab(0.01), seed=11)
        v1b = B.make('aIWO_2p0_s2', geo=B.slab(0.02), seed=11)
        self.assertEqual(C.hi(iface, v1, v1b)['status'], 'INVALID')                     # same seed
        x = B.make('aIWO_1p0_Al2O3_s2', geo=B.interface(0.3))
        y = B.make('aIWO_1p0_s1', geo=B.slab(0.03))
        self.assertEqual(C.hi(iface, x, y)['status'], 'INVALID')                        # interface + 1.0 nm as vacuum
        slab_if = B.make('aIWO_2p0_Al2O3_s2', geo=B.slab(0.7))
        v2 = B.make('aIWO_2p0_s2', geo=B.slab(0.02))
        self.assertEqual(C.hi(slab_if, v1, v2)['status'], 'INVALID')                    # slab as the interface cell
        t10 = B.make('aIWO_1p0_Al2O3_s2', geo=B.interface(0.1))
        a = B.make('aIWO_1p0_s1', geo=B.slab(0.03))
        b = B.make('aIWO_1p0_s2', geo=B.slab(0.04))
        self.assertEqual(C.hi(t10, a, b)['status'], 'NOT REGISTERED')                  # never SUPPORTED off 2.0 nm
        oh1 = B.make('aIWO_2p0_s1', geo=B.slab(0.01), seed=21)
        oh2 = B.make('aIWO_2p0_s1b', geo=B.slab(0.02), seed=21)
        self.assertEqual(C.hh(oh1, oh2)['status'], 'INVALID')                           # passivated 'bare' control


class TestA14A22A23C3C6(unittest.TestCase):
    """A14 (FP p06), A22 (FP p17, p17b, p22), A23 (AP p09)."""

    def test_FP_p06(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))

        def fixed():
            sc = SynthCell(st)
            sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
            sc.add(0.0, ALL, f=0.5).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
            return result(sc, 9.0)
        self.assertEqual(C.c3(fixed(), fixed())['status'], 'INVALID')
        g = B.slab(0.2)
        self.assertEqual(C.c3(B.make(geo=g, w_ry=0.002), B.make(geo=g, w_ry=0.005))['status'], 'INVALID')
        self.assertEqual(C.c3(B.make(geo=g, w_ry=0.01, fam='mv'), B.make(geo=g, w_ry=0.02, fam='mv'))['status'],
                         'INVALID')

    def test_FP_p17_two_localised_starts(self):
        g = B.slab(0.13)
        ref = B.make(geo=g, etot=-10.0)
        sp = lambda m: [dict(s, starting_magnetization=m if s['name'] == 'W' else 0.0) for s in B.PAW_SPECIES]
        a = B.make(geo=g, nspin=2, etot=-10.002, settings={'lsda': True, 'species': sp(0.5)})
        b = B.make(geo=g, nspin=2, etot=-10.001, settings={'lsda': True, 'species': sp(0.6)})
        self.assertEqual(C.c6(a, b, ref)['status'], 'INVALID')

    def test_FP_p17b_split_label_localised_start_passes(self):
        g = B.slab(0.13)
        ref = B.make(geo=g, etot=-10.0)
        a, b = B.spin_starts('aIWO_2p0_s1', g)
        self.assertEqual(C.c6(a, b, ref)['status'], 'PASS')

    def test_FP_p22_energy_tie(self):
        g = B.slab(0.13)
        ref = B.make(geo=g, etot=-10.0)
        for de in (0.0, 1e-12, -1e-12):
            loc, _ = B.spin_starts('aIWO_2p0_s1', g, loc_w=True, e_loc=-10.001 + de)
            _, deloc = B.spin_starts('aIWO_2p0_s1', g, e_deloc=-10.001)
            self.assertEqual(C.c6(deloc, loc, ref)['status'], 'UNRESOLVED')
            self.assertEqual(C.c6(loc, deloc, ref)['status'], 'UNRESOLVED')

    def test_AP_p09_absolute_edges(self):
        g = B.slab(0.2)
        a = B.make(geo=g)
        self.assertEqual(C.c3(a, B.make(geo=g, w_ry=0.002, shift=0.2))['status'], 'FAIL')
        cells = {}
        for name, kind in (('aIO_2p0_s1', 'undoped'), ('aIWO_2p0_s1', 'W-doped'), ('aIWO_2p0_comp_s1', 'compensated')):
            gg = B.slab(0.3 + len(cells) * 0.01, w=kind != 'undoped')
            cells[name] = {0.001: B.make(name, geo=gg, kind=kind), 0.002: B.make(name, geo=gg, kind=kind, w_ry=0.002,
                                                                                 shift=0.2)}
        self.assertIsNone(C.smearing_audit(cells)['provisional_width_candidate_Ry'])


class TestA15Convention(unittest.TestCase):
    """A15: FP p10 / p10b (raw-convention records are refused by comparisons)."""

    def test_FP_p10(self):
        g = B.slab(0.2)
        a = B.make(geo=g, w5d_convention='raw')
        b = B.make(geo=g, w_ry=0.005, w5d_convention='raw')
        self.assertEqual(a['H-N']['W5d_convention'], 'raw')
        self.assertEqual(C.c3(a, b)['status'], 'INVALID')
        self.assertEqual(C.c3(B.make(geo=g), b)['status'], 'INVALID')


class TestA17HG(unittest.TestCase):
    """A17: FP p08."""

    def test_FP_p08(self):
        s1_fail = B.make('aIWO_2p0_s1', geo=B.slab(0.01), loc_w=True)
        s2_pass = B.make('aIWO_2p0_s1', geo=B.slab(0.02))                             # same name, other seed
        r = C.hg_score(s1_fail, s2_pass)
        self.assertEqual(r['P2_f_ext'], {'s1': 'FAIL', 's2': 'PASS'})
        s1 = B.make('aIWO_2p0_s1', geo=B.slab(0.03))
        s1mv = B.make('aIWO_2p0_s2', geo=B.slab(0.035), seed=s1['run_qualification']['seed'], geometry='mv')
        self.assertEqual(set(C.hg_score(s1, s1mv)['P2_f_ext'].values()), {'UNRESOLVED'})
        comp_slot = B.make('aIWO_2p0_comp_s1', geo=B.slab(0.04))                        # W-doped manifest
        a1 = B.make('aIO_2p0_s1', geo=B.slab(0.05))                                     # W-doped, not aIO
        a2 = B.make('aIO_2p0_s2', geo=B.slab(0.06))
        r = C.hg_score(s1, B.make('aIWO_2p0_s2', geo=B.slab(0.07)), comp_slot, a1, a2)
        self.assertEqual(r['claude_Eg_comp']['status'], 'UNRESOLVED')
        self.assertEqual(r['P3_comp']['status'], 'UNRESOLVED')


class TestA19Trust(Tmp):
    """A19: CP p06, CP p11, FP p15."""

    def test_CP_p06_edited_reasons(self):
        g = B.slab(0.2)
        a, b = B.make(geo=g, certified=False), B.make(geo=g, w_ry=0.005, certified=False)
        self.assertEqual(C.c3(a, b)['status'], 'UNRESOLVED')
        ea = rerun(a)
        eb = rerun(b)
        ea['run_qualification']['reasons'] = []
        eb['run_qualification']['reasons'] = []
        self.assertEqual(C.c3(ea, eb)['status'], 'INVALID')                            # seal broken
        ea['self_sha256'] = CERT.canonical_sha256(ea)                                   # re-sealed by hand
        eb['self_sha256'] = CERT.canonical_sha256(eb)
        self.assertEqual(C.c3(ea, eb)['status'], 'UNRESOLVED')                          # reasons recomputed

    def test_CP_p11_stale_inputs(self):
        g = B.slab(0.2)
        a, b = B.make(geo=g), B.make(geo=g, w_ry=0.005)
        old = rerun(b, schema='iwo-amorph-analysis/cell/1')
        old['provenance']['code_sha256'] = '0' * 64
        old['self_sha256'] = CERT.canonical_sha256(old)
        r = C.c3(a, old)
        self.assertEqual(r['status'], 'INVALID')
        self.assertTrue(any('schema' in x for x in r['unresolved_checks']))
        self.assertTrue(any('other code' in x for x in r['unresolved_checks']))

    def test_FP_p15_nan(self):
        g = B.slab(0.13)
        ref = B.make(geo=g, etot=-10.0)
        a, b = B.spin_starts('aIWO_2p0_s1', g)
        an = rerun(a, total_energy_Ry=float('nan'))
        self.assertEqual(C.c6(an, b, ref)['status'], 'INVALID')
        x, y = B.make(geo=g), B.make(geo=g, w_ry=0.005)
        y = rerun(y)
        y['H-N']['Delta_W']['value_eV'] = float('nan')
        self.assertEqual(C.c3(x, y)['status'], 'INVALID')
        iface = rerun(B.make('aIWO_2p0_Al2O3_s2', geo=B.interface()))
        iface['alignment']['aligned_host_edge_eV'] = float('nan')
        paths = []
        for n, rec in (('if', iface), ('v1', B.make('aIWO_2p0_s1', geo=B.slab(0.01))),
                       ('v2', B.make('aIWO_2p0_s2', geo=B.slab(0.02)))):
            p = self.p(n + '.json')
            with open(p, 'w') as f:
                json.dump(rec, f)                                                       # writes the NaN token
            paths.append(p)
        code, out = run_cli(['compare', 'hi'] + paths)
        self.assertIn('STATUS: INVALID', out)


class TestA20A21Occupation(unittest.TestCase):
    """A20 (FP p16), A21 (AP p08, p08b)."""

    def test_FP_p16_minority_occupied(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        top = idx['top']
        for f_trap, expect in ((0.5, 1), (0.49, 1), (0.004, 0)):
            sc = SynthCell(st)
            sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
            sc.add(-0.1, {top[-1]: 0.9, top[-2]: 0.1}, f=f_trap)
            sc.add(0.0, ALL, f=0.5 - f_trap).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
            c = analyse(sc, 9.0, man=manifest())
            self.assertEqual(hh_cell(c)['n_qualifying'], expect, f_trap)

    def test_AP_p08_fixed_without_gap(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st, nks=2, wk=[1.0, 1.0])
        for k in (0, 1):
            sc.add(-3.0, ALL, f=1, k=k).add(-2.5, ALL, f=1, k=k).add(-2.2, ALL, f=1, k=k).add(-2.0, idx['interior'], f=1, k=k)
        sc.add(-0.4, idx['interior'], f=1, k=0).add(0.2, ALL, f=0, k=0).add(1.5, ALL, k=0)
        sc.add(0.6, idx['interior'], f=1, k=1).add(0.9, ALL, f=0, k=1).add(1.8, ALL, k=1)
        c = Section1(sc.build(10.0), st, name='aIO_2p0_s1', manifest={'kind': 'undoped', 'N_ex': 0})
        self.assertTrue(any('A15: fixed occupations without a global gap' in x for x in c.reasons))
        self.assertLess(c.occ_info['global_gap_eV'], 0)
        sc = SynthCell(st, nks=2, wk=[1.0, 1.0])
        for k in (0, 1):
            sc.add(-3.0, ALL, f=1, k=k).add(-2.5, ALL, f=1, k=k).add(-2.2, ALL, f=1, k=k).add(-2.0, idx['interior'], f=1, k=k)
        sc.add(0.0, ALL, f=0.5, k=0).add(0.2, {idx['W']: 1.0}, w5d=0.9, f=0.0, k=0).add(1.5, ALL, k=0)
        sc.add(0.6, ALL, f=0.5, k=1).add(0.9, {idx['W']: 1.0}, w5d=0.9, f=0.0, k=1).add(1.8, ALL, k=1)
        c = Section1(sc.build(9.0), st, name='aIWO_2p0_s1', manifest={'kind': 'W-doped', 'N_ex': 1})
        r = cell_result(c, 'synthetic', qual=qualification(manifest()))
        self.assertEqual(r['H-N']['class'], 'UNRESOLVED')
        self.assertTrue(any(x.startswith('A15') for x in r['H-N']['unresolved_checks']))


class TestA24Audit(unittest.TestCase):
    """A24: FP p13."""

    def cells(self, dx=0.5):
        out = {}
        for i, (name, kind) in enumerate((('aIO_2p0_s1', 'undoped'), ('aIWO_2p0_s1', 'W-doped'),
                                          ('aIWO_2p0_comp_s1', 'compensated'))):
            g = B.slab(dx + 0.01 * i, w=kind != 'undoped')
            out[name] = {w: B.make(name, geo=g, kind=kind, w_ry=w) for w in (0.001, 0.002, 0.005)}
        return out

    def test_FP_p13(self):
        cells = self.cells()
        self.assertEqual(C.smearing_audit(cells)['provisional_width_candidate_Ry'], 0.005)
        bad = self.cells()
        g = B.slab(0.5, w=False)
        bad['aIO_2p0_s1'][0.005] = B.make('aIO_2p0_s1', geo=g, kind='undoped', w_ry=0.002)   # filed under 0.005
        r = C.smearing_audit(bad)
        self.assertIsNone(r['provisional_width_candidate_Ry'])
        one = self.cells()['aIWO_2p0_s1']
        r = C.smearing_audit({'aIO_2p0_s1': one, 'aIWO_2p0_s1': one, 'aIWO_2p0_comp_s1': one})
        self.assertIsNone(r['provisional_width_candidate_Ry'])
        other = self.cells()
        other['aIO_2p0_s1'][0.005] = B.make('aIO_2p0_s1', geo=B.slab(0.9, w=False), kind='undoped', w_ry=0.005)
        r = C.smearing_audit(other)
        self.assertEqual(r['cells']['aIO_2p0_s1']['comparisons']['0.005']['status'], 'INVALID')


class TestA25Attribution(unittest.TestCase):
    """A25: FP p14 (complete parent weights)."""

    def test_FP_p14(self):
        pg = B.c1_parent()
        geo, m = B.c1_paired(pg, 0)
        st, idx = geo
        A, b1, Z = 15, 16, 22
        others = [17, 18, 19, 23, 24, 25]
        trap = {idx['W']: 0.6798, idx['added_O']: 0.05, A: 0.2, b1: 0.012}
        trap.update({a: 0.0582 / len(others) for a in others})
        parent = B.make('aIO_0p7_s1', geo=pg, kind='undoped', extra=[((-0.5, {Z: 0.6996, A: 0.2995, b1: 0.0009}), {})])
        cons = {'type': 'C1-paired', 'parent_geometry_sha256': parent['geometry_sha256'], 'site': idx['W'] + 1,
                'draw_rank': 1}
        paired = B.make('aIWO_0p7_C1a', geo=geo, ef=-0.5, extra=[((-0.5, trap), {'w5d': 0.6})],
                        man_extra={'construction': cons})
        self.assertEqual(paired['H-N']['class'], 'ECB', paired['H-N'])
        ls = [x for x in parent['attribution_data']['localised_states'] if abs(x['E_eV'] + 0.5) < 1e-9][0]
        self.assertEqual(len(ls['p']), pg[0].nat)                                       # complete weights exported
        r = C.attribution(paired, parent, B.atom_map(paired, parent, m))
        self.assertEqual(r['status'], 'HOST-TRAP-MEDIATED', r)


class TestA26ThresholdGuard(unittest.TestCase):
    """A26: FP p12."""

    def test_FP_p12(self):
        r = B.make(geo=B.slab(0.2), edge=0.5, w_E=0.8, top=2.0)
        self.assertAlmostEqual(r['H-N']['Delta_W']['value_eV'], 0.3, places=12)
        self.assertEqual(r['H-N']['class'], 'PARTIAL')


# ================================================================ Tier B
class TestB1Tar(Tmp):
    """B1: CP p07 (and the POSIX names of CP p22)."""

    def test_CP_p07_p22_no_escape(self):
        old = tempfile.tempdir
        tempfile.tempdir = self.p()
        try:
            rel_target = self.p('p07_rel_escape.txt')
            abs_target = self.p('sub', 'p07_abs_escape.txt')
            os.makedirs(self.p('sub'))
            tgz = self.p('sub', 'final_results.tar.gz')
            with tarfile.open(tgz, 'w:gz') as t:
                for name in ('x\\..\\..\\..\\p07_rel_escape.txt', abs_target.replace('\\', '/'), '../p22_up.txt',
                             '/tmp/p22_abs.txt'):
                    b = f'member {name!r}\n'.encode()
                    ti = tarfile.TarInfo(name)
                    ti.size = len(b)
                    t.addfile(ti, io.BytesIO(b))
                ti = tarfile.TarInfo('link')
                ti.type = tarfile.SYMTYPE
                ti.linkname = '../../outside'
                t.addfile(ti)
            try:
                run_cli(['validate-cert', tgz, '--name', 'x', '--certificate', self.p('none.json')])
            except Exception:                                 # nothing to read: the load fails after extraction
                pass
            self.assertFalse(os.path.exists(rel_target))
            self.assertFalse(os.path.exists(abs_target))
            self.assertFalse(os.path.exists(self.p('sub', 'p22_up.txt')))
            from analysis.cli import _safe_member
            for n in ('x\\..\\..\\a', 'C:/x/a', '/a', '../a', 'a/../../b', 'c:a'):
                self.assertIsNone(_safe_member(n), n)
            self.assertEqual(_safe_member('./tmp//slab.save/a.xml'), 'tmp/slab.save/a.xml')
        finally:
            tempfile.tempdir = old


class TestB2Determinism(Tmp):
    """B2: CP p02."""

    def test_CP_p02(self):
        e, ev, w, st = xml_export(self.p('export'))
        cert = certify(e, ev, w)[0]
        a, _ = cell(e, self.p('run0'), cert)
        b, _ = cell(e, self.p('run1'), cert)
        self.assertEqual(CERT.canonical_sha256(a), CERT.canonical_sha256(b))
        self.assertEqual(a['self_sha256'], b['self_sha256'])
        tgz = self.p('final_results.tar.gz')
        with tarfile.open(tgz, 'w:gz') as t:
            for n in ('data-file-schema.xml', 'atomic_proj.xml', 'projwfc_map_final.dat', 'final_avg.dat', 'avg_final.in',
                      'pp_final.in', 'lineage_final.dat'):
                t.add(os.path.join(e, n), arcname=n)
        cert2 = self.p('cert_tgz.json')
        run_cli(['certify', tgz, '--name', 'aIWO_2p0_s1', '--out', cert2, '--manifest', os.path.join(e, 'manifest.json'),
                 '--relaxation', 'converged', '--relaxation-evidence', ev])
        t0, _ = cell(tgz, self.p('tgz0'), cert2)
        t1, _ = cell(tgz, self.p('tgz1'), cert2)
        self.assertEqual(CERT.canonical_sha256(t0), CERT.canonical_sha256(t1))
        self.assertTrue(all(v['origin'].startswith('tarball:final_results.tar.gz::') for v in
                            t0['provenance']['files'].values()))
        cwd = os.getcwd()
        os.chdir(self.d)
        try:
            run_cli(['compare', 'pair', 'run0.json', 'run1.json', '--json', 'cmpA.json'])
        finally:
            os.chdir(cwd)
        run_cli(['compare', 'pair', self.p('run0.json'), self.p('run1.json'), '--json', self.p('cmpB.json')])
        A, Bc = qeio.load_json(self.p('cmpA.json')), qeio.load_json(self.p('cmpB.json'))
        self.assertEqual(CERT.canonical_sha256(A), CERT.canonical_sha256(Bc))
        self.assertEqual(sorted(A['meta']['input_files']), sorted(Bc['meta']['input_files']))
        self.assertTrue(CERT.verify_seal(A))


class TestB3Provenance(Tmp):
    """B3: CP p10."""

    def test_CP_p10(self):
        e, ev, w, st = xml_export(self.p('export'))
        cert, code, out = certify(e, ev, w)
        cj = qeio.load_json(cert)
        self.assertEqual(len(cj['code_sha256']), 64)
        self.assertIn('register_sha256', cj)
        self.assertTrue(cj['pseudopotentials'])
        code, q, out = gate(e, cert)
        self.assertIn('final_avg.dat', q['provenance']['run_files'])
        self.assertEqual(q['provenance']['geometry_sha256'], st.geometry_hash())
        self.assertEqual(q['provenance']['certificate_sha256'], qeio.sha256(cert))
        old = os.environ.get('IWO_REGISTER')
        os.environ['IWO_REGISTER'] = self.p('no_such_register.md')
        try:
            r, _ = cell(e, self.p('noreg'), cert)
        finally:
            if old is None:
                del os.environ['IWO_REGISTER']
            else:
                os.environ['IWO_REGISTER'] = old
        self.assertIsNone(r['provenance']['register']['sha256'])
        self.assertTrue(any('register not found' in x for x in r['run_qualification']['reasons']))
        self.assertEqual(r['H-N']['class'], 'UNRESOLVED')


class TestB4B5B6CertificateRobustness(Tmp):
    """B4 (CP p08, p17, p20a), B5 (CP p09, p20b), B6 (CP p19)."""

    def setUp(self):
        super().setUp()
        self.e, self.ev, self.w, self.st = xml_export(self.p('export'))
        self.cert = certify(self.e, self.ev, self.w)[0]
        self.good = qeio.load_json(self.cert)

    def check(self, c, label):
        p = os.path.join(self.e, 'bad.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(c, f)
        code, q, out = gate(self.e, p)
        self.assertEqual(code, 1, label)
        r, _ = cell(self.e, self.p('o'), p)
        self.assertEqual(r['H-N']['class'], 'UNRESOLVED', label)

    def test_CP_p08_malformed(self):
        g = self.good
        cases = {'top level list': [g], 'run_files list': dict(g, run_files=list(g['run_files'].items())),
                 'manifest string': dict(g, manifest='W-doped'), 'relaxation string': dict(g, relaxation='converged'),
                 'evidence dict': dict(g, relaxation=dict(g['relaxation'], evidence={'file': 'evidence.txt'})),
                 'width string': dict(g, smearing=dict(g['smearing'], width_Ry='0.001 Ry')),
                 'film strings': dict(g, manifest=dict(g['manifest'], film={k: str(v) for k, v in
                                                                            g['manifest']['film'].items()}))}
        for label, c in cases.items():
            self.check(c, label)

    def test_CP_p20a_p17_status_typos(self):
        for key, val in (('relaxation', 'Converged'), ('smearing', 'qualified '), ('geometry', 'Polished'),
                         ('relaxation', 'CONVERGED')):
            c = json.loads(json.dumps(self.good))
            c[key]['status'] = val
            p = os.path.join(self.e, 'v.json')
            with open(p, 'w') as f:
                json.dump(c, f)
            code, q, out = gate(self.e, p)
            self.assertEqual(code, 1, (key, val))
            self.assertTrue(any('unknown' in x for x in q['problems']))

    def test_CP_p09_encoding(self):
        c = dict(self.good, notes='polish checked by \u00cdsak')
        p1 = os.path.join(self.e, 'cert_utf8.json')
        with open(p1, 'wb') as f:
            f.write(json.dumps(c, ensure_ascii=False).encode('utf-8'))
        p2 = os.path.join(self.e, 'cert_bom.json')
        with open(p2, 'wb') as f:
            f.write(codecs.BOM_UTF8 + json.dumps(self.good).encode('utf-8'))
        for p in (p1, p2):
            code, q, out = gate(self.e, p)
            self.assertEqual(code, 0, q['problems'])

    @unittest.skipUnless(os.name == 'nt', 'Windows path spelling')
    def test_CP_p20b_other_mount_evidence(self):
        unc = '\\\\?\\' + os.path.abspath(self.ev)
        cert, code, out = certify(self.e, unc, self.w, out=os.path.join(self.e, 'cert_unc.json'))
        self.assertEqual(code, 0)
        self.assertTrue(os.path.isfile(cert))

    def test_CP_p19_pw_in_units(self):
        base = ("&CONTROL\n  calculation = 'scf'\n/\n&SYSTEM\n  ibrav = 0, nat = 2, ntyp = 2, celldm(1) = 20.0\n/\n"
                "CELL_PARAMETERS\n  1.0 0.0 0.0\n  0.0 1.0 0.0\n  0.0 0.0 2.0\nATOMIC_POSITIONS{unit}\n"
                "  In 0.10 0.20 0.30\n  O  0.50 0.50 0.50\n")
        alat = 20.0 * R.BOHR_A
        p = self.p('scf.in')
        for unit in ('', ' alat', ' {alat}'):
            with open(p, 'w', newline='\n') as f:
                f.write(base.format(unit=unit))
            g = qeio.read_pw_in(p)
            np.testing.assert_allclose(g['positions_A'][0], [0.1 * alat, 0.2 * alat, 0.3 * alat], atol=1e-9)
        with open(p, 'w', newline='\n') as f:
            f.write(base.format(unit=' crystal_sg'))
        with self.assertRaises(ValueError):
            qeio.read_pw_in(p)


class TestRawConventionCLI(Tmp):
    """FP p10b: 'cell --w5d raw' produces a raw-convention record that comparisons refuse."""

    def test_FP_p10b(self):
        e, ev, w, st = xml_export(self.p('a'))
        e5, ev5, w5, _ = xml_export(self.p('b'), w_ry=0.005)
        c1, c5 = certify(e, ev, w)[0], certify(e5, ev5, w5)[0]
        cell(e, self.p('ra'), c1, extra=('--w5d', 'raw'))
        cell(e5, self.p('rb'), c5, extra=('--w5d', 'raw'))
        code, out = run_cli(['compare', 'c3', self.p('ra.json'), self.p('rb.json')])
        self.assertIn('STATUS: INVALID', out)


if __name__ == '__main__':
    unittest.main()
