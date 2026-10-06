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
| `figures/ss_agreement_map` | SS<sub>TCAD</sub> - SS<sub>meas</sub> in sliding one-decade windows for all films |
| `figures/ss_agreement_windows` | per-film ranges where SS agrees within 5 mV/dec, measured raw and floor-removed (post hoc, descriptive) |
| `figures/film_13p2_full` | the 13.2 nm device in full: transfer curves, floor, both SS windows, local SS against current |

## What the paper can claim

1. **13.2 nm on-state.** With two calibrated parameters per film plus tail parameters taken from the 2.0 nm film, the simulation reproduces the gate-voltage dependence of the 13.2 nm on-state: mu<sub>FE</sub> within ±6 % from 1 to 3 V, and power-law exponent 0.23 ± 0.10 against 0.27 ± 0.08 measured.
2. **SS collapse.** The subthreshold swing is set by the normalised current I<sub>D</sub>/I<sub>on</sub>, and all three thicknesses collapse onto one curve. The simulation reproduces this collapse.
3. **SS at equal normalised current.** The simulated swing agrees within 3 mV/dec at 2.0 nm (partly fitted) and 6.3 nm (not fitted).
4. **Range of SS agreement** (post hoc, descriptive; one rule for all films):
   - 2.0 nm: within 5 mV/dec over 3.3 decades, 5.6 x 10<sup>-14</sup>-10<sup>-10</sup> A/um, 6 points (89.1 ± 0.5 vs 89.3 mV/dec);
   - 6.3 nm: within the measurement uncertainty over its whole clean range, 1.5 x 10<sup>-12</sup>-10<sup>-9</sup> A/um, 8 points (145.6 ± 3.7 vs 145.5 mV/dec).

## What the paper must state (in the text and the Supplementary)

1. **Calibrated quantities.** The thresholds and on-currents are calibration targets; their agreement (+19 / +9 / -29 mV, 0.00 %) is not a validation.
2. **Ultrathin-film mobility.** The simulation does not reproduce the stronger gate-voltage dependence of mu<sub>FE</sub> in the 2.0 and 6.3 nm films. At 6.3 nm it is -22 % at 3 V and +31 % at 1.5 V; gamma is 0.57 against 1.13 measured.
3. **13.2 nm swing (reported as a finding, not tuned away).**
   - In the normalised window the simulated SS is 16 ± 3 mV/dec too large. Over the film's whole clean range (6.6 x 10<sup>-11</sup>-10<sup>-9</sup> A/um) it is 16-25 mV/dec too large, and +44 mV/dec at 10<sup>-9</sup>-10<sup>-8</sup>.
   - The simulated swing rises more steeply with current than the measured one, so the model has too many tail states close to the conduction-band edge at this thickness. Its 13.2 nm tail density comes from the thickness law, not from a fit, and the tail width was fixed on the 2.0 nm device. The 2.0 nm film shows the same trend above about 3 x 10<sup>-11</sup> A/um (+7 to +20 mV/dec).
   - Agreement at 13.2 nm appears only at 10<sup>-11</sup>-10<sup>-10</sup> A/um after subtracting the off-state floor (91.8 ± 2.5 vs 90.9 mV/dec, 2 points). This depends on the floor being additive and is not claimed.
   - The registered fixed window (5 x 10<sup>-11</sup>-5 x 10<sup>-10</sup> A/um) gives TCAD too large by 5-16 mV/dec in all films; report it in the Supplementary.
4. **Off-state floors.** The measured floors are not described by this model.
5. **Data limitations.** One device per thickness; only one drain bias (0.7 V); no gate-current or reverse-sweep data.

**Why these statements belong in the paper.** The full comparison is public in the repository. Points 2–3 are also informative: they locate where the trap model of the ultrathin films needs improvement.
