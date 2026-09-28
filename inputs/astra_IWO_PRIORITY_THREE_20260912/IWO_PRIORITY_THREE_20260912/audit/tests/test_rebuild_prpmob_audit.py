"""SYNTHETIC UNIT FIXTURES ONLY; no simulator, calibration or native-result claim."""
import copy
import csv
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebuild_prpmob_audit as audit
import rebuild_check as check
import test_rebuild_check as fixture_module


class PrpmobAuditTests(unittest.TestCase):
    def setUp(self):
        guard = patch('subprocess.Popen', side_effect=AssertionError('Synthetic tests cannot launch any process'))
        guard.start(); self.addCleanup(guard.stop)
        self.fixtures = fixture_module.RebuildCheckTests()
        self.fixtures.setUp()
        self.addCleanup(self.fixtures.doCleanups)
        self.base = self.fixtures.base
        self.cfg = copy.deepcopy(self.fixtures.cfg)
        self.cfg['transport'].update(mode='prpmob', critical_field_V_cm=1e6)
        self.cfg['curves']['31p8']['mu_band_cm2Vs'] = 55.
        self.cfg['diagnostics'] = dict(trap_charge=True, depth_electrons=True, colocate_prp_probes=True)

    def fixture(self, cfg=None, mismatch=False):
        cfg = copy.deepcopy(self.cfg if cfg is None else cfg)
        cols = {name:11+i for i,name in enumerate(check.expected_extras(cfg))}
        def mutate(native, active):
            # Deliberate mathematical unit data, not predicted transistor output.
            width = cfg['geometry']['simulation_width_um']
            native[:, 2] = width*1e-20
            native[:, 5] = -native[:, 8]-native[:, 2]
            mun = cfg['curves']['31p8']['mu_band_cm2Vs']
            if cfg['transport']['mode'] == 'prpmob':
                for mu_col, ey_name, start, end in [
                    (9, 'channel_ey', -2e6, 2e6),
                    (cols['front_mobility'], 'front_ey', -1e6, 3e6),
                    (cols['back_mobility'], 'back_ey', -3e5, 3e5),
                ]:
                    ey = np.linspace(start, end, 121)
                    native[:, cols[ey_name]] = ey
                    native[:, mu_col] = mun/(1+abs(ey)/1e6)
                if mismatch:
                    native[:, cols['front_mobility']] *= .8
            if 'bulk_front_electrons' in cols:
                native[:, cols['bulk_front_electrons']] = 1e14
                native[0, cols['bulk_front_electrons']] = 0
                native[:, cols['bulk_back_electrons']] = 1e16
        return self.fixtures.fixture(cfg, key='31p8', mutate=mutate)

    def test_native_signs_units_and_zero_density_are_preserved(self):
        prepared = audit.prepare(self.fixture())
        self.assertEqual(len(prepared['rows']), 121)
        first, middle = prepared['rows'][0], prepared['rows'][60]
        self.assertLess(first['front_native_signed_ey_V_per_cm'], 0)
        self.assertGreater(prepared['rows'][-1]['front_native_signed_ey_V_per_cm'], 0)
        self.assertLess(first['native_is_A_per_um'], 0)
        self.assertGreater(first['native_ig_A_per_um'], 0)
        self.assertEqual(first['front_native_n_cm3'], 0)
        self.assertEqual(first['front_diagnostic_local_conductivity_proxy_S_per_cm'], 0)
        self.assertAlmostEqual(middle['middle_diagnostic_local_conductivity_proxy_S_per_cm'], audit.Q*1e15*55)
        self.assertAlmostEqual(middle['middle_native_mu_over_MUN'], 1)
        self.assertAlmostEqual(middle['middle_diagnostic_mu_ratio_from_abs_Ey'], 1)
        for values in prepared['summary']['local_comparison_statistics'].values():
            self.assertLess(values['max_abs_ratio_difference'], 1e-14)
        self.assertFalse(prepared['summary']['measurement_fit_validated'])
        self.assertFalse(prepared['summary']['mesh_or_DOS_convergence_granted'])
        self.assertEqual(prepared['summary']['evidence_kind'], 'SYNTHETIC_UNIT_TEST_ONLY')

    def test_disagreement_is_reported_without_replacing_mobility_or_current(self):
        prepared = audit.prepare(self.fixture(mismatch=True))
        statistics = prepared['summary']['local_comparison_statistics']['front']
        self.assertAlmostEqual(statistics['max_abs_ratio_difference'], .2)
        self.assertAlmostEqual(statistics['max_abs_relative_ratio_difference'], .2)
        row = prepared['rows'][30]  # Synthetic front Ey=0, native mobility deliberately reduced.
        self.assertAlmostEqual(row['front_native_mu_cm2_Vs'], 44)
        self.assertAlmostEqual(row['front_diagnostic_mu_ratio_from_abs_Ey'], 1)
        self.assertAlmostEqual(row['native_id_A_per_um'], prepared['run']['terminal']['id'][30])
        self.assertIn('NOT_PHYSICAL_OR_FIT_ACCEPTANCE', prepared['summary']['status'])

    def test_complete_synthetic_report_has_121_rows_plots_manifest_and_no_raw_writes(self):
        folder = self.fixture()
        before = {p.name:check.sha(p) for p in folder.iterdir() if p.is_file()}
        out = self.base/'SYNTHETIC_LOCAL_FIELD_REPORT'
        summary = audit.create_report(folder, out)
        with (out/'native_prpmob_all_121.csv').open(newline='') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 121)
        self.assertEqual(float(rows[0]['front_native_n_cm3']), 0)
        self.assertEqual(summary['evidence_kind'], 'SYNTHETIC_UNIT_TEST_ONLY')
        self.assertEqual(len(list(out.glob('*.png'))), 3)
        self.assertEqual(len(list(out.glob('*.pdf'))), 3)
        manifest = json.loads((out/'report_manifest.json').read_text())
        self.assertTrue(all(check.sha(out/name) == digest for name,digest in manifest.items()))
        after = {p.name:check.sha(p) for p in folder.iterdir() if p.is_file()}
        self.assertEqual(before, after)

    def test_timeout_or_missing_gate_rejected_without_output(self):
        for failure in ('timeout', 'missing_gate'):
            with self.subTest(failure=failure):
                folder = self.fixture()
                if failure == 'timeout':
                    record = json.loads((folder/'execution.json').read_text())
                    record.update(returncode=None, status='SYNTHETIC_TIMEOUT')
                    (folder/'execution.json').write_text(json.dumps(record))
                else:
                    path = folder/'transfer.log'
                    path.write_text('\n'.join(path.read_text().splitlines()[:-1]))
                    self.fixtures.rehash(folder)
                out = self.base/('SYNTHETIC_REFUSED_'+failure)
                with self.assertRaises(ValueError):
                    audit.create_report(folder, out)
                self.assertFalse(out.exists())

    def test_requires_explicit_prpmob_and_colocated_depth_schema(self):
        for mode, colocate in [('constant', False), ('prpmob', False)]:
            with self.subTest(mode=mode, colocate=colocate):
                cfg = copy.deepcopy(self.cfg)
                cfg['transport']['mode'] = mode
                cfg['diagnostics']['colocate_prp_probes'] = colocate
                with self.assertRaisesRegex(ValueError, 'Requires PRPMOB'):
                    audit.prepare(self.fixture(cfg))
        cfg = copy.deepcopy(self.cfg)
        del cfg['diagnostics']['colocate_prp_probes']
        with self.assertRaisesRegex(ValueError, 'Requires PRPMOB'):
            audit.prepare(self.fixture(cfg))

    def test_changed_generated_coordinate_and_native_schema_are_rejected(self):
        for failure in ('coordinate', 'probe_header'):
            with self.subTest(failure=failure):
                folder = self.fixture()
                if failure == 'coordinate':
                    p = folder/'device.in'
                    p.write_text(re.sub(r'(probe name=front_ey x=12.037 y=)-0.001\b', r'\g<1>-0.002', p.read_text()))
                else:
                    p = folder/'transfer.log'
                    p.write_text(p.read_text().replace(' front_ey\n', ' wrong_front_field\n'))
                self.fixtures.rehash(folder)
                with self.assertRaises(ValueError):
                    audit.prepare(folder)

    def test_reserved_unfinished_neighbor_and_existing_output_rejected_before_load(self):
        project = self.base/'SYNTHETIC_PROJECT'
        raw = project/'results/local_session_20260910/runs'
        neighbor = raw/'SYNTHETIC_UNFINISHED'
        neighbor.mkdir(parents=True)
        marker = neighbor/'marker.txt'; marker.write_text('SYNTHETIC preserve me')
        source = project/'SYNTHETIC_ARCHIVED_COPY'
        existing = project/'existing_report'; existing.mkdir()
        for out in (neighbor/'MUST_NOT_EXIST', existing):
            with self.subTest(out=out), patch.object(audit, 'ROOT', project), \
                    patch.object(audit, 'strictload_run') as loader:
                with self.assertRaises(ValueError):
                    audit.create_report(source, out)
                loader.assert_not_called()
        self.assertEqual(list(neighbor.iterdir()), [marker])
        self.assertEqual(list(existing.iterdir()), [])

    def test_concurrent_new_output_is_preserved(self):
        folder = self.fixture()
        prepared = audit.prepare(folder)
        out = self.base/'SYNTHETIC_CONCURRENT_REPORT'
        def another_writer(_):
            out.mkdir()
            (out/'keep.txt').write_text('SYNTHETIC concurrent writer')
            return prepared
        with patch.object(audit, 'prepare', side_effect=another_writer), patch.object(audit, 'plots') as plotter:
            with self.assertRaises(FileExistsError):
                audit.create_report(folder, out)
            plotter.assert_not_called()
        self.assertEqual(list(out.iterdir()), [out/'keep.txt'])


if __name__ == '__main__':
    unittest.main()
