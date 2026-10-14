import math
import unittest

import numpy as np

from analysis.tests import synth  # noqa: F401  (sets sys.path)
from analysis.smearing import ngauss_of, occupations, wgauss


class TestSmearing(unittest.TestCase):
    def test_gaussian_values(self):
        self.assertEqual(float(wgauss(0.0, 0)), 0.5)
        x = np.linspace(-3, 3, 13)
        np.testing.assert_allclose(wgauss(x, 0) + wgauss(-x, 0), 1.0, atol=1e-15)
        self.assertAlmostEqual(float(wgauss(1.0, 0)), 0.5 * math.erfc(-1.0), places=15)

    def test_mv_value_and_not_gaussian(self):
        mv0 = 0.5 * math.erf(-1 / math.sqrt(2)) + math.exp(-0.5) / math.sqrt(2 * math.pi) + 0.5
        self.assertAlmostEqual(float(wgauss(0.0, -1)), mv0, places=14)
        self.assertGreater(abs(float(wgauss(0.0, -1)) - float(wgauss(0.0, 0))), 0.05)

    def test_mp1_value(self):
        x = 1.0
        mp1 = 0.5 * math.erfc(-x) + x * math.exp(-x * x) / (2 * math.sqrt(math.pi))
        self.assertAlmostEqual(float(wgauss(x, 1)), mp1, places=14)
        self.assertEqual(float(wgauss(0.0, 1)), 0.5)

    def test_fd_and_clipping(self):
        self.assertEqual(float(wgauss(0.0, -99)), 0.5)
        self.assertAlmostEqual(float(wgauss(2.0, -99)), 1 / (1 + math.exp(-2.0)), places=15)
        self.assertEqual(float(wgauss(300.0, -99)), 1.0)
        self.assertEqual(float(wgauss(-300.0, -99)), 0.0)

    def test_names(self):
        for n, g in (('gaussian', 0), ('Gaussian', 0), ('mp', 1), ('Methfessel-Paxton', 1), ('mv', -1), ('cold', -1),
                     ('Marzari-Vanderbilt', -1), ('fd', -99), ('Fermi-Dirac', -99)):
            self.assertEqual(ngauss_of(n), g)
        with self.assertRaises(ValueError):
            ngauss_of('fixed')

    def test_occupations_use_the_run_function(self):
        e = np.array([-0.1, 0.0, 0.1])
        g = occupations(e, 0.0, 0.1, 'gaussian')
        m = occupations(e, 0.0, 0.1, 'mv')
        np.testing.assert_allclose(g, [0.5 * math.erfc(-1), 0.5, 0.5 * math.erfc(1)], atol=1e-15)
        self.assertFalse(np.allclose(g, m))
        with self.assertRaises(ValueError):
            occupations(e, 0.0, 0.0, 'gaussian')


if __name__ == '__main__':
    unittest.main()
