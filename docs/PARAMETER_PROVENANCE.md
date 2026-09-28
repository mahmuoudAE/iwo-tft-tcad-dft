# Parameter provenance (every model parameter carries one label)

Labels: MEASURED_TARGET_DEVICE, MEASURED_RELATED_MATERIAL, DFT_TARGET_IWO (none available), DFT_PURE_IN2O3_PROXY, LITERATURE_IWO, LITERATURE_IN2O3_PROXY, CALCULATED, FITTED, NUMERICAL, ASSUMED.

| Parameter | Label | Source | Location | Notes |
|---|---|---|---|---|
| Bandgap | LITERATURE_IWO + DFT_PURE_IN2O3_PROXY | Fan2021 Sec.3 (bulk); Lin2022 Methods; Si2021 Fig.4 | Lin2022 p.21542; Si2021 p.504 | PBE absolute gaps not used |
| Electron affinity | LITERATURE_IWO + DFT_PURE_IN2O3_PROXY | Fan2021 Sec.3; Si2021 | Si2021 p.504 | absolute vacuum alignment not available; relative dEc only |
| Relative permittivity | MEASURED_TARGET_DEVICE | Januar2026 SI Fig.S1 (not bundled; recorded by Astra) | SI Fig.S1b | no thickness dependence imposed |
| Electron effective mass | MEASURED_RELATED_MATERIAL + DFT_PURE_IN2O3_PROXY | Stokey2021; Lin2022 | Stokey2021 Sec.IV.C; Lin2022 p.21540 | nonparabolicity ignored |
| Effective conduction-band DOS | CALCULATED | this work | - | 3-D continuum value; quasi-2D at 2 nm |
| Effective valence-band DOS | ASSUMED | - | - | holes not solved |
| Band mobility | FITTED | this work (real ATLAS) | - | no defensible law; percolation/crystallinity hypothesis |
| Roughness factor | LITERATURE_IWO | Januar2026 | Sec.2.9, Fig.5f |  |
| Constant mobility in deck | CALCULATED | this work | - | gate roll-off theta_r Vov not native (approximation gap) |
| Effective mobility | CALCULATED | - | - | reported as mu_FE from gm in EXPERIMENTAL_VS_SIMULATION |
| Effective background donor density | FITTED | this work; Kim2024 trend | Kim2024 p.6 | electrically active donors only |
| Flat-band carrier density | CALCULATED | - | - | Ioff ~ t n_FB used only as a consistency check |
| Bulk tail trap density | FITTED | this work; Januar2026 | Januar2026 Sec.2.8/2.10 | Januar Nt(2 nm)=5.3e19 with theta_t convention |
| Tail intercept density | CALCULATED | - | - | gTA = NTA exp((E-Ec)/WTA) |
| Tail energy width | FITTED | this work | - | Tt = 464 K; absolute Tt not in the paper |
| Deep acceptor density | ASSUMED | Fan2021 range | Fan2021 p.9 | insensitive; EGA from Ec |
| Interface trap density | ASSUMED | Lin2022; Wang2022 (HfO2/In2O3 6e11) | Lin2022 p.21539; Wang2022 p.4 | Gaussian at Ec-0.3 eV, W 0.12 eV; IWO/Al2O3 interface here |
| Fixed interface charge | FITTED (shared) + FITTED device-specific (6.3 nm) | this work | - | dVfb = -q Qf/Cox = -0.310 V (2 nm), -0.016 V (6.3 nm) |
| Capture cross sections | ASSUMED | - | - | not identifiable from DC |
| Gate work function | ASSUMED | TiN literature range 4.5-4.9 | - | degenerate with chi and Qf |
| S/D contact | ASSUMED (+FITTED for 31.8 nm) | Si2022/Lin2022 (CNL) context | - |  |
| SRH lifetimes | ASSUMED | - | - | negligible |
| Channel length / width | MEASURED_TARGET_DEVICE | schematic | - | A/um normalization |
| Gate-stack capacitance | CALCULATED | SI Fig.S1 (HfO2), Al2O3 eps assumed | - | EOT 3.86 nm |

## Numerical (label NUMERICAL, from config/solver.yaml)

| Item | Value | Evidence |
|---|---|---|
| XANDRNORM + CR.TOLER (strict, depletion) | 1e-17 A scaled by 1e-5 x min active current | Claude run_0006/0009/0010/0011/0018 |
| CR.TOLER (on-state) | 5e-18 default, ^XANDRNORM | Claude run_0011 |
| IR.TOL | 1e-19 A | - |
| MAXTRAPS / ITLIMIT / CLIMIT | 10 / 80 / 1e-6 | documented range |
| DOS levels NUMA/NUMD | 96/48 | x2 check: 0.006 dec (run_0016) |
| vertical mesh | 0.25 nm (2 nm film), 0.0625 nm at interface layer, graded to 1 nm in thick films | mesh x0.5: 0.005 dec (run_0015); x0.7 for 13.2 nm: 0.004 dec (run_0026) |
| interface regularization layer | 0.25 nm | layer /2: 0.009 dec (run_0017) |
| gate step | 0.05 V logged, 0.1 V continuation | - |
