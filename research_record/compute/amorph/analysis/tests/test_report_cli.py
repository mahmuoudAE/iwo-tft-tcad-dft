"""Report rule (no class or status without its unresolved checks), provenance on every output, and the CLI end to end:
certify (DFT agent) -> validate-cert (gate) -> cell -> compare / series, on synthetic export directories."""
import contextlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest

import numpy as np

from analysis.tests import synth
from analysis.tests.synth import donor_cell
from analysis.tests.helpers import result
from analysis import register as R
from analysis.cli import main
from analysis.report import text_report

STATUS_LINE = re.compile(r'(class|P\d\w*|claude\w*|STATUS|GATE)\b.*: (UNRESOLVED|DONOR|ECB|PARTIAL|PASS|FAIL|N/A|VALID|NOT)\b')
MAN = {'kind': 'W-doped', 'film': {'In': 11, 'W': 1, 'O': 19}, 'substrate': {}, 'passivation': 'dissociated-water',
       'N_ex': 1, 'seed': 201}


def check_rule(testcase, text):
    lines = text.splitlines()
    n = 0
    for i, l in enumerate(lines):
        if STATUS_LINE.search(l) and 'N/A' not in l:
            n += 1
            testcase.assertTrue(i + 1 < len(lines) and lines[i + 1].strip().startswith(('unresolved checks:',
                                                                                        'qualification checks:')),
                                f'status line without its unresolved checks: {l!r}')
    return n


class TestReport(unittest.TestCase):
    def test_every_class_has_checks_and_provenance(self):
        sc, st, idx = donor_cell()
        for certified in (True, False):
            r = result(sc, 9.0, certified=certified)
            txt = text_report(r)
            self.assertGreaterEqual(check_rule(self, txt), 4)
            self.assertIn('register sha256', txt)
            pv = r['provenance']
            self.assertEqual(len(pv['code_sha256']), 64)
            self.assertIn('register', pv)
            json.dumps(r)


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_cli_')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def export(self, sub, degauss):
        d = os.path.join(self.d, sub)
        os.makedirs(d)
        sc, st, idx = donor_cell()
        data = sc.build(9.0, smearing='gaussian', degauss_ev=degauss, ef=0.0)
        synth.write_schema(os.path.join(d, 'data-file-schema.xml'), data, st)
        synth.write_atomic_proj(os.path.join(d, 'atomic_proj.xml'), data, st.species)
        smap = synth.write_projwfc_out(os.path.join(d, 'projwfc_final.out'), data, st.species)
        with open(os.path.join(d, 'projwfc_map_final.dat'), 'w') as f:
            f.write('# map\n' + ''.join(f'{i} {a} {s} {w} {l} {m}\n' for i, (a, s, w, l, m) in enumerate(smap, 1)))
        z = np.linspace(0, 40.0 / R.BOHR_A, 3001)[:-1]
        np.savetxt(os.path.join(d, 'final_avg.dat'), np.c_[z, np.full_like(z, 0.1), np.full_like(z, 0.1)])
        with open(os.path.join(d, 'avg_final.in'), 'w') as f:
            f.write('1\nfinal_v.pp\n1.0\n3000\n3\n4.0\n')
        with open(os.path.join(d, 'pp_final.in'), 'w') as f:
            f.write("&INPUTPP\n  prefix = 'slab', outdir = './tmp', filplot = 'final_v.pp', plot_num = 11\n/\n")
        synth.write_lineage(d, data)
        ev = os.path.join(d, 'evidence.txt')
        with open(ev, 'w') as f:
            f.write(f'audit and relax evidence for {sub}\n')
        with open(os.path.join(d, 'manifest.json'), 'w') as f:
            json.dump(dict(MAN, seed=hash(sub) % 1000), f)
        return d, ev, degauss / R.RY_EV

    def run_cli(self, argv, code=None):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                main(argv)
            except SystemExit as e:
                if code is None or e.code != code:
                    raise
        return buf.getvalue()

    def certify(self, d, ev, width):
        cert = os.path.join(d, 'cert.json')
        self.run_cli(['certify', d, '--name', 'aIWO_2p0_s1', '--out', cert, '--manifest', os.path.join(d, 'manifest.json'),
                      '--relaxation', 'converged', '--relaxation-evidence', ev, '--smearing', 'qualified',
                      '--smearing-width', f'{round(width, 10)}', '--smearing-evidence', ev, '--geometry', 'polished',
                      '--geometry-evidence', ev, '--compiled-by', 'test'])
        return cert

    def test_certify_cell_compare(self):
        (e1, ev1, w1), (e5, ev5, w5) = self.export('w001', 0.001 * R.RY_EV), self.export('w005', 0.005 * R.RY_EV)
        c1, c5 = self.certify(e1, ev1, w1), self.certify(e5, ev5, w5)
        out = self.run_cli(['validate-cert', e1, '--name', 'aIWO_2p0_s1', '--certificate', c1], code=0)
        self.assertIn('GATE: VALID', out)
        o1, o5, ou = (os.path.join(self.d, x) for x in ('c001', 'c005', 'unc'))
        out = self.run_cli(['cell', e1, '--name', 'aIWO_2p0_s1', '--certificate', c1, '--out', o1])
        check_rule(self, out)
        self.assertIn('class: DONOR', out)
        self.run_cli(['cell', e5, '--name', 'aIWO_2p0_s1', '--certificate', c5, '--out', o5])
        out = self.run_cli(['cell', e1, '--name', 'aIWO_2p0_s1', '--out', ou])        # no certificate
        self.assertIn('class: UNRESOLVED  (class if resolved: DONOR', out)
        self.assertIn('RELAXATION UNKNOWN', out.upper())
        with open(o1 + '.json') as f:
            r1 = json.load(f)
        self.assertEqual(r1['provenance']['source'], 'xml')
        self.assertEqual(r1['run_qualification']['reasons'], [])
        self.assertEqual(r1['provenance']['certificate_sha256'], r1['run_qualification']['certificate_sha256'])
        self.assertFalse(r1['alignment']['valid'])                    # 4.75 A interior: no common interval
        out = self.run_cli(['compare', 'c3', o1 + '.json', o5 + '.json'])
        self.assertIn('STATUS: PASS\n    unresolved checks: none', out)
        res = json.loads(out.split('STATUS:')[0])
        self.assertEqual(len(res['provenance']['input_files_sha256']), 2)
        self.assertEqual(len(res['meta']['input_files']), 2)
        self.assertEqual(len(res['provenance']['inputs']), 2)
        out = self.run_cli(['compare', 'c3', o1 + '.json', o1 + '.json'])
        self.assertIn('STATUS: NOT A PASS', out)
        out = self.run_cli(['compare', 'c3', ou + '.json', o5 + '.json'])
        self.assertIn('STATUS: UNRESOLVED', out)
        with open(os.path.join(e1, 'atomic_proj.xml'), 'a') as f:
            f.write('\n')                                              # tamper after certification
        out = self.run_cli(['validate-cert', e1, '--name', 'aIWO_2p0_s1', '--certificate', c1], code=1)
        self.assertIn('GATE: NOT VALID', out)
        spec = {'cells': {'2.0': [o5 + '.json', o5 + '.json']}}
        sp = os.path.join(self.d, 'series.json')
        with open(sp, 'w') as f:
            json.dump(spec, f)
        out = self.run_cli(['series', sp])
        self.assertIn('STATUS: UNRESOLVED', out)


if __name__ == '__main__':
    unittest.main()
