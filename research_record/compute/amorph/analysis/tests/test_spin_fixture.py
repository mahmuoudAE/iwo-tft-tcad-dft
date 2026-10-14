"""Real QE 7.5 nspin = 2 fixture (tests/fixtures/spin_toy, made by make_fixture.sh: triplet O2 + H2O toy, NOT a physics
result). Verifies on genuine QE output: the lsda layout of data-file-schema.xml and atomic_proj.xml (block order and
spin attribute, checked through the eigenvalue cross-check with up != down spectra), spin-correct weights and accounting,
the settings that C6 validates (starting magnetisations, convergence), C6 input validation on real converged runs, and
that D-24 lsda tables are reconstructed for diagnostics only."""
import gzip
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from analysis.tests import synth
from analysis.tests.helpers import manifest, qualification
from analysis import compare as C
from analysis.data import from_tables, from_xml
from analysis.report import cell_result
from analysis.section1 import Section1

FIX = os.path.join(synth.HERE, 'fixtures', 'spin_toy')
TAGS = ('ref', 'spinA', 'spinB')
HAVE = all(os.path.isfile(os.path.join(FIX, f'{k}_{t}.{e}')) for t in TAGS
           for k, e in (('data-file-schema', 'xml.gz'), ('atomic_proj', 'xml.gz'), ('projwfc', 'out.gz')))
NEX = 2          # the two O2 pi* electrons above N_v = 9


def load(tag):
    return from_xml(os.path.join(FIX, f'data-file-schema_{tag}.xml.gz'), os.path.join(FIX, f'atomic_proj_{tag}.xml.gz'),
                    os.path.join(FIX, f'projwfc_{tag}.out.gz'))


def res(tag):
    d, st = load(tag)
    c = Section1(d, st, name=f'spin_toy_{tag}', nex=NEX, mode='bulk')
    man = manifest(NEX, 'reference')
    return cell_result(c, 'xml', qual=qualification(man)), c


@unittest.skipUnless(HAVE, 'real nspin = 2 fixture not generated (tests/fixtures/spin_toy/make_fixture.sh)')
class TestSpinFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = {t: res(t) for t in TAGS}

    def test_layout_and_spin_split(self):
        for t in ('spinA', 'spinB'):
            d, st = load(t)                               # from_xml cross-checks every (spin, k, band) eigenvalue
            self.assertEqual(d.nspin, 2)
            self.assertLess(d.sources['_max_abs_e_proj_vs_schema_eV'], 1e-4)
            np.testing.assert_allclose(d.w.sum(axis=1), [1.0, 1.0])
            self.assertGreater(np.abs(d.e[0] - d.e[1]).max(), 0.1)        # up != down: the order is really tested
            hdr = d.sources['_atomic_proj_header']
            self.assertEqual(int(hdr['NUMBER_OF_SPIN_COMPONENTS']), 2)
        d, st = load('ref')
        self.assertEqual(d.nspin, 1)
        np.testing.assert_allclose(d.w.sum(), 2.0)

    def test_accounting_and_settings(self):
        for t in TAGS:
            r, c = self.r[t]
            self.assertEqual(c.acc['check'], 'PASS', (t, c.acc))
            self.assertLess(abs(c.occ_info['sum_f_w'] - c.N_el), 1e-6)
            self.assertTrue(r['run_settings']['scf_converged'])
        mag = lambda t: {s['name']: s['starting_magnetization'] for s in self.r[t][0]['run_settings']['species']}
        self.assertEqual(mag('spinA'), {'O1': 0.5, 'O2': 0.0, 'H': 0.0})
        self.assertEqual(mag('spinB'), {'O1': 0.1, 'O2': 0.1, 'H': 0.1})
        self.assertTrue(self.r['spinA'][0]['run_settings']['lsda'])
        self.assertEqual(len({self.r[t][0]['geometry_sha256'] for t in TAGS}), 1)

    def test_c6_on_real_runs(self):
        a, b, ref = (self.r[t][0] for t in ('spinA', 'spinB', 'ref'))
        out = C.c6(a, b, ref)
        # rc3: the localised start must carry its moment on W (and W first-shell O labels). The toy has no W, so the
        # O-localised start is not a registered localised start; every OTHER input check passes on the real runs
        # (nspin, XML source, geometry, settings, convergence, energies), and the uniform start is recognised.
        self.assertEqual(out['status'], 'INVALID', out)
        self.assertEqual(out['start_classes'], [None, 'delocalised'])
        self.assertEqual(len(out['unresolved_checks']), 1, out['unresolved_checks'])
        self.assertIn('one localised and one delocalised start', out['unresolved_checks'][0])
        self.assertEqual(C.c6(a, a, ref)['status'], 'INVALID')            # same run twice
        self.assertEqual(C.c6(a, b, b)['status'], 'INVALID')              # nspin = 2 reference
        self.assertEqual(C.c6(ref, b, ref)['status'], 'INVALID')          # nspin = 1 as a spin start

    def test_d24_lsda_tables_diagnostic_only(self):
        tmp = tempfile.mkdtemp(prefix='iwo_spin_d24_')
        try:
            sv = os.path.join(tmp, 'tmp', 'slab.save')
            os.makedirs(sv)
            for src, dst in ((f'data-file-schema_spinA.xml.gz', os.path.join(sv, 'data-file-schema.xml')),
                             (f'atomic_proj_spinA.xml.gz', os.path.join(sv, 'atomic_proj.xml')),
                             (f'projwfc_spinA.out.gz', os.path.join(tmp, 'projwfc_final.out'))):
                with gzip.open(os.path.join(FIX, src), 'rb') as fi, open(dst, 'wb') as fo:
                    shutil.copyfileobj(fi, fo)
            shutil.copy(os.path.join(FIX, 'pw_spinA.in'), os.path.join(tmp, 'scf.in'))
            script = os.path.join(tmp, 'export_tables.py')
            with open(script, 'w', newline='\n') as f:
                f.write(synth.d24_export_script())
            r = subprocess.run([sys.executable, script, 'tmp/slab.save', 'final'], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            dt, stt = from_tables(tmp)
            dx, stx = load('spinA')
            self.assertEqual(dt.nspin, 2)
            self.assertTrue(dt.diagnostic_only)
            np.testing.assert_allclose(dt.e, dx.e, atol=1e-5)
            np.testing.assert_allclose(dt.atom_w, dx.atom_w, atol=6e-7)
            c = Section1(dt, stt, name='spin_toy_tables', nex=NEX, mode='bulk')
            self.assertTrue(any('diagnostic only' in x for x in c.reasons))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
