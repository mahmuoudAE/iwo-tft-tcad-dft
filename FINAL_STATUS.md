# FINAL STATUS - IWO_PHYSICS_CONSTRAINED_MODEL_V1 (2026-09-21)

## What was delivered

One thickness-aware ATLAS material model M(t) for ~2 at.% W:In2O3 (config/iwo_material_model.yaml), generated decks in the physical device structure, 15 real ATLAS launches on the local licensed installation (results/RUN_INDEX.csv; every launch keeps its deck, DeckBuild log, transfer.log and exports), supervisor tables, plots, provenance and bibliography. The final set is four runs: 2 nm (calibrated), 13.2 nm (calibrated), 6.3 nm (validation with the shared parameters) and, at the user's later request, 6.3 nm tuned (device-specific offset + mobility). The 31.8 nm device is excluded from the final set (its two runs are kept as evidence).

## Result (same extractor for measured and simulated curves; tables/EXPERIMENTAL_VS_SIMULATION.md)

| t (nm) | run | role | Vth_cc exp / sim (V) | SS_min exp / sim (mV/dec) | mu_FE exp / sim (cm^2/Vs) | Ion exp / sim (A/um) | active log RMSE (dec) |
|---|---|---|---|---|---|---|---|
| 2.0 | run_0012 | calibrated | 0.66 / 0.68 | 84 / 73 | 12.1 / 11.3 | 5.09e-7 / 5.09e-7 (+0.0 %) | 0.037 |
| 13.2 | run_0013 | calibrated | 0.08 / 0.05 | 131 / 151 | 50.2 / 49.0 | 3.07e-6 / 3.07e-6 (-0.0 %) | 0.081 |
| 6.3 | run_0014 | VALIDATION (shared parameters, nothing tuned) | 0.64 / 0.35 | 115 / 108 | 10.9 / 9.1 | 4.03e-7 / 5.11e-7 (+26.8 %) | 0.678 |
| 6.3 | run_0015 | TUNED (device-specific Qf 8.7e10 = +0.29 V offset, mu_band 11.69) | 0.64 / 0.65 | 115 / 111 | 10.9 / 8.4 | 4.03e-7 / 4.03e-7 (-0.0 %) | 0.063 |

Ioff: the simulated off-state is native zero / 1e-20 A/um; the measured floors (5e-15, 1.5e-13, 6.6e-12 A/um) are not modelled, so Ion/Ioff is a lower bound in the simulation and is not compared in per cent (docs/LIMITATIONS.md).

Free quantities in the shared model: ONE fitted electrostatic value (Qf = 1.73e12 cm^-2, equivalently a -0.31 V flat-band offset that absorbs the unmeasured absolute band alignment) and one fitted band mobility per thickness (18.13, 11.69 and 61.9 cm^2/Vs for 2, 6.3 and 13.2 nm). The 6.3 nm film additionally needs ONE device-specific flat-band offset (Qf 8.7e10 instead of 1.73e12, i.e. +0.29 V), added at the user's request after the validation run had shown the miss; its cause is NOT DETERMINED FROM AVAILABLE DATA and it is not part of the shared laws. Everything else is a law or a literature/measured value with a provenance label (tables/PARAMETER_PROVENANCE.csv).

## What the validation says

With the parameters fixed on 2 and 13.2 nm, the 6.3 nm device is reproduced in SHAPE (SS_min 108 vs 115 mV/dec; SS over the 1e-10..1e-8 A/um band 285 vs 295 mV/dec) but its threshold is predicted 0.29 V too negative; the +27 % on-current is the consequence of that overdrive error, not of the mobility. With one device-specific flat-band offset and its own band mobility (run_0015) the same film fits to 0.063 dec with Ion within 0.02 %, Vth within 10 mV and SS within 4 mV/dec, i.e. as well as the other two. The measured 6.3 nm threshold equals the 2 nm one although every monotonic thickness law places it between the 2 and 13.2 nm values. The shared model therefore does NOT predict the 6.3 nm threshold; the tuned run shows that one electrostatic number is all it misses; the cause is NOT DETERMINED FROM AVAILABLE DATA.

## Physics conclusions supported by the runs

1. The pure-In2O3 DFT confinement proxy (dEc = 0.35 eV between 2 and 13.2 nm) together with Nc(t), Nt(t) and Nd(t) accounts for the measured 0.58 V threshold difference between 2 and 13.2 nm: with the laws alone both devices were offset by the same +0.3 V (runs 0001/0002, offsets agreeing to 40 mV), and one shared Qf removed the offset for both (runs 0003/0004).
2. The subthreshold shapes at 2 and 13.2 nm follow from the tail-state law Nt(t) = 2e19 (2/t)^0.75 cm^-3 with one shared WTA = 0.040 eV and a shared interface Dit of 3e11 cm^-2 eV^-1 without tuning.
3. The band mobility is not predicted: 18.1 (2 nm) vs 61.9 cm^2/Vs (13.2 nm) after the roughness factor; the step between 6 and 13 nm has no defensible law.
4. The physical-structure deck (Air, Pd volumes, Al2O3, HfO2, Conductor gate) and the stepped SOLVE VSTEP sweep reproduce the reduced boundary deck to 0.1 % (run_0012 vs run_0008; run_0013 vs run_0009).

## Not done (stated, not hidden)

- No DFT was executed for the target IWO (no Quantum ESPRESSO on this machine); confinement laws are pure-In2O3 PBE proxies, labelled as such.
- Executed on 2026-09-22 (runs 0016-0029): the no-confinement counterfactual at 2 and 13.2 nm (the confinement law moves the 2 nm threshold by 0.32 V and the 13.2 nm one by 0.02 V; without it the films need different fixed charges), eight one-at-a-time perturbations at 2 nm (tables/SENSITIVITY_RESULTS.md), and the mesh/DOS refinement checks on the final decks (docs/NUMERICAL_CONVERGENCE.md). Not run: work-function and m*-only cases, any sensitivity at 6.3 nm.
- 31.8 nm: laws + series resistance give the on-current within 6 % but not the always-on baseline (run_0006); the back-surface hypothesis run (run_0010) aborted in SOLVE INIT and was not investigated (excluded by the user).
- Off-state floors, gate leakage, contact resistance (thin films), temperature and ID-VD dependence are not modelled or not available.
- run_0011 (6.3 nm mobility stage) was launched and then stopped with the chain; it produced no currents.

## Publication readiness (concise statement)

The package is publication-ready as a calibrated, thickness-resolved TCAD parameter extraction for the 2, 6.3 and 13.2 nm devices (0.037 / 0.063 / 0.081 dec), with a documented shared electrostatic offset, one documented device-specific offset for the 6.3 nm film, and a documented NEGATIVE validation result for that film under the shared laws. It is NOT a predictive model of thickness scaling: the shared laws miss the 6.3 nm threshold by 0.29 V, the band mobility is fitted per thickness, the confinement law is a pure-In2O3 proxy, and no independent bias/temperature/C-V data were available. It should be described in a paper as "calibrated on the same transfer curves it reproduces", with the 6.3 nm validation miss and its device-specific correction both reported.
