"""rc6 regression tests: the three blocking items of the Codex rc5 review (counterexamples reproduced) and the focused
self-audit: (a) every control checks the certificate / provenance of EVERY input (table-driven: each input corrupted in
turn gives no pass verdict), (b) data pairing is verified or refused, (c) every entry point reaches the library
validation path (one positive end-to-end test per entry point). Synthetic data only."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

from analysis.tests import builders as B
from analysis.tests import synth
from analysis.tests.helpers import manifest, qualification
from analysis.tests.synth import SynthCell, slab_structure
from analysis.tests.test_compare import series_inputs
from analysis.tests.test_regressions_rc2 import certify, gate, xml_export
from analysis import certify as CERT
from analysis import compare as C
from analysis import qeio
from analysis import register as R
from analysis.data import from_xml
from analysis.report import cell_result
from analysis.section1 import Section1

PASSING = {'PASS', 'ROBUST', 'SUPPORTED', 'W-CENTRED', 'HOST-TRAP-MEDIATED', 'CROSSOVER', 'NO CROSSOVER', 'REPORTED'}
NC = os.path.abspath(os.path.join(synth.HERE, '..', '..', 'hse', 'tools', 'nc_readout.py'))


def corrupt(rec):
    """The record with a NOT VALID certificate (gate problem), re-sealed: its stored classes and edges stay as they
    were, so only a control that recomputes every input's provenance can refuse it."""
    r = json.loads(json.dumps(rec))
    q = r['run_qualification']
    q['problems'] = ['certificate corrupted (test: lineage misses a UPF)']
    q['pseudopotentials_bound'] = False
    q['reasons'] = CERT.qualification_reasons(q)
    r['self_sha256'] = CERT.canonical_sha256(r)
    return r


def verdicts(out):
    v = [out.get('status'), out.get('outcome')]
    for x in out.values():
        if isinstance(x, dict):
            v.append(x.get('status'))                                   # a nested verdict (shift, Eg_difference, ...)
            if x and 'status' not in x and all(isinstance(y, str) for y in x.values()):
                v += list(x.values())                                   # role -> status maps (H-G P1 / P2)
    return {x for x in v if isinstance(x, str)}


class TestItem1C6EveryStart(unittest.TestCase):
    """Counterexample: valid localised start at -100 Ry, delocalised start at -99 Ry with a NOT VALID certificate
    (O UPF lineage missing): rc5 C6 returned PASS."""

    def test_counterexample(self):
        g = B.slab(0.51)
        ref = B.make('aIWO_2p0_s1', geo=g, etot=-100.5)
        a, b = B.spin_starts('aIWO_2p0_s1', g, e_loc=-100.0, e_deloc=-99.0)
        self.assertEqual(C.c6(a, b, ref)['status'], 'PASS')
        bad = corrupt(b)
        r = C.c6(a, bad, ref)
        self.assertNotIn(r['status'], PASSING)
        self.assertTrue(any('NOT VALID' in x for x in r['unresolved_checks']))
        q = qualification(manifest(), pseudos={})                        # an honest NOT VALID record, not re-sealed
        q['problems'], q['pseudopotentials_bound'] = ['lineage does not cover O'], False
        de = [dict(s, starting_magnetization=0.1) for s in B.PAW_SPECIES]
        honest = B.make('aIWO_2p0_s1', geo=g, nspin=2, etot=-99.0, settings={'lsda': True, 'species': de}, q=q)
        self.assertNotIn(C.c6(a, honest, ref)['status'], PASSING)


class TestSelfAuditA_EveryInput(unittest.TestCase):
    """For every control, each input record's certificate is corrupted in turn: no pass verdict may remain."""

    @classmethod
    def setUpClass(cls):
        T = {}
        g = B.slab(0.52)
        T['c3'] = (lambda r: C.c3(*r), [B.make(geo=g), B.make(geo=g, w_ry=0.005)])
        ref = B.make('aIWO_2p0_s1', geo=g, etot=-10.0)
        T['c6'] = (lambda r: C.c6(*r), list(B.spin_starts('aIWO_2p0_s1', g)) + [ref])
        T['c5'] = (lambda r: C.c5(*r), list(B.c5_runs('aIWO_0p7_s1', B.slab(0.53))))
        T['c4'] = (lambda r: C.c4(*r), [B.make('aIWO_1p0_s1', geo=B.slab(0.54), geometry='mv'),
                                        B.make('aIWO_1p0_s1', geo=B.slab(0.55))])
        main, parent, paired, maps = B.c1_set()
        T['c1'] = (lambda r: C.c1(r[0], r[1:4], r[4], maps), [main] + paired + [parent])
        geo, _ = B.c1_paired(B.c1_parent(), 0)
        T['c2'] = (lambda r: C.c2(*r), [paired[0], B.diluted(geo, paired[0], loc_w=True)])
        pg = B.c1_parent()
        pgeo, m = B.c1_paired(pg, 0)
        st, idx = pgeo
        par = B.make('aIO_0p7_s1', geo=pg, kind='undoped')
        cons = {'type': 'C1-paired', 'parent_geometry_sha256': par['geometry_sha256'], 'site': idx['W'] + 1,
                'draw_rank': 1}
        tr = B.make('aIWO_0p7_C1a', geo=pgeo, ef=-0.5, extra=[((-0.5, {idx['W']: 0.5, idx['added_O']: 0.5}),
                                                               {'w5d': 0.2})], man_extra={'construction': cons})
        amap = B.atom_map(tr, par, m)
        T['attribution'] = (lambda r: C.attribution(r[0], r[1], amap), [tr, par])
        s1, s2 = B.make('aIWO_2p0_s1', geo=B.slab(0.01)), B.make('aIWO_2p0_s2', geo=B.slab(0.02))
        comp = B.make('aIWO_2p0_comp_s1', geo=B.slab(0.03), kind='compensated')
        a1 = B.make('aIO_2p0_s1', geo=B.slab(0.04, w=False), kind='undoped')
        a2 = B.make('aIO_2p0_s2', geo=B.slab(0.05, w=False), kind='undoped')
        T['hg'] = (lambda r: C.hg_score(*r), [s1, s2, comp, a1, a2])
        oh = B.make('aIWO_2p0_s1', geo=B.slab(0.01), seed=77, V=1.0)
        bare = B.make('aIWO_2p0_s1_bare', geo=B.slab(0.02), seed=77, V=0.9, man_extra={'passivation': 'none'})
        T['hh'] = (lambda r: C.hh(*r), [oh, bare])
        T['hi'] = (lambda r: C.hi(*r), [B.make('aIWO_2p0_Al2O3_s2', geo=B.interface(), V=1.0),
                                        B.make('aIWO_2p0_s1', geo=B.slab(0.01), V=1.1),
                                        B.make('aIWO_2p0_s2', geo=B.slab(0.02), V=1.05)])
        T['hk'] = (lambda r: C.hk(*r), [B.make('aIWO_0p7_s1', geo=B.slab(0.03), vb=-3.0),
                                        B.make('aIWO_2p0_s1', geo=B.slab(0.01), vb=-2.0, V=1.0),
                                        B.make('aIWO_2p0_s2', geo=B.slab(0.02), vb=-2.1, V=0.95),
                                        B.make('aIWO_1p0_s1', geo=B.slab(0.04), V=0.5)])
        audit = {}
        for name, kind, dx in (('aIO_2p0_s1', 'undoped', 0.01), ('aIWO_2p0_s1', 'W-doped', 0.02),
                               ('aIWO_2p0_comp_s1', 'compensated', 0.03)):
            gg = B.slab(dx, w=kind != 'undoped')
            audit[name] = {w: B.make(name, geo=gg, kind=kind, w_ry=w) for w in (0.001, 0.005)}
        keys = [(n, w) for n in audit for w in audit[n]]

        def run_audit(recs):
            cells = {n: {} for n in audit}
            for (n, w), r in zip(keys, recs):
                cells[n][w] = r
            out = C.smearing_audit(cells)
            return dict(out, status='PASS' if out['provisional_width_candidate_Ry'] else 'UNRESOLVED')
        T['audit'] = (run_audit, [audit[n][w] for n, w in keys])
        cells, ctrl = series_inputs()
        labs = [(l, i) for l, v in cells.items() for i in range(len(v) if isinstance(v, list) else 1)]

        def run_series(recs):
            cs = {}
            for (l, i), r in zip(labs, recs):
                if isinstance(cells[l], list):
                    cs.setdefault(l, []).append(r)
                else:
                    cs[l] = r
            return C.hn_outcome({'cells': cs, 'controls': ctrl})
        T['series'] = (run_series, [(cells[l][i] if isinstance(cells[l], list) else cells[l]) for l, i in labs])
        cls.T = T

    def test_every_control_every_input(self):
        for name, (fn, recs) in self.T.items():
            good = verdicts(fn(recs))
            self.assertTrue(good & PASSING, (name, good))                  # the genuine set passes
            for i in range(len(recs)):
                bad = list(recs)
                bad[i] = corrupt(recs[i])
                v = verdicts(fn(bad))
                self.assertFalse(v & PASSING, (name, i, v))


def two_k_cell(st, idx, wk, loc_first):
    """Degenerate eigenvalues at two k-points; the excess state at E = 0 is W-localised at one k, extended at the other."""
    ALL = list(range(st.nat))
    sc = SynthCell(st, nks=2, wk=wk)
    for k in (0, 1):
        sc.add(-3.0, ALL, k=k).add(-2.5, ALL, k=k).add(-2.2, ALL, k=k).add(-2.0, idx['interior'], k=k)
        loc = (k == 0) == loc_first
        sc.add(0.0, {idx['W']: 1.0} if loc else ALL, w5d=0.9 if loc else 0.0, k=k).add(1.5, ALL, k=k)
    return sc.build(9.0, smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)


class TestItem2KPairing(unittest.TestCase):
    """Counterexample: schema weights [0.9, 0.1], projection blocks reversed with weights [0.1, 0.9]: rc5 paired them
    with a warning and the class became 0.9 / DONOR-like instead of 0.1 / ECB."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_rc6_k_')
        self.st, self.idx = slab_structure()
        self.good = two_k_cell(self.st, self.idx, [0.9, 0.1], loc_first=True)      # truth: 0.9 localised, 0.1 extended
        self.rev = two_k_cell(self.st, self.idx, [0.1, 0.9], loc_first=False)       # the same blocks in reverse order
        self.sch = os.path.join(self.d, 'data-file-schema.xml')
        self.mp = os.path.join(self.d, 'map.dat')
        synth.write_schema(self.sch, self.good, self.st)
        with open(self.mp, 'w', newline='\n') as f:
            f.write(''.join(f'{i} {a} {s} {w} {l} {m}\n' for i, (a, s, w, l, m) in
                            enumerate(synth.state_map(self.st.species), 1)))

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def cls(self, data, st):
        c = Section1(data, st, name='aIWO_2p0_s1', manifest={'kind': 'W-doped', 'N_ex': 1})
        return cell_result(c, 'xml', qual=qualification(manifest(), pseudos={}))['H-N']

    def test_truth(self):
        prj = os.path.join(self.d, 'p.xml')
        synth.write_atomic_proj(prj, self.good, self.st.species)
        hn = self.cls(*from_xml(self.sch, prj, self.mp))
        self.assertAlmostEqual(hn['f_ext'], 0.1, places=6)
        self.assertEqual(hn['class_if_resolved'], 'ECB')

    def test_counterexample_refused(self):
        prj = os.path.join(self.d, 'p.xml')
        synth.write_atomic_proj(prj, self.rev, self.st.species)                      # coordinates in schema order
        with self.assertRaises(ValueError):
            from_xml(self.sch, prj, self.mp)

    def test_verified_remap_by_coordinates(self):
        prj = os.path.join(self.d, 'p.xml')
        synth.write_atomic_proj(prj, self.rev, self.st.species, kcoords=[[0, 0, 0.1], [0, 0, 0.0]])
        data, st = from_xml(self.sch, prj, self.mp)
        self.assertTrue(any('reordered by verified coordinates' in w for w in data.warnings))
        hn = self.cls(data, st)
        self.assertAlmostEqual(hn['f_ext'], 0.1, places=6)
        self.assertEqual(hn['class_if_resolved'], 'ECB')

    def test_ambiguous_coordinates_refused(self):
        prj = os.path.join(self.d, 'p.xml')
        synth.write_atomic_proj(prj, self.rev, self.st.species, kcoords=[[0, 0, 0.0], [0, 0, 0.0]])
        with self.assertRaises(ValueError):
            from_xml(self.sch, prj, self.mp)


class TestSelfAuditB_OccupationPairing(unittest.TestCase):
    def test_recomputed_vs_qe_occupations_unverified(self):
        st, idx = slab_structure()
        sc, _, _ = B.states(st, idx)
        data = sc.build(9.0, smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        self.assertEqual(Section1(data, st, name='x', manifest={'kind': 'W-doped', 'N_ex': 1}).reasons, [])
        data.f_qe = data.f_qe.copy()
        data.f_qe[0, 0, 4] += 0.01                                       # the run's own occupations disagree
        c = Section1(data, st, name='x', manifest={'kind': 'W-doped', 'N_ex': 1})
        self.assertTrue(any('pairing not verified' in x for x in c.reasons))


class TestItem3AndEntryPoints(unittest.TestCase):
    """(c) one positive end-to-end test per entry point; item 3: nc_readout --xml qualifies a complete valid bundle."""

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_rc6_ep_')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def bundle(self):
        e, ev, w, st = xml_export(os.path.join(self.d, 'b'))
        os.remove(os.path.join(e, 'projwfc_map_final.dat'))                          # the map is the projwfc printout
        sc, st2, idx, _ = __import__('analysis.tests.test_regressions_rc2', fromlist=['x']).thick_donor()
        data = sc.build(9.0, smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0)
        synth.write_projwfc_out(os.path.join(e, 'projwfc_final.out'), data, st2.species)
        return e, ev, w

    def test_nc_readout_xml_qualifies(self):
        e, ev, w = self.bundle()
        cert, code, out = certify(e, ev, w)
        self.assertEqual(code, 0, out)
        self.assertEqual(gate(e, cert)[0], 0)
        js = os.path.join(self.d, 'hn.json')
        r = subprocess.run([sys.executable, '-B', NC, '--proj', os.path.join(e, 'atomic_proj.xml'),
                            '--pout', os.path.join(e, 'projwfc_final.out'), '--nv', '4',
                            '--xml', os.path.join(e, 'data-file-schema.xml'), '--nex', '1', '--name', 'aIWO_2p0_s1',
                            '--certificate', cert, '--hn-json', js], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = qeio.load_json(js)
        self.assertEqual(rec['run_qualification']['reasons'], [], rec['run_qualification'])
        self.assertEqual(rec['H-N']['class'], 'DONOR', rec['H-N']['unresolved_checks'])
        self.assertTrue(any(k.startswith('lineage_') for k in rec['provenance']['files']))
        self.assertIn('final_avg.dat', rec['provenance']['files'])
        self.assertTrue(rec['alignment']['valid'])                                  # same path as 'cell'
        self.assertEqual(C.input_problems(rec), [])

    def test_cli_entry_points_positive(self):
        from analysis.tests.test_regressions_rc2 import cell
        e, ev, w, st = xml_export(os.path.join(self.d, 'x'))
        e5, ev5, w5, _ = xml_export(os.path.join(self.d, 'y'), w_ry=0.005)
        c1, code1, _ = certify(e, ev, w)                                              # certify
        c5, code5, _ = certify(e5, ev5, w5)
        self.assertEqual((code1, code5), (0, 0))
        self.assertEqual(gate(e, c1)[0], 0)                                           # validate-cert
        r1, _ = cell(e, os.path.join(self.d, 'r1'), c1)                               # cell
        r5, _ = cell(e5, os.path.join(self.d, 'r5'), c5)
        self.assertEqual((r1['H-N']['class'], r1['run_qualification']['reasons']), ('DONOR', []))
        from analysis.tests.test_regressions_rc2 import run_cli
        code, out = run_cli(['compare', 'c3', os.path.join(self.d, 'r1.json'), os.path.join(self.d, 'r5.json')])
        self.assertIn('STATUS: PASS', out)                                            # compare

    @unittest.skipUnless(os.path.isdir(os.environ.get('IWO_V1_ROOT', os.path.join(synth.HERE, '..', '..', '..', '..',
                                                                                   '..', 'IWO_PHYSICS_CONSTRAINED_MODEL_V1'))),
                         'crystalline reference outputs not present')
    def test_crystalline_cli(self):
        from analysis.cli import main
        js = os.path.join(self.d, 'cry.json')
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                main(['crystalline', '--json', js])
            except SystemExit as e:
                self.assertIn(e.code, (0, None))
        res = qeio.load_json(js)
        self.assertEqual(res['status'], 'REPRODUCED')
        self.assertTrue(CERT.verify_seal(res))
        self.assertEqual(len(res['provenance']['input_files_sha256']), len(res['input_files']))


if __name__ == '__main__':
    unittest.main()
