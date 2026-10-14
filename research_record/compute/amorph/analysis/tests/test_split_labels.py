"""A30 split species labels (In1/In2, O1/O2; label_map_<chain>.tsv): the read-out treats every label as its element.
Synthetic XML pair and D-24 tables written with split labels must give the same structure, geometry hash, composition,
N_ex, accounting and class as the unsplit run; pseudopotential maps compare by element."""
import os
import shutil
import tempfile
import unittest

import numpy as np

from analysis.tests import builders as B
from analysis.tests import synth
from analysis.tests.helpers import manifest, pp_certified, qualification
from analysis.tests.synth import SynthCell, slab_structure
from analysis import certify as CERT
from analysis import compare as C
from analysis import register as R
from analysis.data import from_tables, from_xml
from analysis.geometry import Structure
from analysis.qeio import element_of
from analysis.report import cell_result
from analysis.section1 import Section1


def split_labels(species):
    n = {}
    out = []
    for e in species:
        if e in ('In', 'O'):
            n[e] = n.get(e, 0) + 1
            out.append(f'{e}{1 + (n[e] - 1) % 2}')
        else:
            out.append(e)
    return out


class TestSplitLabels(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='iwo_split_')
        st0, idx = slab_structure()
        self.st0, self.idx = st0, idx
        self.st = Structure(st0.species, st0.pos, st0.cell, split_labels(st0.species))
        ALL = list(range(st0.nat))
        sc = SynthCell(self.st)
        sc.add(-3.0, ALL).add(-2.5, ALL).add(-2.2, ALL).add(-2.0, idx['interior'])
        sc.add(0.0, ALL).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
        names = sorted(set(self.st.labels))
        self.species = [{'name': n, 'pseudo_file': f'{element_of(n)}.pbe-paw.UPF', 'starting_magnetization': 0.0}
                        for n in names]
        self.data0 = sc.build(9.0, smearing='gaussian', degauss_ev=0.001 * R.RY_EV, ef=0.0,
                              settings={'species': self.species})

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_labels_are_split_in_the_inputs(self):
        self.assertEqual({x for x in self.st.labels if x.startswith(('In', 'O'))}, {'In1', 'In2', 'O1', 'O2'})

    def test_xml_pair(self):
        sch, prj, mp = (os.path.join(self.d, n) for n in ('data-file-schema.xml', 'atomic_proj.xml',
                                                            'projwfc_map_final.dat'))
        synth.write_schema(sch, self.data0, self.st)
        synth.write_atomic_proj(prj, self.data0, self.st.species)
        with open(mp, 'w', newline='\n') as f:
            f.write('# map\n' + ''.join(f'{i} {a} {s} {w} {l} {m}\n' for i, (a, s, w, l, m) in
                                       enumerate(synth.state_map(self.st.species, self.st.labels), 1)))
        data, st = from_xml(sch, prj, mp)
        self.assertEqual(st.species, self.st0.species)                    # elements, not labels
        self.assertEqual(st.labels, self.st.labels)
        self.assertEqual(st.geometry_hash(), self.st0.geometry_hash())  # labels never enter the geometry hash
        self.assertEqual(st.composition(), self.st0.composition())
        self.assertEqual(st.formal_excess(), 1)
        man = {'kind': 'W-doped', 'film': {'In': 11, 'W': 1, 'O': 19}, 'substrate': {},
               'passivation': 'dissociated-water', 'N_ex': 1, 'seed': 3}
        self.assertEqual(CERT.check_manifest(man, st), (True, []))
        c = Section1(data, st, name='aIWO_2p0_s1', manifest=man)
        self.assertEqual(c.acc['check'], 'PASS')
        r = cell_result(c, 'xml', qual=qualification(manifest(), pseudos=pp_certified(data)))
        self.assertEqual(r['H-N']['class'], 'DONOR', r['H-N']['unresolved_checks'])
        self.assertEqual(r['structure']['labels'], self.st.labels)
        # W-5d weights sit on the W d orbitals whatever the O/In labels are
        self.assertAlmostEqual(r['H-N']['Delta_W']['value_eV'], 0.5)
        # comparisons map pseudopotentials by element: split and unsplit runs share one element -> file map
        ref = B.make('aIWO_2p0_s1', geo=(self.st0, self.idx), avg=None,
                     settings={'species': [{'name': e, 'pseudo_file': f'{e}.pbe-paw.UPF', 'starting_magnetization': 0.0}
                                           for e in ('H', 'In', 'O', 'W')]})
        self.assertTrue(C.same_pseudos(ref, r))
        self.assertFalse([x for x in C.settings_diff(ref, r, keys=('functional',)) if 'pseudo' in x])

    def test_split_label_with_two_pseudopotentials_is_refused(self):
        r = B.make(geo=B.slab(0.1), avg=None,
                   settings={'species': [{'name': 'O1', 'pseudo_file': 'O.a.UPF'}, {'name': 'O2', 'pseudo_file': 'O.b.UPF'},
                                         {'name': 'In', 'pseudo_file': 'In.UPF'}, {'name': 'W', 'pseudo_file': 'W.UPF'},
                                         {'name': 'H', 'pseudo_file': 'H.UPF'}]})
        self.assertIsNone(C._pseudo_map(r))                              # one element, two pseudopotentials

    def test_d24_tables(self):
        res = synth.run_d24_exporter(self.d, self.data0, self.st)
        self.assertEqual(res.returncode, 0, res.stderr)
        dt, stt = from_tables(self.d)
        self.assertEqual(stt.species, self.st0.species)
        self.assertEqual(dt.species, self.st0.species)
        dx, stx = from_xml(os.path.join(self.d, 'tmp/slab.save/data-file-schema.xml'),
                           os.path.join(self.d, 'tmp/slab.save/atomic_proj.xml'),
                           os.path.join(self.d, 'projwfc_final.out'))
        np.testing.assert_allclose(dt.atom_w, dx.atom_w, atol=6e-7)
        np.testing.assert_allclose(dt.w5d, dx.w5d, atol=6e-7)
        ct = Section1(dt, stt, name='aIWO_2p0_s1', manifest={'kind': 'W-doped', 'N_ex': 1})
        self.assertEqual(ct.acc['check'], 'PASS')


if __name__ == '__main__':
    unittest.main()
