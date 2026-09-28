#!/usr/bin/env python3
"""Build the (UNEXECUTED) Quantum ESPRESSO workflow for the xW x thickness matrix.

Writes qe_workflow/<case>/pw.<step>.in files with a README. Quantum ESPRESSO is NOT installed on this
machine (no pw.x on Windows or in WSL; apt install needs an interactive sudo password), so nothing here
was run; the thickness laws in config/iwo_material_model.yaml remain labelled DFT_PURE_IN2O3_PROXY
until these inputs are executed and their results replace the proxies.

Structures: bixbyite In2O3 (Ia-3, No. 206), a = 10.117 A, In1 8b (1/4,1/4,1/4), In2 24d (u,0,1/4) with
u = -0.0338 (0.4662), O 48e (0.3905, 0.1547, 0.3821) -- Marezio 1966 Wyckoff parameters (METADATA_REQUIRES_VERIFICATION
against the original table; verify the generated 80-atom cell stoichiometry In32O48 and nearest-neighbour distances ~2.2 A).
W substitution: one W on an In2 (24d) site in the 80-atom conventional cell gives xW = 1/32 = 3.1 cation %; in a 1x1x2
supercell (160 atoms) one W gives 1.6 %; two W give 3.1 % -- brackets the ~2 % target (definition of "2 % W" undetermined).
Slabs: (001) slabs cut from the conventional cell, O-terminated, H-passivated top/bottom (one H per surface O, as in
Lin2022/Si2021), 25 A vacuum, dipole correction; thicknesses ~1.0, ~2.0, ~3.5 nm (1, 2, 3.5 conventional-cell units).
Settings follow the supplied papers: PBE, PAW/ONCV, ecutwfc 71 Ry / ecutrho 639 Ry (Januar2026) or 140 Ry ONCV (Lin2022),
k-grid 6x6x6 (bulk primitive) / 3x3x1 (slabs), forces < 1e-3 Ry/Bohr. Convergence tests listed in the README.
Quantities to extract: Eg (PBE, relative shifts only), Ec/Ev shifts vs bulk (vacuum-aligned via the planar-averaged
potential; pp.x + average.x), effective mass (band fit near Gamma), DOS/PDOS (W-5d near CBM), dielectric tensor (ph.x /
DFPT, bulk only), V_O formation energy and charge-transition levels (charged supercells, Makov-Payne correction),
W substitution energy. A crystalline periodic supercell is NOT the amorphous sputtered film: results are trends.
"""
from pathlib import Path
import numpy as np
from ase.spacegroup import crystal
from ase.build import surface, add_vacuum
from ase.io import write
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / 'qe_workflow'

PSEUDO = {'In': 'In.pbe-dn-kjpaw_psl.1.0.0.UPF', 'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF', 'W': 'W.pbe-spn-kjpaw_psl.1.0.0.UPF', 'H': 'H.pbe-kjpaw_psl.1.0.0.UPF'}
BASE = {'control': {'calculation': 'vc-relax', 'prefix': 'in2o3', 'pseudo_dir': './pseudo', 'outdir': './tmp', 'tprnfor': True, 'tstress': True, 'forc_conv_thr': 1e-3, 'etot_conv_thr': 1e-5},
        'system': {'ecutwfc': 71, 'ecutrho': 639, 'occupations': 'fixed', 'nbnd': None},
        'electrons': {'conv_thr': 1e-9, 'mixing_beta': 0.4}, 'ions': {}, 'cell': {'press_conv_thr': 0.5}}

def bulk():
    return crystal(['In', 'In', 'O'], basis=[(0.25, 0.25, 0.25), (0.4662, 0.0, 0.25), (0.3905, 0.1547, 0.3821)], spacegroup=206, cellpar=[10.117, 10.117, 10.117, 90, 90, 90])

def with_w(atoms, n_w):
    a = atoms.copy(); idx = [i for i, s in enumerate(a.get_chemical_symbols()) if s == 'In'][:n_w]
    for i in idx: a[i].symbol = 'W'
    return a

def slab(atoms, layers, vac=25.0):
    s = surface(atoms, (0, 0, 1), layers, vacuum=vac / 2); s.center(vacuum=vac / 2, axis=2)
    # H passivation of surface O (one H per O within 1.2 A of either surface), as in Lin2022 / Si2021
    z = s.positions[:, 2]; zmin, zmax = z[[i for i, e in enumerate(s.get_chemical_symbols()) if e != 'H']].min(), z.max()
    add = []
    for i, (e, p) in enumerate(zip(s.get_chemical_symbols(), s.positions)):
        if e == 'O' and (p[2] - zmin < 1.2 or zmax - p[2] < 1.2): add.append(p + np.array([0, 0, 0.98 if zmax - p[2] < 1.2 else -0.98]))
    from ase import Atoms
    if add: s += Atoms('H' * len(add), positions=add)
    return s

def write_case(name, atoms, kpts, calc='vc-relax', extra=None, notes=''):
    d = OUT / name; d.mkdir(parents=True, exist_ok=True)
    inp = {k: dict(v) for k, v in BASE.items()}; inp['control']['calculation'] = calc; inp['control']['prefix'] = name
    if extra:
        for k, v in extra.items(): inp[k].update(v)
    inp['system'] = {k: v for k, v in inp['system'].items() if v is not None}
    write(d / f'pw.{calc}.in', atoms, format='espresso-in', input_data=inp, pseudopotentials=PSEUDO, kpts=kpts)
    (d / 'NOTES.txt').write_text(f'{name}: {len(atoms)} atoms, formula {atoms.get_chemical_formula()}\n{notes}\nNOT EXECUTED (no QE on this machine).\n')
    return len(atoms), atoms.get_chemical_formula()

def main():
    OUT.mkdir(exist_ok=True); b = bulk(); log = []
    log.append(('bulk_In2O3', *write_case('bulk_In2O3', b, (4, 4, 4), notes='80-atom conventional cell; use the 40-atom primitive (ibrav=3) with 6x6x6 for production; follow with bands (m*), DFPT (eps), pp.x for CBM/VBM')))
    log.append(('bulk_IWO_1W_3p1pct', *write_case('bulk_IWO_1W_3p1pct', with_w(b, 1), (4, 4, 4), extra={'system': {'occupations': 'smearing', 'smearing': 'mv', 'degauss': 0.01, 'nspin': 1}}, notes='1 W on an In site: xW = 1/32 cation = 3.1 %; W6+ donates 3 e -> metallic occupation; compare with charged-cell/compensated variants')))
    sc = b.repeat((1, 1, 2)); log.append(('bulk_IWO_1W_1p6pct_112', *write_case('bulk_IWO_1W_1p6pct_112', with_w(sc, 1), (4, 4, 2), extra={'system': {'occupations': 'smearing', 'smearing': 'mv', 'degauss': 0.01}}, notes='1 W in a 160-atom 1x1x2 cell: 1.6 %; two W -> 3.1 %. W-site configuration sampling (8b vs 24d, W-W distance) required')))
    for layers, tag in [(1, 'slab_1p0nm'), (2, 'slab_2p0nm'), (3, 'slab_3p0nm')]:
        s = slab(b, layers); log.append((tag + '_In2O3', *write_case(tag + '_In2O3', s, (3, 3, 1), calc='relax', extra={'system': {'occupations': 'smearing', 'smearing': 'mv', 'degauss': 0.005, 'nspin': 1}, 'control': {'tefield': True, 'dipfield': True}}, notes='(001) H-passivated slab, 25 A vacuum, dipole correction; extract Ec/Ev vs vacuum (pp.x plot_num=11, average.x), Eg shift vs bulk, m* from bands along Gamma-X')))
        log.append((tag + '_IWO_1W', *write_case(tag + '_IWO_1W', with_w(s, 1), (3, 3, 1), calc='relax', extra={'system': {'occupations': 'smearing', 'smearing': 'mv', 'degauss': 0.005}, 'control': {'tefield': True, 'dipfield': True}}, notes='same slab with one W (xW depends on layer count; report cation %)')))
    readme = ['# Quantum ESPRESSO workflow (NOT EXECUTED)', '', 'pw.x is not available on this machine. These inputs define the matrix xW = {0, ~1.6-3.1 %} x thickness {bulk, ~1, ~2, ~3 nm}.', '',
              '| case | atoms | formula |', '|---|---|---|'] + [f'| {n} | {a} | {f} |' for n, a, f in log] + ['',
              '## Convergence tests required before any number replaces a proxy', '- ecutwfc 50/71/90 Ry (PAW) or 100/140 Ry (ONCV); k-grid 4/6/8 (bulk), 3x3x1 vs 5x5x1 (slabs); vacuum 15/25/35 A; slab thickness series; W configuration (8b vs 24d, W-W separation); relaxation force < 1e-3 Ry/Bohr.',
              '## Extraction', '- Eg: PBE gaps are underestimated (bulk ~0.9 eV vs 2.9-3.2 exp); use ONLY slab-minus-bulk shifts (dEg_QC). For absolute values use HSE06 on the relaxed bulk.',
              '- dEc/dEv: vacuum-aligned CBM/VBM from the planar-averaged electrostatic potential (pp.x plot_num=11 -> average.x); chi = Evac - Ec directly.',
              '- m*: parabolic fit of the lowest conduction band within 0.05 A^-1 of Gamma (bands.x); report nonparabolicity.',
              '- DOS/PDOS: projwfc.x; W-5d weight at the CBM.', '- eps: ph.x DFPT (bulk only; eps_inf and eps_0 from the Born charges/phonons).',
              '- V_O: neutral and +2 vacancy supercells (In2O3 and IWO), formation energy vs O chemical potential, transition levels with Makov-Payne/FNV correction; W substitution energy from the same references.',
              '## Caveat', 'Crystalline periodic supercells approximate the sputtered, largely amorphous IWO film only in trend; results are proxies until compared with the measured devices.']
    (OUT / 'README.md').write_text('\n'.join(readme) + '\n'); print('\n'.join(readme[:14]))

if __name__ == '__main__': main()
