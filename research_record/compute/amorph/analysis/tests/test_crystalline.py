"""Register section 3: the frozen code must reproduce the crystalline results (3 % W-5d, Delta E_c 0.281 eV).
Reads only the crystalline reference outputs (IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow/cern_htcondor/results:
iwo_slab2_final_cpu, slab2_relax_c2, slab1r_final_cpu); skipped when they are not present (set IWO_V1_ROOT)."""
import unittest

from analysis.tests import synth  # noqa: F401
from analysis import crystalline as X

ROOT = X.default_root()
HAVE = (ROOT / 'qe_workflow' / 'cern_htcondor' / 'results' / 'iwo_slab2_final_cpu' / 'scf.out').is_file()


@unittest.skipUnless(HAVE, f'crystalline reference outputs not found under {ROOT}')
class TestCrystalline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = X.reproduce(ROOT)

    def test_reproduced(self):
        self.assertEqual(self.r['status'], 'REPRODUCED', self.r['checks'])

    def test_w5d(self):
        w = self.r['W5d']
        self.assertEqual((w['N_el'], w['N_ex'], w['N_v']), (1329.0, 3, 663))
        self.assertEqual(w['smearing'], 'mv')                          # the run's own function (MV), not Gaussian
        self.assertLessEqual(abs(w['W5d_electrons_raw'] - 0.086), 0.0005)
        self.assertEqual(round(100 * w['W5d_share_raw']), 3)
        self.assertEqual(round(100 * w['W5d_share_section1_normalised']), 3)
        self.assertAlmostEqual(w['electrons_above_Nv'], 3.0, delta=0.02)
        self.assertAlmostEqual(w['electrons_band_664'], 2.041, delta=0.0005)   # logged electrons_in_host_CB_bottom_band

    def test_dec(self):
        t = self.r['dEc']
        self.assertLessEqual(abs(t['dEc_eV'] - 0.2813), 0.00005)
        self.assertAlmostEqual(t['dEv_eV'], -0.0539, delta=0.00005)
        self.assertAlmostEqual(t['plateau_spread_meV_centre_a_over_4'], 8.4, delta=0.05)   # RESULTS_LOG: 8 meV (8.4)


if __name__ == '__main__':
    unittest.main()
