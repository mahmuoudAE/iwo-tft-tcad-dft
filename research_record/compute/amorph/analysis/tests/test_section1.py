"""Register section 1 rule boundaries on synthetic cells (exact-binary numbers where the threshold is representable)."""
import math
import unittest

import numpy as np

from analysis.tests.synth import SynthCell, bulk_structure, donor_cell, slab_structure
from analysis.tests.helpers import analyse
from analysis import register as R
from analysis.geometry import Structure, detect_mode, first_shell_O, regions
from analysis.smearing import occupations


class TestRegions(unittest.TestCase):
    def test_slab_bands_inclusive(self):
        st, idx = slab_structure()
        m, info = regions(st, 'slab')
        self.assertEqual(info['counts']['surface'], 7 + 7 + 6)
        self.assertEqual(info['counts']['interior'], 20)
        self.assertEqual(info['interior_fraction'], 0.5)
        self.assertTrue(m['surface'][idx['bottom'][-1]])      # exactly 3.0 A above the outermost bottom atom
        self.assertTrue(m['surface'][idx['top'][0]])          # exactly 3.0 A below the outermost top atom
        self.assertFalse(m['surface'][idx['interior'][0]])    # 3.25 A
        self.assertTrue(all(m['surface'][i] for i in idx['H']))

    def test_wrapped_slab_same_regions(self):
        st, idx = slab_structure()
        m0, _ = regions(st, 'slab')
        pos = st.pos.copy()
        pos[:, 2] = np.mod(pos[:, 2] + 22.0, 40.0)            # slab now crosses the periodic boundary
        m1, info = regions(Structure(st.species, pos, st.cell), 'slab')
        for k in m0:
            np.testing.assert_array_equal(m0[k], m1[k])
        self.assertGreater(info['vacuum_gap_A'], 15)

    def test_mode_detection(self):
        st, _ = slab_structure()
        self.assertEqual(detect_mode(st, 'aIWO_2p0_s1')[0], 'slab')
        self.assertEqual(detect_mode(bulk_structure(), 'aIWO_bulk_s1'), ('bulk', []))
        g, w = detect_mode(st, 'aIWO_bulk_s1')
        self.assertTrue(w)                                    # name/geometry disagreement is reported
        m, info = regions(bulk_structure(), 'bulk')
        self.assertEqual(info['interior_fraction'], 1.0)

    def test_interface_A24(self):
        sp, pos = [], []
        for i, z in enumerate([5.0, 6.0, 7.0, 8.0, 9.0, 10.0]):   # substrate cations
            sp.append('Al'); pos.append([1.0 + i, 1.0, z])
            sp.append('O'); pos.append([1.0 + i, 3.0, z + 0.5])
        sp.append('In'); pos.append([4.0, 6.0, 5.5])             # film cation on the OUTER face (z < 5.0 + 3.0)
        film_z = [11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5]
        for i, z in enumerate(film_z):
            sp.append('In' if i % 2 == 0 else 'O'); pos.append([1.0 + (i % 5), 6.0, z])
        sp.append('H'); pos.append([1.0, 1.0, 23.5])
        st = Structure(sp, pos, [[12, 0, 0], [0, 12, 0], [0, 0, 40]])
        self.assertEqual(detect_mode(st)[0], 'interface')
        m, info = regions(st, 'interface')
        z = st.pos[:, 2]
        sub = np.array([s == 'Al' for s in sp])
        fc = np.array([s in ('In', 'W') for s in sp]) & (z >= 8.0)
        z_if = 0.5 * (np.percentile(z[sub], 95) + np.percentile(z[fc], 5))
        self.assertAlmostEqual(info['z_if_A'], z_if, places=12)
        outer = 12
        self.assertTrue(m['outer_face'][outer])
        self.assertFalse(m['interface'][outer] or m['interior'][outer] or m['film'][outer])
        self.assertTrue(np.all(m['interface'] == ((np.abs(z - z_if) <= 3.0) & ~m['outer_face'])))
        self.assertTrue(np.all(m['interior'] == (m['film'] & ~m['surface'] & ~m['interface'])))

    def test_first_shell(self):
        st = Structure(['W', 'O', 'O', 'O', 'In'], [[0, 0, 0], [2.45, 0, 0], [0, 2.46, 0], [9.0, 0, 0], [0, 0, 2.0]],
                       [[10, 0, 0], [0, 10, 0], [0, 0, 10]])
        self.assertEqual(first_shell_O(st, 0), [1, 3])        # 2.45 included, 2.46 not, image at 1.0 A included


class TestAccounting(unittest.TestCase):
    def test_donor_cell_basics(self):
        sc, st, idx = donor_cell()
        c = analyse(sc, 9.0, smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        self.assertEqual((c.N_ex, c.N_v), (1, 4))
        self.assertEqual(c.acc['check'], 'PASS')
        self.assertEqual(c.E_c, 0.0)
        self.assertEqual(c.E_v, -2.0)
        self.assertEqual(c.host_edge['unresolved'], [])
        self.assertEqual(c.reasons, [])
        self.assertAlmostEqual(float(c.data.w.sum()), 2.0)          # spin factor 2 for nspin = 1

    def test_nex_from_manifest_not_name(self):
        sc, st, idx = donor_cell()
        # the name says compensated, the composition / manifest say W-doped: the name is ignored
        c = analyse(sc, 9.0, name='aIWO_2p0_comp_s1')
        self.assertEqual((c.N_ex, c.nex_info['N_ex_verified']), (1, False))          # formal-charge count, unverified
        c = analyse(sc, 9.0, name='anything', man={'kind': 'compensated', 'N_ex': 0})
        self.assertEqual((c.N_ex, c.nex_info['N_ex_verified'], c.kind), (0, True, 'compensated'))
        c = analyse(sc, 9.0, name='aIWO_2p0_s1', nex=3)
        self.assertIn('override', c.nex_info['N_ex_source'])
        self.assertFalse(c.nex_info['N_ex_verified'])

    def test_nv_not_integer(self):
        sc, st, idx = donor_cell()
        c = analyse(sc, 9.0, nex=2)                           # (9 - 2)/2 = 3.5
        self.assertTrue(any('not an integer' in r for r in c.reasons))

    def test_accounting_tolerance(self):
        # move 0.0199 e / 0.0201 e from a band <= N_v to a band > N_v: N_el and N_v unchanged
        for extra, ok in ((0.00995, 'PASS'), (0.01005, 'FAIL')):
            st, idx = slab_structure()
            ALL = list(range(st.nat))
            sc = SynthCell(st)
            sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0 - extra)
            sc.add(0.0, ALL, f=0.5).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.2, ALL, f=extra).add(1.5, ALL)
            c = analyse(sc, 9.0)
            self.assertAlmostEqual(c.acc['deviation'], 2 * extra, places=12)
            self.assertEqual(c.acc['check'], ok, extra)
            self.assertEqual(any('accounting' in r for r in c.reasons), ok == 'FAIL')
            self.assertFalse(any('do not reproduce N_el' in r for r in c.reasons))

    def test_electron_count_inconsistent(self):
        sc, st, idx = donor_cell()
        c = analyse(sc, 9.5)
        self.assertTrue(any('do not reproduce N_el' in r for r in c.reasons))

    def test_occupations_recomputed_with_run_function(self):
        sc, st, idx = donor_cell()
        c = analyse(sc, 9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        expect = occupations(c.data.e[0, 0], 0.0, 0.0136, 'gaussian')
        np.testing.assert_allclose(c.f[0, 0], expect)
        self.assertAlmostEqual(c.f[0, 0, 4], 0.5)            # host edge at E_F: Gaussian 0.5 (MV would differ)
        mv = occupations(c.data.e[0, 0], 0.0, 0.0136, 'mv')
        self.assertFalse(np.allclose(c.f[0, 0], mv))


class TestEdges(unittest.TestCase):
    def _cell(self, edge_atoms, low_E=None, edge_compl=1.0, st_idx=None, low_compl=1.0):
        st, idx = st_idx or slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, edge_atoms(idx), f=0.5, compl=edge_compl)
        if low_E is not None:
            sc.add(low_E, [idx['top'][0]], compl=low_compl)           # localised surface state above N_v
        sc.add(1.5, ALL)
        return analyse(sc, 9.0), idx

    def test_pr_exactly_020_is_extended(self):
        c, idx = self._cell(lambda i: i['interior'][:8])
        self.assertEqual(c.host_edge['state']['PR_n'], 0.2)
        self.assertEqual(c.E_c, 0.0)
        c, idx = self._cell(lambda i: i['interior'][:7])               # PR 0.175: no candidate at 0.0
        self.assertNotEqual(c.E_c, 0.0)

    def test_window_exactly_1eV(self):
        c, _ = self._cell(lambda i: i['interior'], low_E=-1.0)
        self.assertEqual(c.host_edge['distance_from_lowest_above_Nv_eV'], 1.0)
        self.assertEqual(c.host_edge['unresolved'], [])
        c, _ = self._cell(lambda i: i['interior'], low_E=-1.0 - 1e-6)
        self.assertTrue(any('within 1.0 eV' in r for r in c.host_edge['unresolved']))
        c, _ = self._cell(lambda i: i['interior'], low_E=-1.0 - 1e-12)          # float guard: still at the boundary
        self.assertFalse(any('within 1.0 eV' in r for r in c.host_edge['unresolved']))

    def test_completeness_flag_boundary(self):
        c, _ = self._cell(lambda i: i['interior'], edge_compl=0.90)
        self.assertFalse(c.host_edge['state']['flagged'])
        self.assertEqual(c.host_edge['unresolved'], [])
        self.assertEqual(c.host_edge['state']['PR_n'], c.host_edge['state']['PR_n'])
        c, _ = self._cell(lambda i: i['interior'], edge_compl=0.8999)
        self.assertTrue(c.host_edge['state']['flagged'])
        self.assertTrue(any('flagged' in r for r in c.host_edge['unresolved']))
        # a lower non-qualifying flagged state also makes the edge rest on flagged states
        c, _ = self._cell(lambda i: i['interior'], low_E=-0.5, low_compl=0.5)
        self.assertTrue(any('lower non-qualifying flagged' in r for r in c.host_edge['unresolved']))

    def test_interior_weight_exactly_at_limit(self):
        st_idx = slab_structure(n_bot=7, n_int=25, n_top=7, n_h_top=1, n_h_bot=0)   # interior fraction 0.625
        st, idx = st_idx
        self.assertEqual(R.INTERIOR_FACTOR * 25 / 40, 0.5)
        at_limit = lambda i: i['interior'][:4] + i['top'][:4]      # 0.5 interior weight, PR 0.2
        c, _ = self._cell(at_limit, st_idx=st_idx)
        self.assertEqual(c.host_edge['state']['weights']['interior'], 0.5)
        self.assertEqual(c.E_c, 0.0)
        below = lambda i: i['interior'][:3] + i['top'][:5]         # 0.375
        c, _ = self._cell(below, st_idx=st_idx)
        self.assertNotEqual(c.E_c, 0.0)

    def test_empty_interior_unresolved(self):
        st, idx = slab_structure(n_bot=7, n_int=0, n_top=7, w_interior_index=None,
                                 species_override={3: 'W'})
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-2.0, ALL, f=1.0).add(0.0, ALL, f=0.5).add(1.5, ALL)
        c = analyse(sc, 3.0, nex=1)
        self.assertTrue(any('no atoms' in r for r in c.host_edge['unresolved']))
        self.assertTrue(any('no atoms' in r for r in c.host_valence_edge['unresolved']))

    def test_no_candidate(self):
        st, idx = slab_structure()
        sc = SynthCell(st)
        sc.add(-2.0, idx['interior'], f=1.0).add(0.0, [idx['W']], f=0.5).add(1.5, [idx['top'][0]])
        c = analyse(sc, 3.0)
        self.assertIsNone(c.E_c)
        self.assertTrue(c.host_edge['unresolved'])

    def test_nv_beyond_bands(self):
        st, idx = slab_structure()
        sc = SynthCell(st)
        sc.add(-2.0, idx['interior'], f=1.0)
        c = analyse(sc, 3.0)
        self.assertTrue(any('no band above N_v' in r for r in c.reasons))


class TestSpin(unittest.TestCase):
    def test_spin_weights_and_accounting(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st, nspin=2)
        for E in (-3.0, -2.5, -2.2):
            sc.add(E, ALL, f=1.0)
        sc.add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, ALL, f=1.0, spin=0).add(0.0, ALL, f=0.0, spin=1)
        sc.add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        c = analyse(sc, 9.0)
        np.testing.assert_allclose(c.data.w, [[1.0], [1.0]])     # spin factor 1 per channel
        self.assertEqual(c.N_v, 4)
        self.assertEqual(c.acc['electrons_above_Nv'], 1.0)
        self.assertEqual(c.acc['check'], 'PASS')
        self.assertEqual(c.host_edge['state']['spin'], 1)

    def test_spin_two_k(self):
        st, idx = slab_structure()
        ALL = list(range(st.nat))
        sc = SynthCell(st, nspin=2, nks=2, wk=[1.0, 3.0])
        for E in (-3.0, -2.5, -2.2):
            sc.add(E, ALL, f=1.0)
        sc.add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, ALL, f=1.0, spin=0).add(0.0, ALL, f=0.0, spin=1)
        sc.add(1.5, ALL)
        c = analyse(sc, 9.0)
        np.testing.assert_allclose(c.data.w, [[0.25, 0.75], [0.25, 0.75]])
        self.assertAlmostEqual(c.acc['electrons_above_Nv'], 1.0)


class TestAlignment(unittest.TestCase):
    """rc3 frozen rule: ASSUMED 5.153 A primary, 4.1224 / 6.1836 A sensitivity windows, box averages of the planar
    average over the common interval (every kernel inside the interior), span >= 2.0 A (Codex rc2 review), primary
    std <= 0.05 eV, spread of the three means <= 0.05 eV; plot_num must be verified as 11; the grid must span the cell;
    aligned edges released only through the gate."""

    def cell(self, n_int=50, slope=0.0, fast=0.3, curv=0.0, slow=0.0):
        st, idx = slab_structure(n_int=n_int)
        ALL = list(range(st.nat))
        sc = SynthCell(st)
        sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
        sc.add(0.0, ALL, f=0.5).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        sc.G = dict(smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        c_b = 40.0 / R.BOHR_A
        z = np.linspace(0, c_b, 3001)[:-1]
        za = z * R.BOHR_A
        zc = 0.5 * (13.25 + 13.25 + 0.25 * (n_int - 1))
        v_ev = 1.0 + fast * np.sin(2 * np.pi * za / 0.8) + slope * (za - zc) + curv * (za - zc) ** 2 \
            + slow * np.sin(2 * np.pi * za / 20.0)
        avg = {'z_bohr': z, 'planar_ry': v_ev / R.RY_EV, 'macro_ry': None, 'window_bohr': 4.0, 'plot_num': 11}
        return sc, avg

    def test_valid_plateau_and_gate(self):
        sc, avg = self.cell()
        c = analyse(sc, 9.0, avg=avg, **sc.G)
        al = c.alignment
        self.assertTrue(al['valid'], al)
        self.assertGreaterEqual(al['common_span_A'], R.ALIGN_MIN_COMMON_SPAN_A)
        self.assertLess(al['plateau_std_eV'], 0.05)
        self.assertAlmostEqual(al['V_interior_eV'], 1.0, places=2)
        self.assertEqual(sorted(al['by_window']), sorted(f'{w:g}' for w in (5.153, 4.1224, 6.1836)))
        g = c.aligned_edges([])
        self.assertAlmostEqual(g['aligned_host_edge_eV'], 0.0 - al['V_interior_eV'])
        g = c.aligned_edges(['smearing qualification pending'])          # unqualified run: withheld
        self.assertIsNone(g['aligned_host_edge_eV'])
        self.assertTrue(g['gate'])

    def test_short_interior(self):
        sc, avg = self.cell(n_int=20)                                    # 4.75 A interior: no common interval
        c = analyse(sc, 9.0, avg=avg)
        self.assertFalse(c.alignment['valid'])
        self.assertTrue(any('common interval' in r for r in c.alignment['unresolved']))
        sc, avg = self.cell(n_int=33)                                    # 8.0 A interior: span 1.82 < 2.0
        c = analyse(sc, 9.0, avg=avg, **sc.G)
        self.assertFalse(c.alignment['valid'])
        self.assertLess(c.alignment['common_span_A'], R.ALIGN_MIN_COMMON_SPAN_A)
        sc, avg = self.cell(n_int=34)                                    # 8.25 A interior: span 2.07 >= 2.0
        c = analyse(sc, 9.0, avg=avg, **sc.G)
        self.assertGreaterEqual(c.alignment['common_span_A'], R.ALIGN_MIN_COMMON_SPAN_A)
        self.assertTrue(c.alignment['valid'], c.alignment)

    def test_std_and_mean_variation(self):
        sc, avg = self.cell(slow=0.2)                                    # long-wave variation survives averaging
        c = analyse(sc, 9.0, avg=avg)
        self.assertFalse(c.alignment['valid'])
        self.assertTrue(any('standard deviation' in r for r in c.alignment['unresolved']))
        sc, avg = self.cell(fast=0.0, curv=0.12)                        # curvature: window-dependent means
        c = analyse(sc, 9.0, avg=avg)
        self.assertGreater(c.alignment['mean_variation_eV'], 0.05)
        self.assertTrue(any('mean varies' in r for r in c.alignment['unresolved']))

    def test_plot_num_and_missing(self):
        sc, avg = self.cell()
        avg['plot_num'] = 0
        self.assertFalse(analyse(sc, 9.0, avg=avg).alignment['valid'])
        avg['plot_num'] = None                                           # unverifiable: never assumed 11
        self.assertFalse(analyse(sc, 9.0, avg=avg).alignment['valid'])
        self.assertFalse(analyse(sc, 9.0).alignment['valid'])

    def test_truncated_grid(self):
        sc, avg = self.cell()
        keep = avg['z_bohr'] * R.BOHR_A < 20.0
        avg = dict(avg, z_bohr=avg['z_bohr'][keep], planar_ry=avg['planar_ry'][keep])
        al = analyse(sc, 9.0, avg=avg, **sc.G).alignment
        self.assertFalse(al['valid'])
        self.assertTrue(any('truncated' in x for x in al['unresolved']))

    def test_gate_on_edge_and_accounting(self):
        sc, avg = self.cell()
        c = analyse(sc, 9.0, avg=avg, nex=2, **sc.G)                             # N_v 3.5: section-1 unresolved
        g = c.aligned_edges([])
        self.assertIsNone(g['aligned_host_edge_eV'])
        self.assertTrue(any('accounting' in x or 'section-1' in x for x in g['gate']))
        st, idx = slab_structure(n_int=50)
        sc = SynthCell(st)
        sc.add(-2.0, idx['interior'], f=1.0).add(0.0, [idx['W']], f=0.5).add(1.5, [idx['top'][0]])   # no host edge
        c = analyse(sc, 3.0, avg=self.cell()[1], nex=1)
        self.assertTrue(c.alignment['valid'])
        self.assertIsNone(c.aligned_edges([])['aligned_host_edge_eV'])


if __name__ == '__main__':
    unittest.main()
