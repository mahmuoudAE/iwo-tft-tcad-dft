"""Independent electrical-stack and native-physics selection checks; no solver launch."""
import copy
import re
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from rebuild_model import load, render


class RebuildModelTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load(ROOT/'config/rebuild_seed.json')

    def test_all_thicknesses_keep_channel_gap_stack_and_measurement_grid(self):
        for key, c in self.cfg['curves'].items():
            with self.subTest(key=key):
                text, meta = render(self.cfg, key)
                self.assertAlmostEqual(meta['drain_start_um']-meta['source_end_um'], 20)
                boundaries = meta['y_boundaries_um']
                self.assertAlmostEqual(-boundaries[1]*1000, c['thickness_nm'])
                self.assertAlmostEqual((boundaries[3]-boundaries[2])*1000, 2)
                self.assertAlmostEqual((boundaries[4]-boundaries[3])*1000, 15)
                self.assertAlmostEqual((boundaries[5]-boundaries[4])*1000, 50)
                self.assertAlmostEqual((boundaries[1]-boundaries[0])*1000, 70)
                self.assertTrue(boundaries[1] < meta['probe_xy_um'][1] < 0)
                sweep = text.split('log outf=transfer.log\n')[1].split('log off')[0]
                values = [float(x) for x in re.findall(r'^solve vgate=(.*)$', sweep, re.M)]
                np.testing.assert_allclose(values, np.linspace(-3, 3, 121), rtol=0, atol=1e-9)
                self.assertNotIn('infile=', text.split('solve init')[0])

    def test_no_dormant_dos_or_mobility_physics_in_minimal_baseline(self):
        text, _ = render(self.cfg)
        self.assertFalse(re.search(r'^defects\b|^intdefects\b|^mobility\b', text, re.M))
        self.assertNotIn('carriers=1', text)

    def test_explicit_native_interface_sheet_and_bulk_energy_references(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['defects'].update(bulk=True, interface=True)
        text, _ = render(cfg)
        self.assertIn('intnumber="2/3" max.gaussian', text)
        self.assertIn('egd=2.85', text)
        self.assertIn('x.min=0 x.max=24 y.min=-1e-6 y.max=1e-6', text)
        self.assertEqual(len(re.findall(r'^region ', text, re.M)), 5)

    def test_plots_cover_every_saved_structure_and_log(self):
        text, _ = render(self.cfg, plots=True)
        saved = re.findall(r'^(?:save|log) outf=(\S+)', text, re.M)
        plotted = re.findall(r'^tonyplot (\S+)', text, re.M)
        self.assertEqual(set(saved), set(plotted))
        self.assertTrue(text.endswith('quit\n'))

    def test_field_mobility_is_an_isolated_model_with_depth_diagnostics(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['transport'].update(mode='prpmob', critical_field_V_cm=1e6)
        text, _ = render(cfg, '31p8')
        self.assertIn('prpmob print', text)
        self.assertNotIn('igzo.tokyo', text)
        self.assertIn('gsurfn=1 ecn.mu=1000000', text)
        probes = re.findall(r'^probe name=(\S+) .*? y=([-0-9.e]+)', text, re.M)
        self.assertEqual(len(probes), 7)
        self.assertTrue(all(-.0318 < float(y) < 0 for _, y in probes))
        for name in ('channel_ey', 'front_mobility', 'front_ey', 'back_mobility', 'back_ey'):
            self.assertIn(f'outfile="{name}_vg.dat"', text)

    def test_resistance_retains_contact_injection_and_internal_voltage_evidence(self):
        cfg = copy.deepcopy(self.cfg)
        cfg['contacts'].update(mode='schottky', electron_barrier_eV=.15, resistance_ohm_um=30000)
        text, _ = render(cfg)
        for name in ('source', 'drain'):
            self.assertIn(f'contact name={name} workfunction=4.45 surf.rec resistance=30000', text)
            self.assertIn(f'vint."{name}"', text)
        self.assertNotIn(' ohms', text.lower())


if __name__ == '__main__':
    unittest.main()
