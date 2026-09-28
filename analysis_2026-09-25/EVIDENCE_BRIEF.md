# Evidence brief for the 2026-09-25 thickness-mechanism analysis (read this first)

Package root: `C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1` (all paths below are relative to it).
Python with numpy/scipy/matplotlib/pyyaml: `..\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe`. Scratch work: `analysis_2026-09-25\scratch\`.
Integrity rules of this project (user + supervisor): never invent parameters, sources or runs; write NOT DETERMINED FROM AVAILABLE DATA where evidence is missing; keep "calibrated" and "validated" distinct; every simulated number must come from a real ATLAS run listed in `results/RUN_INDEX.csv`. **Specialist agents must NOT launch ATLAS** (single 32-bit licence; the main session runs every launch sequentially).

## 1. Device and data (ground truth)
- Bottom-gate TFT: TiN 50 nm / HfO2 15 nm (eps 19.57, measured) / Al2O3 2 nm (eps 9.0, assumed) / IWO (~2 % W, composition definition NOT DETERMINED) / Pd 70 nm top S/D; air above the channel (no passivation). W/L = 290/20 um, Vd = 0.7 V (from the schematic; workbook has no units).
- Cox = 8.955e-7 F/cm^2 (EOT 3.86 nm). q/Cox = 0.179 V per 1e12 cm^-2. kT = 25.85 meV (T assumed 300 K; not recorded).
- Data: ONE ID-VG curve per thickness (2.0, 6.3, 13.2, 31.8 nm), -3..+3 V, 0.05 V steps, `data/experimental_clean.csv` (A/um). NOT available: IG, IS, sweep direction/hysteresis, dwell, temperature, ID-VD, C-V, TLM, number of devices per thickness (device-to-device spread unknown), thickness-measurement method/uncertainty, measurement ambient.
- Target paper: Januar et al. 2026 Small Structures (text in `inputs/papers_text/Januar2026_SmallStruct_IWO.txt`). NOTE: the paper quotes peak mu_FE 5.1 (2 nm) and 27.4 cm^2/Vs (13.2 nm) (tables/THICKNESS_LAW_EVIDENCE.csv), whereas the workbook curves give 12.1 and 50.2 with Cox 8.955e-7, L/W 20/290 um, Vd 0.7 V; the ratio is not constant (2.4x vs 1.8x). Origin NOT DETERMINED (different devices? different extraction/normalisation?).

## 2. Measured metrics (same extractor for data and simulation: `scripts/extract_metrics.py`)
| t (nm) | Vth_cc@1e-9 A/um (V) | Vth_lin (V) | SS_min (mV/dec) | SS 1e-10..1e-8 (mV/dec) | gm_max (A/V/um) | mu_FE (cm2/Vs) | Ion@3V (A/um) | off-band median (A/um) |
|---|---|---|---|---|---|---|---|---|
| 2.0 | 0.662 | 1.663 | 84.5 | 269.9 | 3.807e-7 | 12.15 | 5.09e-7 | 4.6e-15 |
| 6.3 | 0.644 | 1.820 | 114.7 | 295.4 | 3.431e-7 | 10.95 | 4.03e-7 | 1.5e-13 |
| 13.2 | 0.083 | 1.044 | 130.8 | 160.0 | 1.572e-6 | 50.17 | 3.07e-6 | 6.6e-12 |
| 31.8 | always on (Id >= 2.6e-7 A/um at -3 V) | | | | | | 3.59e-6 | |
Observations: Vth, mu_FE and Ion are NON-monotonic or step-like between 6.3 and 13.2 nm (2 and 6.3 nm are similar; 13.2 nm is very different); mu_FE(6.3) < mu_FE(2).

## 3. Model V1 (config/iwo_material_model.yaml, generator scripts/build_iwo_decks.py; docs/PHYSICS_MODEL.md)
Classical electrons-only drift-diffusion (Fermi statistics), continuous DOS (acceptor-like exponential tail NTA/WTA, deep Gaussian), regularized interface acceptor sheet, uniform ionized background donor Nd_eff, fixed front charge Qf, constant band mobility, ideal Ohmic Pd contacts, physical structure, stepped sweep. Thickness laws (value at 2 / 6.3 / 13.2 nm):
| quantity | law | 2.0 | 6.3 | 13.2 | status |
|---|---|---|---|---|---|
| dEc = dEg (confinement) | 0.9205 t^-1.3815 eV (log-log fit through THREE PBE slab points at 0.95-1.98 nm, pure In2O3; EXTRAPOLATED beyond 2 nm) | 0.353 | 0.072 | 0.026 | DFT proxy, +/-50 % |
| m* | 0.208 + 0.1311 t^-1.412 (enters only Nc) | 0.257 | 0.218 | 0.211 | proxy |
| Nt (tail integral) | 2e19 (2/t)^0.75 cm^-3 (anchored on the 2 nm fit; exponent from a 2-point ratio ~4 between 13.2 and 2 nm in Januar 2026) | 2.0e19 | 8.5e18 | 4.9e18 | FITTED |
| Nt x t (sheet) | | 4.0e12 | 5.3e12 | 6.4e12 cm^-2 | derived |
| WTA | 0.040 eV shared | | | | FITTED |
| Nd_eff | 2.5e17 (1+(t/20)^4) | 2.50e17 | 2.52e17 | 2.97e17 | FITTED; q Nd t/Cox = 0.009 / 0.028 / 0.070 V |
| interface acceptor sheet | 3e11 cm^-2 eV^-1 at Ec-0.3 eV, W 0.12 | shared | | | ASSUMED |
| Qf (front, fixed) | 1.73e12 cm^-2 shared (= -0.31 V), 8.7e10 for 6.3 nm tuned only | | | | FITTED |
| mu_band | per film | 18.13 | 11.69 (tuned) / 12.4 (validation) | 61.9 | FITTED per thickness |
| roughness factor (1-0.287/t)^2 | Januar Dsr 2.87 A | 0.734 | 0.911 | 0.957 | literature |
| gate WF | 4.70 eV | | | | ASSUMED (degenerate with Qf, chi) |
Free parameters actually fitted to the 3 thin-film curves: Qf (1 shared + 1 device-specific at 6.3 nm), mu_band x3, Nt2, WTA, Nd law (from V0 13.2 nm shoulder), i.e. the curves are calibrated, not predicted.

## 4. Key ATLAS results (results/runs/<run>/execution.json; tables/EXPERIMENTAL_VS_SIMULATION.md; tables/SENSITIVITY_RESULTS.md)
| run | config | Vth_cc | Vth_lin | SS_min | SS_cc | gm_max | mu_FE | Ion | active RMSE (dec) |
|---|---|---|---|---|---|---|---|---|---|
| 0012 | 2 nm calibrated | 0.676 | 1.559 | 73.2 | 289.1 | 3.531e-7 | 11.27 | 5.09e-7 | 0.037 |
| 0016 | 2 nm, confinement removed (same Qf, mu) | 0.361 | 1.260 | 83.9 | 303.7 | 3.551e-7 | 11.33 | 6.18e-7 | 0.846 |
| 0014 | 6.3 nm VALIDATION (shared params, mu 12.4) | 0.350 | 1.212 | 108.2 | 284.9 | 2.860e-7 | 9.13 | 5.11e-7 | 0.678 |
| 0015 | 6.3 nm TUNED (Qf 8.7e10, mu 11.69) | 0.651 | 1.471 | 110.8 | 288.8 | 2.639e-7 | 8.42 | 4.03e-7 | 0.063 |
| 0013 | 13.2 nm calibrated | 0.053 | 0.999 | 151.3 | 192.5 | 1.534e-6 | 48.95 | 3.07e-6 | 0.081 |
| 0017 | 13.2 nm, confinement removed | 0.030 | 0.979 | 138.6 | 193.3 | 1.533e-6 | 48.92 | 3.10e-6 | 0.115 |
Facts worth testing (not conclusions):
- A Qf change is an exact rigid shift: dVth = -q dQf/Cox reproduced to 1 mV (runs 0001->0003, 0005->0007). Id is exactly linear in mu_band (+7.9 % mu -> +7.9 % Ion).
- The tuned 6.3 nm run matches Vth_cc and Ion but misses Vth_lin by -0.35 V, gm_max by -23 % and mu_FE by -23 %: the on-state SHAPE of 6.3 nm is not reproduced, so the discrepancy is not purely a rigid offset.
- Removing confinement moves SS_min TOWARD the measurement at both calibrated films (2 nm: 73 -> 84 vs 84.5 measured; 13.2 nm: 151 -> 139 vs 131). SS_min extraction robustness on the stepped grid (and its dependence on where the strict->default METHOD switch sits, which is fixed at the MEASURED Vth) has not been checked.
- Symmetry of the calibration: with confinement + one Qf, 2 and 13.2 nm fit and 6.3 nm misses by -0.29 V. Without confinement, the Qf that fits 2 nm is 4.76e10 (rigid shift from run_0016); the Qf that would fit 6.3 nm without confinement is estimated near 8.7e10 - (0.07 V x Cox/q) ~ -3e11, and 13.2 nm would need ~1.86e12. Campaign A run A6 tests the no-confinement held-out prediction for 6.3 nm directly.
- Sensitivities at 2 nm (one at a time vs run_0012): chi +/-0.1 eV -> -/+0.10 V; Nt x1.5 -> +0.08 V, Ion -25 %; WTA +5 meV -> SS +12 mV/dec; Dit x3 -> +0.025 V, SS +9; Nd x2, eps 10.55, 4 um overlap: < 2 %.
- Numerics (docs/NUMERICAL_CONVERGENCE.md): mesh x0.5 (2 nm) and x0.7 (13.2 nm) pass (< 0.005 dec); DOS levels 96/48 -> 384/192 raise Ion by +2.5 % at 2 nm (FAIL of the 1 % criterion, being fixed in campaign B); 6.3 nm mesh check open (campaign A, A7).
- Off-state floors (5e-15 / 1.5e-13 / 6.6e-12 A/um) are not produced by drift-diffusion (thermal generation bound 13-17 decades lower); origin NOT DETERMINED (no IG/IS).
- 31.8 nm: always-on; excluded by the user from the final set; V0 needed a back-surface donor sheet + series R ~9e4 ohm.um.
- Earlier packages: V0 `..\IWO_ATLAS_Model_claude` (34 runs, per-thickness fits, docs/VALIDATION_CHECKS.md) and Astra (`inputs/astra_IWO_PRIORITY_THREE_20260912/.../audit/docs/rebuild_20260912/{MEASUREMENT_CONSTRAINTS,QUANTUM_SENSITIVITY,QUANTUM_CHARGE_VERIFICATION,PRIORITY_THREE_OFF_CURRENT_AUDIT}.md`) - use for cross-checks, do not re-derive.

## 5. New ATLAS campaigns (2026-09-25; results/campaigns/<name>.json holds per-run metrics; run folders in results/runs/)
- Campaign A `config/campaign_A_6p3_hypotheses.json` (runs 0030-0036), one mechanism at a time relative to run_0014 (6.3 nm, shared Qf 1.73e12, mu 12.4, DOS 96/48): A3 back-surface fixed charge -1.64e12 cm^-2 on the exposed IWO/air channel; A1 physical thickness 5.3 nm (all laws at 5.3); A2 Nd0 1e16; A4 front Dit x5; A6 NO confinement + Qf 4.76e10 fitted on 2 nm only (held-out prediction of 6.3 nm); A5 combination (5.8 nm + Nd0 1e16 + back charge -1.0e12); A7 mesh x0.7 on the tuned configuration.
- Campaign B `config/campaign_B_recal_predictions.json` (runs 0037-0051): B0 = pre-registered test of specialist S2's trap/mobility re-partition at 6.3 nm (Nt 2.66e19, mu_band 19.6, Qf 9.8e11, DOS 96/48); DOS 384/192 recalibration of 2 / 6.3 (tuned) / 13.2 nm with mu_band rescaled exactly; PREDICTIONS: ID-VD (Vg 1, 1.5, 2, 2.5, 3 V; Vd 0-3 V) per film, transfer curves at 65 C (338.15 K, 2 nm) and 85 C (358.15 K, 2 / 6.3 / 13.2 nm) - the temperatures of the Januar SI Fig. S12 data that we do NOT possess; isolation tests gate WF +0.1 eV and m* x1.3 at 2 and 13.2 nm.
- Specialist finding already established (S5): run_0027 (overlap 4 um) is MALFORMED - x.mesh ends at 24 um, so the drain collapsed to a zero-width line; its -2.15 % Ion is not an overlap effect. Specialist reports S2 (transport/power laws) and S5 (contacts/experimental validation) are in this folder.

## 5b. Campaign status at the start of the final stage (main-session notes, verified)
- Campaign A complete (runs 0030-0036); A7 mesh x0.7 on the tuned 6.3 nm deck: 0.0625 vs 0.0626 dec, Id(3V) -0.03 % -> check L PASSES.
- Campaign B complete (runs 0037-0051), summary in results/campaigns/campaign_B_recal_predictions.json. Recalibrated mu_band at DOS 384/192 (exact rescale by Ion_meas/Ion_sim, placeholders): 17.69 (2 nm; B1 Ion error 0.00 %), 11.58 (6.3 nm; B2 run at 11.41 gave -1.48 %), 61.60 (13.2 nm; B3 run at 60.39 gave -1.97 %). So the 96/48 -> 384/192 Ion offset is thickness-dependent: +2.5 % / +1.0 % / +0.5 %. B2/B3 curves at the recalibrated mu follow by exact linearity (x1.0150 / x1.0201). ID-VD (B8-B10) and elevated-T runs (B11-B14) used the recalibrated mu values.
- SS_min is NOT a robust metric: B1 (2 nm, DOS 384/192, mu 17.69, Ion identical to run_0012 within 0.01 %) gives SS_min 83.1 vs 73.2 mV/dec in run_0012 (S3 also showed grid-phase/floor-window artefacts). Use fixed-current SS.
- B0 (S2 re-partition, run_0037): Vth_cc 0.654, Vth_lin 1.856, mu_FE 10.40, Ion -7.6 % (S2's pre-registered on-state predictions met except mu_FE marginally low) BUT SS_cc 410.9 and SS_min 141.6 vs measured 295 / 115 (S1 predicted SS_cc ~418 beforehand) -> the re-partition fixes the on-state and breaks the subthreshold.
- IMPORTANT TEMPERATURE CAVEAT (verified in run_0045 deckbuild.out lines 384-423): ATLAS applied its silicon-default constant-mobility temperature exponent tmu = 1.5, i.e. mu_band(T) = mu_band(300 K) x (T/300)^-1.5, although the plan declared a T-independent band mobility. In an isothermal simulation with a spatially uniform constant mobility the current is exactly proportional to that factor (Id linear in mu, demonstrated), so BOTH prediction variants are exact: (P-phonon) as simulated; (P-MTR, T-independent mu_band) = simulated currents x (T/300)^+1.5 = x1.1966 at 338.15 K and x1.3043 at 358.15 K. The 300 K references are B1 and B2/B3 rescaled to the recalibrated mu. Report both variants; never present the as-simulated runs as 'T-independent mobility'.
- Isolation tests (DOS 384/192, vs B1 / B3 at the same mu): gate WF +0.1 eV -> Vth_cc +0.100 V at both 2 and 13.2 nm, SS unchanged, Ion -6.8 % at both (runs 0048/0049). m* x1.3 -> Vth_cc -0.043 V (2 nm) / -0.028 V (13.2 nm), SS_cc -18 / -13 mV/dec, Ion +4.1 / +3.7 % (runs 0050/0051).
- Campaign C (config/campaign_C_6p3_nearEc_band.json, run_0052 when finished): pre-registered test of S4's near-Ec acceptor band (2e12 cm^-2 at Ec-0.03 eV, W 0.02) + mu_band 15.4 on the tuned 6.3 nm deck at DOS 384/192; baseline B2; S4 prediction vs run_0015: gap +0.28 V, gm +24 %, SS_cc +23 mV/dec. Launch budget is now exhausted (52/52).

## 6. Literature available locally (`inputs/papers_text/`)
Januar2026 (target process), Si2021 NanoLett (In2O3 0.7 nm, CNL, DFT dEc), Lin2022 ACS Nano (thin In2O3 DFT gaps/m*, Hall, Dit), Wang2022 Front Mater (traps HfO2/In2O3), Kim2024 APL (IWO thickness vs stability, bulk/border traps vs thickness), Stokey2021 JAP (In2O3 eps, m*), NatElec2022 (In2O3 scaling, contacts), Pandey2025 TED, Wang2025 TED (IGZO compact), Anusha2024 review. `references/REFERENCES_MASTER.md` lists them. Use them; do not web-search unless a specific number is indispensable and absent locally.
