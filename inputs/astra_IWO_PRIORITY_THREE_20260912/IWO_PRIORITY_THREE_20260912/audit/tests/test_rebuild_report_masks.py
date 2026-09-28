"""Pure mask-sensitivity unit tests; no native run records or plots are written."""
import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from rebuild_report import active_mask_sensitivity, metrics


class RebuildReportMaskTests(unittest.TestCase):
    def fixture(self, key='2p0'):
        # Synthetic numeric arrays for tests only, never reported as TCAD output.
        measured = np.array([1., 1., 1., 1., 2., 4., 6., 9., 12.]) * 1e-12
        current = np.array([0., 0., -.1, 1., 0., -2., 6., 0., 12.]) * 1e-12
        active = np.ones(9, dtype=bool) if key == '31p8' else measured > 5e-12
        return dict(key=key, vg=np.array([-2., -1.5, -1., -.5, 0., .5, 1., 2., 3.]),
                    measured=measured, terminal={'id': current}, active=active, low=~active)

    def test_counts_expose_nonpositive_currents_and_factor_five_is_unchanged(self):
        run = self.fixture()
        originals = [run['measured'].copy(), run['terminal']['id'].copy(), run['active'].copy()]
        report = active_mask_sensitivity(run)
        by_factor = {row['reference_multiplier']: row for row in report['rows']}
        self.assertEqual([by_factor[f]['target_count'] for f in (1, 3, 5, 10)], [5, 4, 3, 1])
        broad = by_factor[1]
        self.assertEqual(broad['positive_log_denominator'], 2)
        self.assertEqual(broad['excluded_nonpositive_log_count'], 3)
        self.assertEqual(broad['native_zero_count'], 2)
        self.assertEqual(broad['native_negative_count'], 1)
        self.assertFalse(broad['positive_log_complete'])
        self.assertGreater(broad['rmse_linear_A_per_um'], 0)
        # Even though the positive-only logs happen to match, zeros/negative
        # values remain visible in the denominator, sign counts and linear RMSE.
        self.assertEqual(broad['rmse_positive_log10_decades'], 0)
        original_regions = metrics(run)[3]
        for field in ('target_count', 'linear_denominator', 'positive_log_denominator',
                      'excluded_nonpositive_log_count', 'positive_log_complete',
                      'rmse_linear_A_per_um', 'rmse_positive_log10_decades'):
            self.assertEqual(by_factor[5][field], original_regions['active'][field])
        self.assertEqual(by_factor[5]['native_zero_count'], 1)
        self.assertTrue(by_factor[5]['is_original_acceptance_mask'])
        self.assertTrue(report['original_active_mask_preserved'])
        self.assertEqual(report['original_target_count'], 9)
        for old, new in zip(originals, [run['measured'], run['terminal']['id'], run['active']]):
            np.testing.assert_array_equal(old, new)
        json.dumps(report, allow_nan=False)

    def test_thick_channel_uses_all_original_points_for_every_factor(self):
        report = active_mask_sensitivity(self.fixture('31p8'))
        for row in report['rows']:
            self.assertTrue(row['all_points_override_for_31p8'])
            self.assertEqual(row['target_count'], 9)
            self.assertEqual(row['linear_denominator'], 9)
            self.assertEqual(row['positive_log_denominator'], 3)
            self.assertEqual(row['excluded_nonpositive_log_count'], 6)
            self.assertFalse(row['positive_log_complete'])

    def test_inconsistent_acceptance_mask_is_rejected_instead_of_remasked(self):
        run = self.fixture()
        run['active'] = run['measured'] > 3e-12
        with self.assertRaisesRegex(ValueError, 'fixed factor-5 acceptance definition'):
            active_mask_sensitivity(run)


if __name__ == '__main__':
    unittest.main()
