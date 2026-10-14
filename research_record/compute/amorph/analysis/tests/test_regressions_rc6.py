"""rc7 regression test (Codex rc6 review): NO CROSSOVER (and CROSSOVER) require certified Gaussian polish at 2.0 nm
(both seeds), 1.0 and 0.7 nm, as frozen in register IMPLEMENTATION_CHOICES['series']. Synthetic data only."""
import unittest

from analysis.tests import builders as B
from analysis.tests.test_compare import series_inputs
from analysis import compare as C


class TestThickEndpointPolish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells, cls.ctrl = series_inputs(t07_loc=False, w08=0.5)            # every thickness DONOR

    def test_positive_both_seeds_polished(self):
        r = C.hn_outcome({'cells': self.cells, 'controls': self.ctrl})
        self.assertEqual(r['outcome'], 'NO CROSSOVER', (r['unresolved_checks'], r['controls']))
        self.assertEqual(r['unresolved_checks'], [])

    def test_counterexample_mv_thick_seeds(self):
        cells = dict(self.cells)
        cells['2.0'] = [B.make('aIWO_2p0_s1', geo=B.slab(0.01), geometry='mv'),
                        B.make('aIWO_2p0_s2', geo=B.slab(0.02), geometry='mv')]   # distinct seeds, certified MV
        r = C.hn_outcome({'cells': cells, 'controls': self.ctrl})
        self.assertEqual(r['outcome'], 'UNRESOLVED')
        self.assertTrue(any('polish missing' in x and "'2.0'" in x for x in r['unresolved_checks']), r['unresolved_checks'])
        self.assertIn('MISSING', r['controls']['2.0']['C4'])
        cells['2.0'] = [B.make('aIWO_2p0_s1', geo=B.slab(0.01)),
                        B.make('aIWO_2p0_s2', geo=B.slab(0.02), geometry='mv')]   # one seed unpolished
        self.assertEqual(C.hn_outcome({'cells': cells, 'controls': self.ctrl})['outcome'], 'UNRESOLVED')

    def test_crossover_branch_same_rule(self):
        cells, ctrl = series_inputs()
        self.assertEqual(C.hn_outcome({'cells': cells, 'controls': ctrl})['outcome'], 'CROSSOVER')
        for lab in ('2.0', '1.0', '0.7'):
            cs = dict(cells)
            if lab == '2.0':
                cs['2.0'] = [cells['2.0'][0], B.make('aIWO_2p0_s2', geo=B.slab(0.02), geometry='mv')]
            elif lab == '1.0':
                cs['1.0'] = B.make('aIWO_1p0_s1', geo=B.slab(0.03), geometry='mv')
            else:
                cs['0.7'] = B.make('aIWO_0p7_s1', geo=B.slab(0.05), loc_w=True, geometry='mv')
            r = C.hn_outcome({'cells': cs, 'controls': ctrl})
            self.assertEqual(r['outcome'], 'UNRESOLVED', (lab, r['unresolved_checks']))
            self.assertTrue(any('polish missing' in x for x in r['unresolved_checks']), lab)


if __name__ == '__main__':
    unittest.main()
