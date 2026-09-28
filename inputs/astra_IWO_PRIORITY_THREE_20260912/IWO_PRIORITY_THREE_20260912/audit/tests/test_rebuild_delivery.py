"""Delivery transformation tests only; no simulator and no fabricated run results."""
import sys
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import rebuild_delivery as delivery


# A parser fixture, not an ATLAS simulation or runnable device model.
SOURCE = '''go atlas
title UNIT_TEST_ONLY transfer.log is a literal label
# A comment referring to geometry.str must remain unchanged.
material material=IWO mun=13 affinity=4.3
defects region=2 continuous numa=384 numd=192 \\
 nta=7.33333333e20 wta=.03 afile=bulk_acceptor.dat dfile=bulk_donor.dat
intdefects intnumber="2/3" max.gaussian \\
 afile="interface_acceptor.dat" dfile="interface_donor.dat" tfile="interface_dos.dat"
method newton carriers=1 electrons cr.toler=1e-20
save outf=geometry.str
solve init
log outf=transfer.log
solve vgate=-3
solve vgate=3
log off
save outf=final.str
extract init infile="transfer.log"
extract name="idvg" curve(v."gate",i."drain") outfile="idvg.dat"
quit
'''


class RebuildDeliveryTests(unittest.TestCase):
    def test_only_filename_assignments_change_and_physics_is_identical(self):
        text, mapping, digest = delivery.delivery_block(SOURCE, 'iwo_2p0nm')
        self.assertIn('title UNIT_TEST_ONLY transfer.log is a literal label', text)
        self.assertIn('# A comment referring to geometry.str must remain unchanged.', text)
        self.assertIn('material material=IWO mun=13 affinity=4.3', text)
        self.assertIn('nta=7.33333333e20 wta=.03', text)
        self.assertIn('extract init infile="iwo_2p0nm_transfer.log"', text)
        self.assertIn('outfile="iwo_2p0nm_idvg.dat"', text)
        self.assertIn('afile="iwo_2p0nm_interface_acceptor.dat"', text)
        self.assertEqual(digest, delivery.verify_equivalence(SOURCE, text, mapping))
        self.assertEqual([r.strip() for r in delivery.logical_records(text)
                          if delivery.command_name(r) == 'tonyplot'],
                         ['tonyplot iwo_2p0nm_geometry.str', 'tonyplot iwo_2p0nm_transfer.log',
                          'tonyplot iwo_2p0nm_final.str'])

    def test_physics_mutation_cannot_hide_behind_canonical_filename_check(self):
        text, mapping, _ = delivery.delivery_block(SOURCE, 'iwo_2p0nm')
        for old, new in [('mun=13', 'mun=14'), ('wta=.03', 'wta=.04'),
                         ('cr.toler=1e-20', 'cr.toler=1e-6'), ('solve vgate=3', 'solve vgate=2.9')]:
            with self.subTest(mutation=new):
                with self.assertRaisesRegex(ValueError, 'Non-output ATLAS commands changed'):
                    delivery.verify_equivalence(SOURCE, text.replace(old, new), mapping)

    def test_combined_blocks_retain_all_physics_and_unique_outputs(self):
        first, first_map, digest = delivery.delivery_block(SOURCE, 'iwo_2p0nm', intermediate=True)
        second, second_map, _ = delivery.delivery_block(SOURCE, 'iwo_6p3nm')
        self.assertFalse(set(first_map.values()) & set(second_map.values()))
        self.assertEqual(delivery.verify_equivalence(SOURCE, first, first_map, intermediate=True), digest)
        commands = delivery.canonical_commands(first + second)
        self.assertEqual(commands.count('go atlas'), 2)
        self.assertEqual(commands.count('quit'), 1)
        self.assertEqual(commands[-1], 'quit')
        self.assertEqual(commands.count('material material=iwo mun=13 affinity=4.3'), 2)

    def test_missing_plot_external_input_and_unsafe_filename_are_rejected(self):
        text, mapping, _ = delivery.delivery_block(SOURCE, 'iwo_2p0nm')
        with self.assertRaisesRegex(ValueError, 'TonyPlot must cover'):
            delivery.verify_equivalence(SOURCE, text.replace('tonyplot iwo_2p0nm_final.str\n', ''), mapping)
        with self.assertRaisesRegex(ValueError, 'not produced earlier'):
            delivery.delivery_block(SOURCE.replace('infile="transfer.log"', 'infile="stale.log"'), 'iwo_2p0nm')
        with self.assertRaisesRegex(ValueError, 'plain project-local'):
            delivery.delivery_block(SOURCE.replace('outf=geometry.str', 'outf=../geometry.str'), 'iwo_2p0nm')
        with self.assertRaisesRegex(ValueError, 'Unsafe output prefix'):
            delivery.delivery_block(SOURCE, '../escape')

    def test_verification_failure_creates_no_delivery_directory(self):
        with tempfile.TemporaryDirectory(prefix='UNIT_TEST_DELIVERY_', dir=ROOT / 'tmp') as folder:
            base = Path(folder)
            out = base / 'must_not_exist'
            with patch.object(delivery.check, 'load_run', side_effect=ValueError('Raw hash mismatch')) as verify:
                with self.assertRaisesRegex(ValueError, 'Raw hash mismatch'):
                    delivery.package([base / 'UNVERIFIED_SOURCE'], out)
                verify.assert_called_once()
            self.assertFalse(out.exists())

    def test_existing_output_and_implicit_run_selection_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='UNIT_TEST_DELIVERY_', dir=ROOT / 'tmp') as folder:
            with self.assertRaisesRegex(ValueError, 'new, nonexistent'):
                delivery.package([Path(folder) / 'SOURCE'], folder)
            with self.assertRaisesRegex(ValueError, 'explicit evaluated run'):
                delivery.package([], Path(folder) / 'UNUSED')

    def test_signed_positive_log_denominators_exclude_zero_and_negative_current(self):
        # Pure numerical UNIT TEST values, not ATLAS observations or fit evidence.
        run = dict(measured=np.ones(4), terminal={'id': np.array([0., -1., 1., 10.])},
                   active=np.array([False, False, True, True]), vg=np.arange(4.))
        report = delivery.measured_metrics(run)
        all_region = report['regions']['all']
        self.assertEqual(all_region['target_count'], 4)
        self.assertEqual(all_region['linear_denominator'], 4)
        self.assertEqual(all_region['positive_log_denominator'], 2)
        self.assertEqual(all_region['excluded_nonpositive_log_count'], 2)
        self.assertFalse(all_region['positive_log_complete'])
        self.assertAlmostEqual(all_region['rmse_positive_log10_decades'], np.sqrt(.5))
        low = report['regions']['low_current']
        self.assertEqual(low['native_zero_count'], 1)
        self.assertEqual(low['native_negative_count'], 1)
        self.assertEqual(low['positive_log_denominator'], 0)
        self.assertIsNone(low['rmse_positive_log10_decades'])
        diagnostic = report['guarded_all_log_diagnostic']
        self.assertEqual(diagnostic['status'], 'DIAGNOSTIC_ONLY_NOT_A_VALID_SIGNED_CURRENT_LOG_FIT')
        self.assertEqual(diagnostic['guarded_point_count'], 1)
        self.assertEqual(diagnostic['negative_magnitude_point_count'], 1)
        # Missing logs must serialize as JSON null, never NaN or a fake floor fit.
        json.dumps(report, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
