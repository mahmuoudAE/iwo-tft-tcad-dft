# Figures and claims for the manuscript

All numbers come from `RESULTS_TABLES.md` and `A1_RESULTS.md`, under `PROTOCOL.md` (with amendment A1).

## Main-text figures (`figures/paper/`)

**(a) `paper_a_transfer_curves`** – Measured (circles) and simulated (lines) transfer curves at V<sub>D</sub> = 0.7 V for 2.0, 6.3 and 13.2 nm IWO channels.
- The simulations are calibrated per film:
  - the fixed interface charge Q<sub>f</sub> is fitted to the constant-current threshold (one value shared by 2.0 and 13.2 nm);
  - the band mobility is fitted to I<sub>on</sub> = I<sub>D</sub>(3 V).
- The tail-state parameters were fitted on the 2.0 nm subthreshold region only.
- The measured off-state floors (10<sup>-14</sup>–10<sup>-11</sup> A/µm) are outside the model, which contains no parallel conduction path.

**(b) `paper_b_mobility_13nm`** – Field-effect mobility mu<sub>FE</sub> = L g<sub>m</sub>/(W C<sub>ox</sub> V<sub>D</sub>) of the 13.2 nm device between V<sub>G</sub> = 1 and 3 V, measured (circles) and simulated (line).
- The overall level is constrained by the I<sub>on</sub> calibration; the gate-voltage dependence is not fitted.
- Lower panel: relative deviation (shaded band: ±2 %).
- Error bars: local measurement noise (Savitzky–Golay residuals) combined with 0.7 % numerical uncertainty.
- The deviation is within ±6 % at every point and within 2 % at 1.0, 1.5, 2.0, 2.5 and 3.0 V.

**(c) `paper_c_ss_vs_normalised_current`** – Local subthreshold swing dV<sub>G</sub>/dlog<sub>10</sub>I<sub>D</sub> against the drain current normalised by each device's on-current.
- Measured points are shown where I<sub>D</sub> >= 10 x the off-state floor.
- In this representation the three films collapse onto one curve, in experiment and in simulation alike.
- Shaded: the analysis window [2.15 x 10<sup>-5</sup>, 2.15 x 10<sup>-4</sup>] I<sub>on</sub>. In this window SS is 123.6 ± 1.0, 122.7 ± 9.3 and 115.3 ± 2.4 mV/dec (measured) and 126.4, 121.3 and 131.3 mV/dec (simulated) for 2.0, 6.3 and 13.2 nm.

## Supplementary figures (needed alongside the main figures)

| file | content |
|---|---|
| `figures/fig1_threshold_extraction` | threshold extraction; why linear extrapolation is not used (all curves sweep-limited) |
| `figures/fig2_ss_extraction` | SS in the fixed window 5e-11–5e-10 A/um; local SS against I<sub>D</sub>; floor treatment at 13.2 nm |
| `figures/fig3_mobility_vs_vg` | mu<sub>FE</sub>(V<sub>G</sub>) and the power-law channel mobility for all films, including the 2.0 and 6.3 nm mismatch |
| `figures/fig4_ss_normalised` | the normalised window, its derivation and SS against thickness |
| `figures/compare_a..d` | threshold, SS, mu<sub>FE</sub> at 2 and 3 V, and gamma against thickness |

## What the paper can claim

1. **13.2 nm on-state.** With two calibrated parameters per film plus tail parameters taken from the 2.0 nm film, the simulation reproduces the gate-voltage dependence of the 13.2 nm on-state: mu<sub>FE</sub> within ±6 % from 1 to 3 V, and power-law exponent 0.23 ± 0.10 against 0.27 ± 0.08 measured.
2. **SS collapse.** The subthreshold swing is set by the normalised current I<sub>D</sub>/I<sub>on</sub>, and all three thicknesses collapse onto one curve. The simulation reproduces this collapse.
3. **SS at equal normalised current.** The simulated swing agrees within 3 mV/dec at 2.0 nm (partly fitted) and 6.3 nm (not fitted).

## What the paper must state (in the text and the Supplementary)

1. **Calibrated quantities.** The thresholds and on-currents are calibration targets; their agreement (+19 / +9 / -29 mV, 0.00 %) is not a validation.
2. **Ultrathin-film mobility.** The simulation does not reproduce the stronger gate-voltage dependence of mu<sub>FE</sub> in the 2.0 and 6.3 nm films. At 6.3 nm it is -22 % at 3 V and +31 % at 1.5 V; gamma is 0.57 against 1.13 measured.
3. **13.2 nm swing.** In the normalised window the simulated SS is 16 ± 3 mV/dec too large at 13.2 nm. In the fixed window it is too large by 5–16 mV/dec in all three films.
4. **Off-state floors.** The measured floors are not described by this model.
5. **Data limitations.** One device per thickness; only one drain bias (0.7 V); no gate-current or reverse-sweep data.

**Why these statements belong in the paper.** The full comparison is public in the repository. Points 2–3 are also informative: they locate where the trap model of the ultrathin films needs improvement.
