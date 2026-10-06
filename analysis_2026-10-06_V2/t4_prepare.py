"""T4 input preparation: DFT values of the thin films (slabL2 ~0.75 nm, slabL1 ~0.51 nm) -> thin_dft.json for
make_v2_model.py. Same procedures as for the 1 and 2 nm films (qe_workflow):
  gap, EA       analyze_slabs.one (scf.out + planar-averaged potential)
  dEg           gap(film) - bulk fundamental gap (collect_results.bulk, bands_path.out)
  dEc           dEc(1 nm) + EA(1 nm) - EA(film): the same-termination electron-affinity route used for the 1 nm value
                (dEc(1 nm) = 0.848 eV, EA(1 nm) from slab1r_final_cpu)
  dm            m*(film) - m*(bulk) (collect_results.slab_mass on bands.out; bulk mass from bands_gamma.out)
  thickness     H-to-H distance of the relaxed film (scf.in is written from the relaxed geometry). For the 1 and 2 nm
                films this distance is 0.930 and 1.962 nm, within 2 % of the labels 0.95 and 1.98 used by the V2 laws.
Usage: python t4_prepare.py   (writes thin_dft.json and prints the table; refuses if a film is not finished)
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
QE = HERE.parent / 'qe_workflow'
R = QE / 'cern_htcondor' / 'results'
sys.path.insert(0, str(QE)); sys.path.insert(0, str(QE / 'cern_htcondor'))
from analyze_slabs import one  # noqa: E402
import collect_results as cr  # noqa: E402

DEC_1NM, REF = 0.848, 'slab1r_final_cpu'


def hh(job):
    inp = (R / job / 'scf.in').read_text()
    cell = np.array([[float(x) for x in l.split()] for l in inp.split('CELL_PARAMETERS angstrom')[1].strip().splitlines()[:3]])
    blk = inp.split('ATOMIC_POSITIONS crystal')[1].split('K_POINTS')[0].strip().splitlines()
    sym = [l.split()[0] for l in blk]
    z = (np.array([[float(x) for x in l.split()[1:4]] for l in blk]) @ cell)[:, 2]
    zH = z[[s == 'H' for s in sym]]
    return (zH.max() - zH.min()) / 10.0, float(np.linalg.norm(cell[0]))


def main():
    b = cr.bulk()
    ref = one(R / REF)
    out, rows = {}, []
    # several copies of each film exist (2026-10-05 19:47Z: faster copies *_relax_v2 and their CPU twins); identical
    # inputs, so the first copy that finished all steps is used
    for film in ('slabL2', 'slabL1'):
        cands = [R / f'{film}_relax_{s}' for s in ('v2', 'v2__cpu', 'gpu')]
        done = [c for c in cands if (c / '.fetched').exists() and (c / 'bands.out').exists() and 'JOB DONE' in (c / 'bands.out').read_text(errors='replace')]
        if not done:
            sys.exit(f'{film}: no finished copy yet (need scf.out, the planar average and bands.out)')
        d = done[0]; job = d.name
        r = one(d)
        if r is None or 'EA_eV' not in r:
            sys.exit(f'{job}: band edges or vacuum level missing')
        t, a = hh(job)
        m = cr.slab_mass(d)
        rec = {'job': job, 'thickness_HH_nm': round(t, 3), 'inplane_a_A': round(a, 4), 'gap_eV': r['gap_eV'],
               'dEg': round(r['gap_eV'] - b['gap_fundamental_eV'], 4), 'EA_eV': float(r['EA_eV']),
               'dEc': round(DEC_1NM + float(ref['EA_eV']) - float(r['EA_eV']), 4),
               'mstar_m0': m, 'dm': round(m - b['mstar_m0'], 4) if m else None,
               'vacuum_plateau_spread_meV': float(r['vacuum_plateau_spread_meV'])}
        rec['dEv'] = round(rec['dEc'] - rec['dEg'], 4)
        rows.append(rec)
        out[f"{round(t, 2):.2f}"] = {'dEc': rec['dEc'], 'dEg': rec['dEg'], 'dm': rec['dm'], 'source': job}
    res = {'bulk': b, 'reference_1nm': {'job': REF, 'EA_eV': float(ref['EA_eV']), 'dEc_eV': DEC_1NM}, 'films': rows}
    (HERE / 'thin_dft.json').write_text(json.dumps(out, indent=1))
    (HERE / 'thin_dft_details.json').write_text(json.dumps(res, indent=1, default=float))
    for r in rows:
        print(r)
    print('thin_dft.json:', out)


if __name__ == '__main__':
    main()
