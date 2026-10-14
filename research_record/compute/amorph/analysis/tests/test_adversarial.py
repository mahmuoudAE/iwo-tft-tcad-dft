"""Adversarial tests for the rc1 false-pass paths (Codex read-only probes), ported to rc3 inputs: an applicable quantity
that is missing, only bounded or unresolved gives UNRESOLVED, never PASS / ROBUST; malformed inputs (nspin = 1 into C6,
the same start twice, other geometry, unconverged, tables, duplicates, legacy adapter) never pass."""
import unittest

from analysis.tests import builders as B
from analysis.tests.synth import SynthCell, slab_structure
from analysis.tests.helpers import QUALIFIED, analyse, manifest, qualification
from analysis import compare as C
from analysis import register as R
from analysis.readout import delta_w, hn_cell

G = dict(smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)


def bounded(w_ry, geo, **kw):
    """W state below the W-5d threshold: Delta_W only bounded below by the top band."""
    return B.make('aIWO_2p0_s1', geo=geo, w_ry=w_ry, w5d=0.2, **kw)


class TestFalsePassC3C2(unittest.TestCase):
    def test_c3_delta_w_lower_bounds_unresolved(self):
        g = B.slab(0.21)
        a, b = bounded(0.001, g), bounded(0.005, g)
        self.assertIsNone(a['H-N']['Delta_W']['value_eV'])
        r = C.c3(a, b)
        self.assertEqual(r['status'], 'UNRESOLVED', r)                   # rc1 returned PASS here
        self.assertTrue(any('not evaluable' in x for x in r['unresolved_checks']))

    def test_c3_value_against_bound_unresolved(self):
        g = B.slab(0.21)
        self.assertNotEqual(C.c3(B.make(geo=g), bounded(0.005, g))['status'], 'PASS')

    def test_c2_lower_bounds_unresolved(self):
        _, parent, paired, _ = B.c1_set()
        pg = B.c1_parent()
        geo, _ = B.c1_paired(pg, 0)
        full = B.make(paired[0]['cell'], geo=geo, w5d=0.2,
                      man_extra={'construction': paired[0]['run_qualification']['construction']})
        r = C.c2(full, B.diluted(geo, full, loc_w=False, w5d=0.2))
        self.assertEqual(r['status'], 'UNRESOLVED', r)                   # rc1 returned ROBUST here

    def test_c3_missing_gap_unresolved(self):
        g = B.slab(0.21)
        st, idx = g
        t = idx['top']
        loc_valence = B.make(geo=g)                                      # reference
        sc = SynthCell(st)
        ALL = list(range(st.nat))
        sc.add(-3.0, [t[0]]).add(-2.5, [t[1]]).add(-2.2, [t[2]]).add(-2.0, [t[3]])   # no host valence edge
        sc.add(0.0, ALL).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        from analysis.section1 import Section1
        from analysis.report import cell_result
        man = manifest()
        data = sc.build(9.0, smearing='gaussian', degauss_ev=0.005 * R.RY_EV, ef=0.0, settings=dict(B.PAW))
        r = cell_result(Section1(data, st, name='aIWO_2p0_s1', manifest=man, avg=B.flat_avg(st)), 'xml',
                        qual=qualification(man))
        self.assertEqual(C.c3(loc_valence, r)['status'], 'UNRESOLVED')

    def test_unqualified_inputs_never_pass(self):
        g = B.slab(0.21)
        r = C.c3(B.make(geo=g, certified=False), B.make(geo=g, w_ry=0.005, certified=False))
        self.assertEqual(r['status'], 'UNRESOLVED')
        self.assertTrue(any('certificate' in x for x in r['unresolved_checks']))


class TestC6Inputs(unittest.TestCase):
    def setUp(self):
        self.geo = B.slab(0.13)
        self.ref = B.make('aIWO_2p0_s1', geo=self.geo, etot=-10.0)
        self.a, self.b = B.spin_starts('aIWO_2p0_s1', self.geo)

    def spin(self, mags, etot, **kw):
        sp = [dict(s, starting_magnetization=mags.get(s['name'], 0.0)) for s in B.PAW_SPECIES]
        settings = dict({'lsda': True, 'species': sp}, **kw.pop('settings', {}))
        return B.make('aIWO_2p0_s1', geo=kw.pop('geo', self.geo), nspin=kw.pop('nspin', 2), etot=etot,
                      settings=settings, **kw)

    def test_valid(self):
        self.assertEqual(C.c6(self.a, self.b, self.ref)['status'], 'PASS')

    def test_two_nspin1_inputs(self):
        r = C.c6(B.make(geo=self.geo, etot=-10.1), B.make(geo=self.geo, etot=-10.2), self.ref)
        self.assertEqual(r['status'], 'INVALID')                          # rc1 returned PASS here
        self.assertTrue(any('not an nspin = 2' in x for x in r['unresolved_checks']))

    def test_same_start_kind(self):
        r = C.c6(self.a, self.spin({'W': 0.6}, -10.003), self.ref)        # two localised starts
        self.assertEqual(r['status'], 'INVALID')

    def test_other_geometry_settings_convergence_source(self):
        d = {'In': 0.1, 'O': 0.1, 'W': 0.1, 'H': 0.1}
        self.assertEqual(C.c6(self.a, self.spin(d, -10.0, geo=B.slab(0.5)), self.ref)['status'], 'INVALID')
        self.assertEqual(C.c6(self.a, self.spin(d, -10.0, settings={'ecutwfc_Ry': 50.0}), self.ref)['status'],
                         'INVALID')
        self.assertEqual(C.c6(self.a, self.spin(d, -10.0, settings={'scf_converged': False}), self.ref)['status'],
                         'INVALID')
        self.assertEqual(C.c6(self.a, self.spin(d, -10.0, source='table'), self.ref)['status'], 'INVALID')
        self.assertEqual(C.c6(self.a, self.b, self.spin(d, -10.0))['status'], 'INVALID')   # nspin = 2 reference

    def test_no_magnetisation(self):
        self.assertEqual(C.c6(self.a, self.spin({}, -10.0), self.ref)['status'], 'INVALID')


class TestFlaggedStates(unittest.TestCase):
    def cell(self, w_raw, compl):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, ALL, f=0.5).add(0.2, {idx['W']: 1.0}, w5d=w_raw / compl, compl=compl).add(1.5, ALL)
        return analyse(sc, 9.0, **G)

    def test_qualifying_flagged_state_may_lose_w(self):
        c = self.cell(0.25, 0.8)                         # normalised 0.3125 qualifies; raw 0.25 alone would not
        d = delta_w(c)
        self.assertEqual(d['value_eV'], 0.2)
        self.assertTrue(d['gt_0p3_flag_extremes']['flagged_may_lose_W'])
        self.assertTrue(any('rests on flagged' in x for x in d['unresolved']))
        self.assertEqual(d['bounds_eV'][0], 0.2)
        self.assertGreater(d['bounds_eV'][1] or 99, 0.3)                 # losing W moves Delta_W above 0.3 eV
        self.assertEqual(hn_cell(c, QUALIFIED)['class'], 'UNRESOLVED')

    def test_flagged_state_may_gain_w(self):
        c = self.cell(0.15, 0.8)                         # normalised 0.1875; raw + missing 0.35 could qualify
        d = delta_w(c)
        self.assertIsNone(d['W_state'])
        self.assertFalse(d['gt_0p3_flag_extremes']['flagged_may_gain_W'])
        self.assertTrue(any('rests on flagged' in x for x in d['unresolved']))
        self.assertEqual(d['bounds_eV'][0], 0.2)

    def test_flagged_far_from_threshold_is_harmless(self):
        c = self.cell(0.0, 0.85)                         # cannot reach 0.30 either way
        self.assertFalse(any('rests on flagged' in x for x in delta_w(c)['unresolved']))


class TestDuplicates(unittest.TestCase):
    def test_hg_hi_c1_duplicates(self):
        s = B.make('aIWO_2p0_s1', geo=B.slab(0.01))
        r = C.hg_score(s, s)
        self.assertEqual(set(r['P2_f_ext'].values()), {'UNRESOLVED'})
        main, parent, paired, maps = B.c1_set()
        self.assertEqual(C.c1(main, [paired[0], paired[0], paired[2]], parent, [maps[0], maps[0], maps[2]])['status'],
                         'INVALID')
        iface = B.make('aIWO_2p0_Al2O3_s2', geo=B.interface())
        v = B.make('aIWO_2p0_s1', geo=B.slab(0.01))
        self.assertEqual(C.hi(iface, v, v)['status'], 'INVALID')


class TestInvalidEdgesAndGates(unittest.TestCase):
    def test_aligned_edge_withheld_for_unqualified_run(self):
        oh = B.make('aIWO_2p0_s1', geo=B.slab(0.01), seed=5, relaxation='unknown')
        bare = B.make('aIWO_2p0_s1_bare', geo=B.slab(0.02), seed=5, man_extra={'passivation': 'none'})
        self.assertIsNone(oh['alignment']['aligned_host_edge_eV'])
        r = C.hh(oh, bare)
        self.assertEqual(r['shift']['status'], 'UNRESOLVED')
        self.assertIn('relaxation', ' '.join(r['shift']['unresolved_checks']).lower())

    def test_hi_qualified_failure_kept(self):
        st, idx = B.interface()
        ALL = list(range(st.nat))
        trap = {idx['interface'][0]: 0.5, idx['interface'][1]: 0.5}
        iface = B.make('aIWO_2p0_Al2O3_s2', geo=(st, idx), avg=None,
                       extra=[((-0.1, trap), {})], ef=-0.1)                       # occupied interface trap
        v1 = B.make('aIWO_2p0_s1', geo=B.slab(0.01))
        v2 = B.make('aIWO_2p0_s2', geo=B.slab(0.02))
        r = C.hi(iface, v1, v2)
        self.assertEqual(r['status'], 'FAILED', r)                        # interface state stands, alignment absent
        self.assertTrue(r['unresolved_checks'])
        self.assertIsNotNone(ALL)

    def test_legacy_adapter_rejected_by_c5(self):
        legacy = {'adapter': 'legacy A23 nc_readout', 'primary': False, 'E_c_eV': 1.0}
        paw, nc, _ = B.c5_runs('aIWO_0p7_s1', B.slab(0.17))
        self.assertEqual(C.c5(paw, nc, legacy)['status'], 'INVALID')

    def test_accounting_failure_gates_alignment_and_class(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=0.98995)
        sc.add(0.0, ALL, f=0.5).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.2, ALL, f=0.01005).add(1.5, ALL)
        c = analyse(sc, 9.0, man=manifest())
        self.assertEqual(c.acc['check'], 'FAIL')
        self.assertEqual(hn_cell(c, qualification(manifest()))['class'], 'UNRESOLVED')
        self.assertIsNone(c.aligned_edges([])['aligned_host_edge_eV'])


if __name__ == '__main__':
    unittest.main()
