"""rc5 regression tests: the three blocking items of the Codex rc4 review (each counterexample reproduced) and the
self-audit of the same three bug families: (a) a validation result computed but not propagated, (b) two missing values
counted as equal, (c) a text parse matching inside quotes or comments. Synthetic data only."""
import json
import os
import shutil
import tempfile
import unittest

from analysis.tests import builders as B
from analysis.tests.helpers import manifest, qualification
from analysis.tests.test_regressions_rc2 import cell, certify, gate, xml_export
from analysis import certify as CERT
from analysis import compare as C
from analysis import qeio
from analysis.readout import status


class Tmp(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_rc5_')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)


class TestItem1RejectionPropagates(Tmp):
    """Counterexample: a certificate without code_sha256 / register_sha256 is NOT VALID, yet rc4 left the
    qualification reasons empty and status(True, [], q) gave PASS."""

    def test_counterexample(self):
        e, ev, w, st = xml_export(os.path.join(self.d, 'x'))
        cert = certify(e, ev, w)[0]
        c = qeio.load_json(cert)
        del c['code_sha256'], c['register_sha256']
        bad = os.path.join(e, 'bad.json')
        with open(bad, 'w') as f:
            json.dump(c, f)
        code, q, _ = gate(e, bad)
        self.assertEqual(code, 1)
        self.assertTrue(q['problems'])
        self.assertTrue(q['reasons'])
        self.assertEqual(status(True, [], q)['status'], 'UNRESOLVED')
        r, _ = cell(e, os.path.join(self.d, 'o'), bad)
        self.assertEqual(r['H-N']['class'], 'UNRESOLVED')
        self.assertTrue(any('NOT VALID' in x for x in r['H-N']['unresolved_checks']))
        self.assertIsNone(r['alignment']['aligned_host_edge_eV'])
        self.assertFalse(r['accounting_partition']['N_ex_verified'])          # (a) manifest of a NOT VALID gate unused
        code, q, _ = gate(e, cert)
        self.assertEqual((code, q['reasons']), (0, []))                          # the intact certificate stays VALID

    def test_roles_need_a_valid_gate(self):
        g = B.slab(0.4)
        q = qualification(manifest(seed=9), pseudos={})
        q['problems'] = ['certificate lacks code_sha256']
        self.assertEqual(status(True, [], q)['status'], 'UNRESOLVED')
        r = B.make(geo=g, q=q)
        self.assertIsNone(C.certified_kind(r))
        self.assertIsNone(C.certified_seed(r))
        self.assertIsNone(C.certified_geometry(r))
        self.assertEqual(r['H-N']['class'], 'UNRESOLVED')


class TestItem2UnknownSampling(unittest.TestCase):
    """Counterexample: PAW / NC / HSE records with every k_mesh = None and HSE q_mesh = None gave C5 PASS."""

    def runs(self, k=None, q=None, **common):
        g = B.slab(0.41)
        paw, nc, hse = B.c5_runs('aIWO_0p7_s1', g, common=common)
        mk = lambda rec, **o: B.make(rec['cell'], geo=g, settings=dict(rec['run_settings'], **o))
        return mk(paw, k_mesh=k), mk(nc, k_mesh=k), mk(hse, k_mesh=k, q_mesh=q)

    def test_counterexample(self):
        r = C.c5(*self.runs())
        self.assertEqual(r['status'], 'UNRESOLVED', r)
        self.assertTrue(any('not known' in x for x in r['unresolved_checks']))
        r = C.c5(*self.runs(k=[0, 0, 0, 0, 0, 0], q=[0, 0, 0]))
        self.assertEqual(r['status'], 'UNRESOLVED')
        r = C.c5(*self.runs(k=[2, 2, 1, 0, 0, 0], q=None))
        self.assertEqual(r['status'], 'UNRESOLVED')
        self.assertEqual(C.c5(*self.runs(k=[2, 2, 1, 0, 0, 0], q=[2, 2, 1]))['status'], 'PASS')

    def test_audit_missing_never_equal(self):
        g = B.slab(0.42)
        a, b = B.make(geo=g, settings={'functional': ''}), B.make(geo=g, w_ry=0.005, settings={'functional': ''})
        self.assertEqual(C.c3(a, b)['status'], 'INVALID')                       # unknown functional on both sides
        a, b = B.make(geo=g, settings={'k_mesh': None}), B.make(geo=g, w_ry=0.005, settings={'k_mesh': None})
        self.assertEqual(C.c3(a, b)['status'], 'INVALID')
        a, b = B.make(geo=g, settings={'species': []}), B.make(geo=g, w_ry=0.005, settings={'species': []})
        self.assertFalse(C.same_pseudos(a, b))                                   # no UPF on either side
        nofile = [{'name': e, 'starting_magnetization': 0.0} for e in ('H', 'In', 'O', 'W')]
        a, b = B.make(geo=g, settings={'species': nofile}), B.make(geo=g, w_ry=0.005, settings={'species': nofile})
        self.assertFalse(C.same_pseudos(a, b))
        self.assertEqual(C.c3(a, b)['status'], 'INVALID')
        self.assertIsNone(C._mesh(None))
        self.assertIsNone(C._mesh([2, 2, 1, 0, 0, 2]))
        self.assertEqual(C._mesh([1, 1, 1], 3), [1, 1, 1])


class TestItem3QuotedText(Tmp):
    """Counterexample: &INPUTPP with only prefix='foo plot_num=11 bar' gave plot_num 11."""

    def test_counterexample(self):
        self.assertIsNone(qeio.pp_plot_num("&INPUTPP\n  prefix='foo plot_num=11 bar'\n/\n"))
        self.assertIsNone(qeio.pp_plot_num('&INPUTPP\n  prefix="foo plot_num=11 bar"\n/\n'))
        self.assertIsNone(qeio.pp_plot_num("&INPUTPP\n  prefix='it''s plot_num=11'\n/\n"))
        self.assertEqual(qeio.pp_plot_num("&INPUTPP\n  filplot = 'v/p.pp', plot_num = 11\n/\n"), 11)
        self.assertIsNone(qeio.pp_plot_num("&INPUTPP\n  title = '&inputpp'\n/\n&INPUTPP\n plot_num = 11\n/\n"))

    def test_audit_pw_input(self):
        txt = ("&CONTROL\n  calculation = 'scf', title = 'degauss = 0.9 nat = 7'\n/\n&SYSTEM\n"
               "  ibrav = 0, nat = 2, ntyp = 2  ! degauss = 0.5\n  occupations = 'smearing', smearing = \"gaussian\"\n"
               "  degauss = 0.001, celldm(1) = 20.0, starting_magnetization(2) = 0.3\n/\n"
               "ATOMIC_SPECIES\n  In 114.8 In.upf\n  O 16.0 O.upf  ! O2 16.0 O2.upf\n"
               "CELL_PARAMETERS bohr\n  20.0 0 0\n  0 20.0 0\n  0 0 40.0\n"
               "ATOMIC_POSITIONS angstrom\n  ! In 9 9 9\n  In 0.1 0.2 0.3\n  O 0.5 0.5 0.5  ! comment\n"
               "K_POINTS automatic\n  2 2 1 0 0 0\n")
        p = os.path.join(self.d, 'scf.in')
        with open(p, 'w', newline='\n') as f:
            f.write(txt)
        s = qeio.pw_in_settings(p)
        self.assertEqual((s['degauss_Ry'], s['smearing'], s['k_mesh']), (0.001, 'gaussian', [2, 2, 1, 0, 0, 0]))
        self.assertEqual([x['name'] for x in s['species']], ['In', 'O'])
        self.assertEqual(s['species'][1]['starting_magnetization'], 0.3)
        g = qeio.read_pw_in(p)
        self.assertEqual(g['labels'], ['In', 'O'])
        self.assertAlmostEqual(g['positions_A'][0][0], 0.1)
        with open(p, 'w', newline='\n') as f:
            f.write(txt.replace('degauss = 0.001,', 'degauss = 0.001, degauss = 0.002,'))
        with self.assertRaises(ValueError):                                       # repeated assignment refused
            qeio.pw_in_settings(p)

    def test_audit_lineage_conflict(self):
        p = os.path.join(self.d, 'lineage_final.dat')
        h1, h2 = 'a' * 64, 'b' * 64
        with open(p, 'w', newline='\n') as f:
            f.write(f'# sha256 {h2} pseudo/W.upf\nsha256 {h1} pseudo/In.upf\nsha256 {h1} pseudo/W.upf\n'
                    f'sha256 {h2} pseudo/W.upf\nsha256 {h1} pseudo/O.upf trailing\n')
        lin = CERT.parse_lineage(p)
        self.assertEqual(lin['In.upf'], h1)
        self.assertIsNone(lin['W.upf'])                                          # conflicting entries: not covered
        self.assertNotIn('O.upf', lin)                                           # malformed line ignored


if __name__ == '__main__':
    unittest.main()
