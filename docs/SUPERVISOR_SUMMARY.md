# Supervisor summary (for Mukul) - IWO thickness-aware ATLAS model, V1

## What was built

A single ATLAS material description of the ~2 % W:In2O3 channel whose thickness dependence is carried by explicit laws (band gap / electron affinity / effective mass from pure-In2O3 DFT slab shifts, density of states from the effective mass, tail-state density and background donor density as fitted power laws, one shared interface-state density, one shared fixed charge), applied to the measured bottom-gate device (TiN / HfO2 15 nm / Al2O3 2 nm / IWO / Pd) at VD = 0.7 V. Every number carries a provenance label; every simulated number comes from a real, logged ATLAS run on the local licence.

## Result in one table (identical metric extraction for experiment and simulation)

| t | Vth exp/sim (V) | SS exp/sim (mV/dec) | mu_FE exp/sim | Ion error | log RMSE (active) | status |
|---|---|---|---|---|---|---|
| 2.0 nm | 0.66 / 0.68 | 84 / 73 | 12.1 / 11.3 | 0.0 % | 0.037 dec | calibrated |
| 13.2 nm | 0.08 / 0.05 | 131 / 151 | 50.2 / 49.0 | 0.0 % | 0.081 dec | calibrated |
| 6.3 nm | 0.64 / 0.35 | 115 / 108 | 10.9 / 9.1 | +27 % | 0.68 dec | validation: shape right, threshold 0.29 V off |
| 6.3 nm tuned | 0.64 / 0.65 | 115 / 111 | 10.9 / 8.4 | 0.0 % | 0.063 dec | one device-specific flat-band offset (+0.29 V) + its own band mobility |

Free quantities: one shared fixed charge (1.73e12 cm^-2, a -0.31 V flat-band offset standing in for the unmeasured absolute band alignment), one band mobility per film, and for the 6.3 nm film one device-specific flat-band offset. Astra and Claude V0 reached 0.02-0.05 dec on the same curves but with 4-6 tuned parameters per device; the shared-law model reaches 0.04-0.08 dec with the parameters tied across thickness, except for the single 6.3 nm electrostatic number.

## Three things worth knowing

1. **The confinement story holds for 2 vs 13.2 nm, and it was tested.** With no tuning, the laws put both devices 0.3 V too positive by the same amount; one shared offset fixed both. The counterfactual runs with the confinement law switched off move the 2 nm threshold by 0.32 V and the 13.2 nm threshold by 0.02 V: without the law the two films would need fixed charges differing by 1.6e12 cm^-2, i.e. a per-device parameter. A one-at-a-time sweep at 2 nm (chi, Nd, Nt, WTA, Dit, eps, overlap) shows the threshold is set by the band alignment, the swing by the tail width and Dit, and the on-current by the tail density; donors, permittivity and contact geometry are irrelevant for the 2 nm film.
2. **The 6.3 nm device breaks the trend.** Its measured threshold equals the 2 nm value; every monotonic law puts it 0.3 V lower. This is a real discrepancy, not a fitting failure: both earlier calibrations needed a device-specific parameter here as well, and the tuned run shows that a single flat-band number (+0.29 V, equivalent to 1.6e12 cm^-2 less positive interface charge) brings the film to the same quality as the other two. Candidate causes (sample-to-sample fixed charge, thickness or process deviation, a non-monotonic donor/confinement behaviour between 2 and 6 nm) cannot be separated with one transfer curve per device.
3. **Mobility is fitted, not predicted.** The 5x jump between 6 and 13 nm has no defensible law in the available inputs.

## What would make it predictive

C-V (or Kelvin probe) per thickness to fix the flat band independently; a second bias or temperature per device for validation; DFT of W-doped slabs (inputs are prepared in qe_workflow/) to replace the pure-In2O3 proxy; TLM for the contacts. The 31.8 nm always-on device needs a mechanism beyond bulk donors (a back-surface donor sheet is the working hypothesis) and was left out of the final set.

## Where to look

FINAL_STATUS.md (readiness statement), tables/EXPERIMENTAL_VS_SIMULATION.md, tables/MATERIAL_PARAMETERS_USED.md, plots/<thickness>/overlay_log.png, docs/LIMITATIONS.md, results/RUN_INDEX.csv (all 14 launches).
