# DFT protocol: bulk In2O3 reference (stage 1 of the IWO first-principles study)

Written 2026-09-26, before any result of this protocol was known. All acceptance criteria below were fixed in advance.

## 1. Purpose
The TCAD model uses a confinement law and an effective-mass increment taken from published pure-In2O3 slab calculations (Lin et al., ACS Nano 16, 21536 (2022); Si et al., Nano Lett. 21, 500 (2021)). The goal of the DFT study is to replace these proxies with values computed consistently for In2O3 and then for W-doped In2O3 (IWO), using thin slabs minus bulk.

The bulk calculation in this protocol is the common reference for every later step. It is also the test of the computational setup against well-established experimental and theoretical values.

## 2. Method and its sources

| Choice | Setting | Primary reference |
|---|---|---|
| Code | Quantum ESPRESSO 7.5 (pw.x), conda-forge build | P. Giannozzi et al., J. Phys.: Condens. Matter 21, 395502 (2009); P. Giannozzi et al., J. Phys.: Condens. Matter 29, 465901 (2017) |
| Exchange-correlation | PBE generalized-gradient approximation | J. P. Perdew, K. Burke, M. Ernzerhof, Phys. Rev. Lett. 77, 3865 (1996) |
| Electron-ion interaction | Projector augmented-wave method | P. E. Bloechl, Phys. Rev. B 50, 17953 (1994); G. Kresse, D. Joubert, Phys. Rev. B 59, 1758 (1999) |
| Pseudopotential data sets | pslibrary 1.0.0: In.pbe-dn-kjpaw (4d10 5s2 5p1 in valence), O.pbe-n-kjpaw, W.pbe-spn-kjpaw, H.pbe-kjpaw | A. Dal Corso, Comput. Mater. Sci. 95, 337 (2014) |
| Brillouin-zone sampling | Monkhorst-Pack grids | H. J. Monkhorst, J. D. Pack, Phys. Rev. B 13, 5188 (1976) |
| Variable-cell relaxation | BFGS with the variable-cell Lagrangian of pw.x | R. M. Wentzcovitch, Phys. Rev. B 44, 2358 (1991) |
| Crystal structure | Cubic bixbyite, space group Ia-3 (No. 206), a = 10.117 A, 80 atoms per conventional cell; here the equivalent 40-atom body-centred primitive cell (ibrav = 3) | M. Marezio, Acta Crystallogr. 20, 723 (1966) |

Occupations are fixed, because In2O3 is a semiconductor. The charge-density cutoff is ecutrho = 8 x ecutwfc, the usual ratio for PAW data sets.

## 3. Stage 1: convergence tests (running)
- **Plane-wave cutoff:** 50, 60, 71 and 85 Ry at a 3x3x3 k-grid. 71 Ry is the prepared value.
- **k-points:** 2x2x2, 3x3x3 and 4x4x4 Monkhorst-Pack grids at 71 Ry.

Acceptance criteria, fixed in advance. The converged setting is the lowest cost at which a further increase changes:
- the total energy by less than 1 mRy per atom;
- the pressure by less than 1 kbar;
- the Kohn-Sham gap (highest occupied to lowest unoccupied level) by less than 10 meV.

## 4. Stage 2: structural relaxation (after stage 1)
A vc-relax is run at the converged settings, stopping when forces fall below 1e-4 Ry/Bohr and pressure below 0.2 kbar. The relaxed lattice constant is compared with experiment (10.117 A, Marezio 1966). PBE is known to overestimate lattice constants by about 1-2 %; a deviation larger than 3 % would indicate a setup error.

## 5. Stage 3: electronic structure (after stage 2)
- **Band structure:** computed along high-symmetry lines of the bcc Brillouin zone.
- **Band gap:** the PBE gap is expected to be far below the experimental fundamental gap of about 2.9 eV (A. Walsh et al., Phys. Rev. Lett. 100, 167402 (2008); P. D. C. King et al., Phys. Rev. B 79, 205211 (2009)). The absolute PBE gap is therefore not used; only slab-minus-bulk differences enter the model, as in the literature proxies.
- **Effective mass:** the conduction-band effective mass at Gamma comes from a parabolic fit within 0.05 A^-1 of Gamma, and the non-parabolicity is reported. It is compared with experiment: about 0.18-0.21 m0 (M. Feneberg et al., Phys. Rev. B 93, 045203 (2016); M. Stokey et al., J. Appl. Phys. 129, 225102 (2021)).

## 6. Later stages (planned, not started)
- **Slabs:** 1, 2 and 3 nm slabs of In2O3 and IWO, from qe_workflow. Vacuum convergence at 15/25/35 A; vacuum-aligned band edges from the planar-averaged electrostatic potential.
- **W doping:** the W-substituted bulk cells (1.6 % and 3.1 % cation fraction).
- **Deliverables:** the IWO-specific confinement shift dEc(t) and the effective mass m*(t). These replace the pure-In2O3 proxies of the TCAD model only if they pass the same convergence criteria.

## 7. Limitations stated in advance
- The calculations use crystalline periodic cells. The sputtered IWO films are largely amorphous or nanocrystalline, so DFT results describe trends, not the measured films directly.
- PBE underestimates band gaps. Hybrid-functional (HSE06) corrections for absolute gaps are beyond the present compute budget.

## 7a. Deviation record (2026-09-26)
The first attempt used the 80-atom input prepared earlier in qe_workflow/bulk_In2O3. It had never been run or checked, and its atomic positions do not form a correct bixbyite crystal. The failure was detected in the first finished calculation:
- pw.x found 2 symmetry operations instead of 24;
- the total force was 2.86 Ry/Bohr and the pressure 765 kbar;
- the "gap" was negative.

The structure was rebuilt from the crystallographic definition (Ia-3, a = 10.117 A, Marezio 1966 Wyckoff parameters) with ASE 3.29 and spglib 2.7 (build_structure.py). It was verified before use:
- space group 206 with 48/24 operations;
- 80/40 atoms;
- In-O bonds of 2.123, 2.191 and 2.208 A, consistent with the known 2.12-2.23 A.

A second defect followed. Writing spglib's primitive fractional coordinates with ibrav = 3 placed them in Quantum ESPRESSO's different bcc basis, and again gave 2 operations. The inputs now give the lattice vectors explicitly (ibrav = 0, CELL_PARAMETERS), and pw.x reports 24 symmetry operations (18 with fractional translation), as required.

The discarded outputs are kept in defective_structure_runs/. All other prepared qe_workflow inputs (IWO bulk, slabs) come from the same untested generator and must pass the same checks before use.

## 7b. Stage 1 result and decision (2026-09-27, corrected structure, 24 symmetry operations)

| run | E (Ry) | dE/atom vs 85 Ry (mRy) | P (kbar) | KS gap (eV) |
|---|---|---|---|---|
| 50 Ry, 3x3x3 | -7573.24296524 | 3.17 | 84.28 | 1.1897 |
| 60 Ry, 3x3x3 | -7573.32959316 | 1.00 | 89.87 | 1.1894 |
| 71 Ry, 3x3x3 | -7573.35691861 | 0.32 | 96.57 | 1.1897 |
| 85 Ry, 3x3x3 | -7573.36970781 | 0 | 97.04 | 1.1902 |
| 71 Ry, 2x2x2 | -7573.35524852 | +0.044 vs 4x4x4 | 96.27 | 1.1886 |
| 71 Ry, 4x4x4 | -7573.35701116 | reference | 96.61 | 1.1898 |

Cutoff: 71 Ry is the lowest value meeting all three criteria against 85 Ry (0.32 mRy/atom, 0.47 kbar, 0.5 meV); 60 Ry fails the energy (1.00) and pressure (7.2 kbar) criteria.

k-points: 2x2x2 already meets the criteria against 4x4x4 (0.04 mRy/atom, 0.34 kbar, 1.2 meV). The 3x3x3 grid is nevertheless used for stages 2-3. It changes by only 0.002 mRy/atom, 0.04 kbar and 0.1 meV against 4x4x4, costs almost the same, and keeps a margin for the stress in the relaxation. This is a deliberate choice of the more converged grid and is recorded here as a deviation from the lowest-cost rule.

Physical checks: the PBE Kohn-Sham gap is 1.19 eV, the expected PBE underestimate of the ~2.9 eV experimental gap. The pressure at the experimental lattice constant is +97 kbar; with a bulk modulus of roughly 180-190 GPa, this implies a PBE lattice constant about 1.5-2 % above 10.117 A. Stage 2 tests this.

## 7c. Stage 2 result (2026-09-27)
The vc-relax (71 Ry, 3x3x3, BFGS) ran from 2026-09-26T23:06Z to 2026-09-27T00:54Z. BFGS converged in 11 steps (12 SCF cycles).

| quantity | value |
|---|---|
| final enthalpy | -7573.42463802 Ry |
| last relaxation step | P = -0.08 kbar, total force 2.1e-4 Ry/bohr |
| final SCF with G-vectors of the new cell | E = -7573.42780341 Ry, P = +0.41 kbar |

The final-SCF pressure stays within the 1 kbar convergence criterion, so the Pulay-stress effect is negligible.

**Relaxed cell:**
- primitive volume 547.333 A^3, so **a = 10.3061 A**;
- this is **+1.87 %** above experiment (10.117 A, Marezio 1966), inside the expected 1-2 % PBE overestimate and well below the 3 % error threshold;
- Lin et al. (2022, p. 21542) obtained 10.30 A with PBE and norm-conserving pseudopotentials (difference 0.06 %).

**Relaxed bonds:** In-O are 2.215 A (8b) and 2.167 / 2.240 / 2.256 A (24d), all longer than the experimental values by the same ~1.9 % lattice expansion. Space group Ia-3 is preserved (48 operations in the conventional cell).

**Decision:** the relaxed structure is the host for stage 3 and for all CERN structures (`../structures_v2/relaxed_pbe/`).

## 7d. Stage 3a result: conduction band at Gamma (2026-09-27)

**Run.** Non-SCF run `bands_gamma` on the final vc-relax density, using CG diagonalization. The first Davidson attempt aborted; its outputs are kept in `failed_stage3_david/`.
- The cell is the relaxed one: volume 3693.59 bohr^3.
- pw.x keeps the initial alat (16.557 bohr) after vc-relax. The k-point lengths are therefore converted with the alat printed in the output, so the largest |k| is 0.153 1/A.
- Analysis: `analyze_mass.py bands_gamma.out 176`.

| direction | m* parabolic, abs(k) <= 0.05 1/A | Kane fit over abs(k) <= 0.153 1/A: m*, alpha | E(0.153) - CBM |
|---|---|---|---|
| [100] | 0.1588 m0 | 0.1539 m0, 0.63 1/eV | 0.450 eV |
| [110] | 0.1587 m0 | 0.1542 m0, 0.57 1/eV | 0.458 eV |
| [111] | 0.1587 m0 | 0.1542 m0, 0.55 1/eV | 0.460 eV |

**Result.**
- The PBE band-edge mass is **0.159 m0**. It is isotropic within 0.0001 m0, as expected for the cubic Gamma-point s-like CBM.
- It is 7 % below the PBE value of Lin et al. (0.17 m0, p. 21540; ONCV, 140 Ry). It is also below experiment: 0.18-0.21 m0 (Feneberg 2016; Stokey 2021).
- PBE underestimates the gap, and through k.p coupling this lowers the mass. The TCAD model therefore keeps the measured bulk mass, and only slab-minus-bulk increments computed with this same setup are transferred.
- **Direct gap at Gamma: 0.893 eV** (Lin et al.: 0.94 eV). Whether the VBM lies at Gamma follows from the band path, stage 3b (running).

## 7e. Stage 3b result: band path (2026-09-27, finished 17:02Z)

**Run.** Non-SCF bands on the path Gamma-H-N-Gamma-P-H|P-N: 80 k-points, CG diagonalization, 11.3 h on 10 MPI processes. Analysis: `analyze_path.py bands_path.out 176`.

**Band edges.**
- The CBM is at Gamma (8.9672 eV).
- The VBM (8.0785 eV) lies slightly off Gamma on Gamma-H, at k = (0, 0, 0.196) 2pi/a. It is only 4.4 meV above the top valence state at Gamma, so the valence band is very flat near Gamma.

**Gaps.**
- Fundamental gap: **0.889 eV**. Direct gap at Gamma: **0.893 eV**.
- For all slab-minus-bulk differences, the bulk reference gap is 0.889 eV (fundamental). The 4.4 meV difference between the two gaps is below the 10 meV gap criterion.

## 8. Reproduction
Run inside WSL Ubuntu-22.04 with `~/miniforge3/envs/qe/bin/pw.x`.
- `python make_inputs.py` builds the inputs from the prepared conventional cell.
- `nohup bash run_convergence.sh > convergence.log 2>&1 &` runs stage 1.
- Outputs are the `*.out` files in this folder.
