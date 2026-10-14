"""rc4 regression tests: the seven blocking items of the Codex rc3 review, each reproduced with a synthetic probe
(expected: rejected / UNRESOLVED), plus the genuine path that must still pass. Synthetic data only."""
import os
import shutil
import tempfile
import unittest

import numpy as np

from analysis.tests import builders as B
from analysis.tests.synth import SynthCell, slab_structure
from analysis.tests.helpers import analyse, manifest, qualification
from analysis.tests.test_regressions_rc2 import certify, gate, xml_export
from analysis import compare as C
from analysis import register as R
from analysis.qeio import pp_plot_num, read_avg
from analysis.readout import hh_cell, hi_cell
from analysis.report import support_bounds
from analysis.smearing import wgauss


def _ef_two_states(d, sigma):
    """E_F with 2 [g(E_F) + g(E_F - d)] = 1 e (an edge state at 0 and a second state at d, nspin 1, one k)."""
    lo, hi = -1.0, 1.0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        n = 2 * (wgauss(np.array([m / sigma]), 0)[0] + wgauss(np.array([(m - d) / sigma]), 0)[0])
        lo, hi = (m, hi) if n < 1 else (lo, m)
    return 0.5 * (lo + hi)


class TestItem1FractionBounds(unittest.TestCase):
    """f_ext carries bounds [0.92, 1.0] from a flagged extended state holding 0.08 e; the class is robust (DONOR at
    every extreme) but the admissible f_ext difference reaches 0.08 > 0.05: never PASS (rc3 compared scalars: PASS)."""

    def flagged(self, geo, **kw):
        st, idx = geo
        ef = _ef_two_states(0.016, 0.001 * R.RY_EV)
        return B.make('aIWO_2p0_s1', geo=geo, ef=ef, extra=[((0.016, list(range(st.nat))), {'compl': 0.8})], **kw)

    def test_probe(self):
        g = B.slab(0.31)
        a, b = self.flagged(g), self.flagged(g)
        fr = a['H-N']['fractions']
        self.assertAlmostEqual(fr['f_ext_bounds'][1] - fr['f_ext_bounds'][0], 0.08, delta=0.01)
        self.assertEqual(a['H-N']['class'], 'DONOR', a['H-N']['unresolved_checks'])
        r = C.tolerance_compare(a, b, 'probe')
        item = [i for i in r['items'] if i['quantity'] == 'f_ext'][0]
        self.assertIsNone(item['pass'])
        self.assertEqual(r['status'], 'UNRESOLVED')
        self.assertNotEqual(C.c6(*B.spin_starts('aIWO_2p0_s1', g), a)['status'], 'PASS')

    def test_c2_probe(self):
        """ECB probe (Codex): f_ext ~ 0.3 with bounds of width > 0.15 from a flagged extended state; the class is ECB at
        every extreme, the C2 f_ext tolerance is 0.15: ROBUST must not be reached."""
        pg = B.c1_parent()
        geo, _ = B.c1_paired(pg, 0)
        st, idx = geo
        sigma, eps, d = 0.001 * R.RY_EV, 0.006, 0.0001
        lo, hi = -1.0, 1.0
        g = lambda x: wgauss(np.array([x / sigma]), 0)[0]
        for _ in range(200):
            m = 0.5 * (lo + hi)
            lo, hi = (m, hi) if 2 * (g(m + eps) + g(m) + g(m - d)) < 1 else (lo, m)
        ef = 0.5 * (lo + hi)
        self.assertGreater(2 * g(ef - d), 0.15)
        cons = {'type': 'C1-paired', 'parent_geometry_sha256': 'x', 'site': idx['W'] + 1, 'draw_rank': 1}
        full = B.make('aIWO_0p7_C1a', geo=geo, w_E=-eps, ef=ef, extra=[((d, list(range(st.nat))), {'compl': 0.8})],
                      man_extra={'construction': cons})
        self.assertEqual(full['H-N']['class'], 'ECB', full['H-N']['unresolved_checks'])
        fb = full['H-N']['fractions']['f_ext_bounds']
        self.assertGreater(fb[1] - fb[0], 0.15)
        dil = B.diluted(geo, full, loc_w=False, w_E=-eps, ef=ef,
                        extra=[((d, list(range(2 * st.nat - 1))), {'compl': 0.8})])
        r = C.c2(full, dil)
        self.assertNotEqual(r['status'], 'ROBUST', r)
        self.assertIsNone([i for i in r['items'] if i['quantity'] == 'f_ext'][0]['pass'])

    def test_genuine_unflagged_still_passes(self):
        g = B.slab(0.31)
        self.assertEqual(C.c3(B.make(geo=g), B.make(geo=g, w_ry=0.005))['status'], 'PASS')


class TestItem2UPFIdentity(unittest.TestCase):
    def test_same_filename_other_content(self):
        g = B.slab(0.32)
        ref = B.make(geo=g)
        other = B.make(geo=g, w_ry=0.005, upf_hashes={'W.pbe-paw.UPF': 'f' * 64})
        self.assertEqual(ref['run_settings']['species'], other['run_settings']['species'])     # same file names
        r = C.c3(ref, other)
        self.assertEqual(r['status'], 'INVALID')
        self.assertTrue(any('certified UPF content hash' in x for x in r['unresolved_checks']))
        self.assertEqual(C.c3(ref, B.make(geo=g, w_ry=0.005))['status'], 'PASS')

    def test_partial_lineage_refused(self):
        d = tempfile.mkdtemp(prefix='iwo_rc4_lin_')
        try:
            e, ev, w, st = xml_export(os.path.join(d, 'x'))
            lin = os.path.join(e, 'lineage_final.dat')
            lines = [l for l in open(lin).read().splitlines() if 'pseudo/W.' not in l]
            with open(lin, 'w', newline='\n') as f:
                f.write('\n'.join(lines) + '\n')
            cert = certify(e, ev, w)[0]
            code, q, _ = gate(e, cert)
            self.assertEqual(code, 1)
            self.assertFalse(q['pseudopotentials_bound'])
            self.assertTrue(any('does not cover every UPF' in x for x in q['problems']))
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestItem3HSEParameters(unittest.TestCase):
    def setUp(self):
        self.g = B.slab(0.33)
        self.paw, self.nc, self.hse = B.c5_runs('aIWO_0p7_s1', self.g)

    def hse_with(self, **over):
        s = dict(self.hse['run_settings'], **over)
        return B.make('aIWO_0p7_s1_HSE06', geo=self.g, settings=s)

    def test_probe_wrong_parameters(self):
        r = C.c5(self.paw, self.nc, self.hse_with(hybrid={'exx_fraction': 0.9, 'screening_parameter': 0.0}))
        self.assertEqual(r['status'], 'INVALID')
        r = C.c5(self.paw, self.nc, self.hse_with(hybrid={'exx_fraction': 0.25, 'screening_parameter': 0.2}))
        self.assertEqual(r['status'], 'INVALID')
        r = C.c5(self.paw, self.nc, self.hse_with(functional='HSE06-label'))
        self.assertEqual(r['status'], 'INVALID')

    def test_missing_parameters_unresolved(self):
        r = C.c5(self.paw, self.nc, self.hse_with(hybrid={'ecutfock': 80.0}))
        self.assertEqual(r['status'], 'UNRESOLVED')
        self.assertTrue(any('not recorded' in x for x in r['unresolved_checks']))

    def test_explicit_defaults_and_genuine_pass(self):
        self.assertEqual(C.c5(self.paw, self.nc, self.hse)['status'], 'PASS')
        r = C.c5(self.paw, self.nc, self.hse_with(hybrid={'exx_fraction': '0.25', 'screening_parameter': '0.106'}))
        self.assertEqual(r['status'], 'PASS')


class TestItem4C1Parent(unittest.TestCase):
    def test_unrelaxed_parent(self):
        main, parent, paired, maps = B.c1_set(parent_kw={'relaxation': 'unknown'})
        r = C.c1(main, paired, parent, maps)
        self.assertEqual(r['status'], 'UNRESOLVED')
        self.assertIn('parent relaxation', r['unresolved_checks'][0])
        main, parent, paired, maps = B.c1_set(parent_kw={'relaxation': 'exploratory'}, parent_dx=0.2)
        self.assertNotEqual(C.c1(main, paired, parent, maps)['status'], 'PASS')

    def test_parent_smearing_does_not_gate(self):
        main, parent, paired, maps = B.c1_set(parent_kw={'smearing_ok': False}, parent_dx=0.4)
        self.assertEqual(C.c1(main, paired, parent, maps)['status'], 'PASS')


class TestItem5PlotNum(unittest.TestCase):
    def test_probe_commented_assignment(self):
        self.assertEqual(pp_plot_num("&INPUTPP\n  ! plot_num = 11\n  plot_num = 0\n/\n"), 0)
        self.assertEqual(pp_plot_num("&INPUTPP\n  plot_num = 11  ! ionic + Hartree\n  filplot = 'v!1.pp'\n/\n"), 11)
        for bad in ("&INPUTPP\n  plot_num = 11, plot_num = 11\n/\n", "&INPUTPP\n plot_num = 11\n/\n&INPUTPP\n/\n",
                    "&INPUTPP\n  plot_num(1) = 11\n/\n", "plot_num = 11\n", "&INPUTPP\n  prefix = 'slab'\n/\n",
                    "&INPUTPP\n  plot_num = 1.1e1\n/\n"):
            self.assertIsNone(pp_plot_num(bad), bad)

    def test_alignment_refuses_the_probe(self):
        d = tempfile.mkdtemp(prefix='iwo_rc4_pp_')
        try:
            st, idx = B.slab(0.34)
            z = np.linspace(0, 40.0 / R.BOHR_A, 3001)[:-1]
            np.savetxt(os.path.join(d, 'final_avg.dat'), np.c_[z, np.full_like(z, 0.1), np.full_like(z, 0.1)])
            pp = os.path.join(d, 'pp_final.in')
            with open(pp, 'w', newline='\n') as f:
                f.write("&INPUTPP\n  ! plot_num = 11\n  plot_num = 0\n/\n")
            avg = read_avg(os.path.join(d, 'final_avg.dat'), None, pp)
            self.assertEqual(avg['plot_num'], 0)
            r = B.make(geo=(st, idx), avg=avg)
            self.assertFalse(r['alignment']['valid'])
            self.assertIsNone(r['alignment']['aligned_host_edge_eV'])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestItem6ValenceGateAndLabels(unittest.TestCase):
    def test_probe_missing_valence_reference(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        t = idx['top']
        sc = SynthCell(st)
        sc.add(-3.0, [t[0]]).add(-2.5, [t[1]]).add(-2.2, [t[2]]).add(-2.0, [t[3]])       # no host valence edge
        sc.add(0.0, ALL).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        c = analyse(sc, 9.0, man=manifest(), smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        self.assertIsNone(c.E_v)
        self.assertIsNotNone(c.E_c)
        for g in (hh_cell(c), hi_cell(c)):
            self.assertTrue(any('valence' in x for x in g['unresolved']), g['unresolved'])

    def test_labels_and_frozen_interpretation(self):
        sc, st, idx = B.states(*B.slab(0.35))[0], None, None
        c = analyse(sc, 9.0, man=manifest(), smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        self.assertIn('>= 0.01 e', hh_cell(c)['search'])
        self.assertIn('any occupation', hi_cell(c)['search'])
        self.assertNotIn('majority', hh_cell(c)['search'] + hi_cell(c)['search'])
        self.assertIn('HI_occupation', R.IMPLEMENTATION_CHOICES)
        self.assertNotIn('majority', ' '.join(str(v) for v in R.IMPLEMENTATION_CHOICES.values()))


class TestItem7SupportBounds(unittest.TestCase):
    """Trap: W 0.6526, X 0.2716, A 0.0632, R 0.0126 (normalised), completeness 0.95 (missing m = 0.05). A is in the
    primary 80 % support and its raw weight 0.060 exceeds m (the rc3 'sure' rule), but m placed on X and R lifted above
    A push the cumulative weight past 80 % before A: A is not a sure member. The parent state carries 0.25 on X and 0.07
    on A: rc3 asserted HOST-TRAP-MEDIATED; the rigorous bound gives an inconclusive (UNRESOLVED) criterion (ii)."""

    def test_membership_unit(self):
        p = np.zeros(10)
        X, A, Rr = 1, 2, 3
        p[0], p[X], p[A], p[Rr] = 0.6526, 0.2716, 0.0632, 0.0126
        sure, poss = support_bounds(p, 0.95, [X, A, Rr])
        self.assertEqual(sure, [X + 1])
        self.assertEqual(poss, [X + 1, A + 1, Rr + 1])
        sure1, poss1 = support_bounds(p, 1.0, [X, A, Rr])
        self.assertEqual(sure1, [X + 1, A + 1])                                            # exact without missing weight
        self.assertEqual(poss1, [X + 1, A + 1])

    def test_probe_attribution(self):
        pg = B.c1_parent()
        geo, m = B.c1_paired(pg, 0)
        st, idx = geo
        X, A, Rr, Z = 15, 16, 17, 22
        trap = {idx['W']: 0.6526, X: 0.2716, A: 0.0632, Rr: 0.0126}
        parent = B.make('aIO_0p7_s1', geo=pg, kind='undoped', extra=[((-0.5, {X: 0.25, A: 0.07, Z: 0.68}), {})])
        cons = {'type': 'C1-paired', 'parent_geometry_sha256': parent['geometry_sha256'], 'site': idx['W'] + 1,
                'draw_rank': 1}
        paired = B.make('aIWO_0p7_C1a', geo=geo, ef=-0.5, extra=[((-0.5, trap), {'w5d': 0.6, 'compl': 0.95})],
                        man_extra={'construction': cons})
        self.assertEqual(paired['H-N']['class'], 'ECB', paired['H-N'])
        t = paired['attribution_data']['trapping_states'][0]
        self.assertEqual(t['support_nonW_atoms'], [X + 1, A + 1])
        self.assertNotIn(A + 1, t['support_nonW_atoms_sure'])
        r = C.attribution(paired, parent, B.atom_map(paired, parent, m))
        self.assertEqual(r['status'], 'UNRESOLVED', r)
        self.assertTrue(r['criterion_ii']['parent_states_inconclusive'])


if __name__ == '__main__':
    unittest.main()
