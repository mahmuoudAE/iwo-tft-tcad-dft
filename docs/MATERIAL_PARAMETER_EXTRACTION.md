# Material-parameter extraction: derivations and calculations

All formulas below are implemented in `scripts/material_laws.py` (laws) and `scripts/build_iwo_decks.py` (deck values); the evidence table is `tables/THICKNESS_LAW_EVIDENCE.csv`, the evaluated laws `tables/THICKNESS_LAWS.csv`.

## 1. Quantum-confinement band-edge shift dEg_QC(t) (proxy: pure In2O3, PBE)

Only slab-minus-bulk shifts are used, never PBE absolute gaps (PBE bulk 0.94 eV vs 2.9-3.2 eV experiment).

| source | t (nm) | shift (eV) | how |
|---|---|---|---|
| Lin 2022 (H-passivated slab, vacuum, ONCV/PBE 140 Ry) | 1.98 | +0.33 | 1.27 - 0.94 |
| Lin 2022 | 0.95 | +0.94 | 1.88 - 0.94 |
| Si 2021 (In2O3 on Al2O3, PAW/PBE 420 eV) | 1.5 | +0.60 | dEc, "Ev almost unchanged" |

Log-log least squares: dEg_QC(t) = 0.921 t^-1.382 eV (t in nm). An ideal infinite well gives t^-2; the smaller exponent reflects nonparabolicity and finite barriers. Evaluated: 0.353 (2.0), 0.072 (6.3), 0.026 (13.2), 0.008 eV (31.8). Partition dEc = dEg (Si 2021). The 3.52 nm slab gap of Lin 2022 is not printed in the text and could not be used.

Caveats (labelled DFT_PURE_IN2O3_PROXY): pure In2O3, crystalline slabs, H/Al2O3 terminations vs the air/Al2O3 boundaries of the amorphous IWO film; W raises m* and would weaken confinement. Uncertainty taken as +/-50 % on dEg.

## 2. Eg(t), chi(t)

Eg(t) = 3.05 + dEg_QC(t); chi(t) = 4.30 - dEc(t). Bulk values are Fan 2021 priors for a different sputtered IWO (LITERATURE_IWO). The absolute chi is uncertain by ~0.3 eV and degenerate with the gate work function and Qf; only the THICKNESS DIFFERENCES of chi (0.35 eV between 2 and 13.2 nm) are used as a physical constraint. Absolute vacuum-aligned values would come from the QE slab workflow (qe_workflow/, unexecuted).

TNL consistency: bulk In2O3 CNL/TNL ~0.4 eV above Ec (Si 2021, Lin 2022, Wang 2022). With Ec rising by dEc(t) and the TNL fixed in absolute energy, TNL - Ec(t) = 0.4 - dEc(t): +0.05 eV at 2 nm (still slightly above Ec for pure In2O3); W doping lowers the carrier density further (Januar). The model therefore expects EF farther below Ec and a more positive Vth for thinner films, as observed (measured Vth_cc: 0.66 V at 2 nm vs 0.08 V at 13.2 nm).

## 3. Effective mass and Nc(t)

m*(t) = 0.208 + 0.131 t^-1.412 m0. 0.208 m0 is the measured bulk value (optical Hall, Stokey 2021; Feneberg's zero-density extrapolation 0.18); the increment is the PBE slab-minus-bulk difference from Lin 2022 (0.02, 0.06, 0.13 m0 at 3.52, 1.98, 0.95 nm).

Nc = 2 (2 pi m* k T / h^2)^{3/2} = 2.509e19 (m*/m0)^{3/2} cm^-3 at 300 K -> 3.27e18 (2.0 nm), 2.55e18 (6.3), 2.44e18 (13.2), 2.40e18 (31.8). The Astra/Claude seed 5e18 corresponds to m* = 0.34 m0. At 2 nm the film holds ~2 subbands within kT-scale energies of the ground state only at high density; Nc is used as an effective continuum parameter (stated limitation). Nv = 1e19 (ASSUMED; holes not solved).

## 4. Permittivity

eps_IWO = 9.30 (C-V on the target process, SI Fig. S1; MEASURED_TARGET_DEVICE), eps_In2O3 = 9.03 (same), bulk-crystal static 10.55 (Stokey 2021), evaporated films 8.9 (Hamberg). No thickness dependence imposed. Sensitivity: 9.3 -> 10.55 changes the semiconductor capacitance term only; for a 2 nm film in series with Cox it changes the accumulation charge by < 1 % (t/eps_s << EOT).

## 5. Tail states: Nt(t), Tt

ATLAS tail: g_TA(E) = NTA exp[(E - Ec)/WTA] (acceptor-like, E below Ec). Integral over the gap: Nt = NTA WTA [1 - exp(-Eg/WTA)] ~ NTA WTA. WTA = k Tt.

Anchor: the real-ATLAS calibrations of both lineages give Nt(2 nm) = NTA WTA = 2.0e19 (Claude) / 2.2e19 (Astra) cm^-3, Nt(6.3) = 1.3-1.5e19, Nt(13.2) = 2.5-4.6e18 -> exponent 0.7-0.8; Januar 2026 reports ~4x between 13.2 and 2 nm (exponent 0.73) and Nt(2 nm) = 5.3e19 in the theta_t convention of Eq. (8). Law: Nt(t) = 2.0e19 (2/t)^0.75 cm^-3; WTA = 0.040 eV shared (Tt = 464 K; Astra 0.035-0.040, Claude 0.036-0.044). Absolute Tt is NOT DETERMINED from the paper (only dTt). NTA(t) = Nt/WTA: 5.0e20, 2.1e20, 1.2e20, 6.3e19 cm^-3/eV.

## 6. Effective donor density Nd_eff(t)

Not the W concentration (2 at.% W = ~6e20 cm^-3 W atoms; the electrically active donor density is 3-4 orders lower). Law: Nd_eff(t) = 2.5e17 [1 + (t/20 nm)^4] cm^-3 -> 2.5e17, 2.5e17, 3.0e17, 1.85e18. Support: both lineages need ~2-3e17 for the thin films and >1e18 for 31.8 nm; Kim 2024 finds bulk/border trap densities rising 2.4 -> 3.1 -> 14.6e18 from 10 to 30 nm (different process). Label FITTED law (3 parameters for four films). n_FB(t) is a solver output (equilibrium free-electron density), reported per run.

## 7. Mobility

mu0(t) = mu_band(t) (1 - Dsr/t)^2 with Dsr = 2.87 A (Januar Fig. 5f). Roughness factor 0.734, 0.911, 0.957, 0.982. mu_band is FITTED per thickness (V0 values 16.8, 12.4, 57.6, 84 cm^2/Vs); the step between 6.3 and 13.2 nm is not explained by roughness and is hypothesised to be percolation/crystallinity (Januar Fig. S2-S4: nanoscale grains; Kim 2024: optimum at 20 nm). The gate-dependent partition mu_eff = n_free/(n_free + n_tail + n_it) mu_max is realised by the solver's DOS occupancy; the Ando roll-off mu0/(1 + theta_r Vov) is NOT inserted (no native equivalent; MOBILITY updates between SOLVEs are ignored by this ATLAS).

## 8. Interface states and Qf

Dit: acceptor Gaussian sheet 3e11 cm^-2 eV^-1 at Ec - 0.3 eV, W = 0.12 eV (ASSUMED, shared). Literature HfO2/In2O3 Dit ~6e11 (Lin 2022, Wang 2022); the target interface is IWO/Al2O3 (2 nm Al2O3 interlayer) and is expected to be at least as good (Januar: smoother IWO/high-k interface). Implementation: volume Gaussian in the 0.25 nm layer with amplitude 3e11 / 2.5e-8 cm = 1.2e19 cm^-3 eV^-1, moment-matched with the bulk deep Gaussian (verified equivalence in V0). Qf: one shared value (FITTED, stage 3), dVfb = -q Qf / Cox.

## 9. Cox

Cox = eps0 / (15 nm/19.57 + 2 nm/9.0) = 8.955e-7 F/cm^2 (EOT 3.86 nm); Cox/q = 5.59e12 cm^-2 V^-1.

## 10. Apparent field-effect mobility (extraction, same for exp and sim)

mu_FE = gm_max L / (W Cox Vd), W = 1 um for A/um data, L = 20 um, Vd = 0.7 V. Measured: 12.1 (2.0), 10.9 (6.3), 50.2 (13.2), 49.2 (31.8) cm^2/Vs (paper reports mu_max 5.1 -> 27.4 for 2 -> 13.2 nm with a different extraction).
