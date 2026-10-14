# Review of RQ-001 / HO-002

| Field | Value |
|---|---|
| Reviewer | Codex |
| Commit reviewed | Public evidence checkout HEAD `f315b78`; HO-002 in current private working tree |
| Date | 2026-10-09 |

## 1. Independent assessment (Phase 1; blinding compromised)

**Process disclosure.** The handoff extraction mistakenly searched for `## Part B`, whereas the actual delimiter is `### PART B`. It therefore displayed Part B of HO-002 and the older handoff before this assessment was written. This document cannot satisfy the strict “written before reading Part B” condition. Numerical checks below were independently implemented without importing the owner's reconciliation or protocol code. No owner plan or response file was opened. No Phase 2 verdict is issued. An unexposed reviewer would be required for a genuinely blinded assessment. No commit or push was made, consistent with relay rules.

### What the evidence supports, with status labels

**DERIVED.** A stdlib-only Python implementation reproduces the principal mobility and SS numbers directly from `data/experimental_clean.csv`. The spreadsheet was independently decoded using ZIP/XML; all 121 gate voltages and currents for each of all four films match the CSV exactly (maximum absolute differences zero). The 31.8 nm curve was used only for this integrity check and is excluded from the reconciliation conclusions. Reproduction script: `codex/independent_reviews/RQ-001_check.py`; results: `RQ-001_check_results.json`.

**DERIVED.** Series capacitance from the stated dielectric geometry is 8.9553698143e-7 F/cm². Currents are per micrometre, so the formulas use L/W = 20/1 on these currents; equivalently use total current multiplied by 290 and L/W = 20/290. Mixing these conventions would introduce a factor of 290.

| Independently re-derived quantity | 2.0 nm | 6.3 nm | 13.2 nm |
|---|---:|---:|---:|
| Floor, median over −2 to −0.5 V (A/µm) | 4.60552e-15 | 1.52759e-13 | 6.59655e-12 |
| Constant-current threshold at 1e-9 A/µm (V) | 0.661821 | 0.644004 | 0.082522 |
| Peak gm-normalised mobility (cm²/Vs) | 12.145945 | 10.946664 | 50.166230 |
| Gate voltage at that peak (V) | 3.00 | 2.85 | 2.80 |
| Peak saturation-formula mobility (cm²/Vs) | 5.086524 | 3.858359 | 27.402948 |
| Gate voltage at that peak (V) | 1.75 | 2.55 | 0.95 |
| Saturation-formula mobility at 3 V (cm²/Vs) | 3.240641 | 3.201873 | 8.711301 |
| A1 SS (mV/dec) | 123.598 | 122.667 | 115.293 |
| Raw S1 SS (mV/dec) | 165.634 | 177.641 | 111.866 |
| One-decade SS starting at 3× floor (mV/dec) | 61.719 | 82.945 | 110.664 |
| One-decade SS starting at 5× floor (mV/dec) | 61.076 | 89.673 | 107.824 |
| Steepest 3-point regression, margin 1× (mV/dec) | 63.581 | 89.718 | 104.545 |
| Steepest 5-point regression, margin 1× (mV/dec) | 72.670 | 101.924 | 116.321 |
| Floor-subtracted steepest 4 points, margin 3× (mV/dec) | 64.845 | 91.487 | 119.088 |
| Minimum adjacent-point SS, margin 10× (mV/dec) | 69.436 | 88.398 | 105.698 |

**DERIVED.** Relative to paper text values 5.1 and 27.4 and the supplied digitised 3.731, the saturation-formula peaks differ by −0.264%, +3.41%, and +0.0108%, respectively. This is a strong numerical reconciliation conditional on the stated capacitance and current normalisation. The gm peaks require different common-scale corrections: paper/derived = approximately 0.420, 0.341, 0.546. A single changed capacitance, geometry multiplier or assumed drain bias cannot reconcile all three gm peaks exactly.

**OBSERVED.** Direct inspection of the embedded Fig. 1 raster extracted from the paper confirms that its IWO SS markers are approximately 62, 87 and 119 mV/dec: only the first lies near the dashed 60 line. The off-current axis says A, while the transfer-current axis says A/µm. This is an unresolved unit inconsistency. Approximate PDF literal-text extraction independently locates the 5.1–27.4 mobility statement, the 60–70 SS statement, and SS in the model's fitted-parameter/VIF list. Pixel centroids and their quoted uncertainty were not independently regenerated.

**DERIVED.** The best listed floor-corrected 4-point estimator differs from the supplied paper SS values by about +5.0%, +4.6%, −0.18%. Several other windows give similar matches. The same curves also yield much larger SS in S1/A1. Thus the disagreement can arise from the extraction window without a change of device physics.

**DERIVED.** For constant mobility and gradual-channel linear current I = (W/L)Cμ V_D(u − V_D/2), substitution into 2L/(WC)(d√I/dV_G)² gives μ V_D/(2u − V_D). This equals μ at u = V_D and decreases above that. A falling saturation-formula mobility in a linear-regime curve therefore does not establish decreasing carrier mobility.

### What the evidence does not support

**UNRESOLVED.** Matching three peaks does not identify the paper's actual extraction recipe. It constrains the combination of capacitance, geometry and current normalisation, not each separately. The power-law-effective and Y-function alternatives reported with a common factor remain viable until the fab supplies its recipe. C030's arithmetic is reproduced; C031 remains an inference rather than a verified method attribution.

**UNRESOLVED.** Neither mobility definition establishes intrinsic channel or band mobility. The gm quantity is normalised transconductance; gate-dependent mobility/charge, contacts and finite drain bias affect its interpretation. Even a valid saturation condition is insufficient if mobility varies with overdrive. ELR and fitted thresholds are model-dependent, so the reported overdrive table is a conditional check, not a measured regime boundary. With the independently derived constant-current thresholds, overdrives at the saturation-formula peaks are 1.088, 1.906 and 0.867 V, all above 0.7 V; this criterion is also not a physical threshold determination.

**UNRESOLVED.** Near-thermal minimum SS does not establish near-thermal switching across a broad operating range, nor low trap density. At 2 nm the reproduced steepest 3-point section begins at 1.92169e-14 A/µm (5.573 pA total) and spans only 0.10 V. Four-point fitting spans 0.15 V. Minimum selection and window choice are part of the estimator and must be disclosed.

**UNRESOLVED.** The Monte Carlo cannot establish that instrumental effects did not create the steep section. It assumes a smoothed version of the same curve as truth and independent Gaussian log-current noise; it does not test offsets, range changes, correlated noise, settling, drift or incorrect current units. A stable result under that simulation is conditional estimator robustness. It is not independent measurement validation.

**UNRESOLVED.** Floor subtraction assumes an additive gate-independent current. It necessarily steepens a positive rising curve near its floor: for I = I_channel + F, SS_raw = SS_channel(1 + F/I_channel). A good match after subtraction does not identify the leakage mechanism or validate the subtraction physically. The single-curve data cannot resolve gate leakage without I_G.

**UNRESOLVED.** Agreement of off-current markers and CSV floors is evidence of numerical correspondence, not proof of identical devices or sweeps, especially given the A versus A/µm axis mismatch. Four-significant-digit rounding tests do not independently establish width normalisation.

### My competing hypotheses

- **HYPOTHESIS.** The paper used saturation-formula peak extraction, explaining both peak values and the subsequent decline as a finite-bias/definition effect. The numerical match makes this a leading candidate, subject to recipe confirmation.
- **HYPOTHESIS.** The paper used a fitted mobility or another effective definition with a different capacitance/current/bias convention; the saturation-peak match is coincidental or reflects related shape statistics.
- **HYPOTHESIS.** Paper SS is the fitted compact-model parameter above a constant floor, rather than the minimum measured total-current slope. A fitted parameter need not equal any selected local slope.
- **HYPOTHESIS.** The 2 nm steep low-current section is reproducible channel behaviour over a narrow window, while the larger SS elsewhere reflects gate-dependent charge response.
- **HYPOTHESIS.** That section is partly shaped by instrumentation, additive current, settling or sweep/grid history. The current Monte Carlo does not distinguish this from channel behaviour.
- **HYPOTHESIS.** The paper's plotted devices, sweeps or current-unit conventions differ from this workbook; approximate numerical agreement alone is insufficient provenance.

### Cheapest discriminating tests

1. Obtain the fab's existing extraction script/spreadsheet and exact Fig. 1b device/sweep provenance, including mobility equation, derivative smoothing, capacitance, geometry, current units, drain bias, and SS fit/window/floor treatment. Apply that recipe unchanged to this workbook. This is the first test: it directly separates method attribution from numerical coincidence without new fabrication.
2. As a local arithmetic test, sweep floor offset and window position without choosing an estimator by agreement with the paper; show all outcomes and sampled point counts. For minimum estimators compare fixed contiguous windows and alternate grid phases. This checks extraction sensitivity, not measurement truth.
3. If measurement is needed, preregister the checks before receiving new data: repeat the existing devices with ≤10 mV gate steps, forward/reverse sweeps, recorded I_D/I_S/I_G, settling/range metadata and a probe-lifted baseline. Determine whether the 2 nm steep section persists at the same currents across repeats and grid phases. Request no unreleased holdout data before registration.
4. Compare low-drain-bias gm and genuinely saturated output/transfer measurements under one independently established capacitance convention. This tests whether inferred mobility trends survive the formula and regime changes.

### Numbers not independently reproduced and limitations

No numerical discrepancy was found among the entries in the reproduction table. Python here has no numpy, scipy, openpyxl, pypdf or Pillow, and no standard PDF text/render command was found; no network installation was attempted. ZIP/XML and stdlib arithmetic suffice for the principal checks. The following Part A numbers remain unchecked by an independent numerical implementation:

- Exact Fig. 1b pixel centroids, marker sizes, ±1.5 px error model, ±0.46 mobility / ±1.8–3.5 SS errors, dashed-line 1.4 px residual, and the floor-marker ratios 0.71/0.93/1.02 (their approximate location was visually checked).
- Effective-mobility peaks for all three threshold definitions; ELR and power-law fitted thresholds/overdrives; Y-function values and errors; common factors 0.68/0.66 and residual bounds; fitted channel mobilities at 1/2/3 V.
- Forward/backward/Savitzky–Golay derivative spread 5.04–5.11 / 3.78–3.90 / 25.9–27.5. The central-difference baseline was reproduced.
- Per-film compensating C_ox 2.13e-6/2.45e-6/1.64e-6 and V_D 1.67/1.92/1.28 were not separately rerun (they follow algebraically from reproduced gm peaks and supplied paper values); alternative-capacitance numerical variants were not separately rerun.
- A1 uncertainty bars ±1.0/9.3/2.4; sliding-window uncertainty bars and complete extrema 60.6–69.3, floor ratios 3.9–22, and high-current values 84.5/121/195; all 31-method scores and the count 14 within 15%; the other listed estimator variants and sub-thermal minima 58.6/59.2/41.8–51.2.
- Noise estimates 0.0048/0.156/0.015; 2000-draw Monte Carlo percentiles 68.0–69.8 / 48.8–100.4 / 102.9–118.5, medians and smoothed-reference values; rounding fractions for the 290/1/14.5 multipliers.

The thermal scale 59.5 mV/dec at assumed 300 K is consistent with (kT/q)ln10; temperature was not independently measured. Numerical reproduction is conditional on the repository's units and capacitance, whose physical calibration remains unresolved. No owner evidence files were modified; no ATLAS, CERN, network, commit or push was used.

Strongest finding: The saturation-formula peaks and window-dependent SS are independently reproduced from the workbook-identical CSV.
Strongest doubt: Numerical agreement does not establish the paper's recipe or the physical validity of its mobility and near-floor SS interpretations.
First test: Obtain and apply the fab's exact extraction recipe and Fig. 1b sweep provenance to the existing workbook.
