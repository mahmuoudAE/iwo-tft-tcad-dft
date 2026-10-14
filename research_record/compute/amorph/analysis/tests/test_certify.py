"""Certificates and the validation gate: binding to run files and geometry, evidence hashes, manifest composition
check (kind from composition, never from the name), defaults (relaxation UNKNOWN, smearing pending), and the
propagation of missing qualification into every primary score."""
import json
import os
import shutil
import tempfile
import unittest

import numpy as np

from analysis.tests import synth
from analysis.tests.synth import donor_cell
from analysis import certify as CERT
from analysis.data import attach_lineage, from_xml
from analysis.readout import hn_cell
from analysis.section1 import Section1

MAN = {'kind': 'W-doped', 'film': {'In': 11, 'W': 1, 'O': 19}, 'substrate': {}, 'passivation': 'dissociated-water',
       'N_ex': 1, 'seed': 201}


class TestCertificate(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_cert_')
        sc, st, idx = donor_cell()
        self.data0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.0136, ef=0.0)
        self.paths = [os.path.join(self.d, n) for n in ('data-file-schema.xml', 'atomic_proj.xml', 'projwfc_final.out')]
        synth.write_schema(self.paths[0], self.data0, st)
        synth.write_atomic_proj(self.paths[1], self.data0, st.species)
        synth.write_projwfc_out(self.paths[2], self.data0, st.species)
        os.makedirs(os.path.join(self.d, 'evidence'))
        self.ev = {}
        for k in ('relax', 'audit', 'polish'):
            p = os.path.join(self.d, 'evidence', f'{k}.txt')
            with open(p, 'w') as f:
                f.write(f'{k} evidence\n')
            self.ev[k] = p
        synth.write_lineage(self.d, self.data0)
        self.data, self.st = from_xml(*self.paths)
        attach_lineage(self.data, [self.d])
        self.cert = os.path.join(self.d, 'cert.json')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def compile(self, man=MAN, width=None, relax=True):
        w = self.data.settings['degauss_Ry'] if width is None else width
        CERT.compile_certificate('aIWO_2p0_s1', self.data, self.st, self.cert, manifest=man,
                                 relaxation=('converged', [self.ev['relax']], None) if relax else None,
                                 smearing=('qualified', [self.ev['audit']], {'width_Ry': w}),
                                 geometry=('polished', [self.ev['polish']], None), compiled_by='test')

    def test_valid_and_class_resolves(self):
        self.compile()
        q = CERT.validate(self.cert, 'aIWO_2p0_s1', self.data, self.st)
        self.assertTrue(q['certificate_valid'], q['problems'])
        self.assertEqual((q['relaxation'], q['smearing_qualified'], q['geometry'], q['manifest_verified']),
                         ('converged', True, 'polished', True))
        self.assertEqual(q['reasons'], [])
        c = Section1(self.data, self.st, name='aIWO_2p0_s1', manifest=q['manifest'])
        self.assertEqual(hn_cell(c, q)['class'], 'DONOR')

    def test_defaults_without_certificate(self):
        q = CERT.validate(None, 'aIWO_2p0_s1', self.data, self.st)
        self.assertEqual((q['relaxation'], q['smearing_qualified'], q['geometry']), ('unknown', False, 'unknown'))
        c = Section1(self.data, self.st, name='aIWO_2p0_s1')
        r = hn_cell(c, q)
        self.assertEqual(r['class'], 'UNRESOLVED')
        self.assertEqual(r['class_if_resolved'], 'DONOR')
        self.compile(relax=False)                                       # no relaxation claim: stays UNKNOWN
        q = CERT.validate(self.cert, 'aIWO_2p0_s1', self.data, self.st)
        self.assertEqual(q['relaxation'], 'unknown')
        self.assertTrue(any('RELAXATION UNKNOWN' in x.upper() for x in q['reasons']))

    def test_tampered_run_file_invalidates(self):
        self.compile()
        with open(self.paths[1], 'a') as f:
            f.write('\n')
        data, st = from_xml(*self.paths)
        attach_lineage(data, [self.d])
        q = CERT.validate(self.cert, 'aIWO_2p0_s1', data, st)
        self.assertFalse(q['certificate_valid'])
        self.assertFalse(q['smearing_qualified'])
        self.assertTrue(any('not bound' in p for p in q['problems']))

    def test_wrong_cell_and_geometry(self):
        self.compile()
        self.assertFalse(CERT.validate(self.cert, 'aIWO_2p0_s2', self.data, self.st)['certificate_valid'])
        with open(self.cert) as f:
            cert = json.load(f)
        cert['geometry_sha256'] = 'x' * 64
        with open(self.cert, 'w') as f:
            json.dump(cert, f)
        q = CERT.validate(self.cert, 'aIWO_2p0_s1', self.data, self.st)
        self.assertFalse(q['certificate_valid'])

    def test_evidence_and_width(self):
        self.compile()
        with open(self.ev['audit'], 'a') as f:
            f.write('edited after certification\n')
        q = CERT.validate(self.cert, 'aIWO_2p0_s1', self.data, self.st)
        self.assertTrue(q['certificate_valid'])
        self.assertFalse(q['smearing_qualified'])
        self.compile(width=0.005)                                        # certified width != run width
        q = CERT.validate(self.cert, 'aIWO_2p0_s1', self.data, self.st)
        self.assertFalse(q['smearing_qualified'])

    def test_manifest_composition(self):
        bad = dict(MAN, film={'In': 11, 'W': 1, 'O': 20})
        self.compile(man=bad)
        q = CERT.validate(self.cert, 'aIWO_2p0_s1', self.data, self.st)
        self.assertFalse(q['manifest_verified'])
        self.assertTrue(any('composition manifest' in x for x in q['reasons']))
        lie = dict(MAN, kind='compensated', N_ex=0)                       # declared compensated, composition says 1
        ok, prob = CERT.check_manifest(lie, self.st)
        self.assertFalse(ok)

    def test_kind_from_composition_not_name(self):
        comp = CERT.manifest_from_spec({'name': 'aIWO_2p0_s1', 'mode': 'slab', 'n_In': 98, 'n_W': 2, 'n_O': 153,
                                        'seed': 201, 'passivate': True})
        self.assertEqual((comp['kind'], comp['N_ex']), ('compensated', 0))
        dop = CERT.manifest_from_spec({'name': 'aIWO_2p0_comp_s1', 'mode': 'slab', 'n_In': 98, 'n_W': 2, 'n_O': 152,
                                       'seed': 201, 'passivate': True})
        self.assertEqual((dop['kind'], dop['N_ex']), ('W-doped', 2))
        iface = CERT.manifest_from_spec({'name': 'x', 'mode': 'interface', 'n_In': 98, 'n_W': 2, 'n_O': 152, 'seed': 702,
                                         'passivate': True, 'substrate': {'n_Al': 60, 'n_O': 90, 'thickness_A': 10.2}})
        self.assertEqual(iface['substrate'], {'Al': 60, 'O': 90})

    def test_hashes(self):
        h = CERT.register_hash()
        self.assertTrue(h['sha256'] is None or len(h['sha256']) == 64)
        self.assertEqual(len(CERT.code_fingerprint()), 64)
        self.assertEqual(self.st.geometry_hash(), CERT.geometry_hash(self.st.species, self.st.pos + 1e-7, self.st.cell))


if __name__ == '__main__':
    unittest.main()
