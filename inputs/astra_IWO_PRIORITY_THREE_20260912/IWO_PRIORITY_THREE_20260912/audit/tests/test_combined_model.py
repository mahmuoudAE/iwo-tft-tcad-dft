"""Combined-deck and budget regressions. No real simulator is ever launched.

All process tests replace subprocess.Popen. Their temporary records are marked
UNIT_TEST_ONLY and live below project/tmp, separate from the actual run budget.
Passing these tests establishes generation/guard behavior, not ATLAS physics.
"""
import copy
import hashlib
import json
import re
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import combined_model
import local_probe
from iwo_model import load_config


def commands(text):
    """Join deck continuations and remove explanatory comments for assertions."""
    active = [line.strip() for line in text.splitlines()
              if line.strip() and not line.lstrip().startswith('#')]
    return re.sub(r'\\\s*\n\s*', ' ', '\n'.join(active)).splitlines()


def value(command, key):
    match = re.search(r'(?:^|\s)' + re.escape(key) + r'=([^\s]+)', command)
    if not match:
        raise AssertionError(f'Missing {key} in {command}')
    return match.group(1).strip('"')


class CombinedGenerationTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config(ROOT / 'config/combined_model.json')

    def each_render(self, *, probe=False, plots=False):
        for config_name in ('combined_model.json', 'combined_constant.json'):
            cfg = load_config(ROOT / 'config' / config_name)
            for key in ('2p0', '6p3', '13p2', '31p8'):
                yield config_name, key, cfg, combined_model.render(cfg, key, probe, plots)

    def test_two_engines_in_order_and_only_final_quit(self):
        for name, key, _, (text, _, _) in self.each_render():
            with self.subTest(config=name, thickness=key):
                cards = commands(text)
                engines = [c.split()[1].lower() for c in cards if c.lower().startswith('go ')]
                self.assertEqual(engines, ['athena', 'atlas'])
                self.assertEqual([i for i, c in enumerate(cards) if c.lower() == 'quit'],
                                 [len(cards) - 1])

    def test_atlas_reads_only_structure_produced_in_same_deck(self):
        for name, key, cfg, _ in self.each_render():
            with self.subTest(config=name, thickness=key):
                cfg['athena_structure_path'] = 'DOES_NOT_EXIST_UNIT_TEST/stale.str'
                original = copy.deepcopy(cfg)
                text, meta, effective = combined_model.render(cfg, key)
                cards = commands(text)
                atlas_index = next(i for i, c in enumerate(cards) if c.lower().startswith('go atlas'))
                written = {value(c, 'outfile') for c in cards[:atlas_index]
                           if c.startswith('structure ')}
                meshes = [value(c, 'infile') for c in cards[atlas_index:] if c.startswith('mesh ')]
                expected = f'iwo_{key}nm_athena_device.str'
                self.assertEqual(meshes, [expected])
                self.assertIn(expected, written)
                self.assertEqual(Path(expected).name, expected)
                self.assertNotIn('source_athena.str', text)
                self.assertNotIn('stale.str', text)
                self.assertFalse(meta['external_input_mesh_required'])
                self.assertEqual(effective['athena_structure_path'], expected)
                self.assertEqual(cfg, original, 'Rendering must not mutate caller configuration')

    def test_full_logged_grid_matches_all_121_original_measurements(self):
        for name, key, cfg, (text, meta, _) in self.each_render():
            with self.subTest(config=name, thickness=key):
                cards = commands(text)
                start = cards.index('log outf=transfer.log') + 1
                stop = cards.index('log off', start)
                logged = [float(value(c, 'vgate')) for c in cards[start:stop]
                          if c.startswith('solve ')]
                measured = np.genfromtxt(ROOT / cfg['curves'][key]['data'],
                                         delimiter=',', names=True)['vg_V']
                self.assertEqual(len(logged), 121)
                np.testing.assert_allclose(logged, measured, rtol=0, atol=1e-9)
                np.testing.assert_allclose(meta['requested_gate_points'], logged, rtol=0, atol=1e-9)
                self.assertEqual((logged[0], logged[-1]), (-3, 3))

    def test_probe_grid_is_25_points_and_is_not_full_grid(self):
        for name, key, _, (text, meta, _) in self.each_render(probe=True):
            with self.subTest(config=name, thickness=key):
                cards = commands(text)
                start = cards.index('log outf=transfer.log') + 1
                stop = cards.index('log off', start)
                logged = [float(value(c, 'vgate')) for c in cards[start:stop]
                          if c.startswith('solve ')]
                self.assertEqual(len(logged), 25)
                np.testing.assert_allclose(logged, np.linspace(-3, 3, 25), rtol=0, atol=1e-12)
                self.assertEqual(meta['requested_gate_points'], logged)
                self.assertTrue(meta['probe'])
                self.assertIn('not the full measured grid', text)

    def test_imported_interface_and_probes_track_all_four_actual_films(self):
        for name, key, cfg, (text, _, _) in self.each_render():
            with self.subTest(config=name, thickness=key):
                cards = commands(text)
                film = next(c for c in cards if c.startswith('deposit material=IWO '))
                thickness = float(value(film, 'thick'))
                self.assertAlmostEqual(thickness, cfg['curves'][key]['thickness_nm'] / 1000)
                boundary = -sum(cfg['geometry'][k] for k in
                                ('gate_metal_nm', 'hfo2_nm', 'al2o3_nm')) / 1000
                interface = next(c for c in cards if c.startswith('intdefects '))
                self.assertEqual(value(interface, 'intnumber'), '5/4')
                self.assertIn('max.gaussian', interface)
                self.assertAlmostEqual(float(value(interface, 'y.min')), boundary - 1e-6)
                self.assertAlmostEqual(float(value(interface, 'y.max')), boundary + 1e-6)
                for probe_name, quantity in [('channel_mobility', 'n.mob'),
                                             ('channel_electrons', 'n.conc')]:
                    probe = next(c for c in cards if c.startswith(f'probe name={probe_name} '))
                    y = float(value(probe, 'y'))
                    self.assertEqual(float(value(probe, 'x')), 12)
                    self.assertAlmostEqual(y, boundary - thickness / 2)
                    self.assertLess(boundary - thickness, y)
                    self.assertLess(y, boundary)
                    self.assertIn(quantity, probe.split())
                self.assertIn('dir=0', next(c for c in cards if c.startswith('probe name=channel_mobility ')))

    def test_plots_cover_every_written_structure_and_log_after_both_engines(self):
        for name, key, _, (text, _, _) in self.each_render(plots=True):
            with self.subTest(config=name, thickness=key):
                cards = commands(text)
                produced = set()
                for card in cards:
                    if card.startswith('structure '):
                        produced.add(value(card, 'outfile'))
                    elif card.startswith('save ') or card.startswith('log outf='):
                        produced.add(value(card, 'outf'))
                plot_names = [c.split()[1] for c in cards if c.startswith('tonyplot ')]
                self.assertEqual(set(plot_names), produced)
                self.assertEqual(len(plot_names), len(produced))
                atlas_index = next(i for i, c in enumerate(cards) if c.startswith('go atlas'))
                self.assertTrue(all(i > atlas_index for i, c in enumerate(cards) if c.startswith('tonyplot ')))
                self.assertEqual(cards[-1], 'quit')

    def test_batch_deck_has_no_interactive_plot_calls(self):
        text, _, _ = combined_model.render(self.cfg, plots=False)
        self.assertFalse(any(c.startswith('tonyplot ') for c in commands(text)))

    def test_schottky_comparison_preserves_physics_and_explicit_injection(self):
        cfg = load_config(ROOT / 'config/combined_schottky.json')
        text, meta, effective = combined_model.render(cfg)
        cards = commands(text)
        expected_workfunction = cfg['shared']['affinity_eV'] + cfg['contacts']['effective_electron_barrier_eV']
        for name in ('source', 'drain'):
            card = next(c for c in cards if c.startswith(f'contact name={name} '))
            self.assertAlmostEqual(float(value(card, 'workfunction')), expected_workfunction)
            self.assertIn('surf.rec', card.split())
        self.assertEqual(effective['contacts']['mode'], 'schottky')
        self.assertEqual(meta['effective_contact_barrier_eV'], 0.15)

    def test_mesh_changes_only_athena_lateral_grid(self):
        base = load_config(ROOT / 'config/combined_schottky.json')
        refined = load_config(ROOT / 'config/combined_mesh.json')
        a, _, _ = combined_model.render(base)
        b, meta, _ = combined_model.render(refined)
        aa, bb = commands(a), commands(b)
        self.assertEqual([c for c in aa if not c.startswith('line x ')],
                         [c for c in bb if not c.startswith('line x ')])
        self.assertNotEqual([c for c in aa if c.startswith('line x ')],
                            [c for c in bb if c.startswith('line x ')])
        self.assertEqual(meta['process_mesh']['mode'], 'lateral_refined')

    def test_changed_thickness_cannot_silently_use_fixed_process_template(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['curves']['2p0']['thickness_nm'] = 3.0
        with self.assertRaisesRegex(ValueError, r'(?i)(thick|process|template)'):
            combined_model.render(cfg, '2p0')

    def test_intermediate_quit_in_process_is_rejected(self):
        process_path = ROOT / 'decks_paper_revision/athena/iwo_2p0nm_process.in'
        original_read = Path.read_text
        for quit_card in ('quit', 'QUIT', '   quit', 'Quit # normal deck comment'):
            with self.subTest(quit_card=quit_card):
                def mutated_read(path, *args, **kwargs):
                    text = original_read(path, *args, **kwargs)
                    return text.replace('go athena', 'go athena\n' + quit_card, 1) if path == process_path else text

                with patch.object(Path, 'read_text', mutated_read):
                    with self.assertRaisesRegex(ValueError, 'Intermediate quit'):
                        combined_model.render(self.cfg, '2p0')


class CombinedBudgetGuardTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'tmp').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix='combined_guard_UNIT_TEST_ONLY_', dir=ROOT / 'tmp')
        self.fixture = Path(self.tmp.name).resolve()
        self.assertTrue(self.fixture.is_relative_to((ROOT / 'tmp').resolve()))
        self.base = self.fixture / 'isolated_run_records'
        self.base.mkdir()
        self.budget_file = self.base / 'session_budget.json'
        self.index = self.base / 'run_index.jsonl'
        self.real_budget = ROOT / 'results/local_session_20260910/session_budget.json'
        self.real_before = hashlib.sha256(self.real_budget.read_bytes()).hexdigest()
        self.cfg = {'curves': {}, 'unit_test_fixture_only': True}
        self.deck = '# UNIT_TEST_ONLY: no device physics and no simulator execution\ngo athena\ngo atlas\nquit\n'
        self.root_patch = patch.object(local_probe, 'ROOT', self.fixture)
        self.base_patch = patch.object(local_probe, 'BASE', self.base)
        self.root_patch.start()
        self.base_patch.start()

    def tearDown(self):
        self.base_patch.stop()
        self.root_patch.stop()
        self.assertEqual(hashlib.sha256(self.real_budget.read_bytes()).hexdigest(), self.real_before,
                         'Unit tests must never alter the actual session budget')
        self.assertTrue(self.fixture.is_relative_to((ROOT / 'tmp').resolve()))
        self.tmp.cleanup()

    def budget(self, maximum, deadline=None):
        deadline = deadline or (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        self.budget_file.write_text(json.dumps({'maximum_launches': maximum,
                                               'deadline_utc': deadline,
                                               'unit_test_fixture_only': True}))

    def seed_starts(self):
        # A historical start without the new field counts one; a combined start counts two.
        events = [{'event': 'start', 'run_id': 'UNIT_TEST_ONLY_legacy'},
                  {'event': 'start', 'run_id': 'UNIT_TEST_ONLY_combined', 'reserved_simulator_launches': 2},
                  {'event': 'finish', 'run_id': 'UNIT_TEST_ONLY_combined', 'reserved_simulator_launches': 2}]
        self.index.write_text(''.join(json.dumps(e) + '\n' for e in events))

    def invoke(self):
        return local_probe._run(['UNIT_TEST_ONLY_NEVER_EXECUTABLE', '{deck}', '{stdout}'],
                                self.deck, 'UNIT_TEST_ONLY', timeout=60, config=self.cfg, verbose=False)

    def test_two_stage_cost_rejects_one_remaining_launch_before_popen(self):
        self.budget(4)
        self.seed_starts()
        before = self.index.read_bytes()
        with patch.object(local_probe.subprocess, 'Popen') as launch:
            with self.assertRaisesRegex(RuntimeError, 'insufficient for 2 simulator stages'):
                self.invoke()
            launch.assert_not_called()
        self.assertEqual(self.index.read_bytes(), before)
        self.assertFalse((self.base / 'runs').exists())

    def test_two_stage_reservation_is_durable_before_mock_popen(self):
        self.budget(5)
        self.seed_starts()
        fake = Mock(pid=999999999)
        fake.wait.return_value = 0

        def assert_reserved(*args, **kwargs):
            starts = [json.loads(line) for line in self.index.read_text().splitlines()
                      if json.loads(line)['event'] == 'start']
            self.assertEqual(starts[-1]['reserved_simulator_launches'], 2)
            self.assertEqual(starts[-1]['declared_simulators'], ['athena', 'atlas'])
            self.assertEqual(sum(e.get('reserved_simulator_launches', 1) for e in starts), 5)
            self.assertTrue(Path(kwargs['cwd']).resolve().is_relative_to(self.fixture))
            return fake

        with patch.object(local_probe.subprocess, 'Popen', side_effect=assert_reserved) as launch, \
             patch.object(local_probe, 'wait_owned_tree', return_value=dict(
                 returncode=0, status='PROCESS_EXITED_NOT_YET_VALIDATED',
                 lifecycle={'unit_test_fixture_only': True})):
            dest = self.invoke()
            launch.assert_called_once()
        execution = json.loads((dest / 'execution.json').read_text())
        self.assertEqual(execution['reserved_simulator_launches'], 2)
        self.assertEqual(execution['actual_started_simulator_stages'], [])
        self.assertFalse((dest / 'deckbuild.out').exists(), 'Mock must not fabricate simulator output')

    def test_expired_copy_of_real_budget_blocks_before_popen(self):
        # Exercise the actual deadline parser against a COPY, without resetting or spending the live budget.
        copied_budget = json.loads(self.real_budget.read_text())
        copied_budget['unit_test_fixture_only'] = True
        self.budget_file.write_text(json.dumps(copied_budget))
        after_deadline = datetime.fromisoformat(copied_budget['deadline_utc']).timestamp() + 1
        with patch.object(local_probe.time, 'time', return_value=after_deadline):
            with patch.object(local_probe.subprocess, 'Popen') as launch:
                with self.assertRaisesRegex(RuntimeError, 'wall-time budget exhausted'):
                    self.invoke()
                launch.assert_not_called()
        self.assertFalse(self.index.exists())
        self.assertFalse((self.base / 'runs').exists())

    def test_preparation_uses_remaining_global_budget_without_a_new_launch(self):
        self.budget(5)
        with patch.object(local_probe, 'remaining_budget_seconds', side_effect=[60., -1.]), \
             patch.object(local_probe.subprocess, 'Popen') as launch:
            with self.assertRaisesRegex(RuntimeError, 'expired during preparation'):
                self.invoke()
            launch.assert_not_called()
        self.assertFalse(self.index.exists())
        self.assertFalse((self.fixture / 'tmp/atlas_owned_process_pending.json').exists())

    def test_prelaunch_deadline_is_fresh_and_not_extended_by_preparation(self):
        self.budget(5)
        fake = Mock(pid=999999999)
        with patch.object(local_probe, 'remaining_budget_seconds', side_effect=[60., 3.]), \
             patch.object(local_probe.time, 'monotonic', return_value=100.), \
             patch.object(local_probe.subprocess, 'Popen', return_value=fake) as launch, \
             patch.object(local_probe, 'wait_owned_tree', return_value=dict(returncode=0,
                 status='PROCESS_EXITED_NOT_YET_VALIDATED', lifecycle={'unit_test_fixture_only': True})) as wait:
            dest = self.invoke()
        launch.assert_called_once()
        self.assertEqual(wait.call_args.args[2], 103.)
        self.assertEqual(json.loads((dest / 'execution.json').read_text())['timeout_seconds'], 3.)

    def test_deadline_expiring_during_prelaunch_bookkeeping_never_calls_popen(self):
        self.budget(5)
        with patch.object(local_probe, 'remaining_budget_seconds', side_effect=[60., 3.]), \
             patch.object(local_probe.time, 'monotonic', side_effect=[100., 104., 104.]), \
             patch.object(local_probe.subprocess, 'Popen') as launch, \
             patch.object(local_probe, 'wait_owned_tree') as wait:
            dest = self.invoke()
        launch.assert_not_called(); wait.assert_not_called()
        record = json.loads((dest / 'execution.json').read_text())
        self.assertEqual(record['status'], 'BUDGET_EXPIRED_BEFORE_LAUNCH')
        self.assertIsNone(record['returncode'])
        self.assertFalse((self.fixture / 'tmp/atlas_owned_process_pending.json').exists())

    def test_spawn_index_write_error_still_waits_for_owned_lifecycle(self):
        self.budget(5)
        original_open = Path.open
        index_appends = 0
        def controlled_open(path, mode='r', *args, **kwargs):
            nonlocal index_appends
            if path == self.index and mode == 'a':
                index_appends += 1
                if index_appends == 2:
                    raise OSError('UNIT_TEST_SPAWN_INDEX_WRITE_FAILURE')
            return original_open(path, mode, *args, **kwargs)
        def launched(*args, **kwargs):
            guard = self.fixture / 'tmp/atlas_owned_process_pending.json'
            self.assertTrue(json.loads(guard.read_text())['unobserved_children_possible'])
            return Mock(pid=999999999)
        with patch.object(Path, 'open', controlled_open), \
             patch.object(local_probe.subprocess, 'Popen', side_effect=launched), \
             patch.object(local_probe, 'wait_owned_tree', return_value=dict(returncode=0,
                 status='PROCESS_EXITED_NOT_YET_VALIDATED', lifecycle={'unit_test_fixture_only': True})) as wait:
            dest = self.invoke()
        wait.assert_called_once()
        record = json.loads((dest / 'execution.json').read_text())
        self.assertEqual(record['status'], 'POST_LAUNCH_BOOKKEEPING_FAILED')
        self.assertIsNone(record['returncode'])
        self.assertIn('UNIT_TEST_SPAWN_INDEX_WRITE_FAILURE', record['process_lifecycle']['bookkeeping_error'])


if __name__ == '__main__':
    unittest.main()
