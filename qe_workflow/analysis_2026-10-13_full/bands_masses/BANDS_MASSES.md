# Band structures, effective masses, gaps vs thickness and TCAD-ready parameters (crystalline DFT only)

Analysis of 2026-10-14, read-only, re-derived from the raw Quantum ESPRESSO outputs by the scripts in this folder (`b01_masses.py`, `b02_band_figures.py`, `b03_gaps_laws.py`, `b04_tcad.py`, `b05_holes.py`, `make_bm_report.py`; `bash run_all.sh`). Machine-readable results: `out/b01_masses.json`, `out/b03_gaps_laws.json`, `out/b04_tcad.json` (each value carries its raw file:line source; holes: `out/b05_holes.json`). Figures: `figures/BM1`-`BM9` (PNG 300 dpi + PDF). Hole masses: Section 8. Paths below are relative to `qe_workflow/`.

Scope and sight rule: crystalline cells only (bulk In2O3, H-terminated (001) slabs 0.51 / 0.75 / 1 / 2 nm, W-doped bulk 8b / 24d, W24d slabs 1 / 2 nm, HSE06 bulk / 1 nm, the H-L parent In32O48 cell as a dispersion and DOS check). No amorphous output was opened. No DFT was run, nothing was submitted, nothing was committed.

Labels: COMPUTED (a DFT number), FITTED (a law through COMPUTED points), ESTIMATED (COMPUTED data plus a stated model), CALCULATED (formula applied to COMPUTED or LITERATURE inputs), ASSUMED, LITERATURE, INFERRED. All DFT numbers are PBE (PAW, pslibrary 1.0.0, 71/568 Ry) unless marked HSE06 (SG15 NC, 80 Ry, PBE geometries). kT = 25.85 meV (300 K).

## 1. Band structures

| System | Band data | Figure | k-path status |
|---|---|---|---|
| bulk In2O3 (40-atom primitive, a = 10.306 A) | `bulk_In2O3_protocol/bands_path.out` (80 k, G-H-N-G-P-H\|P-N) + `bulk_In2O3_protocol/bands_gamma.out` (Gamma + 10 points along [100], [110], [111], abs(k) <= 0.153 1/A) | BM1 | complete |
| slab 0.51 nm (H-H 0.4612 nm, `slabL1_relax_v2`) | `cern_htcondor/results/slabL1_relax_v2/bands.out` (Gamma + 10 points along [100] and [110], abs(k) <= 0.15 1/A) + 3x3x1 SCF grid | BM2 | in-plane lines to 0.15 1/A only (half of Gamma-X); no full 2-D path |
| slab 0.75 nm (H-H 0.6953 nm, `slabL2_relax_v2`) | `cern_htcondor/results/slabL2_relax_v2/bands.out` (Gamma + 10 points along [100] and [110], abs(k) <= 0.15 1/A) + 3x3x1 SCF grid | BM2 | in-plane lines to 0.15 1/A only (half of Gamma-X); no full 2-D path |
| slab 1.0 nm (H-H 0.9303 nm, `slab1r_final_cpu`) | `cern_htcondor/results/slab1r_final_cpu/bands.out` (Gamma + 10 points along [100] and [110], abs(k) <= 0.15 1/A) + 3x3x1 SCF grid | BM2 | in-plane lines to 0.15 1/A only (half of Gamma-X); no full 2-D path |
| slab 2.0 nm (H-H 1.9623 nm, `slab2_relax_c2`) | `cern_htcondor/results/slab2_relax_c2/bands.out` (Gamma + 10 points along [100] and [110], abs(k) <= 0.15 1/A) + 3x3x1 SCF grid | BM2 | in-plane lines to 0.15 1/A only (half of Gamma-X); no full 2-D path |
| W bulk 8b (80 atoms, In31WO48) | `cern_htcondor/results/iwo_W8b/bands.out` (Gamma-star, CG) + scf_k4 | BM3 | Gamma-star only; no zone-boundary path |
| W bulk 24d (80 atoms, In31WO48) | `cern_htcondor/results/iwo_W24d/bands.out` (Gamma-star, CG) + scf_k4 | BM3 | Gamma-star only; no zone-boundary path |
| W slabs 1 / 2 nm (W on 24d) | SCF 3x3x1 grid only (`iwo_slab1_final_cpu/scf.out`, `iwo_slab2_final_cpu/scf.out`) | BM4a | **k-path run missing**: the 1 nm bands step stopped (rc 161: factorisation of the overlap matrix failed in cdiaghg, Davidson; cause unresolved); no 2 nm bands step |
| HSE06 bulk (q1, q3) and 1 nm slab | SCF grids only (bulk k3, 4 k; slab 3x3x1, 4 k) | BM4b,c | **k-path run missing** |
| H-L cells (In32O48, In31WO48, vacancy cells) | SCF k3 / k4 grids only | - | **no band run**; the pristine In32O48 grid is used here only as a dispersion and valence-DOS check |

**BM1** (bulk). (a) Band structure along G-H-N-G-P-H|P-N, E - E_VBM. Open circle: VBM at 0.2 G-H (abs(k) = 0.1219 1/A, bulk_In2O3_protocol/bands_path.out:931); filled circle: CBM at Gamma (bulk_In2O3_protocol/bands_path.out:850); arrow: fundamental gap 0.8887 eV (direct at Gamma 0.8931 eV). Black: valence bands, red: conduction bands. (b) CB near Gamma along the three directions with the Kane fit (black, m = 0.1539 m0, alpha = 0.63 1/eV) and the 3-point parabola (dashed). (c) The three VBs degenerate at Gamma: band 176 rises along [100] to the VBM 4.4 meV above VB(Gamma) (open circle), i.e. a camel back. COMPUTED.

**BM2** (relaxed slabs (a) 0.51, (b) 0.75, (c) 1.0, (d) 2.0 nm). Lines: bands.out along [110] (left, plotted at -abs(k)) and [100] (right); open symbols: 3x3x1 SCF-grid eigenvalues (circles on the x / diagonal axes, squares on the y axis, plotted at their abs(k)). Open circle at Gamma: VB(Gamma); blue open circle in (a): the off-Gamma VBM of the 0.51 nm slab on the SCF grid (1.3 meV above VB(Gamma)); filled circle: CBM; arrow: gap. E - E_VBM. COMPUTED.

**BM3** (W bulk (a) 8b, (b) 24d). Gamma-star bands, E - E_F (dotted). Black: valence bands (top = band 351 = n_pure - 1), red: host CB (band 352 = n_pure, filled circle at Gamma), green: bands above (W-5d-rich level and folded host CB). Dashed grey: CB of pure bulk from bands_gamma.out shifted to the host-CB minimum. COMPUTED.

**BM4** (systems with SCF-grid eigenvalues only). (a) CB dispersion E_CB(k) - E_CB(Gamma) of the W slabs (circles, host CB band n_pure) and the pure twins (crosses, band n_pure + 1) at the 3x3x1 grid points. (b) Bulk: VB top and CB relative to VB(Gamma) for PAW-PBE, NC-PBE, HSE06 q1 and q3 at the k3 grid. (c) 1 nm slab: PAW-PBE, NC-PBE, HSE06. The masses derived from these points are ESTIMATED (Section 2.6), not band-edge fits.

## 2. Effective masses

Method (b01_masses.py). For one band along one line through the extremum: anchored parabola E - E0 = hbar^2 k^2/2m over the first n points (windows n = 2, 3, 4, 6, 10, i.e. abs(k) up to 0.031 / 0.046 / 0.061 / 0.092 / 0.153 1/A), the free-intercept parabola (the deck basis is the 3-point window = "4-point incl. Gamma"), a quartic fit (k^2 + k^4) over all points, and the Kane form hbar^2 k^2/2m = E(1 + alpha E) over 4, 6 and 10 points. The band-edge mass is the 10-point Kane value. The print precision of the eigenvalues (0.1 meV) is propagated into every anchored mass (sigma_round in the JSON). DOS mass (bulk) = geometric mean, conductivity mass = harmonic mean of the three directional band-edge masses. Slabs: in-plane tensor with principal axes x, y (point group D2h for 8 symmetry operations, C2v for 4), m_y from 1/m_[110] = (1/m_x + 1/m_y)/2, 2-D DOS mass sqrt(m_x m_y), conductivity mass 2/(1/m_x + 1/m_y) = m_[110].

### 2.1 Bulk electrons (COMPUTED)

| Direction | n=2 | n=3 | n=4 | n=6 | n=10 | free intercept n=3 | quartic | Kane m (10 pt) | Kane alpha (1/eV) |
|---|---|---|---|---|---|---|---|---|---|
| [100] | 0.156 | 0.1583 | 0.1612 | 0.1687 | 0.1887 | 0.1588 | 0.1608 | 0.1539 | 0.63 |
| [110] | 0.1556 | 0.158 | 0.161 | 0.1678 | 0.1861 | 0.1587 | 0.1601 | 0.1542 | 0.57 |
| [111] | 0.1559 | 0.158 | 0.1607 | 0.1674 | 0.1852 | 0.1587 | 0.1599 | 0.1542 | 0.551 |

Window energies: n = 2 / 3 / 4 / 6 / 10 reach E - E_CBM = 22.8, 50.4, 87.6, 186.2, 450.3 meV ([100]). Source: `bulk_In2O3_protocol/bands_gamma.out:656 .. bulk_In2O3_protocol/bands_gamma.out:926`.
- Band-edge mass 0.1541 m0 (DOS = conductivity mass; direction spread 0.19 %, isotropic as required by cubic symmetry). The parabolic mass grows with the window: 0.156 (25 meV) to 0.1887 m0 (450 meV); the deck basis (3-point free intercept) is 0.1588 m0, 3 % above the band edge.
- Kane alpha 0.584 1/eV (direction range 0.551-0.63).
- Checks: the coarser path (G-H first point, abs(k) = 0.0407 1/A) gives 39.8 meV against 39.93 meV from the Kane fit (bulk_In2O3_protocol/bands_path.out:877); the independent H-L parent cell In32O48 (80 atoms, QE 7.3.1 GPU) gives CB 448.4 meV and VB +3.6 meV at 0.1524 1/A along [001] (analysis_2026-10-13_full/raw_cern/hl/vac/In32O48/scf.out:818) against 450.3 / +3.5 meV at 0.15282 1/A in bands_gamma.out.
- Consequence of alpha (CALCULATED from the COMPUTED m and alpha): the isotropic Kane cyclotron / zero-temperature conductivity (optical) mass m(1 + 2 alpha E_F) = 0.228 m0 at 1e20 cm^-3 (E_F - E_C = 0.41 eV) and 0.394 m0 at 1e21 cm^-3 (1.33 eV); Feneberg et al. 2016 report 0.4 m0 at 1e21 cm^-3 from the plasma frequency.

### 2.2 Bulk holes: no meaningful single-band hole mass

- The top valence band is 3-fold degenerate at Gamma (bands 174-176); the next band lies 217.6 meV below. Along [100] one member rises (camel back) to the VBM at abs(k) = 0.1219 1/A, 4.44 meV above VB(Gamma) (six equivalent pockets on <100>; bands_path.out gives 4.4 meV at 0.2 G-H). The whole top band spans 169.7 meV along the path.
- Longitudinal mass at the VBM (parabola through 5 points of bands_gamma [100]): 4.026 +- 0.14 m0 (print-precision error). The transverse masses at the VBM are not computed (no k-points off the line).
- Band masses at Gamma (anchored, n = 4; negative = band rises): band 174: [100] 3.22, [110] 4.3, [111] 7.89; band 175: [100] 7.97, [110] 16.76, [111] 7.89; band 176: [100] -6.93, [110] -45.02, [111] 196.76 m0.
- Verdict: top VB 3-fold degenerate at Gamma; global VBM 4.4 meV above VB(Gamma) (off the fit point); [100]: band rises away from Gamma in the 2-4 point window (camel back); [110]: band rises away from Gamma in the 2-4 point window (camel back); [111]: band rises away from Gamma in the 2-4 point window (camel back). A single band-edge hole mass is therefore not a meaningful bulk parameter in PBE; band-resolved curvature masses and the DOS mass are given as numbers in Section 8.
- What is meaningful is the valence-band effective density of states from a Boltzmann sum over the computed bands (COMPUTED on the stated coarse grids, each referenced to its own grid maximum): Nv(300 K) = 1.93e+21 cm^-3 (80-atom cell, k4, 14 k), 1.92e+21 (primitive k4, experimental lattice), 2.36e+21 (80-atom k3), 2.67e+21 (primitive k3). Referenced instead to the off-Gamma VBM: 1.87e+21 (80-atom k4), 1.99e+21 (80-atom k3), 2.25e+21 (primitive k3). Observed variation: 1.92e+21-2.67e+21 cm^-3 across the four grids (own-maximum reference), 80-atom k3 -> k4 -18 %; convergence error unestablished. DOS-equivalent hole mass about 18.1 m0 (a temperature-dependent representation of the same sum, not a band mass). On the same k3 grid HSE06 gives 0.89 (q1) and 0.6 (q3) times the NC-PBE Nv.

### 2.3 Slab electrons (COMPUTED)

| Slab | t_HH (nm) | Kane m_[100] | Kane m_[110] | alpha_[100] / alpha_[110] (1/eV) | m_x / m_y | 2-D DOS = cond. mass | deck-basis 3-pt [100] | anchored n=2 ... n=10 [100] |
|---|---|---|---|---|---|---|---|---|
| 0.51 | 0.4612 | 0.4256 | 0.4423 | 0.252 / 0.224 | 0.4256 / 0.4604 | 0.4426 | 0.4282 | 0.4308 ... 0.4406 |
| 0.75 | 0.6953 | 0.3329 | 0.3365 | 0.326 / 0.296 | 0.3329 / 0.3402 | 0.3365 | 0.3348 | 0.3348 ... 0.3528 |
| 1.0 | 0.9303 | 0.2788 | 0.2793 | 0.381 / 0.349 | 0.2788 / 0.2798 | 0.2793 | 0.2811 | 0.2819 ... 0.302 |
| 2.0 | 1.9623 | 0.2023 | 0.2026 | 0.496 / 0.449 | 0.2023 / 0.2029 | 0.2026 | 0.2064 | 0.2047 ... 0.2307 |
| 1.0 GPU twin | 0.9303 | 0.2785 | 0.2794 | 0.382 / 0.349 | 0.2785 / 0.2803 | 0.2794 | 0.2811 | 0.2791 ... 0.3017 |
| 1.0 unrelaxed v15 | 0.9875 | 0.2375 | 0.2375 | 0.482 / 0.445 | 0.2375 / 0.2375 | 0.2375 | 0.2411 | 0.238 ... 0.2659 |
| 1.0 unrelaxed v25 | 0.9875 | 0.2377 | 0.2376 | 0.48 / 0.443 | 0.2377 / 0.2375 | 0.2376 | 0.2419 | 0.2396 ... 0.2659 |
| 1.0 unrelaxed v35 | 0.9875 | 0.2377 | 0.2376 | 0.48 / 0.443 | 0.2377 / 0.2375 | 0.2376 | 0.2411 | 0.2396 ... 0.2659 |

Sources: the bands.out of each job (lines in out/b01_masses.json, field `src`). Checks: GPU (QE 7.3.1) and CPU (QE 7.5) runs of the same 1 nm geometry agree within 0.0006 m0; the unrelaxed 1 nm slab is converged in vacuum (15 / 25 / 35 A: identical to 0.0002 m0); relaxation raises the 1 nm mass from 0.2376 to 0.2793 m0 (+18 %). The 4-point values reproduce ../out/f05 (check_vs_f05 in the JSON). The 0.51 nm cell is rectangular (10.70 x 10.02 A): m_y/m_x = 1.082; all other slabs are isotropic in-plane within 2 %.

### 2.4 Slab holes

| Slab | VBM location | next VB at Gamma (meV) | anchored m_h [100], n = 2/3/4/6/10 | anchored m_h [110], n = 2/3/4/6/10 | passes local fit screens? | reasons | Nv2D (cm^-2) / quasi-3D (cm^-3) |
|---|---|---|---|---|---|---|---|
| 0.51 | SCF grid k [0.1958, 0.0, 0.0] 1/A | 72.7 | 1.14 / 1.14 / 1.14 / 1.15 / 2.17 | 1.99 / 2.04 / 2.07 / 2.16 / 2.47 | no | global VBM 1.3 meV above VB(Gamma) (off the fit point) | 2.03e+14 / 4.39e+21 |
| 0.75 | Gamma | 29.1 | 6.78 / 5.94 / 5.86 / 6.05 / 6.51 | 3.39 / 3.3 / 3.33 / 3.54 / 4.55 | yes | - | 1.35e+14 / 1.95e+21 |
| 1.0 | Gamma | 3.3 | 36.5 / 38.17 / 29.75 / 20.24 / 10.91 | 8.57 / 8.56 / 8.57 / 8.81 / 9.3 | no | next band only 3.3 meV below at Gamma (< kT); [100]: 3-point mass 38.1734 has a print-rounding error 8.5912 (> 10 %) | 2.67e+14 / 2.87e+21 |
| 2.0 | Gamma | 9.3 | 2.64 / 2.65 / 2.64 / 4.57 / 20.77 | 5.82 / 6.3 / 6.24 / 6.64 / 7.33 | no | next band only 9.3 meV below at Gamma (< kT) | 3.51e+14 / 1.79e+21 |

Local fit screens (written before the slab values were read): global VBM at Gamma within 1 meV (over the sampled k-points only); next band at least kT below; the 2-, 3- and 4-point masses within +-20 %; monotonic fall over 4 points; print-rounding error of the 3-point mass below 10 % (correlated rounding of E(Gamma) included). Only the 0.75 nm slab passes, which establishes a resolved local curvature of its OH-derived top valence band (75 % on OH oxygens) under the present periodic boundary conditions: m_h = 5.94 m0 [100] and 3.3 m0 [110] (3-point). It does not establish single-band hole transport at 300 K: the next band is 29.1 meV lower (Boltzmann factor 0.324 before its DOS), and the uncorrected polar field of this slab can alter its electronic structure, not only the vacuum reference. At 0.51 nm the Gamma masses are resolved (1.14 [100], 2.0 [110] m0) but a second maximum on the SCF grid lies 1.3 meV higher (multi-valley). At 1 and 2 nm the top two bands are within 3.3 and 9.3 meV: degenerate on the kT scale. Nv from a 3x3x1 grid (4 k) is COMPUTED on that grid; its convergence error is unestablished.

### 2.5 Effect of W (COMPUTED in bulk; ESTIMATED in slabs)

| Cell | host-CB band | m (Kane, [100] / [110] / [111]) | alpha (1/eV) | E_F - E_C(Gamma) (eV) | VB top to host CB at Gamma (eV) | hole mass |
|---|---|---|---|---|---|---|
| bulk 8b | 352 | 0.1622 / 0.1622 / 0.1615 | 0.642 / 0.598 / 0.612 | 1.7126 | 0.8939 | not meaningful (global VBM 1.5 meV above VB(Gamma) (off the fit point); next band only 0.0 meV below at Gamma (< kT)) |
| bulk 24d | 352 | 0.1629 / 0.1622 / 0.161 | 0.658 / 0.59 / 0.577 | 1.7633 | 0.8616 | not meaningful (next band only 19.6 meV below at Gamma (< kT)) |
| pure bulk (reference) | 177 | 0.1539 / 0.1542 / 0.1542 | 0.63 / 0.57 / 0.551 | - | 0.8931 | not meaningful |

- Band-filling check (8b, CALCULATED): with the pure-bulk Kane m and alpha, n = 2.41e+21 - 2.74e+21 cm^-3 in the host CB gives E_F - E_C = 1.978-2.09 eV (parabolic: 4.262-4.64 eV) against DFT 1.7126 eV: the Kane form removes most of the parabolic error but still overestimates E_F by 15-22 %.
- Band-filling check (24d, CALCULATED): with the pure-bulk Kane m and alpha, n = 2.48e+21 - 2.74e+21 cm^-3 in the host CB gives E_F - E_C = 2.001-2.09 eV (parabolic: 4.34-4.64 eV) against DFT 1.7633 eV: the Kane form removes most of the parabolic error but still overestimates E_F by 13-19 %.
- W slab 1 nm (ESTIMATED from the 3x3x1 grid, Section 2.6 method): host-CB band-edge mass 0.2974 m0 (variants 0.2974-0.3013) against the pure twin 0.2793 m0; the pure/W dispersion ratio at the grid points is 1.072, 1.07, 1.073.
- W slab 2 nm (ESTIMATED from the 3x3x1 grid, Section 2.6 method): host-CB band-edge mass 0.2177 m0 (variants 0.2177-0.2212) against the pure twin 0.2026 m0; the pure/W dispersion ratio at the grid points is 1.08, 1.077, 1.08.
- Reading: W at 3.1 % (bulk) raises the host-CB band-edge mass by about 5 % (0.154 -> 0.161-0.163 m0) and leaves alpha unchanged within the direction spread; in the slabs the grid estimate gives +6.5 % (1 nm) and +7.5 % (2 nm). These cells hold 1.4e21-3e21 cm^-3 donated electrons with E_F 1.2-1.8 eV inside the CB, so the curvature includes the self-consistent response to that filling. The W-slab masses are not band-edge fits (k-path run missing).

### 2.6 HSE06 (ESTIMATED from SCF grids)

Method: a 3-point Kane fit (m, alpha) to the CB at the non-Gamma grid points, calibrated by the same fit on the PAW-PBE grid of the same cell (whose band-edge mass is known from the band runs): m_HSE ~ m_PBE,edge x m3pt(HSE)/m3pt(PBE). Two variants bracket the model dependence: alpha fixed to the PBE value at the smallest abs(k), and the plain parabolic ratio at the smallest abs(k).

| Comparison | grid points abs(k) (1/A) | dE_ref/dE_x at the grid points | m estimate (free alpha) | range of variants | calibration factor |
|---|---|---|---|---|---|
| bulk_PAW_vs_NC_PBE (PAW_PBE -> NC_PBE) | 0.287, 0.498, 0.406 | 1.006, 1.005, 1.004 | 0.1552 | 0.155-0.1553 | 0.9425 |
| bulk_q1 (PAW_PBE -> HSE06_q1) | 0.287, 0.498, 0.406 | 1.057, 0.992, 1.009 | 0.1926 | 0.163-0.1926 | 0.9425 |
| bulk_q3 (PAW_PBE -> HSE06_q3) | 0.287, 0.498, 0.406 | 1.03, 0.966, 0.983 | 0.1872 | 0.1587-0.1872 | 0.9425 |
| slab1_PAW_vs_NC_PBE (PAW_PBE -> NC_PBE) | 0.203, 0.203, 0.287 | 1.005, 1.005, 1.005 | 0.2808 | 0.2807-0.2808 | 0.9728 |
| slab1_NCPBE_vs_HSE (NC_PBE -> HSE06_f160) | 0.203, 0.203, 0.287 | 1.008, 1.013, 0.99 | 0.2927 | 0.2829-0.2927 | 0.9678 |

- Validation: on the PAW-PBE k3 grid the same 3-point fit gives 0.1635 m0 and alpha 0.553 1/eV against the band-edge 0.1541 m0 and 0.584 1/eV from the band runs (calibration factor 0.9425). NC-PBE and PAW-PBE dispersions agree within 0.6 %.
- Reading: the calibrated estimates suggest that HSE06 increases the bulk band-edge mass from 0.1541 to 0.1587-0.1926 m0 (the variant range is a model sensitivity, not an uncertainty bound; three coarse-grid energies do not establish the k -> 0 curvature; the free-alpha fit gives 0.1872-0.1926 m0 with alpha 0.344-0.35 1/eV) and the 1 nm slab mass from 0.2793 to 0.2829-0.2927 m0. The HSE confinement increment dm(1 nm) = 0.090-0.134 m0 brackets the PBE value 0.125 m0: not resolved. ESTIMATED only: three grid points per cell at 0.2-0.5 1/A (0.45-2.5 eV above the CBM).

### 2.7 Thickness and W trends (Figures BM5, BM6)

- m*_e rises from 0.1541 (bulk) to 0.2026 (2 nm), 0.2793 (1 nm), 0.3365 (0.75 nm) and 0.4426 m0 (0.51 nm, In8(OH)24). FITTED: dm = a t^-p with a = 0.1145 +- 0.00024, p = 1.2755 +- 0.0048 (band-edge basis, fit3; relative residuals 0.0021, -0.0028, 0.0008); deck basis (3-point parabola) a = 0.11144, p = 1.2611 (V3 config: 0.11116, 1.26387).
- In-plane Kane alpha ([100]/[110] mean) falls with decreasing thickness: 0.47 (2.0 nm), 0.36 (1.0 nm), 0.31 (0.75 nm), 0.24 (0.51 nm) against 0.584 1/eV in bulk: the confined subband is more parabolic in-plane.
- Band-edge (Kane, 2-D DOS) vs 3-point parabola (deck basis): +3.4 % (0.51 nm), +0.5 % (0.75 nm), -0.6 % (1.0 nm), -1.8 % (2.0 nm), -3.0 % (bulk).
- m*_h: a resolved local curvature only at 0.75 nm (5.9 [100] / 3.3 [110] m0; not a single-band transport mass, see 2.4). The DOS-equivalent hole mass from Nv is 13-32 m0 in the slabs and about 18 m0 in bulk, without a monotonic trend; no law is fitted.
- W: +5 % (bulk, COMPUTED), +6.5 / +7.5 % (1 / 2 nm slabs, ESTIMATED). HSE06: the calibrated estimates suggest +3 to +25 % in bulk and +1 to +5 % at 1 nm (ESTIMATED; model sensitivity, not an uncertainty bound).
- The quoted sigma of every fitted law is the residual scatter about that law (one residual degree of freedom for fit3); it excludes the functional, termination, thickness-definition and polar-field errors.

**BM5**. (a) Bulk CB anchored-parabola mass vs the window end energy for [100] / [110] / [111]; horizontal line: Kane band-edge DOS mass. (b) Slab and bulk [100] window masses divided by the band-edge mass. (c) Slab hole masses (anchored) vs the window drop for [100] (solid) and [110] (dashed); filled symbols only where the hole mass passes the criteria (0.75 nm).

**BM6**. (a) m*_e vs H-H thickness: band-edge 2-D DOS mass (filled; open = 0.51 nm, In8(OH)24, outside every law), 3-point parabola (squares), W-slab grid estimates (diamonds, bars = variant range), HSE06 1 nm estimate (triangle), Lin et al. 2022 PBE values at their labels 0.95 / 1.98 nm (crosses); dashed: bulk band-edge mass, dotted: W-bulk mean. (b) dm_e = m(t) - m_bulk with the band-edge fit3 law (solid) and the V3 config law (dashed grey, deck basis). (c) Hole DOS-equivalent mass from the Boltzmann Nv (circles; dashed: bulk), and the 0.75 nm single-band hole masses [100] (up triangle) and [110] (down triangle).

## 3. Gaps, band edges, EA / IP and subbands vs thickness

| Slab | t_HH (nm) | Eg PBE (eV) | Eg direct Gamma | dEg | dEc | dEv | CB share | EA (eV) | IP (eV) | E1 = dEc | E2 | E3 | E21 | E21/E1 | Eg HSE-corrected | Eg exp.-anchored (2.93 + r dEg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.51 | 0.4612 | 3.1401 | 3.1413 | 2.2514 | 1.5845 | -0.6669 | 0.704 | 3.1917 | 6.3318 | 1.5845 | 3.4717 | 3.4723 | 1.8872 | 1.19 | 4.4943-4.5587 | 5.3163-5.4225 |
| 0.75 | 0.6953 | 2.1986 | 2.1985 | 1.3099 | 1.0589 | -0.251 | 0.808 | 3.7173 | 5.9159 | 1.0589 | 2.8741 | 3.2231 | 1.8152 | 1.71 | 3.4964-3.5164 | 4.3184-4.3802 |
| 1.0 | 0.9303 | 1.7885 | 1.7885 | 0.8998 | 0.8477 | -0.0521 | 0.942 | 3.9285 | 5.717 | 0.8477 | 2.3465 | 3.296 | 1.4988 | 1.77 | 3.0617-3.0624 | 3.8837-3.9262 |
| 2.0 | 1.9623 | 1.2239 | 1.2239 | 0.3352 | 0.2812 | -0.054 | 0.839 | 4.495 | 5.7189 | 0.2812 | 1.0003 | 1.8073 | 0.7191 | 2.56 | 2.4373-2.4633 | 3.2853-3.3011 |

Bulk: Eg = 0.8887 eV (indirect by 4.4 meV; direct at Gamma 0.8931), bulk_In2O3_protocol/bands_path.out:931 / bulk_In2O3_protocol/bands_path.out:850. Bulk-equivalent EA 4.7762 eV, IP 5.6649 eV (EA(2 nm) + dEc(2 nm), H-(001), PBE). HSE06: bulk 2.108 (q1, cern_htcondor/results/nc_hse_bulk_e80/scf.out:2958) / 2.0662 eV (q3, cern_htcondor/results/nc_hse_bulk_q3_f160_e80/scf.out:2981), 1 nm slab 3.0475 eV (cern_htcondor/results/nc_hse_slab1_f160_e80/scf.out:5162); r = dEg(HSE)/dEg(PBE) = 1.0599 (q1) / 1.1071 (q3 bulk).

Sources and routes: edges = HOMO/LUMO of each scf.out (bands lines and grid differ by <= 0.3 meV, field edge_beyond_scf_grid_meV); vacuum level = mean planar potential farther than 5 A from every atom plane (qeio.slab_vacuum, raw *_avg.dat); dEc(2 nm) = two-step alignment (a/2 window, plateau spread 8 meV); dEc(t) = dEc(2 nm) + EA(2 nm) - EA(t) (same termination); dEv = dEc - dEg. E1 = dEc, E2 = E1 + E21, E3 = E1 + E31 (CB levels at Gamma relative to the bulk CBM). At 0.51 nm E2 and E3 are degenerate (1.887 / 1.888 eV above E1).

Caveats: 0.75 nm is polar without dipole correction: vacuum ramp 347.1 meV across the vacuum gap, EA/IP/dEc +- 0.1736 eV (ASSUMED reference-choice sensitivity, not a bound); dEc(0.695) range 0.8853-1.2325 eV. 0.51 nm is In8(OH)24 (outside every law). HSE-corrected and experiment-anchored gaps assume dEg_HSE = r dEg_PBE with r measured at 1 nm only and thickness-independent (ASSUMED); the slab EXX q-convergence is untested.

W slabs (COMPUTED, metallic cells): 1 nm: EA(host CB) 4.0693, IP(VB top) 5.7885, work function 2.8417 eV, E_F - host CB min 1.2276 eV, VB-top to host-CB 1.7192 eV; 2 nm: EA(host CB) 4.7463, IP(VB top) 5.8226, work function 3.508 eV, E_F - host CB min 1.2383 eV, VB-top to host-CB 1.0763 eV. At 1 nm W changes EA(host CB) by +0.141 eV and IP(VB top) by +0.072 eV against the pure slab; the work function lies 1.228 eV below its own EA because E_F is in the CB. At 2 nm W changes EA(host CB) by +0.251 eV and IP(VB top) by +0.104 eV against the pure slab; the work function lies 1.238 eV below its own EA because E_F is in the CB.

### 3.1 Laws a t^-p (FITTED; t = H-H thickness in nm)

| Quantity | Fit | Points (t_HH) | a | sigma_a | p | sigma_p | rel. residuals | LOO range a / p | at 2.0 / 6.3 / 13.2 nm |
|---|---|---|---|---|---|---|---|---|---|
| dEg | fit3 | 0.695, 0.93, 1.962 | 0.81466 | 0.0026 | 1.3155 | 0.0073 | -0.0031, 0.0044, -0.0012 | 0.8126-0.8197 / 1.2898-1.323 | 0.3273 / 0.0724 / 0.0273 |
| dEg | fit2_1and2nm | 0.93, 1.962 | 0.81778 | - | 1.323 | - | 0, 0 | - / - | 0.3269 / 0.0716 / 0.0269 |
| dEg | fit4_with_0p46_diagnostic | 0.461, 0.695, 0.93, 1.962 | 0.81443 | 0.0017 | 1.3146 | 0.0037 | -0.0006, -0.0025, 0.0047, -0.0016 | 0.8131-0.8171 / 1.3079-1.3155 | 0.3274 / 0.0725 / 0.0274 |
| dEc | fit3 | 0.695, 0.93, 1.962 | 0.70176 | 0.0488 | 1.3176 | 0.1565 | -0.0652, 0.0983, -0.026 | 0.6655-0.8022 / 0.764-1.4784 | 0.2815 / 0.0621 / 0.0234 |
| dEc | fit2_1and2nm | 0.93, 1.962 | 0.76182 | - | 1.4784 | - | -0, -0 | - / - | 0.2734 / 0.0501 / 0.0168 |
| dEc | fit4_with_0p46_diagnostic | 0.461, 0.695, 0.93, 1.962 | 0.67721 | 0.0429 | 1.2002 | 0.1162 | -0.0758, 0.0109, 0.1478, -0.0675 | 0.6458-0.7832 / 0.8974-1.3176 | 0.2947 / 0.0744 / 0.0306 |
| dEc | fit3_0p695_low | 0.695, 0.93, 1.962 | 0.65386 | 0.0846 | 1.1791 | 0.2912 | -0.1179, 0.1906, -0.0478 | 0.5924-0.8386 / 0.1491-1.4784 | 0.2888 / 0.0746 / 0.0312 |
| dEc | fit3_0p695_high | 0.695, 0.93, 1.962 | 0.74511 | 0.014 | 1.435 | 0.0423 | -0.0181, 0.0256, -0.0071 | 0.7345-0.7725 / 1.2854-1.4784 | 0.2756 / 0.0531 / 0.0184 |
| -dEv | fit3 | 0.695, 0.93, 1.962 | 0.0978 | 0.0518 | 1.1786 | 1.1934 | 0.6724, -0.5107, 0.2222 | 0.0353-0.1465 / -0.048-5.4 | - |
| -dEv | fit2_1and2nm | 0.93, 1.962 | 0.05228 | - | -0.048 | - | -0, -0 | - / - | - |
| dm_e (band edge) | fit3 | 0.695, 0.93, 1.962 | 0.1145 | 0.00024 | 1.2755 | 0.0048 | 0.0021, -0.0028, 0.0008 | 0.114-0.1147 / 1.2706-1.2924 | 0.0473 / 0.0109 / 0.0043 |
| dm_e (band edge) | fit2_1and2nm | 0.93, 1.962 | 0.11422 | - | 1.2706 | - | -0, -0 | - / - | 0.0473 / 0.011 / 0.0043 |
| dm_e (deck basis) | fit3 | 0.695, 0.93, 1.962 | 0.11144 | 0.00015 | 1.2611 | 0.0031 | -0.0013, 0.0019, -0.0005 | 0.1113-0.1117 / 1.2502-1.2643 | 0.0465 / 0.0109 / 0.0043 |

- sigma_a, sigma_p: residual scatter about the law (fit3 has one residual degree of freedom); they exclude functional, termination, thickness-definition and polar-field errors. LOO = leave-one-out refits.
- dEg: fit3 reproduces the V3 / C10 law (0.81431, 1.31518); fit2 and fit4 (with 0.46 nm) differ by < 0.001 eV at 2 nm (small residual scatter, sigma_p 0.007).
- dEc: fit3 (frozen V3 / C10 law, 0.70147, 1.31669) has sigma_p 0.1565; the two-point fit without the polar 0.695 nm point (the primary fit until a dipole-corrected run exists) gives p = 1.4784; at 6.3 nm the options span 0.0501-0.0746 eV.
- -dEv: no meaningful power law: -dEv is 0.0521 eV at 0.930 nm and 0.0540 eV at 1.962 nm (equal within the 15-30 meV spread of the alignment routes, non-monotonic); VB-top character (../out/f08): OH-surface O 2p at 0.51 nm (OH share 0.98) and 0.75 nm (0.75), 0.72 in the 1 nm W slab (no projection of the pure 1 nm), bulk-like interior O 2p in the pure 2 nm slab (0.001).
- m*_h: no law: a single-band hole mass is meaningful only at 0.75 nm (b01 criteria); the hole DOS-equivalent mass from the Boltzmann sum does not vary monotonically with t.
- HSE: dEg_HSE(t) = r dEg_PBE(t) (ASSUMED) scales a to 0.8635-0.9019 with p unchanged.

**BM7**. (a) Gap vs H-H thickness: PBE (circles; open = 0.51 nm), PBE direct at Gamma (bars), HSE-corrected Eg_HSE,bulk + r dEg_PBE (diamonds, mean of the two r / bulk-HSE pairings, which differ by <= 0.06 eV), computed HSE06 1 nm (square); dashed: bulk PBE and bulk HSE06 q3; grey band: experimental fundamental gap 2.93 +- 0.15 eV (King 2009). (b) dEg, dEc and -dEv (log-log) with the fit3 (solid) and fit2 (dashed) laws; bar at 0.695 nm: +-0.17 eV vacuum-reference sensitivity. (c) EA (circles) and IP (squares) of the pure slabs, W slabs (diamonds: host-CB EA and VB-top IP); bars: 0.75 nm sensitivity; dashed: bulk-equivalent EA / IP. (d) CB levels at Gamma relative to the bulk CBM: E1, E2, E3.

## 4. TCAD-ready parameters per thickness

| t (nm) | source | Eg PBE | Eg HSE-corr. | Eg exp.-anchored | Eg deck basis (3.05 + dEg) | chi PBE vacuum | chi deck basis (4.3 - dEc) | m*_e PBE | m*_e deck basis | Nc 3-D (deck m) | Nc 3-D Kane | Nc quasi-2-D (N2D/t) | Nc q-2-D Kane |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.6953 | COMPUTED (DFT slab slabL2_relax_v2) | 2.1986 | 3.4964-3.5164 | 4.3184-4.3802 | 4.3599 | 3.7173 | 3.2411 | 0.3365 | 0.384 | 5.97e+18 | 6.31e+18 | 5.96e+19 | 6.06e+19 |
| 0.9303 | COMPUTED (DFT slab slab1r_final_cpu) | 1.7885 | 3.0617-3.0624 | 3.8837-3.9262 | 3.9498 | 3.9285 | 3.4523 | 0.2793 | 0.3303 | 4.76e+18 | 5.04e+18 | 3.83e+19 | 3.91e+19 |
| 1.9623 | COMPUTED (DFT slab slab2_relax_c2) | 1.2239 | 2.4373-2.4633 | 3.2853-3.3011 | 3.3852 | 4.495 | 4.0188 | 0.2026 | 0.2556 | 3.24e+18 | 3.43e+18 | 1.41e+19 | 1.44e+19 |
| 2.0 | FITTED laws (b03), interpolated | 1.216 | 2.4286-2.4549 | 3.2769-3.2924 | 3.3773 | - | 4.0185 (fit2 4.0266) | 0.2014 | 0.2545 | 3.22e+18 | 3.41e+18 | 1.37e+19 | 1.41e+19 |
| 6.3 | FITTED laws (b03), extrapolated | 0.9611 | 2.1463-2.1847 | 3.0067-3.0101 | 3.1224 | - | 4.2379 (fit2 4.2499) | 0.165 | 0.2189 | 2.57e+18 | 2.72e+18 | n/a (multi-subband) | n/a |
| 13.2 | FITTED laws (b03), extrapolated | 0.916 | 2.0965-2.137 | 2.959-2.9603 | 3.0773 | - | 4.2766 (fit2 4.2832) | 0.1584 | 0.2123 | 2.46e+18 | 2.6e+18 | n/a (multi-subband) | n/a |

Bulk: Eg PBE 0.8887, HSE06 2.0662-2.108 eV; m*_e PBE 0.1541 (HSE estimate 0.1587-0.1926) m0; alpha 0.584 1/eV; chi PBE bulk-equivalent 4.7762 eV; Nc(PBE m) 1.52e+18, Nc(0.208) 2.38e+18 (Kane 2.52e+18) cm^-3; Nv 1.93e+21 cm^-3 (all grids 1.92e+21-2.67e+21).

Labels: Eg PBE, chi PBE vacuum, m*_e PBE, Nv = COMPUTED at the DFT thicknesses and FITTED (laws) at 2.0 / 6.3 / 13.2 nm (6.3 and 13.2 nm are extrapolations); HSE-corrected and experiment-anchored Eg = CALCULATED with the ASSUMED r rule; deck-basis columns = LITERATURE bulk (3.05 eV, 4.3 eV, 0.208 m0) + FITTED increments, exactly the V3 construction; Nc = CALCULATED. Quasi-2-D Nc only where a single subband is justified by a COMPUTED E21 >> kT (t <= 2 nm).

Other TCAD items:
- m* for tunnelling: ASSUMED. the transport-normal (gate / contact tunnelling) mass of the film is not computed: the slab CB is quantised along z; the bulk isotropic band-edge mass (PBE 0.154, HSE estimate 0.16-0.19, experiment 0.18-0.21) is the closest computed quantity; the evanescent (imaginary-k) mass in the gap needs a complex-band-structure run. The deck tunnelling masses (me.tunnel 0.3 / 0.1, F.AE m 0.10) are those of the Al2O3 / HfO2 barriers, not of IWO.
- W donor: resonant, 1.2-1.8 eV above E_C (COMPUTED at the DFT filling only); occupation at device densities ~0 (fully ionised) ONLY IF the resonant level stays >= 1.2 eV above E_C at device density: then exp(-(E_D - E_F)/kT) < exp(-1.2/0.0259) ~ 1e-20 for E_F below E_C. INFERRED: a Kohn-Sham resonance in a filled 3-electron cell does not establish dilute-limit defect ionisation (no charged-defect calculation, no lower-density cell). COMPUTED per cell (level - host CB at Gamma / level - E_F / E_F - host CB, eV): bulk 8b 1.8026 / 0.0901 / 1.7126; bulk 24d 1.764 / 0.0007 / 1.7633; 1 nm 24d 1.2228 / -0.0048 / 1.2276; 2 nm 24d 1.3414 / 0.1031 / 1.2383. Deck: constant effective Nd0 = 2.5e17 cm^-3 (FITTED V1 amplitude, constant form ASSUMED); no W level in the deck. W-5d counts are Loewdin projections of occupied above-VB states (0.09-0.43), not a trapped fraction.
- Surface / OH states: no state inside the gap of any OH-terminated slab (gaps clean, COMPUTED); the VB top is OH-surface O 2p at 0.51 / 0.75 nm and in the 1 / 2 nm W slabs, bulk-like at 2 nm pure; the CB bottom is In 5s / O 2s with an OH share falling from 0.56 (0.51 nm) to 0.008 (2 nm). Ideal OH termination gives no interface trap density: the deck interface sheet (ASSUMED) and Qf (FITTED) are not DFT quantities. Per slab (VB-top OH share / CB-bottom OH share): 0.51 nm 0.984 / 0.5623; 0.75 nm 0.7547 / 0.3488; 1 nm (W slab proxy) 0.7249 / 0.2191; 2 nm pure 0.001 / 0.0081; 2 nm W 0.7198 / 0.0047.
- Fermi level: insulating (fixed occupations): no physical E_F; device E_F is set by Nd, traps and bias in TCAD; W cells: E_F - host CB at Gamma = bulk 8b 1.7126, bulk 24d 1.7633, 1 nm 24d 1.2276, 2 nm 24d 1.2383 eV (E_F 1.2-1.8 eV inside the host CB at 1.4e21-3e21 cm^-3 (degenerate DFT cells); not a device value).
- Nv: COMPUTED Nv is about 1.9e21 cm^-3 (bulk) and 1.8e21-4.4e21 cm^-3 (quasi-3-D, slabs), about 200 times the deck NV300 = 1e19 (ASSUMED). Holes are not solved in the decks, so NV300 enters through n_i: n_i grows by sqrt(190) ~ 14 but stays far below 1 cm^-3 for Eg > 3 eV, so a small absolute contribution is expected; the SRH / trap terms and the registered two-carrier tests still need their conditional bounds checked before calling it negligible.

### 4.1 Comparison with the deck values

| Deck | run | eg300 deck / here (deck basis) | diff (meV) | affinity deck / here fit3 (fit2) | diff fit3 (meV) | m* deck / here | Nc300 deck / here 3-D / q-2-D (Kane) | Nv300 deck / COMPUTED |
|---|---|---|---|---|---|---|---|---|
| V2@2.0 | run_0058_2p0_v2_anchor_2p0 (../results/runs/run_0058_2p0_v2_anchor_2p0/device.in:71) | 3.3805 / 3.3773 | -3.2 | 4.02321 / 4.0185 (4.0266) | -4.71 | 0.2545 / 0.2545 | 3.22e+18 / 3.22e+18 / 1.37e+19 (1.41e+19) | 1e19 / 1.93e+21 |
| C10@2.0 | run_0061_2p0_c10_s0_01_2p0 (../results/runs/run_0061_2p0_c10_s0_01_2p0/device.in:72) | 3.37725 / 3.3773 | 0.05 | 4.01839 / 4.0185 (4.0266) | 0.11 | 0.2543 / 0.2545 | 1.37e+19 / 3.22e+18 / 1.37e+19 (1.41e+19) | 1e19 / 1.93e+21 |
| C10@6.3 | run_0068_6p3_c10_s1_01_6p3 (../results/runs/run_0068_6p3_c10_s1_01_6p3/device.in:71) | 3.12236 / 3.1224 | 0.04 | 4.23784 / 4.2379 (4.2499) | 0.06 | 0.2189 / 0.2189 | 2.57e+18 / 2.57e+18 / n/a | 1e19 / 1.93e+21 |
| C10@13.2 | run_0069_13p2_c10_s1_02_13p2 (../results/runs/run_0069_13p2_c10_s1_02_13p2/device.in:71) | 3.07735 / 3.0773 | -0.05 | 4.27653 / 4.2766 (4.2832) | 0.07 | 0.2123 / 0.2123 | 2.45e+18 / 2.46e+18 / n/a | 1e19 / 1.93e+21 |

- The C10 decks (fit3) are reproduced to <= 0.11 meV in Eg and affinity, 0.0002 m0 in m* and 0.1 % in Nc (2 nm quasi-2-D: deck 1.373e19 vs 1.374e19 here). V2 differs by 3-5 meV because V2 used its two-point laws at the Lin labels (0.95 / 1.98 nm), as recorded in ../out/f06.
- Not in the decks: (i) the CB non-parabolicity (Kane alpha 0.58 bulk, 0.45-0.50 at 2 nm), which raises Nc by 5.7 % (3-D) or 2.5 % (quasi-2-D) and the conductivity (optical) mass at degenerate filling, m(1 + 2 alpha E_F); (ii) the HSE r factor in dEg (+6 to +11 %); (iii) the band-edge (Kane) vs 3-point basis of m* (-3 % bulk to +0.5 % at 0.75 nm); (iv) the computed Nv (x190). None changes the frozen C10 laws; (i) and (ii) are candidate sensitivities only.

**BM8**. TCAD options at the device thicknesses 2.0 / 6.3 / 13.2 nm (crosses: deck values of runs 0058/0061 at 2.0, 0068 at 6.3 and 0069 at 13.2 nm). (a) Nc: 3-D parabolic and Kane with the deck-basis mass; quasi-2-D N2D/t (2.0 nm only). (b) Eg: deck basis (3.05 + dEg), experiment-anchored (2.93 + r dEg), HSE-corrected (Eg_HSE,bulk + r dEg). (c) chi = 4.3 - dEc for fit3 and fit2; grey bars: range over fit3, fit2 and the +-0.17 eV 0.695 nm sensitivity.

## 5. Literature comparison (checked 2026-10-14)

| Quantity | Literature value (method) | Citation | This work | Why ours differs |
|---|---|---|---|---|
| Fundamental gap, bixbyite | 2.93 +- 0.15 eV (photoemission + optical, single crystals); HSE03 VBM slightly off Gamma along G-H, VB(Gamma) only ~50 meV below | King et al., PRB 79, 205211 (2009), doi:10.1103/PhysRevB.79.205211 | PBE 0.8887 eV (indirect by 4.4 meV, VBM at 0.2 G-H); HSE06 2.0662-2.108 eV | PBE self-interaction error (-2.0 eV); HSE06 (25 % exchange) still -0.8 eV: In2O3 needs a larger mixing or GW; the off-Gamma VBM is reproduced qualitatively, with a smaller offset in PBE |
| Fundamental gap (upper limit) | <= 2.9 eV; dipole transitions VB top -> CB forbidden or weak, strong absorption about 0.8 eV higher | Walsh et al., PRL 100, 167402 (2008), doi:10.1103/PhysRevLett.100.167402 | not computed (no dipole matrix elements) | the 0.893 eV "direct gap at Gamma" here is not the optical gap |
| Absorption onset | about 2.7 eV at room temperature (melt-grown crystals), proposed indirect | Irmscher et al., Phys. Status Solidi A 211, 54 (2014), doi:10.1002/pssa.201330184 | - | temperature (300 K vs 0 K DFT) and functional |
| Optical (dipole-allowed) onset | 3.8 eV for n <= 1e19 cm^-3 | Feneberg et al., PRB 93, 045203 (2016), doi:10.1103/PhysRevB.93.045203 (erratum PRB 94, 239905) | - | not computed |
| m*_e (band edge) | 0.18 m0 (zero-density, from plasma frequencies); 0.4 m0 at 1e21 cm^-3 | Feneberg et al. 2016 (above); value from the abstract; the erratum PRB 94, 239905 (doi:10.1103/PhysRevB.94.239905) was not readable here (the Codex review reports that it leaves the results unaffected) | PBE 0.1541 m0 (Kane), 0.1588 (3-point); HSE06 estimate 0.16-0.19; PBE Kane optical mass 0.39 m0 at 1e21 | PBE gap too small -> Kane coupling too strong -> band-edge mass 14 % (vs 0.18) to 26 % (vs 0.208) too small; the calibrated HSE06 estimates suggest that most of the difference closes |
| m*_e (band edge) | 0.208 +- 0.006 m0 (optical Hall effect, n = 2.8e17 cm^-3) | Stokey et al., J. Appl. Phys. 129, 225102 (2021), doi:10.1063/5.0052848 | deck LITERATURE value 0.208 (V3) | as above |
| m*_e (DFT-PBE) | 0.17 m0 bulk; 0.23 m0 (1.98 nm) and 0.30 m0 (0.95 nm) H-passivated slabs; gaps 0.94 / 1.27 / 1.88 eV (PBE, ONCV 140 Ry; Wannier interpolation for DOS) | Lin et al., ACS Nano 16, 21536 (2022), doi:10.1021/acsnano.2c10383 (methods text: arXiv:2205.00357) | bulk 0.154-0.159; 2 nm 0.2064, 1 nm 0.2811 m0; dEg 0.335 / 0.900 eV | their thickness labels are not H-H thicknesses; their fit window is not stated (our 2 nm anchored masses run from 0.2047 to 0.2307 m0 over 0-359 meV); ours are 6-10 % lower on the 3-point basis |
| Confinement in atomic-layer In2O3 | gap opening and Fermi-level shift from quantum confinement, supported by DFT | Si et al., Nano Lett. 21, 500 (2021), doi:10.1021/acs.nanolett.0c03967 | dEg = 0.815 t^-1.316 eV (PBE, fit3) | qualitative agreement; their films are amorphous ALD In2O3 |
| m*_h | no tabulated value located; the top VB is very flat (both papers above) | King 2009; Walsh 2008 | single-band hole mass not meaningful (degenerate, camel back); DOS-equivalent ~18 m0; 0.75 nm slab 3.3-5.9 m0 | not a comparison: flatness confirmed |
| IP / EA | IP about 7.0 eV ((111)) and about 7.7 eV ((100), O-dimer termination, O-rich), photoemission + DFT; EA = IP - 2.93 -> about 4.1-4.8 eV (derived here) | Hohmann et al., J. Phys.: Condens. Matter 23, 334203 (2011), doi:10.1088/0953-8984/23/33/334203 | PBE H-(001) bulk-equivalent IP 5.6649 eV, EA 4.7762 eV | PBE places the VBM too high (IP too small by > 1.3 eV) and the termination differs (OH vs bare / O-dimer); EA is the better-behaved PBE edge; the deck uses 4.3 eV (LITERATURE) |
| Resonant donor (analogue) | Mo 4d donor states lie high in the In2O3 CB and barely perturb the CBM | Swallow et al., Mater. Horiz. 7, 236 (2020), doi:10.1039/c9mh01014a | W 5d level 1.2-1.8 eV above the CBM; host-CB mass +5 % (bulk) | consistent picture; W itself: no peer-reviewed DFT located in this search |

## 6. Not derivable from the existing data: runs needed (none submitted)

Costs are scaled from measured wall times of the same cells (run sheets in ../runs_sep_oct and the protocol outputs); "local" = WSL Ubuntu-22.04, env qe, 10 MPI ranks, -nk 2.

| # | Missing quantity | Exact run | Cost basis (measured) | Estimate |
|---|---|---|---|---|
| 1 | W-slab band-edge masses, 1 nm | SCF (rerun; no save kept) + bands on iwo_slab1_final_cpu geometry, the 21 k tpiba lines of slab1r_final_cpu/bands.in, diagonalization = 'cg' (the Davidson bands step failed in cdiaghg), nbnd 336 | SCF 2 h 55 min, 16 CPUs; pure 1 nm bands 4 h 38 min (16 CPUs or one A100) | ~3 h SCF + 9-12 h bands (CG ~2x) on 16 CPUs |
| 2 | W-slab band-edge masses, 2 nm | SCF + bands on iwo_slab2_final_cpu geometry (21 k, CG), conv_thr 1e-8, beta 0.1, ~66 GB | SCF 8 h 05 min on 33 CPUs; pure 2 nm bands 8 h 22 min on one H100 | ~1 h SCF + 15-20 h bands on one H100 (or 2-3 days on 33 CPUs) |
| 3 | Transverse hole masses at the bulk VBM | 'bands' on the local vcr save: k0 = (0, 0, 0.2) 2pi/a plus +-0.005 ... 0.03 1/A along [100], [010] and [110]-transverse, about 25 k, CG | bands_gamma.out, 31 k: 4 h 21 min local | ~4 h local |
| 4 | Converged Nv / hole DOS (bulk) | nscf 6x6x6 Gamma-centred (24 operations), nbnd 190, occupations = 'tetrahedra_opt', then dos.x / projwfc.x | bands_gamma 31 k: 4.3 h local | ~5 h local |
| 5 | Slab Nv / 2-D DOS | SCF rerun + nscf 6x6x1 (tetrahedra) for 0.75 / 1 / 2 nm | SCF 1 h 6 min (0.75 nm, 11 CPUs), 2 h 19 min (1 nm, 16 CPUs), 56 min (2 nm, H100) | 1-4 h per slab |
| 6 | [010] line of the rectangular 0.51 nm cell | SCF + bands, 11 k along [010] | slabL1 SCF 28 min + bands 43 min (11 CPUs) | ~1.5 h |
| 7 | Dipole-corrected 0.75 nm edges (dEc, EA, IP, VB character) | SCF with tefield = .true., dipfield = .true., edir = 3, emaxpos / eopreg inside the vacuum, + planar average + bands + forces | slabL2 SCF 1 h 6 min + bands 1 h 27 min (11 CPUs); vc-relax 9 h 58 min (H100) if the forces exceed 1e-3 Ry/bohr | ~3 h (+10 h if re-relaxed) |
| 8 | HSE06 band-edge masses (bulk, 1 nm) | HSE06 SCF on a full grid (nosym) + Wannier90 interpolation of the CB, or zero-weight small-k points if pw.x accepts them with EXX (to be tested) | bulk q3 SCF (4 k) 4 h 15 min, 1 nm SCF (4 k) 4 h 0 min on one H100 | 1-3 GPU-days per cell (uncertain) |
| 9 | HSE06 EA / IP and the HSE dEc / dEv split | pp.x plot_num 11 + average.x on the HSE06 1 nm SCF (save needed: rerun) and the HSE bulk <V> via the G = 0 route | 1 nm HSE SCF 4 h on one H100 | ~4 h GPU |
| 10 | r = dEg(HSE)/dEg(PBE) at other thicknesses | HSE06 SCF (ecutfock 160) of the 0.75 and 2 nm slabs | 1 nm (96 atoms) 4 h on one H100; default ecutfock ran out of memory at 1 nm | ~3 h (0.75 nm); 15-25 h and possibly 2 GPUs (2 nm, 176 atoms) |
| 11 | W level vs density (lower W fraction) and spin | 160-atom 1x1x2 cell, 1 W (1.6 %): vc-relax / relax + SCF + projwfc, spin-polarised check; a V0-era input exists in bulk_IWO_1W_1p6pct_112/ (not protocol-checked) | 80-atom W24d: relax 23 h 48 min + SCF 3 h on 32 CPUs | ~5 days on 32 CPUs or ~1 day on one H100 |
| 12 | Tunnelling (evanescent) mass in the gap | complex band structure of bulk In2O3 (pwcond.x; check its PAW support, else SG15 NC) | no measured basis | hours locally (uncertain) |
| 13 | Masses of the H-L vacancy cells | not needed for H-L; would need band runs of In32O47 / In31WO47 | - | not proposed |

## 7. Consistency with RESULTS_LOG, the ledger and the decks

- RESULTS_LOG (2026-10-04 entry): 2 nm in-plane mass 0.2064 [100] / 0.2059 [110] m0, increment +0.047 over 0.159, Lin 0.23 m0 (10 % / 6 % lower) are reproduced exactly on the same 3-point basis (here 0.2064 / 0.2059); E2 - E1 = 0.719 eV (2 nm) and 1.499 eV (1 nm) match.
- C020 (m* 0.206 m0 at 2 nm; 1 nm 0.95-1.00 eV HSE-corrected): matches (r x 0.8998 = 0.954-0.996 eV). The 0.206 is the 3-point parabola; the Kane band-edge value is 0.2026 (2-D DOS).
- V3 config "PBE bulk 0.159 m0" is the 3-point parabola; the band-edge (Kane) mass is 0.154 m0 (-3 %). Not an error; a basis definition to keep consistent.
- The 2 nm pure slab VBM is bulk-like (OH share 0.001; RESULTS_LOG 2026-10-05 18:23Z entry); in the W slabs the VB top is OH-surface O 2p (OH share 0.72 at 1 and 2 nm).
- No new discrepancy with RESULTS_LOG or the ledger was found in this deliverable; the deck NV300 (ASSUMED 1e19) differs from the COMPUTED Nv by about 190x; a small effect on the electron-only simulations is expected but not yet bounded (SRH / trap terms, two-carrier tests).

## 8. Hole masses (b05_holes.py, figure BM9)

Hole convention: m_h = -hbar^2 / (d^2E/dk^2); a negative value means the band rises away from Gamma. All numbers are PBE (PAW) and COMPUTED unless labelled otherwise. The valence-band top of In2O3 is a nearly flat O 2p manifold, so curvature masses describe only the immediate neighbourhood of an extremum; the thermally relevant quantity is the valence-band density of states (8.3).

### 8.1 Bulk: band-resolved directional curvature masses at Gamma (bands 174-176, degenerate at Gamma)

Source: `bulk_In2O3_protocol/bands_gamma.out` (Gamma + 10 points per direction, steps 0.0153 1/A); check: chord masses from the first points of `bulk_In2O3_protocol/bands_path.out` (steps 0.039-0.041 1/A). Windows: n = 2 / 3 / 4 / 6 / 10 points (|dE| up to the values in out/b05_holes.json).

| Band | Direction | n=2 | n=3 | n=4 | n=6 | n=10 | print-rounding sigma (n=3) | path chord masses (1st-4th point) |
|---|---|---|---|---|---|---|---|---|
| 174 | [100] (G-H) | 3.22 | 3.2 | 3.22 | 3.23 | 3.28 | 0.06 | 3.31, 3.23, 3.27, 3.3 |
| 174 | [110] (G-N) | 4.44 | 4.25 | 4.3 | 4.34 | 4.64 | 0.1 | 4.17, 4.34, 4.54, 4.8 |
| 174 | [111] (G-P) | 7.2 | 7.85 | 7.89 | 7.78 | 7.83 | 0.35 | 7.86, 7.62, 7.75, 7.92 |
| 175 | [100] (G-H) | 8.89 | 8.14 | 7.97 | 7.76 | 6.91 | 0.38 | 7.87, 7.87, 7.17, 6.37 |
| 175 | [110] (G-N) | 18.88 | 19.81 | 16.76 | 12.97 | 8.74 | 2.23 | 19.46, 13.77, 9.75, 7.55 |
| 175 | [111] (G-P) | 7.2 | 7.85 | 7.89 | 7.78 | 7.83 | 0.35 | 7.86, 7.62, 7.75, 7.92 |
| 176 | [100] (G-H) | -5.81 | -6.5 | -6.93 | -8.25 | -15.76 | 0.24 | -6.3, -8.13, -12.87, -35.96 |
| 176 | [110] (G-N) | -37.75 | -39.62 | -45.02 | -45.27 | -57.57 | 8.91 | -29.19, -46.83, -52.64, -66.9 |
| 176 | [111] (G-P) | flat (dE 0.0 meV) | flat (dE 0.0 meV) | 196.76 | 65.9 | 31.44 | - | -, 62.85, 35.35, 24.53 |

| Band | character | inverse-curvature average under the angular model, m (n = 3 / 4 / 6 / 10) | star-weighted, same data (n = 4) | sampled directional curvature ratio max/min (n = 4) |
|---|---|---|---|---|
| 174 | lightest falling band ("light-hole-like") | 4.36 / 4.39 / 4.41 / 4.57 | 4.59 | 2.45 |
| 175 | heavy falling band (strong [110] window dependence) | 11 / 10.45 / 9.51 / 7.91 | 10.47 | 2.12 |
| 176 | camel back: rises along [100] and [110], flat along [111] | UNRESOLVED ([111] (G-P) printed-flat) / net 1/m -0.05 < 0 / net 1/m -0.041 < 0 / net 1/m -0.018 < 0 | - | mixed signs |

The directional masses above are the primary result. The "inverse-curvature average under the angular model" expands 1/m in cubic harmonics through the three directions, 1/m(d) = a + b (S4 - 3/5) + c (S6 - 1/105), and reports 1/a. Three directions fix exactly three coefficients, so the angular model is not tested: higher terms can vanish in all three sampled directions and still change the spherical average. It is an ESTIMATED diagnostic with no transport or DOS significance; the star-weighted harmonic mean uses the same data and is not an independent check. The "sampled directional curvature ratio" is the max/min of 1/m over the three sampled directions (neither the anisotropy nor the warping parameter in the strict sense). A printed-flat direction (dE 0.0 meV in the window) is UNRESOLVED, not zero curvature.

### 8.2 Off-Gamma maxima and why curvature masses are not transport masses

- [100] (G-H): band 176 peaks at |k| = 0.1219 1/A, 4.44 meV above VB(Gamma) (global VBM, six pockets on <100>); longitudinal mass 4.026 +- 0.14 m0 (5-point parabola, print rounding).
- [110] (G-N): a second, lower maximum at |k| = 0.1745 1/A, +1.62 meV (coarse path points; bands_gamma reaches +1.4 meV at 0.153 1/A), longitudinal mass 17.816 +- 0.418 m0.
- [111] (G-P): Gamma is the maximum of the triplet along this line (bands 174/175 degenerate, 176 nearly flat).
- Transverse masses at the off-Gamma maxima are not computed (no k-points off the lines). All maxima lie within 4.4 meV of VB(Gamma), far below kT = 25.85 meV: at 300 K holes populate all three bands over |k| up to about 0.2-0.3 1/A, where the bands are strongly warped and non-parabolic (BM9a). No single band-edge hole mass describes them.
- Gamma-local averages of the inverse-curvature averages (equal band populations, ESTIMATED diagnostic): the two falling bands give m_h = 6.242 / 6.188 / 6.024 m0 (n = 3 / 4 / 6); including the camel-back band UNRESOLVED / 10.985 / 10.302 m0. Gamma-local averages with equal band populations; the camel-back band 176 has a negative net angular curvature (it rises on average from Gamma), so the triplet average mixes signs and is not a transport mass. A thermal conductivity mass (Boltzmann-weighted band velocities over the zone) needs a dense uniform grid and an interpolation (BoltzTraP2 / Wannier); not available.

### 8.3 Bulk DOS hole mass from the computed valence-band density of states

N_V(300 K) = (1/V) sum_k w_k sum_n exp(-(E_ref - E_nk)/kT) over the valence states with E_ref - E_nk <= window: the integral of the grid DOS (delta functions at the computed eigenvalues) with the Boltzmann factor; Fermi-Dirac statistics reduce to it for E_F - E_V >> kT (n-type IWO: about 3 eV). m_h,DOS = (N_V / N0)^(2/3) m0 with N0 = 2 (2 pi m0 kT / h^2)^1.5 = 2.5094e+19 cm^-3 (300 K). COMPUTED on the stated grids.

| Grid | E_ref | window 0.05 eV | 0.1 eV | 0.2 eV | all states | m_h,DOS (all) |
|---|---|---|---|---|---|---|
| prim_k3 (4 k, a = 10.306 A) | own grid maximum (Gamma) (8.0741 eV) | 2.42e+21 | 2.6e+21 | 2.67e+21 | 2.67e+21 | 22.4 |
| prim_k3 (4 k, a = 10.306 A) | true VBM of bands_path (same SCF potential) (8.0785 eV) | 2.04e+21 | 2.19e+21 | 2.25e+21 | 2.25e+21 | 20 |
| prim_k4 (8 k, exp. lattice 10.117 A) | own grid maximum (8.9221 eV) | 1.49e+21 | 1.85e+21 | 1.92e+21 | 1.92e+21 | 18 |
| prim_k4 (8 k, exp. lattice 10.117 A) | VB(Gamma) + 4.4 meV (offset transferred) (8.9265 eV) | 1.26e+21 | 1.56e+21 | 1.62e+21 | 1.62e+21 | 16.1 |
| 80-atom k3 (6 k, H-L parent) | own grid maximum (8.0739 eV) | 2.07e+21 | 2.31e+21 | 2.35e+21 | 2.36e+21 | 20.7 |
| 80-atom k3 (6 k, H-L parent) | VB(Gamma) + 4.4 meV (8.0783 eV) | 1.55e+21 | 1.94e+21 | 1.99e+21 | 1.99e+21 | 18.4 |
| 80-atom k4 (14 k, H-L parent) | own grid maximum (8.0774 eV) | 1.54e+21 | 1.84e+21 | 1.93e+21 | 1.93e+21 | 18.1 |
| 80-atom k4 (14 k, H-L parent) | VB(Gamma) + 4.4 meV (8.0782 eV) | 1.49e+21 | 1.79e+21 | 1.87e+21 | 1.87e+21 | 17.7 |

- Energy window: N_V saturates by 0.2-0.3 eV below E_ref (Boltzmann factor 4.4e-4 at 0.2 eV, below 1e-5 near 0.3 eV); about 80 % comes from the top 0.05 eV. This window saturation is separate from k-mesh convergence, which is not established.
- Spread over grids and references: N_V = 1.62e+21-2.67e+21 cm^-3, m_h,DOS = 16.09-22.44 m0. Densest grid (80-atom k4, 14 k): 1.93e+21 cm^-3, 18.1 m0 (own maximum) and 17.7 m0 (off-Gamma VBM reference). Convergence error unestablished.
- HSE06 on the same k3 grid (own maxima): m_h,DOS 21.28 (q1) and 16.28 (q3) m0 against NC-PBE 22.97 m0, i.e. x0.709-0.926 (ESTIMATED: k3 grid only).
- The deck NV300 = 1e19 cm^-3 (ASSUMED) implies m_h,DOS = 0.542 m0; the computed value is about 30-41 times larger in mass and 160-270 times larger in N_V.

### 8.4 Slabs and W cells (in-plane)

| Slab | top band: m_h [100] / [110] (n = 3) | 2nd band (n = 3) | 3rd band (n = 3) | top-band tensor m_x / m_y / 2-D DOS / 2-D cond. (n = 3) | passes local screens? | N_V-equivalent m_h,DOS 2-D / quasi-3-D |
|---|---|---|---|---|---|---|
| 0.51 nm | 1.14 / 2.04 | -1.36 / -2.01 | 2.57 / -2.36 | 1.137 / 9.804 / 3.338 / 2.037 | no | 18.758 / 31.29 |
| 0.75 nm | 5.94 / 3.3 | -15.48 / 15.2 | -0.46 / -0.62 | 5.944 / 2.28 / 3.682 / 3.296 | yes | 12.527 / 18.19 |
| 1.0 nm | 38.17 / 8.56 | 2.03 / 2.48 | -18.66 / 11.04 | 38.173 / 4.82 / 13.565 / 8.56 | no | 24.718 / 23.56 |
| 2.0 nm | 2.65 / 6.3 | -5.51 / 27.05 | -19.04 / -27.05 | inconsistent (1/m_y < 0): not a parabolic D2h band | no | 32.492 / 17.19 |

- 0.51 nm: In8(OH)24 layer; the top VB is 98 % OH-oxygen O 2p; a second VB maximum on the 3x3x1 grid ([100], 0.196 1/A) lies 1.3 meV above VB(Gamma): multi-valley, the masses below are those of the Gamma maximum only. Fix: 6x6x1 nscf + [010] line (rectangular cell).
- 0.75 nm: top VB 75 % on OH oxygens; next band 29.1 meV lower (Boltzmann factor 0.32); polar slab without dipole correction: the curvature may change with a dipole correction. Fix: dipole-corrected SCF + bands.
- 1.0 nm: top two VBs within 3.3 meV at Gamma (degenerate on the kT scale); the top band is extremely flat along [100] (drop 0.1 meV at 0.03 1/A; 3-point mass has a 22.5 % print-rounding error) and crosses the next band near 0.1 1/A. Character of the pure 1 nm VB not projected (the W twin: 72 % OH). Fix: denser lines (0.005 1/A) with 6 decimals (verbosity high prints 4) or a fitted k.p model; projwfc of the pure 1 nm.
- 2.0 nm: VB top bulk-like (OH share 0.001) but the next band is 9.3 meV lower; the top band turns over along [100] (minimum near 0.075 1/A, rising again): only the n <= 4 window is parabolic. Fix: denser k-lines and a 2-D grid around Gamma.

- W bulk 8b: top VB (band 351) n = 3 masses [100] -38.17, [110] -19.1, [111] 38.16 m0; next band 0.0 meV below. 80-atom cubic cell: the bcc H point folds onto Gamma, so the valence states at Gamma mix Gamma and H; the top bands are within a few to 20 meV and nearly flat (drops of 0.1-0.3 meV at 0.015 1/A). Masses are listed for completeness only; the pure 80-atom H-L cell would be the like-for-like reference (no band run exists).
- W bulk 24d: top VB (band 351) n = 3 masses [100] 7.85, [110] 7, [111] 3.83 m0; next band 19.6 meV below. 80-atom cubic cell: the bcc H point folds onto Gamma, so the valence states at Gamma mix Gamma and H; the top bands are within a few to 20 meV and nearly flat (drops of 0.1-0.3 meV at 0.015 1/A). Masses are listed for completeness only; the pure 80-atom H-L cell would be the like-for-like reference (no band run exists).
- W slab 1 nm: ESTIMATED chord masses H2M k^2 / drop at the 3x3x1 grid points (0.20-0.29 1/A): NOT band-edge masses. W cell (VB band 311): drops 20.9, 23.6, 21 meV at 0.203, 0.203, 0.287 1/A, chord masses 7.5, 6.6, 14.9 m0; pure twin 5.2, 21.4, 13.9 m0. SCF grid only (k-path run missing; the 1 nm bands step failed in cdiaghg); VB top 72 % OH (W slabs). Fix: SCF + bands (CG) on the W-slab geometries (runs 1 and 2 of BANDS_MASSES.md Section 6).
- W slab 2 nm: ESTIMATED chord masses H2M k^2 / drop at the 3x3x1 grid points (0.20-0.29 1/A): NOT band-edge masses. W cell (VB band 663): drops 25.4, 9.9, 5.1 meV at 0.203, 0.203, 0.287 1/A, chord masses 6.2, 15.8, 61.6 m0; pure twin 21.8, 56, 23.3 m0. SCF grid only (k-path run missing; the 1 nm bands step failed in cdiaghg); VB top 72 % OH (W slabs). Fix: SCF + bands (CG) on the W-slab geometries (runs 1 and 2 of BANDS_MASSES.md Section 6).

### 8.5 TCAD recommendation for NV300

| t (nm) | NV300 (cm^-3) | form | label |
|---|---|---|---|
| 0.6953 | 1.95e+21 | quasi-3-D = Nv2D / t_HH (all subbands, 3x3x1 grid) | COMPUTED on a 4-k grid (coarse); polar slab |
| 0.9303 | 2.87e+21 | quasi-3-D = Nv2D / t_HH (all subbands, 3x3x1 grid) | COMPUTED on a 4-k grid (coarse) |
| 2.0 | 1.79e+21 | quasi-3-D = Nv2D / t_HH (all subbands, Boltzmann sum on the 3x3x1 grid) | COMPUTED on a 4-k grid (coarse; convergence unestablished); a single-subband quasi-2-D formula is NOT justified for holes: the top VBs are within 9 meV |
| 6.3 | 1.93e+21 | 3-D | ASSUMED transfer of the COMPUTED crystalline bulk value (PBE, 80-atom k4 grid, own-maximum reference; 1.6-2.7e21 over grids and references) to the device film |
| 13.2 | 1.93e+21 | 3-D | ASSUMED transfer of the COMPUTED crystalline bulk value (PBE, 80-atom k4 grid, own-maximum reference; 1.6-2.7e21 over grids and references) to the device film |

- Recommendation: the crystalline PBE valence-band DOS gives N_V of about 2e21 cm^-3 (COMPUTED on coarse grids: 1.6-2.7e21 in bulk, 1.8-2.9e21 quasi-3-D in the 0.7-2 nm slabs; HSE06 on the k3 grid suggests 0.6-0.9 times this). A constant NV300 = 2e21 cm^-3 at every device thickness would be ASSUMED, informed by these COMPUTED crystalline values (bulk-to-film transfer at 6.3 / 13.2 nm, crystalline-to-device transfer everywhere). A quasi-2-D single-subband N2D/t is not justified for holes (the top valence levels are within 3-30 meV); the slab values already sum all subbands. The frozen C10 parameters keep NV300 = 1e19 (ASSUMED) unless a sensitivity run is registered.
- Scope: N_V is a band integral of free (delocalised) valence states. Hybrid-functional work predicts that holes in In2O3 self-trap as small polarons (Varley et al. 2012); that does not change the band integral, but N_V alone does not describe equilibrium hole populations, hole mobility or polaron transport. No polaron calculation was done here.
- Effect on the present TCAD (electrons only): models fermi srh; method ... carriers=1 electrons (run_0061 device.in:81, :103): holes are not solved. n_i at 2 nm: 5.03e-10 cm^-3 (deck) -> 6.72e-09 cm^-3 (computed N_V); equilibrium SRH generation bound n_i/(2 tau) = 0.0034 cm^-3 s^-1; hole emission at the centre of the deep acceptor Gaussian (E_C - 0.6 eV) 3.95e-34 s^-1 (not a bound on the whole Gaussian or on field-assisted emission). In a two-carrier model the hole density is set by the local hole quasi-Fermi level, not the electron one: p > 1e10 cm^-3 needs that level within 0.67 eV of E_V. CALCULATED with ASSUMED capture parameters (sigma 1e-15 cm^2, v_th 1e7 cm/s, tau 1e-6 s): small for the electron current in these terms; not a bound on a two-carrier simulation.

### 8.6 Literature on In2O3 holes

| Statement | Citation | Relation to this work |
|---|---|---|
| Very shallow dispersion of the topmost VB; HSE03 VBM slightly off Gamma along G-H, VB(Gamma) only ~50 meV below | King et al., PRB 79, 205211 (2009), doi:10.1103/PhysRevB.79.205211 | same topology in PBE (VBM at 0.2 G-H) with a smaller offset (4.4 meV) |
| Upper valence bands of small dispersion; VB-top to CB dipole transitions forbidden or weak | Walsh et al., PRL 100, 167402 (2008), doi:10.1103/PhysRevLett.100.167402 | flatness confirmed: curvature masses 3-200 m0 near Gamma |
| Hybrid functional: holes self-trap as small polarons in In2O3 (favoured over free holes in all oxides studied except ZnO and SiO2), which prohibits p-type conductivity | Varley, Janotti, Franchini, Van de Walle, PRB 85, 081109(R) (2012), doi:10.1103/PhysRevB.85.081109 | band (free-hole) masses are therefore not the transport-relevant quantity for holes in In2O3; polarons not computed here |
| nKTB-mBJ DFT reports heavy- and light-hole masses for bixbyite In2O3 (electron mass 0.31 m0 in the abstract) | Halati et al., IET Optoelectron. 20, e70024 (2026), doi:10.1049/ote2.70024 | hole values not accessible here (publisher page 403); not compared |
| No experimental In2O3 hole effective mass located in this search | - | no measured benchmark |

**BM9**. (a) Bulk bands 174 (blue), 175 (orange), 176 (green) near Gamma along [100] = G-H (solid), [110] = G-N (dashed), [111] = G-P (dotted) from bands_gamma.out; open circles: the coarser bands_path.out points; open markers: the off-Gamma maxima ([100] circle = global VBM, [110] square). (b) Directional curvature masses vs fit window for the three bands (circle [100], square [110], triangle [111]); filled = falling band, open = rising band (absolute value plotted). (c) m_h,DOS from the Boltzmann-integrated valence DOS for four grids (filled: own grid maximum, open squares: off-Gamma VBM reference; triangles: HSE06 q1 / q3 on the k3 grid); dashed: the value implied by the deck NV300 = 1e19 cm^-3. (d) Top (solid) and second (dotted) valence band of the four slabs along [110] (left) and [100] (right), relative to VB(Gamma).

