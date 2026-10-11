You are an independent cross-checker. READ-ONLY task: do not create, modify or delete any file; do not use the network; do not run Quantum ESPRESSO, ATLAS or any simulator. Only read files and run short python3 (standard library; numpy only if it is importable) that PRINTS results.

Working directory: the Quantum ESPRESSO results folder `qe_workflow/cern_htcondor/results/` of a W-doped In2O3 (IWO) study (PAW-PBE, QE 7.5). Energies in eV unless stated. Planar-average files `*_avg.dat` have columns z (bohr), planar average (Ry), macroscopic average (Ry); the vacuum level is the mean of column 2 over points within 2.0 angstrom of the cell boundary along z (slab centred in the cell), converted with 1 Ry = 13.605693122994 eV.

IMPORTANT band-count pitfall: the In PAW set has 4d in the valence (5 bands per In) and the W set has 5s5p (4 bands). In a cell where one In is replaced by W, the valence-band top is band n_pure - 1 (one occupied band fewer below the gap than the pure cell), even though the electron count is higher. Confirm band characters from the projwfc.x output (lines `==== e(  N) = ... eV ====` followed by `psi = 0.xxx*[#  k]+...`; the `state #  k: atom  j (El), wfc ... (l=.. m=..)` header maps states to atoms/orbitals) before naming any band.

Compute and report, with the exact file and line pattern you used for each number:

A. `iwo_slab2_final_cpu/` (2 nm IWO slab, one W; pure twin `slab2r_pdos_cpu/`).
  1. Number of electrons and atoms (scf.out), smearing type and degauss (scf.in), Fermi energy (scf.out).
  2. At the first k-point (Gamma) of the projwfc output: for bands n_pure-3 .. n_pure+4 (n_pure = half the electron count of the PURE slab, from slab2r_pdos_cpu/scf.out), the energy, the summed W d weight, In s weight, O p weight. Name: valence-band top, host conduction-band bottom, W-5d-derived band(s).
  3. Gap (VB top to host CB bottom) at Gamma; E_F minus host CB bottom; W-derived band minus host CB bottom; E_vac; EA = E_vac - host CB bottom; IP = E_vac - VB top. Same quantities for the pure twin (VB top = band n_pure, CB = n_pure+1, its E_vac).
  4. Electron filling: using the k-point weights and eigenvalues printed in iwo_slab2_final_cpu/scf.out (if all k-points are printed) and the smearing from scf.in, the number of electrons (spin included) in the host CB bottom band and in each band above it up to E_F + 0.5 eV. State the assumptions.

B. `slabL1_relax_v2/` and `slabL2_relax_v2/` (pure In2O3 slabs, about 0.51 and 0.75 nm), plus `slab1r_final_cpu/` and `slab2_relax_c2/` as references.
  1. HOMO/LUMO from the last `highest occupied, lowest unoccupied level` line of scf.out; gap; E_vac; EA; IP.
  2. Film thickness = max-min z of the H atoms in scf.in (CELL_PARAMETERS angstrom, ATOMIC_POSITIONS crystal); in-plane lattice length.
  3. In-plane conduction-band mass from bands.out: band index n_occ+1 (n_occ = electrons/2), the first 11 k-points (Gamma then along one in-plane direction), k in 1/angstrom = (printed k in units 2pi/alat) * 2pi/alat_angstrom; fit E - E(Gamma) = (hbar^2/2m) k^2 over |k| <= 0.0501 1/angstrom; hbar^2/(2 m0) = 3.80998212 eV angstrom^2.
  4. Energy of the next empty level above the CBM at Gamma (band n_occ+2 minus n_occ+1), from scf.out or bands.out.
  5. From projwfc_*.out of slabL1/slabL2: share of the projected weight of the VBM (band n_occ) and CBM (band n_occ+1), averaged over the listed k-points, that sits on H atoms plus O atoms within 1.15 angstrom of an H, compared with the number fraction of those atoms. Is either band edge a surface (OH) state?

C. Bulk reference: `../../bulk_In2O3_protocol/bands_path.out` fundamental gap (band 177 minimum minus band 176 maximum over all k-points) and `../../bulk_In2O3_protocol/bands_gamma.out` CB mass (same fit as B3, band 177).

Finish with one compact table of all numbers and a list of anything you could not determine, saying why. Do not speculate beyond the files.
