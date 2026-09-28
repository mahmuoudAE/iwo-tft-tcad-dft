"""Priority delivery safety/reproduction tests; no simulator or final package."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import rebuild_priority_delivery as priority
import rebuild_model as model


def stub(key='2p0', run_id='UNIT_TEST_REFERENCE'):
    """Identity-only UNIT TEST fixture; it never passes a real native loader."""
    return dict(key=key, cfg={'defects': {'bulk': True, 'interface': False}},
                summary=dict(run_id=run_id, key=key, run_acceptable=True,
                             directory=str(ROOT / 'tmp' / run_id),
                             evidence_sha256={'input_config.json': 'UNIT_TEST_HASH'}))


def full_fixture():
    reference = stub()
    candidates = {kind: stub(run_id='UNIT_TEST_' + kind) for kind in ('width', 'xmesh', 'ymesh', 'dos')}
    saved = dict(status='PASS', all_required_checks_passed=True,
                 thresholds=priority.check.LIMITS, reference=reference['summary'],
                 checks={kind: dict(status='PASS', pass_check=True, candidate=run['summary'])
                         for kind, run in candidates.items()})
    by_id = {run['summary']['run_id']: run for run in [reference, *candidates.values()]}
    return reference, saved, by_id


class PriorityDeliveryTests(unittest.TestCase):
    def test_exact_priority_three_and_no_duplicate_or_deferred_device(self):
        paths = [ROOT / 'tmp' / ('UNIT_TEST_' + key) for key in priority.KEYS]
        with self.assertRaisesRegex(ValueError, 'exactly three'):
            priority.selected_runs(paths[:2])
        with self.assertRaisesRegex(ValueError, 'Duplicate selected'):
            priority.selected_runs([paths[0], paths[0], paths[2]])
        for keys in [('2p0', '6p3', '31p8'), ('2p0', '6p3', '6p3'), ('2p0', '6p3', 'UNKNOWN')]:
            with patch.object(priority.check, 'load_run', side_effect=[stub(key) for key in keys]):
                with self.assertRaisesRegex(ValueError, 'exactly one run'):
                    priority.selected_runs(paths)
        with patch.object(priority.check, 'load_run', side_effect=[stub(key) for key in reversed(priority.KEYS)]):
            self.assertEqual(list(priority.selected_runs(paths)), list(priority.KEYS))

    def test_bad_certificate_keys_and_duplicates_are_not_silently_replaced(self):
        for entries in [['31p8=a.json'], ['6p3'], ['6p3='], ['6p3=a.json', '6p3=b.json']]:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                priority.certificate_options(entries)
        self.assertEqual(set(priority.certificate_options(['2p0=a.json', '6p3=b.json'])), {'2p0', '6p3'})

    def test_old_physical_reference_cannot_donate_certificate(self):
        chosen = stub('6p3', 'UNIT_TEST_NEW_MOBILITY')
        old = stub('6p3', 'UNIT_TEST_OLD_MOBILITY')
        with patch.object(priority.extension, 'pinned_run', return_value=old):
            with self.assertRaisesRegex(ValueError, 'differs from selected physical candidate'):
                priority.same_reference(old['summary'], chosen)
        changed_hash = copy.deepcopy(chosen)
        changed_hash['summary']['evidence_sha256']['input_config.json'] = 'UNIT_TEST_CHANGED_HASH'
        with patch.object(priority.extension, 'pinned_run', return_value=changed_hash):
            with self.assertRaisesRegex(ValueError, 'differs from selected physical candidate'):
                priority.same_reference(chosen['summary'], chosen)

    def test_full_certificate_recomputes_all_native_controls(self):
        reference, saved, by_id = full_fixture()
        with patch.object(priority.extension, 'pinned_run', side_effect=lambda s: by_id[s['run_id']]), \
             patch.object(priority.extension, 'atlas_version', return_value='5.28.1.R'), \
             patch.object(priority.check, 'compare', return_value=dict(status='PASS', pass_check=True)) as compare:
            result = priority.full_certificate(saved, reference)
            self.assertEqual([call.args[2] for call in compare.call_args_list], ['width', 'xmesh', 'ymesh', 'dos'])
            self.assertEqual(result['validated_scope'], 'DEVICE_WIDTH_X_Y_DOS')
            self.assertFalse(result['predictive_validity_established'])
        saved['thresholds'] = dict(priority.check.LIMITS, ion_relative=.5)
        with self.assertRaisesRegex(ValueError, 'changed thresholds'):
            priority.full_certificate(saved, reference)

    def test_recorded_pass_does_not_override_failed_current_or_physics_check(self):
        reference, saved, by_id = full_fixture()
        with patch.object(priority.extension, 'pinned_run', side_effect=lambda s: by_id[s['run_id']]), \
             patch.object(priority.extension, 'atlas_version', return_value='5.28.1.R'), \
             patch.object(priority.check, 'compare', return_value=dict(status='FAIL', pass_check=False)):
            with self.assertRaisesRegex(ValueError, 'Recomputed numerical control failed'):
                priority.full_certificate(saved, reference)

    def test_scope_reloads_control_references_and_normalization_pin(self):
        reference = stub('6p3', 'UNIT_TEST_SCOPED')
        controls = {k: stub('6p3', 'UNIT_TEST_SCOPE_' + k) for k in ('xmesh', 'ymesh', 'dos')}
        with tempfile.TemporaryDirectory(prefix='UNIT_TEST_PRIORITY_', dir=ROOT / 'tmp') as folder:
            root = Path(folder)
            basis = root / 'basis.json'
            basis_ref = stub()
            basis.write_text(json.dumps({'reference': basis_ref['summary']}))
            saved = dict(status='PASS_SCOPED_EXTENSION_NUMERICS', thresholds=priority.check.LIMITS,
                         reference=reference['summary'],
                         validated_scope='DEVICE_X_Y_DOS_WITH_TRANSFERRED_WIDTH_UNIT_CONVENTION',
                         normalization_basis=dict(source_report=str(basis), source_report_sha256=priority.check.sha(basis)),
                         checks={k: dict(status='PASS', pass_check=True, candidate=v['summary']) for k, v in controls.items()},
                         per_device_width_test_performed=False)
            cert = root / 'scoped.json'
            cert.write_text(json.dumps(saved))
            by_id = {r['summary']['run_id']: r for r in [reference, basis_ref, *controls.values()]}
            recomputed = dict(status='PASS_SCOPED_EXTENSION_NUMERICS', validated_scope=saved['validated_scope'])
            with patch.object(priority.extension, 'pinned_run', side_effect=lambda s: by_id[s['run_id']]), \
                 patch.object(priority, 'full_certificate', return_value={'status': 'PASS'}) as full, \
                 patch.object(priority.extension, 'assess', return_value=recomputed) as assess:
                result = priority.verified_certificate(cert, reference)
                full.assert_called_once()
                self.assertEqual(assess.call_args.args[1], {k: v['summary']['directory'] for k, v in controls.items()})
                self.assertEqual(result['selected_run_id'], reference['summary']['run_id'])
                self.assertEqual(len(result['supporting_certificates']), 1)
                basis.write_text('{}')
                with self.assertRaisesRegex(ValueError, 'Pinned normalization certificate changed'):
                    priority.verified_certificate(cert, reference)

    def test_bad_evidence_or_certificate_leaves_output_uncreated(self):
        with tempfile.TemporaryDirectory(prefix='UNIT_TEST_PRIORITY_', dir=ROOT / 'tmp') as folder:
            out = Path(folder) / 'not_created'
            paths = [ROOT / 'tmp' / ('UNIT_TEST_' + k) for k in priority.KEYS]
            with patch.object(priority.check, 'load_run', side_effect=ValueError('UNIT_TEST raw hash failure')):
                with self.assertRaisesRegex(ValueError, 'raw hash failure'):
                    priority.build(paths, out)
            self.assertFalse(out.exists())
            runs = {k: stub(k, 'UNIT_TEST_' + k) for k in priority.KEYS}
            with patch.object(priority, 'selected_runs', return_value=runs), \
                 patch.object(priority, 'verified_certificate', side_effect=ValueError('UNIT_TEST stale certificate')):
                with self.assertRaisesRegex(ValueError, 'stale certificate'):
                    priority.build(paths, out, {'6p3': ROOT / 'tmp/UNIT_TEST_CERT.json'})
            self.assertFalse(out.exists())

    def test_new_directory_and_reserved_raw_namespace_guards(self):
        paths = [ROOT / 'tmp' / ('UNIT_TEST_' + k) for k in priority.KEYS]
        for out in [ROOT, ROOT / 'scripts', ROOT.parent / 'OUTSIDE_UNIT_TEST',
                    ROOT / 'results/local_session_20260910/runs/UNIT_TEST_RUNNING/no_output']:
            with self.subTest(out=out), patch.object(priority, 'selected_runs') as select:
                with self.assertRaises(ValueError):
                    priority.build(paths, out)
                select.assert_not_called()

    def test_report_cli_uses_one_plural_runs_argument_and_missing_31_panel(self):
        paths = [ROOT / 'tmp' / ('UNIT_TEST_' + k) for k in priority.KEYS]
        out = ROOT / 'tmp/UNIT_TEST_NO_REPORT_WRITTEN'
        with patch.object(priority.report, 'main', return_value=0) as main, \
             patch.object(priority.visual, 'overview', return_value=dict(selected_keys=list(priority.KEYS), missing_keys=['31p8'])):
            priority.generate_reports(paths, out)
            self.assertEqual(main.call_args.args[0], ['--runs', *map(str, paths), '--out', str(out / 'reports')])
        with patch.object(priority.report, 'main', return_value=0), \
             patch.object(priority.visual, 'overview', return_value=dict(selected_keys=list(priority.KEYS), missing_keys=[])):
            with self.assertRaisesRegex(ValueError, '31.8 nm missing'):
                priority.generate_reports(paths, out)

    def test_copied_generator_reproduces_commands_and_catches_config_change(self):
        # Renderer-only fixtures use the real seed/voltage targets. No native
        # results are invented and no fixture passes a native-run validator.
        cfg = model.load(ROOT / 'config/rebuild_seed.json')
        runs = {k: dict(key=k, deck=model.render(cfg, k, plots=False)[0],
                        summary={'run_id': 'UNIT_TEST_RENDER_ONLY_' + k}) for k in priority.KEYS}
        with tempfile.TemporaryDirectory(prefix='UNIT_TEST_PRIORITY_', dir=ROOT / 'tmp') as folder:
            out = Path(folder)
            (out / 'scripts').mkdir()
            (out / 'config').mkdir()
            (out / 'data').mkdir()
            shutil.copyfile(ROOT / 'scripts/rebuild_model.py', out / 'scripts/rebuild_model.py')
            for key in priority.KEYS:
                (out / 'config' / ('iwo_' + key + 'nm.json')).write_text(json.dumps(cfg))
                shutil.copyfile(ROOT / priority.check.DATA[key], out / priority.check.DATA[key])
            result = priority.reproduce_copied_generator(out, runs)
            self.assertEqual(set(result), set(priority.KEYS))
            self.assertTrue(all(row['command_equivalence_pass'] for row in result.values()))
            cfg['curves']['6p3']['mu_band_cm2Vs'] *= 1.2
            (out / 'config/iwo_6p3nm.json').write_text(json.dumps(cfg))
            with self.assertRaisesRegex(ValueError, 'changed source commands for 6p3'):
                priority.reproduce_copied_generator(out, runs)

    def test_narrative_metrics_keep_nonpositive_counts_and_missing_certificate(self):
        # Pure UNIT TEST residual-policy values, never an ATLAS export.
        run = dict(key='2p0', measured=np.ones(4), terminal={'id': np.array([0., -1., 1., 1.])},
                   active=np.array([False, False, True, True]), vg=np.array([-3., -2., 2., 3.]),
                   cfg={'curves': {'2p0': {'thickness_nm': 2}}}, summary={'run_id': 'UNIT_TEST_METRICS_ONLY'})
        row = priority.assessment_rows({'2p0': run}, {})[0]
        self.assertTrue(row['active_fit_targets_met'])
        self.assertEqual(row['native_zero_points'], 1)
        self.assertEqual(row['native_negative_points'], 1)
        self.assertEqual(row['metrics']['regions']['all']['positive_log_denominator'], 2)
        self.assertEqual(row['numerical_status'], 'NOT_SUPPLIED')
        self.assertFalse(row['full_curve_fit_established'])
        self.assertFalse(row['predictive_validity_established'])
        json.dumps(row, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
