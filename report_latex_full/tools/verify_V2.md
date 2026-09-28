# Verifier V2 log (2026-09-25)

Scope: chapters 00, 01, 03, 06, 07, 08, 09, 10, 11, 12 and appendices/*.tex (not generated tables).
Input: tools/citation_report.csv. 7 non-OK rows fell in these files, all key Januar2026. Paper text checked in digest/papers/Januar2026.md by printed page.

## Citation rows (non-OK)

| # | file:line | status | verdict | action |
|---|---|---|---|---|
| 1 | 01_introduction.tex:8 (p.~9, 65/85 C) | PARTIAL | p.9 is correct for PBS trap densities (Nt 2 nm vs 10 nm, p.9). The 65/85 C numbers are in a separate citation (row 2) | kept p.~9 |
| 2 | 01_introduction.tex:8 (p.~8, 65/85 C curves) | NOT_ON_PAGE | SI Fig. S12 (65 C and 85 C, 2 nm IWO) is captioned on printed p.11; the main text refers to S12 on p.9; nothing on p.8 | fixed: p.~8 -> SI Fig.~S12, caption on p.~11 |
| 3 | 03_device_data.tex:26 (p.~2, 0.92/1.04 A per cycle) | PARTIAL | on p.2 ("~0.92 A cycle-1 and ~1.04 A cycle-1"); the checker failed to tokenize 1.04 | kept |
| 4 | 03_device_data.tex:230 (p.~7, 12.15) | NUMBERS_NOT_IN_PAPER | 12.15 and 50.17 are workbook values (numbers.md SYNTHESIS D1), not attributed to the paper; the p.7 citation is for "27.4 to 5.1 with Nt about x4", which is on p.7 | kept |
| 5 | 08_six_nm.tex:193 (p.~9, 0.003-0.24 V) | NUMBERS_NOT_IN_PAPER | 0.003-0.24 V is the S4 extrapolation (numbers.md S4 l.217), attributed to the S4 report in the text; the PBS shifts it builds on (0 to 1.2 V, 0 to 0.72 V) are on p.9 | kept |
| 6 | 10_predictions.tex:6 (p.~8, SI Fig. S12) | NOT_ON_PAGE | S12 is referred to on p.9 and captioned on p.11 | fixed |
| 7 | 12_conclusions.tex:48 (pp.~2--3, long-range crystallinity) | NOT_ON_PAGE | "lack long-range crystallinity" (HRTEM, Fig. S2) is on p.2; 6.3/13.2/39 are report numbers, not paper numbers | fixed: pp.~2--3 -> p.~2 |

## Changes

1. chapters/01_introduction.tex l.8
   before: `...lack long-range crystallinity and show thickness-dependent nanoscale grains and a higher surface roughness at 2~nm than at 10~nm \citep[pp.~2--3]{Januar2026}. ... at 65 and 85~$^{\circ}$C \citep[p.~8]{Januar2026}.`
   after:  `...lack long-range crystallinity and show nanoscale grains \citep[p.~2]{Januar2026}, and the AFM roughness is higher at 2~nm than at 10~nm \citep[p.~8]{Januar2026}. ... at 65 and 85~$^{\circ}$C \citep[SI Fig.~S12, caption on p.~11]{Januar2026}.`
   reason: crystallinity and nanoscale grains are on p.2; the direction of the roughness difference (2 nm > 10 nm) is stated only on p.8 (p.2 only says the roughness is thickness dependent); "thickness-dependent grains" is not stated on p.2 (grain sizes appear in the SI captions), so the qualifier was dropped; the 65/85 C curves are SI Fig. S12, captioned on p.11.
2. chapters/10_predictions.tex l.6
   before: `(SI Fig.~S12, referred to on \citep[p.~8]{Januar2026});`
   after:  `\citep[SI Fig.~S12, referred to on p.~9 and captioned on p.~11]{Januar2026};`
   reason: S12 is referenced on p.9 (twice) and captioned on p.11, not on p.8. The citep inside parentheses was also removed.
3. chapters/12_conclusions.tex l.48
   before: `ultrathin films lack long-range crystallinity \citep[pp.~2--3]{Januar2026}.`
   after:  `ultrathin films lack long-range crystallinity \citep[p.~2]{Januar2026}.`
   reason: the statement is on p.2 only.
4. chapters/11_validation.tex l.73 (row was not flagged, same error as in the introduction)
   before: `AFM roughness is higher at 2~nm than at 10~nm \citep[pp.~2--3]{Januar2026}.`
   after:  `AFM roughness is higher at 2~nm than at 10~nm \citep[p.~8]{Januar2026}.`
   reason: the 2 nm > 10 nm AFM RMS statement is on p.8; p.3 has no roughness statement.
5. chapters/07_calibration.tex l.125
   before: `the fixed-current slopes by $-2.5$ to $-3.8$~mV/dec`
   after:  `the fixed-current slopes by $-1.2$ to $-3.8$~mV/dec`
   reason: runs.csv, run_0003->run_0008 gives -2.45/-3.80 mV/dec and run_0004->run_0009 gives -1.20/-2.51 mV/dec for the two fixed-current windows, so the range runs from -1.2, not -2.5.

No PAGE_MISSING rows in these files.

## Numbers spot-checked against runs.csv / numbers.md (all consistent unless listed above)

- 00_abstract: Vth_cc 0.662/0.644/0.083; mu_FE 12.2/11.0/50.2; rms 0.136 vs 0.133; -0.294 V; 4.6-fold (50.17/10.95); 338/358 K.
- 03_device_data: 12.15/50.17 and factors 2.4/1.8 vs 5.1/27.4; the 0.92/1.04 A per cycle (paper p.2).
- 06_numerics: checks A' (run_0028 vs 0013: -0.4 mV, -0.03 mV/dec, -0.01 %), L (run_0036 vs 0015: 0.0625/0.0626, -0.3 mV, +0.02), C' (+2.0/+2.5 %, +0.9/+1.1 mV, +0.7/+0.8), C'' (+2.5/+1.0/+0.5 %), linearity +7.9 %/+7.9 %, SSmin 83.1 vs 73.2, Ion errors 0.00/-1.48/-1.97.
- 07_calibration: all numeric cells of tab:cal-history for runs 0001-0009, 0012-0015 and 0038-0040 (Vth_cc, Vth_lin, both fixed-current SS windows, mu_FE, Id(3V) error, active RMSE); stage 2 shifts -0.309/-0.310, Vth_lin -0.277/-0.284, Ion +27.1/+18.2 %; stage 3 -9/-6 mV (slope range corrected); stage 5 -0.07/-0.09 mV and 0.002 %; stage 6 +1.98/+0.48 %; 0.333/0.287 V, 47 mV.
- 08_six_nm: Delta Vth_cc for runs 0014, 0015, 0030-0035, 0037, 0052 (-0.294, +0.007, -0.017, -0.258, -0.264, -0.243, -0.079, -0.057, +0.010, +0.004); 0.003-0.24 V; n = 15.7 sigma^2/Delta^2.
- 09_mechanisms: 0.579/0.292/50.4 %; one-at-a-time leverages (runs 0048, 0020/0021, 0023, 0024, 0025, 0022, 0026, 0050, 0016) all match; DOS offset +2.48/+0.95/+0.50 % at equal mobility.
- 10_predictions: Ion(0045)/Ion(0038) = 0.7742; ratio 1.024879 vs 1.024873; mu_band 17.6897/11.582/61.6046.
- 11_validation: SS_cc package +14.6, WTA +0.8, Dit x3 +0.5 mV/dec.
- 12_conclusions: gap range 0.72-0.88 V (computed 0.724-0.879), 0.939, 1.202, SS_cc 410.9; SSmin 73.2/83.1, 151.3/138.6, fixed-current 90.8/92.0; 289.1 vs 303.7; dEc(2 nm) = 0.353 eV; (358.15/300)^1.5 x 0.7742 = 1.0098; +20/+6/+25 mV/dec window misses; +0.036, +0.030, +0.051, 0.215 V.
- appendices/A_runs: run_0027 Ion -2.15 %; x1.0151 / x1.0201 rescalings.

## Unresolved / notes (not edited)

- 07_calibration.tex l.170 (figure caption) gives rescale factors x1.000000, x1.015073, x1.020112, while the table and text use x0.999983, x1.015074, x1.020113. Probably the plotting script's own rounding; the figure script was not checked (out of scope).
- 06_numerics.tex l.364 and 12_conclusions.tex l.19 say run_0038 and run_0012 have "equal Ion within 0.01 %"; runs.csv gives 5.08975e-7 vs 5.09029e-7 = -0.0106 %. This is a rounding-level difference and was left.
- appendices/A_runs.tex l.113: eps_r HfO2 19.57 and IWO 9.30 are attributed to the SI of Januar2026 (SI Fig. S1b). The SI figure data are not bundled in the digest (used_items.csv: NOT_FOUND_BY_STRING). Main text p.2 gives only "approximately 9" for IWO. Not verifiable here.
- abstract "Fifty-two ATLAS runs were made": run_0011 was never executed and run_0010 and run_0018 produced no scored currents; the count is of catalogued run IDs. Wording left as is.
