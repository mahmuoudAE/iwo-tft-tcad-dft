"""SYNTHETIC unit fixtures only; no simulator or real validation claim."""
import copy
import io
import json
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_rebuild_check as fixture_module
import rebuild_check as check
import rebuild_extension_check as extension


class ExtensionCheckTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = fixture_module.RebuildCheckTests()
        self.fixtures.setUp()
        self.addCleanup(self.fixtures.doCleanups)
        self.cfg = copy.deepcopy(self.fixtures.cfg)
        self.cfg['defects'].update(bulk=True, interface=False)
        self.base = self.fixtures.base
        self.basis_paths = self.paths(self.cfg, '2p0')
        self.basis = self.base / 'SYNTHETIC_2NM_CERTIFICATE.json'
        args = []
        for kind, path in self.basis_paths.items():
            args += ['--' + kind, str(path)]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check.main(args + ['--out', str(self.basis)]), 0)

    def paths(self, cfg, key='13p2'):
        result = {'reference': self.fixtures.fixture(cfg, key=key)}
        for kind in ('width', 'xmesh', 'ymesh', 'dos'):
            variant = copy.deepcopy(cfg)
            if kind == 'width':
                variant['geometry']['simulation_width_um'] *= 2
            elif kind == 'xmesh':
                variant['numerics']['x_spacing_um'] /= 2
                variant['numerics']['contact_edge_spacing_um'] /= 2
            elif kind == 'ymesh':
                for name in ('channel_intervals', 'alumina_intervals', 'hafnia_intervals'):
                    variant['numerics'][name] *= 2
            else:
                variant['defects']['bulk_levels_a'] *= 2
                variant['defects']['bulk_levels_d'] *= 2
            result[kind] = self.fixtures.fixture(variant, key=key)
        return result

    def assess(self, paths, width=False):
        with patch('subprocess.Popen', side_effect=AssertionError('Unit test cannot launch a process')):
            return extension.assess(paths['reference'], {k: paths.get(k) for k in extension.SPATIAL_ENERGY_KINDS},
                                    self.basis, paths['width'] if width else None)

    def test_transferred_units_are_scoped_and_never_an_inherited_four_check_certificate(self):
        paths = self.paths(self.cfg)
        before = {str(p): check.sha(p) for folder in paths.values() for p in folder.iterdir() if p.is_file()}
        result = self.assess(paths)
        self.assertEqual(result['status'], 'PASS_SCOPED_EXTENSION_NUMERICS')
        self.assertTrue(result['spatial_and_energy_checks_passed'])
        self.assertTrue(result['normalization_check_passed'])
        self.assertFalse(result['per_device_width_test_performed'])
        self.assertIsNone(result['per_device_width_test_passed'])
        self.assertNotIn('all_required_checks_passed', result)
        self.assertFalse(result['measurement_fit_validated'])
        self.assertFalse(result['predictive_validity_established'])
        after = {str(p): check.sha(p) for folder in paths.values() for p in folder.iterdir() if p.is_file()}
        self.assertEqual(before, after)

    def test_contact_resistance_cannot_inherit_width_but_can_use_its_own_test(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['contacts']['resistance_ohm_um'] = 1e5
        paths = self.paths(cfg, key='31p8')
        rejected = self.assess(paths)
        self.assertEqual(rejected['status'], 'FAIL')
        self.assertTrue(rejected['spatial_and_energy_checks_passed'])
        self.assertFalse(rejected['normalization_check_passed'])
        self.assertIn('REQUIRES_EXPLICIT_WIDTH_RUN', rejected['normalization_basis']['extension_use'])
        accepted = self.assess(paths, width=True)
        self.assertEqual(accepted['status'], 'PASS_SCOPED_EXTENSION_NUMERICS')
        self.assertTrue(accepted['per_device_width_test_performed'])
        self.assertTrue(accepted['per_device_width_test_passed'])
        self.assertEqual(accepted['validated_scope'], 'DEVICE_X_Y_DOS_AND_REPEATED_WIDTH_CHECK')

    def test_missing_and_failed_controls_never_pass(self):
        paths = self.paths(self.cfg)
        missing = dict(paths)
        missing['dos'] = None
        result = self.assess(missing)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['spatial_and_energy_checks_passed'])
        self.assertEqual(result['checks']['dos']['status'], 'MISSING')
        # An actual distinct-control fixture with a 3% active current error fails unchanged thresholds.
        cfg = check.read_json(paths['xmesh'] / 'input_config.json')
        def mutate(native, active):
            native[-1, 8] *= 1.03
            native[-1, 5] = -native[-1, 8]
        paths['xmesh'] = self.fixtures.fixture(cfg, key='13p2', mutate=mutate)
        result = self.assess(paths)
        self.assertEqual(result['status'], 'FAIL')
        self.assertFalse(result['checks']['xmesh']['pass_check'])
        self.assertFalse(result['spatial_and_energy_checks_passed'])

    def test_changed_affinity_or_contact_form_prevents_transfer(self):
        for change in ('affinity', 'contact'):
            with self.subTest(change=change):
                cfg = copy.deepcopy(self.cfg)
                if change == 'affinity':
                    cfg['shared']['affinity_eV'] += .1
                else:
                    cfg['contacts']['mode'] = 'schottky'
                result = self.assess(self.paths(cfg))
                self.assertEqual(result['status'], 'FAIL')
                self.assertFalse(result['normalization_check_passed'])

    def test_changed_actual_atlas_version_prevents_transfer(self):
        paths = self.paths(self.cfg)
        for folder in paths.values():
            path = folder / 'deckbuild.out'
            path.write_text(path.read_text().replace('atlas 5.0', 'atlas 5.1').replace('version 5.0', 'version 5.1'))
            self.fixtures.rehash(folder)
        result = self.assess(paths)
        self.assertTrue(result['spatial_and_energy_checks_passed'])
        self.assertFalse(result['normalization_check_passed'])
        self.assertFalse(result['normalization_basis']['extension_compatibility']['conditions']['same_atlas_version'])

    def test_normalization_source_is_pinned_and_recomputed(self):
        paths = self.paths(self.cfg)
        path = self.basis_paths['width'] / 'idvg.dat'
        path.write_text(path.read_text() + '\nALTERED SYNTHETIC FIXTURE')
        self.fixtures.rehash(self.basis_paths['width'])
        result = self.assess(paths)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['normalization_basis']['status'], 'INVALID_OR_INCOMPLETE')
        self.assertIn('Pinned normalization evidence changed', result['normalization_basis']['error'])

    def test_incomplete_source_certificate_does_not_supply_normalization(self):
        paths = self.paths(self.cfg)
        record = check.read_json(self.basis)
        record['all_required_checks_passed'] = False
        self.basis.write_text(json.dumps(record))
        result = self.assess(paths)
        self.assertFalse(result['normalization_check_passed'])
        self.assertEqual(result['status'], 'FAIL')

    def test_optional_width_failure_is_not_ignored_in_favor_of_transfer(self):
        paths = self.paths(self.cfg)
        cfg = check.read_json(paths['width'] / 'input_config.json')
        paths['width'] = self.fixtures.fixture(cfg, key='13p2', mutate=lambda a, active: a.__setitem__((-1, 9), 0))
        result = self.assess(paths, width=True)
        self.assertTrue(result['per_device_width_test_performed'])
        self.assertFalse(result['per_device_width_test_passed'])
        self.assertEqual(result['status'], 'FAIL')

    def test_cli_writes_only_new_project_json_outside_raw_runs(self):
        paths = self.paths(self.cfg)
        args = ['--normalization-report', str(self.basis)]
        for kind in ('reference',) + extension.SPATIAL_ENERGY_KINDS:
            args += ['--' + kind, str(paths[kind])]
        output = self.base / 'SYNTHETIC_EXTENSION_SCOPE.json'
        with redirect_stdout(io.StringIO()), patch('subprocess.Popen', side_effect=AssertionError('No launcher')):
            self.assertEqual(extension.main(args + ['--out', str(output)]), 0)
        self.assertNotIn('all_required_checks_passed', check.read_json(output))
        for path in (output, paths['reference'] / 'new.json', check.ROOT.parent / 'outside.json'):
            with self.subTest(path=path), patch('sys.stderr', io.StringIO()):
                with self.assertRaises(SystemExit):
                    extension.main(args + ['--out', str(path)])


if __name__ == '__main__':
    unittest.main()
