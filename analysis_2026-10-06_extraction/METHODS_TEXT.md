# Methods text: electrical parameter extraction (draft for the manuscript)

**Parameter extraction.**

*Common treatment.*
- All parameters were extracted with identical code from the measured and the simulated transfer curves.
- The curves were taken at V<sub>D</sub> = 0.7 V with a gate-voltage step of 50 mV.
- Currents are normalised by the channel width W = 290 µm; the channel length is L = 20 µm.
- C<sub>ox</sub> = 0.896 µF cm<sup>-2</sup> follows from the nominal 15 nm HfO<sub>2</sub>/2 nm Al<sub>2</sub>O<sub>3</sub> stack.
- The definitions, current windows and acceptance tests were fixed in a protocol committed before the comparison was computed (repository commit 7a61687). Deviations are listed in Supplementary Note X.

*Threshold voltage.*
- The threshold voltage was taken as the gate voltage at which I<sub>D</sub> = 1 nA µm<sup>-1</sup> (I<sub>D</sub>L/W = 20 nA). It was obtained by log-linear interpolation between the two neighbouring data points (constant-current method)<sup>1,2</sup>.
- Values at 10 nA × W/L are given for comparison.
- The linear-extrapolation method<sup>1,2</sup> was not used: the transconductance has no resolved maximum within the gate sweep for any device, so the extrapolated value depends on the end of the sweep (Supplementary Fig. X).

*Subthreshold swing.*
- SS = ΔV<sub>G</sub>/Δlog<sub>10</sub>I<sub>D</sub> was evaluated between 5 × 10<sup>-11</sup> and 5 × 10<sup>-10</sup> A µm<sup>-1</sup>.
- This window lies below the threshold criterion and at least ten times above the off-state floor (median I<sub>D</sub> for V<sub>G</sub> = -2 to -0.5 V). The exception is the 13.2 nm device, where the floor (6.6 × 10<sup>-12</sup> A µm<sup>-1</sup>) was subtracted, on the assumption of an additive parallel current.
- The full dependence of SS on I<sub>D</sub> is shown, as recommended<sup>3</sup>.
- The equivalent trap density was computed as N<sub>SS</sub> = (SS/[(kT/q) ln 10] - 1) C<sub>ox</sub>/q.

*Mobility.*
- The field-effect mobility μ<sub>FE</sub> = L g<sub>m</sub>/(W C<sub>ox</sub> V<sub>D</sub>) is reported as a function of V<sub>G</sub> (ref. 4). The transconductance g<sub>m</sub> = ∂I<sub>D</sub>/∂V<sub>G</sub> was obtained by second-order central differences.
- Because the mobility of these films depends on the gate voltage, the above-threshold current (V<sub>G</sub> = 1–3 V) was also fitted with the gradual-channel model with a power-law mobility<sup>5,6</sup>, μ(u) = μ<sub>0</sub>(u/1 V)<sup>γ</sup>, where u is the local overdrive:
  I<sub>D</sub> = (W/L) C<sub>ox</sub> μ<sub>0</sub> [V<sub>GT</sub><sup>γ+2</sup> - max(V<sub>GT</sub> - V<sub>D</sub>, 0)<sup>γ+2</sup>]/(γ + 2), with V<sub>GT</sub> = V<sub>G</sub> - V<sub>T</sub>.
  This expression holds in both the linear and the saturation regime at the applied V<sub>D</sub>.
- The fit was a least-squares fit on log<sub>10</sub>I<sub>D</sub>. Its systematic uncertainty was taken from refits over 1.25–3, 1.5–3 and 1.0–2.5 V.

*Uncertainties.*
- **Noise in log<sub>10</sub>I<sub>D</sub>.** Estimated from the median absolute deviation of fourth-order differences of log<sub>10</sub>I<sub>D</sub> near each current level. The estimator was validated on the noise-free simulated curves, where it returns ≤15 % of the measured values.
- **Noise in g<sub>m</sub>.** Estimated from the local scatter about a Savitzky–Golay derivative (7 points, second order)<sup>7</sup>.
- **Interpolation.** Interpolation-method uncertainties compare log-linear with monotone cubic interpolation<sup>8</sup>.
- **Simulation.** The numerical uncertainty of the simulations (trap-DOS discretisation, mesh and bias grid) is ±1.5 mV for V<sub>th</sub>, ±1 mV dec<sup>-1</sup> for SS and ±0.7 % for g<sub>m</sub>.
- **Not included.** One device per thickness was measured, so the quoted uncertainties do not include device-to-device variation.

## References (verified 2026-10-06)

1. Ortiz-Conde, A. et al. A review of recent MOSFET threshold voltage extraction methods. *Microelectron. Reliab.* **42**, 583–596 (2002).
2. Schroder, D. K. *Semiconductor Material and Device Characterization* 3rd edn (Wiley, 2006).
3. Cheng, Z. et al. How to report and benchmark emerging field-effect transistors. *Nat. Electron.* **5**, 416–423 (2022).
4. Choi, H. H., Cho, K., Frisbie, C. D., Sirringhaus, H. & Podzorov, V. Critical assessment of charge mobility extraction in FETs. *Nat. Mater.* **17**, 2–7 (2018).
5. Shur, M. & Hack, M. Physics of amorphous silicon based alloy field-effect transistors. *J. Appl. Phys.* **55**, 3831–3842 (1984).
6. Servati, P., Striakhilev, D. & Nathan, A. Above-threshold parameter extraction and modeling for amorphous silicon thin-film transistors. *IEEE Trans. Electron Devices* **50**, 2227–2235 (2003).
7. Savitzky, A. & Golay, M. J. E. Smoothing and differentiation of data by simplified least squares procedures. *Anal. Chem.* **36**, 1627–1639 (1964).
8. Fritsch, F. N. & Carlson, R. E. Monotone piecewise cubic interpolation. *SIAM J. Numer. Anal.* **17**, 238–246 (1980).

References 1 and 3–6 were checked online on 2026-10-06. References 2, 7 and 8 are standard texts; check their bibliographic details against the journal's style before submission.
