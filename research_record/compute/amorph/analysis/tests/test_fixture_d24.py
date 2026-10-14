"""Real-format fixture: the local QE replay toy of the D-24 export test (In15WO24, a 40-atom CRYSTALLINE toy cell,
Gaussian 0.005 Ry, 7 k, 230 bands; not a project slab). Set IWO_D24_FIXTURE to a directory holding its
atomic_proj.xml.gz, data-file-schema.xml.gz and final_results.tar.gz (from ~/d24f_test/r_ok in WSL Ubuntu-22.04).
Checks: XML path against the D-24 table path, QE occupations reproduced by the recomputed Gaussian occupations,
accounting, and nc_readout.py against the package."""
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

from analysis.tests import synth
from analysis.data import from_tables, from_xml
from analysis.readout import hn_cell
from analysis.tests.helpers import QUALIFIED
from analysis.section1 import Section1

FIX = os.environ.get('IWO_D24_FIXTURE', '')
HAVE = bool(FIX) and all(os.path.isfile(os.path.join(FIX, f)) for f in
                         ('atomic_proj.xml.gz', 'data-file-schema.xml.gz', 'final_results.tar.gz'))
NC = os.path.abspath(os.path.join(synth.HERE, '..', '..', 'hse', 'tools', 'nc_readout.py'))


@unittest.skipUnless(HAVE, 'IWO_D24_FIXTURE not set (real QE toy fixture)')
class TestD24Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix='iwo_fix_')
        with tarfile.open(os.path.join(FIX, 'final_results.tar.gz')) as t:
            t.extractall(cls.d, filter='data') if hasattr(tarfile, 'data_filter') else t.extractall(cls.d)
        dx, sx = from_xml(os.path.join(FIX, 'data-file-schema.xml.gz'), os.path.join(FIX, 'atomic_proj.xml.gz'),
                          os.path.join(cls.d, 'projwfc_map_final.dat'))
        dt, stt = from_tables(cls.d)
        cls.cx = Section1(dx, sx, name='toy_In15WO24_bulk', nex=3)
        cls.ct = Section1(dt, stt, name='toy_In15WO24_bulk', nex=3)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def test_occupations_and_accounting(self):
        self.assertLess(self.cx.occ_info['max_abs_f_recomputed_minus_qe'], 1e-10)
        self.assertEqual(self.cx.acc['check'], 'PASS')
        self.assertEqual(self.cx.mode, 'bulk')

    def test_xml_vs_tables(self):
        self.assertAlmostEqual(self.cx.E_c, self.ct.E_c, places=5)
        self.assertAlmostEqual(self.cx.E_v, self.ct.E_v, places=5)
        a, b = hn_cell(self.cx, QUALIFIED), hn_cell(self.ct, QUALIFIED)
        self.assertEqual(a['class'], b['class'])
        for k in ('f_ext', 'f_locW', 'f_W5d'):
            self.assertAlmostEqual(a[k], b[k], places=5)
        self.assertAlmostEqual(a['Delta_W']['value_eV'], b['Delta_W']['value_eV'], places=5)

    def test_nc_readout_agrees(self):
        ap = os.path.join(self.d, 'atomic_proj.xml')
        import gzip
        with gzip.open(os.path.join(FIX, 'atomic_proj.xml.gz'), 'rb') as fi, open(ap, 'wb') as fo:
            shutil.copyfileobj(fi, fo)
        js = os.path.join(self.d, 'nc.json')
        r = subprocess.run([sys.executable, NC, '--proj', ap, '--pout', os.path.join(self.d, 'projwfc_final_summary.out'),
                            '--nv', '175', '--json', js], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(js) as f:
            j = json.load(f)
        self.assertAlmostEqual(j['E_c_eV'], self.cx.E_c, places=6)
        self.assertAlmostEqual(j['E_v_eV'], self.cx.E_v, places=6)


if __name__ == '__main__':
    unittest.main()
