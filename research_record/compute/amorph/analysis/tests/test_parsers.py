"""Parsers on synthetic QE-format files: XML pair (nspin 1 and 2, with and without spin attributes), the real D-24
table exporter (steps_final.sh.D24) followed by the table reader (nspin 1 and lsda), missing data, mismatches."""
import os
import shutil
import tempfile
import unittest

import numpy as np

from analysis.tests import synth
from analysis.tests.synth import SynthCell, donor_cell, slab_structure
from analysis import qeio
from analysis.data import from_tables, from_xml, load_export
from analysis.readout import hn_cell
from analysis.tests.helpers import QUALIFIED
from analysis.section1 import Section1


def spin_cell():
    st, idx = slab_structure()
    ALL = list(range(st.nat))
    sc = SynthCell(st, nspin=2, nks=2, wk=[1.0, 3.0])
    for E in (-3.0, -2.5, -2.2):
        sc.add(E, ALL, f=1.0)
    sc.add(-2.0, idx['interior'], f=1.0)
    sc.add(0.0, ALL, f=1.0, spin=0).add(0.3, {idx['W']: 0.6, idx['interior'][0]: 0.4}, w5d=0.5, spin=1)
    sc.add(0.6, {idx['W']: 1.0}, w5d=0.9, spin=0).add(0.05, ALL, spin=1)
    sc.add(1.5, ALL)
    return sc, st, idx


class Tmp(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_test_')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def write_xml(self, data, st, **kw):
        sch, prj, out = (os.path.join(self.d, n) for n in ('data-file-schema.xml', 'atomic_proj.xml', 'projwfc_final.out'))
        synth.write_schema(sch, data, st)
        synth.write_atomic_proj(prj, data, st.species, **kw)
        synth.write_projwfc_out(out, data, st.species)
        return sch, prj, out


class TestXML(Tmp):
    def check_same(self, d0, d1):
        np.testing.assert_allclose(d1.e, d0.e, atol=1e-10)
        np.testing.assert_allclose(d1.w, d0.w, atol=1e-12)
        np.testing.assert_allclose(d1.atom_w, d0.atom_w, atol=1e-12)
        np.testing.assert_allclose(d1.w5d, d0.w5d, atol=1e-12)
        np.testing.assert_allclose(d1.compl, d0.compl, atol=1e-12)

    def test_roundtrip_nspin1(self):
        sc, st, idx = donor_cell(nks=2)
        d0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        d1, st1 = from_xml(*self.write_xml(d0, st))
        self.check_same(d0, d1)
        self.assertEqual(d1.smearing, 'gaussian')
        self.assertAlmostEqual(d1.degauss_ev, 0.0136, places=12)
        np.testing.assert_allclose(st1.pos, st.pos, atol=1e-9)
        self.assertAlmostEqual(d1.etot_ry, -100.0)

    def test_roundtrip_spin_attr_and_positional(self):
        sc, st, idx = spin_cell()
        d0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        for kw in ({'spin_attr': True}, {'spin_attr': False}, {'nk_header': 'total'}):
            d1, _ = from_xml(*self.write_xml(d0, st, **kw))
            self.assertEqual(d1.nspin, 2)
            self.check_same(d0, d1)
            np.testing.assert_allclose(d1.w, [[0.25, 0.75], [0.25, 0.75]])

    def test_missing_orbital(self):
        sc, st, idx = donor_cell()
        d0 = sc.build(9.0)
        with self.assertRaises(ValueError):
            from_xml(*self.write_xml(d0, st, drop=(0, 5)))

    def test_eigenvalue_mismatch(self):
        sc, st, idx = donor_cell()
        d0 = sc.build(9.0)
        sch, prj, out = self.write_xml(d0, st)
        d0.e[0, 0, 4] += 0.01
        synth.write_schema(sch, d0, st)
        with self.assertRaises(ValueError):
            from_xml(sch, prj, out)

    def test_map_species_mismatch(self):
        sc, st, idx = donor_cell()
        d0 = sc.build(9.0)
        sch, prj, out = self.write_xml(d0, st)
        with open(out) as f:
            txt = f.read()
        self.assertIn('atom   18 (W  )', txt)
        with open(out, 'w') as f:
            f.write(txt.replace('atom   18 (W  )', 'atom   18 (In )', 1))
        with self.assertRaises(ValueError):
            from_xml(sch, prj, out)

    def test_two_fermi_energies(self):
        sc, st, idx = spin_cell()
        d0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        sch, prj, out = self.write_xml(d0, st)
        synth.write_schema(sch, d0, st, two_fermi=(0.1, -0.1))
        d1, _ = from_xml(sch, prj, out)
        np.testing.assert_allclose(d1.ef, [0.1, -0.1], atol=1e-12)


class TestD24Tables(Tmp):
    def run_export(self, d0, st):
        r = synth.run_d24_exporter(self.d, d0, st)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def test_tables_match_xml_nspin1(self):
        sc, st, idx = donor_cell(nks=2)
        d0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        r = self.run_export(d0, st)
        self.assertIn('proj_atoms_check PASS', r.stdout)
        dt, stt = from_tables(self.d)
        dx, stx = from_xml(os.path.join(self.d, 'tmp/slab.save/data-file-schema.xml'),
                           os.path.join(self.d, 'tmp/slab.save/atomic_proj.xml'), os.path.join(self.d, 'projwfc_map_final.dat'))
        np.testing.assert_allclose(dt.atom_w, dx.atom_w, atol=6e-7)
        np.testing.assert_allclose(dt.e, dx.e, atol=1e-5)
        ct, cx = Section1(dt, stt, name='aIWO_2p0_s1'), Section1(dx, stx, name='aIWO_2p0_s1')
        self.assertEqual(ct.E_c is not None, True)
        self.assertAlmostEqual(ct.E_c, cx.E_c, places=5)
        ht, hx = hn_cell(ct, QUALIFIED), hn_cell(cx, QUALIFIED)
        self.assertEqual(ht['class_if_resolved'], hx['class_if_resolved'])
        self.assertEqual(hx['class'], 'DONOR')
        self.assertEqual(ht['class'], 'UNRESOLVED')                     # tables without scf.out: convergence not shown
        self.assertTrue(any('convergence not shown' in x for x in ct.reasons))
        self.assertAlmostEqual(ht['f_ext'], hx['f_ext'], places=5)
        # load_export prefers the XML pair when complete
        os.replace(os.path.join(self.d, 'tmp/slab.save/data-file-schema.xml'), os.path.join(self.d, 'data-file-schema.xml'))
        os.replace(os.path.join(self.d, 'tmp/slab.save/atomic_proj.xml'), os.path.join(self.d, 'atomic_proj.xml'))
        self.assertEqual(load_export(self.d)[2], 'xml')
        os.remove(os.path.join(self.d, 'atomic_proj.xml'))
        d2, st2, used, notes = load_export(self.d)
        self.assertEqual(used, 'table')
        self.assertTrue(notes)

    def test_tables_lsda_reconstruction(self):
        sc, st, idx = spin_cell()
        d0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        r = self.run_export(d0, st)
        self.assertIn('proj_atoms_check FAIL', r.stdout)       # the D-24 exporter's own check flags lsda tables
        dt, stt = from_tables(self.d)
        self.assertEqual(dt.nspin, 2)
        self.assertTrue(dt.warnings)
        np.testing.assert_allclose(dt.e, d0.e, atol=1e-5)
        np.testing.assert_allclose(dt.atom_w, d0.atom_w, atol=6e-7)
        np.testing.assert_allclose(dt.w, d0.w, atol=1e-9)
        c, c0 = Section1(dt, stt, name='aIWO_2p0_s1'), Section1(d0, st, name='aIWO_2p0_s1')
        self.assertAlmostEqual(c.acc['electrons_above_Nv'], c0.acc['electrons_above_Nv'], places=6)
        self.assertEqual(c.E_c, c0.E_c)

    def test_tables_missing_rows(self):
        sc, st, idx = donor_cell()
        d0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        self.run_export(d0, st)
        p = os.path.join(self.d, 'proj_atoms_final.dat')
        with open(p) as f:
            lines = f.read().splitlines()
        with open(p, 'w') as f:
            f.write('\n'.join(lines[:-1]) + '\n')
        with self.assertRaises(ValueError):
            from_tables(self.d)


class TestAvgAndMap(Tmp):
    def test_read_avg_window(self):
        p, pin = os.path.join(self.d, 'final_avg.dat'), os.path.join(self.d, 'avg_final.in')
        np.savetxt(p, np.array([[0.0, 1.0, 1.1], [0.5, 2.0, 2.1]]))
        with open(pin, 'w') as f:
            f.write('1\nfinal_v.pp\n1.0\n3000\n3\n4.0\n')
        a = qeio.read_avg(p, pin)
        self.assertEqual(a['window_bohr'], 4.0)
        np.testing.assert_allclose(a['macro_ry'], [1.1, 2.1])

    def test_state_map_both_formats(self):
        sc, st, idx = donor_cell()
        d0 = sc.build(9.0)
        out = os.path.join(self.d, 'projwfc_final.out')
        smap = synth.write_projwfc_out(out, d0, st.species)
        m1 = qeio.read_state_map(out)
        dat = os.path.join(self.d, 'projwfc_map_final.dat')
        with open(dat, 'w') as f:
            f.write('# map\n' + ''.join(f'{i} {a} {s} {w} {l} {m}\n' for i, (a, s, w, l, m) in enumerate(smap, 1)))
        m2 = qeio.read_state_map(dat)
        self.assertEqual(m1, m2)
        self.assertEqual(len(m1), len(smap))


if __name__ == '__main__':
    unittest.main()
