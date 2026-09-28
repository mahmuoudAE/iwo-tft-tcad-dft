# Actual calibration tradeoffs for the 6.3 and 13.2 nm candidates

Snapshot after the completed 6.3 nm retry on 2026-09-12. Both new candidates meet the working active-region target (log RMSE <0.05 decades and |+3 V current error| <5%) using **native signed current**, but their independent numerical controls remain pending. The low-current plateaus and several slope errors remain unresolved. This note does not grant full-curve fit acceptance or unique physical parameter identification.

All four compared runs pass a fresh `rebuild_check.load_run` check: native completion, original gate coverage, input/output hashes, signed terminals, biases and KCL. The 121 measured points and original measured-current factor-5 active masks are unchanged. No scaled, interpolated or artificial simulated curve was generated. Report-level logarithmic RMSE below uses the full-precision native current; tiny differences from the older diagnostic metric reflect exported-current rounding.

## 6.3 nm: lower constant band mobility improves the primary target

Previous: `20260912T091742_999942_extension02_charge_6p3nm`. New: `20260912T124657_803129_priority3_fit6_mu12_retry2`. The only physical input change is band mobility **13 → 12 cm²/(V s)**. ND=1e17 cm⁻³, NTA=3.7142857142857145e20 cm⁻³ eV⁻¹, WTA=0.040 eV, and all shared/contact inputs remain fixed.

| Native metric | Previous | New |
|---|---:|---:|
| Signed linear RMSE, all 121 points (A/µm) | 1.944754e-8 | 9.953956e-9 |
| Positive-current log RMSE, all region (decades; 67/121) | 1.805097 | 1.813477 |
| Active log RMSE (decades; 56/56) | 0.06398749 | **0.04920549** |
| Subthreshold scoring-region log RMSE (decades; 12/12) | 0.03923047 | 0.05508456 |
| On scoring-region log RMSE (decades; 44/44) | 0.06921935 | 0.04747593 |
| +3 V signed current error | +10.45450% | **+1.96668%** |
| Middle slope error, 1.5→2 V | +33.25758% | +23.01453% |
| Late slope error, 2.5→3 V | −4.98011% | −12.27913% |

Both runs have **54 native zeros, zero negative currents, and 67 positive currents**. All 121 points enter the linear errors. Only 67 have a logarithm; therefore the positive-only all-region value is not a complete logarithmic fit. The remaining low-current region has 65 measured targets, only 11 positive native samples, and 54 unavailable log residuals. The first active sample at +0.25 V changes from −0.0117278 to −0.0464899 decades.

The new run is preferable for the stated active/current targets and approximately halves the all-point linear RMSE. It worsens the subthreshold score and the late slope, exactly the tradeoff that a global mobility reduction could create. The late native secant is 2.818559156e-7 A/(µm V), compared with measured 3.21310e-7. The middle native secant is 1.8859430814e-7, compared with measured 1.533106e-7. These are endpoint differences at actual original gate targets, not fitted derivatives or interpolated curves. Retain this as the numerical-validation candidate; do not claim the slope or low-current discrepancies are solved.

Fresh report and depth audits are in `results/priority_three_20260912/report_fit6_mu12` and `depth_fit6_mu12`. They retain all original currents and native charge probes. The emitted bulk tail still has a 9.36e12 cm⁻² sheet-equivalent capacity, with zero populated donor/acceptor Gaussian and interface families. The 192-level acceptor export reproduces the specified tail; this parameter/charge audit does not replace the pending DOS-doubling current comparison. The log overlay was visually checked for readable units, legend and the explicit zero-current omission count.

## 13.2 nm: a small donor increase improves early turn-on

Previous: `20260912T090754_224585_extension02_charge_13p2nm`. New: `20260912T122359_458630_priority3_fit13_nd89`. The only physical change is uniform shallow ND **8.6e17 → 8.9e17 cm⁻³**. Band mobility stays 55 cm²/(V s), NTA=7.142857142857143e19 cm⁻³ eV⁻¹, WTA=0.035 eV; all shared/contact inputs remain fixed.

| Native metric | Previous | New |
|---|---:|---:|
| Signed linear RMSE, all 121 points (A/µm) | 4.209230e-8 | 4.709142e-8 |
| Positive-current log RMSE, all region (decades; 75/121) | 2.460418 | 2.402209 |
| Active log RMSE (decades; 62/62) | 0.05383251 | **0.04902804** |
| Subthreshold scoring-region log RMSE (decades; 10/10) | 0.1237340 | 0.1018587 |
| On scoring-region log RMSE (decades; 52/52) | 0.02260493 | 0.02950898 |
| +3 V signed current error | +2.15234% | **+2.45230%** |
| Middle slope error, 1.5→2 V | +4.27139% | +4.33708% |
| Late slope error, 2.5→3 V | −2.60719% | −2.58753% |

The first active sample at −0.05 V improves from −0.335841 to −0.169278 decades. The active aggregate crosses the working target primarily through early-turn-on improvement; the on-region and all-point linear errors increase. Both curves retain **46 native zeros, zero negatives and 75 positives**. In the 59-point low-current scoring region, only 13 native samples have logarithms. The finite measured plateau is still not explained by this model.

The new late secant is 1.495456804e-6 A/(µm V), compared with measured 1.53518e-6; the new middle secant is 1.4146730424e-6, compared with measured 1.355868e-6. Global mobility reduction would not be an unqualified improvement. Retain the current isolated donor candidate for its numerical controls rather than spend an unapproved launch on a marginal fit change.

The existing new-13 nm native report is `results/priority_three_20260912/report_fit13_nd89`. Exact region metrics, secants, configuration differences and native source/output hashes for both comparisons are saved in `results/priority_three_20260912/actual_calibration_tradeoffs.json`. The two failed prior 6.3 nm attempts are excluded from every comparison and selection statement here.

The new curves' active-target margins are small. Their own x/y/DOS comparisons must pass before final retention; certificates from prior physical parameters cannot be transferred. A useful active electrical fit does not establish measured leakage physics, sputter-chemistry prediction, quantum validity, or a universal thickness law.
