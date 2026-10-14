#!/usr/bin/env python3
"""Post-hoc, read-only audit of ML-built interface cells (A18 verification fixes, SLAB_PROTOCOL.md 9).

usage: python iface_audit.py <results>/<name> [...]     (a directory holding <name>.xyz and <name>_qc.json)

Applies mace_amorph.iface_partition() to the final structure: film cations (and film-origin O) on the OUTER oxide
face, left there by the periodic film melt, against buried exchange across z_if; and every O-O contact below the
QC limit with its region. The origin of each atom follows from the build order (substrate, film, then the
passivation groups) and is used only when no water was removed and the species order checks out. Nothing is
written and no QC verdict changes; the QC files of the Al2O3 cells stay as they are.
"""
import json
import sys
from pathlib import Path

import numpy as np
from ase.io import read

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mace_amorph as ma   # noqa: E402


def build_origin(sym, spec, scat, water_removed):
    """1 = substrate, 2 = film, 0 = passivation, from the build order; None if it cannot be trusted."""
    if water_removed:
        return None
    sub = spec['substrate']
    exp_sub = [scat] * sub[f'n_{scat}'] + ['O'] * sub['n_O']
    exp_film = ['In'] * spec['n_In'] + ['W'] * spec['n_W'] + ['O'] * spec['n_O']
    n1, n2 = len(exp_sub), len(exp_sub) + len(exp_film)
    if list(sym[:n1]) != exp_sub or list(sym[n1:n2]) != exp_film or not set(sym[n2:]) <= {'O', 'H'}:
        return None
    return np.array([1] * n1 + [2] * (n2 - n1) + [0] * (len(sym) - n2))


def main():
    for arg in sys.argv[1:]:
        d = Path(arg)
        name = d.name
        q = json.loads((d / f'{name}_qc.json').read_text())
        spec = q['spec']
        scat = 'Hf' if 'n_Hf' in spec['substrate'] else 'Al'
        atoms = read(d / f'{name}.xyz')
        sym = np.array(atoms.get_chemical_symbols())
        origin = build_origin(sym, spec, scat, q.get('water_removed'))
        res = ma.iface_partition(atoms, scat, origin)
        print(json.dumps({'name': name, 'QC': q.get('QC'), 'QC_n_film_cations_in_oxide': q.get('n_film_cations_in_oxide'),
                          f'QC_n_{scat}_in_film': q.get(f'n_{scat}_in_film'), 'QC_interface_z_A': q.get('interface_z_A'),
                          'water_removed': q.get('water_removed'), 'origin_known': origin is not None, **res}))


if __name__ == '__main__':
    main()
