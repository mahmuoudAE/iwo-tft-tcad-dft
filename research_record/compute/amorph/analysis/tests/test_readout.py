"""H-N (A27) and H-G read-out rules at their boundaries, on synthetic cells with fixed occupations (exact numbers).
rc3: fixed occupations with fractional f are A15-unresolved (no global gap shown), so the exact boundary tests read
class_if_resolved and check that the A15 reason is the only unresolved condition; Gaussian cells are used where the
fully resolved class is tested."""
import unittest

from analysis import register as R

from analysis.tests.synth import SynthCell, donor_cell, slab_structure
from analysis.tests.helpers import QUALIFIED, analyse, manifest, qualification
from analysis.readout import PENDING, classify, delta_w, excess_fractions, gap_search, hg_cell, hh_cell, hi_cell, hn_cell


def cell(nex, ext, loc_w=0.0, loc_other=0.0, w_E=0.5, w5d=0.9, top=1.5, w_f=None, extra_states=(), name='aIWO_2p0_s1'):
    """Valence: 4 bands (N_v = 4 for nelec = 8 + nex). Above N_v (one k, w = 2): an extended host-edge state at 0.0 and
    more extended states holding `ext` electrons in total, a localised W state (W-5d w5d) at w_E holding loc_w
    electrons, a localised non-W state at -0.4 holding loc_other electrons, a top band at `top`."""
    st, idx = slab_structure()
    ALL = list(range(st.nat))
    sc = SynthCell(st)
    sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
    rem, E = ext, 0.0
    while rem > 1e-12:
        f = min(1.0, rem / 2.0)
        sc.add(E, ALL, f=f)
        rem -= 2.0 * f
        E += 0.01
    if E == 0.0:
        sc.add(0.0, ALL, f=0.0)
    sc.add(w_E, {idx['W']: 1.0}, w5d=w5d, f=loc_w / 2.0 if w_f is None else w_f)
    sc.add(-0.4, [idx['interior'][0]], f=loc_other / 2.0)
    for s in extra_states:
        sc.add(*s[0], **s[1])
    sc.add(top, ALL)
    return analyse(sc, 8.0 + nex, nex=nex, name=name), idx


G = dict(smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)


def rc(c):
    """class_if_resolved of a fixed-occupation boundary cell; the only unresolved condition must be A15."""
    r = hn_cell(c, QUALIFIED)
    assert all(x.startswith('A15') for x in r['unresolved_checks']), r['unresolved_checks']
    return r['class_if_resolved']


class TestClassify(unittest.TestCase):
    def test_table(self):
        self.assertEqual(classify(0.80, True, 0.0999), 'DONOR')
        self.assertEqual(classify(0.7999, True, 0.0), 'PARTIAL')
        self.assertEqual(classify(0.9, False, 0.0), 'PARTIAL')
        self.assertEqual(classify(0.9, True, 0.10), 'PARTIAL')
        self.assertEqual(classify(0.50, True, 0.0), 'PARTIAL')
        self.assertEqual(classify(0.4999, True, 0.0), 'ECB')
        self.assertEqual(classify(0.9, True, 0.50), 'ECB')
        self.assertIsNone(classify(None, True, 0.0))


class TestHN(unittest.TestCase):
    def test_donor_and_pending(self):
        sc, st, idx = donor_cell()
        c = analyse(sc, 9.0, **G)
        r = hn_cell(c, None)                                   # no certificate: unqualified
        self.assertEqual(r['class'], 'UNRESOLVED')
        self.assertEqual(r['class_if_resolved'], 'DONOR')
        self.assertTrue(any('certificate' in x for x in r['unresolved_checks']))
        self.assertTrue(any('RELAXATION UNKNOWN' in x.upper() for x in r['unresolved_checks']))
        r = hn_cell(c, qualification(manifest(), smearing=False))
        self.assertEqual(r['unresolved_checks'], [PENDING])
        r = hn_cell(c, QUALIFIED)
        self.assertEqual((r['class'], r['unresolved_checks']), ('DONOR', []))
        self.assertAlmostEqual(r['f_ext'], 1.0, places=9)
        self.assertEqual(r['Delta_W']['value_eV'], 0.5)
        self.assertEqual(r['Delta_W']['bounds_eV'], [0.5, 0.5])
        r = hn_cell(c, qualification(manifest(), relaxation='exploratory'))
        self.assertEqual(r['class'], 'UNRESOLVED')

    def test_f_ext_exactly_080(self):
        c, _ = cell(5, ext=4.0, loc_other=1.0)
        r = hn_cell(c, QUALIFIED)
        self.assertEqual(r['f_ext'], 0.8)
        self.assertEqual(rc(c), 'DONOR')
        c, _ = cell(5, ext=3.9, loc_other=1.1)
        self.assertEqual(rc(c), 'PARTIAL')

    def test_f_locw_exactly_010_and_050(self):
        c, _ = cell(10, ext=9.0, loc_w=1.0)
        r = hn_cell(c, QUALIFIED)
        self.assertEqual(r['f_locW'], 0.1)
        self.assertEqual(rc(c), 'PARTIAL')
        c, _ = cell(10, ext=9.1, loc_w=0.9)
        self.assertEqual(rc(c), 'DONOR')
        c, _ = cell(2, ext=1.0, loc_w=1.0)
        r = hn_cell(c, QUALIFIED)
        self.assertEqual((r['f_locW'], r['f_ext'], rc(c)), (0.5, 0.5, 'ECB'))

    def test_f_ext_exactly_050(self):
        c, _ = cell(2, ext=1.0, loc_other=1.0)
        self.assertEqual(rc(c), 'PARTIAL')
        c, _ = cell(2, ext=0.98, loc_other=1.02)
        self.assertEqual(rc(c), 'ECB')

    def test_delta_w_exactly_03(self):
        c, _ = cell(1, ext=1.0, w_E=0.3)
        r = hn_cell(c, QUALIFIED)
        self.assertEqual(r['Delta_W']['value_eV'], 0.3)
        self.assertFalse(r['Delta_W']['gt_0p3'])
        self.assertEqual(rc(c), 'PARTIAL')
        c, _ = cell(1, ext=1.0, w_E=0.3001)
        self.assertEqual(rc(c), 'DONOR')
        c, _ = cell(1, ext=1.0, w_E=0.3 + 1e-12)                  # float guard (1e-9): still not > 0.3
        self.assertEqual(rc(c), 'PARTIAL')

    def test_w5d_exactly_030_qualifies(self):
        c, _ = cell(1, ext=1.0, w_E=0.5, w5d=0.30)
        self.assertEqual(delta_w(c)['value_eV'], 0.5)
        c, _ = cell(1, ext=1.0, w_E=0.5, w5d=0.2999, top=1.6)
        d = delta_w(c)
        self.assertIsNone(d['W_state'])                       # no W state: lower bound from the top band
        self.assertEqual(d['lower_bound_eV'], 1.6)
        self.assertTrue(d['gt_0p3'])

    def test_coverage_exactly_1eV(self):
        c, _ = cell(1, ext=1.0, w_E=0.5, top=1.0)
        r = hn_cell(c, QUALIFIED)
        self.assertTrue(r['Delta_W']['coverage']['pass'])
        self.assertEqual(rc(c), 'DONOR')
        c, _ = cell(1, ext=1.0, w_E=0.5, top=0.99)
        r = hn_cell(c, QUALIFIED)
        self.assertFalse(r['Delta_W']['coverage']['pass'])
        self.assertEqual(r['class'], 'UNRESOLVED')
        self.assertTrue(any('coverage' in x for x in r['unresolved_checks']))

    def test_lower_bound_when_found_state_above_another_k_top(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st, nks=2)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, ALL, f=0.5)
        sc.add(1.2, ALL, k=0).add(2.5, ALL, k=0)                 # k 1: top band 2.5
        sc.add(1.3, ALL, k=1).add(3.0, {idx['W']: 1.0}, w5d=0.9, k=1)   # k 2: W state 3.0 above k-1's top band
        c = analyse(sc, 9.0)
        d = delta_w(c)
        self.assertIsNone(d['value_eV'])
        self.assertEqual(d['lower_bound_eV'], 2.5)
        self.assertEqual(d['upper_found_eV'], 3.0)

    def test_nex_zero_is_na(self):
        sc, st, idx = donor_cell()
        c = analyse(sc, 9.0, name='aIWO_2p0_s1', man={'kind': 'compensated', 'N_ex': 0})
        self.assertEqual(c.N_ex, 0)
        r = hn_cell(c, QUALIFIED)
        self.assertEqual(r['class'], 'N/A')
        self.assertIn('N/A', excess_fractions(c)['note'])

    def test_flagged_state_changes_class(self):
        # 0.2 e in a flagged state at the host edge: as extended -> DONOR, as not extended -> f_ext 0.78 PARTIAL
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, ALL, f=0.4).add(0.01, ALL, f=0.1, compl=0.5).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        sc.add(-0.4, [idx['interior'][0]], f=0.0)
        c = analyse(sc, 9.0)
        r = hn_cell(c, QUALIFIED)
        self.assertEqual(r['class_if_resolved'], 'DONOR')
        self.assertEqual(r['class'], 'UNRESOLVED')
        self.assertTrue(any('rests on flagged' in x for x in r['unresolved_checks']))

    def test_w5d_convention_flag(self):
        # raw W-5d 0.28 with completeness 0.92 -> normalised 0.304: the W state qualifies only when normalised
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, ALL, f=0.5).add(0.2, {idx['W']: 1.0}, w5d=0.28 / 0.92, compl=0.92).add(1.5, ALL)
        c = analyse(sc, 9.0, **G)
        i = int(((c.e == 0.2)).nonzero()[0][0])
        self.assertAlmostEqual(c.W5d_raw[i], 0.28)
        self.assertAlmostEqual(c.W5d_norm[i], 0.28 / 0.92)
        r = hn_cell(c, QUALIFIED)
        self.assertEqual(r['class'], 'PARTIAL')                      # Delta_W = 0.2 (normalised W-5d 0.304)
        self.assertEqual(r['class_with_raw_W5d'], 'DONOR')            # raw 0.28: no W state -> lower bound 1.5
        self.assertTrue(r['W5d_convention_sensitive'])
        c = analyse(sc, 9.0, w5d='raw', **G)                          # raw primary: the opposite is normalised
        r = hn_cell(c, QUALIFIED)
        self.assertEqual((r['W5d_convention'], r['opposite_W5d_convention']), ('raw', 'normalised'))
        self.assertEqual(r['class_with_opposite_W5d'], 'PARTIAL')
        self.assertTrue(r['W5d_convention_sensitive'])

    def test_states_used_have_neff(self):
        sc, st, idx = donor_cell()
        r = hn_cell(analyse(sc, 9.0), QUALIFIED)
        for s in r['states_used']:
            self.assertAlmostEqual(s['N_eff'], 40 * s['PR_n'])


class TestHG(unittest.TestCase):
    def test_hg_cell_items(self):
        sc, st, idx = donor_cell()
        r = hg_cell(analyse(sc, 9.0, **G), QUALIFIED)
        self.assertEqual(r['P1_lowest_W5d_state_above_host_edge']['status'], 'PASS')
        self.assertEqual(r['P2_f_ext']['status'], 'PASS')
        self.assertEqual(r['claude_host_edge_state_W5d']['status'], 'PASS')
        r = hg_cell(analyse(sc, 9.0, **G), qualification(manifest(), smearing=False))
        self.assertEqual(r['P2_f_ext']['status'], 'UNRESOLVED')
        self.assertEqual(r['P2_f_ext']['conditional_status'], 'PASS')

    def test_comp_cell_gap_state(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        for f, expect in ((1.0, 'FAIL'), (0.5, 'FAIL'), (0.49, 'FAIL'), (0.005, 'FAIL'), (0.004, 'PASS')):
            # rc3: occupied means >= 0.01 e in the state (f x 2/nspin), not f >= 0.5
            sc2 = SynthCell(st)
            sc2.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
            sc2.add(-1.0, {idx['W']: 1.0}, w5d=0.9, f=f).add(0.0, ALL).add(1.5, ALL)
            c = analyse(sc2, 8.0 + 2 * f, name='x', man={'kind': 'compensated', 'N_ex': 0})
            p3 = hg_cell(c, QUALIFIED)['P3_comp_no_occupied_localised_W_state_in_gap']
            self.assertEqual(p3['conditional_status'], expect, f)


class TestGapSearches(unittest.TestCase):
    def test_hh_window_inclusive(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(-0.5, [idx['top'][0]], f=0.25)                 # surface state exactly 0.5 below: outside
        sc.add(0.0, ALL, f=0.0).add(1.5, ALL)
        c = analyse(sc, 9.0)
        self.assertEqual(hh_cell(c)['n_qualifying'], 0)
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(-0.25, [idx['top'][0]], f=0.5)                 # 0.25 below the edge, f = 0.5 -> occupied
        sc.add(0.0, ALL, f=0.0).add(1.5, ALL)
        c = analyse(sc, 9.0)
        g = hh_cell(c)
        self.assertEqual(g['n_qualifying'], 1)
        self.assertEqual(g['window_eV'], [-0.3, 0.0])

    def test_window_lower_limit_included(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(-1.0, [idx['top'][0]], f=0.5).add(-0.5, ALL).add(0.5, ALL).add(1.5, ALL)
        c = analyse(sc, 9.0)
        self.assertEqual(c.E_c, -0.5)
        g = gap_search(c, lo=-1.0, hi=c.E_c, include_lo=True, occupied=True, weight_key='surface')
        self.assertEqual(g['n_qualifying'], 1)
        g = gap_search(c, lo=-1.0, hi=c.E_c, include_lo=False, occupied=True, weight_key='surface')
        self.assertEqual(g['n_qualifying'], 0)

    def test_flagged_in_window_unresolved(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(-0.1, [idx['interior'][0]], f=0.5, compl=0.5).add(0.0, ALL, f=0.0).add(1.5, ALL)
        c = analyse(sc, 9.0)
        self.assertTrue(hi_cell(c)['unresolved'])


if __name__ == '__main__':
    unittest.main()
