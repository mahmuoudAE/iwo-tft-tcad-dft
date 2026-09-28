# Quantum ESPRESSO workflow (NOT EXECUTED)

pw.x is not available on this machine. These inputs define the matrix xW = {0, ~1.6-3.1 %} x thickness {bulk, ~1, ~2, ~3 nm}.

| case | atoms | formula |
|---|---|---|
| bulk_In2O3 | 80 | In32O48 |
| bulk_IWO_1W_3p1pct | 80 | In31O48W |
| bulk_IWO_1W_1p6pct_112 | 160 | In63O96W |
| slab_1p0nm_In2O3 | 96 | H16In32O48 |
| slab_1p0nm_IWO_1W | 96 | H16In31O48W |
| slab_2p0nm_In2O3 | 176 | H16In64O96 |
| slab_2p0nm_IWO_1W | 176 | H16In63O96W |
| slab_3p0nm_In2O3 | 256 | H16In96O144 |
| slab_3p0nm_IWO_1W | 256 | H16In95O144W |

## Convergence tests required before any number replaces a proxy
- ecutwfc 50/71/90 Ry (PAW) or 100/140 Ry (ONCV); k-grid 4/6/8 (bulk), 3x3x1 vs 5x5x1 (slabs); vacuum 15/25/35 A; slab thickness series; W configuration (8b vs 24d, W-W separation); relaxation force < 1e-3 Ry/Bohr.
## Extraction
- Eg: PBE gaps are underestimated (bulk ~0.9 eV vs 2.9-3.2 exp); use ONLY slab-minus-bulk shifts (dEg_QC). For absolute values use HSE06 on the relaxed bulk.
- dEc/dEv: vacuum-aligned CBM/VBM from the planar-averaged electrostatic potential (pp.x plot_num=11 -> average.x); chi = Evac - Ec directly.
- m*: parabolic fit of the lowest conduction band within 0.05 A^-1 of Gamma (bands.x); report nonparabolicity.
- DOS/PDOS: projwfc.x; W-5d weight at the CBM.
- eps: ph.x DFPT (bulk only; eps_inf and eps_0 from the Born charges/phonons).
- V_O: neutral and +2 vacancy supercells (In2O3 and IWO), formation energy vs O chemical potential, transition levels with Makov-Payne/FNV correction; W substitution energy from the same references.
## Caveat
Crystalline periodic supercells approximate the sputtered, largely amorphous IWO film only in trend; results are proxies until compared with the measured devices.
