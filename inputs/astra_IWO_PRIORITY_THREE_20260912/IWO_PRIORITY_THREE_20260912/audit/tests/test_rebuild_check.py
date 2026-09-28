"""SYNTHETIC UNIT TESTS ONLY: fixtures are not ATLAS simulations or fit results.

All fabricated raw records live in a TemporaryDirectory under project/tmp and
are removed by unittest cleanup. No solver, process launcher, or budget is used.
"""
import copy
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import rebuild_check as check
from rebuild_model import render


class RebuildCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='SYNTHETIC_rebuild_unit_', dir=check.ROOT / 'tmp')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.cfg = check.read_json(check.ROOT / 'config/rebuild_seed.json')
        # These are deliberately fabricated unit-test data, never model evidence.
        self.counter = 0

    def rehash(self, folder):
        record = check.read_json(folder / 'execution.json')
        record['deck_sha256'] = check.sha(folder / 'device.in')
        record['config_sha256'] = check.sha(folder / 'input_config.json')
        record['outputs'] = {p.name: check.sha(p) for p in folder.iterdir()
                             if p.is_file() and p.name not in {'execution.json', 'comparison_all_measurements.csv'}}
        (folder / 'execution.json').write_text(json.dumps(record))

    def fixture(self, cfg=None, key='2p0', mutate=None):
        cfg = copy.deepcopy(cfg if cfg is not None else self.cfg)
        self.counter += 1
        folder = self.base / ('SYNTHETIC_NOT_ATLAS_' + str(self.counter))
        folder.mkdir()
        observed = check.table(check.ROOT / check.DATA[key])
        vg = np.array([float(r['vg_V']) for r in observed])
        measured = np.array([float(r['id_A_per_um']) for r in observed])
        off = np.median(measured[(vg >= -2) & (vg <= -.5)])
        active = measured > 5 * off if key != '31p8' else np.ones(len(vg), bool)
        width = cfg['geometry']['simulation_width_um']
        extra = check.expected_extras(cfg)
        native = np.zeros((len(vg), 11 + len(extra)))
        native[:, 0] = native[:, 1] = vg
        native[:, 6] = native[:, 7] = cfg['shared']['vd_V']
        native[:, 8] = width * np.logspace(-16, -7, len(vg))
        native[:, 5] = -native[:, 8]
        native[:, 9], native[:, 10] = 10., 1e15
        for index, name in enumerate(extra, start=11):
            native[:, index] = (1e15 if name == 'bulk_free_electrons' else 0 if name.startswith('bulk_')
                                else 8 if 'mobility' in name else -1e5)
        if cfg['contacts'].get('resistance_ohm_um', 0) > 0:
            native[:, 4], native[:, 7] = .01, cfg['shared']['vd_V'] - .01
        if mutate is not None:
            mutate(native, active)
        (folder / 'input_config.json').write_text(json.dumps(cfg))
        deck, _ = render(cfg, key, plots=False)
        (folder / 'device.in').write_text('# SYNTHETIC UNIT FIXTURE; NOT AN ATLAS RUN\n' + deck)
        # Mock banners exercise recognition only. They never constitute real validation.
        # Explicit mock mesh counts distinguish spacing requests from realized meshes.
        n = cfg['numerics']
        points = int((100 / n['x_spacing_um'] + 10 / n['contact_edge_spacing_um'])
                     * (n['channel_intervals'] + n['alumina_intervals'] + n['hafnia_intervals']))
        (folder / 'deckbuild.out').write_text('SYNTHETIC UNIT TEST ONLY\nVersion: atlas 5.0\n'
            + f'Total grid points: {points}\nTotal triangles: {2*points}\nATLAS version 5.0 finished\n')
        for name in ['geometry.str', 'equilibrium.str', 'off.str', 'final.str']:
            (folder / name).write_text('SYNTHETIC UNIT TEST ONLY; NOT A STRUCTURE')
        if cfg['defects']['bulk']:
            for name in ['bulk_acceptor.dat', 'bulk_donor.dat']:
                (folder / name).write_text('SYNTHETIC UNIT TEST ONLY\n0 1\n')
        if cfg['defects']['interface']:
            for name in ['interface_acceptor.dat', 'interface_donor.dat', 'interface_dos.dat']:
                (folder / name).write_text('SYNTHETIC UNIT TEST ONLY\n0 1\n')
        log = ['SYNTHETIC UNIT TEST ONLY; NOT SIMULATION OUTPUT', 'f 3 "gate" "source" "drain"']
        log += ['o ' + str(index) + ' ' + name for index, name in enumerate(
            ('channel_mobility', 'channel_electrons') + extra, start=1)]
        log += ['p ' + str(native.shape[1]) + ' 2 601 20 3 602 21 4 603 22 '
                + ' '.join(str(3000+index) for index in range(2+len(extra)))]
        log += ['d ' + ' '.join(format(x, '.17g') for x in row) for row in native]
        (folder / 'transfer.log').write_text('\n'.join(log))
        for name, column in check.native_export_columns(cfg).items():
            (folder / name).write_text('SYNTHETIC UNIT TEST ONLY\n121 2 2\n' + '\n'.join(
                format(v, '.17g') + ' ' + format(i, '.17g') for v, i in zip(vg, native[:, column])))
        signed = native[:, 8] / width
        fields = ['vg_V', 'measured_A_per_um', 'atlas_signed_A_per_um', 'active', 'low_current',
                  'linear_residual_A_per_um', 'log10_magnitude_residual']
        with (folder / 'comparison_all_measurements.csv').open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow(fields)
            writer.writerows(zip(vg, measured, signed, active, ~active, signed-measured,
                                 np.log10(np.maximum(abs(signed), 1e-40) / measured)))
        (folder / 'execution.json').write_text(json.dumps(dict(
            run_id=folder.name, event='finish', returncode=0, actual_started_simulator_stages=['atlas'],
            fixture_notice='SYNTHETIC UNIT TEST ONLY; NOT A LICENSED SIMULATION')))
        self.rehash(folder)
        return folder

    def variants(self, cfg=None):
        cfg = copy.deepcopy(cfg or self.cfg)
        paths = {'reference': self.fixture(cfg)}
        for name in ('width', 'xmesh', 'ymesh', 'dos'):
            variant = copy.deepcopy(cfg)
            if name == 'width':
                variant['geometry']['simulation_width_um'] *= 2
            elif name == 'xmesh':
                variant['numerics']['x_spacing_um'] /= 2
                variant['numerics']['contact_edge_spacing_um'] /= 2
            elif name == 'ymesh':
                for key in ('channel_intervals', 'alumina_intervals', 'hafnia_intervals'):
                    variant['numerics'][key] *= 2
            else:
                for key in ('bulk_levels_a', 'bulk_levels_d', 'interface_levels_a', 'interface_levels_d'):
                    variant['defects'][key] *= 2
            paths[name] = self.fixture(variant)
        return paths

    def cli(self, paths, dos=False):
        # Each invocation preserves its earlier diagnostic/certificate result.
        index = len(list(self.base.glob('SYNTHETIC_UNIT_RESULT_*.json')))
        dest = self.base / f'SYNTHETIC_UNIT_RESULT_{index:03d}.json'
        argv = []
        for name in ('reference', 'width', 'xmesh', 'ymesh') + (('dos',) if dos else ()):
            argv += ['--' + name, str(paths[name])]
        with redirect_stdout(io.StringIO()), patch('subprocess.Popen', side_effect=AssertionError('No process allowed')):
            code = check.main(argv + ['--out', str(dest)])
        return code, check.read_json(dest)

    def test_all_four_original_series_and_native_probe_targets_are_verified(self):
        for key in check.DATA:
            with self.subTest(key=key):
                run = check.load_run(self.fixture(key=key))
                self.assertEqual(run['key'], key)
                self.assertEqual(run['summary']['gate_points'], 121)
                self.assertTrue(run['summary']['run_acceptable'])

    def test_complete_trap_free_gate_pass_has_explicit_dos_na(self):
        code, result = self.cli(self.variants())
        self.assertEqual(code, 0)
        self.assertTrue(result['all_required_checks_passed'])
        self.assertEqual(result['checks']['dos']['status'], 'N/A')
        self.assertFalse(result['calibration_eligible'])
        self.assertFalse(result['measurement_fit_validated'])

    def test_trap_enabled_requires_dos_then_passes_independent_doubling(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['defects'].update(bulk=True, interface=True)
        paths = self.variants(cfg)
        code, result = self.cli(paths)
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertEqual(result['checks']['dos']['status'], 'MISSING')
        code, result = self.cli(paths, dos=True)
        self.assertEqual(code, 0)
        self.assertEqual(result['checks']['dos']['status'], 'PASS')

    def test_tampered_execution_hashed_export_cannot_pass(self):
        folder = self.fixture()
        with (folder / 'idvg.dat').open('a') as handle:
            handle.write('\nCHANGED')
        with self.assertRaisesRegex(ValueError, 'changed'):
            check.load_run(folder)

    def test_recovered_bias_reduction_passes_only_complete_verified_run(self):
        folder = self.fixture()
        path = folder / 'deckbuild.out'
        path.write_text(path.read_text() + '\nWarning: Newton algorithm did not converge in 60 iterations.\n'
                        + 'Warning: Convergence problem.  Taking smaller bias\n')
        self.rehash(folder)
        run = check.load_run(folder)
        self.assertTrue(run['summary']['run_acceptable'])
        self.assertEqual(run['summary']['recovered_bias_reductions'], 1)
        self.assertEqual(len(run['summary']['raw_warning_lines']), 2)
        # The warning does not excuse an unachieved original target.
        path = folder / 'transfer.log'
        path.write_text('\n'.join(path.read_text().splitlines()[:-1]))
        self.rehash(folder)
        with self.assertRaisesRegex(ValueError, 'Missing original measurement'):
            check.load_run(folder)

    def test_exhausted_retries_never_count_as_recovered_steps(self):
        for failure in ('Cannot trap', 'Could not trap', 'Cannot reduce bias', 'Error # 1', 'fatal error'):
            with self.subTest(failure=failure):
                folder = self.fixture()
                path = folder / 'deckbuild.out'
                path.write_text(path.read_text() + '\nWarning: ' + failure + '\n')
                self.rehash(folder)
                with self.assertRaisesRegex(ValueError, 'failure'):
                    check.load_run(folder)

    def test_missing_required_hash_and_failed_execution_are_rejected(self):
        for field in ('missing_hash', 'failed_return', 'wrong_stage'):
            with self.subTest(field=field):
                folder = self.fixture()
                record = check.read_json(folder / 'execution.json')
                if field == 'missing_hash':
                    record['outputs'].pop('electrons_vg.dat')
                elif field == 'failed_return':
                    record['returncode'] = 1
                else:
                    record['actual_started_simulator_stages'] = ['athena', 'atlas']
                (folder / 'execution.json').write_text(json.dumps(record))
                with self.assertRaises(ValueError):
                    check.load_run(folder)

    def test_missing_native_or_export_bias_is_not_interpolated(self):
        for name in ('transfer.log', 'mobility_vg.dat'):
            with self.subTest(name=name):
                folder = self.fixture()
                path = folder / name
                lines = path.read_text().splitlines()
                prefix = 'd ' if name == 'transfer.log' else ''
                index = next(i for i, line in enumerate(lines) if line.startswith(prefix + '0.5 '))
                lines.pop(index)
                path.write_text('\n'.join(lines))
                self.rehash(folder)
                with self.assertRaisesRegex(ValueError, 'Missing original measurement'):
                    check.load_run(folder)

    def test_native_export_disagreement_rejected_even_with_new_hash(self):
        folder = self.fixture()
        path = folder / 'electrons_vg.dat'
        lines = path.read_text().splitlines()
        lines[-1] = '3 2e15'
        path.write_text('\n'.join(lines))
        self.rehash(folder)
        with self.assertRaisesRegex(ValueError, 'EXTRACT disagree'):
            check.load_run(folder)

    def test_untrusted_comparison_values_masks_and_residuals_recomputed(self):
        for field in ('measured_A_per_um', 'atlas_signed_A_per_um', 'active', 'linear_residual_A_per_um'):
            with self.subTest(field=field):
                folder = self.fixture()
                rows = check.table(folder / 'comparison_all_measurements.csv')
                rows[-1][field] = 'False' if field == 'active' else '1.2345'
                with (folder / 'comparison_all_measurements.csv').open('w', newline='') as handle:
                    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
                with self.assertRaises(ValueError):
                    check.load_run(folder)

    def test_native_kcl_is_checked_at_low_and_active_points(self):
        for index in (0, -1):
            with self.subTest(index=index):
                def mutate(native, active):
                    native[index, 5] = 0
                run = check.load_run(self.fixture(mutate=mutate))
                self.assertFalse(run['summary']['kcl_recomputed_pass'])
                self.assertFalse(run['summary']['run_acceptable'])

    def test_signed_drain_and_active_native_probe_failures_block_gate(self):
        for column in (8, 9, 10):
            with self.subTest(column=column):
                def mutate(native, active):
                    native[-1, column] = -abs(native[-1, column]) if column == 8 else 0
                    if column == 8:
                        native[-1, 5] = -native[-1, 8]
                run = check.load_run(self.fixture(mutate=mutate))
                self.assertFalse(run['summary']['run_acceptable'])

    def test_identical_discretization_and_hidden_physics_changes_rejected(self):
        ref = check.load_run(self.fixture())
        for kind in check.CONTROLS:
            with self.subTest(kind=kind):
                self.assertFalse(check.design_check(ref, ref, kind)['pass_check'])
        cfg = copy.deepcopy(self.cfg)
        cfg['geometry']['simulation_width_um'] *= 2
        cfg['curves']['2p0']['mu_band_cm2Vs'] *= 1.01
        candidate = check.load_run(self.fixture(cfg))
        self.assertFalse(check.design_check(ref, candidate, 'width')['pass_check'])

    def test_deck_config_disagreement_rejected_after_hashes_recomputed(self):
        folder = self.fixture()
        path = folder / 'device.in'
        path.write_text(path.read_text().replace('mesh width=1', 'mesh width=2'))
        self.rehash(folder)
        with self.assertRaisesRegex(ValueError, 'regeneration'):
            check.load_run(folder)

    def test_x_and_y_mesh_cannot_be_combined_into_one_check(self):
        ref = check.load_run(self.fixture())
        cfg = copy.deepcopy(self.cfg)
        cfg['numerics']['x_spacing_um'] /= 2
        cfg['numerics']['channel_intervals'] *= 2
        candidate = check.load_run(self.fixture(cfg))
        for kind in ('xmesh', 'ymesh'):
            self.assertFalse(check.design_check(ref, candidate, kind)['pass_check'])

    def test_contact_length_half_and_double_are_isolated_sensitivities(self):
        ref = check.load_run(self.fixture())
        for length in (1.0, 4.0):
            with self.subTest(length=length):
                cfg = copy.deepcopy(self.cfg)
                cfg['geometry']['contact_length_um'] = length
                candidate = check.load_run(self.fixture(cfg))
                result = check.compare(ref, candidate, 'contact_length')
                self.assertTrue(result['pass_check'])
                self.assertEqual(set(result['design']['changed_config']), {'geometry.contact_length_um'})
                self.assertTrue(result['design']['regenerated_contact_commands_match'])
                self.assertNotEqual(ref['deck'], candidate['deck'])

    def test_contact_length_rejects_changed_channel_length_or_gate_physics(self):
        ref = check.load_run(self.fixture())
        for field in ('channel_length', 'gate_shift'):
            with self.subTest(field=field):
                cfg = copy.deepcopy(self.cfg)
                cfg['geometry']['contact_length_um'] = 1
                if field == 'channel_length':
                    cfg['geometry']['channel_length_um'] = 19
                else:
                    cfg['curves']['2p0']['gate_shift_V'] += .1
                candidate = check.load_run(self.fixture(cfg))
                self.assertFalse(check.design_check(ref, candidate, 'contact_length')['pass_check'])

    def test_contact_length_cannot_hide_wrong_gate_command(self):
        ref = check.load_run(self.fixture())
        cfg = copy.deepcopy(self.cfg)
        cfg['geometry']['contact_length_um'] = 1
        candidate = check.load_run(self.fixture(cfg))
        candidate['deck'] = candidate['deck'].replace('solve vgate=3\n', 'solve vgate=2.9\n')
        result = check.design_check(ref, candidate, 'contact_length')
        self.assertFalse(result['pass_check'])
        self.assertFalse(result['regenerated_contact_commands_match'])

    def test_contact_length_uses_unchanged_current_tolerances(self):
        ref = check.load_run(self.fixture())
        cfg = copy.deepcopy(self.cfg)
        cfg['geometry']['contact_length_um'] = 1
        candidate = check.load_run(self.fixture(cfg))
        candidate['terminal']['id'][-1] *= 1.015
        candidate['terminal']['is'][-1] = -candidate['terminal']['id'][-1]
        result = check.compare(ref, candidate, 'contact_length')
        self.assertTrue(result['design']['pass_check'])
        self.assertLess(result['active_max_log10_difference_decades'], .01)
        self.assertFalse(result['pass_check'])  # Ion still must agree within 1%.

    def test_requested_refinement_with_identical_realized_mesh_is_rejected(self):
        paths = self.variants()
        ref = check.load_run(paths['reference'])
        for kind in ('xmesh', 'ymesh'):
            with self.subTest(kind=kind):
                candidate = check.load_run(paths[kind])
                candidate['summary']['realized_mesh'] = ref['summary']['realized_mesh'].copy()
                self.assertFalse(check.design_check(ref, candidate, kind)['pass_check'])

    def test_unverified_native_layout_or_nonfinite_probe_is_rejected(self):
        for failure in ('layout', 'nonfinite'):
            with self.subTest(failure=failure):
                folder = self.fixture()
                path = folder / 'transfer.log'
                text = path.read_text()
                if failure == 'layout':
                    text = text.replace('3000 3001', '3001 3000')
                else:
                    lines = text.splitlines()
                    words = lines[-1].split()
                    words[-1] = 'nan'
                    lines[-1] = ' '.join(words)
                    text = '\n'.join(lines)
                path.write_text(text)
                self.rehash(folder)
                with self.assertRaises(ValueError):
                    check.load_run(folder)

    def test_prpmob_native_schema_strictly_preserves_first_eleven_columns(self):
        folder = self.fixture()
        path = folder / 'transfer.log'
        target = np.linspace(-3, 3, 121)
        old, _ = check.native_log(path, target)
        lines = path.read_text().splitlines()
        at = next(i for i, line in enumerate(lines) if line.startswith('p '))
        lines[at:at+1] = ['o ' + str(index) + ' ' + name for index, name in enumerate(check.PRPMOB_EXTRA, start=3)] + [
            'p 16 2 601 20 3 602 21 4 603 22 3000 3001 3002 3003 3004 3005 3006']
        lines = [line + ' -100000 8 -200000 9 300000' if line.startswith('d ') else line for line in lines]
        path.write_text('\n'.join(lines))
        parsed, _ = check.native_log(path, target, check.PRPMOB_EXTRA)
        self.assertEqual(parsed.shape, (121, 16))
        np.testing.assert_array_equal(parsed[:, :11], old)
        self.assertTrue((parsed[:, 11] < 0).all())  # Electric fields remain signed.
        with self.assertRaisesRegex(ValueError, 'layout'):
            check.native_log(path, target)  # No silent extension of legacy schema.
        path.write_text(path.read_text().replace('o 4 front_mobility', 'o 4 back_mobility'))
        with self.assertRaisesRegex(ValueError, 'layout'):
            check.native_log(path, target, check.PRPMOB_EXTRA)

    def test_prpmob_extras_are_expected_only_for_prpmob_mode(self):
        cfg = copy.deepcopy(self.cfg)
        self.assertEqual(check.expected_extras(cfg), ())
        cfg['transport']['mode'] = 'prpmob'
        self.assertEqual(check.expected_extras(cfg), check.PRPMOB_EXTRA)
        with self.assertRaisesRegex(ValueError, 'Unsupported requested'):
            check.native_log(self.base / 'unused.log', np.linspace(-3, 3, 121), ('arbitrary_probe',))

    def test_trap_charge_probe_layout_with_and_without_prpmob(self):
        for mode in ('constant', 'prpmob'):
            with self.subTest(mode=mode):
                cfg = copy.deepcopy(self.cfg)
                cfg['transport'].update(mode=mode, critical_field_V_cm=1e6)
                cfg['diagnostics'] = {'trap_charge': True}
                folder = self.fixture(cfg)
                run = check.load_run(folder)
                self.assertTrue(run['summary']['run_acceptable'])
                names = check.expected_extras(cfg)
                self.assertEqual(names[-3:], check.TRAP_CHARGE_EXTRA)
                native, _ = check.native_log(folder / 'transfer.log', run['vg'], names)
                self.assertEqual(native.shape[1], 19 if mode == 'prpmob' else 14)
                self.assertTrue((native[:, -1] == 0).all())
                self.assertTrue((native[:, -2] == 0).all())
                self.assertNotIn('bulk_ionized_donors', run['summary']['native_probes'])
                # Explicit finite-only trap diagnostics must not fail for inactive zero populations.
                self.assertEqual(run['summary']['native_extra_probes']['bulk_ionized_donors']['minimum'], 0)
                with self.assertRaisesRegex(ValueError, 'layout'):
                    check.native_log(folder / 'transfer.log', run['vg'],
                                     check.PRPMOB_EXTRA if mode == 'prpmob' else ())

    def test_trap_charge_exports_are_required_and_crosschecked(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['diagnostics'] = {'trap_charge': True}
        for failure in ('missing_manifest', 'changed_native_export'):
            with self.subTest(failure=failure):
                folder = self.fixture(cfg)
                if failure == 'missing_manifest':
                    record = check.read_json(folder / 'execution.json')
                    record['outputs'].pop('bulk_free_electrons_vg.dat')
                    (folder / 'execution.json').write_text(json.dumps(record))
                else:
                    path = folder / 'bulk_ionized_donors_vg.dat'
                    lines = path.read_text().splitlines()
                    lines[-1] = '3 1e15'
                    path.write_text('\n'.join(lines))
                    self.rehash(folder)
                with self.assertRaises(ValueError):
                    check.load_run(folder)

    def test_all_optional_probe_combinations_preserve_strict_order_and_legacy(self):
        signatures = set()
        for mode in ('constant', 'prpmob'):
            for traps in (False, True):
                for depth in (False, True):
                    with self.subTest(mode=mode, traps=traps, depth=depth):
                        cfg = copy.deepcopy(self.cfg)
                        cfg['transport'].update(mode=mode, critical_field_V_cm=1e6)
                        cfg['diagnostics'] = {'trap_charge': traps, 'depth_electrons': depth}
                        expected = ((check.PRPMOB_EXTRA if mode == 'prpmob' else ())
                                    + (check.TRAP_CHARGE_EXTRA if traps else ())
                                    + (check.DEPTH_ELECTRON_EXTRA if depth else ()))
                        self.assertEqual(check.expected_extras(cfg), expected)
                        signatures.add(expected)
                        folder = self.fixture(cfg)
                        run = check.load_run(folder)
                        native, _ = check.native_log(folder / 'transfer.log', run['vg'], expected)
                        self.assertEqual(native.shape, (121, 11 + len(expected)))
                        self.assertTrue(run['summary']['run_acceptable'])
                        if depth:
                            self.assertEqual(expected[-2:], check.DEPTH_ELECTRON_EXTRA)
                            self.assertTrue((native[:, -2:] == 0).all())
        self.assertEqual(signatures, set(check.ALLOWED_EXTRA_SCHEMAS))
        self.assertEqual(len(signatures), 8)

    def test_depth_probe_missing_renamed_and_wrong_order_are_rejected(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['diagnostics'] = {'depth_electrons': True}
        for failure in ('missing', 'renamed', 'reordered'):
            with self.subTest(failure=failure):
                folder = self.fixture(cfg)
                path = folder / 'transfer.log'
                text = path.read_text()
                if failure == 'missing':
                    text = '\n'.join(s for s in text.splitlines() if s != 'o 4 bulk_back_electrons')
                elif failure == 'renamed':
                    text = text.replace('bulk_front_electrons', 'bulk_front_density')
                else:
                    text = text.replace('o 3 bulk_front_electrons', 'o 3 bulk_back_electrons').replace(
                        'o 4 bulk_back_electrons', 'o 4 bulk_front_electrons')
                path.write_text(text)
                self.rehash(folder)
                with self.assertRaisesRegex(ValueError, 'layout'):
                    check.load_run(folder)

    def test_negative_depth_density_rejected_even_at_off_bias(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['diagnostics'] = {'depth_electrons': True}
        for column in (11, 12):
            with self.subTest(column=column):
                def mutate(native, active):
                    native[0, column] = -1e-30
                with self.assertRaisesRegex(ValueError, 'Negative native depth electron'):
                    check.load_run(self.fixture(cfg, mutate=mutate))

    def test_depth_probe_requires_hash_manifest_and_boolean_flag(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['diagnostics'] = {'depth_electrons': True}
        folder = self.fixture(cfg)
        record = check.read_json(folder / 'execution.json')
        record['outputs'].pop('bulk_back_electrons_vg.dat')
        (folder / 'execution.json').write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'missing from execution'):
            check.load_run(folder)
        cfg['diagnostics']['depth_electrons'] = 'true'
        with self.assertRaisesRegex(ValueError, 'must be a boolean'):
            check.expected_extras(cfg)

    def test_contact_resistance_requires_verified_internal_voltages(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['contacts']['resistance_ohm_um'] = 1e5
        folder = self.fixture(cfg)
        self.assertTrue(check.load_run(folder)['summary']['run_acceptable'])
        self.assertEqual(check.native_export_columns(cfg)['source_internal_vg.dat'], 4)
        self.assertEqual(check.native_export_columns(cfg)['drain_internal_vg.dat'], 7)
        path = folder / 'drain_internal_vg.dat'
        lines = path.read_text().splitlines()
        lines[-1] = '3 0.7'  # External voltage is not the internal contact voltage.
        path.write_text('\n'.join(lines))
        self.rehash(folder)
        with self.assertRaisesRegex(ValueError, 'EXTRACT disagree'):
            check.load_run(folder)

    def test_dos_doubling_must_cover_every_enabled_population(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['defects'].update(bulk=True, interface=True)
        ref = check.load_run(self.fixture(cfg))
        cfg['defects']['bulk_levels_a'] *= 2
        cfg['defects']['interface_levels_a'] *= 2
        candidate = check.load_run(self.fixture(cfg))
        self.assertFalse(check.design_check(ref, candidate, 'dos')['pass_check'])

    def test_low_signed_limit_uses_sum_of_both_magnitudes(self):
        paths = self.variants()
        ref, candidate = check.load_run(paths['reference']), check.load_run(paths['width'])
        for run, value in ((ref, 1e-14), (candidate, 1.018e-14)):
            run['terminal']['id'][0] = value
            run['terminal']['is'][0] = -value
        self.assertTrue(check.compare(ref, candidate, 'width')['pass_check'])
        candidate['terminal']['id'][0] = 1.03e-14
        candidate['terminal']['is'][0] = -1.03e-14
        self.assertFalse(check.compare(ref, candidate, 'width')['pass_check'])

    def test_active_log_and_ion_bounds_are_both_required(self):
        paths = self.variants()
        ref = check.load_run(paths['reference'])
        candidate = check.load_run(paths['width'])
        candidate['terminal']['id'][-1] *= 1.015
        result = check.compare(ref, candidate, 'width')
        self.assertLess(result['active_max_log10_difference_decades'], .01)
        self.assertFalse(result['pass_check'])
        candidate = check.load_run(paths['width'])
        candidate['terminal']['id'][-2] *= 1.03
        result = check.compare(ref, candidate, 'width')
        self.assertEqual(result['ion_relative_difference'], 0)
        self.assertFalse(result['pass_check'])

    def test_failed_reference_prevents_cli_pass_and_raw_files_unchanged(self):
        paths = self.variants()
        paths['reference'] = self.fixture(mutate=lambda native, active: native.__setitem__((-1, 9), 0))
        before = {str(p): check.sha(p) for folder in paths.values() for p in folder.iterdir() if p.is_file()}
        code, result = self.cli(paths)
        after = {str(p): check.sha(p) for folder in paths.values() for p in folder.iterdir() if p.is_file()}
        self.assertEqual(code, 2)
        self.assertFalse(result['all_required_checks_passed'])
        self.assertEqual(before, after)

    def test_cli_output_cannot_overwrite_raw_evidence_or_leave_project(self):
        paths = self.variants()
        argv = []
        for name in ('reference', 'width', 'xmesh', 'ymesh'):
            argv += ['--' + name, str(paths[name])]
        for out in (paths['reference'] / 'execution.json', check.ROOT.parent / 'outside.json'):
            with self.subTest(out=out), redirect_stdout(io.StringIO()), patch('sys.stderr', io.StringIO()):
                with self.assertRaises(SystemExit):
                    check.main(argv + ['--out', str(out)])


if __name__ == '__main__':
    unittest.main()
