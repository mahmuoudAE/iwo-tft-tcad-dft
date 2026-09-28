# Material parameters used in the simulation (V1)

Values are those written to the decks (see decks/*_metadata.json). Label = provenance class; no fitted value is called measured.

| Parameter | Symbol | ATLAS | Units | 2.0 nm | 6.3 nm | 13.2 nm | 31.8 nm | Law | Label | Source | Uncertainty |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bandgap | Eg(t) | EG300 | eV | 3.403 | 3.122 | 3.076 | 3.058 | Eg_bulk + dEg_QC(t), dEg_QC = 0.920 t^-1.381 | LITERATURE_IWO + DFT_PURE_IN2O3_PROXY | Fan2021 Sec.3 (bulk); Lin2022 Methods; Si2021 Fig.4 | +/-0.2 eV bulk; +/-50 % on dEg |
| Electron affinity | chi(t) | AFFINITY | eV | 3.947 | 4.228 | 4.274 | 4.292 | chi_bulk - dEc(t), dEc = dEg (Ev fixed) | LITERATURE_IWO + DFT_PURE_IN2O3_PROXY | Fan2021 Sec.3; Si2021 | +/-0.3 eV absolute |
| Relative permittivity | eps_r | PERMITTIVITY | - | 9.3 | 9.3 | 9.3 | 9.3 | shared | MEASURED_TARGET_DEVICE | Januar2026 SI Fig.S1 (not bundled; recorded by Astra) | +/-0.04 (SI); bulk crystal 10.55 (Stokey2021) |
| Electron effective mass | m*(t) | (none; enters Nc) | m0 | 0.2573 | 0.2177 | 0.2114 | 0.209 | 0.208 + 0.131 t^-1.412 | MEASURED_RELATED_MATERIAL + DFT_PURE_IN2O3_PROXY | Stokey2021; Lin2022 | +/-0.03 m0 |
| Effective conduction-band DOS | Nc(t) | NC300 | cm^-3 | 3.274e+18 | 2.550e+18 | 2.440e+18 | 2.398e+18 | 2(2 pi m* kT/h^2)^1.5 | CALCULATED | this work | x0.8-1.3 |
| Effective valence-band DOS | Nv | NV300 | cm^-3 | 1.0e+19 | 1.0e+19 | 1.0e+19 | 1.0e+19 | shared | ASSUMED | - | x10 |
| Band mobility | mu_band(t) | (enters MUN) | cm^2/Vs | 18.13 | 11.69 | 61.9 | 84 | per thickness | FITTED | this work (real ATLAS) | see SENSITIVITY_RESULTS |
| Roughness factor | (1-Dsr/t)^2 | - | - | 0.7336 | 0.911 | 0.957 | 0.982 | Dsr = 2.87 A | LITERATURE_IWO | Januar2026 | unit ambiguity A vs nm noted |
| Constant mobility in deck | mu0(t) | MUN | cm^2/Vs | 13.3 | 10.65 | 59.24 | 82.49 | mu_band(t) (1-Dsr/t)^2 | CALCULATED | this work | - |
| Effective mobility | mu_eff(Vg) | (solver output: n_free/(n_free+n_trap) x mu0) | cm^2/Vs | solver | solver | solver | solver | from DOS occupancy | CALCULATED | - | - |
| Effective background donor density | Nd_eff(t) | DOPING N.TYPE CONC | cm^-3 | 2.500e+17 | 2.525e+17 | 2.974e+17 | 1.848e+18 | Nd0(1+(t/tc)^k), Nd0=2.5e+17, tc=20 nm, k=4 | FITTED | this work; Kim2024 trend | x2 |
| Flat-band carrier density | n_FB(t) | (solver equilibrium n) | cm^-3 | solver | solver | solver | solver | from equilibrium solution | CALCULATED | - | - |
| Bulk tail trap density | Nt(t) | (NTA*WTA) | cm^-3 | 2.000e+19 | 8.459e+18 | 4.857e+18 | 2.512e+18 | Nt2 (2/t)^alpha, Nt2=2.0e+19, alpha=0.75 | FITTED | this work; Januar2026 | x2 |
| Tail intercept density | NTA(t) | NTA | cm^-3/eV | 5.000e+20 | 2.115e+20 | 1.214e+20 | 6.279e+19 | Nt/WTA | CALCULATED | - | - |
| Tail energy width | WTA = kTt | WTA | eV | 0.04 | 0.04 | 0.04 | 0.04 | shared | FITTED | this work | +/-0.005 eV |
| Deep acceptor density | NGA | NGA | cm^-3/eV | 5.0e+16 | 5.0e+16 | 5.0e+16 | 5.0e+16 | shared | ASSUMED | Fan2021 range | x10 |
| Interface trap density | Dit | regularized NGA in region 2 (sheet/0.25 nm) | cm^-2 eV^-1 | 3.0e+11 | 3.0e+11 | 3.0e+11 | 3.0e+11 | shared | ASSUMED | Lin2022; Wang2022 (HfO2/In2O3 6e11) | x3 |
| Fixed interface charge | Qf | INTERFACE QF | cm^-2 | 1.730e+12 | 8.700e+10 | 1.730e+12 | 1.730e+12 | shared value 1.73e12; 6.3 nm DEVICE-SPECIFIC 8.7e10 (cause NOT DETERMINED) | FITTED (shared) + FITTED device-specific (6.3 nm) | this work | - |
| Capture cross sections | sigma | SIGTAE.. SIGGDH | cm^2 | 1e-15 | 1e-15 | 1e-15 | 1e-15 | shared | ASSUMED | - | x100 |
| Gate work function | Phi_TiN | CONTACT WORKFUNCTION | eV | 4.7 | 4.7 | 4.7 | 4.7 | shared | ASSUMED | TiN literature range 4.5-4.9 | +/-0.2 eV |
| S/D contact | Pd/IWO | CONTACT (no WF) [+RESISTANCE] | ohm.um | 0 | 0 | 0 | 9.2e+04 | ideal Ohmic; 31.8 nm series R | ASSUMED (+FITTED for 31.8 nm) | Si2022/Lin2022 (CNL) context | underconstrained (no TLM) |
| SRH lifetimes | tau_n, tau_p | TAUN0 TAUP0 | s | 1e-06 | 1e-06 | 1e-06 | 1e-06 | shared | ASSUMED | - | x100 |
| Channel length / width | L / W | geometry / MESH WIDTH | um | 20 / 290 (sim 1) | 20 / 290 (sim 1) | 20 / 290 (sim 1) | 20 / 290 (sim 1) | - | MEASURED_TARGET_DEVICE | schematic | - |
| Gate-stack capacitance | Cox | (from eps and thickness) | F/cm^2 | 8.9554e-07 | 8.9554e-07 | 8.9554e-07 | 8.9554e-07 | eps0/(15 nm/19.57 + 2 nm/9.0) | CALCULATED | SI Fig.S1 (HfO2), Al2O3 eps assumed | +/-5 % |
