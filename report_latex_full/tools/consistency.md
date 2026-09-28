# Stage 5 consistency pass -- change log

Primary sources: analysis_2026-09-25/SYNTHESIS.md (sections 0, A-D); digest/runs.csv.
Run count basis (runs.csv): run_0001..run_0052 = 52 recorded launches; 46 REAL_ATLAS_SCORED + 3 REAL_ATLAS_PREDICTION
= 49 with scored currents; run_0010 (NO_EXPORT), run_0011 (NO_EXECUTION_JSON), run_0018 (TIMEOUT) have no currents;
run_0027 scored but retracted (malformed deck).
Canonical factors: rescale x1.015074 (run_0039), x1.020113 (run_0040); P-MTR tmu factors 1.19669 (338.15 K), 1.30441 (358.15 K).

Pre-pass grep: no earlier consistency.md existed; the files were re-read in their current state.

## Changes (one line per edit, in the order made)

1. chapters/00_abstract.tex: "Fifty-two ATLAS runs were made" -> "Fifty-two ATLAS launches were recorded, of which 49 produced scored currents" (run-count wording, runs.csv).
2. chapters/01_introduction.tex (Methodology): "All 52 ATLAS launches" -> "All 52 recorded ATLAS launches ..., of which 49 produced scored currents".
3. chapters/01_introduction.tex (What is new): "numerics are converged for 300 K transfer" -> "converged where checked for 300 K transfer" (SYNTHESIS D9 wording; open items in F).
4. chapters/01_introduction.tex (keyresult): "52-run ATLAS study" -> "52 recorded launches, of which 49 produced scored currents"; added a one-sentence transition to the literature chapter after the keyresult box.
5. chapters/02a_literature_target.tex (Januar used-box, mu_max row): caveat "linear muFE is 12.1 / 50.2" -> "12.15 / 50.17" (SYNTHESIS D1 values; the abstract rounds 12.15 to 12.2, so the 12.1 rounding disagreed).
6. chapters/02a_literature_target.tex (Mobility definition): "12.1, 10.9, 50.2 and 49.2 cm2/Vs" -> "12.15, 10.95 and 50.17" and added that the 31.8 nm 49.2 is not a mobility (several gm maxima; SYNTHESIS A.3).
(02b_literature_in2o3.tex read: no change needed.)
(02c_literature_methods.tex read: no change needed.)
7. chapters/02d_provenance.tex (intro convention ii): rescale factors x1.0151 / x1.0201 -> x1.015074 / x1.020113.
8. chapters/02d_provenance.tex (table row "muband, DOS 384/192"): same factor correction.
9. chapters/02d_provenance.tex (row "Required Qf per film"): no-confinement 2 nm value 0.048e12 -> 0.047e12 (SYNTHESIS D3, [SYN-b]).
10. chapters/02d_provenance.tex (keyresult): fitted muband "17.69 / 11.41 / 60.39" (unscaled run values) -> final calibrated "17.69 / 11.58 / 61.60" with run_0039 x1.015074, run_0040 x1.020113 (SYNTHESIS D8; contradicted 05, 07, 12).
11. chapters/02d_provenance.tex: added a two-sentence transition to the device-and-data chapter after the closing keyresult of the literature chapter.
12. chapters/03_device_data.tex (feature 2, floors): "origin (gate leakage, measurement floor, or channel conduction) is not determined" -> gate leakage disfavoured at 6.3/13.2 nm (floors bias-independent, cref sec:mech-traps); remaining origin not determined (SYNTHESIS B4 and D "Gate leakage as the dominant floor" rejected).
13. chapters/03_device_data.tex (limitation 2): same alignment with SYNTHESIS B4/D.
14. chapters/03_device_data.tex: added a transition to the derivation chapters after the closing keyresult.
15. chapters/04_derivations_electrostatics.tex (sec:par-dec, Status): "film confinement at 2 nm exists (strongly supported, THEORY)" -> "physically expected (THEORY; not measured on these films, and not identified from ID-VG)" (overclaim vs SYNTHESIS 0 and Q1).
16. chapters/04 (sec:par-deep, Derivation): removed the SS_min-based inference "which is why SS_min of run_0012 (73) is below the measured 84.5"; replaced by consistency with the too-soft 1e-10..1e-9 window and a note that SS_min is not robust (SYNTHESIS D7, B2).
17. chapters/04 (sec:par-deep, C1 run_0052): verdict "partially passed" -> "partly failed" (SYNTHESIS D table: C1 "OOS, partly failed").
18. chapters/04 (sec:par-dit, Dit x5): rejection no longer rests on SS_min (~155 vs 114.7); now rests on magnitude x23-24 at 6.3 nm only on a shared stack (SYNTHESIS D); SS_min change kept as history.
19. chapters/04 (sec:par-qf, Degeneracy): no-confinement 2 nm Qf 0.048e12 -> 0.047e12 and rms 0.132 V -> 0.133 V (SYNTHESIS D3: 0.1325 V; abstract and Ch. 9 quote 0.133).
20. chapters/04_derivations_electrostatics.tex: added a transition to the transport chapter after the closing keyresult.
21. chapters/05_derivations_transport.tex (sec:der-tlc, C1 bullet): "35 % of the gap miss while keeping SS ... partially passed" -> "33 % of the 0.356 V gap miss ... SScc +15.6 mV/dec ... Ion +16 % vs +/-3 % predicted; partly failed" (SYNTHESIS D table; agreed with Ch. 4 and 8).
22. chapters/05 (keyresult): "DOS 384/192 is converged" -> "converged where checked (2 nm, 300 K ...)" (SYNTHESIS D9; the section's own caveat). Added a transition to the numerics chapter after the keyresult.
23. chapters/06_numerics.tex (Discussion): rescale factors x1.0151 / x1.0201 -> x1.015074 / x1.020113.
24. chapters/06_numerics.tex (Budget and cost): added "52 recorded launches, of which 49 produced scored currents (run_0010 aborted, run_0011 never executed, run_0018 timed out)" with cref to sec:app-runs-composition.
25. chapters/06_numerics.tex: added a transition to the calibration chapter after the closing keyresult.
26. chapters/02c_literature_methods.tex (ATLAS table, SOLVE row): "stepped gate sweeps -3 -> +3 V in 0.05 V" -> "(steps 0.2 / 0.05 / 0.1 V)" (contradicted sec:num-sweep, whose stepped segments are (-1,0.2),(1.5,0.05),(3,0.1)).
27. chapters/02d_provenance.tex (Bias sweep row): "0.05 V" clarified as the measured grid; stepped simulation segments 0.2 / 0.05 / 0.1 V (same source).
28. chapters/07_calibration.tex (fig:calibrated_overlays caption): factors x1.000000 / x1.015073 / x1.020112 -> x0.999983 / x1.015074 / x1.020113 (agrees with tab:cal-final caption, which gives run_0038 x0.999983 = 17.6897/17.69).
29. chapters/07_calibration.tex (intro): "the only out-of-sample test, the 6.3 nm threshold, failed" -> "the out-of-sample test of the shared parameters ... failed, and the registered 6.3 nm hypothesis tests B0 and C1 failed or partly failed" (SYNTHESIS D: B0 OOS failed, C1 OOS partly failed; contradicted Ch. 8).
30. chapters/07_calibration.tex: added a transition to the 6.3 nm chapter after the closing keyresult.
31. chapters/05_derivations_transport.tex (tab:d2-mu-values): run_0038 "x1.000000" -> "at 17.69, x0.999983" (same source as 28).
32. chapters/08_six_nm.tex (C1 outcome): "33--35 % ... while keeping the slope. Verdict: partially passed" -> "33 % of 0.356 V ... at a moderate slope cost (SScc +15.6) ... partly failed (SYNTHESIS D)"; Ch. 9 verdict table already said "OOS, partly failed".
33. chapters/08_six_nm.tex (tab:6p3-prereg, P3): outcome "partially passed" -> "partly failed" (same source).
34. chapters/08_six_nm.tex (keyresult): trade-off "3--8.5" -> "3.2--8.5" mV per mV/dec (matches sec:6p3-shape and Ch. 5); stated explicitly that the shape part remains unexplained (overclaim guard, SYNTHESIS 0/A.2). Added a transition to the mechanisms chapter.
35. chapters/09_mechanisms.tex: added a transition to the predictions chapter after the closing keyresult (09 grep-checked: confinement, SS_min, run_0027, validation wording already consistent with SYNTHESIS).
36. chapters/10_predictions.tex (intro): "The single out-of-sample test ... run_0014 failed" -> OOS tests (run_0014, and registered B0 run_0037, C1 run_0052) failed or partly failed (SYNTHESIS D; agrees with Ch. 11 keyresult). Added a transition to the validation chapter after the keyresult.
37. chapters/11_validation.tex: added a transition to the conclusions chapter after the closing keyresult (content already consistent: no claim validated).
38. chapters/12_conclusions.tex (opening): "The one out-of-sample test inside the data" -> shared-parameter test failed and B0/C1 failed or partly failed (same source).
39. chapters/12_conclusions.tex (keyresult): shape part "remains unexplained"; mobility-step bullet marked "model-conditional ... within the calibrated model" (SYNTHESIS 0, B1).
40. chapters/12_conclusions.tex (corrections table, FINAL_STATUS and SUPERVISOR_SUMMARY rows): "52 launches" -> "52 recorded launches, of which 49 produced scored currents".
41. appendices/A_runs.tex (composition paragraph): reworded to "52 recorded launches, of which 49 produced scored currents: 46 SCORED + 3 PREDICTION; three produced no usable curve (0010, 0011, 0018)".
42. appendices/A_runs.tex (Rescaled curves): x1.0151 / x1.0201 -> x1.015074 / x1.020113.
43. appendices/A_runs.tex (keyresult): "52 run identifiers: 46 ... 3 ... and 3" -> "52 recorded launches, of which 49 produced scored currents (46 + 3), and 3 launches without a usable curve".
44. appendices/C_decks.tex (run_0039 row): x1.0151 -> x1.015074.
45. appendices/C_decks.tex (run_0040 row): x1.0201 -> x1.020113.
46. appendices/E_reproducibility.tex (Launch budget): added "52 recorded launches, of which 49 produced scored currents" with cref to sec:app-runs-composition.

## Post-pass checks
- No remaining x1.0151 / x1.0201 / x1.015073 / x1.020112 in chapters or appendices; 1.19665 / 1.30426 survive only where they are quoted as the register's known typo (05, 10, 12, D).
- No "partially passed" left; C1 is "partly failed" everywhere.
- All edited files ASCII-only; keyresult begin/end and unescaped braces balanced in every chapter/appendix; every label cited in new text exists (sec:mech-traps, sec:cal-final, sec:num-convergence, sec:app-runs-composition, ch:6p3).
- Citation pages untouched; no number changed except where it disagreed with SYNTHESIS / runs.csv (items 5, 6, 9, 10, 19).

## Unresolved (left for a later pass)
- Duplicated passages not yet collapsed into \cref: run_0027 retraction (03, 05, 07, 09, A), SS_min artefact (04, 05, 06, 07, 12), tmu variants (05, 10, 12, D).
- Ch. 4 tab:d1-e1 ratios law/EM 1.45 / 2.15 (S3 effective-width reference) vs Ch. 5 / Ch. 9 x1.59 / x2.51 (infinite-well bound, SYNTHESIS Q3): different references, both stated; not harmonised.
- Ch. 4 inversion agreement 0.81-1.17 (u = -0.125..-0.025 eV) vs Ch. 9 / SYNTHESIS B2 0.81-1.46 "near Ec": probably different windows; not verified against S4.
- 02d says rescaled mobilities used in run_0041--0047 (intro) and run_0041--0051 (table row).
- Only partly read this pass: 06 (lines 40-262), 09 body, 10-12 bodies, B_code, C_decks, D_register, E_reproducibility.

## Pass 2 (2026-09-26): duplicates collapsed to one statement + \cref, dEc overshoot references, overclaim read of 06, 09-12, B-E
47. 07 (sec:cal-param-control, retracted overlap run): made this the single full statement of the run_0027 retraction by merging the details previously spread over 05 and A (override, x.mesh 24 um vs electrodes 28 um, gate/source shortening, 15-node point drain, L 20.1 um, -2.17 % SENSITIVITY_RESULTS row, withdrawn <2 % claim, kept in catalogue).
48. 07 (tab:cal-oat notes): SS_min note now points to sec:der-metrics.
49. 07 (keyresult): SS_min bullet points to sec:der-metrics.
50. 05 (sec:par-contacts, sensitivity evidence): run_0027 bullet shortened to one sentence + cref sec:cal-param-control.
51. 05 (keyresult, contacts bullet): run_0027 mention cites sec:cal-param-control.
52. 05 (sec:der-powerlaw, discussion): dEc overshoot now names both references (x1.59/x2.51 vs infinite-well upper bound; x1.45/x2.15 vs S3 DFT-anchored effective width) with a disambiguating sentence.
53. 04 (sec:par-dec, derivation (i)): overshoot names its reference (x1.45/x2.15 vs S3 DFT-anchored effective width) and adds the infinite-well x1.59/x2.51 with a disambiguating sentence.
54. 04 (tab:d1-e1 caption): states that ratio law/EM is relative to the S3 effective-width estimate and gives the infinite-well x1.59/x2.51.
55. 04 (sec:der-confinement, summary): the 2x / 1.6x overestimate now names its reference (S3 subthreshold-equivalent shift).
56. 04 (closing summary): same reference named for the ~2x overestimate.
57. 04 (intro, standing corrections): SS_min cites sec:der-metrics.
58. 04 (sec:par-dec, sensitivity): SS_min artefact sentence cites sec:der-metrics instead of restating the source chain.
59. 04 (sec:par-deep): SS_min cref sec:num-convergence -> sec:der-metrics.
60. 04 (naive inversion): SS_min window cites sec:der-metrics.
61. 04 (trap-DOS status): SS_min retirement cites sec:der-metrics.
62. 03 (geometry, overlap): run_0027 one-sentence mention now cites sec:cal-param-control.
63. 03 (measured metrics): SS_min cref -> sec:der-metrics.
64. 06 (sec:num-sweep): SS_min paragraph shortened to one sentence + cref sec:der-metrics.
65. 06 (discussion): SS_min cites sec:der-metrics.
66. 06 (keyresult): SS_min cites sec:der-metrics.
67. 06 (discussion): 'change the drain current by less than 0.01 dec' qualified 'where checked' (V1 2 nm mesh not re-run; ch. 11).
68. 06 (keyresult): overclaim fixed - the 2 nm mesh check is inherited from V0, not demonstrated on the V1 deck.
69. 06 (transition): 'numerics verified' -> 'checked as far as the launch budget allowed'.
70. 09 (sec:mech-confinement): dEc overshoot names both references explicitly, with a disambiguating sentence.
71. 09 (tab:mech-verdicts): overshoot row names both references.
72. 09 (SS artefact paragraph): SS_min cref -> sec:der-metrics.
73. 09 (sec:mech-contacts, extraction methods): run_0027 shortened to one sentence + cref sec:cal-param-control.
74. 09 (tab:mech-verdicts): 'Confinement exists at 2 nm / plausible' -> 'expected (theory); not identified from ID-VG' (overclaim).
75. 09 (couplings, 6.3 nm decomposition): shape part stated as unexplained; C5 is a candidate, not an attribution.
76. 09 (chapter keyresult): transport-change statement marked model-conditional.
77. 09 (chapter keyresult): shape part 'remains unexplained'.
78. 10 (tmu caveat box): explanation shortened to one sentence + cref sec:par-temperature; prediction tables, figure and falsification tables unchanged.
79. 11 (tab:val-status): convergence row qualified 'where checked'.
80. 11 (tab:val-status): confinement row states 'expected; not identified from ID-VG'.
81. 11 (review (d)): shape part 'remains unexplained'.
82. 11 (review (e)): 'Converged' -> 'Converged where checked'.
83. 11 (completed work): launch count stated as 52 recorded launches, 49 with scored currents.
84. 12 (demonstrated item 7): SS_min artefact shortened to one sentence + cref sec:der-metrics.
85. 12 (demonstrated item 10): tmu variants shortened to one sentence + cref sec:par-temperature.
86. 12 (demonstrated item 11): run_0027 shortened to one sentence + cref sec:cal-param-control.
87. 12 (tab:concl-rejected): SS row cites sec:der-metrics.
88. 12 (tab:concl-rejected): overshoot row names the infinite-well reference.
89. 12 (S1): marked model-conditional.
90. 12 (publication claim 4): 'the shape points to a limitation of the constant-mobility model' -> shape unexplained, constant mobility the leading untested candidate.
91. D (known textual error): tmu multiplier explanation shortened to one sentence + cref sec:par-temperature.
92. A (run notes, run_0027): shortened to one sentence + cref sec:cal-param-control.
93. B (sensitivity_analysis.py): run_0027 flagged as retracted.
94. B (S1_s1_poisson1d.py): surrogate 'validated' -> 'checked' against ATLAS (calibrated/validated vocabulary).
95. B (S1_s1_shape_test.py): same wording fix.
96. C (intro): run_0014 is a failed held-out test, not a 'validation' deck.
97. C (tab:decks-set): same.
98. C (subsection title run_0014): same.
99. C (keyresult): same.
100. E (tab:repro-filemap): launch count wording.

### Pass 2 checks
- Read in full this pass: 06, 09, 10, 11, 12, appendices B, C, D, E (tables *_table.tex skipped). No further change needed in 10 beyond the tmu box, in E beyond item 100, in D beyond item 97.
- Single full statements: run_0027 retraction only in 07 sec:cal-param-control (other mentions one sentence + \cref; 09 verdict-table row and 11 checklist 3.4 keep only the "Electrode shortened" keyword); SS_min artefact only in 05 sec:der-metrics (06 tab:num-convergence row and fig. caption keep data only); tmu variants only in 05 sec:par-temperature (10 tables, fig. captions and the register-rule item unchanged; 12 corrections-table row unchanged).
- dEc overshoot: every mention in 04, 05, 09 (and 12 table) now names its reference: x1.45/x2.15 = vs S3 DFT-anchored effective-width estimate; x1.59/x2.51 = vs infinite-well upper bound; x2 / x1.6 = vs S3 subthreshold-equivalent shift.
- tools/lint_latex.py: 0 errors, 0 warnings (26 files, 273 labels, 919 refs). All edited files ASCII; only existing labels cited (sec:cal-param-control, sec:der-metrics, sec:par-temperature, sec:pred-falsification, sec:app-runs-composition, sec:6p3-verdict, tab:d1-e1, ch:app-runs, sec:mech-contacts). No citation page and no number changed.
- Still open from pass 1: Ch. 4 vs Ch. 9 inversion ratio windows (0.81-1.17 vs 0.81-1.46) not verified against S4; 02d run_0041--0047 vs 0041--0051 wording.
- ZIP rebuilt with tools/make_zip.py after this pass.