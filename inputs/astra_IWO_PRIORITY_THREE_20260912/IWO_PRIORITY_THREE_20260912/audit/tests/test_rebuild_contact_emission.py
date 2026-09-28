"""Check isolated contact-emission rendering; never launches Silvaco."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from rebuild_model import load, render
from rebuild_check import commands


class ContactEmissionTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load(ROOT / 'config/rebuild_fit_bulk_width04.json')
        guard = patch('subprocess.Popen', side_effect=AssertionError('No engines in software checks'))
        guard.start()
        self.addCleanup(guard.stop)

    def test_explicit_coefficient_changes_only_iwo_material_command(self):
        before, _ = render(self.cfg, '2p0')
        cfg = copy.deepcopy(self.cfg)
        cfg['shared']['electron_richardson_A_cm2_K2'] = 40.9958341
        after, _ = render(cfg, '2p0')
        old, new = commands(before), commands(after)
        changed = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual(len(old), len(new))
        self.assertEqual(len(changed), 1)
        a, b = changed[0]
        self.assertTrue(a.startswith('material material=iwo '))
        self.assertEqual(b, a + ' arichn=40.9958341')
        self.assertNotIn('vsurfn=', after)
        self.assertNotIn('arichp=', after)

    def test_omitted_field_preserves_historical_native_input(self):
        source = ROOT / 'results/local_session_20260910/runs/20260912T074527_865393_fit_bulk_width04_2nm/device.in'
        generated, _ = render(self.cfg, '2p0')
        self.assertEqual(commands(source.read_text(encoding='ascii')), commands(generated))

    def test_nonpositive_or_nonfinite_coefficient_rejected(self):
        for value in (0, -1, float('inf'), float('nan')):
            with self.subTest(value=value):
                cfg = copy.deepcopy(self.cfg)
                cfg['shared']['electron_richardson_A_cm2_K2'] = value
                with self.assertRaises(ValueError):
                    render(cfg, '2p0')


if __name__ == '__main__':
    unittest.main()
