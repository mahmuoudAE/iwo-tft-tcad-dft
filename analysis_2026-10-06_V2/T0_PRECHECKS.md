# Model V2, step T0: checks and pre-registration (no ATLAS launch)

Written 2026-10-06, before any V2 launch. Script: `t0_prechecks.py` (output `t0_results.json`); V2 model file: `config/iwo_material_model_v2.yaml`, written by `make_v2_model.py`.

The user approved the plan on 2026-10-05: launch budget 57 → 71, thin DFT films, and labelled scenarios if the prediction test fails.

## 1. Off-current floors (T0a)

### Measured floors
`t0_floor_data.py` gives the measured floors (median over Vg −2 to −0.5 V).

| Film | Floor (A/µm) | Device total | Shape over −3 to −0.5 V |
|---|---|---|---|
| 2.0 nm | 4.61e-15 | 1.3 pA | rises from 0.05 to 1.5 pA; smooth (lag-1 autocorrelation 0.86). Looks like a start-of-sweep transient on a setup-level floor |
| 6.3 nm | 1.53e-13 | 44 pA | flat (−0.011 dec/V); noisy ±30 % (mostly random) |
| 13.2 nm | 6.60e-12 | 1.9 nA | flat (−0.002 dec/V, ±3 %) |

The floors scale as t^3.85 from 2 to 13.2 nm.

### Which explanations survive
Excluded before any model:
- **Gate leakage.** It would be largest at −3 V and change ≥ 3× over the range. The 6.3 and 13.2 nm floors are flat, and the 2 nm floor is lowest at −3 V.
- **A current range fixed by the on-current.** The 2 and 6.3 nm devices have similar on-currents but floors 33× apart.
- **A back-surface path coupled to the gate.** Flatness within 3 % over 2.5 V would need about 2e16 cm⁻² eV⁻¹ of pinning states.

The floor must therefore be a gate-independent current from drain to source, or an instrument effect.

### Ungated-strip screen
The candidate is a strip of the same film outside gate control. Its sheet conductance is q·n₀·μ₀·t, with n₀ from charge neutrality using the V1 donor, tail and deep-state laws. One geometric factor (W/L) is fitted on 13.2 nm.

| Strip variant | Scaling | 2 nm, pred/meas | 6.3 nm, pred/meas |
|---|---|---|---|
| N: neutral film | t^2.99 | 5.07 | 1.21 |
| D: one surface with the V1 interface acceptor sheet (6.4e10 cm⁻²) | t^4.24 | 0.48 | 0.77 |
| Q: as D plus Qf 1.73e12 (same interface as the channel) | t^1.25 | 134 | 4.76 |

Plan criterion: both predicted floors within 3×. **Only variant D passes.**

### How robust variant D is
Each input scaled by 2 in turn, with W/L re-fitted each time:

| Change | 2 nm, pred/meas | 6.3 nm, pred/meas |
|---|---|---|
| Dit ×0.5 | 1.92 | 0.99 |
| Dit ×2 | 0.06 | 0.37 |
| Nd₀ ×0.5 | 0.15 | 0.43 |
| Nd₀ ×2 | 1.64 | 0.97 |

- The 6.3 nm prediction is robust.
- The 2 nm prediction is not a strong test. It also sits at the setup floor, so an under-prediction there would not contradict the data.

The uniform-film approximation holds: the band bending across the film from the surface sheet is a few meV, much less than kT.

### Model adopted in V2 (T1)
I_D,total(Vg) = I_ATLAS(Vg) + G_D(t)·V_D.
- G_D(t) = q·n₀,D(t)·μ₀(t)·t·(W/L)ₚₐᵣ, with (W/L)ₚₐᵣ = 1.03e-4 per µm of width (fitted on 13.2 nm).
- Adding a gate-independent parallel conductance after the solver is exact at fixed V_D, so it costs no launch.
- **Status: hypothesis.** The strip's location and interface are not determined; that needs gate and source currents, an L-series and the layout.

## 2. DFT into TCAD (T0b)

### New laws
Fitted through our DFT points (PBE; RESULTS_LOG 2026-10-04/05):

| Quantity | Law | DFT points | V1 law |
|---|---|---|---|
| Conduction-band shift dEc | 0.78504 t^-1.50400 eV | 0.848 (0.95 nm), 0.281 (1.98 nm) | 0.9205 t^-1.3815, all in the CB |
| Gap opening dEg | 0.83997 t^-1.34569 eV | 0.900, 0.335 | same law as dEc |
| Mass increment Δm* | 0.11416 t^-1.29453 m₀ | +0.122, +0.047 (bulk PBE 0.159) | 0.1311 t^-1.4121 |

- HSE06/PBE ratio of the gap opening: 1.06 (range 1.06–1.11). PBE is kept as the central value, as PROTOCOL_CERN pre-registered.
- The power laws are used only for t ≥ 0.95 nm. The 0.75 and 0.51 nm films enter as tabulated DFT points (T4).

### Effect on the curves
Exact consequences:
- Every trap level in the decks is referenced to Ec and the contacts are ideal Ohmic. So an affinity change shifts the transfer curve rigidly by the change of dEc.
- A Qf change is a rigid shift, verified to 1 mV.
- Id is linear in a uniform mobility.
- The mass term comes from the isolation runs 0050/0051 (m* ×1.3 → −0.043 V at 2 nm, −0.028 V at 13.2 nm). It is under 2 mV here.

| Film | dEc V1 → V2 (eV) | Curve shift from the laws |
|---|---|---|
| 2.0 nm | 0.3533 → 0.2768 | −0.0748 V |
| 6.3 nm | 0.0724 → 0.0493 | −0.0236 V |
| 13.2 nm | 0.0261 → 0.0162 | −0.0102 V |

### V2 calibration
It follows the V1 protocol:
- **One shared Qf**, from least squares of the active log-RMSE on the 2 and 13.2 nm anchors. It shifts every curve by +0.062 V, so **Qf_V2 = 1.38345e12 cm⁻²** (V1: 1.73e12).
- **μ_band per anchor** from the measured Ion: 17.6897 (2 nm) and 63.2597 (13.2 nm).

## 3. Pre-registered predictions and criteria

### T2: ATLAS confirmation of the V2 anchors (2 launches)
The ATLAS V2 runs must agree with the exact transformations below:
- Vth_cc within ±0.005 V;
- Ion within ±1 %;
- active RMSE within ±0.005 dec.

| Anchor | Active RMSE (dec) | Vth_cc (V) | Vth_lin (V) | SS_cc (mV/dec) | Ion (A/µm) |
|---|---|---|---|---|---|
| 2.0 nm, predicted V2 | 0.060 (V1 0.043) | 0.668 | 1.522 | 291.1 | 5.090e-7 |
| 2.0 nm, measured | — | 0.662 | 1.663 | 269.9 | 5.090e-7 |
| 13.2 nm, predicted V2 | 0.097 (V1 0.081) | 0.103 | 1.043 | 191.8 | 3.071e-6 |
| 13.2 nm, measured | — | 0.083 | 1.044 | 160.0 | 3.071e-6 |

### T3: held-out 6.3 nm prediction (1 launch)
Inputs: V2 model, nothing fitted to 6.3 nm.

Mobility:
- **P (full prediction):** the pre-registered rule μ_band = 17.6897·(t/2)^0.67526, i.e. **38.3893** at 6.3 nm.
- **E (electrostatics only):** mobility normalised to the measured Ion by an exact rescale of the same run (no extra launch).

Pass requires all of:
- |ΔVth_cc| ≤ 0.10 V;
- |ΔVth_lin| ≤ 0.10 V;
- SS_cc within ±20 %;
- active RMSE ≤ 0.15 dec;
- for P only, Ion within ±30 %.

Predicted values, from the exact transformation of run_0039:

| | Active RMSE | Vth_cc | Vth_lin | SS_cc | Ion | Predicted verdict |
|---|---|---|---|---|---|---|
| measured | — | 0.644 | 1.820 | 295.4 | 4.034e-7 | — |
| P | 1.036 | 0.271 (−0.373) | 1.206 (−0.614) | 220.1 (−25 %) | 1.337e-6 (+231 %) | **FAIL** |
| E | 0.594 | 0.398 (−0.246) | 1.206 (−0.614) | 289.5 (−2 %) | 4.034e-7 | **FAIL** |

For comparison, V1 with the shared Qf missed Vth_cc by −0.285 V. **The DFT inputs reduce the 6.3 nm miss by only ~0.04 V.**

### T4: ultrathin scenarios (rules fixed now, before the 0.75 and 0.51 nm DFT results)
Thicknesses: 0.95 nm (the DFT fit point), and the relaxed 0.75 and 0.51 nm films (same thickness definition as 0.95/1.98 nm). Everything else is V2.

| Input | Central | Bound |
|---|---|---|
| dEc, dEg, Δm* | DFT values at that thickness | dEc × 1.06–1.11 (HSE), exact rigid shift |
| Nt | 2e19·(2/t)^0.75 | Nt held at its 2 nm value; one launch at 0.51 nm |
| Nd | Nd₀ = 2.5e17 | — |
| μ_band | held at 17.6897 | power-law rule 17.6897·(t/2)^0.67526; exact rescale |
| μ₀ | μ_band·(1 − 0.287/t)² | — |

- Qf_V2, gate work function 4.70 eV and interface states as V2.
- Sweep −3 to +3 V; 0.05 V steps from −1 V. Strict acceptance up to the rigid-shift estimate of Vth_cc.
- Reported: Vth_cc, Vth_lin, SS_cc, Ion(3 V), and Ion/Ioff with the variant-D floor and the measured setup floor (≈ 4.6e-15 A/µm).
- **All T4 results are labelled SCENARIO**, because the 6.3 nm test is predicted to fail.

## 4. Registration
SHA-256 of the inputs at registration time are listed in `T0_REGISTRATION.txt` (written by `register.py`).
