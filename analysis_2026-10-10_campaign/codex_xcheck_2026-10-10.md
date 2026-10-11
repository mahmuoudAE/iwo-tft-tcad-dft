# Codex cross-check of the DFT read-out (2026-10-10)

- **What this is.** The final answer of an independent, read-only Codex run (codex-cli 0.162.0 in WSL "Ubuntu", `codex exec --sandbox read-only`). Codex wrote its own parsing scripts and read the same QE output files. It did not see Claude's numbers.
- **Prompt.** It asked for the 2 nm W-slab band characters and filling, the gap, EA, IP, H-to-H thickness, mass and E2-E1 of the 0.5, 0.75, 1 and 2 nm slabs, the surface-state shares of the thin slabs, and the bulk gap and mass.
- **Agreement with `dft_to_tcad_extract.py`.** Every shared number agrees to the printed digits. The masses differ by at most 0.001 m0 because Codex fits through the origin.
- **Status.** This is unedited Codex output. It is data, not a decision.

---
**The band-count correction is confirmed:** \(n_\text{pure}=1328/2=664\), but the IWO VBM is **band 663**, and its host CB bottom is **band 664**. Bands **666–668** have substantial W-5d character; band 665 is predominantly host-like.

All work was read-only, using local files and standard-library Python. No network or simulator was used.

The source keys below specify the exact files and line patterns used. Line numbers are one-based.

- **A-S:** `iwo_slab2_final_cpu/scf.out`: `number of atoms/cell` at line **53**, `number of electrons` at **55**, `the Fermi energy is` at **2872**. `iwo_slab2_final_cpu/scf.in` line **7** specifies `occupations = 'smearing', smearing = 'mv', degauss = 0.01`.
- **A-P:** `iwo_slab2_final_cpu/projwfc_iwo_slab2_final_cpu.out`, first `k = 0 ... 0` block. The `==== e( N) = ... eV ====` lines for bands **661–668** are respectively **21987, 22012, 22036, 22058, 22093, 22138, 22158, 22196**. Weights were summed from the following `psi = ...*[# k]` terms, using the `state # ... atom ... (El) ... (l=...)` mapping. W is atom **87**; its d states **543–547** are mapped at lines **613–617**.
- **P-S/P-P:** `slab2r_pdos_cpu/scf.out`: atoms **53**, electrons **55**, last `highest occupied, lowest unoccupied level` **2646**. In `slab2r_pdos_cpu/projwfc_slab2r_pdos_cpu.out`, Gamma bands **664/665** have energy headers at **22999/23034**; their printed O-p/In-s weights are **0.920/0.584**, respectively.
- **V:** Each folder’s `<folder>_avg.dat`, numeric rows `z planar macroscopic`; only **column 2** was averaged. Selected line ranges: IWO, pure twin and `slab2_relax_c2`: **1–133 and 2869–3000**; L1: **1–200 and 2802–3000**; L2: **1–185 and 2817–3000**; `slab1r_final_cpu`: **1–173 and 2829–3000**. Boundary distances used the z cell length from `CELL_PARAMETERS angstrom` in `scf.in`, rather than treating the final grid point as the boundary.
- **B-S:** Last `highest occupied, lowest unoccupied level (ev):` in each `scf.out`: L1 **1389**, L2 **1771**, `slab1r_final_cpu` **1884**, `slab2_relax_c2` **2855**. Electron-count lines **54, 54, 295, 51**, respectively, give \(n_\text{occ}=136,224,312,664\).
- **B-G:** Each `scf.in`: `CELL_PARAMETERS angstrom` at **17**, cell vectors **18–20**, `ATOMIC_POSITIONS crystal` at **21**. H coordinate blocks: L1 **54–77**, L2 **74–97**, `slab1r_final_cpu` **94–117**, `slab2_relax_c2` **174–197**. Thickness uses Cartesian H \(z_\max-z_\min\).
- **B-M:** Each `bands.out`, first 11 `k = ... bands (ev):` blocks, extracting band \(n_\text{occ}+1\). The cutoff retained the first **four** points, including Gamma. Their CB-energy lines are L1 **549,571,593,615**; L2 **556,589,622,655**; `slab1r_final_cpu` **832,876,920,964**; `slab2_relax_c2` **855,943,1031,1119**. Printed `lattice parameter (alat)` occurs at **54,54,295,51**, respectively. Gamma next-level differences use bands \(n_\text{occ}+1,n_\text{occ}+2\) on **549,556,832,855**, respectively.
- **B-P:** `slabL1_relax_v2/projwfc_slabL1_relax_v2.out`: VBM headers **2348,4979,7751,10667**, CBM **2361,4992,7770,10686**. `slabL2_relax_v2/projwfc_slabL2_relax_v2.out`: VBM **4672,10043,15451,21272**, CBM **4692,10062,15470,21291**. The same state-map and `psi` patterns were used.
- **C:** `../../bulk_In2O3_protocol/bands_path.out`: band-176 maximum **8.0785 eV**, line **954**, fourth k-point; band-177 minimum **8.9672 eV**, line **874**, first k-point, over **80** listed k-points. `../../bulk_In2O3_protocol/bands_gamma.out`: `alat` line **58**; band-177 fit energies at **680,707,734,761**, within the first 11 points.

The mass fits were constrained through the origin:
\[
\Delta E=A k^2,\qquad m^*/m_0=3.80998212/A.
\]
The largest fit residual across the slab fits was **0.00010 eV**.

For filling, all four SCF k-points were printed. `A-S` lines **532–535** give weights **0.2222222, 0.4444444, 0.4444444, 0.8888889**, which already sum to approximately **2**, including spin. I used Marzari–Vanderbilt cold smearing with \(\sigma=0.1360569312\) eV:
\[
N_b=\sum_k w_k\left[\tfrac12\operatorname{erfc}(1/\sqrt2-x)
+\frac{e^{-(x-1/\sqrt2)^2}}{\sqrt{2\pi}}\right],
\quad x=(E_F-E_{bk})/\sigma .
\]
Band 664 eigenvalues occur at **2248,2425,2602,2779**; bands 665–668 at **2249,2426,2603,2780**. Corresponding `occupation numbers` are at **2336/2337,2513/2514,2690/2691,2867/2868**. The reconstruction totals **1329.00009 electrons**. Cold-smearing occupations can exceed one, explaining the host band’s filling above two. “Up to \(E_F+0.5\)” includes bands with **any sampled eigenvalue** below **2.8496 eV**; this includes band 668.

Surface shares are the arithmetic mean of each k-point’s surface weight divided by its total **printed projected weight**. Surface atoms comprise H plus O within 1.15 Å of H, using periodic minimum-image distances. L1 has **24 H + 24 O**; L2 also has **24 H + 24 O**. The L1 VBM is overwhelmingly on OH-associated O-p orbitals. The L2 VBM is surface-enriched but appreciably distributed beyond those atoms. Neither CBM is surface-dominated by this measure. These projections support that distinction; they do not establish strict spatial localization.

| System / quantity | Result | Source |
|---|---|---|
| IWO electrons; atoms; smearing; \(E_F\) | **1329; 176; MV, 0.01 Ry; 2.3496 eV** | A-S |
| Pure twin electrons; atoms; \(n_\text{pure}\) | **1328; 176; 664** | P-S |
| IWO Gamma band 661: energy; W-d / In-s / O-p weight | **0.02908; 0 / 0 / 0.925** | A-P |
| IWO Gamma band 662 | **0.03089; 0 / 0 / 0.920** | A-P |
| IWO Gamma band 663 — VBM | **0.03502; 0 / 0 / 0.896** | A-P |
| IWO Gamma band 664 — host CB bottom | **1.11129; 0 / 0.555 / 0.060** | A-P |
| IWO Gamma band 665 — host-like | **1.86667; 0.005 / 0.446 / 0.131** | A-P |
| IWO Gamma band 666 — W-d-derived | **2.45267; 0.524 / 0.106 / 0.200** | A-P |
| IWO Gamma band 667 — mixed W-d-derived | **2.56879; 0.260 / 0.229 / 0.191** | A-P |
| IWO Gamma band 668 — mixed W-d-derived | **2.87716; 0.279 / 0.188 / 0.209** | A-P |
| IWO Gamma gap; \(E_F-E_\mathrm{CB}\) | **1.07627; 1.23831 eV** | A-P, A-S |
| IWO W-band offsets from host CB, bands 666/667/668 | **1.34138 / 1.45750 / 1.76587 eV** | A-P |
| IWO \(E_\mathrm{vac}\); EA; IP | **5.85757; 4.74628; 5.82255 eV** | V, A-P |
| Pure twin Gamma VBM; CB; gap | **0.04746; 1.27133; 1.22387 eV** | P-P |
| Pure twin \(E_\mathrm{vac}\); EA; IP | **5.76630; 4.49497; 5.71884 eV** | V, P-P |
| IWO electrons in bands 664/665/666/667/668 | **2.040885 / 0.861597 / 0.096754 / 0.000919 / \(4.67\times10^{-9}\)** | A-S eigenvalues, weights, cold-smearing reconstruction |
| L1 HOMO; LUMO; gap | **−4.7219; −1.5818; 3.1401 eV** | B-S |
| L1 \(E_\mathrm{vac}\); EA; IP | **1.60991; 3.19171; 6.33181 eV** | V, B-S |
| L1 H thickness; in-plane \(a,b\) | **4.61181 Å (0.46118 nm); 10.69545, 10.01879 Å** | B-G |
| L1 CB mass; next-empty separation at Gamma | **0.42917 \(m_0\); 1.8872 eV** | B-M |
| L1 surface atom fraction; VBM/CBM surface shares | **48/56 = 85.714%; 98.458% / 56.281%** | B-G, B-P |
| L2 HOMO; LUMO; gap | **−3.3537; −1.1551; 2.1986 eV** | B-S |
| L2 \(E_\mathrm{vac}\); EA; IP | **2.56258; 3.71768; 5.91628 eV** | V, B-S |
| L2 H thickness; in-plane \(a,b\) | **6.95317 Å (0.69532 nm); 10.42840, 10.29283 Å** | B-G |
| L2 CB mass; next-empty separation at Gamma | **0.33479 \(m_0\); 1.8152 eV** | B-M |
| L2 surface atom fraction; VBM/CBM surface shares | **48/76 = 63.158%; 75.801% / 35.795%** | B-G, B-P |
| `slab1r_final_cpu` HOMO; LUMO; gap | **−2.3403; −0.5518; 1.7885 eV** | B-S |
| `slab1r_final_cpu` \(E_\mathrm{vac}\); EA; IP | **3.37670; 3.92850; 5.71700 eV** | V, B-S |
| `slab1r_final_cpu` H thickness; \(a,b\) | **9.30334 Å; 10.33643, 10.33450 Å** | B-G |
| `slab1r_final_cpu` CB mass; next-empty separation | **0.28145 \(m_0\); 1.4988 eV** | B-M |
| `slab2_relax_c2` HOMO; LUMO; gap | **0.0473; 1.2712; 1.2239 eV** | B-S |
| `slab2_relax_c2` \(E_\mathrm{vac}\); EA; IP | **5.76623; 4.49503; 5.71893 eV** | V, B-S |
| `slab2_relax_c2` H thickness; \(a,b\) | **19.62327 Å; 10.31792, 10.30849 Å** | B-G |
| `slab2_relax_c2` CB mass; next-empty separation | **0.20603 \(m_0\); 0.7191 eV** | B-M |
| Bulk VBM maximum; CBM minimum; fundamental path gap | **8.0785; 8.9672; 0.8887 eV** | C |
| Bulk Gamma CB mass | **0.15825 \(m_0\)** | C |

Could not determine:

- **Pure-twin \(E_F-E_\mathrm{CB}\):** its fixed-occupation SCF output reports HOMO/LUMO, with no Fermi energy.
- **Pure-twin W-derived offsets:** no W atom or W projection exists.
- **Exact untruncated projection shares:** `psi` coefficients are rounded and omit small contributions. Reported zero weights mean no printed contribution.
- **A definitive localization label for the L2 VBM:** the requested projection measure establishes surface enrichment, but does not by itself establish localization.