"""nc_readout.py (A23 / A27 C5 reader): nspin = 1 behaviour against the package, nspin = 2 support, and the --xml H-N
accounting path (every class printed with its unresolved checks). Synthetic bulk cells only."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from analysis.tests import synth
from analysis.tests.synth import SynthCell, bulk_structure
from analysis.data import from_xml
from analysis.section1 import Section1

NC = os.path.abspath(os.path.join(synth.HERE, '..', '..', 'hse', 'tools', 'nc_readout.py'))


def bulk_cell(nspin=1):
    st = bulk_structure()
    ALL = list(range(st.nat))
    half = ALL[:20]
    sc = SynthCell(st, nspin=nspin, nks=2, wk=[1.0, 1.0])
    for E in (-3.0, -2.5, -2.2, -2.0):
        sc.add(E, ALL)
    if nspin == 1:
        sc.add(0.0, half).add(0.4, {5: 1.0}, w5d=0.8).add(1.6, ALL)
    else:
        sc.add(0.0, half, spin=0).add(0.4, {5: 1.0}, w5d=0.8, spin=0).add(1.6, ALL, spin=0)
        sc.add(0.1, ALL, spin=1).add(0.2, {5: 1.0}, w5d=0.6, spin=1).add(1.7, ALL, spin=1)
    return sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0), st


class TestNcReadout(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_nc_')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def files(self, data, st):
        p = {k: os.path.join(self.d, v) for k, v in (('proj', 'atomic_proj_pbe.xml'), ('pout', 'projwfc_pbe.out'),
                                                      ('xml', 'data-file-schema_pbe.xml'), ('json', 'nc.json'),
                                                      ('hn', 'hn.json'))}
        synth.write_atomic_proj(p['proj'], data, st.species)
        synth.write_projwfc_out(p['pout'], data, st.species)
        synth.write_schema(p['xml'], data, st)
        return p

    def run_nc(self, p, extra=()):
        cmd = [sys.executable, NC, '--proj', p['proj'], '--pout', p['pout'], '--nv', '4', '--json', p['json'], *extra]
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(p['json']) as f:
            return r.stdout, json.load(f)

    def test_golden_against_committed_original(self):
        """Legacy-adapter numbers identical to the committed (rc0) nc_readout.py; only the non-primary label added."""
        try:
            src = subprocess.run(['git', 'show', 'HEAD:compute/amorph/hse/tools/nc_readout.py'], capture_output=True,
                                 text=True, cwd=os.path.dirname(NC), check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest('git or the committed nc_readout.py not available')
        orig = os.path.join(self.d, 'nc_readout_orig.py')
        with open(orig, 'w', newline='\n') as f:
            f.write(src)
        data, st = bulk_cell(1)
        p = self.files(data, st)
        out_new, j_new = self.run_nc(p)
        js = os.path.join(self.d, 'orig.json')
        r = subprocess.run([sys.executable, orig, '--proj', p['proj'], '--pout', p['pout'], '--nv', '4', '--json', js],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(js) as f:
            j_old = json.load(f)
        self.assertEqual({k: v for k, v in j_new.items() if k not in ('adapter', 'primary')}, j_old)
        self.assertEqual((j_new['primary'], 'LEGACY' in out_new), (False, True))
        self.assertEqual([l for l in out_new.splitlines() if not l.startswith('LEGACY')], r.stdout.splitlines())

    def test_nspin1_matches_package(self):
        data, st = bulk_cell(1)
        p = self.files(data, st)
        out, j = self.run_nc(p)
        self.assertNotIn('nspin', j)
        self.assertFalse(j['primary'])
        d, s = from_xml(p['xml'], p['proj'], p['pout'])
        c = Section1(d, s, name='bulk_test', nex=1, mode='bulk')
        self.assertAlmostEqual(j['E_c_eV'], c.E_c, places=6)
        self.assertAlmostEqual(j['E_v_eV'], c.E_v, places=6)
        self.assertAlmostEqual(j['W5d_minus_Ec_eV'], 0.4, places=6)

    def test_nspin2(self):
        data, st = bulk_cell(2)
        p = self.files(data, st)
        out, j = self.run_nc(p)
        self.assertEqual(j['nspin'], 2)
        self.assertEqual(j['n_k'], 2)
        self.assertEqual(j['E_c_state']['s'], 1)
        self.assertAlmostEqual(j['E_c_eV'], 0.0, places=6)
        self.assertEqual(j['W5d_state']['s'], 2)                         # the 0.2 eV W state is in the down channel
        self.assertAlmostEqual(j['W5d_minus_Ec_eV'], 0.2, places=6)
        self.assertIn(' s k  band', out)

    def test_hn_accounting(self):
        data, st = bulk_cell(2)
        p = self.files(data, st)
        out, j = self.run_nc(p, ['--xml', p['xml'], '--nex', '1', '--name', 'synthetic_spin', '--hn-json', p['hn']])
        lines = out.splitlines()
        i = next(k for k, l in enumerate(lines) if l.startswith('H-N class:'))
        self.assertTrue(lines[i + 1].strip().startswith('unresolved checks:'))
        with open(p['hn']) as f:
            hn = json.load(f)
        self.assertEqual(hn['occupations']['nspin'], 2)
        self.assertIn('class_if_resolved', hn['H-N'])
        r = subprocess.run([sys.executable, NC, '--proj', p['proj'], '--pout', p['pout'], '--nv', '4', '--xml', p['xml']],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)                              # --xml without --nex is refused


if __name__ == '__main__':
    unittest.main()
