"""rc3: GENUINE passing controls still pass (C1-C6, attribution, H-N outcome, H-G, H-H, H-I, H-K, A15 audit), built
the registered way (builders.py), and the immediate negative neighbours of each."""
import unittest

from analysis.tests import builders as B
from analysis import compare as C
from analysis import register as R


class TestC3(unittest.TestCase):
    def setUp(self):
        self.geo = B.slab(0.11)
        self.ref = B.make('aIWO_2p0_s1', geo=self.geo)

    def test_genuine_pass_both_pending_widths(self):
        for w in R.C3_PENDING_WIDTHS_RY:
            r = C.c3(self.ref, B.make('aIWO_2p0_s1', geo=self.geo, w_ry=w))
            self.assertEqual(r['status'], 'PASS', r)
            self.assertEqual(r['widths_Ry'], [0.001, w])
            self.assertTrue(any(i['quantity'].startswith('host edge (eV, absolute)') for i in r['items']))
        r = C.c3(self.ref, B.make('aIWO_2p0_s1', geo=self.geo, w_ry=0.003), audit_width_Ry=0.003)
        self.assertEqual(r['status'], 'PASS')                       # an audit-selected width

    def test_boundary_and_failures(self):
        r = C.c3(self.ref, B.make(geo=self.geo, w_ry=0.005, w_E=0.55))          # Delta_W moves exactly 0.05 eV
        self.assertEqual(r['status'], 'PASS', r)
        r = C.c3(self.ref, B.make(geo=self.geo, w_ry=0.005, w_E=0.56))
        self.assertEqual(r['status'], 'FAIL')
        self.assertEqual(C.c3(self.ref, B.make(geo=self.geo, w_ry=0.005, loc_w=True))['status'], 'FAIL')
        r = C.c3(self.ref, B.make(geo=self.geo, w_ry=0.005, shift=0.2))         # rigid shift: absolute edges move
        self.assertEqual(r['status'], 'FAIL')

    def test_roles_and_identity(self):
        self.assertEqual(C.c3(self.ref, self.ref)['status'], 'NOT A PASS')     # comparing a result with itself
        self.assertEqual(C.c3(B.make(geo=self.geo, w_ry=0.002), B.make(geo=self.geo, w_ry=0.005))['status'],
                         'INVALID')                                             # no 0.001 Ry reference
        self.assertEqual(C.c3(self.ref, B.make(geo=B.slab(0.2), w_ry=0.005))['status'], 'INVALID')
        self.assertEqual(C.c3(self.ref, B.make(geo=self.geo, w_ry=0.003))['status'], 'INVALID')   # not registered


class TestC6(unittest.TestCase):
    def test_genuine_pass_split_label(self):
        geo = B.slab(0.13)
        ref = B.make('aIWO_2p0_s1', geo=geo, etot=-10.0)
        a, b = B.spin_starts('aIWO_2p0_s1', geo)
        r = C.c6(a, b, ref)
        self.assertEqual(r['status'], 'PASS', r)
        self.assertEqual(r['start_classes'], ['localised', 'delocalised'])
        self.assertEqual(r['lower_energy_start'], a['cell'])
        r = C.c6(b, a, ref)                                                       # order does not matter
        self.assertEqual(r['status'], 'PASS')

    def test_lower_energy_start_changes_class(self):
        geo = B.slab(0.13)
        ref = B.make('aIWO_2p0_s1', geo=geo, etot=-10.0)
        a, _ = B.spin_starts('aIWO_2p0_s1', geo, loc_w=True, e_loc=-10.005)
        _, b = B.spin_starts('aIWO_2p0_s1', geo)
        self.assertEqual(C.c6(a, b, ref)['status'], 'FAIL')

    def test_tie_below_resolution(self):
        geo = B.slab(0.13)
        ref = B.make('aIWO_2p0_s1', geo=geo, etot=-10.0)
        a, _ = B.spin_starts('aIWO_2p0_s1', geo, loc_w=True, e_loc=-10.001)
        _, b = B.spin_starts('aIWO_2p0_s1', geo, e_deloc=-10.001)
        self.assertEqual(C.c6(a, b, ref)['status'], 'UNRESOLVED')
        self.assertEqual(C.c6(b, a, ref)['status'], 'UNRESOLVED')
        a2, b2 = B.spin_starts('aIWO_2p0_s1', geo, e_loc=-10.001, e_deloc=-10.001)
        self.assertEqual(C.c6(a2, b2, ref)['status'], 'PASS')                    # same class, both pass


class TestC5(unittest.TestCase):
    def test_genuine_pass_and_functional_sensitive(self):
        geo = B.slab(0.17)
        paw, nc, hse = B.c5_runs('aIWO_0p7_s1', geo, loc_w=True)
        r = C.c5(paw, nc, hse)
        self.assertEqual(r['status'], 'PASS', r)
        paw, nc, hse = B.c5_runs('aIWO_0p7_s1', geo, loc_w=True, hse_loc_w=False)
        self.assertEqual(C.c5(paw, nc, hse)['status'], 'FUNCTIONAL-SENSITIVE')

    def test_gamma_route(self):
        geo = B.slab(0.17)
        paw, nc, hse = B.c5_runs('aIWO_0p7_s1', geo, gamma=True)
        self.assertEqual(C.c5(paw, nc, hse)['status'], 'UNRESOLVED')          # Gamma needs the NC production mesh
        ncp = B.make('aIWO_0p7_s1_NCk', geo=geo, settings={'functional': 'PBE', 'paw': False, 'uspp': False,
                                                          'species': B.NC_SPECIES, 'ecutwfc_Ry': 80.0,
                                                          'ecutrho_Ry': 320.0, 'k_mesh': [2, 2, 1, 0, 0, 0]})
        self.assertEqual(C.c5(paw, nc, hse, ncp)['status'], 'PASS')

    def test_settings_rejected(self):
        geo = B.slab(0.17)
        paw, nc, hse = B.c5_runs('aIWO_0p7_s1', geo)
        self.assertEqual(C.c5(paw, nc, nc)['status'], 'INVALID')
        self.assertEqual(C.c5(paw, paw, hse)['status'], 'INVALID')
        bad = B.make('x_HSE', geo=geo, settings=dict(hse['run_settings'], ecutfock_Ry=120.0))
        self.assertEqual(C.c5(paw, nc, bad)['status'], 'INVALID')
        bad = B.make('x_HSE', geo=geo, settings=dict(hse['run_settings'], q_mesh=[1, 1, 1]))
        self.assertEqual(C.c5(paw, nc, bad)['status'], 'INVALID')


class TestC1C2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main, cls.parent, cls.paired, cls.maps = B.c1_set()

    def test_c1_genuine_pass(self):
        r = C.c1(self.main, self.paired, self.parent, self.maps)
        self.assertEqual(r['status'], 'PASS', r)
        self.assertEqual(r['n_agree'], 3)

    def test_c1_fail_and_unresolved(self):
        main, parent, paired, maps = B.c1_set(t='0p7', paired_loc_w=(True, False, False), parent_dx=0.3)
        self.assertEqual(C.c1(main, paired, parent, maps)['status'], 'FAIL')
        self.assertEqual(C.c1(main, paired[:2], parent, maps[:2])['status'], 'UNRESOLVED')

    def test_c1_rejects_wrong_sets(self):
        self.assertEqual(C.c1(self.main, self.paired + [self.paired[0]], self.parent, self.maps)['status'], 'INVALID')
        self.assertEqual(C.c1(self.main, [self.paired[0]] * 3, self.parent, [self.maps[0]] * 3)['status'], 'INVALID')
        swapped = [self.maps[1], self.maps[0], self.maps[2]]
        self.assertEqual(C.c1(self.main, self.paired, self.parent, swapped)['status'], 'INVALID')
        self.assertEqual(C.c1(self.main, self.paired, None, None)['status'], 'INVALID')

    def test_c2_genuine_robust_and_not_robust(self):
        pg = B.c1_parent()
        geo, _ = B.c1_paired(pg, 0)
        full = self.paired[0]
        d = B.diluted(geo, full, loc_w=True)
        r = C.c2(full, d)
        self.assertEqual(r['status'], 'ROBUST', r)
        d2 = B.diluted(geo, full, loc_w=False)                                     # dilution delocalises: class change
        self.assertEqual(C.c2(full, d2)['status'], 'NOT ROBUST')

    def test_c2_rejects_non_dilutions(self):
        full = self.paired[0]
        self.assertEqual(C.c2(full, self.paired[1])['status'], 'INVALID')
        self.assertEqual(C.c2(self.main, self.paired[1])['status'], 'INVALID')


class TestAttribution(unittest.TestCase):
    def build(self, trap_on_W):
        pg = B.c1_parent()
        geo, m = B.c1_paired(pg, 0)
        st, idx = geo
        o1, o2 = pg[1]['sites'][1] + 1, pg[1]['sites'][1] + 2        # O atoms of another octahedron
        trap = {idx['W']: 0.5, idx['added_O']: 0.5} if trap_on_W else {o1: 0.5, o2: 0.5}
        parent = B.make('aIO_0p7_s1', geo=pg, kind='undoped', extra=[((-0.5, {o1: 0.5, o2: 0.5}), {})])
        cons = {'type': 'C1-paired', 'parent_geometry_sha256': parent['geometry_sha256'], 'site': idx['W'] + 1,
                'draw_rank': 1}
        paired = B.make('aIWO_0p7_C1a', geo=geo, loc_w=False, w_E=0.6, edge=0.0, ef=-0.5,
                        extra=[((-0.5, trap), {'w5d': 0.2 if trap_on_W else 0.0})], man_extra={'construction': cons})
        return paired, parent, B.atom_map(paired, parent, m)

    def test_w_centred_and_host_trap(self):
        p, par, amap = self.build(True)
        self.assertEqual(p['H-N']['class'], 'ECB', p['H-N'])
        r = C.attribution(p, par, amap)
        self.assertEqual(r['status'], 'W-CENTRED', r)
        p, par, amap = self.build(False)
        r = C.attribution(p, par, amap)
        self.assertEqual(r['status'], 'HOST-TRAP-MEDIATED', r)
        self.assertTrue(C.hn_pair(p, par)['aIO_tail_states_at_trap_energies'])

    def test_atom_map_required(self):
        p, par, amap = self.build(True)
        self.assertEqual(C.attribution(p, par, None)['status'], 'UNRESOLVED')


def series_inputs(polish_10=True, t07_loc=True, w08=0.2):
    """A complete, genuinely controlled thickness series: certified cells and every required control report."""
    cells = {'bulk': B.make('aIWO_bulk_s1', geo=B.bulk(), avg=None),
             '2.0': [B.make('aIWO_2p0_s1', geo=B.slab(0.01)), B.make('aIWO_2p0_s2', geo=B.slab(0.02))],
             '1.0': B.make('aIWO_1p0_s1', geo=B.slab(0.03), geometry='polished' if polish_10 else 'mv'),
             '0.8': B.make('aIWO_0p8_s1', geo=B.slab(0.04), w_E=w08),
             '0.7': None}
    g07 = B.slab(0.05)
    cells['0.7'] = B.make('aIWO_0p7_s1', geo=g07, loc_w=t07_loc)
    ctrl = {'2.0': {'C3': [], 'C6': []}, '0.7': {}}
    for i, c in enumerate(cells['2.0']):
        g = B.slab(0.01 * (i + 1))
        ctrl['2.0']['C3'] += [C.c3(c, B.make(c['cell'], geo=g, w_ry=w)) for w in R.C3_PENDING_WIDTHS_RY]
        a, b = B.spin_starts(c['cell'], g)
        ctrl['2.0']['C6'].append(C.c6(a, b, c))
    t07 = cells['0.7']
    ctrl['0.7']['C3'] = [C.c3(t07, B.make(t07['cell'], geo=g07, loc_w=t07_loc, w_ry=w)) for w in R.C3_PENDING_WIDTHS_RY]
    a, b = B.spin_starts(t07['cell'], g07, loc_w=t07_loc)
    ctrl['0.7']['C6'] = C.c6(a, b, t07)
    _, parent, paired, maps = B.c1_set(main_geo=g07, paired_loc_w=(t07_loc,) * 3)
    ctrl['0.7']['C1'] = C.c1(t07, paired, parent, maps)
    geo, _ = B.c1_paired(B.c1_parent(), 0)
    ctrl['0.7']['C2'] = C.c2(paired[0], B.diluted(geo, paired[0], loc_w=t07_loc))
    _, nc, hse = B.c5_runs(t07['cell'], g07, loc_w=t07_loc)
    ctrl['0.7']['C5'] = C.c5(t07, nc, hse)
    return cells, ctrl


class TestOutcome(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells, cls.ctrl = series_inputs()

    def test_genuine_crossover(self):
        st = {k: (v if isinstance(v, dict) else [x['status'] for x in v]) for k, v in
              {f'{l}:{c}': r for l, d in self.ctrl.items() for c, r in d.items()}.items()}
        r = C.hn_outcome({'cells': self.cells, 'controls': self.ctrl})
        self.assertEqual(r['outcome'], 'CROSSOVER', (r['unresolved_checks'], r['controls'], st))
        self.assertEqual(r['bracket_nm'], ['1.0', '0.7'])
        self.assertTrue(len(r['provenance']['inputs']) > 6)                # cells and control reports

    def test_genuine_no_crossover(self):
        cells, ctrl = series_inputs(t07_loc=False, w08=0.5)
        r = C.hn_outcome({'cells': cells, 'controls': ctrl})
        self.assertEqual(r['outcome'], 'NO CROSSOVER', (r['unresolved_checks'], r['controls']))

    def test_missing_control_or_polish_blocks(self):
        ctrl = {l: dict(d) for l, d in self.ctrl.items()}
        del ctrl['0.7']['C5']
        r = C.hn_outcome({'cells': self.cells, 'controls': ctrl})
        self.assertNotEqual(r['outcome'], 'CROSSOVER')
        cells, ctrl = series_inputs(polish_10=False)
        r = C.hn_outcome({'cells': cells, 'controls': ctrl})
        self.assertNotEqual(r['outcome'], 'CROSSOVER')
        self.assertIn('MISSING', r['controls']['1.0']['C4'])

    def test_one_seed_controls_missing(self):
        ctrl = {l: dict(d) for l, d in self.ctrl.items()}
        ctrl['2.0'] = {'C3': self.ctrl['2.0']['C3'][:2], 'C6': self.ctrl['2.0']['C6']}    # seed 2 has no C3
        r = C.hn_outcome({'cells': self.cells, 'controls': ctrl})
        self.assertNotEqual(r['outcome'], 'CROSSOVER')


class TestHGHHHIHK(unittest.TestCase):
    def test_hg_genuine(self):
        s1, s2 = B.make('aIWO_2p0_s1', geo=B.slab(0.01)), B.make('aIWO_2p0_s2', geo=B.slab(0.02))
        comp = B.make('aIWO_2p0_comp_s1', geo=B.slab(0.03), kind='compensated')
        a1 = B.make('aIO_2p0_s1', geo=B.slab(0.04, w=False), kind='undoped')
        a2 = B.make('aIO_2p0_s2', geo=B.slab(0.05, w=False), kind='undoped')
        r = C.hg_score(s1, s2, comp, a1, a2)
        self.assertEqual(r['P2_f_ext'], {'s1': 'PASS', 's2': 'PASS'}, r)
        self.assertEqual(r['claude_Eg_comp']['status'], 'PASS', r['claude_Eg_comp'])
        self.assertIn(r['P3_comp']['status'], ('PASS', 'FAIL'))

    def test_hh_genuine(self):
        seed = 77
        oh = B.make('aIWO_2p0_s1', geo=B.slab(0.01), seed=seed, V=1.0)
        bare = B.make('aIWO_2p0_s1_bare', geo=B.slab(0.02), seed=seed, V=0.9, man_extra={'passivation': 'none'})
        r = C.hh(oh, bare)
        self.assertEqual((r['shift']['status'], r['new_surface_state']['status']), ('PASS', 'PASS'), r)
        bare = B.make('aIWO_2p0_s1_bare', geo=B.slab(0.02), seed=seed, V=0.84, man_extra={'passivation': 'none'})
        self.assertEqual(C.hh(oh, bare)['shift']['status'], 'FAIL')

    def test_hi_genuine(self):
        iface = B.make('aIWO_2p0_Al2O3_s2', geo=B.interface(), V=1.0)
        self.assertEqual(iface['mode'], 'interface')
        v1 = B.make('aIWO_2p0_s1', geo=B.slab(0.01), V=1.1)
        v2 = B.make('aIWO_2p0_s2', geo=B.slab(0.02), V=1.05)
        r = C.hi(iface, v1, v2)
        self.assertEqual(r['status'], 'SUPPORTED', r)
        v1 = B.make('aIWO_2p0_s1', geo=B.slab(0.01), V=1.3)
        v2 = B.make('aIWO_2p0_s2', geo=B.slab(0.02), V=1.25)
        self.assertEqual(C.hi(iface, v1, v2)['status'], 'FAILED')

    def test_hk_genuine(self):
        t07 = B.make('aIWO_0p7_s1', geo=B.slab(0.03), vb=-3.0)
        s1 = B.make('aIWO_2p0_s1', geo=B.slab(0.01), vb=-2.0, V=1.0)
        s2 = B.make('aIWO_2p0_s2', geo=B.slab(0.02), vb=-2.1, V=0.95)
        t10 = B.make('aIWO_1p0_s1', geo=B.slab(0.04), V=0.5)
        r = C.hk(t07, s1, s2, t10)
        self.assertEqual(r['Eg_difference']['status'], 'PASS', r)
        self.assertEqual(r['aligned_edge_rise']['status'], 'PASS', r)

    def test_audit_genuine_partial_candidate(self):
        cells = {}
        for name, kind, dx in (('aIO_2p0_s1', 'undoped', 0.01), ('aIWO_2p0_s1', 'W-doped', 0.02),
                               ('aIWO_2p0_comp_s1', 'compensated', 0.03)):
            g = B.slab(dx, w=kind != 'undoped')
            cells[name] = {w: B.make(name, geo=g, kind=kind, w_ry=w) for w in (0.001, 0.002, 0.005)}
        r = C.smearing_audit(cells)
        self.assertEqual(r['status'], 'PARTIAL')
        self.assertEqual(r['provisional_width_candidate_Ry'], 0.005, r['unresolved_checks'])


if __name__ == '__main__':
    unittest.main()
