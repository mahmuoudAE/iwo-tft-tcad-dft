# Threshold voltage, subthreshold swing and on-state mobility: data versus TCAD

Analysis of 2026-10-06 under `PROTOCOL.md` (committed as 7a61687 before any comparison was computed).

- Numbers: `RESULTS_TABLES.md`, generated from `results.json`.
- Machine-readable copies: `results_table.csv`, `mobility_vs_vg.csv` and `results.xlsx`.
- Code: `extraction.py` (methods), `run_extraction.py`, `figures_extraction.py`, `make_tables.py`.

Uncertainties are 1 sigma and cover the measurement noise of this one device per thickness plus the extraction method. They contain no device-to-device spread, which these data cannot provide.

## 1 Results in brief

### Threshold voltage
- **What is reported.** The constant-current threshold at 1e-9 A/um (I<sub>D</sub>L/W = 20 nA, V<sub>D</sub> = 0.7 V):
  - measured: 0.662 ± 0.001, 0.644 ± 0.001 and 0.083 ± 0.001 V (2.0 / 6.3 / 13.2 nm);
  - TCAD: +19, +9 and -29 mV from these.
- **Why the agreement is not a test.** These differences are calibration residuals, because Q<sub>f</sub> was fitted on this threshold.
- **Value for comparison with other papers.** At 10 nA·W/L (5e-10 A/um) the measured thresholds are 0.591, 0.569 and 0.041 V.
- **The threshold depends on how it is defined, by up to about 1 V on the same curve:**
  - power-law gradual-channel V<sub>T</sub>: 0.3–0.5 V;
  - linear extrapolation with the -V<sub>D</sub>/2 correction: 0.7–1.5 V.
- **Why linear extrapolation is not used.** In all six curves, measured and TCAD, g<sub>m</sub> has no maximum resolved inside the sweep (the "sweep-limited" flag), so the extrapolated value depends on where the sweep ends.
- **Why the power-law V<sub>T</sub> is not used as the threshold.** It is correlated with gamma at r = -0.97 and moves by up to 0.2 V with the fit range.

### Subthreshold swing, 5e-11 to 5e-10 A/um
- **Measured.** 165.6 ± 0.6, 177.6 ± 2.0 and 106.1 ± 1.9 mV/dec. The 13.2 nm value is floor-corrected; without the correction it is 111.9 ± 2.6.
- **TCAD.** 179.9, 182.6 and 122.2 mV/dec: higher than measured by +14.2 ± 1.2, +5.0 ± 2.2 and +16.1 ± 2.2 mV/dec.
- **The difference grows with current at 2 and 13.2 nm** (windows shifted by -0.25 / 0 / +0.25 decade: +9 / +14 / +20 and +13 / +16 / +20 mV/dec). The TCAD swing rises with current faster than the measured one.
- **Equivalent trap density** N<sub>SS</sub> = (SS/S<sub>th</sub> - 1) C<sub>ox</sub>/q:
  - measured: 1.0e13, 1.1e13 and 4.4e12 cm<sup>-2</sup> eV<sup>-1</sup>;
  - TCAD: 1.13e13, 1.16e13 and 5.9e12 cm<sup>-2</sup> eV<sup>-1</sup>.

### Mobility, V<sub>G</sub> = 1–3 V
- **Field-effect mobility at 1.0 → 3.0 V, measured versus TCAD (cm<sup>2</sup>/Vs):**
  - 2.0 nm: 1.57 → 12.15 measured, 1.32 → 11.10 TCAD;
  - 6.3 nm: 1.28 → 10.74 measured, 1.49 → 8.39 TCAD;
  - 13.2 nm: 28.7 → 49.1 measured, 28.6 → 48.9 TCAD.
- **13.2 nm.** TCAD agrees within uncertainty at every gate voltage (\|Delta\| <= 0.9 cm<sup>2</sup>/Vs, <= 2 %).
- **2.0 and 6.3 nm.** TCAD is too high at 1.5–2 V and too low at 2.5–3 V:
  - 2.0 nm: -1.05 cm<sup>2</sup>/Vs at 3 V;
  - 6.3 nm: -2.34 cm<sup>2</sup>/Vs (-22 %) at 3 V and +1.17 cm<sup>2</sup>/Vs (+31 %) at 1.5 V.
- **What this means.** In the ultrathin films the measured mobility depends more strongly on gate voltage than in the model.
- **Power-law exponent gamma (mu<sub>ch</sub> = mu<sub>0</sub>(V<sub>G</sub> - V<sub>T</sub>)<sup>gamma</sup>):**
  - measured: 0.91 ± 0.28, 1.13 ± 0.06 and 0.27 ± 0.08;
  - TCAD: 0.77, 0.57 and 0.23;
  - at 6.3 nm the TCAD value is lower in every fit range, by 0.42–0.87.
- **Model channel mobility against the band value.** At 3 V the TCAD channel mobility is 0.72, 0.66 and 0.74 of the solver's free-electron mobility (12.98, 10.55 and 58.95 cm<sup>2</sup>/Vs), because part of the induced charge is trapped.

## 2 What the comparison does and does not test

| quantity | 2.0 nm | 6.3 nm | 13.2 nm | status of the TCAD value |
|---|---|---|---|---|
| V<sub>th,cc</sub> | +19 mV | +9 mV | -29 mV | fitted (Q<sub>f</sub>); residuals of the fit, not validation |
| I<sub>on</sub> = I<sub>D</sub>(3 V) | 0.00 % | 0.00 % | 0.00 % | fitted (mu<sub>band</sub>), exact by construction |
| SS window | +14.2 | +5.0 | +16.1 mV/dec | 2.0 nm fitted (W<sub>TA</sub>, N<sub>t</sub>); 6.3 and 13.2 nm not fitted |
| mu<sub>FE</sub>(V<sub>G</sub>) shape | differs | differs | consistent | not fitted (the scale at 3 V follows from the I<sub>on</sub> fit) |
| gamma | -0.15 (consistent) | -0.56 (see D5) | -0.04 (consistent) | not fitted |

Genuine tests are the not-fitted rows.
- **Reproduced:** the 13.2 nm on-state shape.
- **Close:** the 6.3 nm swing, within 5 mV/dec (3 %). This is 2.3 sigma beyond the noise of this one device, but well below the 2.0 and 13.2 nm differences and probably within device-to-device spread, which these data cannot quantify.
- **Not reproduced:**
  - the gate-voltage dependence of the mobility of the 2.0 and 6.3 nm films;
  - the current dependence of SS (TCAD too soft above about 1e-10 A/um at 2.0 and 13.2 nm).

For the 2.0 nm film the tail parameters were fitted on the deeper subthreshold. The report shows agreement within 2.3 mV/dec in 1e-11 to 1e-10 A/um. The +14 mV/dec in this window therefore shows that one exponential tail width does not reproduce the measured SS(I<sub>D</sub>) over two decades.

The measured exponents of the ultrathin films (0.9–1.1) are of the order expected for multiple trapping in an exponential tail with W<sub>TA</sub> = 40 meV: gamma ≈ 2(T<sub>t</sub>/T - 1) = 1.1 (Shur and Hack, 1984). That relation assumes a semi-infinite accumulation layer, so it is context, not a test, for films of 2–6 nm.

## 3 Validation of the methods

- **Noise estimator (see D1).** On the noise-free TCAD curves, the estimator written in the protocol returns 0.006–0.04 decade, which is curvature error, not noise. The order-4 difference estimator returns 1e-4 to 2e-3 decade on TCAD, against 1e-3 to 6.5e-2 decade on the measured curves (TCAD/measured <= 15 %).
- **Crossings.** Every level is crossed exactly once on every curve.
- **TCAD data integrity.** The native solver points equal `comparison.csv` to a relative 4e-15 at shared voltages. The solver's mobility probe is constant over the sweep, as the constant-mobility model requires.
- **Power-law fit.**
  - Adequate (log RMS <= 0.01 decade) for five of six curves.
  - The 2.0 nm TCAD curve is flagged: RMS 0.015 decade (3.5 %).
  - V<sub>T</sub> and gamma drift monotonically with the lower fit limit, so the effective exponent falls at high V<sub>G</sub>. The power law is a descriptor over 1–3 V, not an exact law.
- **Linear-extrapolation threshold.** All six curves are flagged "sweep-limited"; the linear-regime condition at V<sub>G</sub>\* is met in all of them.

## 4 Deviations from the protocol (with their effect)

- **D1 – Noise estimator for the crossings replaced.**
  - Protocol: residual std of a 9-point quadratic fit. It failed the validation above.
  - Replacement: robust order-4 difference estimator, 1.4826 MAD(D<sup>4</sup>log<sub>10</sub>I)/sqrt(70), over the points within ±1.5 decade of the level and ±7 grid points.
  - Effect: measured sigma(V<sub>th,cc</sub>) fell from 2.3–2.7 to 0.6–1.3 mV, and sigma(SS) from 4.1–5.5 to 0.6–2.0 mV/dec.
  - The retired values are kept in `results.json` (`sigma_log10_quadratic_retired`).
- **D2 – g<sub>m</sub> noise evaluated locally.**
  - Protocol: one Savitzky–Golay residual std over 1–3 V. Replacement: the same residual over ±5 points; end points ×2 (one-sided difference).
  - Reason: the scatter grows with current (2.0 nm: 0.0019 µS/µm at 1–2 V, 0.0040 µS/µm at 2–3 V).
  - The global values are kept (`sig_global_protocol`).
- **D3 – Uncertainty of the extrapolation threshold.** The protocol did not specify one. Used: sigma = I<sub>D</sub>\* sigma<sub>gm</sub>\*/g<sub>m</sub>\*<sup>2</sup>. No conclusion rests on this quantity.
- **D4 – Uncertainty of the floor-corrected SS** includes the standard error of the median floor. It adds at most 0.03 mV/dec.
- **D5 – Paired fit-range comparison of the power-law parameters (post hoc, supplementary).**
  - The protocol rule adds the fit-range systematics of data and TCAD in quadrature, although they share the same ranges. Both treatments are reported.
  - Only gamma at 6.3 nm changes:
    - protocol rule: Delta = -0.56 ± 0.25, differs;
    - paired: -0.56 ± 0.30, consistent at 1.9 sigma, but negative in all four ranges (-0.42 to -0.87).

**Combined effect of D1–D3 on the verdicts.** Eight verdicts differ between the estimators written in the protocol and the validated ones. The list is generated in `RESULTS_TABLES.md`.
- Seven changed from consistent to differs, because the protocol's estimator counted curvature as noise:
  - SS at 6.3 nm in all three windows;
  - SS at 2.0 nm (-0.25 decade window) and at 13.2 nm (+0.25 decade window);
  - V<sub>th,cc</sub> at 5e-10 A/um at 6.3 nm (+6.5 mV);
  - mu<sub>FE</sub>(1.0 V) at 6.3 nm.
- One changed from differs to consistent: V<sub>th,ELR</sub> at 13.2 nm, once it carried a real uncertainty (D3) instead of a placeholder.
- The conclusions of section 2 do not change. The 6.3 nm swing is stated there as a size (5 mV/dec, 3 %), on which both estimators agree.

**Implementation notes (not deviations).**
- TCAD derivatives use the native solver grid; the grid-dependent difference to the 0.05 V grid is included in the TCAD sigma.
- The TCAD power-law fit uses the 0.05 V measurement grid, so both fits weight V<sub>G</sub> identically.

## 5 Limitations to state in a paper

1. **One device per thickness.** No device-to-device statistics. "Differs" means beyond the noise of this one device, not beyond the spread between devices.
2. **One drain bias, 0.7 V, which is not small.** The linear-regime condition holds only for V<sub>G</sub> >~ V<sub>T</sub> + 0.7 V. Below that, mu<sub>FE</sub> is a normalised transconductance. The guidelines ask for V<sub>DS</sub> small enough for linear operation but above about 2kT/q (Cheng et al., 2022).
3. **No gate current and no reverse sweep.** Gate leakage in the floors and hysteresis cannot be assessed.
4. **No channel-length series.** Contact resistance is not identifiable from one channel length. Within the calibrated model it is <= 4 % (2.0 nm) and 4–9 % (13.2 nm) of R<sub>on</sub>, which bounds the effect on mu<sub>FE</sub>.
5. **C<sub>ox</sub> is nominal.** The mobilities scale as 1/C<sub>ox</sub>. With C<sub>eff</sub>/C<sub>ox</sub> ≈ 0.87 (charge centroid and degenerate density of states) they would be about 15 % higher, for data and TCAD alike.
6. **Assumptions.**
   - Measurement temperature 300 K (enters S<sub>th</sub> and N<sub>SS</sub> only).
   - The 13.2 nm floor correction assumes an additive, gate-independent parallel current.

**What would make the extraction complete for submission:**
- several devices per thickness;
- transfer curves at V<sub>D</sub> = 50–100 mV and in saturation, forward and reverse, with I<sub>G</sub>;
- a channel-length (TLM) series;
- C–V on the stack;
- a gate sweep long enough for g<sub>m</sub> to peak, or keeping the constant-current threshold as the reported one.

## 6 Figure captions

**Fig. 1 (`figures/fig1_threshold_extraction`).** Threshold-voltage extraction for the measured (circles) and TCAD (lines) transfer curves at V<sub>D</sub> = 0.7 V.
- (a–c) Constant-current threshold:
  - the dashed line is I<sub>D</sub> = 1e-9 A/um (I<sub>D</sub>L/W = 20 nA);
  - filled circles are the two measured points bracketing it, and V<sub>th,cc</sub> is their log-linear interpolation (crosses: measured black, TCAD coloured);
  - the uncertainty is measurement noise plus the interpolation-method difference.
- (d–f) Linear extrapolation with the drain-bias correction:
  - tangent at maximum g<sub>m</sub> (dashed) and its intercept V<sub>G,i</sub> (squares);
  - V<sub>th,ELR</sub> = V<sub>G,i</sub> - V<sub>D</sub>/2 (triangles);
  - in every curve the maximum of g<sub>m</sub> lies at or within 0.2 V of the end of the sweep, so this threshold is sweep-limited and is not used as the reported value.

**Fig. 2 (`figures/fig2_ss_extraction`).** Subthreshold-swing extraction.
- (a–c) Transfer curves around the window 5e-11 to 5e-10 A/um (shaded).
  - Crosses mark the interpolated crossings: x measured, + TCAD.
  - SS = Delta V<sub>G</sub>/Delta log<sub>10</sub>I<sub>D</sub> over the window.
  - For 13.2 nm, the lower window edge is only 7.6 times the measured off-floor (dotted; dash-dot: 10 × floor). The measured SS is therefore taken on I<sub>D</sub> minus the floor (diamonds).
- (d–f) Local SS = dV<sub>G</sub>/dlog<sub>10</sub>I<sub>D</sub> against I<sub>D</sub>.
  - Horizontal bars are the window averages (black measured, coloured TCAD).
  - The dashed line is (kT/q) ln 10 at 300 K.

**Fig. 3 (`figures/fig3_mobility_vs_vg`).** Mobility as a function of gate voltage between 1 and 3 V.
- (a–c) Field-effect mobility mu<sub>FE</sub> = L g<sub>m</sub>/(W C<sub>ox</sub> V<sub>D</sub>):
  - g<sub>m</sub> from central differences;
  - error bars are local measurement noise;
  - the dotted line is the constant free-electron mobility used in the TCAD.
- (d–f) Channel mobility mu<sub>ch</sub> = mu<sub>0</sub>(V<sub>G</sub> - V<sub>T</sub>)<sup>gamma</sup> from the power-law gradual-channel fit over 1–3 V, measured (dashed) and TCAD (solid). Shading is the envelope of the fits over 1.25–3, 1.5–3 and 1.0–2.5 V.

**Comparison panels (`figures/compare_a..d`).** Measured (filled circles) and TCAD (open squares) against IWO thickness:
- (a) V<sub>th,cc</sub>;
- (b) SS in the common window (open diamond: 13.2 nm measured without floor correction);
- (c) mu<sub>FE</sub> at V<sub>G</sub> = 2 V and 3 V;
- (d) power-law exponent gamma (error bars: statistical plus fit range).
