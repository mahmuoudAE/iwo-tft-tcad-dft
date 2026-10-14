# Z9 - gate-leakage bounds recomputed offline (0 launches)

**Status: PENDING CODEX REVIEW** (plus manual check per the TCAD check rule). Date 2026-10-15. No ATLAS launch; no sealed output read; no tracked file modified.

## Commands
```
python -I IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-10-10_campaign/leakage_bounds.py          # unmodified, regression source
python prelaunch/z9_leakage_wrapper.py IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-10-10_campaign > prelaunch/z9_wrapper_output.txt
```
`leakage_bounds.py` (35 lines) has no parameters or functions, so `z9_leakage_wrapper.py` imports it (stdout captured) and reuses its constants, floors, gate area and FN A/B form (l.3-7, l.20-24). Full 72-row output: `z9_wrapper_output.txt`.

## Method (all CALCULATED by the wrapper unless labelled)
- Electron injection from the TiN gate at V_G = -3 V. V_ox = 3.0 V (ASSUMED, `leakage_bounds.py` l.15 "all voltage across the stack") and 3.43 V (upper end of 3.0-3.43 V, CALCULATED in PLAN_C10 l.557).
- Fields from D-continuity: HfO2 15 nm eps 19.57 (thickness fab schematic, eps MEASURED; CAMPAIGN_DESIGN l.167), Al2O3 2 nm eps 9.0 (ASSUMED, design l.168). E_HfO2 = 1.550e6 / 1.773e6 V/cm.
- Conduction-band profile with steps chi_prev - chi_next; WKB exponent S = 2*int(kappa) at the gate Fermi level, numerically over both layers; J = A(phi_inj, m_inj) E_inj^2 exp(-S) + Richardson (A* 120 A/cm^2K^2, ASSUMED) over the highest barrier. I_G = J x 24 um x 1 um (gate area ASSUMED, `leakage_bounds.py` l.24).
- Checks: wrapper reproduces the script's four FN lines (7.21e-21, 2.42e-28, 1.79e-38, 2.13e-15 vs printed 7.2e-21, 2.4e-28, 1.8e-38, 2.1e-15 A/um; COMPUTED); single-triangle limit gives S = B/E to 4 decimals (28.0801).
- Two dispersions: parabolic (as the script) and Franz two-band (kappa^2 x (1 - U/E_g)), which raises I_G. Which one QTNLSC uses was not checked in the 5.28 manual: UNVERIFIED.
- Two stack orders: registered TiN/HfO2/Al2O3/IWO, and the reverse TiN/Al2O3/HfO2/IWO (the Al2O3 position is ASSUMED, design l.168, open item H.3). The TiN/Al2O3 barrier 2.25-2.85 eV only enters the reverse order.
- Image-force lowering, temperature broadening and the direct-tunnelling prefactor are not included; the FN prefactor in the trapezoidal regime is ASSUMED good to about +/-1 dec.

## Inputs
| Set | HfO2 chi / m / E_g | Al2O3 chi / m / E_g | phi TiN->first layer | Label / source |
|---|---|---|---|---|
| a1 registered nominal | 2.5 / 0.20 / 5.8 | 1.25 / 0.35 / 8.8 | 2.2 | design l.202; chi,E_g LITERATURE (Al2O3 = sapphire values, `03` C3 NOT SUPPORTED for ALD); m ASSUMED |
| a2 registered worst | 3.2 / 0.10 / 5.8 | 1.6 / 0.30 / 8.8 | 1.5 | design l.203, ASSUMED |
| b1 / b2 ALD Al2O3 | nominal HfO2 | 1.85 / 2.45, m 0.35 (b3/b4: 0.22), E_g 6.4 | 2.2 (reverse order 2.85 / 2.25) | chi CALCULATED = 4.05 - CBO from R&W 2015 Tables 1, 3 (`03` l.51; J. Robertson, R. M. Wallace, Mater. Sci. Eng. R 88, 1-41 (2015), doi:10.1016/j.mser.2014.11.001, citation text verified in `03` l.50); TiN/Al2O3 2.25-2.85 eV CALCULATED with W 4.7 ASSUMED (PLAN l.346); m 0.35 ASSUMED; 0.22 Perevalov lower end, UNVERIFIED for ALD (PLAN l.558) |
| c1-c3 Monaghan HfO2 | 2.0 / 0.11 / 5.8 | registered, 1.85, 2.45 | 2.7 | LITERATURE: S. Monaghan, P. K. Hurley, K. Cherkaoui, M. A. Negara, A. Schenk, Solid-State Electron. 53, 438-444 (2009), doi:10.1016/j.sse.2008.09.018 (`03` l.50, l.54; abstract only); phi = 4.7 - 2.0 CALCULATED |

Floors 4.61e-15 / 1.53e-13 / 6.60e-12 A/um: MEASURED/DERIVED (CAMPAIGN_DESIGN l.344; `leakage_bounds.py` l.4). Margin = log10(floor / I_G), CALCULATED.

## Results (I_G in A/um, CALCULATED; margins in dec for 2.0 / 6.3 / 13.2 nm)
I_G does not depend on the film (same oxide); only the floor does, so 2.0 nm is always the binding margin.

Registered order TiN/HfO2/Al2O3/IWO:
| Set | V_ox 3.0, parabolic | V_ox 3.43, parabolic | V_ox 3.0, Franz | V_ox 3.43, Franz |
|---|---|---|---|---|
| a1 nominal | 5.6e-33; 17.9/19.4/21.1 | 6.5e-28; 12.9/14.4/16.0 | 2.5e-29; 14.3/15.8/17.4 | 8.0e-25; 9.8/11.3/12.9 |
| a2 worst | 3.4e-14; -0.9/0.7/2.3 | 8.6e-11; -4.3/-2.7/-1.1 | 3.3e-13; -1.9/-0.3/1.3 | 5.6e-10; -5.1/-3.6/-1.9 |
| b1 ALD 1.85 | 2.6e-30; 15.3/16.8/18.4 | 4.2e-25; 10.0/11.6/13.2 | 7.8e-27; 11.8/13.3/14.9 | 4.2e-22; 7.0/8.6/10.2 |
| b2 ALD 2.45 (no Al2O3 barrier; mass-independent, = b4) | 2.4e-28; 13.3/14.8/16.4 | 1.0e-24; 9.7/11.2/12.8 | 6.6e-25; 9.8/11.4/13.0 | 1.0e-21; 6.7/8.2/9.8 |
| b3 ALD 1.85, m_Al 0.22 | 6.6e-30; 14.8/16.4/18.0 | 5.0e-25; 10.0/11.5/13.1 | 1.9e-26; 11.4/12.9/14.5 | 5.1e-22; 7.0/8.5/10.1 |
| c1 Monaghan + reg. Al2O3 | 1.4e-31; 16.5/18.0/19.7 | 6.7e-28; 12.8/14.4/16.0 | 4.7e-27; 12.0/13.5/15.2 | 5.1e-24; 9.0/10.5/12.1 |
| c2 Monaghan + ALD 1.85 | 6.3e-29; 13.9/15.4/17.0 | 4.3e-25; 10.0/11.6/13.2 | 1.4e-24; 9.5/11.0/12.7 | 2.7e-21; 6.2/7.8/9.4 |
| c3 Monaghan + ALD 2.45 | 6.0e-27; 11.9/13.4/15.0 | 1.0e-24; 9.6/11.2/12.8 | 1.2e-22; 7.6/9.1/10.7 | 6.4e-21; 5.9/7.4/9.0 |

Reverse order TiN/Al2O3/HfO2/IWO (H.3 alternative), 2.0 nm margin only, parabolic V 3.0 -> Franz V 3.43: a1 10.5 -> 4.2; b1 9.5 -> 3.2; b2 8.3 -> 2.6; b3 7.6 -> 1.6; b4 6.6 -> 1.2; c1 12.7 -> 5.7; c2 11.7 -> 4.7; c3 10.5 -> 4.1 dec (full rows in the output file).

## Verdict on the ">= 9-decade nominal margin" (CALCULATED, conditional on the ASSUMED items above)
- **Survives** for the registered order with parabolic dispersion: minimum 11.9 dec (c3) at V_ox 3.0 V and 9.6 dec (c3; b2 9.7) at 3.43 V, at 2.0 nm. 6.3 and 13.2 nm: >= 11.2 dec.
- **Does not survive** with Franz dispersion at V_ox 3.43 V: 5.9 dec (c3), 6.7 (b2), 7.0 (b1) at 2.0 nm; 13.2 nm stays >= 9.0. At V_ox 3.0 V with Franz: c3 7.6, c2 9.5, b2 9.8.
- **Does not survive** for the reverse stack order with the ALD Al2O3 pair (b2 8.3 dec even parabolic at 3.0 V; down to 1.2 dec).
- Design §7.3 "I_G(-3 V) <= 1e-24 A/um": holds for a1 in all four columns (max 8.0e-25); for b2/c3 it is reached (1.0e-24) at 3.43 V parabolic and exceeded under Franz.
- Registered worst set: 3.4e-14 to 5.6e-10 A/um, at or above the 2.0 nm floor, consistent with design l.384 at 3.0 V; at 3.43 V it exceeds that expectation's 1e-11 upper end.
- Recommended wording until Codex review: "at least 9 decades for the registered stack order and parabolic WKB; 6-10 decades (2.0 nm) across the ALD Al2O3 and Monaghan pairs when a two-band dispersion and V_ox 3.43 V are allowed; not robust to the Al2O3 position (H.3)."

## Open for Codex
1. QTNLSC dispersion (parabolic vs two-band) from the 5.28 manual (UNVERIFIED here).
2. FN prefactor in the trapezoidal regime (+/-1 dec ASSUMED).
3. Whether channel-side injection at positive V_G (IWO/ALD-Al2O3 barrier 1.57-2.17 eV, PLAN l.346) needs a separate bound; not computed here.
