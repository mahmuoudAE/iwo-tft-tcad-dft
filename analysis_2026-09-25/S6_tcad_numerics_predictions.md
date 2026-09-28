# S6: TCAD numerical validity, robust metrics, 6.3 nm hypothesis closure and the prediction register

Specialist S6, 2026-09-25. No ATLAS launch; no package script or config modified. Scripts and outputs are in `analysis_2026-09-25/scratch/S6/`:
- `s6_lib.py`: helpers; it imports `scripts/extract_metrics.py` unchanged.
- `s6_part1_numerics.py` → `s6_part1_out.txt/.json`.
- `s6_part2_robust.py` → `s6_part2_out.txt/.json`.
- `s6_part3_predictions.py` → `s6_part3_out.txt/.json`.
- `s6_write_register.py` → `PREDICTIONS_REGISTER.md` (registered 2026-09-24T23:24:53Z) and `predictions_canonical.csv` (1917 rows).

Simulated legacy metrics are recomputed exactly as `run_atlas.py` does: `np.interp` from the native grid onto the 0.05 V measurement grid.

**Robust metrics used below** (all at the drain bias of the data, Vd = 0.7 V):
- **V(I):** Vg at a fixed current I, by log-linear interpolation.
- **SS(I1..I2):** fixed-current slope, [V(I2) − V(I1)]/log10(I2/I1).
- **gap:** Vth_lin − Vth_cc.
- **gap7:** V(1e-7) − Vth_cc.
- **Ion/gm:** Ion/gm_max, in V.

## 0. Bottom line

1. **Numerics are closed.**
   - Id is linear in mu_band to 1e-5.
   - ID-VD at Vd = 0.7 V reproduces the rescaled transfer curves to < 0.001 %.
   - The 6.3 nm mesh check passes: A7/run_0036 gives max 0.0039 dec and ΔVth_cc −0.3 mV.
   - The DOS 384/192 residual is +0.16 % Ion at 2 nm (Richardson extrapolation, order 2.0).
   - Native zeros occur only at Vg ≤ −0.10 V with |Id| ≤ 6.3e-18 A/µm, three decades below every measured floor.
2. **SS_min is not a valid metric.** A 2.6 % current difference at a single grid point (Vg = 0.15 V) moves it by 10 mV/dec. The fixed-current SS at 1e-11..1e-10 A/µm reproduces the data within 2.3 mV/dec for all three films.
3. **The model must fit and the data must reproduce this on-state shape** (§3.3). With the converged model, 2 and 13.2 nm fit the subthreshold region, but the on-state shape is missed:

   | film | gap miss | gm miss |
   |---|---|---|
   | 2 nm | −0.145 V | −8.6 % |
   | 6.3 nm | −0.362 V | −23 % |
   | 13.2 nm | −0.021 V | −2.6 % |

   No tested V1 change repairs the 6.3 nm on-state without breaking its subthreshold:
   - B0 fixes the gap but raises SS_cc by 116 mV/dec.
   - C1 keeps SS but recovers only 35 % of the gap.

   The most likely cause is the model form: a constant, density-independent mobility.
4. **Work function, electron affinity and Qf are one parameter.** Each is an exact rigid shift at every thickness tested (max |Δlog Id| ≤ 1.6e-5 after a 0.100 V shift), so none can alter the thickness dependence. m* (through Nc) is second order: it changes the 2→13.2 nm Vth step by +14.9 mV.
5. **Pre-registered tests:**
   - S2's B0 on-state and S1's B0 SS_cc (418 predicted, 410.9 obtained) passed.
   - B0's subthreshold failed.
   - S4's C1 partially passed: gm and SS were met, but the gap came out +0.12 V against +0.28 V predicted, and Ion +16 % against ±3 %.
   - The A6 held-out Vth_cc passed at −57 mV.
   - The S2 MTR temperature expectations were reproduced by ATLAS (P-MTR variant) within 1 mV and 0.4 %.
6. **The register is written.** It holds ID-VD shape, temperature changes in two exact variants (P-phonon and P-MTR, because ATLAS applied tmu = 1.5), activation energies and falsification criteria, with SHA-256 hashes.

## 1. Numerical closure (Task 1)

### 1.1 Exactness of rescaling

**Linearity in mu_band:**
- The run_0029/run_0038 current ratio is 1.024879 (min 1.024817, max 1.025135 over 43 points with Id > 1e-14), against 18.13/17.69 = 1.024873.
- The run_0008/run_0003 ratio is 1.079171, against 1.079167.

The rescalings B2 ×1.015074 (11.582/11.41) and B3 ×1.020113 are therefore exact.

**Path independence.** B8–B10 at Vd = 0.7 V equal the rescaled B1/B2/B3 at Vg = 1–3 V to 0.000 %.

### 1.2 DOS 96/48 → 384/192 (same mu after exact rescale)

The offset depends on Vg and is not a constant Ion factor:

| film (pair) | ΔId at Vg 0.7 / 1.5 / 2 / 3 V | ΔVth_cc | ΔVth_lin | Δgm | ΔSS fixed-current |
|---|---|---|---|---|---|
| 2 nm (0012→0029) | −0.95 / +2.56 / +3.64 / +2.48 % | +1.1 mV | −22.0 mV | +0.9 % | ≤ +0.8 |
| 6.3 nm (0015→B2 ×11.69/11.41) | −0.63 / +0.78 / +1.12 / +0.95 % | +0.7 | −4.8 | +0.6 % | ≤ +0.6 |
| 13.2 nm (0013→B3 ×61.9/60.39) | −0.04 / +0.68 / +0.64 / +0.50 % | +0.2 | −4.5 | +0.3 % | ≤ +0.3 |

**Refinement series at 2 nm:**
- Ion changes +1.98 % (96→192) and +0.48 % (192→384), which gives an observed order p = 2.03.
- The Richardson residual beyond 384/192 is +0.16 % Ion and about −1.4 mV Vth_lin.

**Thickness dependence.** The Ion offset at 3 V scales 1 : 0.38 : 0.20, close to Nt(t) = 2.0e19 : 8.5e18 : 4.9e18 (1 : 0.43 : 0.25). It is a quadrature error of the discretized tail. Its sign flips between threshold (trapped charge over-counted) and the on-state (under-counted). Where ATLAS places the levels is NOT DETERMINED.

**Recalibrated band mobilities:**

| film | mu_band (cm²/Vs) | Ion error at the run's mu |
|---|---|---|
| 2 nm | 17.6897 | B1 0.00 % |
| 6.3 nm | 11.5820 | B2 −1.48 % at 11.41 |
| 13.2 nm | 61.6046 | B3 −1.97 % at 60.39 |

### 1.3 Mesh, KCL, native zeros

**Mesh ×0.7:**

| film (runs) | max Δlog Id | ΔVth_cc | ΔSS fixed-current | ΔVth_lin | Δgm | ΔIon |
|---|---|---|---|---|---|---|
| 6.3 nm (A7 run_0036 vs run_0015) | 0.0039 dec (rms 0.0012) | −0.32 mV | ≤ 0.07 mV/dec | −0.15 mV | −0.02 % | −0.013 % |
| 13.2 nm (run_0028 vs 0013) | 0.0029 dec | −0.36 mV | — | — | — | −0.013 % |

The 6.3 nm check L therefore PASSES.

**KCL.** The maximum is 2.5e-16 A over transfer runs 0012–0052 (0 failures) and 1e-14 A for ID-VD runs 0041 and 0042.

**Native zeros.** There are 6–17 non-positive points per run on the native grid. All sit at Vg ≤ −0.10 V with |Id| ≤ 6.3e-18 A/µm. No metric uses them; simulated Ion/Ioff remains a lower bound.

### 1.4 Why SS_min moved from 73.2 to 83.1 mV/dec

SS_min is the minimum over 5-point windows whose first point exceeds 5× the measured floor. At 2 nm that threshold is 2.30e-14 A/µm. Two runs sit on either side of it at Vg = 0.15 V:
- run_0012: Id(0.15 V) = 2.34e-14. The first window starts at 0.15 V and gives 73.2 mV/dec.
- B1: Id(0.15 V) = 2.28e-14. The window jumps to 0.20 V and gives 83.1 mV/dec.

run_0003 → run_0008, a pure ×1.079 mobility scaling, flips SS_min the same way (83.1 → 73.2).

Fixed-current SS agrees within 1–2 mV/dec in both cases:

| pair | SS 1e-11..1e-10 | SS 1e-10..1e-9 |
|---|---|---|
| run_0012 / B1 | 122.5 / 123.5 | 212.9 / 215.0 |

At 13.2 nm, run_0013 vs run_0017 gives SS_min 151.3 vs 138.6 but fixed-current 90.8 vs 92.0. This confirms S3's artefact finding.

The measured 13.2 nm window 1e-11..1e-10 sits only 1.5× above the floor (6.6e-12). Subtracting the floor changes its SS from 136.1 to 91.8 mV/dec, so floor-subtracted values are used.

**Recommendation.** Retire SS_min. Use V(1e-9), SS over 1e-11..1e-10 and over 1e-10..1e-9, SS_cc, and the on-state shape markers gap7 and Ion/gm.

### 1.5 Residual numerical uncertainty per metric (final DOS 384/192 runs)

| metric | DOS residual | mesh | interpolation/grid | total numerical |
|---|---|---|---|---|
| Vth_cc, V(I) | < 0.5 mV | ≤ 0.4 mV | log-linear vs PCHIP ≤ 1.5 mV | **±1.5 mV** |
| fixed-current SS | < 0.3 mV/dec | ≤ 0.1 | ≤ 1.1 (measured 13.2 nm at 1e-11: 4.6) | **±1 mV/dec** |
| SS_min | — | — | window phase ±10 | **invalid** |
| Vth_lin | about −1.4 mV (2 nm) | 0.15 mV | 0.1 V solver grid above 1.5 V biases sim vs data by −5.4 / −0.8 / −11.7 mV | **±2 mV + that bias** |
| gm_max, mu_FE | about 0.1 % | 0.02 % | −0.4 / 0 / −0.7 % | **±0.7 %** |
| Ion, Id | +0.16 / ~0.06 / ~0.03 % | 0.013 % | exact | **±0.2 %** |

### 1.6 Final converged comparison (B1 ×0.999983, B2 ×1.015074, B3 ×1.020113)

Each cell is measured / simulated.

| t (nm) | Vth_cc | SS 1e-11..1e-10 | SS 1e-10..1e-9 | SS_cc | Vth_lin | gap | gap7 | gm (A/V/µm) | mu_FE | Ion/gm (V) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.0 | 0.662 / 0.680 | 121.2 / 123.5 | 194.8 / 215.0 | 269.9 / 290.9 | 1.663 / 1.537 | 1.001 / 0.856 | 1.051 / 1.024 | 3.807e-7 / 3.478e-7 | 12.15 / 11.10 | 1.337 / 1.463 |
| 6.3 | 0.644 / 0.653 | 124.5 / 124.5 | 210.0 / 215.6 | 295.4 / 289.7 | 1.820 / 1.466 | 1.176 / 0.814 | 1.224 / 1.085 | 3.431e-7 / 2.631e-7 | 10.95 / 8.39 | 1.176 / 1.534 |
| 13.2 | 0.083 / 0.054 | 91.8* / 90.9 | 118.8* / 143.4 | 158.4* / 193.0 | 1.044 / 0.995 | 0.962 / 0.941 | 0.571 / 0.630 | 1.572e-6 / 1.531e-6 | 50.17 / 48.85 | 1.953 / 2.005 |

\* Measured 13.2 nm floor (6.6e-12) subtracted.

Ion matches to 0.00 % at every film by construction.

**What fits and what misses:**
- Vth_cc is within +19 / +9 / −29 mV.
- The deep subthreshold (1e-11..1e-10) is within 2.3 mV/dec in all films.
- In 1e-10..1e-9 the model is too soft by +20 / +6 / +25 mV/dec.
- The on-state shape misses mainly at 6.3 nm, somewhat at 2 nm, and hardly at 13.2 nm.

## 2. Parameter isolation (Task 2; B4–B7 vs B1/B3, same mu)

| change | film | ΔVth_cc | ΔSS 1e-11..1e-10 / 1e-10..1e-9 / cc | ΔVth_lin | ΔIon | rigid-shift test |
|---|---|---|---|---|---|---|
| WF +0.1 eV (run_0048) | 2 | +0.100 V | 0 / 0 / 0 | +0.092 | −6.8 % | exact 0.100 V shift, max Δlog 1.6e-5 |
| WF +0.1 eV (run_0049) | 13.2 | +0.100 | 0 / 0 / 0 | +0.092 | **−5.0 %** | exact, 4.1e-6 |
| χ ∓0.1 eV (runs 0020/0021, 96/48) | 2 | ±0.100 | 0 | ±0.091 | ∓6.9/7.0 % | exact, 6e-6 |
| Qf pairs (0001→0003, 0002→0004, 0005→0007) | 2 / 13.2 / 6.3 | −309.2…−309.7 / −309.4…−309.8 / +293.6…+294.2 mV across 1e-11…1e-7 | — | — | — | analytic −309.5 / +293.9 mV |
| m* ×1.3 (run_0050) | 2 | −0.044 | −10.2 / −18.0 / −17.7 | −0.043 | +4.1 % | not rigid (0.17 dec) |
| m* ×1.3 (run_0051) | 13.2 | −0.029 | −4.7 / −10.5 / −13.2 | −0.061 | **+5.8 %** | not rigid |

**Correction to EVIDENCE_BRIEF §5b.** The 13.2 nm ΔIon values relative to the B3 baseline are −5.0 % (WF) and +5.8 % (m*). The brief's −6.9 % and +3.7 % are errors relative to the *measurement*.

**Effect on the thickness dependence:**

| change | 2→13.2 ΔVth_cc | Ion(13.2)/Ion(2) | SS_cc(13.2) − SS_cc(2) |
|---|---|---|---|
| WF +0.1 eV | −0.6251 → −0.6251 V (0.0 mV) | 5.914 → 6.031 (+2.0 %) | unchanged |
| m* ×1.3 | +14.9 mV (2.4 % of the step) | +1.6 % | −97.1 → −92.7 mV/dec |

- **WF.** The Ion ratio moves only because Ion is read at a fixed Vg of 3 V: Ion/gm is 1.46 V at 2 nm against 2.00 V at 13.2 nm. Refitting Qf removes this.
- **m\*.** The Vth shift equals SS_local × log10(1.3^1.5): Nc changes the free/trapped partition at fixed current, as a mobility change would through the constant-current definition.

**Identifiability.** WF, χ and Qf are exactly one number per curve and are thickness-independent. The only thickness-dependent alignment terms in V1 are:
- dEc(t);
- the tail filling Nt(t);
- Nd·t;
- the constant-current mobility term.

A thickness-dependent interface dipole or charge is indistinguishable from dEc(t) on ID-VG (S3), because the Qf shift is constant across five decades of current.

## 3. 6.3 nm hypothesis closure (Task 3)

### 3.1 Robust metrics

The measured row gives absolute values; the other rows give model minus measured (Ion/gm is absolute). run_0014, run_0015, A1–A6 and B0 use DOS 96/48; B2 and C1 use 384/192. The DOS effect on these metrics is ≤ 1 mV / 0.6 mV/dec / 1 %.

| run | Vth_cc | SS 1e-11..1e-10 | SS 1e-10..1e-9 | SS_cc | gap | gap7 | gm | Ion/gm (V) | Ion | RMSE (dec) |
|---|---|---|---|---|---|---|---|---|---|---|
| measured | 0.644 | 124.5 | 210.0 | 295.4 | 1.176 | 1.224 | 3.431e-7 | 1.176 | 4.03e-7 | — |
| 0014 validation | −0.294 | −2.2 | +1.4 | −10.5 | −0.314 | −0.161 | −16.6 % | 1.788 | +26.8 % | 0.678 |
| 0015 tuned | +0.007 | −0.4 | +4.4 | −6.6 | −0.356 | −0.137 | −23.1 % | 1.529 | 0.0 % | 0.063 |
| B2 (0039 ×1.0151) | +0.009 | 0.0 | +5.6 | −5.7 | −0.362 | −0.139 | −23.3 % | 1.534 | 0.0 % | 0.059† |
| A3 back −1.64e12 | −0.017 | −21.8 | −43.2 | −64.1 | −0.452 | −0.267 | −18.4 % | 1.648 | +14.4 % | 0.237 |
| A1 t = 5.3 nm | −0.258 | 0.0 | +5.0 | −4.9 | −0.297 | −0.137 | −18.1 % | 1.735 | +20.8 % | 0.613 |
| A2 Nd0 1e16 | −0.264 | −2.0 | −1.3 | −14.7 | −0.329 | −0.168 | −17.5 % | 1.773 | +24.4 % | 0.634 |
| A4 Dit ×5 | −0.243 | +2.8 | +3.5 | −9.1 | −0.319 | −0.160 | −16.9 % | 1.742 | +23.1 % | 0.595 |
| A6 no QC, Qf from 2 nm | −0.057 | +0.6 | +4.8 | −7.7 | −0.337 | −0.154 | −18.4 % | 1.574 | +9.2 % | 0.211 |
| A5 combination | −0.079 | −14.9 | −28.4 | −45.9 | −0.405 | −0.221 | −19.6 % | 1.664 | +13.9 % | 0.246 |
| B0 S2 re-partition | +0.010 | **+48.8** | **+103.8** | **+115.5** | +0.026 | +0.115 | −5.0 % | 1.144 | −7.6 % | 0.270 |
| C1 near-Ec band, mu 15.4 | +0.004 | +1.4 | +12.9 | +9.0 | −0.237 | −0.137 | −3.5 % | 1.413 | +16.0 % | 0.081 |

† Run at mu 11.41.

A7 is a numerical duplicate of run_0015 (§1.3).

**Ion-matched view.** Rescaling the mobility so that Ion matches the measurement:

| run | mu_band | gm vs measured | gap |
|---|---|---|---|
| C1 | 13.28 | −16.8 % | unchanged (−0.237) |
| B0 | 21.2 | +2.8 % | +0.026 |

So:
- C1 recovers 28 % of the gm miss and 35 % of the gap miss while keeping SS.
- B0 recovers the whole on-state but adds +116 mV/dec to SS_cc.

### 3.2 Pre-registered predictions and outcomes

Timestamps are UTC file times; run end times come from RUN_INDEX.

| # | prediction (source, registered) | quantity: predicted → obtained | outcome |
|---|---|---|---|
| P1 | S2 for B0 (`s2_part3_out` 18:59:35Z; config B 19:06:27Z; run_0037 ended 19:21:30Z) | Vth_cc 0.64 ± 0.03 → 0.654 ✓; Vth_lin 1.82–1.90 → 1.856 ✓; Ion −5…−10 % → −7.6 % ✓; mu_FE 10.5–11.0 → 10.40 ✗ (1 % low); SS_min +3…+15 over run_0015 → +30.8 ✗ (SS 1e-11..1e-10 +49) | on-state **passed**, subthreshold **failed** → re-partition rejected as the explanation |
| P2 | S1 for B0 (1-D code 19:18:00Z; its output file 19:24:15Z is after the run ended; the code reads run_0014 parameters, not run_0037 → blind) | SS_cc 418 (±10) → 410.9 ✓; Vth_cc 0.656 → 0.654 ✓; gm 3.31e-7 → 3.26e-7 ✓; Vth_lin 1.889 → 1.856 (−33 mV, marginal) | **passed** (blind, not strictly timestamp-pre-registered) |
| P3 | S4 for C1 (`s4_part3_out` 19:21:48Z; config C 19:35:23Z; run_0052 ended 22:47:22Z), vs run_0015 | gap +0.28 → +0.119 ✗; gm +24 % → +25.5 % ✓; SS_cc +23 (range +20…+30) → +15.6 (≈); Ion ±3 % → +16.0 % ✗; stated falsifiers (gm not rising, or SS_cc > 330) not triggered | **partially passed** |
| P3' | S1's competing expectation for C1: the gap does not open without SS_cc rising well above 295 | gap +0.12 of the +0.36 needed, at SS_cc 304 | consistent |
| P4 | A6 held-out (design in config A 18:28:53Z; run 18:57Z) | Vth_cc −57 mV (vs −294 with confinement); SS within 8 mV/dec; gap −0.34 V; Ion +9 % (mu 12.4 is labelled "FITTED per thickness", origin undocumented → Ion is not held-out) | threshold **passed** at the ±0.1 V level; on-state failed (common to all runs) |
| P5 | A2 analytic bound ≤ +0.03 V (config A) | +0.030 V | **passed** |
| P6 | A4 discriminator: traps shift Vth *and* degrade SS | +0.051 V; SS 1e-11..1e-10 +5.0, SS_min +8.3 | **passed** (qualitative) |
| P7 | S2 MTR expectation at 350 K (`s2_part2_out` 18:56:57Z; runs 0044–0047 ended 21:21–21:54Z), vs ATLAS P-MTR | ΔVth_cc −64/−66 → −63.4/−65.6 mV; mu_FE ×0.993/0.999 → 0.9930/1.0002; Ion ×1.004/1.011 → 1.0084/1.0131; ΔVth_lin −15/−24 → −22.7/−25.9; Ea within 1–7 meV | **passed** (numerical cross-check only) |
| P8 | S3: ATLAS SP/BQP at 6.3/13.2 nm moves Vg(n_s = 1e12) by +0.15…0.19 V | not run (budget) | not yet tested |
| P9 | S1: 13.2 nm no-confinement run with Qf 4.76e10 → Vth_cc 0.33 | exact rigid identity from run_0017: 0.331 V (miss +0.248 V; required Qf 1.43e12, confirming S1/S4 over the brief's ~1.86e12) | determined by identity; no run needed |
| P10 | S5: Januar Fig. 5a mu_sat(6.3 nm) = 3.86 | figure values not local | not yet tested |
| P11 | This register (ID-VD, 338/358 K) | — | not yet tested |

### 3.3 What remains unexplained and why

**The unexplained feature.** The measured 6.3 nm curve reaches 1e-7 A/µm 1.224 V after Vth_cc, and then rises with Ion/gm = 1.176 V. Every simulation whose fixed-current SS is within ~15 mV/dec of the data in every window sits at:
- gap7 ≤ 1.09 V;
- Ion/gm ≥ 1.41 V.

**The trade-off within V1's form.** Every trap-side change moves along one line that gains gap at the cost of SS_cc:

| step | Δgap | ΔSS_cc | gap gained per SS lost |
|---|---|---|---|
| B2 → C1 | +0.125 V | +15 mV/dec | 8.5 mV per mV/dec |
| B2 → B0 | +0.388 V | +121 mV/dec | 3.2 mV per mV/dec |

Even at C1's efficiency, the missing +0.36 V costs SS_cc ≈ 332 against 295 measured.

**What would break the trade-off.** The feature needs current that rises faster than the free charge above threshold, without extra subthreshold charge. That is a carrier-density-dependent (percolation or power-law) mobility, which also lowers SS.

**Ranked model-form causes:**
1. Constant, density-independent mobility. ATLAS ignores MOBILITY statements between SOLVEs (a verified runner fact), so V1 cannot emulate this within a sweep.
2. Rigid equilibrium tails with no above-threshold trapping or sweep history (S4: PBS 0.003–0.24 V).
3. Gate-field quantization with local tails. S3 estimates +0.15–0.19 V in Vg(1e12) at t ≥ 6.3 nm, but this should also appear at 13.2 nm, where the classical model already fits.

**Correlation with thickness.** The miss is largest at 6.3 nm, smaller at 2 nm and negligible at 13.2 nm. This matches S2's disordered-thin vs 13.2 nm step. It is a correlation, not a demonstration.

## 4. Model validity statement for a reviewer (Task 4)

- **Classical DD at 2 nm.** S3's Schrödinger-Poisson shows trap-free electrostatics are adequate: rigid within 11 mV and C_eff within 1 %.
  - ATLAS dEc = 0.353 eV (realised 0.315–0.345 V) lies at the top of the SP range: bracket 0.14–0.38, central 0.26–0.30 V for m* 0.18.
  - The trap-limited device depends on the **tail energy reference**: tails that follow the confined edge give a 0.26 V shift, tails left at the bulk edge give 0.91 V. V1 implicitly uses the confined edge. This is NOT DETERMINED (localization length vs t).
- **Electrons only.** The hole current is 1e-38 to 1e-55 A (check I), so this is safe for on/subthreshold. The off-state floors are not modelled (13–17 decades above thermal generation). Ioff comparisons remain invalid.
- **Constant mobility.** mu enters exactly linearly. mu_band therefore lumps together:
  - any Rsd;
  - C_eff/Cox ≈ 0.87 (S3);
  - the m*(t) Drude term (−18 % at 2 nm, S2);
  - roughness.

  It carries no density or field dependence, which is the cause identified in §3.3.
- **Ideal Ohmic contacts.** Rsd is not identifiable from one ID-VG (α–θ correlation +1.00, S5). The model-conditional bounds are ≲ 5e4 Ω·µm at 2 nm and ≲ 1–2e4 Ω·µm at 13.2 nm. The ID-VD register (§5) is the test.
- **Tail reference under confinement.** Above; this is the dominant model-form uncertainty at 2 nm.
- **dEc law extrapolation.** It exceeds the effective-mass bound beyond about 3 nm: ×1.45–1.59 at 6.3 nm and ×2.15–2.51 at 13.2 nm (S2, S3). The Vth impact is ≤ 35 mV. The DFT-anchored curve (0.357 / 0.050 / 0.012 eV) should replace it.
- **Regularized sheets.** The interface sheets live in a 0.25 nm layer. Halving that layer changes Id by ≤ 0.009 dec and −0.06 % (check E). C1's band is moment-matched in the same layer.
- **run_0027 is malformed** (S5: the drain collapsed to a zero-width line at x = 24 µm). **The "OAT overlap_4um" row in `tables/SENSITIVITY_RESULTS.{md,csv}` (−2.17 % Ion) must be retracted**, together with "contact geometry … irrelevant" in `docs/SUPERVISOR_SUMMARY.md`. With ideal-Ohmic boundaries the model cannot test contact physics at all.
- **tmu = 1.5 (silicon default)** in all T ≠ 300 K runs. The as-simulated runs are "phonon-like". Both variants are registered, and each is exact.
- **Other issues:**
  - DOS 96/48 errors were Vg-dependent (Vth_lin −22 mV at 2 nm); all final numbers are now at 384/192.
  - The 0.1 V solver grid above 1.5 V biases sim Vth_lin by up to −12 mV.
  - SS_min is invalid.
  - The 6.3 nm Qf is device-specific.
  - N = 1 device per thickness.

## 5. Prediction register (Task 5): `PREDICTIONS_REGISTER.md`, `predictions_canonical.csv`

### ID-VD (B8–B10, 300 K)

| film | Id(0.1)/Id(0.05), Vg 1 → 3 V | Vd_sat (gd = 10 % of gd0), Vg 1 → 3 V | gd(3 V)/gd0 | Id(Vg 3, Vd 0.1 / 3 V) (A/µm) |
|---|---|---|---|---|
| 2 nm | 1.80 → 1.97 | 0.43 → 1.80 V | 0.01–0.17 % | 8.77e-8 / 8.69e-7 |
| 6.3 nm | 1.81 → 1.97 | 0.44 → 1.90 V | 0.01–0.19 % | 6.90e-8 / 7.14e-7 |
| 13.2 nm | 1.91 → 1.98 | 0.68 → 2.30 V | 0.03–0.68 % | 5.04e-7 / 6.39e-6 |

d²Id/dVd² < 0 at Vd → 0 everywhere (no S-shape). Id(13.2)/Id(2) at Vg 3 V rises from 5.75 (Vd 0.1 V) to 7.35 (Vd 3 V). The genuine prediction content is the shape normalised to the calibrated Vd = 0.7 V point; absolute values at Vd 0.7 V are calibration.

### Temperature (358.15 K)

| quantity | 2 nm | 6.3 nm | 13.2 nm |
|---|---|---|---|
| ΔVth_cc, P-MTR | −73.1 mV | −78.9 mV | −76.3 mV |
| ΔVth_cc, P-phonon | −40.5 mV | −46.7 mV | −56.6 mV |
| ΔVth_lin (both variants) | −26.5 mV | −34.5 mV | −30.1 mV |
| ΔSS 1e-10..1e-9, P-MTR | −12.1 | −12.5 | −10.6 |
| ΔSS 1e-10..1e-9, P-phonon | +2.0 | +2.4 | −3.3 |
| mu_FE ratio, P-MTR | ×0.992 | ×1.000 | ×1.000 |
| mu_FE ratio, P-phonon | ×0.760 | ×0.766 | ×0.767 |
| ΔIon, P-MTR | +1.0 % | +2.2 % | +1.5 % |
| ΔIon, P-phonon | −22.6 % | −21.6 % | −22.2 % |

At 338.15 K (2 nm), ΔVth_cc is −49.3 mV (P-MTR) and −27.9 mV (P-phonon).

**Activation energy Ea(Vg), P-MTR, meV:**

| film | Vg 0.5 | 1 | 1.5 | 2 | 3 V |
|---|---|---|---|---|---|
| 2 nm | 124 | 57 | 23 | 8 | 1.5 |
| 6.3 nm | 128 | 53 | 20 | 9 | 3.5 |
| 13.2 nm | 63 | 21 | 8 | 5 | 2.4 |

P-phonon is exactly 42.3 meV lower at every Vg.

**Thickness ratio.** mu_FE(13.2)/mu_FE(2) goes from 4.40 to 4.44 in both variants.

**Falsifiers** (full map in register §6):
- S-shaped low-Vd output → non-Ohmic contacts.
- ΔIon > ~+5 % at 358 K → activated band mobility or percolation.
- ΔIon ≈ −22 % → phonon-limited band transport.
- Thin-film Ea(3 V) > Ea(13.2) + 10 meV, or the mu_FE ratio shrinking toward 3.3 → no common transport mechanism.
- ΔVth_cc outside −35…−85 mV, or a thickness spread ≫ 20 mV → charge beyond equilibrium tail filling.

Numerical uncertainty is ±0.2 % on currents, ±1.5 mV on V(I) and < 0.5 meV on Ea. DOS convergence was verified only at 300 K.

## 6. Calibration vs validation status of the major claims (Task 6)

Status codes: DN = demonstrated-numerically; CAL = calibrated; PNT = predicted-not-yet-tested; PTP = prospectively-tested-passed; FAIL = failed; ASM = assumed.

| # | claim (source) | status | evidence |
|---|---|---|---|
| 1 | 2 / 13.2 nm fits 0.037 / 0.081 dec (FINAL_STATUS) | CAL | now 0.043 / 0.081 at 384/192 (B1, B3) |
| 2 | 6.3 nm tuned fit 0.063 dec | CAL (device-specific Qf + mu) | B2 0.059 |
| 3 | Shared laws predict 6.3 nm | **FAIL** | run_0014: −0.294 V, 0.678 dec |
| 4 | "6.3 nm reproduced in SHAPE" (FINAL_STATUS) | subthreshold PTP; **on-state FAIL** | SS 1e-11..1e-10 −2.2; gap −0.31 V, gm −17 % |
| 5 | Confinement accounts for the 2 vs 13.2 nm Vth step; "it was tested" (FINAL_STATUS #1, SUPERVISOR #1) | DN within the model; physically ASM | rigid-degenerate with 1.7e12 cm⁻²; A6 favours no-QC; wording "tested" should be removed |
| 6 | Subthreshold follows Nt(t) + WTA + Dit "without tuning" | CAL | SS 1e-11..1e-10 within 2.3; 1e-10..1e-9 +6…+25 mV/dec |
| 7 | mu_band fitted per film; no law (FINAL_STATUS #3) | CAL | — |
| 8 | Physical deck ≡ reduced deck | DN | runs 0008/0012, 0009/0013 |
| 9 | Qf is an exact rigid shift; Id linear in mu | DN | §1.1, §2 |
| 10 | Mesh/DOS convergence | DN | §1.2–1.3; residual +0.16 % |
| 11 | Removing confinement moves SS toward the data | **FAIL (artefact)** | §1.4 |
| 12 | Donors and permittivity irrelevant at 2 nm | DN | runs 0022, 0026 |
| 13 | Contact geometry irrelevant; SENSITIVITY overlap row | **retract** | run_0027 malformed |
| 14 | WF, m*, 6.3 nm sensitivities "not run" (FINAL_STATUS) | superseded | runs 0030–0036, 0048–0051 |
| 15 | 86 % of the model's 2→6.3 drop is dEc (S1) | DN | 1-D surrogate ≤ 3 mV vs ATLAS |
| 16 | No confinement + 2 nm Qf predicts 6.3 nm Vth (S1, S3) | PTP (Vth only) | A6 −57 mV |
| 17 | A1/A2/A3/A4/A5 rejected as the sole cause (S1, S4) | DN (model-conditional) | §3.1 |
| 18 | Trap/mobility re-partition explains 6.3 nm (S2) | **FAIL** (on-state PTP) | B0 SS_cc +116 |
| 19 | Near-Ec band explains the 6.3 nm shape (S4) | partially PTP / **FAIL** on gap and Ion | C1 |
| 20 | 6.3 nm on-state shape is not a rigid offset | DN | all A/B/C runs |
| 21 | Paper mu 5.1 / 27.4 = saturation formula (S2, S5) | passed (retrodiction of independent numbers) | 5.09 / 27.40 |
| 22 | Structural step between 6.3 and 13.2 nm (S2) | PNT (correlation) | T series, GIXRD |
| 23 | MTR temperature signature (S2) | numerical PTP; physical PNT | P7; register |
| 24 | Confinement 0.26–0.30 V at 2 nm (S3 SP) | PNT (theory) | optical gap / IPES |
| 25 | dEc not identifiable from ID-VG (S3) | DN | exact degeneracy |
| 26 | t^-1.38 law unphysical beyond 3 nm | DN (analytic, effective-mass) | ≤ 35 mV Vth impact |
| 27 | Floors = ungated parallel path, not gate leakage (S4) | PNT (correlation) | IG/IS |
| 28 | Rsd cannot explain the thickness trend (S5) | correlation; bounds CAL | TLM |
| 29 | WF/χ/Qf are one parameter; m* second-order (S6) | DN | §2 |
| 30 | Ideal Ohmic contacts, constant mobility, T-independent tails | ASM | register tests |
| 31 | ID-VD and 338/358 K predictions | PNT | `PREDICTIONS_REGISTER.md` |

**Other document corrections:**

| document | correction |
|---|---|
| EVIDENCE_BRIEF §5b | 13.2 nm isolation ΔIon values (§2) |
| EVIDENCE_BRIEF §4 | 13.2 nm no-confinement Qf is 1.43e12, not ~1.86e12 |
| S1 §3.1 | A7 now has execution.json (PASS) |
| NUMERICAL_CONVERGENCE | check L → PASS (run_0036); check C' → resolved by recalibration |

## Verdicts

| item | verdict | evidence class | key number |
|---|---|---|---|
| Linear rescaling in mu_band (B2 ×1.0151, B3 ×1.0201) | demonstrated | numerical | ratio error 6e-6 |
| DOS 384/192 converged | demonstrated | numerical | residual +0.16 % Ion (2 nm), p = 2.0 |
| DOS offset thickness dependence | demonstrated | numerical | +2.48 / +0.95 / +0.50 % ∝ ~Nt(t); Vg-dependent sign |
| 6.3 nm mesh (check L) | PASS | numerical | 0.0039 dec, −0.3 mV |
| KCL / native zeros | PASS / harmless | numerical | ≤ 2.5e-16 A; zeros ≤ 6.3e-18 A/µm at Vg ≤ −0.10 V |
| SS_min as a metric | rejected | numerical audit | 73.2 ↔ 83.1 from 2.6 % at one point |
| Fixed-current SS 1e-11..1e-10 | model matches all films | calibration | within 2.3 mV/dec |
| WF/χ/Qf degeneracy | demonstrated (exact, thickness-independent) | numerical | 0.100 V rigid, Δlog ≤ 1.6e-5 |
| m* effect on thickness dependence | second-order | numerical | +14.9 mV on a 0.625 V step |
| B0 re-partition (S2) | rejected | prospective test | on-state passed, SS_cc +116 |
| S1's B0 SS_cc 418 | passed (blind) | prospective surrogate | 410.9 |
| C1 near-Ec band (S4) | partially passed; not the explanation | prospective test | gap +0.12 vs +0.28 V; Ion +16 % |
| A6 held-out Vth_cc | passed (Vth only) | prospective | −57 mV |
| S2 MTR temperature expectations vs ATLAS P-MTR | passed | numerical cross-check | ΔVth_cc within 0.6 mV |
| 6.3 nm on-state shape | unexplained within V1 | — | gap −0.36 V, gm −23 % |
| Constant mobility as the most likely cause | plausible, unverified | inference from the trade-off | 3.2–8.5 mV gap per mV/dec SS |
| run_0027 SENSITIVITY row | retract | numerical audit (S5) | drain collapsed |
| Temperature predictions (tmu 1.5) | registered in two exact variants | prediction | ΔIon(358 K, 2 nm) +1.0 % vs −22.6 % |
| ID-VD predictions | registered | prediction | Id(0.1)/Id(0.05) 1.80–1.98, no S-shape |
