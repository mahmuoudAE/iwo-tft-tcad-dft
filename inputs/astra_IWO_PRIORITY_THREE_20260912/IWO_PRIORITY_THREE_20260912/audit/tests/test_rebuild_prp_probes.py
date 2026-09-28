"""Diagnostic-location regression checks only; never launches a simulator."""
import copy
from pathlib import Path
import shlex
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from rebuild_model import load, render
from rebuild_check import commands, expected_extras


def probes(deck):
    result = {}
    for line in commands(deck):
        words = shlex.split(line)
        if words[0] == 'probe':
            parameters = dict(word.split('=', 1) for word in words[1:] if '=' in word)
            result[parameters['name']] = (parameters, tuple(word for word in words[1:] if '=' not in word))
    return result


class RebuildPrpProbeTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load(ROOT / 'config/rebuild_seed.json')
        self.cfg['transport'].update(mode='prpmob', critical_field_V_cm=1e6)
        self.cfg['diagnostics'] = dict(trap_charge=True, depth_electrons=True)
        guard = patch('subprocess.Popen', side_effect=AssertionError('Probe tests must not launch a process'))
        guard.start()
        self.addCleanup(guard.stop)

    def test_enabled_31nm_points_match_native_density_locations_and_keep_centre(self):
        self.cfg['diagnostics']['colocate_prp_probes'] = True
        deck, meta = render(self.cfg, '31p8')
        locations = probes(deck)
        for names, y in [
            (('front_mobility', 'front_ey', 'bulk_front_electrons'), -.001),
            (('back_mobility', 'back_ey', 'bulk_back_electrons'), -.0308),
            (('channel_mobility', 'channel_ey', 'channel_electrons'), -.014946),
        ]:
            for name in names:
                with self.subTest(name=name):
                    parameters = locations[name][0]
                    self.assertAlmostEqual(float(parameters['x']), 12.037, places=12)
                    self.assertAlmostEqual(float(parameters['y']), y, places=12)
                    self.assertTrue(-.0318 < float(parameters['y']) < 0)
        self.assertEqual(meta['probe_xy_um'], [12.037, -.0318*.47])
        for name, y in [('front', -.001), ('middle', -.014946), ('back', -.0308)]:
            point = meta['colocated_prp_probe_xy_um'][name]
            self.assertAlmostEqual(point[0], 12.037, places=12)
            self.assertAlmostEqual(point[1], y, places=12)
        for name in ('channel_mobility', 'front_mobility', 'back_mobility'):
            self.assertEqual(locations[name][0]['dir'], '0')
            self.assertIn('n.mob', locations[name][1])
        for name in ('channel_ey', 'front_ey', 'back_ey'):
            self.assertEqual(locations[name][0]['dir'], '90')
            self.assertIn('field', locations[name][1])

    def test_enabled_points_stay_inside_every_supported_film(self):
        self.cfg['diagnostics']['colocate_prp_probes'] = True
        expected = {
            '2p0': (-.00026, -.00174),
            '6p3': (-.000819, -.005481),
            '13p2': (-.001, -.0122),
            '31p8': (-.001, -.0308),
        }
        for key, (front_y, back_y) in expected.items():
            with self.subTest(key=key):
                locations = probes(render(self.cfg, key)[0])
                for prefix, y in [('front', front_y), ('back', back_y)]:
                    for name in (prefix+'_mobility', prefix+'_ey', 'bulk_'+prefix+'_electrons'):
                        self.assertAlmostEqual(float(locations[name][0]['y']), y, places=12)

    def test_omitted_and_false_flags_preserve_legacy_prp_probe_positions(self):
        omitted, omitted_meta = render(self.cfg, '31p8')
        self.cfg['diagnostics']['colocate_prp_probes'] = False
        disabled, disabled_meta = render(self.cfg, '31p8')
        self.assertEqual(omitted, disabled)
        self.assertEqual(omitted_meta, disabled_meta)
        self.assertNotIn('colocated_prp_probe_xy_um', omitted_meta)
        locations = probes(omitted)
        for name, y in [('front_mobility', -.004134), ('front_ey', -.004134),
                        ('back_mobility', -.026394), ('back_ey', -.026394),
                        ('bulk_front_electrons', -.001), ('bulk_back_electrons', -.0308)]:
            self.assertAlmostEqual(float(locations[name][0]['y']), y, places=12)

    def test_enabled_option_changes_only_four_probe_commands_not_physics_or_schema(self):
        default, default_meta = render(self.cfg, '31p8')
        default_schema = expected_extras(self.cfg)
        enabled_cfg = copy.deepcopy(self.cfg)
        enabled_cfg['diagnostics']['colocate_prp_probes'] = True
        enabled, enabled_meta = render(enabled_cfg, '31p8')
        before, after = commands(default), commands(enabled)
        self.assertEqual(len(before), len(after))
        changed = [(a, b) for a, b in zip(before, after) if a != b]
        self.assertEqual(len(changed), 4)
        expected_names = {'front_mobility', 'front_ey', 'back_mobility', 'back_ey'}
        actual_names = set()
        for old, new in changed:
            old_probe, new_probe = probes(old), probes(new)
            self.assertEqual(set(old_probe), set(new_probe))
            name = next(iter(old_probe))
            actual_names.add(name)
            old_parameters, old_selectors = old_probe[name]
            new_parameters, new_selectors = new_probe[name]
            self.assertEqual(old_selectors, new_selectors)
            self.assertEqual({k:v for k,v in old_parameters.items() if k != 'y'},
                             {k:v for k,v in new_parameters.items() if k != 'y'})
        self.assertEqual(actual_names, expected_names)
        self.assertEqual([line for line in before if not line.startswith('probe ')],
                         [line for line in after if not line.startswith('probe ')])
        self.assertEqual(expected_extras(enabled_cfg), default_schema)
        self.assertEqual(default_meta['extra_probe_names'], enabled_meta['extra_probe_names'])

    def test_flag_must_be_an_actual_boolean(self):
        for value in (None, 0, 1, 0.0, 1.0, 'true', 'false', [], {}):
            with self.subTest(value=value):
                cfg = copy.deepcopy(self.cfg)
                cfg['diagnostics']['colocate_prp_probes'] = value
                with self.assertRaisesRegex(ValueError, 'colocate_prp_probes'):
                    render(cfg, '31p8')

    def test_enabled_option_requires_prpmob_and_enabled_depth_electrons(self):
        for mode in ('constant', 'tokyo'):
            with self.subTest(mode=mode):
                cfg = copy.deepcopy(self.cfg)
                cfg['transport']['mode'] = mode
                cfg['diagnostics']['colocate_prp_probes'] = True
                with self.assertRaises(ValueError):
                    render(cfg, '31p8')
        for value in (False, None, 'true'):
            with self.subTest(depth_electrons=value):
                cfg = copy.deepcopy(self.cfg)
                cfg['diagnostics'].update(colocate_prp_probes=True, depth_electrons=value)
                with self.assertRaises(ValueError):
                    render(cfg, '31p8')
        cfg = copy.deepcopy(self.cfg)
        del cfg['diagnostics']['depth_electrons']
        cfg['diagnostics']['colocate_prp_probes'] = True
        with self.assertRaises(ValueError):
            render(cfg, '31p8')

    def test_false_option_does_not_require_or_enable_prpmob_or_depth_probes(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['transport']['mode'] = 'constant'
        cfg['diagnostics'] = dict(trap_charge=False, depth_electrons=False)
        old, _ = render(cfg, '31p8')
        cfg['diagnostics']['colocate_prp_probes'] = False
        new, _ = render(cfg, '31p8')
        self.assertEqual(old, new)
        self.assertEqual(set(probes(new)), {'channel_mobility', 'channel_electrons'})


if __name__ == '__main__':
    unittest.main()
