# NC audit: C10 S1-05 (3-D NC300) against S0-01 (quasi-2D NC300), 2.0 nm

**Status:** analysis only, 2026-10-11. No ATLAS/DeckBuild launch, no run_atlas/run_campaign call, no edit to a registered file, `RUN_INDEX.csv`, `data/` or `results/runs/`. The audit used no launch.

**Runs:**
- S0-01 = `results/runs/run_0061_2p0_c10_s0_01_2p0`, NC300 = 1.373e19 cm^-3 (quasi-2D, N2D/t).
- S1-05 = `results/runs/run_0072_2p0_c10_s1_05_2p0`, NC300 = 3.21785e18 cm^-3 (3-D formula, m* = 0.2543 m0).

**Registered stop rule:** `campaign_extract.py:185-187` and `CAMPAIGN_DESIGN.md:299`. The registered compare gives:
- dV_th,cc = **+142.15 mV**, against an expected +40 to +70 mV: FAIL;
- dSS = +48.7 mV/dec in the fixed window and +29.7 in the A1 window;
- d(active RMSE) = −0.314 dec (0.367 → 0.053).

**Labels used here:**
- [ATLAS]: solver output read directly.
- [CALC]: closed-form arithmetic on ATLAS output.
- [1-D]: the vertical Poisson model of section 3.2, validated against ATLAS nodes.
- [EST]: estimate from existing curves; not an ATLAS result.

## 0. Verdict

**Outcome (ii), an explainable electrostatic response.** The +142 mV is the 37.5 meV statistics shift, amplified by trapped charge in the exponential acceptor tail.
- **(i) Implementation error is excluded** (section 1).
- **(iii) Inadequate statistics contributes < 1 mV at V_th,cc** (section 5). It matters only above threshold, as about 7 to 8 % in I_on.
- **Why the registered band failed.** The expectation converted 37.5 meV into V_G with a slope factor of about 1.47 (≈ 87 mV/dec; `DFT_TO_TCAD.md:28`). At the criterion current (1e-9 A/um), S0-01's local swing is 211 mV/dec, and it rises to 290 mV/dec across the 0.63 decade of the NC ratio. The model is right; the registered expectation was wrong.

## 1. Implementation check (outcome i): no error found

| Check | Evidence | Result |
|---|---|---|
| Deck difference | `diff device.in`: only line 73 (S0-01) / 72 (S1-05) `nc300=`, plus the two header comments (lines 16 and 32) | Only NC300 differs |
| Solver received it | `deckbuild.out:252` (S0-01) `Nc 1.37e+019`; `deckbuild.out:251` (S1-05) `Nc 3.22e+018`. ni 5.03e-10 / 2.43e-10 (lines 254/253) | ni ratio 2.07 = sqrt(4.267) [CALC]. The rest of the material echo (lines 230-440) is identical |
| Trap tables | `acceptor_r1/r2.dat`, `donor_r1/r2.dat` | Identical apart from the timestamp line |
| Occupancy as implemented | ATLAS stores the ionised-acceptor density (structure code 1038000). It is reproduced at every node in x = 12 um, in both runs and at all three saved biases, by the formula in section 3.1 with the run's own NC | Max relative error ≤ 1.3e-5. One node on the region 1/2 boundary is excluded: it stores the region-2 trap fields |
| Charge balance | Gate equation V_G = V_n + (Φ_M − χ) − (E_c − E_Fn)_int + q(n_sh + N_A,sh − Q_f − N_D t)/C_ox, with nodal sheets at x = 12 um | Closes to ≤ 0.1 mV at 6 of 6 saved states [CALC] |
| Solver warnings | One `Projection cannot be done` per run, at the drain ramp (`deckbuild.out:1177` / `1182`). This is the standard first-step message; no convergence failures | Identical in both runs |

## 2. Shift/scale diagnostic (part 1): the change is not rigid

The fit maps log I(S1-05)(V) ≈ log I(S0-01)(V − ΔV) + c. Both runs are read on their native grids.

| Window (S1-05 current) | Shift only: ΔV, rms (max) | Shift + scale: ΔV, log10 s, rms |
|---|---|---|
| 1e-15 to 1e-12 | 40.0 mV, 0.012 (0.016) dec | (3 points, degenerate) |
| 1e-14 to 1e-9 | 54.2 mV, **0.242 (0.365)** | 4.6 mV, **−0.566**, **0.009** |
| Fixed SS window 5e-11 to 5e-10 | 92.2 mV, 0.083 | 10.2 mV, −0.541, 0.001 |
| 1e-9 to 1e-7 | 186.1 mV, 0.074 (0.172) | 123.4 mV, −0.168, 0.027 |
| On-state, V_G 1 to 3 V | **222.8 mV, 0.014 (0.043)** | 215.1 mV, −0.012, 0.012 |
| Whole active range | 62.6 mV, 0.237 | 35.5 mV, −0.245, 0.137 |

**Local horizontal shift V(S1) − V(I) − V(S0)(I) (mV)** [ATLAS]:

| I (A/um) | 1e-15 | 1e-13 | 1e-12 | 1e-11 | 1e-10 | 1e-9 | 1e-8 | 1e-7 | 5e-7 |
|---|---|---|---|---|---|---|---|---|---|
| ΔV (mV) | 38.5 | 40.5 | 43.5 | 54.3 | 83.6 | 142.5 | 211.2 | 236.1 | 230.9 |

**Vertical difference at fixed V_G**, log10(I_S1/I_S0):

| V_G (V) | 0.1 | 0.5 | 1.0 | 2.0 | 3.0 |
|---|---|---|---|---|---|
| Δlog10 I (dec) | −0.630 | −0.597 | −0.453 | −0.142 | −0.065 |

The pure NC ratio is −0.630 dec.

**Reading.**
- In subthreshold the change is a **current scale at fixed V_G**, not a voltage shift. It equals the NC ratio (−0.630 dec) at low V_G and falls to −0.60 dec at 0.5 V, where free-carrier screening starts.
- Above threshold it becomes a near-rigid shift of 0.215 to 0.223 V.
- At a current criterion the horizontal shift therefore equals the 0.63-decade drop read through the local swing. It grows from 38.5 mV (deep subthreshold, which is the registered "pure statistics" value) to 142.5 mV at 1e-9 A/um.
- Why fixed V_G gives a scale: the ATLAS trap occupancy depends only on η = (E_Fn − E_c)/kT (section 3.1). At a fixed band position the trapped charge is therefore independent of NC, while n scales with NC. In subthreshold the gate charge is trapped plus fixed charge, so the bands do not move.

## 3. Matched-current comparison (part 2)

### 3.1 Occupancy formula (verified against ATLAS)

ATLAS steady-state acceptor occupancy, with σ_n = σ_p = 1e-15 cm^2. The hole terms p and p1 vanish for E_g = 3.38 eV and carriers = 1.

    f(E) = n / (n + n1(E)),   n1(E) = NC exp(-(Ec - E)/kT)
         = F_1/2(η) / (F_1/2(η) + exp(-d/kT)),   d = Ec - E,   η = (E_Fn - Ec)/kT

- In the non-degenerate limit this is the Fermi-Dirac occupancy referenced to E_Fn.
- Trapped sheets are trapezoid integrals of g(d)·f over the deck's own `afile` tables. Those tables come from the DEFECTS lines `device.in:84-98` (S0-01 numbering) and contain:
  - tail: NTA 5e20 cm^-3/eV, WTA 0.04 eV, in both regions;
  - deep Gaussian: 5e16 at 0.6 eV, W 0.15, region 1;
  - interface Gaussian: 1.16757e19 at 0.3016 eV, W 0.124, region 2 (0.25 nm). This is the 3e11 cm^-2/eV sheet.

### 3.2 Method

**Profiles.** The full vertical profile at the channel centre (x = 12 um) comes from a 1-D model. It integrates Poisson from the free top surface (zero field under the air layer) to the Al2O3 interface. It uses the deck values: ε = 9.3, N_D = 2.5e17, Q_f = 1.38345e12 at y = 0, C_ox = 8.9554e-7 F/cm², Φ_M − χ = 0.68161 eV.

**How each level is fixed.**
- At each current level, V_G is taken from each run's own I_D–V_G curve.
- n_centre at that V_G comes from the native probe `chan_electrons_vg.dat` at (12, −0.001) um.
- The model profile is the one with that centre density.

**Validation against the ATLAS nodes in `*.str`.**
- u_top and u_int agree within 0.1 meV, and n_sheet within 0.4 %.
- N_A,sheet agrees within 0.8 %. The exception is equilibrium, at 8 %, where the sheet is only 1e10 cm^-2 and the difference is the region-boundary node, worth < 0.2 mV.
- V_G agrees within −1.6 mV at 0.7 V and −7.8 / −4.3 mV at 3 V.

**Inferred local V_n.** The local quasi-Fermi potential V_n(x = 12) inferred from the model agrees with the ATLAS QFL at the saved biases. Model: 0.0804 at 0.672 V and 0.312 at 2.97 V. ATLAS: 0.0832 at 0.7 V and 0.309 at 3.0 V.

### 3.3 States at matched current

Columns are S0-01 / S1-05. E_c − E_Fn is the local value in meV.

| I (A/um) | V_G (V) | n_centre (cm^-3) | n_avg probe | E_c−E_Fn centre | E_c−E_Fn interface | Tail sheet (cm^-2) | D_it sheet | Free sheet |
|---|---|---|---|---|---|---|---|---|
| 1e-12 | 0.206 / 0.250 | 8.42e14 / 7.97e14 | 8.79e14 / 8.27e14 | 250.7 / 214.6 | 251.1 / 214.6 | 1.67e10 / 4.05e10 | 4.46e10 / 5.20e10 | 1.68e8 / 1.59e8 |
| 1e-10 | 0.372 / 0.456 | 5.38e16 / 3.96e16 | 5.18e16 / 3.81e16 | 143.2 / 113.6 | 140.4 / 107.6 | 2.25e11 / 4.46e11 | 6.07e10 / 6.24e10 | 1.09e10 / 8.16e9 |
| **1e-9** | **0.530 / 0.672** | 3.02e17 / 2.09e17 | 2.89e17 / 2.05e17 | **98.5 / 70.0** | **89.4 / 54.4** | **6.23e11 / 1.12e12** | 6.30e10 / 6.37e10 | 6.33e10 / 4.60e10 |
| 1e-8 | 0.829 / 1.040 | 1.41e18 / 1.10e18 | 1.40e18 / 1.14e18 | 57.9 / 24.7 | 34.9 / −9.7 | 1.42e12 / 2.31e12 | 6.38e10 / 6.40e10 | 3.28e11 / 2.75e11 |
| 1e-7 | 1.461 / 1.697 | 6.10e18 / 6.86e18 | 6.63e18 / 7.11e18 | 16.9 / −38.5 | −35.1 / −106.7 | 2.53e12 / 3.45e12 | 6.41e10 / 6.41e10 | 1.75e12 / 1.76e12 |
| 5e-7 | 2.736 / 2.967 | 2.12e19 / 2.87e19 | 2.56e19 / 3.01e19 | −25.0 / −130.0 | −135.8 / −266.6 | 3.29e12 / 3.85e12 | 6.41e10 / 6.41e10 | 7.05e12 / 7.06e12 |

The deep Gaussian (2.33e9 cm^-2) is fully occupied in both runs at every level.

### 3.4 Decomposition of dV_G = V_G(S1-05) − V_G(S0-01) at matched current

All terms are in mV. Terms (1) to (6) sum to the ATLAS value exactly; (6) is the closure.

| Level | ATLAS dV_G | (1) pure statistics δ | (2) density mismatch / degeneracy at centre | (3) in-film bending | (4) **trapped charge**: tail + D_it + deep | (5) free carriers | (6) local QFL dV_n(x=12) |
|---|---|---|---|---|---|---|---|
| 1e-13 | 40.5 | 37.5 | −0.5 | +0.1 | **+2.8** (1.1 + 1.7 + 0.0) | 0.0 | +0.6 |
| 1e-11 | 54.3 | 37.5 | −4.3 | +1.2 | **+15.2** (14.5 + 0.7) | 0.0 | +4.7 |
| 1e-10 | 83.6 | 37.5 | −7.9 | +3.1 | **+39.7** (39.4 + 0.3) | −0.5 | +11.6 |
| **1e-9 (V_th,cc)** | **142.5** | **37.5** | **−9.0** | **+6.5** | **+89.5** (89.4 + 0.11 + 0.00) | **−3.1** | **+21.1** |
| 1e-8 | 211.2 | 37.5 | −4.3 | +11.4 | +158.8 | −9.5 | +17.3 |
| 1e-7 | 236.1 | 37.5 | +17.9 | +16.2 | +164.3 | +2.3 | −2.2 |
| 5e-7 | 230.9 | 37.5 | +67.5 | +25.7 | +100.1 | +1.5 | −1.5 |

**At V_th,cc (1e-9 A/um), 142.5 mV splits into:**

| Part | mV | Share | Detail |
|---|---|---|---|
| (a) free-carrier statistics shift | 37.5 | 26 % | kT ln 4.267 |
| (b) trapped-charge change Q_trap/C_ox | 89.5 | 63 % | +5.0e11 cm^-2 more electrons in the tail (6.23e11 → 1.12e12). The interface sheet adds 0.1 mV and the deep Gaussian 0 |
| in-film bending | 6.5 | 5 % | Electrostatic consequence of (b) |
| free-carrier charge | −3.1 | | |
| lateral channel term | +12.1 | | (2) + (6): at the same terminal current the S1-05 mid-channel density is 0.69× and V_n(12 um) is 21 mV higher. This is a 2-D channel-profile effect, not model error |

- The model-only closure at the saved biases is ≤ 1.6 mV.
- At E_F about 90 meV below E_c, the trap response is entirely the 40 meV tail. At matched local density the tail sheet rises 2.16× (6.23e11 → 1.35e12 cm^-2). The asymptotic value is exp(δ/W_TA) = 2.55; the linear estimate 1 + δ/W_TA = 1.94 is too low.

**Intrinsic split at matched local density** [1-D]. S1-05 is solved at the S0-01 centre density of each level (`nc_audit_supp_results.json`, part A).

| Level | dV | δ | bending | tail | D_it | free |
|---|---|---|---|---|---|---|
| 1e-9 | **178.7** | 38.2 | 9.8 | **129.7** (73 %) | 0.14 | 0.8 |
| 1e-10 | 97.3 | 37.6 | 4.3 | 54.9 | 0.4 | 0.0 |
| 1e-12 | 43.8 | 37.5 | 0.4 | 4.5 | 1.4 | 0.0 |

The lateral term in the matched-current number reduces this local 179 mV to the terminal 142.5 mV.

## 4. Analytic cross-check (part 3)

All values in mV.

| Level | ATLAS | δ·SS_S0/(kT ln10), registered style with the simulated local SS | δ(1 + C_trap/C_ox), S0-01 state | δ(1 + C_trap/C_ox), S1-05 state | Rigid-profile nonlinear: δ + qΔN_trap(δ)/C_ox |
|---|---|---|---|---|---|
| 1e-12 | 43.5 | 42 | 42 (C/C_ox 0.11) | 45 (0.21) | 43 |
| 1e-10 | 83.6 | 73 | 73 (0.95) | 104 (1.77) | 91 |
| **1e-9** | **142.5** | **133** | **126 (2.37)** | **178 (3.74)** | **159** |
| 1e-8 | 211.2 | 259 | 198 (4.28) | 209 (4.56) | 211 |

- C_trap = q² dN_trap,sheet/dE_F is taken numerically on the self-consistent profile.
- The analytic band [126, 178] mV at 1e-9 brackets ATLAS (142.5) and the local 1-D value (178.7).
- The linear form underestimates because the tail response is exponential: e^{0.94} − 1 = 1.55, not 0.94.
- The registered +40 to +70 mV corresponds to C_trap/C_ox ≈ 0.1 to 0.9. The simulated device has that only below about 1e-10 A/um.
- The registered band would have passed for a criterion at or below 1e-11 A/um (38.5 to 54 mV).

## 5. Quasi-2D NC in F_1/2 versus genuine 2-D statistics (part 4, outcome iii)

**Function-level comparison** (same NC = N2D/t).

| η | −3 | −1 | 0 | +1 | +3 |
|---|---|---|---|---|---|
| F_1/2(η)/F_0(η) | 1.007 | 1.046 | 1.104 | 1.200 | 1.472 |
| ATLAS trap drive F_1/2(η)/e^η (FD = 1) | 0.983 | 0.891 | 0.765 | 0.580 | 0.223 |

**Device level** [1-D]. Genuine 2-D is approximated by local F_0 carriers plus Fermi-Dirac trap occupancy, on the S0-01 parameters.

| Level | η centre / interface | dV_G at the same n_sheet: F_0 carriers only | dV_G at the same n_sheet: full 2-D | n_sheet ratio at the same gate drive (full 2-D) |
|---|---|---|---|---|
| 1e-12 | −9.7 / −9.7 | 0.00 mV | 0.00 mV | 1.000 |
| 1e-10 | −5.5 / −5.4 | +0.02 | +0.07 | 0.999 |
| **1e-9** | −3.8 / −3.5 | +0.09 | **+0.86** | 0.992 |
| 1e-8 | −2.2 / −1.4 | +0.7 | +8.2 | 0.963 |
| 1e-7 | −0.7 / +1.4 | +9.9 | +47.5 | 0.910 |
| V_G = 3 V | +1.2 / +5.9 | +62.3 | **+124.2** | **0.928** |

**Answer.**
- **Subthreshold and V_th,cc:** the quasi-2D override reproduces 2-D statistics. The V_G error at fixed n_sheet is +0.86 mV at 1e-9 A/um, +0.07 mV at 1e-10 and 0.00 mV at 1e-12. So (iii) does not cause the 142 mV.
- **On-state:** it does not reproduce 2-D statistics. At V_G = 3 V, true 2-D gives about 7 % less sheet charge, so I_on is overstated by about 7 to 8 % (−0.03 dec), or +0.12 V at the same n_sheet.
  - About half of this comes from F_1/2 against F_0.
  - About half comes from ATLAS's n1-form occupancy, which under-fills traps when degenerate.
- **Comparison with DFT_TO_TCAD.** The "1.7×" of `DFT_TO_TCAD.md:125` is the fixed-η ratio. Self-consistently the gate fixes the charge, so the error appears as about −7 % n_sheet.
- **Not covered.** A real single-subband gas has a |ψ1|² profile and no interface pile-up. The classical solution puts η_int = +5.9 within about 0.25 nm of Al2O3. The dark-space reduction of the effective C_ox (an order-of-magnitude estimate, 5 to 10 % for a centroid shift of 0.5 to 1 nm in ε = 9.3) affects the on-state of both NC branches.

## 6. NC is a reparametrisation in subthreshold (consequence for calibration)

Because f depends only on n/NC, the change NC → NC/r is identical, at fixed n, to moving every acceptor level deeper by kT ln r:
- NTA × r^{kT/W_TA}, which is 2.554 here;
- EGA + 37.5 meV for both Gaussians.

The free-carrier part is a rigid kT ln r, which is absorbed by Q_f − C_ox δ/q = −2.10e11 cm^-2.

**Numerical test** [1-D]. The quasi-2D model with Q_f = 1.1738e12 and the shifted tables reproduces the 3-D-NC model at matched n_sheet:

| Level | |dV_G| |
|---|---|
| ≤ 1e-11 | ≤ 0.04 mV |
| 1e-9 | 2.2 mV |
| 1e-8 | 16 mV |
| 1e-7 | 68 mV |
| 5e-7 | 136 mV |

The residual comes only from F_1/2 degeneracy.

**Consequences.**
- The NC choice cannot be identified from subthreshold or V_th data. Only the degenerate on-state carries information, and there neither branch is genuine 2-D physics (section 5).
- S1-05's better fit is not evidence for 3-D statistics:
  - V_th,cc error +11 mV against −131 mV for S0-01;
  - active RMSE 0.053 against 0.367 dec;
  - I_D(3 V) error +0.5 % against +16.7 %.

  The shared start values (Q_f, N_s, W_T) were FITTED in V1/V2 with the 3-D NC (V2 used 3.24e18; `DFT_TO_TCAD.md:27`). S1-05 is therefore close to the calibrated V2 state.
- The override acts only at 2.0 nm, while Q_f and N_s are shared. A quasi-2D shared fit must therefore absorb a 2.0-nm-only factor:
  - 2.55 in the effective tail density (N_s,eff(2 nm) ≈ 1.0e13 against 4e12 cm^-2);
  - or a 37.5 meV level shift, or 2.1e11 cm^-2 of Q_f.

  This will appear as an apparent thickness dependence of N_t (α) and/or a Q_f offset.

## 7. Recommendation for the NC treatment

1. **Keep quasi-2D N2D/t as the provisional primary at 2.0 nm, and keep the 3-D NC as the robustness branch,** as Codex proposes. S1-05 already exists, so no new launch is needed.
   - Quasi-2D is the correct DOS in the regime that sets V_th and SS: single subband with E21 = 0.72 eV, and an error against genuine 2-D statistics of < 1 mV at V_th,cc.
   - 3-D NC at 2 nm has no physical basis beyond being the V2 convention.
2. **The S4/S5 reports must state the NC convention with every trap or Q_f number.** For any trap-thickness law (α, N_s) or Q_f inference, show both branches. The branch difference at 2 nm is exactly ×2.55 in N_TA (or 37.5 meV in level depth) and 2.1e11 cm^-2 in Q_f.
3. **Do not use the S0-01 versus S1-05 fit quality to choose between the branches,** because it reflects which convention the start values were fitted in.
4. **Treat 2.0 nm on-state differences below about 0.05 dec as model-form uncertainty in both branches.** This covers the quasi-2D-in-F_1/2 I_on overstatement of about 7 to 8 % and the classical charge centroid. Implementing true 2-D statistics, for example through user-defined statistics, is not justified by the V_th/SS observables.
5. **Use the local amplification factor A = SS_loc/(kT ln10) at 1e-9 A/um as the rule of thumb for any NC-type change.** A is about 3.5 at 2.0 nm (S0-01), 3.0 at 6.3 nm and 2.6 at 13.2 nm (upper bounds) [EST]. For example, the S6 quasi-2D box at 6.3 nm (NC × 1.467) forecasts dV_th,cc = −10 mV (bare) to −29 mV (scale bound) [EST], not −10 mV.

## 8. Proposed amendments to H-E and N1 (for the register; not applied here)

**Affinity alone is exactly rigid in this model class.** Traps are referenced to E_c, Q_f and N_D are fixed, the S/D contacts are Ohmic and holes are not solved. So dV_G = −Δχ at every current, and E_g has no effect.

**The terms of the 2.0 nm all-off run (S3-01) against S0-01** at 1e-9 A/um [EST, from the ATLAS curves]. Deck values were read from in-memory deck text: S3-01 has χ 4.3, NC 2.380e18, MUN 15.865.

| Term | dV_th,cc (mV) | Basis |
|---|---|---|
| Affinity | **−281.6** | Exact |
| NC 1.373e19 → 3.218e18 | **+142.5** | ATLAS (S1-05) |
| NC 3.218e18 → 2.380e18 | **+29.6 to +38.5** | Secant in ln NC (lower) to pure scale (upper) |
| MUN × 1.2225 | **−24.2 to −25.9** | I ∝ MUN exactly |
| **Total** | **−135 to −125** | |

**H-E, 2.0 nm all-off.**
- Replace −0.23 ± 0.04 V by **−0.13 ± 0.03 V** against S0-01.
- Also register **S3-01 − S1-05 = −0.272 ± 0.010 V**. This is cleaner, because it removes the trap-amplified NC step that S1-05 already measured.

**H-E, 6.3 and 13.2 nm.** These change only through the mass in NC (×1/1.079 and ×1/1.031) and through the mobility (×1.052 and ×1.021).

| Film | Affinity (mV) | NC (mV) | Mobility (mV) | Total (mV) | Registered (V) |
|---|---|---|---|---|---|
| 6.3 nm | −62.2 | +2.0 to +6.0 | −4.0 | about −60 | −0.062 ± 0.015, keep |
| 13.2 nm | −23.5 | +0.8 to +2.0 | −1.3 | about −23 | −0.023 ± 0.008, keep |

**H-E, share of the measured 2.0 → 13.2 nm shift.** It falls from 36 ± 7 % to about **18 ± 6 %**: (0.13 − 0.023)/0.579.

**Shared-fit statement.** "≥ 0.15 V without confinement" must be re-derived before the freeze, because the 2.0 nm confinement contrast shrinks to about 0.13 V. This audit does not compute it.

**AFF-2p0 / AFF-6p3.**
- Register −281.6 and −62.2 mV at every current level, with the S1 numerics tolerance of 5 mV. A larger deviation is an implementation finding.
- This restores N1's rigid mapping for affinity-only differences: ΔV_th = +Δ(ΔE_c) = −Δχ, 1:1. *(Sign corrected 2026-10-11 after the Codex re-check; the earlier text read −Δ(ΔE_c). The equivalence statement in nc_audit_results.json was also corrected: an NC reduction by r is equivalent to trap depths increasing by kT ln r.)*
- Any accompanying NC/mass change is not rigid. It is amplified by A (item 5 of section 7).

**Caveat.** The rigidity rests on the ASSUMED convention that the tail and Gaussian levels follow the confined band edge. ATLAS DEFECTS energies are measured from E_c. If localised tail states did not shift with the 0.28 eV confinement, the affinity term would not be rigid. This is untested and should be listed as a scope limit of H-E.

## 9. Limitations

- The 1-D model is a vertical slice at x = 12 um. The lateral term in section 3.4 is obtained as a closure, not modelled. It is identified with the mid-channel QFL difference, which is consistent with the n_centre ratio of 0.69 and with the ATLAS QFL at the saved biases.
- The genuine-2-D comparison uses a local F_0 approximation. Wavefunction and dark-space effects are not computed.
- The H-E 2.0 nm numbers combine one ATLAS result (S1-05) with curve-based estimates. An S3-01 launch would replace them; none was made.
- Simulated currents below about 1e-17 A/um are noise (KCL floor about 1e-18). The levels used start at 1e-15.

## 10. Files and reproduction

**Scripts.**
- `nc_audit/nc_audit.py`: parts 1 to 6. Output `nc_audit_results.json`.
- `nc_audit/nc_audit_supp.py`: matched-local-density split, reparametrisation test, registered SS extraction, H-E arithmetic, and in-memory deck parameters via `campaign_tools.entry_deck`. Output `nc_audit_supp_results.json`.

**Run commands**, from the package root:

    set IWO_MODEL_FILE=config/iwo_material_model_v3.yaml
    <venv>\Scripts\python.exe -I -B analysis_2026-10-10_campaign/nc_audit/nc_audit.py
    <venv>\Scripts\python.exe -I -B analysis_2026-10-10_campaign/nc_audit/nc_audit_supp.py

**Inputs** (read only):
- both run folders: `device.in`, `deckbuild.out`, `terminal_currents.csv`, `chan_electrons_vg.dat`, `avg_electrons_vg.dat`, `acceptor_r*.dat`, `equilibrium.str`, `near_vth.str`, `final.str`;
- runs 0068 and 0069 (6.3 and 13.2 nm slopes);
- `campaign_extract.compare/extract` (registered extraction; its writer `main()` was not called).

**Side effect.** Importing `campaign_extract`/`campaign_tools` during the first run created two bytecode caches, `analysis_2026-10-10_campaign/__pycache__/campaign_extract.cpython-313.pyc` and `campaign_tools.cpython-313.pyc`. These are not source files; later runs use `-B`.
