# Hypothesis register: IWO TFT TCAD + DFT, revision 2

**Status: FROZEN, 2026-10-10T18:33:13Z** (user approval, decision log D-17; git tag `register-rev2-frozen-20261010T1833Z`). From now on, every change is a logged amendment, and the frozen predictions stay scored.
- Revision 1 is kept unchanged in `HYPOTHESIS_REGISTER_rev1.md`. Every change from revision 1 is listed in section 5 as an amendment (A1 to A16; A17 to A31 and A34 to A44 added after the freeze; A32 and A33 are reserved for the pending warm-start and MACE-seed pilots).
- **Review history:**
  - Codex ultra review (FIX_FIRST), answered by A1 to A12 and A14;
  - NC audit, applied as A13;
  - Codex re-check (FIX_FIRST), answered by A16;
  - Codex confirmation (FREEZE_OK_WITH_EDITS), edits applied.
- A15 (the CERN SCF rescue) was approved on 2026-10-11 as a pilot on aIO_0p8_s1 (D-16). Its pass/fail criteria were registered in `CODEX_WORK_CHAT.md` before submission.

## 0. Rules, disclosures, budget
- **Registered prediction:** a frozen pass/fail test.
- **Forecast:** a drafter's estimate. It is recorded but is not the test.
- **Thresholds:** every threshold is an ASSUMED decision threshold. A looser registered bound with a tighter forecast is used only where its physical or numerical justification is stated.
- **Censoring rule:**
  - A quantity below the demonstrated numerical resolution is reported as *below resolution*.
  - It counts as consistent with an upper-bound prediction only if that resolution is below the bound.
  - Otherwise it is *unresolved*, never a pass.
  - Current balance (KCL) is a sanity check, not an uncertainty estimate.
- **Results seen before revision 2:**
  - S0-01 and S0-02 (run_0061, run_0067).
  - All of S1 (run_0068 to run_0074).

  | Run | What it tested | Result |
  |---|---|---|
  | S1-01 | 6.3 nm baseline | 1.18 dec; I_D(3 V) ×4.87 |
  | S1-02 | 13.2 nm baseline | 0.056 dec |
  | S1-03 | 13.2 nm, finer mesh | Passed the numerics rule (Δ = −0.0005 dec) |
  | S1-04 | DOS grid | Passed the numerics rule (Δ = −0.00002 dec) |
  | S1-05 | 3-D NC300 instead of quasi-2D | ΔV_th,cc = +142 mV, outside the registered +40 to +70 mV: **FAIL**. ΔSS +49 mV/dec. Active RMSE 0.367 → 0.053 dec |
  | S1-06 | 13.2 nm, two carriers | Timed out: unresolved |
  | S1-07 | Native check of the offline profiling | Passed. Maximum deviation 2.05e-4 dec over both J windows (1.44e-4 on-state). This validates the tested Q_f/MUN transformation only, not profiling in general |

  - **Blind to:** S2 to S7, and every amorphous-DFT electronic target quantity (edges, projections, localisation, EA, gaps).
  - **Seen (A16):** the SCF-convergence failures of aIO_0p8_s1 and aIO_2p0_s1, which give convergence behaviour, one first-SCF energy and one force norm only.
  - **Retrospective:** every comparison with the device data. There is one device per thickness.
- **Budget:** 14 C10 launches used (run_0061 to run_0074), 186 remaining.
- **Protocol deviation, disclosed:** S0-02 needed 6 launches, against the cap of 3 repairs in CAMPAIGN_DESIGN.md:294.
- **DFT resolution limit:** one state per DFT cell is about 6e13 cm^-2. The fitted Q_f (about 0.023 e per cell) and N_s (about 0.07 states per cell) cannot be tested by DFT.
- **Floor reference:** the measured 2.0 nm floor is 4.6e-15 A/um.

## 1. Definitions (frozen with the register)
- **Host edge.** The lowest conduction state of the interior host network. It is not necessarily the LUMO: the LUMO may be a surface, interface or W state. Each test says which one it uses.
- **Projections (A16).**
  - For each state (n, k), the atom weight p_i is the Löwdin projection (`projwfc.x`) summed over all orbitals of atom i. It is then normalised so that Σ_i p_i = 1.
  - **Completeness:** the unnormalised sum (1 − spilling) is reported per state.
  - A state with completeness < 0.90 is flagged. A test that rests on flagged states is *unresolved*.
  - Atom and orbital maps are exported with the projections (A14).
- **Localisation.**
  - Normalised participation ratio: PR_n = 1 / (N · Σ_i p_i²).
    - **Atom domain (A16):** all N atoms of the cell, including H and, in interface cells, the oxide atoms.
    - A film-only PR_n is also reported, but it is not the test.
  - Extended: PR_n ≥ 0.20. Localised: PR_n ≤ 0.05. Anything between is intermediate.
  - This is an absolute rule. It replaces the relative-IPR rule of revision 1, which could call a fully localised spectrum extended.
- **Occupations and k-weights (A16).**
  - Each state contributes f_nk · w_k, where:
    - w_k is the normalised k-weight, including the spin factor 2;
    - f_nk is computed with the final SCF's own smearing function (Gaussian formulas for a Gaussian run, never the MV formulas).
- **Host edge, operational rule (A16).** The host edge is the lowest eigenvalue over all k of any state that is:
  - above band index N_v (defined below);
  - PR_n ≥ 0.20;
  - interior-weighted, with an interior weight of at least 0.8 × the interior atom fraction.

  The rule does not use the W-5d weight, so H-G's W-weight tests are not circular. The host edge is *unresolved* when:
  - no state qualifies within 1.0 eV above the lowest state above N_v; or
  - the interior region contains no atoms. Otherwise the threshold would be zero and would admit surface states automatically.
- **Regions** (geometric, from the relaxed structure):
  - **surface:** atoms within 3.0 A of the outermost non-H atom of each face, plus H;
  - **interface:** atoms within 3.0 A of the film/oxide boundary plane (QC `interface_z_A`);
  - **interior:** the film atoms not in either.
- **Projected-electron accounting (A16).**
  - **Band split:** N_v = (N_el − N_ex)/2, where N_ex is the nominal excess-electron count. N_ex = n_W in every W-doped cell (OH-terminated, bare and Al2O3-interface), and 0 in the compensated and undoped cells. The check below verifies this electron count. Bands with index ≤ N_v form the **electron-accounting partition** (not a physical valence manifold).
  - **Excess electrons:** all occupation in bands above N_v, at any energy. This includes localised states below the host edge.
  - **Check:** their sum must equal N_ex within 0.02 e. Otherwise the accounting is *unresolved*.
  - **Fractions:** every fraction uses the **nominal denominator N_ex**. Trapped electrons stay in the denominator.
  - **Reported:** the W-5d, surface, interface and interior weights.
  - **Gap-state searches:**
    - Searches for occupied gap states (H-G compensated cell, H-H, H-I) include **all bands**, including those below N_v.
    - They use a separately defined **host valence edge**: the highest eigenvalue over all k of any state with PR_n ≥ 0.20 and an interior weight of at least 0.8 × the interior atom fraction, at or below band N_v.
    - Without that reference, the gap test is *unresolved*.
  - **When N_ex = 0,** excess-electron fractions are N/A.
- **Valid interior alignment.**
  - A planar-averaged potential plateau over the interior region, with a standard deviation of 0.05 eV or less.
  - Without such a plateau (thin films), the alignment is *unresolved*: no edge shift is claimed.
- **Mobility.**
  - *Band mobility* is mu_inf · (m_bulk / m(t)) / (1 + ℓ/t).
  - The ATLAS MUN also includes the existing roughness factor.
  - Mass-ratio statements refer to band mobility only.
- **W-5d weight:** the Löwdin projection.
- **Sample spread:** as defined in ML_VALIDATION.md:36.
- **Convergence:** the host edge stable within 0.05 eV; resolved leakage within 0.1 dec under mesh refinement.
- **NC convention (A13):** every fitted trap density, Q_f or Gaussian depth names its NC convention (quasi-2D NC300 = 1.373e19 or 3-D = 3.21785e18 cm^-3 at 2.0 nm). Values from different conventions are not compared directly.

## 2. Hypotheses

| ID | Hypothesis (short) | Codex | Claude | Priority |
|---|---|---|---|---|
| H-A | The 2.0 nm floor is extrinsic or instrument-limited | H01 | H2, part | 1 |
| H-B | One shared ungated strip explains the floor scaling | H02 | H2 | 1 |
| H-C | Gate leakage and generation do not set the floor | H03 | H1 | 1 |
| H-D | Band mobility needs 1/t scattering, not only the mass | H04 | H3 | 1 |
| H-E | Confinement explains part of V_th(t) (amended after the NC audit) | H05 | H4 | 1 |
| H-F | The 6.3 nm shape residual is unexplained | H06 | H5 | 1 |
| H-G | W is consistent with a donor into host states, with no pinning state seen | H07 | H6 | 1 |
| H-H | OH termination moves dipoles, not the interior host edge | H08 | H7a/b | 1 |
| H-I | Al2O3 changes the alignment without channel-edge traps | H09 | H7c | 2 |
| H-J | One shared model transfers across 2.0, 6.3 and 13.2 nm | H10 | H8 | 1 |
| H-K | Amorphous confinement agrees with the crystalline laws | H05, part | H7d | 2 |
| H-L | W suppresses O vacancies in crystalline In2O3 (A17, after the freeze) | — | new | 2 |
| H-M | HfO2 interface control at 2.0 nm (A18, after the freeze) | — | new | 2 |
| H-N | Extended-carrier efficacy of W against thickness, exploratory (A27, after the freeze) | — | new | 1 |

### H-A: the 2.0 nm floor is extrinsic or instrument-limited
- **Registered prediction.** Converged, independently constrained intrinsic mechanisms (H-C) stay at least 1 dec below 4.6e-15 A/um at 2.0 nm, and their numerical resolution is shown to be below that bound.
- **Falsified if** a constrained mechanism reproduces the floor's magnitude, flatness and thickness scaling.
- **Unresolved if** the instrument records stay unavailable. This is the expected outcome for the decisive part.
- **Open anomaly:** at 2.0 nm the current drops ×19 between −2 and −3 V. It is reported, not explained.
- **Cost:** 0 launches.

### H-B: the ungated strip
- **Tests.**
  - S2-14 to S2-17 and STRIP-6p3.
    - S2-14 and S2-15 (13.2 and 2.0 nm) carry Q_f.
    - S2-16 and S2-17 are the matching Q_f-off controls.
  - Then frozen S6-24 to S6-26.
  - **Calibration film, frozen now: 13.2 nm** (largest and best-resolved floor). **Q_f branch frozen: with Q_f** (the baseline model).
- **Registered predictions.**
  - I(0.7 V)/I(0.1 V) = 7.0 ± 0.5. The margin covers the numerical spread of the extraction.
  - With (W/L)_par fitted on 13.2 nm only, the predicted floors at **both** 6.3 and 2.0 nm lie within 0.5 dec of the measured ones.
- **Claude forecast:** with Q_f, G(13.2)/G(2.0) ≤ 10², so the 2.0 nm prediction over-predicts by at least 10×.
- **Falsified if** either registered prediction fails. The no-Q_f branch is reported as a sensitivity and is never selected using the held-out films.
- **Withdrawn from revision 1 (A2):** the rule "ΔV0 must then be a gate work function". Strip runs cannot separate work function, affinity and where the charge sits.
- **Decisive only by measurement:** V_D steps show ×7 for a strip and ×1.02 for diffusion. V_D steps are added to the strip decks (REG-001).
- **Cost:** 5 diagnostic launches plus 3 later frozen ones (S6-24 to S6-26), 8 in total (A16 as corrected).

### H-C: gate leakage and generation do not set the floor
- **Tests.**
  - S2-11, redefined as oxide y-mesh ×0.5: run first.
  - Nominal oxide: S2-04, S2-06.
  - Worst-case oxide: S2-08.
  - Oxide TAT with ^tat.poisson: S2-12, S2-13.
  - Generation: S2-03, plus the matched controls S2-01 and S2-02, which are now retained (A9).
- **Registered predictions.** All are subject to the censoring rule in section 0.

  | Case | Prediction |
  |---|---|
  | Nominal leakage at −3 V | ≤ 1e-2 × floor of the same film, but only if a numerical ceiling below that bound is demonstrated; otherwise *unresolved* |
  | Extreme generation | ≤ 1e-20 A/um, or *below resolution* with the resolution stated |
  | Worst-case leakage | Fails the registered flatness (slope > 2× measured + 2σ) or thickness-scaling criterion |
  | Resolved leakage under S2-11 | Changes by ≤ 0.1 dec |

- **Forecasts.**
  - Codex: nominal ≤ 1e-24 A/um. Kept as a conditional forecast.
  - Claude: nominal ≤ 1e-22 A/um; S2-08 I_G(−3 V) = 2.7e-12 within ×3, thickness-independent, slope > 0.2 dec/V.
- **Falsified if** a converged tested mechanism passes all the floor criteria of CAMPAIGN_DESIGN §7.2.
- **Not excluded:** pinholes and arbitrary trap distributions.
- **Cost:** 9 launches (A16).

### H-D: band mobility needs 1/t scattering
- **Tests.**
  - S4 profiling, with a nested ℓ = 0 comparison, then native best triples.
  - DFT dispersion and localisation on aIO and aIWO at 2.0 nm (s1 and s2) and at 1.0 nm (s1). This needs a new dispersion workflow.
- **Registered predictions** (band mobility, section 1):
  - the mass-only band-mobility ratio, 2.0 against 13.2 nm, is 0.75 to 0.95;
  - **restored (A4):** the scattering branch gives 0.20 to 0.35, with ℓ = 4 to 12 nm.
- **Forecast** (Claude): mass-only 0.835; the mass explains about 14 % of the log drop (18 % with the PBE mass); ℓ = 8 ± 3 nm.
- **Falsified if** the shared branch fails native mobility acceptance or needs film-specific scattering. The fitted ℓ is a fit, not a test.
- **Cost:** up to 6 confirmation launches; 24 to 72 node-hours.
- **A22 (2026-10-10T20:45Z, before any amorphous electronic result; user approved after the Codex audit, item 8).** The new DFT dispersion (effective-mass) workflow for the amorphous slabs is **descoped**. It was not built, and the analysis-code freeze is 12 Oct 18:00 UTC.
  - The registered mass-only prediction (band-mobility ratio 0.75–0.95) is reported as **"unresolved: not computed"**. It is not dropped from the record.
  - **Kept:**
    - the S4 profiling with the nested ℓ = 0 comparison;
    - the native best triples;
    - the scattering-branch prediction (0.20–0.35, ℓ = 4–12 nm), which then rests on the existing crystalline mass inputs. This is stated wherever it is used;
    - the normalised localisation analysis (PR_n) on the amorphous slabs.
  - In section 3 the CERN item "Additions: dispersion" no longer applies.

### H-E: confinement and the threshold (amended by A13 after the NC audit)
- **Tests.**
  - S3-01 to S3-03 against S0-01, S1-01 and S1-02. These switch **all** confinement inputs off together: affinity, E_g, mass and NC override.
  - **Added (A6):** affinity-only runs at 2.0 and 6.3 nm (AFF-2p0, AFF-6p3; 2 launches). Without them no contribution is attributed to the affinity shift alone.
- **Registered predictions.**
  - All-inputs-off: ΔV_th,cc at 2.0 nm, 6.3 nm and 13.2 nm.
    - **2.0 nm: −0.13 ± 0.03 V.** This is an S1-informed, pre-S3 registration (A13).
      - The revision-1 prediction, −0.23 ± 0.04 V, is **preserved** as the original registration.
      - Both are scored and reported. Neither replaces the other in the record.
    - **6.3 nm:** −0.062 ± 0.015 V.
    - **13.2 nm:** −0.023 ± 0.008 V.
    - **2.0 nm decomposition (NC audit):** affinity −281.6 mV, NC override removed +172 to +181 mV, mobility ×1.22 −24 to −26 mV.
  - **S3-01 − S1-05 = −0.272 ± 0.010 V (A13).**
    - This removes the measured NC-convention change, because S1-05 already carries the 3-D NC.
    - It keeps the mass-dependent NC change: NC goes from 3.218e18 to 2.380e18 cm^-3 when the mass input is switched off.
    - It is **not independent** of the 2.0 nm all-off band: both constrain the same S3-01 outcome.
  - **Affinity-only runs (A13; model-consistency checks, not physics tests):**
    - AFF-2p0 shifts V_th,cc by −281.6 ± 5 mV;
    - AFF-6p3 shifts it by −62.2 ± 5 mV;
    - the shift is rigid at every current level within ±5 mV.
    - **Scoring, frozen (A16):**
      - **Current levels:** every 0.5 dec, from max(1e-13 A/µm, 10 × the run's demonstrated resolution) up to the smaller of the two curves' maximum current divided by 1.5.
      - **Interpolation:** linear interpolation of V_G against log10 I between adjacent bias points.
      - **Range and exclusions:** only the range supported by both curves is used. There is no extrapolation. Censored, non-positive and below-resolution points are excluded.
      - **Rigid** means max |ΔV_G(I) − ΔV_th,cc| ≤ 5 mV.
      - **Unresolved** if fewer than 3 levels qualify.

    The shift is rigid only because the trap levels follow E_c in the model, which is ASSUMED.
  - In the two-film shared fit: max |ΔV_th,cc| ≤ 0.10 V with confinement.
    - The statement "≥ 0.15 V without confinement" is **demoted to a forecast (A13)**. It was derived with the old 2.0 nm band and has not been re-derived.
  - The crystalline-input uncertainty moves the 6.3 nm threshold by < 0.10 V.
- **Falsified if** a prediction misses its stated band. Revision 1's widening to "twice the band" is **removed (A5)**.
- **A13: S1-05 and the NC audit.**
  - **The registered S1-05 expectation failed and stays recorded as a failure.** It expected +40 to +70 mV and got +142.15 mV.
  - **The audit found no implementation error:**
    - only `nc300` differs between the two decks;
    - the trap occupation reproduces to about 1e-5;
    - the gate charge balances to within 0.1 mV.
  - **Where the +142 mV comes from at V_th,cc (1e-9 A/µm):**
    - +37.5 mV from the statistics shift;
    - +89.5 mV from extra charge trapped in the 40 meV acceptor tail;
    - +6.5 mV from band bending;
    - −3.1 mV from free carriers;
    - +12.1 mV from the lateral channel.

    The registration assumed a slope factor of about 1.47, but at 1e-9 A/µm it is about 3.5. The +40 to +70 mV band holds only below about 1e-11 A/µm.
  - **Quasi-2D NC compared with true 2-D statistics (2.0 nm):**
    - **+0.86 mV at V_th,cc.** This is a *local surrogate comparison at matched sheet density* (F0 carriers, Fermi–Dirac traps), not a 2-D transport calculation.
    - **I_on at 3 V overstated by about 7–8 %.** This is an *inferred* bias from the 7 % lower sheet charge, conditional on unchanged transport. It is a disclosed model limitation at 2.0 nm.
  - **NC convention:** from subthreshold transfer data, NC cannot be told apart from (Q_f, N_TA, Gaussian depth). Every fitted trap density or Q_f must state its NC convention (definitions, section 1).
  - **Unchanged:** the 6.3 and 13.2 nm all-off bands stand (audit: about −0.060 and −0.023 V).
- **Forecasts:**
  - Claude: N_D ×10 moves V_th,cc by −0.08 to −0.10 V (2.0 nm) and −0.5 to −0.95 V (13.2 nm); about 1e18 cm^-3 could mimic the DFT term.
  - NC audit:
    - the **net all-inputs-off counterfactual** share of the measured 2.0 → 13.2 nm shift falls from about 36 % to about 18 %.
      - This is not an identified physical confinement contribution;
    - the 6.3 nm NC ×1.467 sensitivity run shifts V_th,cc by −10 to −29 mV;
    - "≥ 0.15 V without confinement" in the shared fit (demoted, see A13).

### H-F: the 6.3 nm shape residual is unexplained (renamed, A7)
- **Tests.**
  - S3-10 to S3-13, with **native confirmation S3-27 required** before any branch counts (restored, A7).
  - Contacts S3-17 to S3-23 are conditional. **Trigger, frozen now:** run them only if the 6.3 nm shape RMSE stays > 0.15 dec after S3-10 to S3-13.
  - The S5 fold that leaves out 6.3 nm.
- **Registered predictions.**
  - Two-film reference: 6.3 nm needs a rigid shift of +0.28 ± 0.08 V and a current scale of 0.15 to 0.35.
  - Baseline shape RMSE > 0.15 dec.
  - IGZO.TOKYO improves 6.3 nm by ≥ 0.05 dec and moves γ toward 0.9 to 1.3, **and** gives γ ≥ 0.5 at 13.2 nm (measured 0.27). It is therefore not adopted under the rule that no film may get worse.
- **Falsified if** the baseline passes, or any natively confirmed branch passes §5.3 for all three films.

### H-G: W behaves as a donor into host states, with no pinning state seen (reworded, A10)
- **Tests.** aIWO_2p0_s1 and s2, aIO_2p0_s1 and s2, and the compensated aIWO_2p0_comp_s1.
- **Registered predictions** (definitions in section 1):
  - The lowest state with ≥ 30 % W-5d weight lies > 0.3 eV above the **host edge**.
    - Justification: 0.3 eV ≈ 12 kT at 300 K, well above the 0.01 Ry (0.136 eV) smearing.
    - Kept as a forecast: ≥ 0.5 eV above the LUMO (Claude).
  - 1 e/W cells: ≥ 80 % of the **nominal** excess electrons (denominator N_ex, A16) occupy extended host states. These are states with PR_n ≥ 0.20 at or above the host edge.
    - Electrons in states below the host edge or with PR_n < 0.20 count against the prediction.
  - Compensated cell: no occupied localised state (PR_n ≤ 0.05) with ≥ 30 % W-5d weight in the gap.
  - Claude adds: the host-edge state has ≤ 10 % W-5d weight; |E_g(comp) − E_g(a-In2O3)| ≤ max(0.15 eV, sample spread).
- **Forecasts** (Claude): ≤ 15 % of the excess electrons on W-5d; E_F 0.4 to 1.0 eV above the host edge in the 1 e/W cells.
- **Scope.**
  - Neutral, spin-unpolarised PBE cells without +U can show *consistency* with donor behaviour. They **cannot** establish full ionisation or thermodynamic charge-transition levels.
  - The smearing is audited before shallow levels are interpreted.
- **N2** (a W trap in TCAD) stays an ASSUMED sensitivity if H-G fails. It is not a fitted trap.

### H-H: OH termination
- **Tests.** aIWO_2p0_s1 and aIWO_0p7_s1, each against its bare control.
- **Registered predictions.**
  - Interior-aligned host-edge shift ≤ 0.15 eV at 2.0 nm (only if the interior alignment is valid, section 1).
  - No new occupied localised state (PR_n ≤ 0.05) with ≥ 30 % surface weight within 0.3 eV below the host edge.
- **Forecasts.** |ΔEA| ≥ 0.2 eV (Codex). The bare 0.7 nm slab has a surface state near the edge (Claude).
- At 0.7 nm the interior alignment is expected to be *unresolved*.

### H-I: the Al2O3 interface
- **Tests.** aIWO_2p0_Al2O3_s2 and aIWO_1p0_Al2O3_s2, against the vacuum ensembles.
- **Registered predictions (fixed target restored, A16):**
  - |host-edge difference| ≤ 0.2 eV at 2.0 nm;
  - no localised interface state (PR_n ≤ 0.05, interface weight ≥ 30 %) within 0.3 eV below the host edge.
- **Outcome rule, frozen:**
  - **Supported:** both predictions hold, with a valid interior alignment in both cells.
  - **Failed:** |Δ| > 0.2 eV with a valid alignment, or a qualifying interface state.
  - **Unresolved:** an invalid alignment, the projection-completeness flag, or a vacuum s1/s2 spread above 0.2 eV.
- **Seed spread:** the 2.0 nm s1/s2 spread is reported separately and is never added to the bound. Two seeds give diagnostic variability, not a confidence interval.
- **Forecasts** (Claude): ≤ 0.10 eV at 2.0 nm and ≤ 0.20 eV at 1.0 nm; no state within 0.5 eV; PBE conduction-band offset 2.0 to 3.5 eV.
- **Caveat:** different seeds confound the attribution.

### H-J: transfer of one shared model
- **Tests.** S4a and S4c, then S5, all frozen and native. **Calibration membership is frozen:** S4 uses all three thin films (2.0, 6.3, 13.2 nm); each S5 fold leaves one out.
- **Registered acceptance, unchanged.** For every film:
  - RMSE ≤ 0.15 dec;
  - V_th within ±0.10 V;
  - I_on within ±30 %;
  - SS and mu_FE within ±20 %.
  - Any failure falsifies transfer.
- **Forecasts. Revision 1 misattributed these (A8).**
  - Codex originally forecast success. It withdrew that as overconfident on 2026-10-11.
  - Claude forecasts failure:
    - best S4a √J of 0.25 to 0.65 dec;
    - S4c fails at 2 or more films;
    - leaving out 6.3 nm: −0.33 ± 0.10 V and I_on ×3 to 6;
    - leaving out 2.0 nm: ℓ at the 50 nm bound;
    - leaving out 13.2 nm: I_on ×0.15 to 0.4.
- **Reporting rule:** the two-film fit (2.0 and 13.2 nm) is reported first.

### H-K: amorphous against crystalline confinement
- **Registered predictions.**
  - E_g(0.7 nm) − E_g(2.0 nm) = 0.6 to 1.3 eV, with sample spread 0.03 to 0.20 eV.
  - The aligned host edge rises by 0.2 to 1.0 eV from 2.0 to 1.0 nm, where the alignment is valid.
- **N1, amended (A11, A13).** If the amorphous ΔE_c law differs from the crystalline law by more than 0.05 eV, run affinity-only interventions (3 launches).
  - **Registered (A13), conditional on AFF-2p0 and AFF-6p3 passing their ±5 mV rigidity check:** ΔV_th,cc = +Δ(ΔE_c) = −Δχ, at a 1:1 ratio within ±5 mV.
    - It is scored at the frozen AFF current levels (H-E).
    - This is a statement about the model, not the device.
  - **If AFF fails rigidity:** there is no rigid-shift prediction, and N1 reports the measured mapping.


### H-L: W suppresses oxygen vacancies in crystalline In2O3 (added after the freeze by A17, 2026-10-10T18:48Z, before any vacancy cell was built or submitted)
- **Question:** plan Q3, "Does W really suppress oxygen vacancies, and by how much?" This is a crystalline reference test. It does not test the amorphous film.
- **Cells and settings (frozen now):**
  - 80-atom bixbyite conventional cell, with the cell fixed at the stage-2 PBE host value a = 10.3061 A;
  - PBE, pslibrary 1.0.0 PAW, 71/568 Ry, k 3x3x3 for relaxation;
  - Gaussian smearing 0.005 Ry, spin-unpolarised, neutral cells;
  - atoms relaxed to 1e-3 Ry/bohr and 1e-4 Ry;
  - W on the 24d site (stage 4: 24d preferred by 0.258 eV);
  - **convergence check:** single-point SCF at k 4x4x4 on every relaxed geometry. If any registered difference changes by more than 10 meV between k3 and k4, the k4 value is used and the change is reported.
- **Five calculations:** In32O48 and In31WO48 (references), In32O47 (V_O in pure In2O3), and In31WO47 with V_O **near** W and **far** from W.
- **Site definitions:**
  - **near:** the O with the shortest W–O bond in the relaxed In31WO48;
  - **far:** the O with the largest minimum-image distance to W.

  Both are chosen from the relaxed host before the vacancy runs.
- **Registered predictions.** μ_O cancels in both differences.
  - **ΔE_local** = E(In31WO47, near) − E(In31WO47, far) ≥ +0.3 eV. A vacancy next to W costs more.
  - **ΔE_dop** = [E(In31WO47, far) − E(In31WO48)] − [E(In32O47) − E(In32O48)] > +0.05 eV. The degenerate W doping raises the neutral-vacancy formation energy away from W.
- **Falsified if** ΔE_local < +0.3 eV or ΔE_dop ≤ +0.05 eV, at converged geometry and k-points.
- **Unresolved if** any of the five relaxations is not converged by 17 Oct 10:00 UTC (section 3 rule).
- **Forecasts (Claude):**
  - ΔE_local +0.5 to +1.5 eV (W–O bond strength plus donor–donor repulsion);
  - ΔE_dop +0.5 to +3 eV (the V_O electrons sit at the W-raised Fermi level, about 2.8e21 cm^-3 in this cell).
- **Scope and limits:**
  - neutral charge state only; no charged states or finite-size corrections;
  - in the 80-atom cell, "far" is only about 6–8 A from W and its images, so ΔE_local is a cell-limited estimate;
  - PBE gap error;
  - the doping is far above the TFT channel density, so ΔE_dop is an upper-limit illustration of the Fermi-level effect, not a device-density value.
- **Cost:** 5 relaxations plus 5 k4 SCFs on 1 GPU each, about 1 day. Decision D-19.
- **A19 (2026-10-10T19:26Z, before any H-L job was submitted): resolving the near/far sites, and run hygiene.**
  - **Near site.** The only relaxed In31WO48 available before submission is the stage-4 one (MV 0.01 Ry, QE 7.5). Its two shortest W–O pairs differ by only 0.0105 A: O30/O69 at 1.8919 A and O72/O73 at 1.9024 A (0-based indices; 1-based 31/70 and 73/74). **Both candidates are therefore computed:** In31WO47_near (O30 removed) and In31WO47_near72 (O72 removed).
    - The registered ΔE_local uses whichever candidate is the shortest W–O bond in the **H-L-relaxed** In31WO48, determined when that relaxation converges.
    - The other candidate is reported as a sensitivity. The predictions themselves are unchanged.
  - **Far site.** The far site stays O32 (6.848 A; the next is O29 at 6.766 A, a margin of 0.08 A). If the H-L host relaxation reverses that order, the far result is reported with a flag; no extra run.
  - **Convergence.** RELAX counts as CONVERGED only if QE prints "bfgs converged". A BFGS failure continues from the lowest-energy validated geometry. The k4 SCF counts only with a converged '!' energy; a failed SCF is not replayed.
  - **Settings not frozen by H-L, fixed now for all six cells:** conv_thr 1e-8, plain mixing β 0.3, electron_maxstep 100, nstep 300, QE 7.3.1 GPU. These energies are never mixed with the stage-4 QE 7.5 energies.
  - **Cost:** one more relaxation and SCF on 1 GPU.
- **A20 (2026-10-10T20:42Z, H-L jobs submitted but no result exists; user approved "vacancy robustness" after the Codex audit).**
  - **Sensitivities (reported, not registered).** On the relaxed geometries of all six cells, k 3x3x3, 1 GPU (A100 allowed):
    - (i) a spin-polarised single point (nspin = 2, small starting magnetisation on W and its O neighbours, total magnetisation free). In31WO48 has an odd electron count (705);
    - (ii) a Gaussian degauss 0.002 Ry single point.
    - ΔE_local and ΔE_dop are recomputed with each.
  - **Robustness.** If a sensitivity shifts a registered difference by more than 50 meV, or flips its verdict, H-L is reported as **"not robust"**. The registered score is still shown.
  - **k-points.** A k3→k4 change above 10 meV in a registered difference means **"unresolved significance"**. The k4 value is reported and is not adopted automatically as converged.
  - **Site rule.**
    - The registered near cell is the *computed* candidate (O30 or O72) with the strictly shorter W–O bond in the H-L-relaxed In31WO48.
    - If the two pairs lie within 1e-3 A of each other, a TIE is flagged, both results are reported, and O30 is registered (the tie-break is declared now).
    - A symmetry partner (O69, O73) stands for its computed cell only while its pair is unsplit (within 1e-3 A).
    - If the shortest bond belongs to an uncomputed partner of a split pair, or to any other O, ΔE_local is **unresolved**; nothing is substituted. `select_near.py` was changed accordingly before any result.
  - **Limits stated.**
    - 3.125 % W (1 W per 32 cations) in an 80-atom cell.
    - ΔE_dop mixes local chemistry, strain and band filling; it is **not** an upper bound on the Fermi-level effect.
    - Neutral cells only; charge-state thermodynamics are not addressed (e.g. Chatratin et al., PRMaterials 3, 074604, 2019).
  - **Cost:** 12 single-point SCFs on 1 GPU.

### H-M: the HfO2 interface (added after the freeze by A18, 2026-10-10T18:52Z, before the Hf pseudopotential was installed or any structure was built)
- **Why:** the user kept the HfO2 extra (plan priority 5). The fab schematic reads TiN / HfO2 15 nm / Al2O3 2 nm / channel, so Al2O3 most likely touches the film. H-M is therefore a **control** for the unresolved stack order (`01_CURRENT_STATE.md` item 3): does the 2 nm Al2O3 interlayer matter for the channel edge? It becomes the primary interface only if the fab confirms that HfO2 touches the channel.
- **Cell, frozen now:** `aIWO_2p0_HfO2_s1`, ML seed 902.
  - The film is identical in composition and lateral cell to `aIWO_2p0_Al2O3_s2`: In98W2O152, L = 12.91 A, 2.0 % W.
  - It sits on about 1 nm of a-HfO2 at 9.6 g/cm3 (ASSUMED; ALD a-HfO2 is about 9.1–9.7).
  - The SLAB_PROTOCOL §5 recipe applies unchanged:
    1. melt-quench the oxide;
    2. melt and quench the film with the oxide fixed;
    3. cleave below the oxide;
    4. anneal at 800 K with all atoms free;
    5. passivate both faces with OH.
  - Pseudopotential: Hf PAW from pslibrary 1.0.0.
  - DFT settings: identical to `aIWO_2p0_Al2O3_s2` (relax MV 0.01 Ry; final SCF Gaussian, gated by the A15 audit).
  - QC rules: as in SLAB_PROTOCOL. A QC rejection gets a new seed, which is logged.
- **Registered predictions** (fixed targets, definitions as in section 1; the outcome rule is H-I's):
  - |host edge(HfO2 cell) − mean host edge(aIWO_2p0_s1, s2)| ≤ 0.2 eV, with a valid interior alignment;
  - no localised interface state (PR_n ≤ 0.05, interface weight ≥ 30 %) within 0.3 eV below the host edge.
  - The s1/s2 spread is reported separately and is never added to the bound.
- **Forecasts (Claude, not tests):**
  - |host edge(HfO2) − host edge(Al2O3_s2)| ≤ 0.15 eV;
  - the PBE conduction-band offset of film to HfO2 is 0.5–1.5 eV smaller than that of film to Al2O3.
- **Limits:**
  - one seed, so the seeds differ from the Al2O3 cell, which confounds attribution (as in H-I);
  - PBE offsets are qualitative;
  - the 15 nm HfO2 bulk is not represented.
- **Unresolved if** the relaxation is not converged by 17 Oct 10:00 UTC. Decision D-20.
- **A21 (2026-10-10T20:45Z, before any HfO2 structure exists; user approved after the Codex audit, item 7).**
  - **Scope.** H-M is an *alternative-interface* control only. It cannot establish the fab's stack order, and it cannot isolate the removal of the real 2 nm Al2O3 interlayer, because the oxide, the seed and the bonding all change together.
  - **Hf force check.** Before the DFT relaxation result is used, the MACE-MPA-0 forces on two to three snapshots of the HfO2 interface trajectory are compared with DFT single-point forces at the relax settings, using the ML_VALIDATION.md method.
    - The QC also reports the Hf coordination statistics and the Hf–O bond-length distribution.
    - If the force agreement is worse than the worst value accepted in ML_VALIDATION.md for the In/W/O cells, H-M is reported as **"ML structure not validated"** and is not scored.
- **Erratum and clarification (2026-10-10T21:35Z, before any production HfO2 structure; no rule, threshold or prediction changed; from the independent verification of the A18 build).**
  - **A21 timing.** The label "before any HfO2 structure exists" in A21, and "before any HfO2 structure" in the A21 row of the amendment table, should read: "before any *production* HfO2 structure; a non-production `--quick` smoke build (19:05–20:49Z) was in progress and was not used for any prediction".
  - **Replacement seed.** This is fixed now, before the production result, under the SLAB_PROTOCOL §7 rule "same recipe, next seed". If `aIWO_2p0_HfO2_s1` (seed 902) fails QC, its replacement is `aIWO_2p0_HfO2_s2` with seed 903. A second rejection gives s3, seed 904.

### H-N: extended-carrier efficacy of W against thickness (added after the freeze by A27, 2026-10-11T09:09Z, EXPLORATORY with frozen read-out rules, before any slab electronic result was read)

**Cells:**
- bulk: aIWO_bulk_s1 / aIO_bulk_s1;
- 2.0 nm: aIWO_2p0_s1, s2 / aIO_2p0_s1, s2;
- 1.5 nm: optional, the first item cut if capacity is short;
- 1.0 nm: aIWO_1p0_s1 / aIO_1p0_s1;
- 0.8 nm: aIWO_0p8_s2 / aIO_0p8_s1;
- 0.7 nm: aIWO_0p7_s1 / aIO_0p7_s1.

**Observables:** for every W-doped cell, from the FINAL SCF, using the section-1 definitions. Fractions use the excess-accounting partition (bands n > N_v) and the nominal denominator N_ex = n_W.
- **f_ext:** the fraction of N_ex in extended host states (PR_n ≥ 0.20, at or above the host edge), i.e. the H-G quantity.
- **f_locW:** the fraction of N_ex in states with n > N_v that are localised (PR_n ≤ 0.05) and have ≥ 30 % W-5d weight. Filled W–O bonding bands (n ≤ N_v) are never counted.
- **f_W5d:** the W-5d share of the excess electrons, n > N_v only.
- **Δ_W:** E(lowest state with ≥ 30 % W-5d among states above the section-1 host valence edge) − E(host edge).
  - **Band coverage:** the FINAL nbnd must reach at least 1.0 eV above the host edge at every k-point.
  - If no qualifying W state lies within the computed bands, Δ_W is reported as a lower bound, "> (top computed band − host edge)". It counts as > 0.3 eV only if that bound exceeds 0.3 eV.
  - If the coverage rule fails, Δ_W is UNRESOLVED.
- **Also reported:** E_F − host edge, and N_eff = N · PR_n for every state used. PR_n scales with 1/N for unchanged localised support.

**Pairing with aIO:** the aIO partner at the same thickness supplies the undoped host edge, its tail states at the same energies, and ΔE_host(t) where the interior alignment is valid. The aIO partner is not part of the basic classification. H-G's historical scoring at 2.0 nm is unchanged and reported separately.

**Per-cell classes (assumed operational screens, not universal donor criteria):**
- **DONOR:** f_ext ≥ 0.80, Δ_W > 0.3 eV, and f_locW < 0.10.
- **ECB (extended-carrier efficacy breakdown):** f_ext < 0.50, or f_locW ≥ 0.50.
  - A low f_ext can also mean that an ionised donor's electron sits in a host or surface trap. ECB therefore does not by itself mean that W stopped donating.
- **PARTIAL:** anything else.
- **UNRESOLVED:** any section-1 unresolved condition, a failed band-coverage rule, or a smearing qualification still pending (A26).

**W-centred attribution of an ECB** needs both of the following, checked against the C1 paired parent:
- (i) the trapping states (n > N_v, PR_n ≤ 0.05) carry ≥ 30 % of their weight on W plus its first-shell O;
- (ii) the paired aIO parent has no localised state (PR_n ≤ 0.05) within ±0.10 eV carrying ≥ 30 % weight on the same non-W atoms.

Otherwise the ECB is reported as **host-trap-mediated** or **unattributed**.

**Outcome rules (frozen):**
- **Endpoints:**
  - The thick endpoint is 2.0 nm. **Both** 2.0 nm seeds must be DONOR; if they disagree, the result is **sample-dependent** and no crossover is claimed.
  - The thin decisive endpoint is fixed now at **0.7 nm**. 1.0 nm is the intermediate control point.
- **CROSSOVER:** bulk and both 2.0 nm cells are DONOR, 0.7 nm is ECB, and the required controls pass at both endpoints (see the control table).
  - The report gives a crossover **bracket**: from the thinnest DONOR thickness to the thickest ECB thickness.
  - A non-monotonic sequence is flagged as a **reversal**, and no single crossover thickness is given.
- **NO CROSSOVER:** DONOR at bulk, 2.0, 1.0, 0.8 and 0.7 nm, all resolved, with the required controls passing at 0.7 nm. Missing coverage at any of these thicknesses means NO CROSSOVER cannot be claimed.
- **Otherwise:** the trend is reported as PARTIAL, sample-dependent or UNRESOLVED, without a crossover claim.

**Scope:**
- H-G's scope applies. These cells can show consistency with extended-carrier efficacy or its breakdown in the specified networks. They cannot establish charge-transition levels.
- Fixed-geometry hybrid results support **electronic** robustness only. Equilibrium self-trapping would need a structural qualification, which is not claimed.
- Unless independent parent quenches are added at the contrast thicknesses, C1 results are restricted to the computed parent networks.

**Forecast (Claude, not scored: H-N is exploratory, D-28):** DONOR at bulk, 2.0 and 1.0 nm; PARTIAL at 0.7 nm.

#### Controls

| Control | Thick endpoint (2.0 nm) | Thin endpoint (0.7 nm) | 1.0 nm |
|---|---|---|---|
| C3 widths | required | required | reported |
| C4 Gaussian polish | required | required | required (geometry exists now) |
| C6 spin | required | required | reported |
| C1 paired substitution | not run (cost); scope stated | required | not run (D-28: 0.7 nm only) |
| C2 directional dilution | not run | required for a crossover | — |
| C5 hybrid | not run; scope stated | required for a crossover | — |

**C1. Paired substitution, testing "W substitution plus O incorporation" (not W alone).**
- **Parent:** the relaxed aIO_t.
- **Sites:** three paired cells, on interior In sites (section-1 regions) with CN ≥ 5, drawn in a seeded random order (seed 2711).
- **Construction:**
  - one W replaces one In, and one O is added in the W first shell, giving In49W1O76 against In50O75 and N_ex = 1;
  - **O placement:**
    - **Grid:** the 500 Fibonacci points on a 1.95 Å sphere around W, in a fixed orientation (pole along c).
    - **Constraints (minimum-image distances):** ≥ 2.4 Å to every O, ≥ 2.8 Å to every cation except the substituted W, and ≥ 2.0 Å to every H.
    - **Selection:** maximise the minimum distance to all other atoms. Ties go to the lowest grid index.
    - **Placement failure:** if no point satisfies the constraints, the next site in the draw order is used and the skip is recorded.
  - **Fewer than three eligible sites:** C1 is UNRESOLVED.
- **MACE pre-relax:** MACE-MPA-0 to fmax 0.05 eV/Å, keeping stoichiometry and the SLAB_PROTOCOL QC.
- **DFT:**
  - a relax with the parent's settings (Gaussian 0.005 Ry, A15);
  - a FINAL as A26/A15.
- **Requirement:** the class at t must agree between the independent-quench aIWO_t and at least 2 of the 3 paired cells.
- **Cost:** about 45–75 GPU-hours per thickness, plus three FINALs.

**C2. Directional dilution sensitivity.**
- **Cell:** a 2 × 1 lateral supercell of a **C1 paired cell**, where the added O is known.
- **Halving W:** in one image, W is replaced by In and the traceable added O is removed. This halves x_W along one axis only; the image spacing along the other axis is unchanged, and donor density and screening change.
- **Relaxation:** a DFT relaxation, unless the unrelaxed full-cell DFT forces already meet the production thresholds. Split labels are allowed under A25.
- **Robust if:** |Δf_ext| ≤ 0.15, |ΔΔ_W| ≤ 0.15 eV, the class is unchanged, and N_eff is compared rather than PR_n.
- **Limit:** C2 cannot certify complete image isolation.

**C3. Occupation width.**
- **Comparison:** the Gaussian 0.001 Ry reference FINAL (A26) against the width selected by the A15 audit, or 0.002 and 0.005 Ry if the audit is pending.
- **Pass:** the class is unchanged, edges move ≤ 0.05 eV, and fractions move ≤ 5 percentage points.
- **Rule:** comparing a result with itself is not a pass.

**C4. Relaxation-smearing family.**
- **Screen:** MV 0.01 against Gaussian 0.005 single-point forces on the relaxed aIWO_1p0_s1 now. This is the A15 force check, promoted.
- **Required regardless of the screen:** at each endpoint and at 1.0 nm, the aIWO cell is polished by a Gaussian 0.005 relax, starting from its MV geometry.
- **Rule:** classes are reported for both geometries, and a crossover must hold on the Gaussian-polished geometries.

**C6. Spin (compulsory where marked).**
- **Calculation:** nspin = 2 single points from two starts: localised (moment on W plus first shell) and delocalised (a small uniform moment).
- **Accounting:** spin-correct, with the spin factor in w_k.
- **Pass:** the class and the C3 tolerances hold for the lower-energy state.

**C5. Hybrid functional.**
- **Chain:** PAW-PBE → NC-PBE → HSE06, all at identical geometry and occupation width.
- **PAW against NC-PBE:** they must agree within the C3 tolerances first.
- **HSE settings:** SG15 NC 80 Ry, ecutfock 160 Ry.
- **Meshes:** frozen now. The k-mesh is that of the production FINAL, and q equals the k-mesh. Γ with q = 1 is allowed only if NC-PBE at Γ agrees with NC-PBE at the production mesh within the C3 tolerances.
- **Reader:** `nc_readout.py` must be extended for spin and H-N accounting before any result. Today it rejects spin input and lacks H-N accounting.
- **Requirement:** the class must agree between NC-PBE and HSE06; otherwise the result is **functional-sensitive** and no crossover is claimed.
- **Cost:** not yet known. The hybrid workflow runs on CPU (QE 7.5), so the H100 estimate in v1 is invalid. One benchmark on a 150-atom slab must come first.

#### Budget, cuts and deadline
**Cut first:**
- 1.5 nm;
- any duplicate thin-control bundle;
- C1 at 1.0 nm: not run (D-28).

**Order:**
1. Existing-series FINALs.
2. C4 polish and C6 spin at the endpoints.
3. C1 at 0.7 nm, once aIO_0p7_s1 has converged.
4. C2 and C5, only if 0.7 nm is ECB or PARTIAL.

**Deadlines:**
- Relaxations stay under the 17 Oct 10:00 UTC cutoff.
- Single-point controls must finish by 20 Oct 12:00 UTC; anything unfinished leaves its claim UNRESOLVED.
- The capacity estimate (about 0.8 of our GPU starts per hour) is an observation, not a guaranteed capacity.

#### Not changed
- H-G and its scoring.
- The section-1 definitions.
- A15, A25 and A26.

### A23: gap anchoring and hybrid-functional checks (added after the freeze, 2026-10-10T21:06Z, before any of these calculations was built)
- **Scheme (as in the TCAD model):** E_g(t) = E_g,anchor + r · ΔE_g^PBE(t).
  - **E_g,anchor** is a *measured* gap. Currently it is 3.05 eV (LITERATURE_IWO, Fan 2021, a different sputtered IWO device). A measured gap of the user's own films replaces it if one becomes available, and that is logged.
  - **ΔE_g^PBE(t)** = host-edge gap of the slab minus the host-edge gap of the **matching amorphous bulk** (a-In2O3 for the aIO slabs, a-IWO for the aIWO slabs). The edges follow section 1 (PR_n, interior weight); the KS HOMO–LUMO gap is not used because tail states distort it.
  - **r** is the HSE/PBE change ratio. The crystalline value is 1.06–1.11 (RESULTS_LOG, 2026-10-01), and its spread is carried as an uncertainty.
  - **Why not HSE06 as the absolute anchor:** HSE06 underestimates the In2O3 gap (2.11 eV crystalline against about 3.05 eV measured for IWO).
- **(i) Amorphous bulk PBE references.**
  - **Cells:** aIO_bulk_s1 and aIWO_bulk_s1, 125 atoms each, ML-built, QC PASS.
  - **Relaxation:** atoms only, fixed cell. PAW 60/480 Ry, k 2x2x2, **Gaussian 0.005 Ry for both** (stated as a difference from the MV relaxation of the aIWO slabs). Repaired continuation (exit 0/1/2, UNLESS-EXIT 2).
  - **Final SCF:** 71/568 Ry with projections, through the same A15 gate and A14/D-24 export as the slabs.
  - **Unresolved** if not converged by 17 Oct 10:00 UTC.
- **(ii) W-cell hybrid check (sensitivity for H-G; not a registered test of H-G).**
  - **Cell:** crystalline In31WO48 at the H-L-relaxed geometry (PAW-PBE, Gaussian 0.005; `bfgs converged` required).
  - **Method:** SG15 norm-conserving pseudopotentials at 80 Ry, the same setup as the 2026-10-01 HSE check. One HSE06 single point (q = 1, ecutfock 160 Ry) and one NC-PBE single point at identical settings: k 2x2x2, Gaussian 0.005, spin-unpolarised.
  - **Read-out:** the energy of the lowest state with ≥ 30 % W-5d weight, relative to the host conduction edge (section-1 rule; for a bulk cell the interior means all atoms), in PBE and in HSE.
  - **Rule:**
    - If that state stays above the host edge in both functionals, the PBE W-donor reading is called **functional-robust**.
    - If HSE moves it more than 0.1 eV below the host edge, H-G is reported with a **"functional-sensitive"** caveat.
    - The H-G registered scores are not changed in either case.
- **(iii) Amorphous-bulk hybrid check.**
  - **Cell:** aIO_bulk_s1 at its PBE-relaxed geometry from (i). Same NC setup (HSE06 q = 1, ecutfock 160) plus NC-PBE; k-point choice stated with the input.
  - **Read-out:** the amorphous offset Δ_a = E_g^HSE − E_g^PBE (host-edge gaps), compared with the crystalline Δ_c = 2.108 − 0.920 = 1.188 eV.
  - **Rule:**
    - If |Δ_a − Δ_c| ≤ 0.10 eV, the crystalline-based correction is used for the amorphous films.
    - Otherwise the amorphous offset is reported and used, with its uncertainty.
    - This checks the **offset**, not the thickness ratio r; an amorphous slab hybrid is out of scope because of cost.
- **Cost (measured basis: the 96-atom slab HSE took 4.0 h on 1 H100):** about 2–4 h for (ii) and 3–9 h for (iii) on 1 GPU; (i) is 2 relaxations plus 2 finals. Decision D-25.

### A24: outer-face material in interface cells, and HfO2 crystallinity flags (added after the freeze, 2026-10-11T03:13Z, before any interface-cell DFT result exists; user decision D-26)
- **Finding (SLAB_PROTOCOL §9).** In the periodic film melt the film top touches the bottom of the oxide, so film cations and film-origin O end up on the *outer* oxide face. Both Al2O3 cells and the HfO2 test builds show it; in the HfO2 smoke build it also produced a peroxide O–O (1.45 Å).
- **Decision (b): the recipe is unchanged.** H-M stays built exactly like the Al2O3 cells it is compared with.
- **Interface definitions, fixed now for every interface cell (Al2O3 and HfO2), using `iface_partition()`:**
  - the *outer face* is z < z(lowest substrate cation) + 3 Å (`OUTER_FACE_A`);
  - the "interface weight" in H-I and H-M (the ≥ 30 % criterion) counts only atoms outside the outer face; outer-face atoms count in neither the interface nor the film interior;
  - z_if is computed from the substrate-cation p95 and the p5 of film cations *not* on the outer face (the old p5 included them);
  - outer-face film cations per nm² are reported for every interface cell; a state with ≥ 30 % weight on the outer face is reported as an outer-face state, not an interface state.
- **Crystallinity flags for the HfO2 oxide (approved; reported only; fixed before the production QC is read):**
  - no-diffusion flag: Hf MSD over the 4 ps hold < 1.0 Å²;
  - ordering flag: more than 20 % of oxide-interior Hf have a local Steinhardt q6 (Hf neighbours ≤ 4.2 Å) closer to the ideal monoclinic HfO2 value than to the mean of the smoke-test amorphous oxide (both references computed before the production structure is read);
  - if a flag is raised, a further amendment (e.g. a 4000 K oxide melt) comes before H-M is used; no threshold changes after the result.

### A25: aIO_2p0_s1 on one GPU with split species labels (added after the freeze, 2026-10-11T08:14Z, before any result of these calculations exists; user go 2026-10-11 after Codex GO-WITH-CHANGES (work chat); decision D-27)
- **Scope.** aIO_2p0_s1 only (In100O156H12, 268 atoms). For this cell, and only while 2-GPU slots cannot match, A25 supersedes the A15 line "aIO_2p0_s1 runs on 2 GPUs with `QE_NK=1`".
  - On 2026-10-11, 2-GPU jobs matched 0 slots. On 1 GPU the s1 SCF converged (Gaussian 0.005 Ry, 134 iterations), but the first force step ran out of GPU memory in `addusforce_g`, 16.6 MB short.
  - The A15 rescue physics is unchanged: Gaussian 0.005 Ry, β = 0.1, local-TF, mixing_ndim 12, at most 300 iterations, SCF tolerance unchanged. The 2-GPU A15 route stays valid if a slot appears.
- **Route.** 1 H100 NVL, non-MIG. Species labels are split: In → In1/In2, O → O1/O2, H unchanged.
  - Identical to the unsplit input: the UPF files (checksums recorded), masses, cutoffs, smearing, nbnd, atom order, cell, symmetry, k-mesh and k-weights, FFT grid, and every other species-dependent setting (none is set per species: nspin 1, no Hubbard, no starting magnetisation).
  - Only the label names and the per-species summation order change.
  - A reversible atom-to-element map and a label-blind position hash are logged with the input.
  - `NV_ACC_MEM_MANAGE=0` is not used for this cell, so the run tests the split alone.
- **Equivalence gate.** The first converged SCF of the split run must give E0 within 1e-5 Ry of −47594.50669747 Ry (the unsplit s1 SCF at the same geometry and settings). Otherwise the run is stopped and its output is not used. The iteration-1 energy (unsplit: −47604.97202492 Ry) is logged as a diagnostic only, not a veto.
- **Force qualification.** Split against unsplit SCF + forces at identical geometry and settings, on the best-validated geometry of aIO_1p0_s1 (aIO, same species, A15 Gaussian settings, fits on 1 GPU).
  - Pass: max |ΔF| over all force components ≤ 1e-5 Ry/bohr, and |ΔE| ≤ 1e-5 Ry.
  - It is completed before any rollout of the split to other cells.
  - If it fails, the split is used for no other cell, and the aIO_2p0_s1 geometry is flagged "split not force-qualified"; its use in a registered test then needs a further amendment, logged before its FINAL SCF result is read.
- **FINAL SCF.** A fresh SCF with the original labels (In, O, H): ntyp, the species cards and the projection bookkeeping are restored through the atom-to-element map. A25 changes no FINAL setting.
- **Memory.** The force-step peak of about 75 GB on one H100 NVL is an assumption (memory model, error ±5–10 GB), not a measurement.
- **Fallback if the force step still runs out of memory: park the cell.** The 2-GPU A15 route remains if a slot appears; otherwise the section 3 deadline rule applies (17 Oct 10:00 UTC).
  - A reduced-nbnd RELAX would first need its own amendment, with: the highest retained band above E_F + 1 eV at every k-point; negligible occupation of the upper bands; the registered band count restored for the FINAL.
- **Not part of A25:** moving any other 2 nm cell (or 12884198) to one GPU, and any nbnd change. A successful force step here does not show that the cells whose SCF ran out of memory will fit; each would need its own amendment and approval.

### A26: early Gaussian 0.001 Ry reference FINALs (added after the freeze, 2026-10-11T08:14Z, before any result of these calculations exists; user go 2026-10-11 after Codex GO-WITH-CHANGES (work chat); decision D-27)
- **Rule (Codex's wording, adopted verbatim):** "Permit Gaussian 0.001 Ry reference FINALs before the representative 2 nm audit. Retain the audit, tolerances, selection and unresolved rules. Self-comparison does not count as an audit pass. Classifications remain conditional; primary comparisons require a common width or explicit sensitivity qualification."
- **What A26 does not claim.** It does not claim that a 0.001 Ry FINAL is valid whatever width the audit selects: agreement on the 2.0 nm cells does not prove agreement at 1 nm.
  - The A15 audit (0.005 → 0.002 → 0.001 Ry at fixed geometry on the 2.0 nm aIO, aIWO and compensated cells), its acceptance tolerances, its selection rule and its unresolved rule are unchanged, and they still fix the final smearing.
- **First use: aIWO_1p0_s1** (relaxation CONVERGED after 36 BFGS steps, no SCF failure). Its FINAL runs at Gaussian 0.001 Ry; every other FINAL setting is as registered.
- **Execution (procedural, no physics change):**
  - `-nk 1` is forced at 34 CPUs / 102 GB (the staged script would otherwise choose 2 pools); the peak memory is checked from the job record afterwards;
  - the D-24 item C export is installed, and the EOS probe and the pull fallback are verified, before the release;
  - complete export is verified separately against the A14 list. DAG success does not certify it.

### A27: H-N, extended-carrier efficacy of W against thickness, with controls C1-C6 (added after the freeze, 2026-10-11T09:09Z, before any slab electronic result was read; user go after Codex review FREEZE-WITH-EDITS (work chat); decision D-28)
- **What it adds:** the new exploratory hypothesis H-N (section 2), with frozen observables, per-cell classes, outcome rules, and controls C1-C6. Codex's review edits are applied.
- **User decisions (D-28):**
  - H-N is EXPLORATORY: the read-out rules are frozen, but no direction is scored.
  - C1 (paired substitution) runs at 0.7 nm only.
- **Sight history:** no slab FINAL has run, so no slab electronic metric has been seen by anyone. The only electronic outputs seen so far are relax-SCF energies and iteration counts, plus geomsel summaries with KS gaps for aIO_0p8_s1. The first slab FINAL (aIWO_1p0_s1, A26) was released on 2026-10-11. This amendment must be frozen before any of its electronic metrics is read.
**Why.**
H-G tests W only at 2.0 nm, so the thickness question is not registered. Three confounds would make a thickness trend ambiguous:
- **Topology:** each aIO cell is an independent melt-quench (seed + 10), not the W cell's parent network.
- **Relaxation smearing:** aIO slabs relax with Gaussian 0.005 Ry (A15), aIWO slabs with MV 0.01 Ry.
- **Functional:** PBE's delocalisation error biases the localised-versus-extended question.

W–W image interaction is only partly controlled: W is about 2 % of cations and W images are ≥ 12.5 Å apart.

### A28: H-L near-cell restart and pre-declared SCF fallback (added after the freeze, 2026-10-11T10:06Z, before any H-L energy difference was computed; user decision D-29)
- **Situation:** select_near.py on the H-L-relaxed In31WO48 ('bfgs converged', 0 steps) registered **In31WO47_near** (O30, W-O 1.89194 A; O30/O69 tied; O72 pair +0.01043 A), with near72 as the sensitivity. Its relaxation FAILED: two validated SCFs, then the SCF at BFGS step 3 did not converge in 100 iterations under the A19 settings. Its DAG ended (rescue001).
- **Restart 1:** from the lowest-energy validated geometry (step 2, E = -15454.49343800 Ry), with the A19 settings unchanged. Earlier tarballs are archived before the rescue run, because the rescue resets segment numbering.
- **Fallback, fixed now:** if restart 1 has an SCF failure, the next attempt for this cell only uses local-TF mixing, beta 0.1, electron_maxstep 300 and mixing_ndim 12. conv_thr 1e-8 and all other settings are unchanged. This changes the SCF path, not the converged energy beyond conv_thr. The cell's settings are reported with its result.
- **Rule:** if both attempts fail, or the relax is not converged by 17 Oct 10:00 UTC, the registered near-site Delta E_local is UNRESOLVED and near72 is reported only as the sensitivity.
- **Erratum (2026-10-11T13:09Z):** s0 had **three** validated SCFs (geometries 0, 1 and 2; E = -15454.48376998, -15454.48911861 and -15454.49343800 Ry), not two. The SCF at geometry 3 failed. The restart geometry (2, the lowest-energy validated one) is unchanged. Restart 1 was submitted 2026-10-11T13:04Z (DAGMan 12892680, RELAX 12892681) with the Q2 submit files.

### A29: aIO_2p0_s1 allocator setting (added after the freeze, 2026-10-11T12:53Z, before any relaxation result beyond geometry 0 exists; user go after Codex GO-WITH-CHANGES; decision D-30)
- **Wording (Codex):** For aIO_2p0_s1 only, permit `NV_ACC_MEM_MANAGE=0`. The retained-memory explanation is ASSUMED. All physical settings, A25 equivalence gates and force qualification remain unchanged. This supersedes A25's exclusion of this variable for this cell.
- **Evidence that prompted it** (rescue DAG 12891110, relax_s0, job 12891111, 09:56-12:25Z):
  - The A25 equivalence gate passed: E0 = -47594.50669745 Ry against -47594.50669747 Ry, and the iteration-1 energy also matched.
  - The force step passed.
  - The second SCF then ran out of GPU memory in `vloc_psi_k_gpu`: 8.04 GB was requested with 6.14 GB free.
  - The guard held the next retry (12891752, code 3/3); no retry was used.
- **Restart:** geometry 0 (unchanged `relax.in`), same binary and numerics. Both failed attempts and their provenance are kept.
- **Acceptance:**
  - reproduce E0 within 1e-5 Ry;
  - converge the second SCF;
  - produce a newly electronically validated geometry.

  Passing permits continued relaxation; ionic convergence still needs the registered criteria. The split-versus-unsplit force qualification (A25) still applies.
- **Monitoring:**
  - more than 104 s per iteration is a reporting trigger, not a rejection;
  - watch memory over several force/SCF cycles;
  - an unvalidated BFGS trial is never selected.
- **If out-of-memory recurs:** inspect the Davidson workspace settings first. A further amendment would qualify `cg`, which QE documents as lower-memory, or PPCG; otherwise park the cell under the 17 Oct rule.

### A30: 1-GPU split-label route for seven idle 1.5/2 nm chains (added after the freeze, 2026-10-11T20:30Z, before any of these chains has run a single SCF; user go conditional on the A29 acceptance, which passed; decision D-31)
- **Scope:** aIO_1p5_s1, aIO_2p0_s2, aIWO_1p5_s1, aIWO_2p0_comp_s1, aIWO_2p0_s1, aIWO_2p0_s1_bare, aIWO_2p0_s2 (252 to 274 atoms). Excluded, kept on their multi-GPU requests: aIWO_1p0_Al2O3_s2 (300 atoms, earlier 1-GPU attempt reverted) and aIWO_2p0_Al2O3_s2 (414 atoms, 4 GPUs).
- **Change (numerical route only):** A25 species-label split (In -> In1/In2, O -> O1/O2, alternating rule, same UPF files and masses; W and H unchanged), made with a25_labels.py (md5 93caf6fc); A29 `NV_ACC_MEM_MANAGE=0`; 1 x H100 non-MIG, 81000 MB. All physical and numerical settings (cutoffs, k-points, smearing, conv_thr, mixing, BFGS thresholds, D-24 guard and restart rules) unchanged.
- **Qualification already in hand:** (1) S2 split-vs-unsplit check on a 134-atom 1.0 nm cell at conv_thr 1e-14: |dE| = 1e-8 Ry, max |dF| = 3e-8 Ry/bohr (A25 tolerances 1e-5; claim C035). (2) A29 acceptance on aIO_2p0_s1 (job 12891752): E0 = -47594.50669741 Ry against -47594.50669745 Ry; SCF 2 converged; a new electronically validated geometry (E = -47594.52080105 Ry); about 88 s per SCF iteration.
- **Per-chain gate:** these chains have never run, so no unsplit E0 exists for an energy gate. Replaced by a construction gate: `a25_labels.py check` must show that only ntyp, ATOMIC_SPECIES and position labels differ and that restore(split) equals the original input byte for byte; otherwise that chain is not changed.
- **Failure handling:** a GPU out-of-memory stops the segment through the guard (exit 3, hold); that chain then returns to its original 2-GPU request and unsplit input. Nothing else changes.
- **Not claimed:** that 274-atom W-containing cells fit in 1 GPU (memory margin unmeasured); the retained-memory cause stays ASSUMED.
- **Read-out note:** the label map per chain (label_map_<chain>.tsv) is kept; analysis maps In1/In2 -> In and O1/O2 -> O.
- **Erratum (2026-10-12T06:06Z):** the failure-handling line "a GPU out-of-memory stops the segment through the guard (exit 3, hold)" describes the next attempt. No rule changes.
  - The out-of-memory segment itself exits 1 (nodes.log 'return value 1'), and DAGMan uses one retry: retry #1 of 8 on each 1.5 nm chain (dagman.out).
  - The FAILED [infra] line written by that segment then makes the next attempt exit 3 and be held, if that attempt starts before the guard is reset.
  - For the 1.5 nm chains the guard was reset when they returned to 2 GPUs (notes in segment_guard.20261011T233016Z). Both idle retries, 12897137 and 12897204, were REMOVED with their DAGMans (12884188, 12884192) on 2026-10-12 ~05:55Z by user decision: 1.5 nm is cut under the register's cut-first rule (section 3).
  - The A29 evidence line "no retry was used" probably reads the same way: 12891752 is relax_s1 of the rescue DAG, which is retry 1. This stays unconfirmed until checked against that DAG's dagman.out.

### A31: A15 audit route, SCF path, provisional width and role substitution (added after the freeze, 2026-10-12T00:16Z, before any 2.0 nm FINAL or width-comparison result exists; Codex GO-WITH-CHANGES, all edits applied; user go; decision D-33)
- **Why.** At the registered FINAL settings (71/568 Ry, nbnd 1.3 x occupied) the 2.0 nm cells need about 104-109 GB of GPU memory with Davidson (estimate calibrated on the measured 27,244 MiB persistent use of aIO_2p0_s1, job 12891752), more than one H100 NVL; 2-GPU jobs match no slot. The frozen read-out code (1.0.0-rc7) does not compute EA.
- **(a) Route.** The nine A15 audit runs (Gaussian 0.005, 0.002 and 0.001 Ry at fixed geometry on aIO_2p0_s1, aIWO_2p0_s1, aIWO_2p0_comp_s1) run as CPU FINALs on the registered FINAL code path (QE 7.5, D-24 export), -nk 1, 64 cores, 200 GB, runtime limit 250000 s (69.44 h, including post-processing and export). All widths of a cell use the same build and identical physical settings. Memory is an estimate until measured on the first reference run. A GPU route needs its own amendment.
- **(b) SCF path (numerical only).** conv_thr 1e-8, mixing_beta 0.1, mixing_ndim 12, electron_maxstep 300, local-TF, identical across the widths of a cell. A26 reference FINALs of cells relaxed on the A15 rescue path may use the same beta, ndim and maxstep with conv_thr as registered. **Fallback, once per run:** a non-converged run is rerun as a NEW SCF from a converged sibling width's charge density: restart_mode='from_scratch', startingpot='file', fresh wavefunctions, private copied storage; all else unchanged. Sibling order is frozen: for 0.001 Ry use 0.002 then 0.005; for 0.002 Ry use 0.001 then 0.005; for 0.005 Ry use 0.002 then 0.001. If no sibling converged or the fallback fails, the A15 unresolved rule applies.
- **(c) Labels.** Original element labels (A25 FINAL rule); a split relax.in is restored through the chain's label map; the label-blind position hash must be identical across the three widths.
- **(d) EA and provisional width (amends A15's qualification requirement).** A15 requires EA agreement; rc7 does not evaluate EA. Therefore the audit outcome is PARTIAL by construction and the A15 width is **provisional**: it is the rc7 provisional_width_candidate_Ry, reported as "edges, trap classes and donated charge compared; EA not evaluated", never as A15 met. Every result that depends on it carries the condition "A15 width provisional (EA not evaluated)". Trap-class agreement is judged on the class predicates of each flagged state matched across widths (from the rc7 per-state class lists), not on state counts; any change of a state's class makes the affected quantity UNRESOLVED. If the candidate is null, A15 is unresolved for the affected quantities.
- **(e) Common width.** The series may use the A26 0.001 Ry reference as its common width only when every cell has a 0.001 Ry FINAL with C3 PASS at both 0.002 and 0.005 Ry, the A15 candidate is non-null, and the (d) qualification is complete (provisional status recorded). Choosing a wider width never bypasses a failed cell-specific C3 check. No tolerance, threshold, class, selection or unresolved rule changes.
- **(f) Role substitution.** Eligible backups, named now: aIO_2p0_s2 for aIO_2p0_s1; aIWO_2p0_s2 for aIWO_2p0_s1; none for aIWO_2p0_comp_s1. s1 is preferred; substitution happens only if the s1 cell is not relaxation-converged by 17 Oct 10:00 UTC and the backup is, decided by relaxation status alone before any electronic result. The chosen seed and geometry are used at every width. Where no eligible backup exists, the role stays unresolved.
- **Held FINALs (D1):** the four held FINALs are released at 0.001 Ry under A26 (plain variant, no rescue mixing), with D-24 export and -nk 1; their scientific classification stays conditional under A26 and (d).

### A34: two 1-GPU split-label routes for jobs idle since 10-11 Oct: the 2.0 nm MACE force-check SCFs and aIWO_1p0_Al2O3_s2 (added after the freeze, 2026-10-12T06:06Z, before either calculation has run a single SCF; internal reviews GO-WITH-CHANGES, all changes applied; Codex: (i) GO, (ii) GO-WITH-CHANGES, all three changes applied; user go 2026-10-12, both parts included subject to Codex review; decision D-34)
- **Number.** A32 and A33 are reserved for the pending warm-start and MACE-seed pilots, so this is A34.
- **Why.**
  - All three jobs ask for 2 GPUs on one slot. 2-GPU requests match 0 slots now and 4 if drained, and this pool does no draining (measured, condor_q -better-analyze 2026-10-12 04:43-04:59Z).
  - 12890593 has been idle since 11 Oct and 12884198 since its 10 Oct 14:05Z submission, both with 0 starts.
  - 12884198's 1 x H200 attempt (D-24 item D) never matched, because the H200 nodes are VO-filtered for our group. It was reverted at 2026-10-11T12:39Z.
- **Scope.**
  - Three jobs: 12890593.0 (val_aIWO_2p0_s1_slab_annealed, 252 atoms), 12890593.1 (val_aIWO_2p0_s1_final, 270 atoms), and the aIWO_1p0_Al2O3_s2 chain (RELAX 12884198 and its DAG retries, 300 atoms).
  - For these jobs only, A34 extends the A25 split and the A29 allocator setting.
  - For aIWO_1p0_Al2O3_s2 it supersedes the A30 exclusion and the A25 line "Not part of A25: moving any other 2 nm cell (or 12884198) to one GPU".
  - Not in scope: aIWO_2p0_Al2O3_s2, the 1.5 nm chains, and any change of nbnd, solver, smearing, mixing, tolerances or BFGS settings.

- **(i) 2.0 nm MACE force-check SCFs, 12890593.0/.1 (ML_VALIDATION.md; D-12).**
  - **Route.**
    - 1 x H100 NVL, non-MIG: PreVerRequirements regexp("H100") && !regexp("MIG") && GPUs_GlobalMemoryMb >= 94000, plus the standard clauses.
    - Environment "HOME=/afs/cern.ch/user/m/melrashe QE_NK=1 NV_ACC_MEM_MANAGE=0" (A29).
    - RequestCpus 28 / RequestMemory 86016 (28 x 3072 MB, unchanged by CERN's RebalanceMemCpu transform).
    - JobPrio stays -10, below every chain.
    - One MPI rank, threads capped at 1, so the CPU count changes no numerics.
  - **Why 28 / 86016.**
    - A val job then cannot fit one of our 27/81000 chain dynamic slots, so it never takes a chain's claim.
    - In a fresh negotiation the chains win on JobPrio (0/10/15), and claim reuse is limited by CLAIM_WORKLIFE 1200 s.
    - What remains is the ~5 s DAG resubmission gap and segments held by the D-24 guard.
    - Slots: 0 now, 12 if drained (measured).
  - **No single-GPU-slot clause.** Dynamic slots report TotalSlotGPUs = 1 even on the 4-GPU boxes, so a TotalSlotGPUs clause would not protect those boxes. It would only remove 4 of the 12 slots that match if drained (measured).
  - **Labels.**
    - A25/A30 split with a25_labels.py (md5 93caf6fc): In -> In1/In2 (49/49); O -> O1/O2 (76/76 in slab_annealed, 79/79 in final).
    - W and H are unchanged; ntyp goes 3 -> 5 and 4 -> 6; the UPF files and masses are the same.
    - Unchanged: positions, cell, 60/480 Ry, MV 0.01 Ry, k 2x2x1, dipole correction, conv_thr 1e-7, beta 0.2, local-TF, electron_maxstep 200, nbnd and the ML_VALIDATION limits.
  - **Construction gate (each frame, before the qedit).**
    - Already PASS on the staged files: restore(split) equals the original byte for byte (originals md5 f68b981f / d1337644), and the label-blind position hash is unchanged (a73bd21d97e6 / 7989d9abbb80).
    - Required at install: common/a30gate.py (md5 b30d63f5) must also print PASS. It checks that undoing the split is byte-identical, that the split species share mass and UPF, and that the counts balance within 1.
    - Installed split inputs: md5 44f38c2d (slab_annealed) and 5a980640 (final). Label maps 4b6a1df4 / d49c84c3 are kept as a30_label_map.tsv.
    - A frame that fails the gate is not changed.
  - **Order and files.**
    - The input swap comes before the qedit.
    - No submit file is installed: these are plain jobs with no DAG, and nothing reads val_gpu.sub.
    - A resubmission would need new submit files whose queue lines point to ~/iwo_amorph/val/.
  - **Read-out.** Forces are compared with mace_ref.json by atom index. Element identity comes from the label map (In1/In2 -> In, O1/O2 -> O).
  - **Memory basis (measured).**
    - The live 2.0 nm chains on this route (split labels, NV_ACC_MEM_MANAGE=0, 27 CPUs / 81000 MB) use 85636-90182 MB of GPU memory (GPUsMemoryUsage) and 73243 MB of host memory.
    - Among them, 12884201 (aIWO_2p0_s1, 270 atoms, the composition of the final frame) is at 88342 MB after about 8 h of SCF and force cycles.
    - t1b 12898823 peaked at 87803 MiB of 95830 MiB (nvidia-smi) through forces and SCF 2 iteration 1.
    - Margins: about 6-8 GB on the GPU and about 12.8 GB on the host at 86016 MB.
    - The 252-atom frame has fewer electrons (no H, 6 fewer O).
    - No fit is claimed beyond these figures.
  - **Pass, per frame:**
    - exit 0, 'JOB DONE' and 'convergence has been achieved';
    - a 'Forces acting on atoms' block with nat rows (252 or 270);
    - peak GPU memory below 95830 MiB and MemoryUsage below RequestMemory (job-log termination block);
    - wall time below 72000 s.
  - **Crash or out-of-memory.**
    - OnExitHold '(ExitBySignal == true) || (ExitCode =!= 0)' holds the job with subcode 31.
    - There is no DAG and no retry. A held job is not released on 1 GPU; the frame goes to the fallback.
    - That val_results.tar.gz comes back on hold is ASSUMED, not verified for these jobs. CERN removes held jobs after 24 h.
  - **Non-converged SCF.**
    - pw.x stops and val_node.sh still exits 0, because it ends with a grep for 'JOB DONE'. Probe 12898434 returned rc 0 after 'convergence NOT achieved'.
    - The job completes and leaves the queue; no hold fires.
    - The frozen comparator marks the frame FAILED if scf.out contains 'convergence NOT achieved' or 'Maximum CPU time', or has no 'Forces acting on atoms' block with nat rows.
    - A FAILED frame counts as "not computed", never as a pass or as a failed limit.
    - A34 makes no SCF-path change for these frames.
  - **Comparator.**
    - It computes force RMSE and MAE over all atoms and the RMSE of W plus first-shell O; the melt frame is reported only.
    - Units: 25.711 eV/Å per Ry/bohr. Species come from the label map.
    - It is committed, and its hash recorded, before any val_results.tar.gz is opened.
  - **Fallback, fixed now.**
    - Trigger: a 2.0 nm frame has not started by 14 Oct 12:00 UTC, or is held for out-of-memory.
    - Route: the CPU route. RequestGPUs 0, 63 CPUs / 193536 MB (63 x 3072; an odd rank count gives nk 1), share-pool Requirements.
    - The original unsplit scf.in is restored, and the frame runs QE 7.5 CPU as the other six frames do.
    - Estimate: about 126 GB and 10-20 h. It competes with the A31 CPU FINALs.
    - A frame with no converged result by 17 Oct 10:00 UTC is reported as not computed. The 2.0 nm ML structures are then described as "starting points relaxed by DFT" (ML_VALIDATION.md).
  - **Declared differences.**
    - The 2.0 nm frames run QE 7.3.1 GPU, as the relaxations do, now with split labels. The other six frames run QE 7.5 CPU.
    - C035 qualifies the label split, not the MACE forces.

- **(ii) aIWO_1p0_Al2O3_s2 (RELAX 12884198; Al60 H16 In49 O174 W1).**
  - **Route.**
    - 1 x H100, non-MIG: PreVerRequirements regexp("H100") && !regexp("MIG"). H200 is dropped because it is VO-filtered.
    - Environment "HOME=/afs/cern.ch/user/m/melrashe QE_NK=1 NV_ACC_MEM_MANAGE=0" (A29).
    - RequestCpus 28 / RequestMemory 84000, set both by condor_qedit on the idle ad and as request_memory = 84000 in the swapped relax.sub. Every DAG retry is a fresh submit of relax.sub, so this is how each retry carries the route.
    - The md5 of the restaged relax.sub is recorded in ROLLBACK.txt before the swap.
    - qedit order: Environment, hold attributes, requirements, memory and CPUs, then RequestGPUs 1 last.
    - JobPrio stays 0.
  - **Why 84000.**
    - RebalanceMemCpu turns 84000 MB into 28 CPUs / 84000 MB and leaves it there.
    - Any request of 82944 MB or less comes back as 27/81000. That would reuse our own freed 2.0 nm claims (aIO_2p0_s1 first) and delay that chain.
    - Slots: 0 now, 12 if drained (measured).
  - **Labels.**
    - A25 split for In and O only: In -> In1/In2 (25/24), O -> O1/O2 (87/87). Al, W and H keep their labels.
    - ntyp goes 5 -> 7; the UPF files and masses are the same.
    - Made with a25_labels.py (93caf6fc). Label map label_map_aIWO_1p0_Al2O3_s2.tsv (md5 75888383); split relax.in md5 de20b08c; original e46f9e41.
    - All physical and numerical settings are unchanged: 60/480 Ry, MV 0.01 Ry, k-points, conv_thr 1e-7, beta 0.2, local-TF, electron_maxstep 200, nbnd, BFGS thresholds, and the D-24 guard and restart rules.
  - **Construction gate (PASS on the staged pair).**
    - common/a30gate.py (b30d63f5) passes: undoing the split is byte-identical, the split species share mass and UPF, and the counts balance.
    - a25_labels.py restore is byte-identical, and the label-blind hash is unchanged (8ccb1da2046f).
    - Disclosure: `a25_labels.py check` prints FAIL on four lines whose expected values are fixed for aIO_2p0_s1 (ntyp 3 -> 5, five species lines, 268 position rows, In 50/50, O 78/78, H 12).
    - These are not construction defects. The generic gate is the one used for the seven A30 chains.
  - **Hold policy, exactly as staged** (relax.sub.stuckfix_1gpu, and qedited into the idle ad):
    - `on_exit_hold = (ExitBySignal =?= false) && ((ExitCode =?= 3) || ((ExitCode =?= 1) && ((time() - JobCurrentStartDate) < 3600)))`
    - `on_exit_hold_subcode = ifThenElse(ExitCode =?= 3, 3, 4)`
    - `on_exit_hold_reason = ifThenElse(ExitCode =?= 3, "D-24 stop: segment_guard or segment_stop holds a STOP or FAILED line, pw.x not run; reset per common/README_D24_BD.txt section 3, then condor_release (the job ran seconds)", "stuckfix: exit 1 within 1 h of start on the 1-GPU route (likely GPU out-of-memory); do not release before the rollback in checks/stuckfix_al2o3/ROLLBACK.txt")`
    - Exit 1 within 1 h of start: held with subcode 4, and no DAG retry is used. Exit 3 (guard or stop): held with subcode 3, as before.
    - Before the last edit (RequestGPUs 1), the qedited strings are compared word for word with the staged ones (condor_q -af:r). Any mismatch stops the change.
    - This policy is used only if the G0 policy test passes. G0 runs three CPU test jobs: exit 1 must be held 3/4, exit 3 held 3/3, and exit 0 must complete.
    - If G0 fails, the original OnExitHold stays, and an early out-of-memory error costs one of the 8 retries (0 used so far).
    - The preflight exit 1 cannot fire on this ad, because geomsel.py, segment_guard and segment_stop are transferred. A subcode-4 hold is still read from relax.out before any action.
  - **Out-of-memory path.**
    - The chain returns to its 2026-10-11T12:39Z state with unsplit input. relax.sub.pre_stuckfix_<stamp> (md5 be214634) and relax.in.pre_stuckfix_<stamp> (e46f9e41) are copied back.
    - The ad goes back to RequestGPUs 2, RequestCpus 22, RequestMemory 66000, regexp("H100|H200") && !MIG, Environment QE_NK=1, and OnExitHold with code 3 only.
    - Early OOM (subcode 4): the rollback is applied to the held job, which is then released and waits for a 2-GPU slot.
    - Late OOM (after 1 h, for example at a force step or SCF 2): the segment exits 1 and uses one DAG retry. The guard (FAILED [infra]) then holds the next attempt with subcode 3, and the same rollback is applied to that held retry before any release. This relies on the recovery-rule correction below.
    - Nothing else changes.
  - **Recovery-rule correction (Codex change 1).**
    - The steps_relax variant used by aIWO_1p0_Al2O3_s2 (md5 737dd426 lineage) accepted best_new=yes as CONTINUE before checking fatal GPU errors. An out-of-memory error after a new validated geometry therefore wrote no guard.
    - Before the route starts, the steps check fatal GPU/CUDA errors before accepting continuation. On such an error they archive the validated geometry, write FAILED [infra], and the next retry must hold. This is verified by a test before the route starts.
    - Whether the same ordering exists in the 2 nm chain variant is being checked separately. A34 claims neither that it does nor that it does not.
    - **Check result for the other chain variant (2026-10-12T07:16Z; procedural, no rule change; Codex GO; decision D-37).** D-24 steps md5 61b079ad in the live chains: the same 3-line guard-ordering fix installed 2026-10-12 (md5 5ac5556a); tested scope: fatal GPU errors that formerly entered CONTINUE now give FAILED [infra] with the geometry archived; all other classifications unchanged (18 real segments, 7 synthetic cases).
      - 61b079ad had the same ordering: CONTINUE on best_new=yes (line 34) came before the GPU/CUDA check (lines 38-39). The insert (after line 33) is identical to the 737dd426 -> a29a6f11 insert of A34(ii).
      - The only changed case is a fatal GPU/CUDA error ('Out of memory allocating', CUDA_ERROR, cudaError, 'Accelerator Fatal Error') in a segment that also produced a new validated geometry. It now gives FAILED [infra]: the geometry is archived as relax_s<k>_bestvalid.in, relax.in stays at the segment input, and the next attempt exits 3 and holds.
      - Tests against 61b079ad before the install: A34 tests (a)-(e) PASS. Independent check: 18 real segment tarballs of the 61b079ad run dirs and 4 synthetic unchanged cases gave identical results; the 3 synthetic "new geometry + fatal GPU error" cases changed as intended.
      - Installed 07:16:41Z in seven live run dirs: aIO_2p0_s1, aIO_2p0_s2, aIWO_2p0_s1, aIWO_2p0_s2, aIWO_2p0_comp_s1, aIWO_0p7_s1 and aIWO_0p7_s1_bare (backups steps_relax.sh.pre_A34b_20261012T071640Z). It takes effect from each chain's next segment; running segments are untouched. aIWO_0p8_s2 was left at 61b079ad by this install.
      - It implements A30's registered failure handling and the D-24 [infra] classification; neither is changed. Accepted cost: after a late out-of-memory error a 2.0 nm chain is held until a decision, and a transient CUDA fault also holds a chain; a hold left > 24 h is removed by the CERN schedd and costs one DAG retry.
      - Not covered: the A15 pilot variant 4d6d99a9 (aIO_0p8_s1, bulk references), which has no guard and no GPU check. Its separate fix is pending a separate user go.
  - **SCF risk (measured) and the response, fixed now.**
    - 12884198 has the same ELECTRONS block as aIWO_2p0_s1_bare: MV 0.01 Ry, beta 0.2, local-TF, electron_maxstep 200, conv_thr 1e-7.
    - That chain's first SCF (12884200) stalled at about 5e-4 Ry for 160 iterations. It wrote FAILED [scf] at 2026-10-12T04:37:32Z after 14,723 s and used DAG retry 1 of 8. Its retry, 12900773, was held by the guard at 04:38:39Z.
    - An aIO 2.0 nm run with beta 0.2 and MV smearing also failed at 200 iterations (12883895).
    - Here the same failure would show after about 3-4 h (estimate).
    - Response: on FAILED [scf] the chain is parked as aIWO_2p0_s1_bare was. segment_stop is armed, the guard-held retry is not released, and the DAG is removed only on the user's go.
    - A34 makes no SCF rescue (no change of mixing, smearing, electron_maxstep, solver or restart density). Any rescue is a separate physics amendment, logged before any further result of this cell is read.
  - **Scope and deadline (section 3).**
    - **Frozen scope (Codex change 3).** The 1.0 nm interface route is exploratory regardless of completion time. The statement that it cannot converge by the cutoff is an estimate (ASSUMED), not an established fact, and does not determine eligibility for primary scoring: eligibility follows from this amendment's exploratory scope alone.
    - Estimate (ASSUMED): this chain does not converge by 17 Oct 10:00 UTC. The 2.0 nm chains on this route take about 2.5-4 h per BFGS step (measured: 43-142 SCF iterations at 89-94 s, 5-8 BFGS steps per 20 h segment). At most six segments fit before the cutoff (estimate).
    - Its geometry, relaxation eigenvalues and any FINAL are exploratory fallbacks that never stand in for a primary test, whenever the chain converges.
    - What the move gives: an exploratory 1.0 nm interface geometry and continuation until access ends on 21 Oct (last submission 18 Oct 22:00 UTC). It gives no H-I result.
  - **FINAL.**
    - Original labels, restored through the label map (A25 FINAL rule).
    - It has no route before the deadline. A FINAL runs only after RELAX converges, and A34 sets no FINAL resources for this cell. A31's CPU route covers the audit cells only.
  - **Not claimed.**
    - That the 300-atom cell fits one H100. The memory model gives 81-93k MiB of 95,311 MiB, worst case 92.8k (estimate).
    - The retained-memory cause behind A29 stays ASSUMED.
    - More than 180 s per SCF iteration, or GPUsMemoryUsage above 93,000 MiB, is a reporting trigger, not a rejection.

- **aIWO_2p0_Al2O3_s2 (RELAX 12884202, 414 atoms) has no route.**
  - It does not fit one H100 (core 128.9 GB, estimate), and 1 x H200 is VO-filtered (measured).
  - 2-4 x H100 on one node match 0 slots now and 4 if drained, and this pool does no draining (measured).
  - Even with a reservation it would need about 1.6-2.1 h per BFGS step and could not converge by the cutoff (estimate).
  - A 2-GPU route would also need the A25 split (the unsplit force step is about 91k of 95.3k MiB per GPU, estimate) and its own amendment.
  - It was stopped 2026-10-12 ~05:55Z by user decision (segment_stop STOP; DAGMan 12884193 removed with never-started node 12884202); H-I expected UNRESOLVED. The A30 exclusion stands for this cell.
- **What H-I can and cannot conclude (H-I text unchanged).**
  - H-I tests both Al2O3 cells. Its |Δ| ≤ 0.2 eV prediction is at 2.0 nm, and Supported needs both predictions with a valid interior alignment in both cells.
  - Without aIWO_2p0_Al2O3_s2, H-I cannot be Supported, and the |Δ| > 0.2 eV branch of Failed cannot fire.
  - The only scoring path left would be Failed through a qualifying interface state in the 1.0 nm cell, which needs a converged geometry and its FINAL. On the A34 route that cell is exploratory by scope (frozen above), so its results do not score H-I whenever they arrive. H-I is therefore expected UNRESOLVED at 17 Oct 10:00 UTC (section-3 rule).
  - An interface state seen in the exploratory 1.0 nm relaxation eigenvalues (A24 interface weight) is reported as an exploratory observation. It does not score H-I.
  - H-M is unaffected. Its DFT settings are those of aIWO_2p0_Al2O3_s2, and resources are not settings. Its comparison with Al2O3_s2 is a forecast, not a test, and is reported as not evaluated.
- **Implementation note (2026-10-12T07:27Z; records the installs and corrects the out-of-memory rollback; no threshold, physics or route change; Codex GO-WITH-CHANGES, change applied).**
  - **(ii) installed 06:19:27Z; idle ad 12884198 qedited 06:20:45-06:20:49Z (1 GPU / 28 CPUs / 84000 MB, hold attributes as staged).**
    - steps_relax.sh 737dd426 -> a29a6f11 adds a 3-line insert before the CONTINUE branch.
      - A fatal GPU/CUDA error after a new validated geometry now gives FAILED [infra]. It uses the same pattern as the existing [infra] check.
      - The geometry is archived as relax_s<k>_bestvalid.in, and relax.in stays at the segment input.
      - The guard line makes the next attempt exit 3 and hold.
    - Tests (a)-(e) against 737dd426: PASS.
      - (a) New validated geometry, then out-of-memory. Original: CONTINUE, next attempt exit 1. Fixed: FAILED [infra], next attempt exit 3. The archived geometry equals the original's CONTINUE geometry.
      - (b) new geometry without error, (c1) out-of-memory at start-up, (c2) out-of-memory after SCF 1 with no new geometry, (d) converged, (e) SCF failure after a new geometry: output identical to the original.
    - relax.sub c63a7878 -> 07a50f7f, built from the measure-3 file (LIMIT 79200 s kept).
    - relax.in e46f9e41 -> de20b08c: a30gate PASS; label map 300/300 rows, 0 mismatches.
    - Backups: *.pre_A34_20261012T061927Z.
    - The install's label-map check first aborted at 06:18:04Z, before any change, because it did not skip the map's header row. The rerun at 06:19:27Z passed.
    - G0 hold test, cluster 12901311: PASS. Exit 1 was held 3/4, exit 3 held 3/3, and exit 0 completed.
      - A first automated verdict line read FAIL for the exit-0 job, because condor_history printed an empty job id. The job record (JobStatus 4, ExitCode 0) and the user log show normal termination.
      - The extended hold policy is therefore in use.
  - **(i) installed 06:08Z; ads 12890593.0/.1 qedited to 1 GPU / 28 CPUs / 86016 MB.**
    - a25_labels.py check exits 1 on both frames only because its expected values are fixed for aIO_2p0_s1. slab_annealed has 2 FAIL lines (row count, label counts); final has 4 (ntyp, species lines, row count, label counts). As disclosed for (ii), these are not construction defects.
    - a30gate.py (b30d63f5): 3 x PASS per frame. restore is byte-identical, and the label-blind hashes are unchanged (a73bd21d97e6 / 7989d9abbb80).
    - The independent frame check (a34i_framecheck.py, md5 208e4f5d), with frame-specific expected values: PASS.
    - The label maps carry a header that names aIO_2p0_s1. Their content is correct; the frozen comparator skips '#' lines and the header row.
  - **Out-of-memory path: backup names corrected.**
    - The out-of-memory-path bullet above names relax.sub.pre_stuckfix_<stamp> (md5 be214634) and relax.in.pre_stuckfix_<stamp>.
    - The backups the install actually wrote are relax.sub.pre_A34_20261012T061927Z (md5 c63a7878: 2 GPUs, LIMIT 79200 s) and relax.in.pre_A34_20261012T061927Z (e46f9e41).
    - be214634 is relax.sub.D24_2gpu (also kept as relax.sub.pre_m3_20261012T051854Z), with LIMIT 72000 s. It is not used.
  - **Rollback correction (out-of-memory / FAILED [infra] path only; Codex change).**
    - After an out-of-memory error / FAILED [infra] in segment k >= 1, the rollback resumes from the chain's lowest-energy validated geometry: relax_s<k>_bestvalid.in, or relax_s<k>_input.in if segment k produced no new validated geometry.
    - That geometry is restored to the original labels: a25_labels.py restore, a30gate PASS, and no split label left.
    - The s0 input e46f9e41 is used only when no validated geometry beyond s0 g0 exists.
    - The relax.sub restored is relax.sub.pre_A34_20261012T061927Z (c63a7878, LIMIT 79200 s).
    - steps_relax.sh stays a29a6f11, because the correction is also valid on 2 GPUs. 737dd426 is restored only in a full revert.
    - A FAILED [scf] keeps the registered response: park, no rescue ("SCF risk" bullet above). No rollback and no release follow it.
    - ROLLBACK.txt: 126cd76b (predecessor) -> **3765bf2f** (corrected, 06:41:35Z; backup ROLLBACK.txt.pre_A34fix_20261012T064135Z): adds this branch as steps (1)-(5); nothing was removed.
    - Then 3765bf2f -> f5b1c42c (~07:10Z): step (5) corrected so that a 2-GPU rollback keeps steps_relax.sh a29a6f11 (and skips the relax.in line) unless a full revert is decided.
    - Where ROLLBACK.txt words the branch more broadly, this note governs: the branch is used for the out-of-memory / [infra] path only.

### A35: aIWO_0p8_s2 Gaussian rescue, one attempt, with a final qualification SCF (added after the freeze, 2026-10-12T07:27Z, after the diagnosis of segments s0-s2 and before any output of the rescue segment exists; user go 2026-10-12 after the diagnosis; internal skeptic review, changes applied; Codex GO-WITH-CHANGES, all changes applied; decision D-36)
- **Scope.** aIWO_0p8_s2 only (147 atoms, 1163 electrons, nspin 1), from segment s3 on. For this cell, A35 replaces the MV 0.01 Ry relaxation smearing that the register records for the aIWO slabs (A23 (i); A27, "Relaxation smearing"), and applies the A15 rescue settings to one aIWO cell. No other cell changes.
- **Why.**
  - Three SCF failures on MV 0.01 Ry, each after converged SCFs (RESULTS_LOG 2026-10-12 07:22Z; claim C036):
    - s0 (job 12884030; pre-D-24 mixing): the SCF at g14 did not converge in 200 iterations;
    - s1 (job 12889333; aids beta 0.1, mixing_ndim 12, electron_maxstep 300; from s0 g13): g11, 300 iterations; FAILED [scf] at 2026-10-11T15:42:37Z;
    - s2 (job 12893894; same settings; from s1 g10): g2, after a 0.0032 Å step (largest atom move). The SCF accuracy stayed between 8.5e-6 and 1.5e-4 Ry over iterations 11-300. FAILED [scf] at 2026-10-12T05:50:37Z.
  - A fresh restart at a fixed geometry did not reproduce the continued MV SCF at production tolerance (finding E, below).
  - The step was pre-declared before the s1 result, in the work chat at 2026-10-11T03:15Z: "If this SCF fails again, the next step is Gaussian (A15 settings) for this chain."
    - s1's failure (15:42:37Z) met that condition. But on a user go at 18:15:33Z, s2 was released on MV with the same aids from s1 g10 (disclosure below).
    - A35 takes the pre-declared step one segment late.
  - The A15 pilot passed on aIO_0p8_s1 (D-16; work chat 2026-10-10T21:35Z). That cell is the 0.8 nm partner of this one and relaxes on Gaussian 0.005 Ry. With A35, the 0.8 nm pair shares one relaxation-smearing family.
- **Change.**
  - Start geometry: relax_s2_bestvalid.in (md5 7ce25d2602bde39483bd8f45ba9f497a), from runs/aIWO_0p8_s2/relax_s2_results.tar.gz (md5 1fd8de15cd6ecb9bc055d99030645fe2).
    - s2 g1, F = -24364.22155515 Ry. Its largest force component is 4.651e-3 Ry/bohr (largest per-atom force 5.10e-3).
    - Rows md5 e0098124335b (convention of the 03:15Z note). d24_posmd5 e24b17e60a84 (confirmed), as the s3 lineage log will print it.
  - smearing = 'gaussian', degauss = 0.005 Ry (was 'mv', 0.01).
    - Apart from the per-segment max_seconds (driver.sh rewrites it every segment), this is the only changed line.
    - The A15 pilot input uses verbosity 'high'; A35 keeps 'low', which changes only the output.
  - Unchanged:
    - SCF: mixing_beta 0.1, local-TF, mixing_ndim 12, electron_maxstep 300, conv_thr 1e-7;
    - ionic: forc_conv_thr 1e-3, etot_conv_thr 1e-4, BFGS settings;
    - cell: dipole correction (tefield/dipfield, edir 3), 60/480 Ry, k-points, nbnd (QE default, 698), nspin 1;
    - procedure: the D-24 guard and restart rules, the A19 convergence rule, RELAX LIMIT 79200 s (D-35).
  - Install per README_D24_BD.txt section 3:
    - relax.in is replaced first (backup relax.in.pre_reset_<utc>; the current relax.in is the s2 input, md5 7eb8a89e).
    - Then the stop texts are kept (segment_guard.<utc>, segment_stop.<utc>) and cleared. segment_guard is emptied, not deleted: the job transfers it, and its absence re-held 12893894 on 11 Oct.
    - Then the reset is logged in the work chat (time, reason, new relax.in md5).
    - The idle retry 12901263 reads these files when it starts. If it starts before the reset, it is held (exit 3). After the reset it is released with condor_release (it ran seconds).
- **Budget.** Six node attempts remain in DAG 12884028 (retries #3 to #8 of 8).
  - #3 is the idle 12901263 (segment s3; 0 starts at 07:06Z; LIMIT 79200 s).
  - Each A35 segment uses one attempt. "One attempt" below means one rescue route; its CONTINUE segments draw on this budget.
  - At most about five 22 h segments fit before 17 Oct 10:00 UTC, and only if each starts at once (estimate).
- **One attempt only.**
  - If any A35 segment writes FAILED [scf], or the relaxation has not printed 'bfgs converged' (A19) by 17 Oct 10:00 UTC, the 0.8 nm W class is UNRESOLVED for H-N. NO CROSSOVER then cannot be claimed (H-N outcome rules: missing coverage at 0.8 nm).
  - The chain is then parked as aIWO_2p0_s1_bare was (D-35): segment_stop STOP is armed, the guard-held retry is not released, and the DAG is removed only on the user's go.
  - There is no further rescue: no other smearing or width, mixing, solver, spin, band count or restart density.
  - A FAILED of another category ([infra], [early], [noprogress], [parse]) follows the D-24 guard and restart rules unchanged. Resuming after it is not a second rescue.
- **A15 force comparison: UNRESOLVED by design for this cell (fixed now).**
  - A15's force check (MV 0.01 against Gaussian 0.005 single-point forces, 1e-3 Ry/bohr) names one 2.0 nm aIWO geometry. The A27 C4 screen ran it on the 1.0 nm W cell (aIWO_1p0_s1; RESULTS_LOG 2026-10-11 10:41Z, clusters 12891104/12891105): max |ΔF| 2.42e-4 ≤ 1e-3 Ry/bohr, so the smearing family is not a geometry uncertainty at 1.0 nm (C034).
  - The per-cell comparison for aIWO_0p8_s2 is new, and it is UNRESOLVED by design:
    - This cell's MV force reproducibility across a restart at production tolerance is about 5e-3 Ry/bohr or worse (max |ΔF| 4.99e-3 and 2.69e-2 Ry/bohr, finding E).
    - A comparison at 1e-3 Ry/bohr is below that resolution (section 0 censoring rule).
  - The geometry uncertainty from the smearing family is therefore reported as unresolved for this cell, not as absent.
  - The first Gaussian SCF at s3 g0 (F and the largest force component only) is reported as a diagnostic.
- **Restart reproducibility gate (every A35 segment restart).**
  - At every A35 segment restart, the first SCF of the new segment (a fresh start) recomputes the carried geometry.
  - It must reproduce the previous segment's value at the same geometry within 1e-5 Ry in F (the A25 energy tolerance), and within 1e-3 Ry/bohr in max |ΔF| over all 441 force components (the relaxation's forc_conv_thr).
  - s3 changes the smearing, so its g0 is not compared with s2. The restart gate applies from s4 on (Gaussian against Gaussian).
  - If the relaxation converges inside s3, the restart gate is reported as "not exercised"; the qualification SCF below is still required.
  - A failed gate does not stop the chain.
- **Qualification SCF at the final geometry (required, regardless of how many segments ran).**
  - After 'bfgs converged' (A19), a fresh-start SCF (a new pw.x run) is computed at the final geometry with the relaxation settings: Gaussian 0.005 Ry, conv_thr 1e-7, the aids, the dipole correction, 60/480 Ry and the same k-points, nbnd and nspin; calculation 'scf', forces printed.
  - It is compared with the relaxation's last SCF at that geometry. It passes within 1e-5 Ry in F and within 1e-3 Ry/bohr in max |ΔF| over all 441 force components (the frozen gate tolerances).
  - So a relaxation that converges inside s3 is qualified too: convergence within one segment does not bypass the qualification.
  - An SCF that does not converge in this run counts as a failed qualification. A run that stops before its first SCF energy for an infrastructure reason (out of memory, eviction) may be repeated with the identical input.
- **Certificate binding and the exploratory rule (new A35 rule, modelled on section 3).**
  - The gate evidence is bound into the relaxation block of this cell's run certificate as evidence files with their sha256: every segment-restart gate and the final qualification, each with both outputs and the comparison.
  - The relaxation block is 'converged' only if 'bfgs converged' was printed (A19), the qualification passed, and no gate on the lineage failed.
  - A failed or missing qualification, or any earlier gate failure on the lineage, gives relaxation=exploratory. The frozen reader excludes it from primary scoring: compute/amorph/analysis/certify.py line 218 makes any relaxation other than 'converged' a disqualifying reason.
  - Earlier gate failures stay attached to the descendants: a failed gate is carried by every geometry relaxed from the gated geometry, and it is reported with every result on them.
  - A class read on an exploratory geometry is reported, but does not count as resolved 0.8 nm coverage for NO CROSSOVER.
- **H-N read-out (A27 rules unchanged).**
  - A27 records the relaxation-smearing confound: aIO slabs relax with Gaussian 0.005, aIWO slabs with MV 0.01. C4 handles it at 2.0, 1.0 and 0.7 nm:
    - those aIWO cells get a Gaussian 0.005 polish from their MV geometries;
    - classes are reported for both geometries;
    - a crossover must hold on the Gaussian-polished geometries.
  - aIWO_0p8_s2 has only a Gaussian-family geometry, because its MV segments never converged.
    - Its class is read on that geometry. It belongs to the Gaussian series, on which a crossover must hold, with the C4-polished cells and aIWO_bulk_s1 (Gaussian 0.005, A23).
    - In the MV-geometry series it is listed as "Gaussian geometry (A35); no MV geometry".
  - The 0.8 nm W cell and its aIO partner therefore share the relaxation smearing. At 2.0, 1.0 and 0.7 nm, the pairs share it only on the C4-polished geometries.
  - 0.8 nm is not a C4 point, so A35 adds no control.
  - The FINAL is unchanged: A35 changes the relaxation smearing only. The FINAL width follows A26/A31, as for every cell.
  - **Disclosed: the W series uses mixed relaxation smearing.**
    - aIWO_bulk_s1: Gaussian 0.005 (A23).
    - aIWO 2.0, 1.0 and 0.7 nm: MV 0.01, with the C4 Gaussian polish.
    - aIWO_0p8_s2: MV 0.01 for s0-s2 (not converged), then Gaussian 0.005 (A35).
    - Every H-N table gives each cell's relaxation smearing and geometry lineage.
- **Sight history.**
  - Read before A35: the relax.out of s0-s2 of this cell. That is, relax-SCF energies and energy components (one-electron, Hartree, Ewald, electric-field (dipole) correction, -TS), forces and SCF-accuracy traces.
  - The diagnosis and check scripts also parsed the relax-SCF Fermi energies of s0-s2. They appear in the review digest (work chat 2026-10-12T07:08Z), but they were not used for any conclusion or decision and are not reported in RESULTS_LOG.
  - The s2 relax.out also served, unmodified, as fixture (e) of the A34(ii) recovery-rule test at 06:11Z. The s1 relax.out was the base of the synthetic cases of the 2 nm guard-fix check (07:00-07:06Z).
  - Not read: projections, PR_n, gaps or edges. No FINAL exists for this cell.
  - A35 is logged before any output of segment s3 or later is read.
- **Disclosure (post hoc, user approved; D-36).**
  - s1 wrote FAILED [scf] at 2026-10-11T15:42:37Z. That met the 03:15Z condition for the Gaussian step.
  - On a user go, the chain was nevertheless released at 18:15:33Z on MV 0.01 Ry with the aids kept.
    - relax.in = relax_s1_bestvalid.in (s1 g10, F -24364.22108847 Ry; rows md5 5a37d5ee3f89; d24_posmd5 59daedf1ee26).
    - The job was held again at 18:27:28Z. It was released at 20:29:46Z, after an empty segment_guard was created. s2 (job 12893894) then ran on that input.
  - These steps were recorded only in CERN runs/aIWO_0p8_s2/d24_release.log: "released 12893894 ... user go" and "empty segment_guard created (transfer needs it), 12893894 released again".
    - README_D24_BD.txt section 3 (step 4) requires a work-chat log, and none was written.
    - There was also no register line and no decision row.
  - At the 2026-10-12T00:20Z monitor, Codex asked for a terminal diagnosis "before another attempt". The MV attempt had already been released and was idle. The digest showed the node idle, but not that it was this released attempt.
  - Recorded now in the work chat (action note 2026-10-12T07:27Z), in D-36, and here.
- **Finding (E): restart non-reproducibility at production tolerance.**
  - **Observation.**
    - At fixed geometry and identical settings (s1 g10 -> s2 g0), a fresh MV SCF gave ΔF 1.18e-5 Ry and max |ΔF| 4.99e-3 Ry/bohr.
    - Across the s0 -> s1 restart, where the mixing settings also changed (beta 0.2/200 -> 0.1/ndim 12/300), it gave 4.0e-3 Ry and 2.69e-2 Ry/bohr.
    - The s1 -> s2 pair would fail A35's own gate on both tolerances.
  - **Same geometry, by record.**
    - The fresh segment's input is geomsel's copy of the previous segment's validated geometry. geomsel (5bfbae78) copies the segment input and replaces only ATOMIC_POSITIONS; the relaxation is fixed-cell.
    - The position rows (coordinates with species labels) hash equal: d24_posmd5 aad143fa86fe (s0 bestvalid = s1 input) and 59daedf1ee26 (s1 bestvalid = s2 input). The rows md5, xyz-only and raw-row hashes also match.
    - The cell, species and k-point cards are carried by that construction and were not hashed separately. The namelists differ only in max_seconds and, for s0 -> s1, the mixing line.
    - Ewald agreement within 5e-8 Ry is consistent with this. It is not used as the identity test.
  - **Interpretation open.**
    - It may be an incomplete-SCF force error at conv_thr 1e-7.
    - It may instead be two distinct converged electronic branches. The branches and their dipole mechanism remain ASSUMED.
    - The SCF-correction forces already printed in the s0-s2 relax.out are inspected before any stronger attribution.
    - Numbers behind the ASSUMED mechanism: at g13 (a pair that also changed the mixing), with the Ewald term fixed, Hartree moves +3.62 Ry and one-electron -3.61 Ry, and the dipole-correction energy goes 5.18 -> 3.83 mRy.
    - Conditions shared with the cell: odd electron count (1163), nspin 1, MV, dipole correction. They are not sufficient on their own: the 1.0 nm W cell (also odd-electron, MV, dipole correction) reproduced to 4e-8 Ry (RESULTS_LOG 2026-10-11 10:41Z).
  - **A28.** Numerical-path invariance cannot be assumed for this cell. A28's premise ("This changes the SCF path, not the converged energy beyond conv_thr") concerns the crystalline H-L cell, and this observation does not falsify A28's result. Nothing is claimed for other cells.
- **Not changed.**
  - H-N cells, observables, classes, thresholds, controls and outcome rules.
  - C4 and its endpoints.
  - A15, A25, A26, A28, A31.
  - The section 3 cutoff (17 Oct 10:00 UTC).
  - The MV relaxation of every other aIWO cell.

### A36: 2.0 nm W-chain SCF rescues, one attempt each, with a final qualification SCF; conditional rescue of aIWO_2p0_s1 (added after the freeze, 2026-10-12T13:21Z (commit b164faa), after reading segment s0 of aIWO_2p0_s2 and aIWO_2p0_comp_s1 and before any output of a rescue segment exists; internal diagnosis and skeptic review; Codex GO-WITH-CHANGES for both cells, all changes applied (work chat 2026-10-12T13:15Z); user go 2026-10-12 ~13:15Z, conditional on Codex GO, with mechanical changes applied; decision D-40)
- **Scope.** Two 2.0 nm W chains from segment s1 on, both on the A30 route (1 x H100 NVL non-MIG, A25 split labels, NV_ACC_MEM_MANAGE=0), plus a pre-declared conditional rescue of aIWO_2p0_s1. No other cell changes.
  - aIWO_2p0_s2: 264 atoms, In98 W2 O156 H8, 2246 electrons, nbnd 1348, nspin 1, DAG 12884196.
  - aIWO_2p0_comp_s1: 274 atoms, In98 W2 O160 H14, 2276 electrons, nbnd 1366, N_ex 0, DAG 12884377.
- **Why.**
  - aIWO_2p0_s2, s0 (job 12884203): 3 converged SCFs (g0-g2: 127, 118, 89 iterations; F -48288.69855246, -48288.71987938, -48288.73039545 Ry; largest force component 4.62e-2, 1.74e-2, 1.38e-2 Ry/bohr). The SCF at g3 (after a 0.0096 A largest atom move) stalled at 6.9e-7 to 1.5e-6 Ry from about iteration 45 to 200 (conv_thr 1e-7). FAILED [scf] 2026-10-12T09:57:56Z. The converged SCF at g1 also sat at 1.5e-7 to 1.2e-6 for about 70 iterations, so 1e-7 is near a floor for this cell on MV; a larger iteration budget alone is not expected to help.
  - aIWO_2p0_comp_s1, s0 (job 12884378): 2 converged SCFs (106, 168 iterations; F -48462.5980789, -48462.62999873 Ry; largest component 5.81e-2, 2.18e-2). The SCF at g2 reached 200 iterations with the accuracy still falling (5.9e-5 at 100, 1.6e-5 at 160, 3.0e-7 at 190, 1.7e-7 at 200). FAILED [scf] 2026-10-12T09:38:54Z: an iteration-limit failure, not a stall.
  - Both s0 segments ran the original ELECTRONS line (mixing_beta 0.2, electron_maxstep 200, default mixing_ndim, local-TF), without the A15 aids.
  - The 2.0 nm W cells on MV 0.01 had 3 SCF failures in 14 completed SCFs (s2, comp, s1_bare); the amorphous Gaussian 0.005 slabs had none in their completed SCFs. Small samples; no causal claim.
  - QE's Fermi-level minimisation fell back to bisection 9 (s2) and 13 (comp) times, all at iteration 40 or earlier, none during the stall or slow tail. No causal role is claimed.
- **Change.**
  - Start geometries: each chain's best validated geometry from runs/<cell>/relax_s0_results.tar.gz.

    | Cell | Source | relax_s0_bestvalid.in md5 | Tarball md5 | F (Ry) | Rows md5 |
    |---|---|---|---|---|---|
    | aIWO_2p0_s2 | s0 g2 | 2223d6cf9511a9084e399e9b8a1086e3 | 4b9a194fb3227359a76b5c8ce79131f4 | -48288.73039545 | 02b98b22e8e7 |
    | aIWO_2p0_comp_s1 | s0 g1 | 8aacdf982a87ec3d24b977537bc8f579 | cf585c850f86e4fa76ec2efecc12af73 | -48462.62999873 | fb23c0ea8b3c |

  - **aIWO_2p0_s2 (Gaussian plus aids; Codex GO-WITH-CHANGES):** two changed lines against the bestvalid input, byte-identical to the A35 s3 input lines:
    - smearing = 'gaussian', degauss = 0.005 (was 'mv', 0.01);
    - mixing_beta 0.1, electron_maxstep 300, mixing_ndim 12 (was 0.2, 200, default). Staged relax.in md5 0df5ad470e41288cf51db317995e964d.
  - **aIWO_2p0_comp_s1 (MV plus aids; Codex recommendation):** one changed line: mixing_beta 0.1, electron_maxstep 300, mixing_ndim 12 (was 0.2, 200, default). Smearing stays MV 0.01, the registered aIWO relaxation family. Staged relax.in md5 09eab9f1a6189891d5858bdd79c601bf. This is an amended numerical change recorded here, not an undocumented README section 3 reset.
  - Unchanged for both: conv_thr 1e-7, local-TF; forc_conv_thr 1e-3, etot_conv_thr 1e-4, BFGS settings; dipole correction (edir 3, emaxpos 0.95, eopreg 0.04); 60/480 Ry; k 2x2x1; QE-default nbnd; nspin 1; verbosity low; A25 split labels (species block byte-identical, position rows hash equal); NV_ACC_MEM_MANAGE=0; RELAX LIMIT 79200 s (D-35); D-24 guard and restart rules with the steps 5ac5556a (D-37); A19; A30 out-of-memory rule. driver.sh still rewrites max_seconds every segment.
  - Memory (ASSUMED): mixing_ndim 12 adds about 0.4 GB; the live 2 nm chains use 85.6-90.2 of 95.8 GB.
  - Install per README_D24_BD.txt section 3 with checks/gpumax_a36/install_A36.sh (md5 65a68d5339d52756e2bf123167377172): backup relax.in.pre_reset_<utc>, install, keep and empty segment_guard/segment_stop, log in the work chat. The idle s1 nodes 12901989 (s2) and 12901955 (comp) read the files when they start; at 13:17Z they were reshaped to 28 CPUs / 86016 MB (user go) so that they start on a newly free H100 instead of taking a running chain's GPU.
- **Budget.** Each chain has its idle s1 node (retry #1) and retries #2-#8: 8 node attempts. Each A36 segment uses one. "One attempt" below means one rescue route; its CONTINUE segments draw on this budget.
- **One attempt only (per cell).** If any A36 segment of a cell writes FAILED [scf], or the cell has not printed 'bfgs converged' (A19) by 17 Oct 10:00 UTC, the cell's roles below are UNRESOLVED and the chain is parked as aIWO_2p0_s1_bare was (D-35): segment_stop STOP armed, the guard-held retry not released, the DAG removed only on the user's go. No further rescue: no other smearing or width, mixing, solver, spin, band count, restart density or conv_thr. Other failure categories follow D-24 unchanged; resuming after them is not a second rescue. Out-of-memory follows A30. Late convergence is not promoted after the fact (section 3).
- **Conditional rescue of aIWO_2p0_s1 (pre-declared now; Codex: keep s1 on MV while it progresses).**
  - aIWO_2p0_s1 stays on MV 0.01 with its current settings while it progresses. Live at 13:12Z: 6 of 6 SCFs converged (111, 92, 85, 89, 49, 95 iterations), SCF 7 flat near 1.0-1.3e-7.
  - Trigger: an aIWO_2p0_s1 segment writes FAILED [scf] before 17 Oct 10:00 UTC.
  - Action: the A36 Gaussian-plus-aids route once, applied to that segment's relax_s<k>_bestvalid.in with the same two changed lines as aIWO_2p0_s2 (both lines checked to equal the current originals before the edit, and nothing else changed), installed per README_D24_BD section 3 and logged in the work chat before the next segment starts. The same one-attempt, gate, qualification, certificate and exploratory rules apply.
  - Consequences, accepted now: aIWO_2p0_s1 then has no MV-converged geometry. A15's 2.0 nm aIWO force check (MV 0.01 against Gaussian 0.005 at an MV geometry) becomes UNRESOLVED; C4 at 2.0 nm cannot be satisfied for s1; the H-N 2.0 nm endpoint is UNRESOLVED (see below). Its H-G, A15/A31 audit (fixed-geometry width comparison) and H-M roles continue on the Gaussian-family geometry, with the lineage disclosed.
- **C4 and H-N (Codex blocking point, resolved conservatively).** The register requires the 2.0 nm endpoint polish from an MV geometry (A27 C4), and the frozen reader requires certified polish for both 2.0 nm seeds (compute/amorph/analysis/compare.py:1272). A36 does not amend C4 eligibility and does not change the reader:
  - A Gaussian-rescued aIWO_2p0_s2 has no MV-converged geometry, so C4 cannot be satisfied for it. The A36 relaxation is not the C4 control and is never labelled as such.
  - The H-N 2.0 nm endpoint therefore stays UNRESOLVED whenever either 2.0 nm seed lacks a certified MV-to-Gaussian C4 polish; neither CROSSOVER nor NO CROSSOVER can be claimed from an A36 geometry. The cell's class is reported per cell, labelled "Gaussian geometry (A36); no MV geometry; C4 not satisfied".
  - aIWO_2p0_comp_s1 is not an H-N cell; its MV-plus-aids geometry keeps the registered family.
- **A15 force comparison.** A15's 2.0 nm aIWO check stays with aIWO_2p0_s1 (MV geometry) unless s1 is rescued (then UNRESOLVED, above). For aIWO_2p0_s2, a pre-declared diagnostic only: max |dF| over 792 components between s0 g2 (MV, continued SCF) and s1 g0 (Gaussian plus aids, fresh start); it mixes smearing and restart effects and is not the A15 check. comp: not applicable.
- **Restart reproducibility gate (A35 tolerances, frozen).** s1 changes settings, so its g0 is not compared with s0. From s2 on, at every restart, the first SCF of the new segment must reproduce the previous segment's value at the same geometry within 1e-5 Ry in F and 1e-3 Ry/bohr in max |dF| over all force components (792 for s2, 822 for comp). A failed gate does not stop the chain. Risk (ASSUMED): the s0 SCF-correction force norms are 0.65-1.85e-3 Ry/bohr at conv_thr 1e-7, so the gate may fail even when the SCF reproduces.
- **Qualification SCF at the final geometry (required for every A36 cell, whatever the number of segments).** As in A35: after 'bfgs converged', a fresh-start 'scf' run with forces at the final geometry with the cell's relaxation settings (s2 and a rescued s1: Gaussian 0.005 plus aids; comp: MV 0.01 plus aids; dipole correction, 60/480 Ry, same k-points, nbnd, nspin and split labels), compared with the relaxation's last SCF within 1e-5 Ry and 1e-3 Ry/bohr. A non-converged qualification fails; an infrastructure stop before the first energy may be repeated with an identical input. It needs its own submit with the user's go. The DAG FINAL (A26/A31) may run concurrently with the qualification; primary scoring waits for the qualification result (Codex).
- **Certificate binding and exploratory rule.** Copied from A35: gate and qualification evidence bound into the relaxation block with sha256; 'converged' requires A19, a passed qualification and no failed gate on the lineage; otherwise relaxation=exploratory (certify.py:218), inherited by descendants. An exploratory class is reported but does not count as resolved coverage.
- **Roles if a cell ends UNRESOLVED or exploratory.** aIWO_2p0_s2: H-N second 2.0 nm seed (already UNRESOLVED for H-N by the C4 point above), H-G 2.0 nm test cell, A31(f) named backup for aIWO_2p0_s1 in the A15 audit, H-M reference (mean host edge of s1 and s2). aIWO_2p0_comp_s1: H-G compensated-cell predictions, A15 audit cell (A31(a); no backup), final-SCF priority 1; not an H-N cell.
- **Disclosed: mixed relaxation smearing in the 2.0 nm W class.** aIWO_2p0_s1 MV 0.01 (Gaussian 0.005 if rescued); aIWO_2p0_s2 MV 0.01 for s0 (2 validated steps), then Gaussian 0.005; aIWO_2p0_comp_s1 MV 0.01 throughout (aids from s1). Every H-G, H-N and H-M table gives each cell's relaxation smearing and lineage. The FINALs are unchanged (A26/A31).
- **Sight history.** Read before A36: the s0 relax.out of aIWO_2p0_s2 and aIWO_2p0_comp_s1 (SCF energies, iteration counts, forces including total force and SCF correction, accuracy traces, positions of the Fermi-minimisation warnings, BFGS trust radii); aIWO_2p0_s1 s0 live (iterations, accuracy, forces; no energies); aIWO_0p8_s2 s3 live (allowed after A35). Not read: projections, PR_n, gaps, edges, Fermi energies. No FINAL exists for these cells. A36 is logged before any output of an A36 segment exists.
  - **Erratum (sight event, 2026-10-12, before any A36 segment output; Codex-reviewed wording 14:54Z; work chat 14:55Z).** The line "Not read: ... Fermi energies" above was wrong when written. Relaxation-SCF Fermi energies and KS band eigenvalues were parsed: team exposure at ~12:49Z, before A36 was committed (13:21Z), when a research agent ran a parser on copies of the relaxation outputs of aIO_2p0_s1 (s0, s1), aIWO_2p0_s2 (s0), aIWO_2p0_comp_s1 (s0) and the aIWO_2p0_s1 thread-test SCF (t1b), deriving the position of band nelec/2+56 relative to E_F (3.45-4.22 eV) for an nbnd proposal; main-session exposure at ~13:28Z, when Claude read those four derived values in the agent report. No projections, PR_n, gaps or edges were computed. The values informed no decision; the nbnd lever is dropped before the cutoff; the files are quarantined with sha256 (scratchpad quarantine_sight_20261012). This is a partial electronic unblinding for these 2.0 nm cells: every 2.0 nm H-G/H-N table carries a linked disclosure footnote; no blanket statement that no electronic quantity was seen is made; unchanged projection, PR_n and class tests are not automatically invalidated; later control cuts or scoring amendments acknowledge this sight history and preserve the original unresolved scores. No A36 physics change follows.
  - **Sight note (2026-10-13T21:34Z, during the A43 metadata fill; Codex classification 2026-10-13T21:47Z; disclosed in the A43 draft v4/v5 and the work chat 21:47Z).**
    - **What was read:** the segment_guard backup files on lxplus, to bind the s0 failure category of the two A36 cells:
      - aIWO_2p0_s2: `segment_guard.20261012T132139Z` (written 2026-10-12T09:57:56Z by s0, node job 12884203);
      - aIWO_2p0_comp_s1: `segment_guard.20261012T132140Z` (written 2026-10-12T09:38:54Z by s0, node job 12884378).
    - **Fields displayed on screen:**
      - the label `FAILED <utc> relax_s0 [scf]: SCF not converged (1x)`;
      - the D-24 geomsel summary on the same line: n_scf, n_geom, best index, best_new, **E0 and Ebest** (relaxation-SCF total energies of s0), the SCF iteration counts, scf_fail, and the count of Fermi-minimisation warnings (a count, not a value).
    - **Not displayed:** forces, Fermi energies, eigenvalues, projections or any other electronic quantity. No relax.out or driver log was opened.
    - **Classification (Codex):** re-exposure of relaxation-SCF totals already read before A36 (this section's first bullet), with no new electronic target unblinding.
    - **Consequences:** none. No physics or scoring amendment follows. The values are not used by any rule and are not copied into any record. The raw probe output was moved without reopening to `scratchpad/sealed/r35_a36_cat.out.SEALED` (sha256 041e4513cc5751dbb1a0da4d0490084e51b4e7d15b1be0b3cbdb2cd51afe0360); the probe script golist/r35_a36_cat.sh is kept.
- **Not changed.** H-G, H-M and H-N cells, observables, classes, thresholds and outcome rules; C4 and its eligibility; the frozen reader rc7; A15, A25, A26, A28, A31 and A35; the section 3 cutoff; the MV relaxation of every other aIWO cell.

### A37: H-N thick endpoint (2.0 nm) UNRESOLVED in every branch, by a formal reporting override; C2 and C5 cut (added after the freeze, 2026-10-13T00:10Z, before any H-N class of any cell has been computed, in particular before any 0.7 nm class exists; Codex GO-WITH-CHANGES 15:08Z, changes applied; user go 2026-10-13 ~00:05Z; decision D-42)

- **Scope.** H-N only: its thick endpoint, its control list, and how the registered outcome is reported.
  - No cell, observable, class, threshold, tolerance, outcome rule, series input or reader line changes.
  - The reader is rc7, unchanged.

- **Why.**
  - aIWO_2p0_s2 runs the A36 Gaussian route from s1 (installed 13:21:39Z, E). Its only MV segment (s0) never converged.
    - A36's one-attempt rule forbids any other smearing for it. So it can never have an MV-converged parent, and therefore never the A27 C4 polish ("polished by a Gaussian 0.005 relax, starting from its MV geometry", register:500).
  - No other 2.0 nm W seed exists. The H-N cell list names aIWO_2p0_s1 and s2 only; aIWO_2p0_s1_bare is a different termination and is parked (D-35).
  - The thick endpoint needs both seeds DONOR with C4 at 2.0 nm (register:442, 459-466). A36 already states the consequence for any seed without an MV-to-Gaussian polish (register:1016-1018).
    - A37 records that this holds **in every branch**: whatever happens to aIWO_2p0_s1 (MV convergence, conditional A36 rescue, cutoff), to the A15 audit, or to an extension of CERN access (A39(e)).
  - **No native-Gaussian eligibility amendment.** Codex 15:08Z: "Declining native-Gaussian eligibility is acceptable." Reasons:
    - the 2.0 nm relaxation-SCF Fermi energies and KS band eigenvalues of aIWO_2p0_s2 and aIWO_2p0_comp_s1 were parsed at ~12:49Z (A36 erratum). An eligibility change that restored a scorable endpoint for partially unblinded cells would be result-exposed;
    - it would need new certificate semantics and a versioned reader (rc8) after the rc7 freeze;
    - the seed pair would mix relaxation families (s1 MV, then polish; s2 MV for two steps, then native Gaussian). C4 exists to remove exactly this confound.
  - **Why an override and not an input filter (Codex 15:08Z).** "Prefer an explicit formal H-N reporting override, retaining both seed records and raw rc7 output as diagnostics. Do not manufacture missing coverage by filtering s2 out."
    - Filtering s2 out of the 2.0 nm slot would make rc7 print UNRESOLVED for the wrong reason ("1 given"). It would also hide a registered cell from the series.
    - The override states the actual reason: the endpoint cannot be scored. It leaves the reader's input and output intact.
  - **Controls.** CROSSOVER needs both 2.0 nm seeds DONOR with C4, and NO CROSSOVER needs DONOR at 2.0 nm (both seeds) with C4 (reader: register.py:69; compare.py:1319-1331). Both are therefore unreachable.
    - C2 and C5 appear only as "required for a crossover" (register:465-466) and, in the budget, "only if 0.7 nm is ECB or PARTIAL" (register:527). They serve no outcome that can still be scored.
    - Deciding them after a 0.7 nm class exists would be result-conditioned, so A37 decides now.
    - C1 and C6 at 0.7 nm are kept. They qualify the per-cell 0.7 nm class and the W-centred attribution of any ECB (A27: "checked against the C1 paired parent"). Both are reported whatever the series outcome. C1 is the D-28 0.7 nm control.

- **Rule.**
  1. **Endpoint.** The H-N thick endpoint (2.0 nm) is UNRESOLVED in every branch. Neither CROSSOVER nor NO CROSSOVER can be claimed.
  2. **Formal H-N reporting override.**
     - The registered H-N outcome is reported as **UNRESOLVED** in every branch, with the reason "2.0 nm thick endpoint UNRESOLVED (A36 C4 point; A37 override)".
     - The override acts on the outcome string only, and in one direction. It replaces whatever rc7 `hn_outcome` returns (CROSSOVER, NO CROSSOVER, SAMPLE-DEPENDENT, PARTIAL, UNRESOLVED) by UNRESOLVED. It never upgrades anything.
     - It changes no per-cell class, class_if_resolved, control status, sequence, bracket or note.
     - It applies to every `series` run listed in the D-43 F10 manifest: the MV-geometry series and the Gaussian (polished) series (A35:928-935).
     - The series specs are the registered ones. In each spec the 2.0 nm slot holds both registered W seeds:
       - aIWO_2p0_s1: the record of that series' geometry family (MV, or polished if certified 'polished');
       - aIWO_2p0_s2: its A36 Gaussian-lineage record.

       No seed is filtered out and no coverage is manufactured. A seed without a FINAL is MISSING, as rc7 reports it.
     - If rc7 returns INVALID, the inputs have a technical fault. It is logged, and the inputs are corrected only by a logged F10 addendum. The registered outcome stays UNRESOLVED.
  3. **Diagnostics retained.**
     - The raw rc7 `hn_outcome` output of every series run is committed with its self_sha256: outcome string, sequence, classes, controls, notes and unresolved checks.
     - It is reported verbatim in a row labelled "rc7 raw hn_outcome (diagnostic; not the registered outcome; A37 override)".
     - Both 2.0 nm seed records (`cell` outputs with self_sha256) are kept and reported per cell:
       - aIWO_2p0_s2 is labelled "Gaussian geometry (A36); no MV geometry; C4 not satisfied" (A36:1018);
       - aIWO_2p0_s1 is labelled with its lineage (MV; polished if certified; Gaussian if rescued under A36).
  4. **Cut, requirement kept.** C2 and C5 are not built and not run. Their registered requirement is not removed:
     - a CROSSOVER claim without them stays UNRESOLVED;
     - the reader keeps listing them (register.py:80; compare.py:1282-1283).

     The cut removes compute, not a requirement, so every original UNRESOLVED score is preserved. Also dropped: the nc_readout spin/H-N extension that C5 needed (register:513). Each H-N table lists C2 and C5 as "not run (A37 cut); requirement unmet".
  5. **Seed discrepancies at 2.0 nm (Codex: lineage-confounded).**
     - If the two 2.0 nm per-cell classes (or their class_if_resolved) differ, the difference is reported as: "lineage-confounded cell discrepancy at 2.0 nm: aIWO_2p0_s1 (<lineage>) reads X, aIWO_2p0_s2 (MV s0, then A36 Gaussian 0.005) reads Y".
     - It is never reported as seed dependence, sample dependence or the registered SAMPLE-DEPENDENT outcome. The two seeds differ in relaxation lineage as well as in quench, so the two causes cannot be separated.
     - If rc7 prints SAMPLE-DEPENDENT (compare.py:1268-1270, 1344-1345), that string appears only in the diagnostic row.
  6. **Reporting.** Every H-N table gives:
     - the registered outcome line (UNRESOLVED, A37 override);
     - the raw rc7 diagnostic row;
     - the line "2.0 nm endpoint UNRESOLVED (A36, A37)";
     - each cell's relaxation smearing, lineage and C4 status (A35/A36 disclosure);
     - spin at 2.0 nm "untested (C6 cut, A40 pending)";
     - footnote † on every 2.0 nm row.
  7. **Until A37 is logged.** Checks on any 0.7 nm FINAL (aIWO_0p7_s1 12902517, aIO_0p7_s1) are limited to exit status, the SCF convergence line, export completeness and sha256. No completeness statistics, no projections and no reader command (`cell`, `compare`, `series`).

- **Footnote †, fixed now (Codex 14:54Z), for every 2.0 nm H-G/H-N table and the claims table.** "† Partial electronic unblinding (register A36 erratum; work chat 2026-10-12T14:55Z):
  - relaxation-SCF Fermi energies and KS band eigenvalues of aIO_2p0_s1 (s0, s1), aIWO_2p0_s2 (s0), aIWO_2p0_comp_s1 (s0) and the aIWO_2p0_s1 thread-test SCF (t1b) were parsed by a research agent at ~12:49Z on 12 Oct (team exposure);
  - one derived quantity per cell (band nelec/2+56 relative to E_F, 3.45-4.22 eV) was seen by the main session at ~13:28Z;
  - no projections, PR_n, gaps, edges or classes were computed. These are relaxation-SCF quantities at earlier geometries and the relaxation smearing, not the FINAL read-out."

- **Check against the frozen reader (compare.py rc7, `hn_outcome`; line numbers as of 8a74a5e = HEAD).**
  - **CROSSOVER and NO CROSSOVER are blocked without C4 at 2.0 nm.**
    - Class patterns: 1319-1322. `pol` covers 2.0, 1.0 and 0.7 nm. A missing polish adds an unresolved check and sets clean = False (1323-1329). Both outcomes need all(pol.values()) (1330-1331).
    - `polished()` (1272-1275) requires every 2.0 nm record to be certified 'polished' with a Gaussian FINAL.
    - `certified_geometry` (219-220) trusts the certificate whenever the gate is VALID. certify.py:376-382 accepts 'polished' on any sha256-bound evidence.
    - So the reader enforces this only if no A36 geometry is ever certified 'polished'. The D-43 F9 checker (cert_assert.py) rejects 'polished' for aIWO_2p0_s2 by name. It also rejects it for any certificate without a genuine MV parent (tests: test_a36_cell_can_never_be_polished, test_parent_on_gaussian_rescue_lineage_is_not_mv).
  - **SAMPLE-DEPENDENT and PARTIAL are reachable without C4 when both seeds are in the slot.**
    - SAMPLE-DEPENDENT: 1268-1270, returned at 1344-1345 when clean. PARTIAL: 1349-1350. Neither checks C4 (or C3/C6) at 2.0 nm.
    - Both need every series class resolved. A qualification reason makes a class UNRESOLVED (readout.py:259-261), and certify.py:218-221 turns relaxation ≠ 'converged' or smearing ≠ 'qualified' into such a reason.
    - They can therefore fire only if the A15 audit gives a non-null provisional width and every series certificate passes F9 as smearing-'qualified' (A31(d), (e)).
    - In that branch the override reports UNRESOLVED, and the raw string is the diagnostic.
  - **Every other branch:** rc7 returns UNRESOLVED (1346-1348) or INVALID (1216-1220). The registered outcome is UNRESOLVED in all of them.
  - Expected cosmetic output:
    - the controls block lists C2/C5 as MISSING at 0.7 nm (1282-1283, 1310-1311);
    - C4 at 2.0 nm is listed MISSING (1286-1287);
    - C6 at 2.0 nm is listed MISSING (A40 cut, pending).

    These listings are correct and harmless.

- **Not changed.**
  - H-N cells, observables, classes, thresholds, outcome rules and the control table (the C2/C5 text stays).
  - C4 and its eligibility; the series inputs; the rc7 reader.
  - H-G and its historical scoring. aIWO_2p0_s2 keeps its H-G role on the Gaussian lineage (A36).
  - A15, A26, A31, A35, A36; section 3.

- **Sight history.**
  - **2.0 nm:** the partial unblinding in footnote †. A37 does not depend on it: it follows from A36's C4 point (Codex 13:15Z; A36 committed 13:21Z, after the team exposure and before the main-session exposure).
  - **1.0 nm:** the aIWO_1p0_s1 A26 FINAL post-run check read the minimum projection completeness (0.239) and the count of states below 0.90 (480) (work chat ~2026-10-11T23:4xZ). No class was computed.
  - **0.7 nm:** aIWO_0p7_s1 FINAL 12902517 was released at 12:59:08Z on 12 Oct. [At logging: state its status, and confirm that only blind checks were run.] aIO_0p7_s1 FINAL is done and has not been read by the reader.
  - **No H-N class of any cell has been computed or seen.**
  - Seen: C037 (MACE force check); thin-cell relaxation energies, forces and SCF traces.

**Section 5 row:**

### A38: the ML_VALIDATION 2 nm stop action is overridden; the trigger is kept and reported (result-informed amendment, added after the freeze, 2026-10-13T00:10Z, before any output of 12890593.0/.1 or of their A34 CPU fallback has been opened; Codex 15:08Z: B acceptable only as an explicit result-informed amendment; user go 2026-10-13 ~00:05Z; decision D-42)

- **Type: a result-informed amendment, not an erratum.**
  - It overrides the action in ML_VALIDATION.md:32, which was frozen on 2026-10-10 under D-12. Codex 15:08Z: "B overrides that action; it is not an erratum."
  - It is result-informed. When it was written, the following were already known:
    - (i) C037: MACE force check OVERALL FAIL on the bulk and 0.7 nm frames (13:05Z);
    - (ii) the progress, energies, forces and SCF behaviour of the aIWO_2p0_s1 relaxation from s0 on (A36 sight history);
    - (iii) probably the DFT half of the 'final' frame, if that frame is s0 g0 (identity check below);
    - (iv) the cost of a DFT anneal against the 17 Oct cutoff.
  - No output of either 2.0 nm frame exists or has been opened.
- **Superseded action (quoted; disclosed with every 2.0 nm result).**
  - ML_VALIDATION.md:32: "If the 2 nm slab fails badly (force RMSE > 0.3 eV/Å), its production run is stopped, and the slot is reused for a short DFT anneal of that slab."
  - Under A38 the production run is **not** stopped and **no** anneal is run, whatever the verdict.
  - The ML_VALIDATION file is not edited. The override is recorded in the register (this amendment) and in D-42.
- **Not overridden.**
  - ML_VALIDATION.md:28-31 (ordinary FAIL: "Production DFT relaxations continue (decision D-12)", the "starting points relaxed by DFT" wording, no ML-stage statistics) applies unchanged. Codex 15:08Z: "Ordinary FAIL permits continuation".
  - The comparator, its limits and C037 are unchanged.
- **D-12.** D-12 says "Production jobs are stopped if the parallel validation fails". The frozen criteria file of the same day refines this:
  - an ordinary FAIL continues (lines 28-29; current practice after C037);
  - only the > 0.30 eV/Å case stops (line 32).

  D-42 records that A38 overrides that stop clause for aIWO_2p0_s1, together with line 32. No erratum is claimed for either text.

- **Trigger (preserved; fixed before output).**
  - **Comparator.** compare_val.py as committed in d0179e1 (sha256 4ae21f152faba6c530de46206291a0670be2704016a4de0011bae29abe58a62d), run once on both frames together. Its output and sha256 are committed before any report.
  - **Metric.** D4 RMSE_all over all atoms and all 3 components, in eV/Å (25.711033738 per Ry/bohr, D1), at full precision.
  - **D8 as coded (compare_val.py:684-691):**
    - **TRIGGERED** if any SCORED frame of aIWO_2p0_s1 has RMSE_all > 0.30 eV/Å. One valid frame above 0.30 triggers even if its partner is MISSING, FAIL_NOT_SCORED or late.
    - **NOT_TRIGGERED** only if both frames are SCORED with RMSE_all ≤ 0.30.
    - **UNDETERMINED** otherwise: no SCORED frame above 0.30 and at least one frame not SCORED.
  - **Both frames are kept:**
    - 12890593.0: val_aIWO_2p0_s1_slab_annealed, 252 atoms, label-blind hash a73bd21d97e6;
    - 12890593.1: val_aIWO_2p0_s1_final, 270 atoms, label-blind hash 7989d9abbb80;
    - or their A34(i) CPU-fallback reruns of the same frames.

    No frame is dropped, whatever the identity check below shows. The exposure label is reported next to the verdict. It never changes the verdict.
  - MAE and RMSE_W1 never enter the trigger. They stay in the ordinary C037 PASS/FAIL.
  - **Cells.** The verdict concerns aIWO_2p0_s1 only, the structure the frames come from (STOP_STRUCTURE, compare_val.py:118).
    - It is not extrapolated to aIWO_2p0_s2, aIWO_2p0_comp_s1, aIWO_2p0_s1_bare or aIO_2p0_s1/s2.
    - Those cells share the potential and the protocol, and this is stated as relevant evidence wherever the verdict is reported.
  - **Deadline.** A frame with no result by 17 Oct 10:00 UTC is "not computed" (A34(i)). A single SCORED frame above 0.30 still gives TRIGGERED.
  - **Timing rule.** A38 is logged before either val_results.tar.gz is opened. If a frame returns earlier, only blind checks are made until A38 is logged: the job-log termination block, the exit code and the tarball sha256.

- **Action under A38 (replaces ML_VALIDATION.md:32).**
  - No chain is stopped and no anneal is run, in every branch.
  - **TRIGGERED** attaches a fixed limitation to every 2.0 nm result (H-G, H-K, H-M, the H-N per-cell classes, A39 read-outs) and to the claims table:
    - "The 2.0 nm networks were annealed with MACE-MPA-0, whose force RMSE on the aIWO_2p0_s1 frame(s) [tags, prior-exposure labels] exceeds the 0.30 eV/Å stop threshold of ML_VALIDATION.md:32.
    - The stop action of that rule was overridden by a result-informed amendment (A38).
    - The DFT relaxation removes residual forces at 0 K, but it does not re-sample the network topology; a possible topology bias remains uncorrected.
    - The 2.0 nm structures are DFT-relaxed ML starting points whose representativeness is not supported."
  - **UNDETERMINED:** "The 2.0 nm stop-rule check was not completed (frames: [status each]); topology representativeness at 2.0 nm is untested."
  - **NOT_TRIGGERED:** the ordinary C037 wording.
  - **Disclosure line, in every branch:** "ML_VALIDATION.md:32 stop action superseded by A38 (result-informed amendment, D-42); trigger computed as frozen: <verdict>."
- **Reasons for the override (stated as result-informed).**
  1. The remedy cannot be delivered before the cutoff (cost below). Applying the rule could only turn a possibly converging primary chain into an exploratory one.
  2. Stopping removes the only MV 2.0 nm W chain, with its A15 force check, A31 audit role and H-G s1 role. It would also treat seeds asymmetrically: s2, comp and the aIO cells share the potential but have no frames.
  3. D-12 runs production in parallel with validation, and ML_VALIDATION.md:30 already treats DFT relaxation as the correction ("starting points relaxed by DFT").
  4. The 'final' frame verdict is probably not blind (below), so a stop decision would partly rest on a number that has already been seen. This reason is itself result-informed.
- **Cost of the override, accepted openly.** If the rule is triggered, a possible topology bias remains uncorrected in the 2.0 nm structures. It is disclosed, not repaired.
- **What the superseded action would have done (formerly option A; not applied).**
  - segment_stop STOP armed in runs/aIWO_2p0_s1 within 1 h of a logged TRIGGERED.
  - The aIWO_2p0_s1 roles UNRESOLVED: H-G s1, the A15 2.0 nm force check, H-M (with s2), and the A31(a) audit role passing to the A31(f) backup.
  - A Born-Oppenheimer MD anneal needing its own amendment. Cost (A): about 0.7-1.5 GPU-h per MD step, so 70-150 h for 100 steps (0.1-0.2 ps). No anneal plus relaxation could finish before 17 Oct 10:00 UTC.
- **Priority.** The val CPU-fallback frames are CPU-4 (D-43 F7): below the primary FINALs and the 0.7 nm controls, before 17 Oct 10:00 only.

- **Geometry-identity check of the 'final' frame (blind; done and logged before A38 is logged).**
  - **Purpose.** Establish whether val_aIWO_2p0_s1_final (270 atoms) is the aIWO_2p0_s1 relaxation's starting geometry (s0 g0), whose DFT forces have been read.
  - **Inputs: input files only.** No output file (scf.out, relax.out, val_results.tar.gz, XML) is opened.
    - (a) the staged pw.x input of frame 12890593.1 (original labels), the file whose label-blind hash was logged as 7989d9abbb80 (A34(i), register:705);
    - (b) runs/aIWO_2p0_s1 s0 relax.in as submitted. If it is split-labelled, it is restored through the chain's A25 label map, and the restore is checked to be byte-identical with the logged original.
    - Both are read from the local archive copies with their sha256 recorded. CERN is not contacted for this check. If either file is not in the local archive, the check waits for the user's go to fetch it.
  - **Parser (allowlist).** Only these are kept:
    - nat;
    - the CELL_PARAMETERS block with its unit;
    - the ATOMIC_POSITIONS block with its unit;
    - the species label of each row, mapped to its element.

    Every other line is discarded unparsed and never printed. A deny assertion aborts on any line matching /Fermi|bands \(ev\)|highest occupied|lowest unoccupied|eigen/i; input files should contain none.
  - **Hashes, each computed on both files:**
    - **H1:** the A25 label-blind position hash, with the same script version that produced 7989d9abbb80 (its sha256 recorded);
    - **H2:** the rc7 geometry hash (certify.py:440-444): element species, Cartesian positions and cell in Å, each rounded to 1e-4 Å, canonical JSON, sha256. Units are converted with the cell first.
    - Also recorded: nat and the element-ordered composition.
  - **Default label (Codex 15:56Z).** Until the check is completed and logged, the 'final' frame is labelled **"UNDETERMINED, treated as exposed"** in every report, and that label applies if the verdict is reported before the check.
  - **Outcome and prior-exposure label of the 'final' frame after the check:**
    - **EXPOSED:** H1 and H2 both equal. The frame is s0 g0, and its DFT forces were read (A36 sight history). Its verdict is partly inferable.
    - **NOT_IDENTICAL:** H1 and H2 both differ, with the same nat and composition. Exposure of this geometry's DFT forces is not established.
    - **UNDETERMINED (treated as EXPOSED):** a file is unavailable, H1 and H2 disagree, or nat or composition differ.
  - **slab_annealed** (252 atoms, before passivation) has never been computed with DFT. Its label is "prior exposure: none".
  - The check computes no force, energy or RMSE estimate, and A38 does not estimate the 'final' frame's RMSE from the known residual forces.
  - Record: work chat line with both input sha256s, H1, H2, nat, composition, the label, and the UTC, logged before A38.

- **Not changed.**
  - The comparator and its limits; C037; the A34(i) route, pass rules and fallback (14 Oct 12:00 UTC trigger).
  - ML_VALIDATION.md (the file is not edited); every DFT setting.
- **Sight history.**
  - **Seen:** C037 (bulk and 0.7 nm frames, 13:05Z); aIWO_2p0_s1 relaxation forces from s0 on (A36 sight history; digest 13:12Z: largest component 5.88e-2 to 5.74e-3 Ry/bohr).
  - **2.0 nm frames:** no output exists. [At logging: confirm the state of 12890593.0/.1; 0 starts at 13:05Z.]
  - **'final' frame:** probably s0 g0 (identity check above). If so, the DFT half of its comparison has been seen.
  - The A36 erratum (footnote †, A37) is acknowledged. It concerns other quantities.

**Section 5 row:**

### A39: read-out rules at the 17 Oct 10:00 UTC cutoff: read-out geometry (A19 final geometry, or G* for exploratory chains), residual forces, a measured admission rule for the registered read-out route (no read-out otherwise), submission and hold semantics, export order and a non-discretionary extension rule (added after the freeze, 2026-10-13T00:10Z, before the cutoff and before any electronic quantity of a cutoff geometry exists; Codex GO-WITH-CHANGES 15:08Z and 15:56Z, changes applied; user go 2026-10-13 ~00:05Z; decision D-42)

- **Scope.**
  - Every relaxation chain of a registered cell that has not printed a verified 'bfgs converged' (A19) by 17 Oct 10:00:00 UTC. Expected (A): aIO_2p0_s1, aIO_2p0_s2, aIWO_2p0_s1, aIWO_2p0_s2, aIWO_2p0_comp_s1; possibly aIWO_0p7_s1_bare and aIWO_0p8_s2.
  - Also in scope: the qualification deadline for chains that converged before the cutoff, rule (a1).
  - **Not in scope:**
    - the H-L vacancy cells (A19/A20/A28);
    - the cut cells (1.5 nm, aIWO_2p0_Al2O3_s2);
    - aIWO_1p0_Al2O3_s2 (A34(ii): exploratory by scope, no FINAL route; its G* is recorded only);
    - C4 polishes (failure route in D-43 F5);
    - C1 paired cells (a paired relaxation not converged at the cutoff gives C1 UNRESOLVED).
  - A39 creates, rescues or promotes no primary test. Every G* output is an exploratory fallback under section 3.
- **Why.**
  - Section 3 says an unconverged relaxation is exploratory, and that "its final SCF and any relaxation eigenvalues used in its place" are exploratory fallbacks.
  - It does not say which geometry, which route or which order. Codex (04:19Z): "Freeze now: deterministic selection of exploratory cutoff geometries, residual-force reporting and export priority."

**(a) Read-out geometry.**

- **(a1) Converged chains (primary): the actual A19 final geometry.**
  - A chain counts as converged at the cutoff if it printed 'bfgs converged' (A19) at a time verified ≤ 17 Oct 10:00:00Z by rule (a3). Its read-out geometry is the final geometry of the converging segment: the 'Begin final coordinates' block, whose rc7 geometry hash the certificate binds.
  - G* is not computed for such a chain and never replaces that geometry (Codex: "Primary read-outs use the actual A19-converged final geometry").
  - Where A35/A36 (or D-43 F5 for C4 polishes) requires a qualification SCF, the chain is "converged pending qualification" until the qualification result exists. A qualification completed by 20 Oct 12:00 UTC is accepted only if both hold:
    - (i) 'bfgs converged' was verified before the cutoff;
    - (ii) no gate on the lineage has failed, own or inherited from any ancestor segment or parent chain (A35:926).

    If (ii) fails, the chain is exploratory immediately, and no qualification can restore it.
  - A failed or missed qualification gives relaxation=exploratory (A35). The read-out stays the FINAL at the A19 final geometry (the DAG FINAL may already have run, A36), labelled exploratory. G* is not used for it.
  - 'bfgs converged' printed after 10:00:00Z, or at a time that cannot be verified by (a3), leaves the chain in (a2). It is recorded, and there is no retrospective promotion.
- **(a2) Exploratory chains: G\*.** Only chains with no verified 'bfgs converged' by the cutoff get a G*.
  - **Validated evaluation.** An ionic configuration with a printed '!' energy (the free energy F of the smeared run) and a complete total-force block, as in the geomsel 5bfbae78 rule.
  - **Settings epoch.** A maximal run of consecutive segments with identical &SYSTEM, &ELECTRONS (max_seconds excluded), dipole keys, K_POINTS, cell, pseudopotentials and atom order. Only the chain's **last** epoch is used.
    - A25/A30/A34 label splits and D-41 segment lengths do not start an epoch.
    - The A35 epoch starts at aIWO_0p8_s2 s3. The A36 epochs start at s1 (aIWO_2p0_s2: Gaussian plus aids; aIWO_2p0_comp_s1: MV plus aids). A conditional A36 rescue of aIWO_2p0_s1 starts its own epoch.
- **(a3) Cutoff set C and timing verification (Codex: a later snapshot cannot establish that an evaluation preceded 10:00).** An evaluation of the last epoch enters C only if its print time is verified ≤ 10:00:00Z by one of:
  - **(i) Returned segment.** The segment that printed it ended by 10:00:00Z: the termination event (UTC) in the segment's HTCondor job log is ≤ 10:00:00Z.
  - **(ii) Pre-cutoff snapshot.** It appears in a running-sandbox snapshot of relax.out whose transfer **completed** at or before 10:00:00Z. The UTC comes from the NTP-synchronised local clock at transfer end and is recorded with the snapshot sha256.
    - Procedure: from 09:00Z, every running in-scope segment is snapshotted at intervals of ≤ 15 min, with the last snapshot started no earlier than 09:45Z. The latest snapshot completed ≤ 10:00:00Z counts.
    - **Execution approval (kept, Codex 15:56Z).** The snapshot session contacts CERN, so it runs only with the user's explicit go, given for that session. Without it, (ii) is unavailable, and only (i) applies.
    - Each snapshot is recorded as a small JSON {transfer_completed_utc} next to the snapshot file. Both are bound by sha256 in the F9 cutoff_selection record.
  - **Overhang.** An evaluation seen only in a later snapshot or in output returned after 10:00:00Z is excluded from C. It is listed separately in the (a) record as "overhang; pre-cutoff timing not verifiable" (F and the force summary only) and is never selected.
  - QE's in-file CPU-time lines, the start stamp and file modification times are never used to establish timing.
  - A segment lost without return contributes nothing.
  - (Optional, procedural.) segment_stop STOP is armed at 10:00Z. It ends the chain but proves no timing.
- **(a4) Selection, measured from the set minimum (Codex: global minimum, not pairwise).**
  - Duplicate evaluations (equal label-blind position hashes) are merged first, keeping the later one.
  - F_min = min F over C. T1 = {e in C : F(e) − F_min ≤ 1e-5 Ry} (the A25 tolerance).
  - f(e) = the largest Cartesian force component of e. f_min = min f over T1. T2 = {e in T1 : f(e) − f_min ≤ 1e-6 Ry/bohr}.
  - G* = the element of T2 with the latest lineage position (segment, then step).
  - Every tolerance is measured from a set minimum, never between pairs, so the selection is unique and order-independent.
  - Also recorded: L, the last evaluation in C, and g0, the first evaluation of the epoch.
- **(a5) No validated evaluation in the last epoch: no read-out.**
  - This applies even if an earlier epoch had validated geometries. Examples: a rescue epoch whose first SCF failed; aIWO_2p0_s1_bare.
  - The roles are UNRESOLVED with no exploratory number. The ML structure is never read out in their place.
- **(a6) Selection script (sight gate; allowlist accepted by Codex).** It reads relax.out from the returned tarballs and the (a3) snapshots in memory, through an **allowlist** filter that passes only:
  - '!' lines, and the first total-force block after 'Forces acting on atoms';
  - 'Total force' and 'Total SCF correction';
  - ATOMIC_POSITIONS block rows;
  - 'convergence has been achieved' / 'convergence NOT achieved', 'bfgs converged', 'End of BFGS' and 'JOB DONE'.

  Further rules:
  - The filtered stream is then checked against /Fermi energ|bands \(ev\)|highest occupied|lowest unoccupied/i. A match aborts the script with no output.
  - A denylist alone is not enough: the eigenvalue rows after a 'bands (ev)' header do not contain the header text.
  - The script never reads scratchpad\quarantine_sight_20261012\ or scratchpad\finishfast\scfspeed\data\.
  - Its source sha256 is committed before 17 Oct 10:00Z.
  - It writes one selection record per chain, committed with its sha256 before any read-out output is opened. The record holds the lineage, the epoch, C with energies, forces, hashes and timing sources, the overhang list, G*, L and g0.
  - **Implemented (draft v3).** This is the F9 writer `f9_writers.py cutoff_selection`. It uses the f9_common allowlist reader with its deny assertion, job-log or snapshot timing with explicit time zones, and the (a4) global-minimum rule.
    - Tested on synthetic fixtures: pre-cutoff snapshot counted; late snapshot and post-cutoff steps listed as overhang; duplicate geometries merged; the tie rule chooses the global-minimum set where pairwise chaining would not.
    - The checker re-derives the record before any certificate may cite it.
  - That record is the F9 'cutoff_selection' evidence of the certificate's relaxation block, with status 'exploratory'.
  - Relaxation eigenvalues are never used "in place of" a final SCF (the section 3 option is not taken).
- **(a7) After the cutoff.** segment_stop STOP is armed at 10:00Z in every unconverged in-scope chain. Exception: aIWO_1p0_Al2O3_s2, which continues under A34(ii). A35/A36 gate failures stay attached to G*.

**(b) Residual-force report** (every in-scope chain; converged chains are listed for comparison). Unchanged from v1:
- **For G\*, L and g0:**
  - '!' F;
  - the largest Cartesian component and its ratio to forc_conv_thr (1e-3 Ry/bohr);
  - the largest per-atom |F| and the RMS over 3N components;
  - QE's 'Total force' and 'Total SCF correction';
  - units Ry/bohr and eV/Å.
- **Per region on G\*:** surface, interior, H, and W plus first-shell O (section-1 regions, from positions only).
- **Trajectory:** the validated steps and segments; F of every validated evaluation; ΔF over the last three steps against etot_conv_thr; the last trust radius.
- **Descriptive bins** of the largest per-atom force (not a criterion): ≤ 0.026, ≤ 0.05, ≤ 0.10, > 0.10 eV/Å.
- **Wording:** "ML structure relaxed by DFT for N BFGS steps; residual largest force X eV/Å; not converged at the registered criterion."

**(c) Read-out route (v3: registered CPU route only; no automatic fallback).**
- **Route: the registered FINAL at G\*, only if admitted by the rule below.**
  - Settings: A26 Gaussian 0.001 Ry, 71/568 Ry, registered nbnd, QE 7.5 CPU, the A31(a) resources (-nk 1, 64 cores, 200 GB, 250000 s including in-job export), the A31(b) SCF path, original labels (A25), D-24 export with projections and planar averages.
  - Certificate: relaxation 'exploratory' (evidence: the F9 cutoff_selection record, (a6)); smearing 'pending'; geometry 'unknown'.
  - The reader then gives class UNRESOLVED with class_if_resolved, and withholds aligned edges (readout.py:259-261).
  - Converged chains are not A39 read-outs. Their FINALs are primary jobs under D-43 F7.
- **No automatic fallback (Codex 15:56Z).** If a read-out is not admitted, there is **no read-out**: its roles are UNRESOLVED with no exploratory number, and the residual-force report (b) is still given.
  - The v2 60/480 GPU fallback and its 1.0 nm bridge are withdrawn.
  - Any fallback would need its own amendment, logged before the cutoff, with a measured memory, runtime and export qualification.
- **Deadlines (Codex 15:56Z).**
  - Exploratory read-out artifacts must be complete, exported and sha256-verified off CERN by **20 Oct 18:00 UTC**, an 80 h window from the cutoff.
  - Primary qualifications and single-point controls stay due **20 Oct 12:00 UTC** (A27; A35/A36; (a1); D-43 F5).
- **Admission decision on 14 Oct (definitions frozen now; every input is measured at or before the decision time).**
  - Measurement window 14 Oct 06:00-12:00Z. The numbers and the sha256 of every raw command output are recorded in the work chat by 12:00:00Z, and they are not revised later. The measurements contact CERN, so they run only with the user's execution approval.
  - **S (slots).**
    - A held probe job with exactly the A31(a) request (64 CPUs, 200 GB, MaxRuntime 250000 s, the same Requirements and accounting group) is analysed with `condor_q -better-analyze <probe>` at 06:00, 09:00 and 12:00Z.
    - S = the minimum over the three of the number of slots reported as available to run the probe. The probe is removed afterwards, well inside the 24 h hold limit.
  - **P (primary CPU load).** P = the number of D-43 F7 CPU-1 to CPU-3 jobs not completed at 12:00Z, counted from the F7 list.
    - This counts listed jobs that may never be needed, such as an unused A31(f) backup.
    - It is an upper bound known at decision time.
  - **q (queue wait).** Measured from the HTCondor job logs of our CPU jobs requesting ≥ 34 CPUs, submitted or released since 12 Oct 00:00Z:
    - a started job's wait = first execute event − last submit-or-release event;
    - a job still idle (not held) at 12:00Z has wait = 12:00Z − that event (a lower bound).
    - q = the larger of the median started wait and the largest current idle wait. With no such job, q = 24 h (A, conservative).
  - **T (conservative runtime; kept, Codex 15:56Z).**
    - If a 2.0 nm CPU FINAL with the A31(a) request has completed by 12:00Z: T = 1.25 × its longest wall time (execute to terminate event).
    - Otherwise: T = 69.44 h, the A31(a) runtime limit, which includes in-job post-processing and export.
  - **X (export allowance; kept).** X = 6 h for transfer off CERN (AFS route or the D-24 puller) and sha256 verification (A, conservative; (d)).
  - **Rule.**
    - CPU admission requires **q + T + X ≤ 80 h** (17 Oct 10:00Z to 20 Oct 18:00Z) and T ≤ 69.44 h.
    - If admitted: the first max(0, S − P) read-outs in the order below are admitted, and the rest get no read-out.
    - If not admitted: no read-out for any chain.
    - No complete record by 12:00:00Z: no read-out. The rule is never applied to unmeasured inputs.
  - **Consequence, stated now.** With no completed 2.0 nm CPU FINAL by 14 Oct, T = 69.44 h and X = 6 h, so admission needs q ≤ 4.56 h.
- **Order** (section 3 FINAL priority). These read-outs rank after every primary CPU FINAL (D-43 F7):
  1. aIWO_2p0_comp_s1
  2. aIWO_2p0_s1
  3. aIO_2p0_s1
  4. aIWO_2p0_s2
  5. aIO_2p0_s2
  6. aIWO_0p7_s1_bare
  7. aIWO_0p8_s2
- **Submission, holds and release (Codex 15:08Z and 15:56Z; HTCondor condor_release; CERN removes jobs held for more than 24 h).**
  - The removal rule is given by the coordinator and Codex (A). Its exact lxplus expression is read (`condor_config_val SYSTEM_PERIODIC_REMOVE`, or the CERN batch documentation) with the user's approval before 14 Oct.
  - **New submission.** 18 Oct 22:00Z is the last submission (section 3). A new submission is any new HTCondor job (new cluster or proc). This includes every node job that DAGMan submits: RELAX and FINAL nodes, RETRY attempts and rescue-DAG nodes.
  - **Default: submit idle, not held.** An admitted read-out is submitted **idle**, with its final input (the G* geometry and settings, after the (a6) record is committed), at the CPU-5 JobPrio, before 18 Oct 22:00Z. JobPrio, not a hold, keeps it behind the primary jobs.
  - **Release exception (unchanged held job).** A job held at any time (hold expression, out of memory, or the user) and released within 24 h of its hold event is not a new submission, before or after 18 Oct 22:00Z, if it is unchanged:
    - same cluster.proc;
    - no condor_qedit of arguments, environment, transfer-input list, Requirements or resource requests;
    - input sha256 at release equal to those recorded at submission.

    condor_release only changes a held job to idle. An eviction that returns a job to idle is likewise not a submission.
  - **Removed jobs.** A job removed by CERN's 24 h rule (or by anyone) cannot use the release exception: its job ad no longer exists.
    - Replacing it is a new submission, allowed only before 18 Oct 22:00Z, with identical input and logged as a resubmission.
    - After 18 Oct 22:00Z a removed read-out is lost: UNRESOLVED with no number.
    - Every hold event is logged with its UTC and its removal deadline (hold + 24 h). A job held at or after 17 Oct 22:00Z must be released before its deadline, because no resubmission is possible once the deadline passes 18 Oct 22:00Z.
  - A DAG node that DAGMan would submit after 18 Oct 22:00Z (a retry, a rescue node or a FINAL node) is a new submission and is not allowed, unless (e) moved the date before it passed.
- **Deadline.** Complete, exported and sha256-verified off CERN by 20 Oct 18:00 UTC; otherwise UNRESOLVED with no number.
- **Failure.** Out of memory or eviction: one repeat with identical input. It is done as a release of the same job (within 24 h of a hold) or the eviction's own return to idle, or as a resubmission only before 18 Oct 22:00Z. No other smearing, mixing, cutoff or band change.
- **Sight.** No observable of a cutoff read-out is opened before all of:
  1. A39 is logged;
  2. the (a6) record is committed;
  3. the cutoff has passed and (e) has been applied or has lapsed.

  Blind completion checks are allowed: exit status, convergence line, export hashes, memory, timing. Every 2.0 nm table carries footnote † (A37).

**(d) Export order.**
- The A14 list is unchanged. Everything must be verified off CERN by 20 Oct 18:00 UTC.
- **A14 gaps are preserved.** An item missing from an export stays recorded as a gap in the export manifest and in every report that uses the run (e.g. aIO_0p8_s1 12904001 "A14 INCOMPLETE"). A gap is never filled from another run or by reconstruction.
- **Routes:**
  - HTCondor output transfer to AFS is the primary route (it works without a credential; Codex 14:54Z: essential);
  - the in-job EOS copy only while the credential is valid (the stored renewal chain ends 15 Oct 09:26Z, D-35);
  - the D-24 puller, which needs the user's ticket.
- **AFS verification (mandatory; Codex 15:08Z).**
  - Before P1, a test file of known sha256 is sent through HTCondor output transfer to the AFS target and verified off CERN.
  - `fs listquota` on the AFS target is recorded daily from 14 Oct.
  - Every transferred file is sha256-verified off CERN, and a transfer counts only after that verification.
  - AFS has a 2 GB quota: keep ≤ 1 GB pending. A file that would exceed the quota goes by the puller, or by EOS while the credential is valid.
  - **Export sizes (Codex 15:56Z: verify before freezing).** Before 17 Oct, the per-run export size of each run type is taken from existing completed exports. These are file sizes only (thin-cell FINAL, 2.0 nm FINAL with charge density, PDOS tarball), read from local archive listings; no content is opened.
    - The sizes are compared with the AFS quota and the ≤ 1 GB pending rule, and each run type is assigned its route.
    - The table is logged with the replacement hashes of F9 (D-43 F13).
- **Order:**
  - **P0 (daily, now):** every chain's relaxation lineage (segment tarballs, bestvalid files, lineage, release and reset logs, guard archives, DAG logs) and the HTCondor job logs used for timing (a3).
  - **P1 (cutoff + 1 h):** the snapshots and the (a6) records, also committed to the private repo.
  - **P2 (as each completes):** FINAL exports of converged cells in priority order, then the cutoff read-outs in (c) order.
  - **P3:** the 2.0 nm charge densities (A14).
  - **P4:** PDOS tarballs, bridge sets and val-frame outputs.
  - **Never:** wavefunctions.
- On the laptop keep ≥ 10 GB free. Small files go to the private repo (≤ 50 MB each), never to the public repo before publication.

**(e) Extension rule (non-discretionary).**
- **Trigger.** A written CERN confirmation of a later access end date (e-mail or ticket text saved with its sha256, personal data redacted), logged in the work chat **before 17 Oct 10:00:00 UTC**.
- **Effect.** Every registered date not yet passed at logging moves by the same Δ = (confirmed end date − 21 Oct), in whole days, rounded down:
  - the relaxation cutoff (section 3 and every amendment citing it: A23(i), A28, A31(f), A34, A35, A36, H-N budget);
  - 18 Oct 22:00 (last submission);
  - 20 Oct 12:00 (primary single points and qualifications);
  - 20 Oct 18:00 (export, and the exploratory read-out deadline of (c)).
- **Never revives (Codex 15:08Z).** The shift moves only dates. These stay as they are:
  - a chain that wrote FAILED [scf] under a one-attempt rule (A28, A35, A36, D-43 F5);
  - a failed or missed qualification;
  - a failed gate (inherited by descendants);
  - a parked or cut chain;
  - any UNRESOLVED fixed before the logging.

  No new rescue, no revived or new cell, no threshold change. A chain that converges by the shifted cutoff is converged under the unchanged rules.
- **A confirmation logged after the cutoff** does not move the cutoff.
  - It extends only the dates not yet passed for finishing and exporting read-outs of geometries fixed at the cutoff (G* and converged cells), their single-point controls and qualifications, and export.
  - Chains may continue only to report residual forces. 'bfgs converged' after the cutoff gives one registered FINAL, reported as "converged after the cutoff (exploratory)" next to the G* read-out, which stays the designated read-out.
- **Administrative rescue DAG (frozen budget; Codex: continue the same route after retry exhaustion).**
  - **Trigger.** A live chain's DAG has exhausted RETRY RELAX 8 with its last segment CONTINUE, or with a resumed non-[scf] D-24 category.
  - **Action.** One HTCondor rescue DAG may be submitted for that chain, **once in total per chain**: not once per extension, and not renewed by any extension. It is the existing .rescueNNN with identical submit files, relax.in lineage and driver.
  - **Frozen budget (Codex 15:56Z).** At most **9 additional RELAX node executions** per chain in total: the rescue DAG keeps RETRY RELAX 8 unchanged, giving one first execution plus 8 retries. No second rescue DAG; no edit of RETRY.
  - **No revival of terminal failures.** The rescue DAG is allowed only for retry exhaustion of a live chain whose last segment is CONTINUE or a resumed non-[scf] D-24 category. It is never used after:
    - FAILED [scf] under a one-attempt rule (A28, A35, A36, D-43 F5);
    - a failed or missed qualification;
    - a failed restart gate;
    - parking;
    - a cut.
  - It continues the same route: same smearing, settings and epoch. It is administrative (a retry resource), not a rescue under A35/A36/F5, and it resets no one-attempt rule. Segment numbering is handled as in A28.
  - Every rescue-DAG node is a new submission. RELAX nodes are allowed only before the (possibly shifted) cutoff, and any node only before the (possibly shifted) last-submission date.
  - Logged per README_D24_BD section 3.

- **Consequences already fixed elsewhere (stated, not changed).** A15/A31: without a converged 2.0 nm role (A31(f)) the candidate is null, so every smearing block stays 'pending' and every DFT registered status is UNRESOLVED, with conditional values reported. H-G, H-K and H-M are then UNRESOLVED; the 2.0 nm part of H-H is UNRESOLVED (D-35); H-I is UNRESOLVED (A34); the H-N endpoint is UNRESOLVED (A37).
- **Not changed.** Section 3; A14; A15; A19; A23-A31; A34-A37; every hypothesis, threshold, class and tolerance; rc7.
- **Sight history.**
  - The 2.0 nm partial unblinding (footnote †; A36 erratum). A39 does not depend on it: no rule here uses an electronic quantity.
  - 2.0 nm relax.out files have otherwise been parsed for energies, forces, SCF traces, timing and memory.
  - 1.0 nm completeness statistics (A37). No class of any cell has been computed.

**Section 5 row:**

### A40: C3 width companions (Gaussian 0.002 and 0.005 Ry against the A26 0.001 Ry reference), fresh-start eligibility, zero-step polish reuse, and the 2.0 nm C3/C6 scope (added after the freeze, logged 2026-10-14T10:35Z, before any companion has run; no reference FINAL has been read by `cell`; the reader (rc7 certify/validate-cert loader) performed restricted machine parsing of the seven thin/bulk reference FINALs under A44 on 2026-10-14 (provenance binding; only validated hash, provenance and status fields shown; nothing electronic printed or viewed);Codex 15:08Z: A40, policy GO on draft v5 2026-10-12T20:44Z; user go: 2026-10-13 ~04:15Z item 2 (log D-43 and A40 after the metadata audit); decision D-43)

- **Scope.**
  - The C3 control (A27) for the cells in the table below.
  - The comparison is the A26 Gaussian 0.001 Ry reference FINAL against Gaussian 0.002 and 0.005 Ry companions at the same geometry. These are the pending widths while the A15 audit is pending (register.py:96-97; compare.py:447).
  - The reader binds C3 to a 0.001 Ry cell only when **both** widths pass (compare.py:1169-1179).
  - The A15 audit itself (A31(a)-(d), including its A31(b) fallback) is unchanged. A40 changes only what counts as C3 evidence.
- **Why an amendment.** Excluding density-seeded runs from counting changes which comparisons are eligible: for the series C3 control, for the A31(e) common width, and for the D-42 F9 'qualified' assertion. That is a rule change.
- **Rule.**
  0. **Frozen slots and one log per slot (v4; F9 inventory, Codex 20:25Z).**
     - Before any companion is submitted, every C3 slot (cell, geometry hash, width) is listed in the frozen F10 C3 plan.
     - Every attempt for a slot, fresh or an A31(b) density-seeded fallback, is submitted with that slot's single HTCondor user log.
     - Each attempt's inputs and outputs are exported with a sha256 manifest that also contains its certified run files.
     - F9 derives the inventory from the plan, the logs and the reports. An unaccounted attempt, a missing report or a stray report makes the inventory underivable, and the cell then cannot be qualified.
  1. **Identical settings except degauss.**
     - Each companion input is the reference's as-run input (from its A14 export) with exactly one changed physical line: degauss = 0.002 or 0.005.
     - Everything else is identical: smearing 'gaussian', the explicit nbnd value, cutoffs, k-mesh, conv_thr, mixing line, dipole keys, pseudopotentials (sha256 via lineage), original element labels, QE build (7.5 CPU), -nk 1 and the D-39 resources.
     - Only the prefix, outdir and job names may also differ.
     - A diff gate prints the changed lines and the md5 of both inputs. Any other difference blocks submission. The gate result is written into the companion's F9 'c3_companion_run' record (changed_physical_lines = ['degauss']).
     - Export: D-24, with projections and, for slabs, planar averages.
  2. **Fresh start; density-seeded runs are reported, not counted.**
     - Fresh start means startingpot and startingwfc at their defaults, an empty private outdir, and no copied density or wavefunctions. It is recorded as start_mode 'fresh'.
     - If the SCF does not converge, the A31(b) fallback is allowed once: a new SCF from a converged sibling width's density, sibling order as in A31(b). The run is then labelled **'density-seeded'** (start_mode 'density-seeded').
     - A density-seeded comparison is computed and reported as "<status> (density-seeded; reported, not counted)". It is excluded from fresh-start qualification:
       - it does not count towards the series C3 control. It is not listed in the `series` controls, so its width counts as MISSING (compare.py:1175-1178);
       - it does not count towards the A31(e) common width;
       - it does not count towards the F9 'qualified' C3 coverage.
     - Reason: finding E (A35) shows that distinct SCF branches are possible in W cells. Seeding from a sibling may carry its branch over and bias the comparison towards agreement.
     - The same counting rule applies to A15 audit runs reused as C3 (item 7): an audit run that used the A31(b) fallback is density-seeded for C3 counting. The audit outcome itself is unchanged.
     - **Both endpoints (v5; Codex 20:44Z).** A comparison counts only if BOTH the 0.001 Ry reference and the companion are fresh starts, each derived from the as-run scf.in recorded in its certified lineage file. A density-seeded reference, including an audit run that used the A31(b) fallback, is reported, not counted.
     - **Attempts without output (v5).** Every attempt in a slot's user log must have its report, or a terminal event showing it failed (non-zero exit, signal, abort). A job that ended normally without its output, or one with no terminal event, blocks the cell's qualification. [F9 v6 tightens this: digest_13oct_v6.md, blocker 1.] [F9 v7: the attempt's slot is UNRESOLVED and only that cell and geometry are blocked; D-43 wording in Release_decision.md item 1 (Codex GO, prospective).]
     - **A density-seeded FAIL still blocks (v3, new; F9).** A density-seeded comparison never counts towards a PASS. A FAIL, fresh or density-seeded, blocks the smearing qualification of that run at every width. Seeding biases towards agreement, so a disagreement despite it is informative.
  3. **Geometry. C3 qualifies only the geometry it was run on (Codex 15:56Z).** A C3 comparison applies to a run only if its reference and compared runs share that run's geometry hash. F9 enforces this from the complete C3 inventory (test_mv_geometry_not_qualified_by_polished_c3). Polished-geometry comparisons therefore never qualify a moved-from MV geometry.
     - W cells at the C4 endpoints and at 1.0 nm use their **C4-polished** geometry for the H-N reading, so each needs a polished 0.001 Ry reference FINAL plus two companions.
     - **MV geometry used as the 0.7 nm H-H reference (Codex 15:56Z: retain, or leave H-H unresolved).** H-H at 0.7 nm compares MV geometries (D-42 F6): aIWO_0p7_s1 at its MV geometry (A26 FINAL 12902517) against aIWO_0p7_s1_bare.
       - The MV-geometry companions 0.002 and 0.005 Ry of aIWO_0p7_s1 are therefore **retained** (table below), as are those of the bare cell.
       - If either cell lacks fresh C3 PASS at both widths on its MV geometry by 20 Oct 12:00 UTC, **H-H 0.7 nm is UNRESOLVED**, stated explicitly.
       - If the 0.7 nm polish converges in zero steps (rule 4), the polished and MV geometries are the same geometry, so one companion set serves both.
     - Other MV-geometry FINALs (aIWO_1p0_s1 MV) stay C4 "class on the MV geometry" reports and get no C3.
     - aIO cells, aIWO_bulk_s1 and aIWO_0p8_s2 use their own Gaussian 0.005-relaxed geometries (A15, A23, A35).
     - **Native-Gaussian exception: aIWO_2p0_s2 (stated explicitly, Codex 15:56Z).** It has only its A36 Gaussian-lineage geometry: no MV-converged geometry, and it is never polished (A36, A37).
       - Where its C3 is needed for primary qualification (item 7), it runs at that native Gaussian-lineage geometry, and only if the cell is relaxation-converged and A36-qualified.
       - It is labelled "Gaussian geometry (A36); no MV geometry; C4 not satisfied". This is the second exception to the polished-geometry rule, alongside aIWO_0p8_s2 (A35).
  4. **Zero-step polish reuse (Codex 15:08Z).** The existing A26 FINAL may serve as the polished 0.001 Ry reference, with no new FINAL, only if all of the following hold. Otherwise a new polished FINAL runs.
     - (i) **Actual converged polish.** The polish printed 'bfgs converged' (A19) at a verified time ≤ the cutoff, with zero ionic steps.
     - (ii) **Exact geometry identity.** The rc7 geometry hash of the polish final geometry equals that of the MV parent's final geometry and the existing FINAL's certified geometry.
     - (iii) **Exact settings identity.** (F9 v9: every FINAL used for a positive certificate, not only a reused one, must match the registered FINAL template of its cell apart from the width; the template keys are frozen in f9_common.REGISTERED_FINAL_TEMPLATES before use.) The existing FINAL's as-run input equals the A26 polished-FINAL template for that cell except prefix, outdir and job names: the diff gate of rule 1 with zero changed physical lines. The settings sha256 is pinned in the reuse record.
     - (iv) **UPF identity.** The sha256 of every UPF of the polish and of the FINAL are equal, equal to the run lineage, and equal to the certificate's pseudopotential block.
     - (v) **Fresh final-geometry qualification.** The D-42 F5 qualification SCF of the polish has passed. Zero-step cases are included.
     - (vi) **Newly bound polish evidence.** A new certificate of the existing FINAL binds the polish record (C4 record, polish lineage, qualification and reuse record) in its geometry block.
       - The old certificate is superseded.
       - Every cell record and comparison bound to the old certificate is recomputed (D-42 B.2b).
       - F9 checks (i)-(vi): cert_assert.py tests test_zero_step_polish_reuse_passes, test_settings_identity, test_upf_identity, test_reuse_needs_actual_converged_polish, test_zero_step_polish_still_needs_qualification.
  5. **Cells (thin and bulk).**

     | Cell | Geometry | 0.001 reference | Companions |
     |---|---|---|---|
     | aIO_bulk_s1 | A23 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIWO_bulk_s1 | A23 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIO_0p7_s1 | A15 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIO_1p0_s1 | A15 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIO_0p8_s1 | A15 Gaussian | 12904001 (running; A14 INCOMPLETE disclosed and preserved) | 0.002, 0.005, after it completes |
     | aIWO_1p0_s1 | C4 polish (12904173) | new polished FINAL, or the existing one under rule 4 | 0.002, 0.005 |
     | aIWO_0p7_s1 | C4 polish (12904172) | new polished FINAL, or the existing one under rule 4 | 0.002, 0.005 |
     | aIWO_0p8_s2 | A35 Gaussian | its FINAL, only if converged and A35-qualified | 0.002, 0.005 |
     | aIWO_0p7_s1 (MV geometry; H-H reference, v3) | MV (A26 FINAL 12902517) | existing (12902517) | 0.002, 0.005 (shared with the polished set if the polish is zero-step) |
     | aIWO_0p7_s1_bare | MV geometry (H-H: MV geometries; FINALs Gaussian 0.001, D-42 F6) | its FINAL, only if converged | 0.002, 0.005 |

     - Count: up to 20 companions plus 2 polished references (A: each about the reference's measured wall time; to be filled in from the job records).
     - Order: 0.7 nm (aIWO_0p7_s1 polished, aIO_0p7_s1, aIWO_0p7_s1 MV), then 1.0 nm, 0.8 nm, bulk, then bare.
     - Deadline: every run complete and exported by 20 Oct 12:00 UTC (H-N single points). Otherwise that width is MISSING.
     - The runs are blind computations. They may be submitted before the D-42 release, and their outputs are read only after it.
  6. **Comparison and tolerances (unchanged).**
     - One `compare c3 <ref> <other>` per width, without --audit-width while A15 is pending.
     - The reader refuses: a geometry-hash mismatch (450-451); differing functional, cutoffs, k or lsda (452-454); a self-comparison (441-442).
     - Pass criteria (register.py:70-71): the class is unchanged; edges move ≤ 0.05 eV (absolute host and valence edges, Δ_W, E_F − host edge, host gap); fractions move ≤ 5 percentage points on interval bounds.
  7. **2.0 nm C3 and C6 (Codex 15:08Z).**
     - **Audit cells: reuse, no duplicate runs.** The A31(a) audit runs (0.005, 0.002 and 0.001 Ry at fixed geometry on the audit roles) are the 2.0 nm C3 comparisons of those cells. `compare c3` is run on the audit outputs (0.001 against 0.002, 0.001 against 0.005). No companion is run for an audit cell.
     - **Non-duplicated 2.0 nm C3 needed for primary qualification is kept.** It applies to a relaxation-converged (and, where required, qualified) 2.0 nm cell outside the audit whose 0.001 Ry FINAL needs the A31(e) common-width route: aIWO_2p0_s2 and aIO_2p0_s2 when they are not A31(f) backups.
       - Such a cell gets companions 0.002 and 0.005 at CPU-6 (D-42 F7).
       - An unconverged cell gets none: it cannot be primary.
       - The exact list is fixed in the F10 manifest after the A31(f) role decision at the cutoff, from relaxation status only.
     - **2.0 nm C6 is cut** (it served only the unreachable H-N endpoint, A37).
       - Its requirement text is kept: C6 at 2.0 nm is listed MISSING by rc7, and any claim needing it stays UNRESOLVED.
       - Every 2.0 nm H-G/H-N row states "spin robustness: untested (C6 cut, A40)".
       - C6 at 0.7 nm (and 1.0 nm, reported) is unchanged.
  8. **Labels.**
     - A cell with fresh C3 PASS at both widths is reported as **"width-robust within C3 tolerances, cell-local; A15 not met"**. Its C3 quantities and class_if_resolved do not change between 0.001 and 0.005 Ry at this geometry.
     - That label is not a smearing qualification. It does not transfer to another cell, does not resolve any class, and does not meet A15 (the 2.0 nm audit, which also needs EA). On its own it does not meet A31(e), which also needs a non-null A15 candidate.
     - **A cell-local C3 PASS while the class stays UNRESOLVED is legitimate** (Codex 15:08Z). The C3 status and the class status are reported side by side, and neither is inferred from the other.
     - C3 FAIL at any width gives "width-sensitive (C3 FAIL at x Ry)", and the affected quantities are UNRESOLVED.
- **What the frozen reader will show.**
  - **Certificates.** The smearing block stays **'pending'** for every cell unless the A15 audit gives a non-null candidate and A31(d)/(e) are complete, as checked by F9 (cert_assert.py).
    - C3 reports alone never qualify (F9 test test_c3_alone_never_qualifies).
    - certify.py:357-375 would accept any sha256-bound file with a matching numeric width. The semantics are enforced by F9 before `cell`.
    - Consequence: every class stays UNRESOLVED with "smearing qualification pending (A26/A15; not certified)" (certify.py:220-221; readout.py:259-261). class_if_resolved is reported.
  - **C3 statuses** can still read PASS or FAIL. c3 calls tolerance_compare with drop_smearing=True (compare.py:457, 393-394), and compares class_if_resolved (400-403).
    - Other qualification gaps (relaxation not converged, flagged states) make the status UNRESOLVED unless an item fails (421-426).
  - **Series.** control_status gives C3 'PASS' for a 0.001 Ry cell when both widths pass, without checking the smearing qualification in that role (1169-1179). So the series controls table can show C3 PASS while every class is UNRESOLVED. This is expected, legitimate and reported as such.
- **Not changed.** C3 tolerances, roles and the self-comparison rule; A15 and the A31 audit (including its fallback); C4; C6 at 0.7 and 1.0 nm; rc7.
- **Sight history.**
  - No reference FINAL has been read by `cell`. A44 (2026-10-14) performed restricted machine parsing of the seven thin/bulk reference FINALs (rc7 certify/validate-cert, provenance binding; no electronic quantity printed or viewed). The aIWO_1p0_s1 completeness statistics are known (A37).
  - No 0.002 or 0.005 Ry slab FINAL exists.
  - The 2.0 nm partial unblinding (footnote †) concerns the 2.0 nm cells of item 7, whose rows carry †. It does not concern the thin or bulk cells.
- **As-of note at logging (facts only; no rule change).**
  - References in this entry to "D-42 F<n>", "D-42 B.2b" and "the D-42 release" mean the release decision, now numbered D-43 (D-42 row: "References in A37-A39 to release-decision items ... point to the release decision, now numbered D-43").
  - aIO_0p8_s1 FINAL 12904001 has completed (exports verified; A14 INCOMPLETE disclosed and preserved).
  - The C4 polishes 12904172/12904173 named in the table were removed in the 13 Oct full stop and resubmitted under A43 item 6 as 12920318 (aIWO_0p7_s1) and 12920319 (aIWO_1p0_s1); the removed IDs never count as attempts. At logging (10:35Z): 12920318 finished (reported CONVERGED, exit 0, 2244 s, relax_s0_results.tar.gz returned, ~10:31Z; not yet verified by F9); 12920319 started 10:33Z. No qualification SCF has been submitted (it needs its own user go, D-43 F5).
  - Sight (corrected per Codex 2026-10-14): the frozen text said "No reference FINAL has been read by the reader". The A44 audit performed restricted machine parsing of the seven thin/bulk reference FINALs, so the heading and the sight-history line now say so.
- **Source.** Verbatim from compute/amorph/f9_checker/C3_protocol.md (frozen, D-47; sha256 1af4908f325e43aefa216daf2857245464f2726876852358f3ad2f3bc7ad3d22), lines "### A40" to the section 5 row; only the heading fill, the corrected sight-history line and this as-of note differ.

### A41: S2 resolution-method sign-off; one rerun of S2-11 with the fixed runner; S0-02 DOS x2 resolution run; frozen trigger for matched oxide-mesh refinements (added after the freeze, 2026-10-13T02:16Z, after run_0075 (sealed, invalid for scoring) and before any output of the S2-11 rerun or of S0-02-DOS2 exists; disclosure: "S1-informed operational method; S2 blinding cannot be demonstrated; possibly exposed; not viewed according to the user's statement" (Codex 2026-10-13T01:32Z item 6; the same S2-11 deck's output was displayed on screen 2026-10-12 15:14Z/15:19Z, before the method sign-off, Codex D7; user statement D-42 (3)); Codex: scorer GO to freeze 16:08Z, adaptive amendment recommended in round 3 (15:50Z), GO-WITH-CHANGES on this text 2026-10-13T01:32Z, changes applied in revision 3; user go 2026-10-13 ~00:05Z (work chat 00:15Z), subject to Codex review; decision D-44)

- **Scope.**
  - ATLAS C10, register H-C. A41 covers:
    - the registered entry S2-11 (one rerun);
    - the new resolution run S0-02-DOS2;
    - the frozen refinement trigger for the three designated QTNLSC mechanism runs S2-04, S2-06 and S2-08 ((d)).
  - Revision 2 said "entry S2-11 only". That was corrected in revision 3 (Codex item 1).
  - This amendment adds:
    - the resolution-method sign-off;
    - one repeated launch of the registered S2-11 entry;
    - one new launch, S0-02-DOS2;
    - a frozen, scorer-bound trigger for at most six later refinement launches, with their labels registered now.
  - It keeps the launch order of register section 3 (S2-11 first). The S2-11 rerun runs first and S0-02-DOS2 follows it. S0-02-DOS2 is an addition outside the 26-launch diagnostic set. Both precede every S2 mechanism launch (see (e)).
  - It changes no registered prediction, threshold, band or rule text of H-C.
  - It changes no code of the frozen scorer (score_register.py c0f28bb9), of post_run_checks.py, of regress_all_decks.py or of the committed runner (public repo 1375164).

- **Why.**
  - **run_0075 is invalid for scoring.** S2-11 ran once as run_0075 (12 Oct, 14:53:22Z to 16:34:32Z; sealed).
    - DeckBuild waited on a TonyPlot viewer until the runner's 5400 s timeout killed the DeckBuild tree at 16:23:24Z.
    - The runner records exit_code=timeout, elapsed 6060 s, timed_out=true and returncode=1 (all four as reported in the work-chat action note 2026-10-12T16:40Z). The frozen scorer rejects a timed-out run (run_problems, score_register.py:245).
    - Codex (20:28Z D5 and D7; 21:14Z) keeps the timeout rejection, the "possibly exposed" label and post_export_hang as diagnostic metadata only.
  - **No I_G resolution pair exists for S2-11.** With the existing runs the hc_mesh verdict can only be PROVISIONAL (S2_SCORER_FIXES_2026-10-12.md section 9.7 and the round-3 consequence).
    - Codex, round 3 (15:50Z), recommended an adaptive amendment: "Add **one S0-02 DOS ×2 run** first. Its I_G comparison with run_0067 may qualify S2-11."
    - Codex also asked to "reserve matching oxide-mesh refinements for mechanisms whose screened contribution could satisfy the registered floor criteria. Freeze that trigger now, and register the new comparison labels."
  - **The method must be signed off before any S2 output is inspected.** Codex (13:18Z (c)): "freeze the resolution methodology before outputs are inspected, not merely before scoring", otherwise disclose a result-informed amendment. See the sight state in (a).
    - The scorer received "GO to freeze after the user's resolution-method sign-off" (Codex 16:08Z).
  - **The runner is fixed.** Commit 1375164 adds bounded, identity-checked timeout cleanup, viewer recording, state-only sealed reporting and the post_export_hang diagnostic (S2_RUNNER_GATES_2026-10-13.md, revision 3; Codex OK 21:14Z).

#### (a) Resolution-method sign-off (record)

- **Scorer.** `analysis_2026-10-10_campaign/score_register.py`, sha256 `c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a`.
  - 1486 lines, committed in public repo ff5f6c1; selftest 90/90.
  - Codex "GO to freeze after the user's resolution-method sign-off" (16:08Z).
  - From logging on, this file is the frozen S2 scorer. Any change needs a new hash, Codex review and a logged amendment.
  - Tag at logging (proposed): `s2-scorer-c0f28bb9-frozen-<utc>`.
- **Evidence.**
  - A resolution is demonstrated only by a `resolution_pair` JSON written by this scorer.
  - It is recomputed from its two run directories at every use; the run-file sha256 and the candidate must match.
  - Free text is never evidence.
  - Without a qualifying pair, the runner's KCL limit is a PROXY, and every verdict under it is PROVISIONAL.
  - Unchanged from the scorer docstring [C1]-[C11].
- **Signed-off values: exactly the five constants the scorer designates** ("the values below are part of the resolution-method sign-off", score_register.py:200-205; S2_SCORER_FIXES 9.3):

  | Constant | Value | Meaning |
  |---|---|---|
  | `RES_SUPPORT_MIN` (:202) | 3 | agreeing points with both currents above the candidate R |
  | `RES_NEAR_DEC` (:203) | 1.0 | at least one of them within this many decades above R |
  | `RES_BIAS_COVERAGE` (:204) | 1.0 | every bias point of both runs compared; no partial pairs |
  | `RATIO_RTOL` (:205) | 1e-3 | deck value ratio against the claimed knob ratio |
  | `OXIDE_LINES_UM` (:201) | (0.002, 0.017) | the y.mesh lines the oxide factor scales; y = 0 is never one |

  - Agreement within 0.1 dec (`MESH_DEC`) and at least 3 points resolved in both runs for an hc_mesh PASS (`MESH_MIN_PTS`) are H-C rule values (:187), frozen by the hash, not part of this sign-off.
  - The candidate R is the largest max(|I_a|, |I_b|) over common points that disagree by more than 0.1 dec, change sign or are zero. With no such point, R is the smallest common same-sign current (resolution_pair, :596).
- **Wording, as Codex approved it** (round 3, Question 1, 15:50Z): "Accept the proposed support values [...] as an **ASSUMED operational method**. Keep the disclosure that the one-decade choice used already-seen S1 pairs. This is prospective for S2, not a blind validation of S1. Pair agreement establishes numerical stability under the tested intervention; it does not automatically establish an absolute error bound." Confirmed at 16:08Z: "The method's **ASSUMED** label and S1-informed threshold disclosure are appropriate."
  - Codex review of this text (2026-10-13T01:32Z, item 1) accepted the five constants, the ASSUMED operational-method label, the S1 disclosure, the verbatim candidate R and the preservation of run_0075.
  - **Disclosure (S1 pairs).** One decade is the tightest value both existing numerical pairs satisfy: each has exactly one supporting point in the first decade above its candidate (S1-04, run_0071 DOS x2 against run_0061: 48 support points in all; S1-03, run_0070 mesh x0.7 against run_0069: 56). The value was chosen knowing those pairs; no S2 data were involved in choosing it (S2_SCORER_FIXES 9.3).
- **Application scope, frozen (rulings b and c; fixes 9 to 11).**
  - A resolution applies only within its quantity (id_A_per_um or ig_raw_A), its film, its physical settings and its compared bias range.
    - Physical settings means: overrides other than the numerical knobs, the material model, and the deck statements with the knob values masked.
    - There is no cross-film transfer and no transfer to another oxide parameter set.
  - The scored run's actual numerical settings (its unmasked deck) must equal one endpoint of the pair.
    - hc_mesh alone also accepts a verified refinement of an endpoint that is finer in every component.
    - An unverified, coarser or mixed grid is refused (qualify :368-427; intervention :522-593).
  - The exact pair under test never supplies its own resolution (forbid_pair, :400).
  - A pair that contains a run under an upper-bound test (hc_nominal, hc_generation) is not independent ceiling evidence for that test (:398-399).
  - A DOS comparison and an oxide-mesh comparison may share run_0067. The shared baseline is recorded (resolution_pair_relation, :898-904, "independent": false), and the two comparisons are never called independent.
  - hc_generation, hc_explains and hc_worst take one resolution per run (fix 11); generation subtraction keeps R_a + R_b.
- **Sight state at sign-off.**
  - No S2 output has been inspected according to the user's statement: the TonyPlot windows of run_0075 were not viewed (D-42 (3)).
  - But the output of the same S2-11 deck was displayed on screen on 2026-10-12, on near_vth.str at 15:14:13Z and on transfer.log at 15:19:40Z. That was before the support values were proposed (round-3 request, 15:50Z) and before Codex's freeze GO (16:08Z) and this sign-off. Codex D7 (20:28Z): "Preserve run_0075's **possibly exposed** label; prevention cannot restore historical blinding."
  - The rerun deck is byte-identical to run_0075's (deck text sha256 3034b7e2...e956), so the rerun is expected to reproduce that output. Rerunning does not restore blinding.
  - The sign-off is therefore not result-informed according to the user's statement, but its blindness cannot be demonstrated. No evidence establishes that S2 results informed the selection, so no confirmed result-informed classification is made. Conversely, the user's statement does not establish team-wide blindness (Codex item 6).
  - **A41 disclosure label.** The registered S2-11 verdict from the rerun carries this label verbatim (Codex 2026-10-13T01:32Z, item 6): **"S1-informed operational method; S2 blinding cannot be demonstrated; possibly exposed; not viewed according to the user's statement."** It retains both earlier labels: "possibly exposed" (Codex D7) and "not viewed (user statement, D-42 (3))".
  - No other S2 run exists.

#### (b) S2-11 rerun

- **run_0075 stays recorded and is invalid for scoring.**
  - It is not deleted, not re-labelled and never substituted. Its record (facts as reported in the work chat 2026-10-12T16:40Z; not re-read for this draft):
    - RUN_INDEX: exit_code=timeout, elapsed 6060 s;
    - execution.json: timed_out=true, returncode=1;
    - sealed launcher log: results/sealed/DIAGa_launch_20261012T145322Z.log (sha256 FB944B94...F343);
    - the legacy summary results/campaigns/campaign_C10_DIAGa_S2-11.json (holds run_0075 metrics) was moved unopened to results/sealed/legacy_campaigns/ with its sha256 recorded (work chat 20:56Z, item 3). Where that sha256 is recorded is not stated in the work chat; the main session to cite it at logging.
  - **TonyPlot facts (work chat 16:40Z):**
    - Viewer windows opened on near_vth.str at 15:14:13Z and on transfer.log at 15:19:40Z. The deck has no tonyplot statement; the origin is ASSUMED to be the DeckBuild GUI (Codex 20:28Z).
    - DeckBuild waited on the viewer until the 5400 s kill at 16:23:24Z.
    - A second viewer, outside the killed tree, held the runner's pipes until the launch agent "closed that viewer window normally" at about 16:34Z.
    - **Viewer-close method: UNKNOWN until documented** (Codex item 6). The work chat records only that the window was closed normally. Whether a screenshot or any other display was involved is not recorded. This is an open item for the main session; a screenshot would be a team sight event of the displayed transfer.log.
    - The ATLAS outputs were written by 15:20:37Z. post_export_hang is diagnostic only: it is not proof of complete exports and does not change eligibility.
    - The launch agent's masked grep of the sealed log matched the runner's summary JSON line with digits masked (metric key names seen, no values; work chat 16:40Z).
  - **Labels kept:** the A41 disclosure label ((a)), which retains "possibly exposed (displayed on screen before the method sign-off)" (Codex D7) and "not viewed (user statement, D-42 (3))". The record still shows that the windows opened.
  - run_0075 stays sealed. It is listed in the sealed-run inventory config/sealed_runs.json ((e)). Opening it later needs a logged decision, and it can never be scored or substituted.
- **Runner for the rerun:** committed public repo 1375164, unchanged (scripts/run_campaign.py, run_atlas.py, campaign_gates.py, campaign_sealed.py and proc_guard.py equal HEAD). In particular:
  - **state-only reporting** (`"state_only": {"sealed_dir": "results/sealed/campaigns"}`): console, summary and RUN_INDEX finish note carry status only; the full record is sealed;
  - **viewer policy `record`** (IWO_ATLAS_VIEWERS unset): a viewer is recorded in execution.json process_guard and is not killed (Codex D4: killing needs a supervised DeckBuild test first);
  - **bounded cleanup:** identity-checked termination of the launch's processes; licence daemons kept; at most 60 s for DeckBuild and 30 s per pipe after a timeout.
- **Known risk, for both launches, accepted with the user's choice of `record`.**
  - The record policy does not stop DeckBuild from waiting on a viewer. It applies to S0-02-DOS2 (same save/log/extract statements, deck lines 118, 122, 126, 133) as much as to the rerun.
  - The rerun held by a viewer times out at 5400 s: it is invalid under the same frozen rule, and S2-11 is UNRESOLVED (QTNLSC convergence not demonstrated).
  - S0-02-DOS2 held by a viewer times out at 3600 s: it is invalid, there is no I_G pair, and S2-11 can at best be PROVISIONAL.
  - With S2-11 first, the first real launch of the committed runner 1375164 is the rerun itself. A runner defect that ends the invocation then costs the one rerun, and S2-11 is UNRESOLVED. Revision 2's runner-canary reason for DOS2 first is withdrawn together with that order.
  - There is no further launch under A41. A viewer-kill qualification or another remedy needs a new amendment and the user's go.
  - Viewer windows are not looked at. Any viewer recorded by the guard is disclosed in the action note. Because the method is signed off before the launch, such a display would be a disclosed sight event after the freeze.
- **How the rerun is launched: `--retry S2-11` under the registered label, chosen over a new label.**
  - The entry is unchanged (id S2-11, label c10_s2_11_2p0, the same 21 overrides, timeout 5400 s). Its deck text sha256 3034b7e276d40f8f8e3587219cbafe82c97c9db43ce23706938e18b4285ee956 equals the 2026-10-11 dry-build and RUN_INDEX deck_sha256 of run_0075 (an input column).
  - It is the first entry of the new plan `config/campaign_C10_DIAGb.json` (sha256 662fd6628b350fc2fa9a968d7934f96f38fff27d242837a71621674eeca563aa). First invocation, in PowerShell from the package root, only after the pre-launch gate below has exited 0 in the same session:

    `$env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & "<venv>\Scripts\python.exe" -I -B <gate>; if ($LASTEXITCODE -eq 0) { & "<venv>\Scripts\python.exe" scripts/run_campaign.py config/campaign_C10_DIAGb.json --retry S2-11 }`

  - **Why `--retry`.**
    - The C10 label-reuse rule (run_campaign.py:130-160, :216) never re-launches a label that already has a RUN_INDEX row. `--retry ID` is the rule's own exception: it "spends a new (reserve) launch on purpose" (:206, :216).
    - Without it, run_campaign would reuse run_0075 for S2-11 and go on to S0-02-DOS2. Its execution.json status is a runner success although it timed out, and earlier_launch only checks that status (synthetic checks: label_reuse_a41.py 4/4; reviewer sandbox of run_campaign.main, retry_sandbox.py 14/14).
  - **Why not a new label.**
    - The frozen scorer keys the registered S2-11 test on the label pair (c10_s2_11_2p0, c10_s0_02_2p0) (REG['hc_mesh'], :178). A new label would score as "smoke test" (status, :474).
    - hc_explains would then refuse it as mesh evidence (mesh_convergence requires a "registered test" hc_mesh score, :1040).
    - campaign_C10_DIAG, which reuses S2-11 by label, would still find only run_0075.
  - **Pre-launch gate before EVERY invocation, including a resume (Codex item 2).**
    - When: immediately before every invocation of campaign_C10_DIAGb. This covers the first invocation and any re-invocation after an interruption, a crash, sleep or a declined hook.
    - Where: the same PowerShell session and working directory as the invocation.
    - What: the A41 pre-launch gate `prelaunch_gate_a41.py` (sha256 7cb0de4cdcbb960179961b9e5a59511f3f59687dfd65dccad09515b1c789a14c), run with `python -I -B`, must exit 0.
    - Reason (Codex): a runner crash can leave DeckBuild running. A resume would then start the next entry beside it, against the one-launch-at-a-time rule.
    - It asserts by explicit equality and exits non-zero on any mismatch. It checks:
      - interpreter: isolated mode and the project venv;
      - working directory = the package root;
      - environment: IWO_MODEL_FILE = config/iwo_material_model_v3.yaml; IWO_ATLAS_VIEWERS and IWO_ATLAS_JOB unset;
      - frozen files: the plan sha256; the exact file set and sha256 of scripts/ (1375164); score_register.py, regress_all_decks.py and regress_sealed_aware.py;
      - the plan: runnable, state-only, no gates, order S2-11 then S0-02-DOS2;
      - the dry build with the runner's own functions, for both entries: deck text 3034b7e2... (S2-11) and 09bb893d... (S0-02-DOS2), material text 974b23ea...;
      - processes: no deckbuild, dbascii, atlas*, tonyplot*, athena*, devedit process (tasklist and CIM); no python*.exe process whose command line names run_atlas or run_campaign. Under this venv the runner's interpreter is python3.13.exe, the child of the venv launcher python.exe; both are covered. An unreadable process list fails;
      - RUN_INDEX: run_id and label of every row. For a started A41 run only, the input columns of its STARTED row are also checked (deck_sha256, model_sha256, model note);
      - every started A41 run is listed in config/sealed_runs.json with the registered values;
      - the next free run id equals the expected one;
      - the launch budget and the C10 cap.
    - Exit 0: it prints the one command to use. Exit 1: a mismatch; nothing is invoked and the failure is reported. Exit 4: both A41 runs have started and nothing remains to launch. A running DeckBuild/ATLAS process is not killed without the user's decision.
    - Failure paths tested (test_prelaunch_gate_a41.py, 34/34; sha256 b65322f54d9f536af4f39e33b5f3952f38c5c89ac94bc60ed9da44c825bf8d6f):
      - real gate processes: IWO_MODEL_FILE unset or V2; IWO_ATLAS_VIEWERS=kill; IWO_ATLAS_JOB=0; no -I; wrong working directory; non-venv interpreter;
      - real fake processes: a running process named tonyplot.exe (a renamed copy of PING.EXE); a running python process whose command line contains run_campaign;
      - injected mismatches: each expected deck hash, the material hash, the plan hash, a scripts/ hash, the scorer hash;
      - fake process lists: deckbuild.exe; atlas.exe + tonyplot3d.exe; python.exe or python3.13.exe running a runner; an unreadable list;
      - synthetic RUN_INDEX states: rerun started but not inventoried; wrong STARTED-row deck hash; note without model=; wrong inventory values; DOS2 before the rerun; a second rerun id; another launch after run_0075.
      - Each of these exits 1. The rerun-started state (inventoried) exits 0 without --retry; both started exits 4; a licence daemon alone exits 0.
    - It replaces prelaunch_dry_a41.py as the launch gate. Codex noted that script printed mismatches without failing. It now also exits 1 on a mismatch (sha256 968ca193...b80e), but it is informational only.
  - **--retry rule (STARTED-row based, unchanged).** Read the RUN_INDEX columns run_id and label only:
    - pass `--retry S2-11` if and only if no c10_s2_11_2p0 row with a run id above run_0075 exists;
    - otherwise never pass it. A rerun start row counts as the one A41 rerun, finished or not; there is no third S2-11 launch.
    - Never repeat the stored launch command verbatim once the rerun has a RUN_INDEX row (it would spend a third S2-11 launch; reviewer sandbox case C).
    - With S2-11 first (Codex item 3), the rerun's STARTED row is the first row the plan writes. Before it exists, --retry is passed and both entries are pending. After it exists, only S0-02-DOS2 can remain.
    - The rule is still needed. A re-invocation without --retry before the rerun's STARTED row exists would record run_0075 as DIAGb's S2-11 ("reused") and launch S0-02-DOS2 without the rerun. A DIAGb record of S2-11 = run_0075 "reused" is never the registered S2-11 result; it is reported and the rule above applied.
    - The gate also stops for a main-session decision on:
      - a S0-02-DOS2 row without a rerun row (order not followed);
      - more than one rerun or S0-02-DOS2 run id;
      - any other launch after run_0075.
    - S0-02-DOS2 is never relaunched (label rule). campaign_C10_DIAG, when it runs, reuses S2-11 by label: the highest c10_s2_11_2p0 run id, which is the rerun (:132-134).
- **Pinned for scoring.**
  - The registered S2-11 result is the rerun: the first launch of c10_s2_11_2p0 after A41, made by campaign_C10_DIAGb as its first entry. Its run id is written into the register when known; it is expected to be run_0076 (the next free id), and S0-02-DOS2 is expected to be run_0077.
  - run_0075 can never be substituted: not if the rerun fails, not as a fallback, and not under any later ruling on timed-out runs.
  - **The frozen scorer cannot enforce this pin.** Its PIN covers only c10_s0_02_2p0 = run_0067 (:186), so status() labels any c10_s2_11_2p0 launch "registered test". The pin is therefore procedural:
    - the registered hc_mesh invocation names the rerun directory;
    - any `--mesh-score` cited to hc_explains or a gate must be the rerun's score (its evidence block names the run id and file sha256);
    - run_0075 scores "invalid (... return code 1; timed out)" in any case (run_problems :245).
    - A later scorer amendment (for example the one (d) needs) may add PIN c10_s2_11_2p0 = <rerun id>; not part of A41.
- **campaign_C10_DIAGa_S2-11 is superseded and now held.** It is regenerated with runnable=false and a not_runnable_reason (make_campaign_configs.py HOLD; file sha256 260c1203...8150 -> fb3eb685...734a; runs unchanged). Reason: invoking it would reuse run_0075 (or, after A41, the rerun), and because it is not state-only, run_campaign would write that run's summarize() metrics into the unsealed results/campaigns/campaign_C10_DIAGa_S2-11.json (run_campaign.py:155-156, :196), recreating the leak removed on 12 Oct.

#### (c) S0-02-DOS2, the I_G resolution run for S2-11

- **Registered entry:** id S0-02-DOS2, label `c10_s0_02_dos2_2p0`, 2.0 nm, stage S2_resolution_refinements (new; held stage plan campaign_C10_S2r_resolution), status planned_fixed, timeout 3600 s. It is the second entry of campaign_C10_DIAGb, after the S2-11 rerun (expected run_0077).
  - The timeout is S0-02's x1.5 doubled to x3.0, as S1-04 doubled S0-01's x1.0. For scale: run_0067 took 1246 s, S1-04 476.8 s against S0-01's 395.8 s (expected DOS2 about 1500 s).
- **Definition.** run_0067's settings, as launched, with only the DOS level counts doubled.
  - The override list is run_0067's execution.json list (20 entries, identical to the matrix S0-02 entry), with two values changed in place (positions 13 and 14):
    - `solver.dos_levels.numa=384` -> `solver.dos_levels.numa=768`
    - `solver.dos_levels.numd=192` -> `solver.dos_levels.numd=384`
  - These are the keys and factor of the existing DOS x2 pair, S1-04 (run_0071) against S0-01 (run_0061). Override order changes neither the deck nor score_register.intervention, which compares key-value maps.
  - Model file V3. The material text is identical to run_0067's (text sha256 974b23ea...8204 = RUN_INDEX model_sha256 of run_0067; file bytes 5403594e...c224e).
  - **Effective change:** the acceptor energy quadrature only. NTD = NGD = 0 in both regions, so the donor DOS is zero and doubling NUMD is inert. The acceptor step falls from 8.82 to 4.40 meV over the unchanged range 0 to 3.37725 eV (383 to 767 intervals; the grids are not nested). The same g(E) and range were verified on the AFILE echo of seen runs run_0067 (384 levels) and run_0071/S1-04 (768 levels): tail and Gaussian columns reproduced to 3e-5 or better (TCAD reviewer, dos_echo2.py/dos_echo3.py).
  - **Numerical, not physical (Codex 2026-10-13T01:32Z).** ATLAS defines NUMA and NUMD as the energy-level intervals of the numerical integral for continuous defects (atlas_manual_pages.txt:37397-37401). Agreement under this perturbation establishes reproducibility, not an absolute tunnelling error bound. Estimating the discretization error would need additional convergence assumptions.
- **Dry-built deck** (current generator, no launch): text sha256 09bb893d3254c9f0de24238e5b6f5eca3fa99c549c8d3f9456709eec95ff8e85, 157 lines (unchanged in revision 3: the reorder changes no deck).
  - Against run_0067/device.in (text sha256 8493301437f5...08ad, equal to the current S0-02 rebuild), exactly two statements differ and no comment line differs:

    ```
    @@ -92 +92 @@
    -defects region=1 continuous numa=384 numd=192 \
    +defects region=1 continuous numa=768 numd=384 \
    @@ -101 +101 @@
    -defects region=2 continuous numa=384 numd=192 \
    +defects region=2 continuous numa=768 numd=384 \
    ```

  - Every continuation line (nta, wta, ntd, wtd, nga, ega, wga, ngd, egd, wgd, sig*, afile/dfile) is identical.
  - **TCAD manual check (5.28 text, atlas_manual_pages.txt).**
    - 15.2.7 Continuous Defects, PDF p.887, lines 37397-37401: with CONTINUOUS, NUMA and NUMD "correspond to the number of acceptor and donor energy level intervals used in the integral"; Table 15-4 (37419-37423): defaults 12.
    - 22.10 DEFECTS: parameter table PDF p.1174 (48757-48758, NUMA/NUMD Real 12); descriptions p.1177 (48883-48884, NUMA: the number of discrete levels used to simulate the continuous acceptor distribution) and p.1178 (48888-48889, NUMD).
    - The DOS itself is set only by NTA/NTD/WTA/WTD/NGA/NGD/EGA/EGD/WGA/WGD (15.2.3, Eq. 15-1 to 15-5, p.879-880), unchanged. INT_LIM1/INT_LIM2 (48851-48854) are not set in either deck, so the integration range is unchanged. FLUENCE.MODEL (4.2.10, where NUMA has another meaning and default 10), TAT.TRAP/LIMIT1/LIMIT2 and MODIFY ("NUMA and NUMD cannot be modified", 48865) are not used.
    - Conclusion: doubling NUMA/NUMD refines the energy quadrature only, a numerical knob. (Revision 1 cited p.466, :20828-20829; that is the Radiation Fluence Model table, the wrong chapter.)
- **Purpose.** An I_G resolution pair with run_0067 for the 2.0 nm film, the worst oxide set and run_0067's physical settings (QTNLSC, automatic slicing, S/D exclude_near, oxide mesh unchanged).
  - It is not a physics test and carries no prediction.
  - It qualifies only under the frozen support rule in (a).
  - **What it measures:** I_G reproducibility under the acceptor-quadrature perturbation only. The DOS knob reaches I_G only through the IWO trap charge and band bending; the QTNLSC oxide path, the slicing and the oxide mesh are unchanged. It is therefore a reproducibility floor for I_G, not a bound on the tunnelling discretization that S2-11 tests. For S2-11 this is conservative: a lower R makes hc_mesh stricter.
- **How the scorer uses it** (frozen c0f28bb9; CLI forms in the module docstring):
  1. `score_register.py resolution_pair <S0-02-DOS2 run> <run_0067> ig_raw_A` writes the PAIR JSON.
     - intervention() must verify a DOS grid change with refined = run and deck ratio numa 2 / numd 2 on the defects lines only (:542-548, :576-583, :588-592).
     - Both runs must be gate-tunnelling, accepted and complete, and the support and coverage rule must hold (:613-626).
     - If the call raises or writes no JSON, there is no pair. Known edge (reviewer probe, confirmed in the code at :626): if the only disagreeing common points are exact zeros of I_G in both runs (R = 0) while at least 3 points agree, the frozen scorer raises ZeroDivisionError instead of "not qualified". This fails safe (no JSON, no demonstrated resolution) and is reported to Codex for any future scorer revision; no scorer change now.
  2. `score_register.py hc_mesh <S2-11 rerun> <run_0067> --resolution-ig <R> --resolution-ig-source <PAIR JSON>` gives the registered S2-11 score.
     - **R is the PAIR JSON's candidate_resolution_A_per_um, cited verbatim. No larger value may be cited** (qualify accepts any value at or above the candidate, :422, and a larger R censors more points). The sha256 of the PAIR JSON and of the score JSON are recorded in the action note.
     - ig_resolution(..., forbid_pair=(rerun, run_0067), refine_ok=True) (:896) accepts the pair through two routes: run_0067 is an endpoint; the rerun is a verified oxide y-mesh refinement (deck ratio 0.5) of endpoint run_0067 (qualify :411-420).
     - The run pair's settings must equal the pair's scope (:407).
     - The output records resolution_pair_relation = {shared_baseline: [run_0067], independent: false} (:898-904).
     - **Disclosure in the post-run report:** R compared with the deck's absolute tolerances, METHOD ir.tol = 1e-19 and cr.toler = 1e-17 (strict, to V_G = 0.7 V) / 5e-18 (on-state) (deck lines 110-111, 128-129; manual 56194, 56202). If R lies below them, agreement shows run-to-run reproducibility, not accuracy controlled by the Newton convergence test. Label: "reproducibility floor under the DOS intervention".
  3. If the pair does not qualify (for example I_G disagreement, too little support, I_G zero throughout, or the edge above), hc_mesh runs without --resolution-ig and is PROVISIONAL. There is no second DOS run (Codex: extra runs cannot guarantee qualification).
- **What the DOS pair does not do:**
  - it is no ceiling evidence for hc_nominal on run_0067 or on S0-02-DOS2 (not independent, :398);
  - it does not qualify any upper-bound test on the S2-11 rerun (numerical-scope guard: the rerun equals neither endpoint);
  - it does not transfer to the nominal set (S2-04), to 13.2 nm, or to ITAT;
  - it is no absolute bound on the tunnelling error (above).
- **Not independent.** The DOS comparison and the S2-11 comparison share run_0067. Their agreement shows numerical stability of that baseline under two interventions, not two independent confirmations.

#### (d) Frozen trigger for matched oxide-mesh refinements (no launch now)

- **Codex review (2026-10-13T01:32Z, item 4):** accepted the narrowed branch (B), the six-launch ceiling, the REG/PIN-only scorer amendment and OOM -> UNRESOLVED, with the labelling and evidence conditions below.
- **Mechanisms in scope (the three designated refinement triggers).** The QTNLSC mechanism runs of the register's hc_explains set whose physical settings lie outside the S2-11 scope (ruling b):

  | Mechanism | Film | Oxide set | Control |
  |---|---|---|---|
  | S2-04 | 2.0 nm | nominal | S0-01 |
  | S2-06 | 13.2 nm | nominal | S1-02 |
  | S2-08 | 13.2 nm | worst | S1-02 |

  - The 2.0 nm worst-set QTNLSC form is S2-11/S0-02 itself.
- **Input, fixed now.** For each mechanism, exactly once: `score_register.py hc_explains <mechanism run> <control>`, with `--mesh-score` set to the registered S2-11 score if it exists and without it otherwise, and with **no --resolution* input of any kind**.
  - When: at the first scoring of the mechanism run, after the mechanism run and its control have both completed, under the register's unsealing order, before any other output of that run is inspected.
  - Neither choice changes the screen: these three runs lie outside the S2-11 scope, so `converged` is null with or without a mesh score (mesh_convergence :1050), and the floor criteria use the fixed 7.1 validity limit (floor_metrics_masked :930-957) whatever resolution is given; a resolution only adds the PROVISIONAL prefix (floor_qualification and prov, :429-434, :1083).
  - The trigger reads the JSON fields `verdict`, `criteria`, `converged` and `floor_metrics` only. The JSON sha256 is recorded in the action note.
- **Trigger, evaluated mechanically** (after stripping a leading "PROVISIONAL (...): " prefix):
  - **TRIGGERED (A)** if the verdict starts with "unresolved (passes all four 7.2 floor criteria" (explains_verdict :1026): all four `criteria` are true and `converged` is not true.
  - **TRIGGERED (B)** if the verdict starts with "unresolved (insufficient support" (:1079-1081) **and** no criterion that is computable on the uncensored points fails: `floor_metrics.d_floor_ratio_dec` is null or within 0.5 dec, **and** `floor_metrics.floor_slope_dec_per_V` is null or its magnitude is at most `floor_metrics.slope_limit_dec_per_V`.
    - Why the extra condition: as coded, the insufficient-support verdict appears whenever any criterion fails and any window point is KCL-censored or the control is unsupported, with (valid + censored)/window >= 0.8, whatever the floor ratio or slope (the kcl_pass_window criterion is itself false whenever a window point is censored). Without the condition it could trigger refinement launches for a mechanism decades below the floor, which is wider than Codex's criterion ("screened contribution could satisfy the registered floor criteria"). Codex accepted this narrowing (item 4).
    - **Branch (B) is an operational spending screen** (Codex item 4). It decides only whether refinement launches are spent. Failing its partial-data slope/ratio condition does not resolve the censored scientific result. The raw hc_explains verdict ("unresolved (insufficient support ...") is preserved and reported as UNRESOLVED; it is never re-read as "does not explain the floor".
  - **NOT_TRIGGERED** otherwise, in particular for a verdict starting with:
    - "does not explain the floor" (:1024): a criterion fails on the uncensored points;
    - "unresolved (insufficient support" with a failing uncensored d_floor or slope (above). This is not triggered for spending only; the verdict stays UNRESOLVED;
    - "FALSIFIES H-C" (:1025): already converged;
    - "invalid (": the mechanism run or control is invalid. This is reported, and its repair is a separate decision.
  - The result is binding; there is no discretionary override in either direction.
- **Registered labels now** (ids, then labels; constructions fixed now):

  | Mechanism | Resolution companion (first) | Oxide-mesh refinement (second) | Registered comparison label pair |
  |---|---|---|---|
  | S2-04 | S2-04-DOS2 -> `c10_s2_04_dos2_2p0` | S2-04-OXM -> `c10_s2_04_oxm_2p0` | (c10_s2_04_oxm_2p0, c10_s2_04_2p0) |
  | S2-06 | S2-06-DOS2 -> `c10_s2_06_dos2_13p2` | S2-06-OXM -> `c10_s2_06_oxm_13p2` | (c10_s2_06_oxm_13p2, c10_s2_06_13p2) |
  | S2-08 | S2-08-DOS2 -> `c10_s2_08_dos2_13p2` | S2-08-OXM -> `c10_s2_08_oxm_13p2` | (c10_s2_08_oxm_13p2, c10_s2_08_13p2) |

  - **OXM** = the mechanism's matrix overrides plus `solver.physics_options.gate_tunnelling.oxide_mesh_factor=0.5`: the S2-11 construction, y.mesh at 0.002 and 0.017 um halved, y = 0 kept. Timeout: the mechanism's x3, as S2-11 is to S0-02.
  - **DOS2** = the mechanism's overrides with numa/numd 384/192 -> 768/384 in place: the S0-02-DOS2 construction. Timeout: the mechanism's x2.
  - All six constructions are verified refinements by the frozen intervention() (DOS ratio 2 and 2, oxide ratio 0.5, refined = run) with equal settings (reviewer dry-build check, trigger_constructions.py).
  - **Scoring of a triggered pair:**
    - hc_mesh <OXM> <mechanism run> --resolution-ig <R> --resolution-ig-source <resolution_pair <DOS2> <mechanism run> ig_raw_A>, with **R = that PAIR JSON's candidate_resolution_A_per_um, verbatim; no larger value** (as for S2-11);
    - same rule as S2-11 (resolved log10 |I_G| within 0.1 dec, at least 3 points resolved in both runs);
    - each certifies only that mechanism's exact settings; the shared mechanism baseline is recorded, not independent.
  - **What the refinements establish (Codex item 4):** I_G oxide-mesh stability of that mechanism's settings only. A non-PROVISIONAL hc_explains result still needs matching I_D resolution evidence for the mechanism run and its control. Without it, hc_explains stays PROVISIONAL even when the mesh pair passes.
- **Prerequisite before any triggered launch: a scorer amendment, limited now.** The frozen scorer cannot use these pairs today (such a label pair scores as "smoke test"; scorer_compat_a41.py).
  - The amendment may add exactly: the three registered label pairs above to REG['hc_mesh'], and PIN entries for the mechanism labels at their DIAG run ids (optionally PIN c10_s2_11_2p0 = the A41 rerun id). Nothing else. Its diff is checked to contain only those lines, then a new hash, Codex review and freezing, all before the triggered launch.
  - mesh_convergence() needs no other change: it already requires the mechanism's settings to equal the mesh score's scope (:1050).
- **13.2 nm OXM and the section-K mesh rule.** 01_CURRENT_STATE.md:295 ("Refine the 13.2 nm mesh by x0.7; x0.5 exceeds memory") concerns the global spacing factor (geometry.mesh.spacing_factor), which OXM does not touch; OXM halves only the two oxide y lines.
  - Size estimate (ASSUMED, arithmetic on node counts of seen runs): the structures are rectangular grids of 117 x lines (run_0067 9,594 = 117 x 82; run_0062 13,689 = 117 x 117; run_0069 12,051 = 117 x 103). The oxide x0.5 adds 35 y lines at 2.0 nm (82 -> 117, S2_PREP section 6). A 13.2 nm OXM deck would have about 117 x 138 = 16.1k nodes, against run_0070 (13.2 nm, global x0.7, no QTNLSC) with 24,255 nodes, which ran. QTNLSC memory per node is higher (run_0067: 1.69 GB peak of 4 GB at 9,594 nodes), so memory is unverified.
  - **Frozen now:** an out-of-memory or other failure of an OXM (or DOS2) launch makes that mechanism's QTNLSC convergence UNRESOLVED. No factor change, no post-hoc switch to x0.7 and no repeat under A41.
- **Launch rules for triggered refinements.**
  - At most 2 launches per triggered mechanism and at most 6 in total (Codex: two launches now, at most six triggered later).
  - Each runs from its own state-only plan written after the trigger result and the scorer amendment are logged, with the DOS2 companion first.
  - Each needs the user's go per launch, under the existing launch rules, and the same kind of pre-launch gate before every invocation.
- **Not covered by the trigger:**
  - ITAT (S2-12/S2-13): the knob is TAT.SLICEPTS, which is not a scorer knob. Convergence stays UNRESOLVED without its own amendment.
  - Generation (S2-01/S2-02, S2-03): no mechanism-specific refinement; it stays UNRESOLVED.
- **Tiny nulls stay PROVISIONAL or UNRESOLVED.**
  - Nominal leakage (hc_nominal: S2-04, S2-06) and generation (hc_generation: S2-01/S2-02) keep PROVISIONAL or UNRESOLVED verdicts whenever their in-scope, independent, numerically matched ceiling cannot be demonstrated.
  - A41 registers no ceiling runs for them. Under the numerical-scope guard such a ceiling would need an independent pair with an endpoint identical to the tested deck, and Codex advises that extra runs cannot guarantee qualification.

#### (e) Order, budget, sealing and logging

- **Launch order: the S2-11 rerun first, then S0-02-DOS2** (one invocation, sequential). Codex (2026-10-13T01:32Z, item 3): "use S2-11 first, then S0-02-DOS2. This simplifies rerun bookkeeping and preserves the registered S2-first order. It does not replace the resume safeguards."
  - The register section 3 order (S2-11 first) is kept. S0-02-DOS2 is an addition outside the 26-launch diagnostic set; it precedes every S2 mechanism launch (S2-04 and later).
  - Revision 2 proposed S0-02-DOS2 first (runner canary); that proposal and its reasons are withdrawn. Codex: DOS2-first was scientifically acceptable, but offered no necessary advantage.
  - Blinding is unaffected by the order: both decks are frozen by A41, and both outputs stay sealed until both runs have ended.
  - The S2-11 matrix entry's purpose text says "first S2 launch"; it is now literally true for DIAGb as well. The entry is unchanged.
  - **Plan-file effects of the reorder.**
    - campaign_C10_DIAGb.json is regenerated: entry order swapped, purpose and stop rules updated, entries identical by id; e0f3173e...72cd -> 662fd662...63aa.
    - campaign_C10_S2r_resolution.json changes only in its HOLD text, whose parenthetical names DIAGb's order (two fields: stop_rules[0] and not_runnable_reason); b7cde9f7...f676 -> 9134aa89...c115.
    - Every other plan file, the matrix (83a4cc46...bec) and make_campaign_matrix.py (afd5307c...8154) are byte-identical to revision 2.
- **Budget.**
  - Global: 75/260 used now (RUN_INDEX: 75 distinct run ids; config/solver.yaml max_launches 260); 77/260 after this plan.
  - C10: 15/200 now (run_0061 to run_0075); 17/200 after.
  - Expected run ids: run_0076 (S2-11 rerun) and run_0077 (S0-02-DOS2). These hold if nothing else launches in between: the next free id is run_0076 (RUN_INDEX run_id column), and the gate refuses if it changes.
  - Later: campaign_C10_DIAG adds 18 new launches (S2-11 reused), giving 35/200; DIAG_HF 5 (40/200); S6-13/S6-15 2 (42/200); the A41 trigger at most 6 (at most 48/200).
  - **Effective reserve.** The matrix figure (reserve 15 = 200 - 185 entries) ignores the 5 extra S0-02 repair launches and the S2-11 rerun, itself a reserve launch under --retry. After A41: 11 matrix entries launched with 17 C10 launches, 174 entries unlaunched, so the effective C10 reserve is 200 - 17 - 174 = **9**, or **3** if all six trigger launches happen (checked from RUN_INDEX run_id/label and the matrix, prelaunch_dry_a41.py).
  - H-C cost: 9 (A16) + 2 (A41), plus at most 6 trigger-conditional launches (Codex: keep two launches now and at most six triggered later).
- **Sealing.**
  - Both new runs use the state-only surface. No current, metric or note of either run is opened, printed or scored before both launches have ended and A41 with the sign-off is logged.
  - The only reads allowed before then are the input columns of each run's STARTED row in RUN_INDEX (run_id, label, deck_sha256, model_sha256 and the STARTED note, written at launch before any output). Post-launch input check: deck_sha256 = 3034b7e2... (rerun) and 09bb893d... (DOS2), model_sha256 = 974b23ea..., note contains model=config/iwo_material_model_v3.yaml.
  - **Sealed-run inventory.** Each A41 run is appended to config/sealed_runs.json as soon as its STARTED row exists, during or right after the invocation. This happens before any later regression check or re-invocation. The entry carries the registered label, entry, model file, deck_sha256 and model_sha256. The regression wrapper then checks the RUN_INDEX input columns against them; this is the post-launch input check in reproducible form. The pre-launch gate refuses a re-invocation while a started A41 run is missing.
  - **Validity** is read from the RUN_INDEX exit_code of the run's finish row or from the scorer's run_problems, never from the state file. The state projection (campaign_sealed.STATE_KEYS) has no timed_out or return code, so a timed-out run with complete exports shows as "completed" with status REAL_ATLAS_SCORED, as run_0075 did (run_atlas.py:279-298).
  - Then scoring follows this order:
    1. runner state and validity;
    2. resolution_pair (S0-02-DOS2 against run_0067, ig_raw_A);
    3. hc_mesh (rerun against run_0067), with --resolution-ig = the PAIR candidate verbatim, or without it, as in (c).
  - run_0075 stays sealed (above). The legacy DIAGa summary was already moved unopened (work chat 20:56Z); no housekeeping step remains.
- **Deck regression gate in a sealed-aware form: a committed repo wrapper (Codex item 5).**
  - Script: `analysis_2026-10-10_campaign/regress_sealed_aware.py` (sha256 9c06581434762a12d1426b9b2333d3b8ffc7191bc6b2117c66b721bd8f1bb41d; new, committed at logging). It imports the committed regress_all_decks.py unchanged (d7f26e9b).
  - It runs that gate over every run except the ids of the explicit inventory `config/sealed_runs.json` (sha256 644d21d9abfe9cd536aa0076984e8c28558a3cb60b106951af672aa907fffd7b). The inventory now lists run_0075 only, with label c10_s2_11_2p0, entry S2-11, model file V3, deck_sha256 3034b7e2... and model_sha256 974b23ea....
  - The RUN_INDEX rows of an inventoried id are dropped by run_id before any other column is read, and its directory is skipped by name.
  - For each sealed id, the RUN_INDEX label, deck_sha256 and model_sha256 must equal the inventory, and the current rebuild of its matrix entry must hash to the inventory values.
  - Before anything else it refuses to run (exit 2) while a RUN_INDEX run with a state-only plan label is missing from the inventory.
  - Location: analysis_2026-10-10_campaign/, beside the gate it wraps, because scripts/ is frozen at 1375164.
  - Rule: the two A41 runs are appended right after they start, before any later regression check. Removing an entry needs a logged decision.
  - Result now: "identical 58; unexpected differences 0". That is 57 unsealed runs, line for line equal to the reviewed scratchpad wrapper's output (regress_unsealed_a41.py 60f8bb07...411a, now superseded), plus run_0075 by its input hashes.
  - Guard paths tested: inventory without run_0075 -> exit 2 before any other read; a wrong inventory deck_sha256 -> exit 1.
- **Logging order (all before either launch).**
  1. Codex reviewed revision 2, config/campaign_C10_DIAGb.json (e0f3173e...72cd), config/campaign_C10_DIAGa_S2-11.json (fb3eb685...734a, held), the generator diff, the dry-build diffs and the compatibility checks, under the TCAD rule (manual check done: (c)): GO-WITH-CHANGES, 2026-10-13T01:32Z.
  2. Codex's six changes are applied (this revision 3) and every gate re-run: the sealed-aware regression wrapper, --check, scorer selftest and hash, the pre-launch gate and its failure-path tests (done; see Files and checks).
  3. The user confirms the final sign-off wording (a), including the A41 disclosure label, and the launch order (S2-11 first).
  4. A41 is logged in the register (section 2 text, section 5 row, header "A34 to A39, A41"), together with decision log D-44 (the ATLAS go of ~00:05Z) and a work-chat action note.
  5. The scorer hash is recorded and tagged. The generators, the configs, regress_sealed_aware.py and config/sealed_runs.json are committed in the public repo. The plan files carry final wording (no "DRAFT" text); they are not regenerated after logging, so the hash Codex reviews is the committed one.
  6. Pre-launch checks before the first invocation (campaign_C10_DIAGb.json stop rule 3), in the same PowerShell session and working directory as the launch (the package root):
     - regress_sealed_aware.py;
     - --check;
     - scorer hash and selftest;
     - runner files = 1375164;
     - the pre-launch gate (stop rule 2), which repeats the environment, file, deck/material, process, RUN_INDEX, inventory and budget checks.
  7. The user gives a go for THIS launch, and the hook asks.
  8. campaign_C10_DIAGb is invoked with the command the gate prints (first invocation: --retry S2-11). Every re-invocation is preceded by the gate again and follows the --retry rule in (b).
  9. Post-run:
     - run ids;
     - both runs appended to config/sealed_runs.json, then the STARTED-row input check (regress_sealed_aware.py);
     - validity;
     - the S2-11 verdict against the registered prediction (resolved |I_G| changes by at most 0.1 dec), with the A41 disclosure label;
     - R against ir.tol/cr.toler, as a reproducibility floor, not an absolute bound;
     - solver warnings, viewer events and any resumed-process overlap.
     - Failed runs are reported and kept.

- **Budget, failures.** Every launch counts. A failed or timed-out launch is reported and kept, never deleted, and not relaunched under A41:
  - a timed-out or failed S2-11 rerun is invalid, and S2-11 is UNRESOLVED;
  - a failed, timed-out or non-qualifying S0-02-DOS2 leaves S2-11 PROVISIONAL.

- **Not changed.**
  - H-C predictions, thresholds and rule text.
  - Register sections 0 and 1. The censoring rule: KCL is a sanity check, not an uncertainty estimate.
  - The 26-entry diagnostic set and its section 3 order (S2-11 first; kept).
  - score_register.py c0f28bb9 (no code change), post_run_checks.py 39d3d51d, profile_shared.py 958c3605, regress_all_decks.py d7f26e9b.
  - The runner files at 1375164.
  - The S2-11 entry and deck (3034b7e2...).
  - All existing matrix entries and 20 of the 21 existing config/campaign_*.json files (byte-identical; DIAGa changes as stated in (b)). campaign_C10_DIAG.json 430a6d1a and campaign_C10_S2_offfloor.json are unchanged, although the latter's HOLD text still names DIAGa as the register route (held file; left byte-identical).
  - DIAG's gates and holds (sign-off, run_0075 rulings, acknowledgement audits).
  - DIAG_HF held; ITAT and H-F handling.
  - run_0075's record.

- **Sight history.** The preparation accesses of revisions 1 and 2 are kept as disclosed (Codex item 6).
  - **Read before revision 1 (prep):**
    - run_0067 (S0-02, seen before revision 2): execution.json overrides and status flags, device.in, material_model_used.json;
    - RUN_INDEX elapsed_s of run_0061, run_0067, run_0069, run_0070 and run_0071;
    - for run_0075:
      - the file names and sizes in its run directory;
      - **its device.in (deck input; compared with the dry-build, equal).** This broke the workflow's sealing rule for run_0075 (names and sizes only); no output information was involved. Future equality checks use RUN_INDEX deck_sha256 instead;
      - RUN_INDEX run_id, label, exit_code (timeout, already recorded) and deck_sha256;
      - regress_all_decks.py in its committed form, which json-parses run_0075's execution.json (only its overrides used), reads its STARTED note and device.in, and prints "IDENTICAL" and the deck sha.
    - results/sealed/: its two top-level names (DIAGa_launch_20261012T145322Z.log, legacy_campaigns) were listed once by mistake; no file was opened.
  - **Read for revision 2:** no run_0075 file; run directory names only (glob); RUN_INDEX rows parsed with only run_id, label, deck_sha256 and model_sha256 accessed for run_0075 (equality printed, no value); run_0067 device.in and execution.json overrides; results/campaigns/ names; the work chat (12-13 Oct), the decision log D-42 and the ATLAS manual text. results/sealed/ was not listed.
  - **Reviewers (2026-10-13):** the TCAD reviewer read the AFILE echo of run_0067 and run_0071 (seen runs) and RUN_INDEX deck_sha256 of run_0075; the runner reviewer listed results/campaigns/ names, ran run_campaign.main in a sandbox with a synthetic RUN_INDEX and fake execute, and read RUN_INDEX deck_sha256/model_sha256 of run_0075; no reviewer ran the committed regression gate on run_0075.
  - **Read for revision 3:**
    - the RUN_INDEX run_id column (next free id) and the run_id/label columns of all rows (state-only label guard, gate state);
    - for run_0075, only its label, deck_sha256 and model_sha256 columns, through regress_sealed_aware.py, the gate and prelaunch_dry_a41.py (equalities printed, no value);
    - run_0067 device.in and execution.json overrides (deck_diffs_a41.py re-run);
    - run directory names (glob);
    - the work chat entry 2026-10-13T01:32Z; the manual lines 37395-37401.
    - Tested for existence only, never opened or listed: results/campaigns/campaign_C10_DIAGb.json and results/sealed/campaigns/campaign_C10_DIAGb.full.json / .console.log (none exists).
    - No sealed file, no run_0075 file and no S2 output was opened. The failure-path tests started and stopped two stand-in processes: a renamed copy of PING.EXE named tonyplot.exe, and a python sleep process. No Silvaco program was started.
  - **Not read by anyone in this preparation:**
    - any other run_0075 file;
    - run_0075's RUN_INDEX notes, elapsed or metric columns (the 6060 s figure is from the work chat);
    - results/sealed/legacy_campaigns/ contents;
    - any current of any run (the compatibility checks use synthetic currents only).

- **Files.**
  - Public repo, working copy, uncommitted, sha256 of the file bytes:

    | File | sha256 | Status |
    |---|---|---|
    | analysis_2026-10-10_campaign/make_campaign_matrix.py | afd5307c...8154 | M (unchanged since revision 2) |
    | analysis_2026-10-10_campaign/campaign_matrix.json | 83a4cc46...bec | M (unchanged since revision 1) |
    | analysis_2026-10-10_campaign/make_campaign_configs.py | ac423f72...6135 | M (revision 3: order, DIAGB rules and command, docstring, --check message) |
    | config/campaign_C10_DIAGb.json | 662fd662...63aa | new (revision 3; revision 2 e0f3173e...72cd) |
    | config/campaign_C10_S2r_resolution.json | 9134aa89...c115 | new (revision 3: HOLD order wording; revision 2 b7cde9f7...f676) |
    | config/campaign_C10_DIAGa_S2-11.json | fb3eb685...734a | M (held; unchanged since revision 2) |
    | analysis_2026-10-10_campaign/regress_sealed_aware.py | 9c065814...b41d | new (revision 3) |
    | config/sealed_runs.json | 644d21d9...fd7b | new (revision 3; changes when the A41 runs are appended) |

  - Scratchpad (atlas_a41/final; not in the repo): prelaunch_gate_a41.py 7cb0de4c...a14c (the launch gate); test_prelaunch_gate_a41.py b65322f5...8d6f; prelaunch_dry_a41.py 968ca193...b80e (revision 2: d622f966...8463); deck_diffs_a41.py 92b9e4c1...1388 (unchanged); regress_unsealed_a41.py 60f8bb07...411a (superseded by the repo wrapper).
  - Checks (revision 3):
    - sealed-aware regression gate (repo wrapper): identical 58 (57 + run_0075 by input hashes), unexpected differences 0;
    - make_campaign_configs --check: exit 0, YES (185 entries, 7 stage plans; DIAGa listed HELD; DIAGb "S2-11 then S0-02-DOS2");
    - score_register selftest: 90/90 (output identical to revision 2), sha256 c0f28bb9 unchanged; regress_all_decks.py d7f26e9b unchanged;
    - scripts/ = 1375164 (git diff empty, no untracked file; 16 files; three working copies carry CRLF endings, content equal to the commit);
    - pre-launch gate: exit 0, first invocation, "--retry S2-11: PASS IT", expected run_0076 then run_0077;
    - gate and wrapper failure paths: 34/34;
    - deck_diffs_a41.py: output and deck texts identical to revision 2;
    - prelaunch_dry_a41.py: mismatches 0, exit 0 (exit 1 under a V2 environment);
    - RUN_INDEX unchanged (c6953d45...); nothing launched;
    - revision 1 checks still valid (matrix unchanged): s2_prep_decks, check_v3_equivalence 102/102, make_sample_decks, scorer_compat_a41.py 19/19, label_reuse_a41.py 4/4.
- **Logging note (2026-10-13T02:16Z).** Codex reviewed the revision-3 record note (work chat 2026-10-13T02:04Z): A41 revision 3 policy GO; launch gate FIX_FIRST on one point (a python process with a null CIM command line passed the process check). Fixed before logging: tasklist and CIM are reconciled by PID, and any other python process with a missing CIM entry, a null/empty command line or an image-name conflict stops the gate as UNVERIFIABLE; both regression cases added (tests 41/41). The gate and its tests are committed beside the wrapper: analysis_2026-10-10_campaign/prelaunch_gate_a41.py (sha256 35df463326bd7345236f3807f865d338a30cd2383606ed738643a5ba3449d75e) and analysis_2026-10-10_campaign/test_prelaunch_gate_a41.py (480ffa5a7989b8b4a8a515b0ca87744c1917768d66a6ecfb16eb83c6be8908f2); they replace the scratchpad gate 7cb0de4c...a14c named above. Public repo commit adf6ae3 holds the generators, the plan files, the wrapper, the inventory and the gate (git stores LF; the working-tree bytes the gate checks keep their CRLF hashes, e.g. DIAGb 662fd662...63aa). Scorer tag s2-scorer-c0f28bb9-frozen-20261013T0216Z. The user confirmed the sign-off wording and the order at ~02:07Z and gave the go for this launch after logging.

### A42: A20(i) implementation for H-L: two seed starts, primary energy min(E_A, E_B, E_nspin1), additive start-A trigger, split-label equivalence gate, one fallback, counting bound to the submitted job (result-informed amendment, added after the freeze, 2026-10-13T21:33Z, after the H-L k3/k4 and A20(ii) differences were read (2026-10-13T00:25-00:31Z) and before any A20(i) output exists; two internal reviews GO-WITH-CHANGES, blocking changes applied; Codex 2026-10-13 reply to the 03:26Z digest: A20(i) GO-WITH-CHANGES with FIX_FIRST, fixes applied in comparator v3; Codex FIX_FIRST on this draft (removal-reason evidence, hold/release sequence, budget wording) applied in comparator v4; Codex review of this text: Codex 2026-10-13T21:27Z (reply on checker v12): GO to log the installed v4 amendment; the install disclosure supersedes the annex's pre-install state; user go: 2026-10-13 ~04:15Z (work chat USER GO item 3, conditional on Codex review; met); decision D-45)

- **Type: a result-informed amendment** (Codex, item 3), not an implementation note. It adds seed, selection, trigger, fallback and budget rules to A20(i). The registered A20(i) text (A20, 2026-10-10T20:42Z) is not edited and is quoted in the annex (§1).
- **Disclosure (quoted with every A20(i) result; annex §0).** The rules below were fixed on 2026-10-13 (annex v1 02:20Z, v2 03:07Z, v3 03:55Z, v4 later on 2026-10-13) after the H-L differences had been read and before any A20(i) output existed. A stage-4 In31WO48 spin output with different settings (QE 7.5 CPU, MV 0.01 Ry, k3: M_tot 0.62 muB/cell, 19.5 meV below its nspin=1 energy) was read during the design and informed start B. Every rule listed here is result-informed.
- **Annex and frozen files.**
  - Annex: A20i_implementation_record.md v4, sha256 7b9d0c5bb265c6b2ecfe4dd358944a311c0331d00ae6170c6c73b11696fa3a6c (`codex/work_chat/annex/A42_A20i_implementation_record_v4.md`).
  - Comparator a20i_compare.py v4, sha256 87e2ae1c510477cfc961fd6f49b2fa45825182a6a5ffcfcfc1f1f7b984832949. Test a20i_compare_test.py v4, sha256 f24c84f2858e9016852fa2dcab1372fe21d814a4baa75765be8ddb35e248ad22: 47/47 PASS (WSL Python 3.12.3, and on lxplus Python 3.9.25 at the v4 install 2026-10-13T21:07Z). The 7 event-policy tests (E1a-E1d, E2a-E2c) were written first; the 5 counterexamples fail on the v3 comparator (42/47). Superseded: comparator v3 b7989ad6… (test a5a13114…, 40/40), whose 12 FIX_FIRST tests failed on v2 (27/40).
  - Manifest a20i_manifest.json, sha256 08c0741ea8badc67ac6f9a93e74cff149b4d5ae320f2a6ab9b39db4e12bb155d (embedded in the comparator).
  - Staged at lxplus `~/iwo_amorph/checks/gpumax_work/a20_spin/` (v4 installed 2026-10-13T21:07Z with the user's go; v3 copies kept in `v3_comparator_superseded_20261014T0000Z/`; `BUILD_v4_comparator_20261014T0000Z.txt`; nothing submitted): a20_spin.sub 1653ff567443f1312b4eee7edfee1c7c0d5443ab5a1cdee067e0782831c77568, a20_spin_fb.sub 7fee9ac937b930d9f1fdefdb4ddef0780f42b96bbfdac670a369eea9f5d322dd, README.txt a03cc045cb75f19cf02b6c6b068eb09d391ed311594ab6749782d6c9e2793671, MD5SUMS (65 files) a3c99f1d619d11b57762ff96489e977690490aca757b11fb4f47046a36da5748 (regenerated at the v4 install; md5sum -c: 0 non-OK). The 24 input sha256 values are in annex Appendix A (byte-identical since v1). The v2 comparator files are kept in `v2_comparator_superseded_20261013T0355Z/`.
- **Settings.** nspin 2, total magnetisation free, k 3x3x3, Gaussian 0.005 Ry, A19 SCF numerics (conv_thr 1e-8, plain beta 0.3, electron_maxstep 100), QE 7.3.1 GPU, on the six bound H-L geometries (annex §1a). Seeded atoms use the split labels O1/In1 with the same PAW files (pseudo md5 checked).
- **Starts (annex §3).**
  - A (the registered reading): 0.1 on W and its O first shell (< 2.6 A). In32O47: 0.1 on the 4 In bonded to the vacancy site. In32O48: matched sites.
  - B (cation-large, informed by the stage-4 output): 0.5 on W and on the vacancy-shell In, 0.1 on O1.
  - Seed units: QE reads starting_magnetization as a fractional polarisation of the valence charge (per valence electron). In1 = 0.5 is a large nominal seed (~6.5 muB per In1 atom in the starting density), not a 0.5 muB moment.
- **Readings and verdict (annex §4).**
  - Primary cell energy E_s = min(E_A, E_B, E_nspin1) over the counted starts: the lowest tested stationary state at fixed geometry, **not** a demonstrated spin ground state.
  - Triggers add: a shift > 50 meV or a k3 threshold flip in a registered difference, in the primary **or** in the start-A reading, makes H-L "not robust". min(A,B) and B-only are reported only. O72 never triggers.
  - A start-A trigger without a primary trigger (A above the lowest tested state) is labelled **"not robust to the registered spin-start branch; metastable start"**, with "primary reading unchanged".
  - A registered-difference cell where A counts and B does not is labelled **"second-start sensitivity unresolved"**; no two-start robustness is claimed. A missing start A gives "UNRESOLVED (registered start A incomplete)".
  - Split-label equivalence gate (annex §5): zero-moment starts reproduce the nspin=1 energy within 1e-5 Ry and In32O48 stays non-magnetic. A gate failure makes A20(i) UNRESOLVED, with the raw triggers shown.
- **Counting and binding (annex §6; Codex FIX_FIRST).**
  - Each attempt is bound to its submitted cluster.proc: attempt 1 from the saved stdout of `condor_submit a20_spin.sub | tee submit_attempt1.txt` and the line order of jobs.txt; a fallback from `condor_submit a20_spin_fb.sub | tee submit_fallback.txt` and fb_list.txt.
  - Only the bound job's events in the attempt's own user log are evaluated, in log order.
  - An attempt counts only if its bound job left the queue by termination and its archive passes every check. A valid archive of a removed job, or of a job still in the queue, never counts. This applies to both attempts.
  - Missing or ambiguous evidence (no submission record, no user log, events of another job, events out of order, more than one terminal event) leaves the start UNRESOLVED with no fallback.
- **Failures (annex §6).**
  - One A20(i) fallback per start (local-TF, beta 0.1, ndim 12, maxstep 300; new for A20(i), not A28's), labelled "fallback SCF path; branch may differ".
  - The fallback list is made mechanically: the comparator writes fb_list.txt and refuses once submit_fallback.txt exists. One user go covers all fallbacks; declining it makes A20(i) UNRESOLVED.
  - A running job is removed only after a system hold that followed > 1 h of running, or at wall time. Any other removal makes the start UNRESOLVED with no fallback. A removal is a system removal only with evidence in its reason (SYSTEM_PERIODIC_REMOVE / PeriodicRemove); a missing or unrecognised reason, or "by user condor", is UNRESOLVED with no fallback. Releasing a `condor_hold` of a running job, or a system hold after > 1 h of running, makes the start UNRESOLVED whatever follows.
  - Running A20(i) jobs are excluded from any pause. Monitoring is blind: no spin output is read before every start is final.
  - Deadline 2026-10-17T10:00Z (pw.x end time in the driver log).
- **Budget.** 12 spin single points (A20 total 18 with the 6 A20(ii) points) and at most 12 fallbacks. Each job uses 1 x A100/H100 (non-MIG), 8 CPU, 32 GB and 40 GB disk; ~6-15 GPU-h for the 12 first attempts (estimate); fallbacks add cost (at most 12, each estimated at up to ~4.7 h; an estimate, not a verified hard maximum). Submission after the GPU pause (Codex). No extra seed expansion (Codex).
- **Scope.** A20(i) is a **reported sensitivity; it does not replace the original registered score**. H-L stays UNRESOLVED overall (C038), ΔE_local(O30)'s unresolved significance (k-mesh) is unchanged, and nothing is adopted at k4. A "robust" A20(i) only bounds the shifts under these numerics. A moment found is not evidence of physical magnetism (PBE, k3, odd-electron metallic W cells). Chatratin et al. (Phys. Rev. Materials 3, 074604, 2019) include spin polarisation throughout, which supports testing spin sensitivity, not a magnetism claim.
- **Not changed.** The H-L predictions, thresholds and site rule (O30 registered, O72 sensitivity), A19, A20 (including its heading wording), A20(ii) and its result, A28 and C038.

### A43: administrative continuation after the 13 Oct GPU full stop: same epoch, preserved budget, no new allowance (result-informed administrative amendment, added after the pause began at 2026-10-13T03:13:17Z and before any paused job resumes; logged 2026-10-14T09:05Z; Codex review: Codex 2026-10-14T08:59Z: GO to log A43/D-46 after the text corrections (applied in draft v6); user go: 2026-10-14 ~08:50Z (work chat USER GO: log A43 and resubmit the two C4 polishes on their registered 1-GPU route); decision D-46)

- **Type: result-informed administrative continuation.** This is **not** a pre-pause suspension rule, and it is not backdated.
  - The pause began at **2026-10-13T03:13:17Z**, when `STOP 2026-10-13T03:13:17Z manual: full stop of GPU requests ...` was armed in segment_stop of the 7 DAG chains. The time is the stamp of that line, identical in all 7 files. User decision ~03:20Z; Codex GO-WITH-CHANGES for steps 1-3 (work chat 03:18Z/03:40Z).
  - This text was written after the pause began. It is logged before the first execution of any resumed job.
  - Information that may be known at logging, disclosed:
    - **the three segments running at the pause (outcomes known at logging, from dagman.out (local CEST minus 2 h) and the lineage-log label):**
      - aIO_2p0_s1 s2, job 12901845: terminated 2026-10-13T07:29:22Z, `segment relax_s2: CONTINUE`;
      - aIWO_0p7_s1_bare s2, job 12901160: terminated 08:23:19Z, `CONTINUE`;
      - aIWO_0p8_s2 s3, job 12901263 (A35 epoch): terminated 08:34:38Z, `CONTINUE`.
      All results were returned (relax_s<k>_results.tar.gz with saved input, lineage log and returned relax.in).
    - **guard-only retries (listed separately; each is one counted execution).** These node retries started and stopped at the armed segment_stop before pw.x, then were held: 12910599 (aIO_2p0_s1 s3, 08:35:17Z), 12910971 (aIWO_0p7_s1_bare s3, 08:35:18Z), 12911057 (aIWO_0p8_s2 s4, 08:35:19Z). They wrote RELAX_STATUS FAILED (stop, not a pw.x failure). Their DAGMans 12891110, 12884014 and 12884028 were removed at 20:55Z.
    - the removal records of the never-started jobs;
    - the queue and priority figures.
  - No energy, force or electronic quantity of any chain is used by this rule.
- **Scope.** The 7 DAG chains whose segment_stop was armed:
  - running at 03:13:17Z: aIO_2p0_s1 (job 12901845, rescue DAG 12891110), aIWO_0p7_s1_bare (12901160, DAG 12884014) and aIWO_0p8_s2 (12901263, A35 epoch, DAG 12884028);
  - idle and never started, DAGMan removed: aIO_2p0_s2 (DAGMan 12884189, node 12905862), aIWO_2p0_s1 (12884195, 12905564), aIWO_2p0_s2 (12884196, 12901989; A36) and aIWO_2p0_comp_s1 (12884377, 12901955; A36). Their relax.in md5s d2572847 / 08a6523e / 0df5ad47 / 09eab9f1 were kept.
  - It also covers the never-started non-DAG jobs that were removed: the C4 polishes 12904172 and 12904173, and the MACE GPU frames 12890593.0/.1.
- **Rule (Codex wording adopted).** The administrative continuation:
  - continues the same epoch;
  - retains each chain's existing remaining execution budget and prior rescue usage;
  - grants no additional A39 allowance.
  All terminal failures and restart gates remain binding.
  1. **Budget.** Each chain resumes with exactly the **remaining RELAX node executions before resumption, including the guard-only executions during the pause** (table 1b): 9 per DAG (RELAX + RETRY 8) minus the executions already used, where one execution is one cluster, guard-only node attempts are included, and an eviction or re-execution inside one cluster is not counted.
     - HTCondor would reset retries on the rescue submission. That count is never inherited.
     - **Configuration plus count enforcement (Codex).** The resubmission sets `DAGMAN_RESET_RETRIES_UPON_RESCUE = False` (DAG-local configuration, procedural). This governs only rescue files written after it is set; it cannot repair rescue files already written with reset counts (for example the files written when the four idle DAGMans were removed on 13 Oct).
     - Before any resumed execution, every chain's existing rescue file is read. The RELAX node's remaining `RETRY` is recorded and must satisfy RETRY + 1 <= the preserved remaining executions.
     - **An oversized rescue file is never used:** its chain is not resubmitted from it. No rescue file and no `RETRY` line is edited (A39: no edit of RETRY).
     - **Count-enforcement procedure (registered here; design GO-WITH-CHANGES from Codex 2026-10-13T21:31Z; drafts13oct/A43_count_enforcement_draft.md).** For each chain, after the archive move of item 7:
       - (a) new files in runs/<name>/ only:
         - `a43_dagman.config` containing exactly `DAGMAN_RESET_RETRIES_UPON_RESCUE = False`;
         - `<name>.a43.dag` = `<name>.dag` with exactly two changes: `RETRY RELAX <remaining - 1>` (4 / 4 / 3 / 7 / 7 / 7 / 7 for table (1b)) and one `CONFIG a43_dagman.config` line.
         Node submit files, relax.in and every existing file stay unchanged. There must be no rescue or recovery state under the new basename.
       - (b) `condor_submit_dag -no_submit <name>.a43.dag` writes `<name>.a43.dag.condor.sub`. It is reviewed and its sha256 recorded: exactly one scheduler-universe DAGMan job, the audited condor_dagman executable, the chain's run directory, `-Dag <name>.a43.dag` and `-DoRescueFrom 0`, and no other recovery or force option.
       - (c) Submission submits **that reviewed file** with `condor_submit <name>.a43.dag.condor.sub | tee submit_a43.txt`. It does not run `condor_submit_dag` again, which could regenerate the reviewed bytes. The submitted DAGMan ad is bound to the reviewed files (cluster from the submit record; its Cmd, Iwd and Arguments equal the reviewed file).
       - (d) After startup, the DAGMan header must report the False setting. **When retries occur**, every retry line must read "retry #k of <RETRY>"; a successful first execution writes none.
       - (e) **Any later invocation** of any DAG for the chain (A43 or A39) first recomputes the remaining budget and requires its registered authorization and reviewed DAG form. The False setting lowers the retries written into a later rescue file, but it does not stop a further invocation from adding an initial execution.
     - **Execution gate.** A DAG chain resumes only after this entry is logged, the F9 checker version that verifies (a)-(d) is frozen, and the first real `.condor.sub` and DAGMan ad are audited (Codex: "execution still requires the corrected checker and real-file audit").
     - **Measured 2026-10-13T21:08Z:** all seven existing rescue files read `RETRY RELAX 8` (DAGMAN_RESET_RETRIES_UPON_RESCUE was True in every DAGMan), i.e. 9 executions, above every chain's preserved remaining count. All seven DAG chains therefore resume only through the procedure above.
     - **aIO_2p0_s1 receives no fresh allowance because its existing rescue DAG 12891110 was removed.**
  2. **Prior rescue use.** The administrative continuation does not count as, consume, renew or replace the A39 administrative rescue ("once in total per chain"). A39 remains available afterwards only under its own trigger (retry exhaustion with the last segment CONTINUE or a resumed non-[scf] category). Prior rescue use is preserved as recorded in (1b).
     - **A39 +9 DAG form (registered here; changes A39's "existing .rescueNNN" action before any use; Codex 21:31Z (ii) and 21:47Z).** With `DAGMAN_RESET_RETRIES_UPON_RESCUE = False` kept, an exhausted chain's rescue file carries no fresh retries. A39's administrative rescue is therefore run as `<name>.a39.dag`: the original DAG with `RETRY RELAX 8` and the same `CONFIG` line. It is prepared, dry-run, submitted and bound exactly as in item 1 (a)-(e). It adds at most 9 RELAX executions, is available **once per chain**, and only after **genuine exhaustion**: remaining executions 0 and A39's existing trigger and eligibility (last segment CONTINUE or a resumed non-[scf] category; never after a terminal failure, a failed or missed qualification, a failed gate, parking or a cut). Nothing else in A39 changes.
  3. **Terminal and inherited status (unchanged rules; A43 adds no stop).**
     - A chain that wrote FAILED [scf] under a one-attempt rule (A28, A35, A36, D-43 F5), or that is parked or cut, is not resumed. These are the registered stops.
     - A failed restart gate or a failed or missed qualification is not a new stop. The chain keeps the status the registered rule gives it: under A35/A36 its relaxation becomes **exploratory**, inherited by descendants, and the chain may continue exactly as A35/A36 permit. That status is preserved across the pause and is not cleared or upgraded by it.
     - Clearing segment_stop does not clear segment_guard and revives nothing.
  4. **Same epoch, geometry and settings.**
     - A CONTINUE segment resumes from its returned relax.in.
     - A FAILED segment is handled only under README_D24_BD section 3 and its registered rule. A geometry-only reset from the independently verified bestvalid is allowed where that rule permits it.
     - An [infra] failure keeps the segment input (A30 rollback), **except** A34's documented case: a fatal GPU/CUDA error after a new validated geometry archives relax_s<k>_bestvalid.in (D-37 guard-ordering fix), and that case is recognised. It is **not usable** until its restoration evidence (the permitted rollback rule, the restored input, labels and resource request, and the failure evidence) is defined and reviewed. F9 v13 refuses it. Its scope stays the chains where that fix is installed (D-37: aIO_2p0_s1, aIO_2p0_s2, aIWO_2p0_s1, aIWO_2p0_s2, aIWO_2p0_comp_s1, aIWO_0p7_s1, aIWO_0p7_s1_bare; A34(ii): aIWO_1p0_Al2O3_s2). None of the seven paused chains needs it.
     - The A35/A36 one-attempt rules override all of this.
     - No setting, smearing, mixing, tolerance or submit file changes. The rescue DAG's local s0 is not a new physics epoch.
  5. **Gates.** Every mandatory restart gate applies across the pause boundary as at any segment boundary (A35 from s4; A36 from s2). A missing or unevaluable gate counts as failed. Qualification SCFs stay required as registered.
  6. **Never-started removed jobs.** They had no execution event (NumJobStarts 0), so they used no RELAX execution, no retry and no one-attempt rule.
     - DAG nodes resume through their chain's rescue file under items 1-5.
     - The C4 polishes and the MACE frames are **not** DAG chains: item 1 (rescue files, count-enforcement procedure) does not apply to them.
     - They may be resubmitted, after this entry is logged and with the user's go for the submission, as new clusters with byte-identical submit files and inputs (sha256 checked against the 12 Oct submission record checks/gpumax_work/submit_20261012T131733Z.log for the C4 polishes).
     - The removed cluster IDs (12904172, 12904173, 12890593.0/.1) are recorded and never count as attempts.
     - **F5 bound prospectively (D-43 is still a draft):** the resubmitted C4 polishes follow the reviewed F5 rule text, quoted in the annex `A43_annex_F5_rule.md` (sha256 of the F5 block 8aceddaaacf919c5d5e9c882efef05361610f122c1b99f964aea4a0260d155ac). It covers the one attempt, the infrastructure-stop repeat, the convergence deadline 17 Oct 10:00 UTC, the fresh final-geometry qualification due 20 Oct 12:00 UTC, the restart gates and the zero-step rule, and it starts at their first execution. A later D-43 logging may not weaken it for these two jobs.
     - The A34 14 Oct 12:00Z CPU fallback for the MACE frames is unchanged.
  7. **Evidence and order.** Before resumption, each chain's archives are moved to attempt<N>/ (README_D24_BD section 3) and indexed by (run, DAG generation, local segment, cluster).
     - A per-chain F9 transition record is written: schema iwo-f9-transition/2, kind section3_rescue, authorization `A43-<chain>`, with remaining_before = remaining_after = the (1b) value, prior_rescues and terminal_failure no.
     - The record is attached to the chain's first resumed execution, even if that is a guard-only node attempt. It is bound with the chain's A43 DAG files from item 1 (a)-(d). A guard-only first execution counts against the budget, but it does not move the chain's registered scientific position (the next pw.x segment keeps the pending transition, for example the A36 rescue start from bestvalid).
     - F9 checks it against this entry (basis `continuation_amendment`: result-informed; logged after the pause start and before the resumed first execution; state preserved; no additional executions).
  8. **Dates unchanged.** These are unchanged: the 17 Oct 10:00Z cutoff, the 18 Oct 22:00Z last submission, the A39 read-out rules and admission measurements (14 Oct 06:00-12:00Z), section 3 and every hypothesis, threshold and tolerance. The pause shifts no date.
- **Not claimed.** That the pause cost nothing. Queue position and internal optimizer or electronic state are not preserved; a resumed segment restarts fresh (registered fresh start) from the preserved geometry.
- **Annexes.** `codex/work_chat/annex/A43_administrative_continuation_draft_v6.md` (the full draft v6 with table (1b), sources and notes; sha256 1303449959737a2e5f76b68168d0cd0c0030001fcfa79ebf351b100b34d2c55d); `codex/work_chat/annex/A43_C4_F5_rule.md` (the F5 rule text bound in item 6; sha256 6981d3de16e6c5946d20318d52dcfc63d44c6eedce4578c434fb100c3056467c).
- **Correction (2026-10-14T09:32Z; Codex 2026-10-14 v15 reply; no rule change):** item 6 names the F5 annex `A43_annex_F5_rule.md` (its scratchpad draft name). The committed annex is `codex/work_chat/annex/A43_C4_F5_rule.md`, as the Annexes line above states; its content and sha256 are unchanged. Implementation facts are kept in `codex/work_chat/annex/A43_implementation_record.md`.
- **Procedural addendum (2026-10-14T13:48Z; Codex 2026-10-14 spool reply: "GO-WITH-CHANGES ... pin the new hash in an A43 procedural addendum"; no rule change).** The CERN schedd rejected plain `condor_submit` of the reviewed scheduler-universe <name>.a43.dag.condor.sub as a -spool submission (comp, 13:41:57Z; nothing queued; reconciled, STOP restored, no RELAX execution consumed). Submission is therefore made with DAGMan's documented path `condor_submit_dag -append "hold = True" <name>.a43.dag` from runs/<name>/. The reviewed file is kept as <name>.a43.dag.condor.sub.reviewed. The file regenerated with STOP armed (`-no_submit`, no `-update_submit`, which would forward an unreviewed DAGMan argument) differs from the reviewed one only by the line `hold = True`, and passes the frozen v20 DAG-identity and submission-grammar checks. Pinned regenerated hashes: aIWO_2p0_comp_s1 930e5fccfe6a72bfae1f4a39c874f539d98dd6c99f530610a4b5982bdaf1a52e (reviewed 42875cf2); aIWO_2p0_s1 b1defb84ecbadf8f7e0a110cd723ebfbd4be02cf0448d63e8ea277c12a6c71a7 (reviewed 68bca41b); aIO_2p0_s2 c39c85b8477ab341ad7cd8b7b35670675efb9600df99acadcb3b1d699079a802 (reviewed 607ecf2f); aIWO_2p0_s2 e9bb5e7ea0b466c22295a20aeb753eb5550fc4f32f6f588eafbac35a1ec3bc4e (reviewed 2522714c). Before release, the hash produced at submission must equal the pin, and the held-ad audit must pass. Order: comp, aIWO_2p0_s1, aIO_2p0_s2, aIWO_2p0_s2 (aIO_2p0_s1 parked). comp may retry only from its documented reconciled/no-job state, with its STOPPED history preserved.
- **Procedural addendum, version 2 (2026-10-14T13:55Z; Codex 2026-10-14: "GO - one comp-only diagnostic attempt"; no rule change).** Both submissions of comp (plain condor_submit, then condor_submit_dag -append "hold = True") were rejected by the bigbird26 schedd with the -spool error. Nothing was queued; both were reconciled; no RELAX execution was consumed. One diagnostic attempt for comp only uses `condor_submit_dag -append "hold = True" -append "should_transfer_files = NO" aIWO_2p0_comp_s1.a43.dag` (the DAGMan job runs on the shared AFS run directory; the RELAX/FINAL node files are unchanged). The regenerated file (STOP armed, -no_submit) = the reviewed file plus the two appended lines only, and passes frozen v20. Pinned: cc983bb8b9107d23d77b116d2f816cc338cb139cb4dd8ab3d8f2b2ff1ae92737. Release requires that pin, exactly one held, never-started DAGMan, the existing ad checks plus ShouldTransferFiles = "NO", and STOP verified cleared. If it is rejected again, the DAG submission route stops (escalation).
- **Procedural addendum, version 3 (2026-10-14T14:00Z; bounded exception to D-55; Codex 2026-10-14: "NO to the halt-file path ... Preferred alternative: one comp-only held diagnostic with transfer_output_files = \"\""; no rule change).** The diagnostic with should_transfer_files = NO was also rejected (13:55:49Z; reconciled; nothing queued). One more comp-only held attempt uses `condor_submit_dag -append "hold = True" -append 'transfer_output_files = ""' aIWO_2p0_comp_s1.a43.dag`. The regenerated file (STOP armed, -no_submit) = the reviewed file plus those two lines, passes frozen v20, and its dry-run ad has TransferOutput = "" (defined, empty). Pinned: a4debdb06fa2c2e0661ff6a053c061f504650da7a91109b6264a438e3796ae64. Release gates are unchanged (pin, one held never-started DAGMan, ad audit incl. TransferOutput = "", STOP verified cleared). Rollback: hold and reconcile for review; condor_rm only after positively establishing no child jobs.
- **Procedural addendum, version 4 (2026-10-14T14:12Z; D-57; Codex 2026-10-14: "GO to log D-57 and use the three pinned scripts in the proposed sequence"; no rule change).** The D-56 recipe (`-append "hold = True" -append 'transfer_output_files = ""'`) was accepted for comp (DAGMan 12926512, HEADER_OK, frozen-v20 post-run binding None). It now applies to aIWO_2p0_s1, then aIO_2p0_s2, then aIWO_2p0_s2. Each chain starts only after the previous chain's HEADER_OK, and each gets its own frozen-v20 post-submission binding. The regenerated files (STOP armed, -no_submit) equal the reviewed files plus those two lines. Pins: aIWO_2p0_s1 bebf8fd957ad4563975ac2424f6821d2789495ae98afab22011b3847b549d496, aIO_2p0_s2 615b1b90c4c67d6796b3831f1a41e3b0e441c16535cd2e94cb80eab3783b02f4, aIWO_2p0_s2 c2ff69015b7b35ad2d5d60d5e044c8acde91e53e4fbc4562c2d668deec6ba184. aIO_2p0_s1 stays parked. The gates and rollback are those of version 3.

### A44: blind evidence-audit scope exception: rc7 `certify`/`validate-cert` and frozen F9 before D-43, provenance binding only (procedural scope exception, added after the freeze, logged 2026-10-14T10:12Z, before any of these commands has run on an amorphous FINAL; Codex review: Codex 2026-10-14 (v16 reply, work chat 09:49Z): "GO-WITH-CHANGES for the blind evidence audit: permit (i) and (ii) under a logged scope exception"; user go: work chat USER GO: certify scope exception (the line is stamped "~10:30Z" but precedes the 10:00Z heading, so it was recorded before 10:00Z; the stamp is approximate); decision D-48)

- **Type: procedural scope exception for an audit.** It is **not** D-43 and not a read-out release. It does not authorize `cell`, `compare`, `series`, `hg` or `audit`, nor any electronic class or target quantity. Every registered score, the D-43 release order (draft Release_decision.md section B) and the A39 sight rules are unchanged.
- **Disclosure (Codex).** rc7 `certify` is not metadata-only. Its shared loader (cli.py:179 → data.py:105) parses eigenvalues, Fermi levels and projections inside the process.
  - Its normal output contains only provenance and gate information. This exception accepts that in-process parsing.
  - Nothing electronic is printed to a person, displayed or written to an audit summary.
  - Relaxation and SCF text outputs are read only by F9, through the frozen A39(a6) allowlist with its deny assertion (relaxation energies and forces allowed; Fermi energies, eigenvalues, DOS/PDOS and gaps refused). No other QE output is read.
- **Pinned inventory: 7 cells, A26 FINALs.** The input is `final_small.tar.gz` (sha256 below) from the verified local archive; the reader follows the EOS-layout directory beside the tarball.

  | Cell | FINAL | final_small.tar.gz sha256 |
  |---|---|---|
  | aIO_bulk_s1 | 12890432 | b427c1f77ad0fdd811d43ebaca66179b002e5144eff950a36cde9db54e9b16b1 |
  | aIWO_bulk_s1 | 12891160 | 4d9d799f8e1f7e18641a72dffd42c1398e64b620c1aa63af586a8faa947c6a59 |
  | aIO_1p0_s1 | 12891132 | 63a6ba5fd4ebce2268ea4a9a9b97bb8043482c61567f33ef18c521c36e21040a |
  | aIWO_1p0_s1 | 12889857 | ba93b4b3bef66dd94bf5eb8240458c1e653805730b7492504257aa9ab9b8da36 |
  | aIO_0p8_s1 | 12904001 | c2c3595895917303c51fd94441d1c7e17b9798d219d4846999c6ed24e0d506f6 |
  | aIO_0p7_s1 | 12894279 | ce62ecea308b1d2e1585268bbc63c3c1aa54e31f1edd260477cfbe0cfb6eca0d |
  | aIWO_0p7_s1 | 12902517 | 582257a4bf41c01aef6a909e8a3f03e00cf77110e9e4d16845ef897154bc85bc |

  - Local archive: `C:\Users\moham\iwo_exports_final_20261014` (outside OneDrive), with `SHA256MANIFEST.txt` sha256 43aaf7a68e286ba5822e6e9b0e56483310fb5f1dcf41bbef57e0d663f94e98df.
  - The manifest covers 56 files and 498003201 bytes. All 56 are equal in size and sha256 to the lxplus listing, and each in-job export manifest's entries equal the local files (annex A44_F13_size_table.md).
  - No 2.0 nm cell, C3 companion, polish or other run is in scope.
- **Pinned code.**
  - Reader: rc7 tag `readout-1.0.0-rc7-frozen-20261011T2249Z` (8a74a5e); code_sha256 fff642a13a62db6d0cde3e4704cdbf343913fc1972d9fa95d79f7ad8f4e01158; tests d8f96f26…; `git diff` against the tag is empty.
  - F9: frozen **v15** (D-47; tag `checker-v15-a9943bdc-frozen-20261014`): cert_assert.py a9943bdc, f9_writers.py 1830f33a, f9_common.py d251700f; writer fingerprint 0e346e3d. Drafts v16-v18 are not used; resource-route proofs that need the resolver stay UNRESOLVED.
  - Runner: `annex/A44_audit_runner.py`, sha256 e4593b0664ca213ec41e82e4afed75b448a7dcad8f6025f68d4da7235a0cb6df. It holds the exact commands and the sealing validator. A synthetic dry run (rc7 test builders, temporary folders) passed before logging.
- **Pinned environment (F11).** venv `C:\Users\moham\iwo_readout_venv_rc7`: Python 3.13.14, numpy 2.2.6 only, pip freeze sha256 a23aaf94250a9f53031a592980142245a848e2372b6c6c3093e8260b129265b8, Windows 11 build 26200 (annex A44_F11_venv_record.txt).
  - Frozen F9 v15 tests under it: 157/157 (`-I -B`).
  - rc7 reader tests: 217 OK, 3 skipped (IWO_D24_FIXTURE unset) and 1 failure, **disclosed**: test_nc_readout.test_golden_against_committed_original compares against `git show HEAD:…/nc_readout.py`. Since the freeze commit, HEAD holds the new nc_readout.py (c399ad05), not the rc0 original (28d63fca), so the test compares new with new. With HEAD at the rc0 original (a temporary repository), the test passes 4/4 under this venv.
  - nc_readout.py is not used by certify, validate-cert or F9.
  - IWO_REGISTER is the absolute path of the committed register containing this entry. F12 is **not met** (A40 and D-43 are not logged): the certificates bind this register's sha256, and that is disclosed.
- **Commands (exact; run from compute/amorph by the runner).** For each cell C with FINAL J, with T = the tarball above and AUD = `C:\Users\moham\iwo_release_audit_20261014`:
  0. Delete `analysis/__pycache__` immediately before. Then: code fingerprint check; `<venv>\python -E -B -m analysis crystalline` (REPRODUCED required); `<venv>\python -I -B f9_checker\cert_assert.py --self-test`.
  1. `<venv>\python -E -B -m analysis certify T --name C --out AUD\C\cert_C_final_J_r1.json --spec specs\spec_C.json --compiled-by "A44 blind evidence audit" --relaxation converged --relaxation-evidence --geometry mv --geometry-evidence`.
     - These are the registered intent for an A26 FINAL of a converged chain.
     - The evidence lists are empty, because no F9 evidence record exists yet. Missing evidence stays pending or underivable, and a certificate's hash binding alone establishes no qualification.
  2. `<venv>\python -E -B -m analysis validate-cert T --name C --certificate <cert>`.
  3. `<venv>\python -I -B f9_checker\cert_assert.py <cert> --json AUD\C\f9_C_r1.json`.
  4. On DOWNGRADE_REQUIRED, the certificate is recompiled with the statuses F9 permits, never stronger (`unknown`/`pending` → no claim): round r2, then r3 at most, steps 1-3 again. Every round is kept.
- **Sealing.**
  - stdout and stderr of every command go to `AUD\sealed\` before anything is read. Their sha256 and exit codes are logged in `AUD\commands.log`.
  - A key/type/value allowlist validator then reads them. It shows only:
    - validated hashes and file names;
    - provenance (code and register sha256);
    - qualification statuses: certificate_valid, relaxation, geometry, smearing_qualified, manifest_verified, pseudopotentials_bound, GATE and the F9 verdict/permitted statuses;
    - problem categories from fixed prefixes (no free text).
  - Unexpected output aborts that cell silently, with only the step, exit code and sealed-file sha256 shown: another key, type or value, non-empty stderr, a traceback, or unparsable text.
  - Sealed files are never displayed. F9 output is additionally checked against its frozen OUTPUT_KEYS/BLOCK_KEYS.
- **Audit artifacts (new).** `AUD` holds the certificates, sealed outputs, F9 JSONs, `step0.json`, `summary.json` (validated fields only) and `hash_table.txt`. They are not release outputs and do not satisfy D-43 step 2.
- **Afterwards.** The D-43 release still needs F1-F13 committed with their sha256 in its row, writer records audited by Codex, and F9 CLAIMS_OK for every certificate with its intended claims.
- **Annexes.** `codex/work_chat/annex/A44_audit_runner.py` (e4593b06…), `A44_F11_venv_record.txt` (65c38043…), `A44_F13_size_table.md` (439984d8…), `A44_F13_SHA256MANIFEST.txt` (43aaf7a6…).
- **Correction (2026-10-14T10:22Z; no rule change, no effect on any outcome):** the round-1 geometry claim `mv` in step 1 is the registered intent only for the MV-relaxed cells aIWO_1p0_s1 and aIWO_0p7_s1. aIO_bulk_s1 and aIWO_bulk_s1 (A23 Gaussian) and aIO_1p0_s1, aIO_0p8_s1 and aIO_0p7_s1 (A15 Gaussian) are native-Gaussian relaxations (A40 table), and no positive geometry status applies to them. Their round-1 `mv` claim was refused by F9 (no evidence), and the permitted status is `unknown`, so the audit outcome is unchanged. Relaxation `converged` is the intent for all seven.
- **Addendum 1 (2026-10-14T10:42Z; logged before processing; Codex 2026-10-14 reply to the release-prerequisite digest: "An A44-scoped local copy is acceptable ... Log the expanded inventory and selected checker version before processing"; relayed user go 2026-10-14).** Lineage/qualification evidence audit of the same 7 cells:
  - Inventory: annex A44_add1_lineage_inventory.txt (sha256 a1c5dcb19e40dc1cfcffb51e6f1f5e0cf9895807c97272ff33b88c349ca1ffe7): 124 run files (segment archives relax_s<k>_results.tar.gz, HTCondor user logs, driver stdout, DAG/dagman files, d24_transition.log, lineage_relax.dat, RELAX_STATUS, staged inputs, aIO_0p8_s1 attempt1_mv) and 10 EOS checkpoints relax_s<k>_<cluster>.tar.gz; 17943729 bytes (C: ~6.4 GB free; AFS 24% used). Copied byte-exact to C:\Users\moham\iwo_lineage_evidence_20261014 and verified against these lxplus sha256 values before processing.
  - Offset evidence: annex A44_add1_offset_evidence_lxplus.txt (sha256 4522cf3f9c63467a638c637d1bfc4898ec2c493ec92255bdb8ad35b376a86acf), captured read-only on lxplus9105 (Europe/Zurich, CEST) at 2026-10-14T10:37:32Z; validity 2026-03-29T01:00Z to 2026-10-25T01:00Z.
  - Checker: frozen **v18** (D-49): f9_writers.py cefc47db (writer fingerprint 8b1d39f1), f9_common.py 039ac64a, cert_assert.py 860bfab1, run with the F11 venv `-I -B`.
  - Processing: the frozen writers build relaxation_lineage records (route registered-MV for aIWO_1p0_s1 and aIWO_0p7_s1, registered-Gaussian otherwise) from the bound archives. QE output is read only through the frozen A39(a6) allowlist with its deny assertion. Members needed as files (relax.out, the saved or checkpoint relax.in) are copied byte-exact from their archives into a sealed folder and never displayed. Archive-identity records (iwo-f9-archive-identity/1) are written by the audit from the job-log cluster/segment mapping and cross-checked by the writers. Only DeriveError codes, record sha256 and F9 statuses are displayed. Then F9 v18 runs per cell on certificates carrying the records as evidence (rc7 certify/validate-cert as in A44 steps 1-2). Stop before `cell`.
  - Not in scope: any qualification SCF submission (separate user go); the C4 polishes 12920318 (finished) and 12920319 (running) are inventoried only (no polished FINAL or qualification exists to bind).
- **Provenance note (2026-10-14T11:05Z; Codex 2026-10-14 real-record audit: records FAITHFUL; mapping construction acceptable).** The archive-identity records used by addendum 1 are audit-created mapping records (written 2026-10-14 ~10:49:50Z from the user-log cluster/segment mapping, corroborated by DAGMan events), not in-job evidence. They are preserved byte-exact with their construction provenance in annex A44_add1_mapping_records/ (PROVENANCE.md dacf68ff).
- **Addendum 2 (2026-10-14T13:15Z; logged before processing; Codex v19 reply: "GO to freeze v19 ... then rebuild and check aIO_1p0_s1 only").** Checker frozen **v19** (D-50) is selected only to rebuild aIO_1p0_s1's relaxation_lineage record (same verified evidence and spec 12a537ce) and to rerun certify / validate-cert / F9 v19 on its certificate. The claims are relaxation converged only: geometry unknown, smearing pending, and the MV-then-Gaussian history is kept. The four FAITHFUL v18 records and their v18 results, and the earlier aIO_1p0_s1 downgrade records, stay unchanged; versions are not mixed. Stop before `cell`.

## 3. Experiment plan
- **Diagnostic set** (A12, recounted in A16):
  - S2-11 (redefined), S2-01 to S2-04, S2-06, S2-08, S2-12 and S2-13;
  - S2-14 to S2-17 and STRIP-6p3;
  - S3-01 to S3-03, S3-10 to S3-13 and S3-27;
  - AFF-2p0 and AFF-6p3;
  - S6-13 and S6-15.

  - **That is 26 entries and 26 launches, all pending.** The Q_f on/off pairs are already S2-14/16 and S2-15/17, so nothing is doubled.
  - **Per hypothesis:**
    - H-C, 9 launches: S2-01 to S2-04, S2-06, S2-08, S2-11, S2-12 and S2-13;
    - H-B, 5 launches: S2-14 to S2-17 and STRIP-6p3. The later frozen S6-24 to S6-26 add 3, so H-B costs 8 in total;
    - H-E, 5 launches;
    - H-F, 5 launches;
    - S6-13 and S6-15, 2 launches.
  - Revision 2 said "29 entries" and gave H-C as 10 launches; both were wrong. A first A16 draft said 30 launches, because it doubled S2-14 to S2-17; that was also wrong.
  - The set diagnoses mechanisms. H-A also needs the instrument records, H-D and H-J need S4 and S5, and H-G to H-K need DFT.
- **Kept out:**
  - S3-04 and S3-07 (duplicates);
  - the old S2-11;
  - BQP and Boltzmann, the FNORD duplicates, S2-05 and S2-07, S6-16 to S6-19 and S6-27.
  - S7: 2 exploratory stress runs, explicitly without a prediction.
- **S1-06 (two carriers).** One targeted continuation repair is allowed, preserving current and Poisson accuracy. It goes through a Codex check under the TCAD rule. Electron-only stays ASSUMED until it succeeds.
- **NC branch.** The quasi-2D NC is *provisional primary* at 2.0 nm. A 3-D NC robustness branch is calibrated separately in S4. The better starting RMSE of the 3-D NC does not select it.
- **Order:**
  1. S2 (S2-11 first);
  2. S3 confinement, then the AFF runs;
  3. IGZO, with S3-27;
  4. S3-10;
  5. tail runs;
  6. S4a in batches, then S4c;
  7. S5 (the 6.3 nm fold first);
  8. targeted S6;
  9. S7;
  10. conditional runs: contacts, N1, N2.

  Total about 110 to 140 launches; at least 46 remain uncommitted.
- **CERN** (access ends 21 Oct; UTC deadlines):
  - **12 Oct 18:00:** analysis code frozen. It must first reproduce the crystalline results: 3 % W-5d, ΔE_c 0.281 eV.
  - **Additions:** dispersion, normalised localisation, smearing audit.
  - **Final-SCF priority:**
    1. compensated, IWO and IO at 2.0 nm;
    2. s2;
    3. termination pairs;
    4. interfaces;
    5. the remaining thicknesses.
  - **17 Oct 10:00:** a relaxation that is not converged is labelled *exploratory*. Its final SCF and any relaxation eigenvalues used in its place are reported as exploratory fallbacks. They never stand in for converged primary tests. A primary test without converged geometry is *unresolved*.
  - **18 Oct 22:00:** last job submission.
  - **Export, frozen now.** Before scratch is lost, these are copied to EOS and to the repository (A14):
    - per-state projwfc projections, with atom and orbital maps and the completeness values (A16);
    - PDOS;
    - occupations and k-weights;
    - planar averages;
    - final geometries, with their lineage (which segment and validated step);
    - eigenvalues;
    - the actual inputs and logs of every segment;
    - the charge density for the 2.0 nm cells.
  - **19 to 21 Oct:** analysis.

## 4. Freeze list: tag before any S2 launch and any DFT final SCF
1. The registered predictions of H-A to H-K, with the section 0 rules (censoring, forecasts against tests).
2. The section 1 definitions.
3. Component failure rules, branch triggers (contacts, N1, N2, S1-06 repair), the calibration film and Q_f branch (H-B), and the calibration membership (H-J).
4. Scoring windows and stop rules, as in CAMPAIGN_DESIGN.md. Seed exclusions and the amendment history, as in SLAB_PROTOCOL.md.
5. The CERN deadlines (UTC) and the export requirements.
6. This amendment log.

## 5. Amendment log: revision 1 → revision 2 (2026-10-11, from Codex's ultra review)

| # | Change | Reason |
|---|---|---|
| A1 | S1-04 to S1-07 disclosed; budget corrected (14 used, 186 left); freeze deadline replaced | Procedure |
| A2 | H-B: the work-function rule withdrawn; calibration film and Q_f branch frozen; predictions required for both remaining films | Strip runs cannot identify ΔV0 |
| A3 | Band mobility separated from MUN | MUN includes roughness |
| A4 | H-D: scattering-branch ratio 0.20 to 0.35 restored | Lost in the merge |
| A5 | H-E: "twice the band" removed | It widened acceptance |
| A6 | H-E: affinity-only runs added | Confinement-off changes several inputs |
| A7 | H-F renamed "unexplained shape residual"; native S3-27 confirmation restored; contact trigger frozen | Codex |
| A8 | H-J forecasts re-attributed: Codex's withdrawn success forecast recorded | Misattribution in revision 1 |
| A9 | S2-01 and S2-02 retained as matched generation controls | Revision 1 assumed S2-03 dominates without proving it |
| A10 | H-G worded as consistency; host edge and LUMO separated; normalised localisation; N2 stays ASSUMED | Neutral PBE limits |
| A11 | N1 rigid mapping removed until affinity-only data exist | Mapping not established |
| A12 | Diagnostic set labelled diagnostic (the recount to 29 was itself wrong; see A16) | Count error in revision 1 |
| A13 | H-E 2.0 nm: −0.13 ± 0.03 V added as an S1-informed, pre-S3 registration. The original −0.23 ± 0.04 V is preserved and both are scored. New: S3-01 − S1-05 = −0.272 ± 0.010 V; AFF rigidity checks (±5 mV). "≥ 0.15 V without confinement" demoted to a forecast. N1 1:1 mapping, conditional on AFF. NC convention required for every fitted trap value. Quasi-2D I_on bias disclosed. The S1-05 registered failure stays recorded. | NC audit (no launches; `nc_audit/NC_AUDIT.md`). The band moves after S1 was seen: disclosed, before any S3 run |
| A14 | Exploratory-fallback rule replaces "substitute"; export requirements frozen | CERN scratch is temporary |
| A15 | **Proposed, needs the user's go:** CERN SCF rescue for the undoped aIO slabs and a final-SCF smearing audit (details below the table). The smearing change is a disclosed numerical amendment; the retry and GPU changes are procedural | aIO SCF failures, 10 Oct (work chat; Codex: CONCERN) |
| A16 | Corrections from the Codex re-check, plus the three confirmatory edits (details below the table) | Codex re-check 2026-10-11: FIX_FIRST, then FREEZE_OK_WITH_EDITS |
| A17 | H-L (oxygen vacancies, crystalline, 5 cells) added after the freeze, at 2026-10-10T18:48Z, before any vacancy structure was built or submitted. Predictions and settings frozen in the H-L section | User go for the vacancy jobs (D-19); plan item Q3 |
| A18 | H-M (HfO2 interface control, 2.0 nm) added after the freeze, at 2026-10-10T18:52Z, before the Hf PAW was installed or any structure was built | User kept HfO2 and approved the download and build (D-20) |
| A19 | H-L, before submission: both near-site candidates (O30, O72) are computed and the registered one is selected by the frozen shortest-bond rule on the H-L-relaxed host; convergence and SCF acceptance tightened; unfrozen numerical settings fixed | Independent pre-submission verification found a 0.0105 A tie and a QE 'final coordinates on BFGS failure' trap |
| A20 | H-L robustness: spin and smearing sensitivities (not registered), a 'not robust' rule above 50 meV, k3→k4 above 10 meV means unresolved significance, no substitution of uncomputed symmetry partners, limits stated | Codex CERN audit (CONCERN) item 6; user approved; before any H-L result |
| A21 | H-M limited to an alternative-interface control; Hf-specific MACE-vs-DFT force check, and 'not validated' if it fails | Codex CERN audit item 7; user approved; before any HfO2 structure |
| A22 | H-D: the amorphous dispersion/mass workflow is descoped; the mass-only prediction is reported as 'unresolved: not computed'; scattering branch and localisation kept | Codex CERN audit item 8; user approved; analysis-code freeze 12 Oct 18:00 UTC |
| A23 | Gap anchoring (measured anchor plus r·ΔE_g^PBE against the matching amorphous bulk); amorphous bulk PBE references; W-cell and a-In2O3-bulk HSE06 sensitivity checks with pre-set read-out rules | User request 2026-10-11 (D-25), before any of these was built |
| A24 | Interface cells: recipe kept; outer oxide face excluded from the H-I/H-M interface weight and from z_if; HfO2 crystallinity flags (MSD, q6) fixed, reported only | User decision 2026-10-11 (D-26), before any interface-cell DFT result |
| A25 | aIO_2p0_s1 only, while 2-GPU slots cannot match: 1 H100 NVL (non-MIG) with split species labels (In1/In2, O1/O2; same UPFs and settings) instead of A15's 2 GPUs. E0 gate (1e-5 Ry); split-vs-unsplit force check on aIO_1p0_s1 (≤ 1e-5 Ry/bohr) before any rollout; FINAL with the original labels; fallback: park (section 2, A25) | 2-GPU jobs match 0 slots; the 1-GPU run ran out of memory 16.6 MB short at its first force step. User go (D-27) after Codex GO-WITH-CHANGES, 2026-10-11T08:14Z, before any result |
| A26 | Gaussian 0.001 Ry reference FINALs allowed before the 2 nm smearing audit; audit, tolerances, selection and unresolved rules kept; self-comparison is not an audit pass; classifications conditional. First use: aIWO_1p0_s1 (-nk 1, D-24 item C export) (section 2, A26) | The audit cannot run before the 2 nm cells relax. User go (D-27) after Codex GO-WITH-CHANGES, 2026-10-11T08:14Z, before any result |
| A27 | H-N (exploratory): W extended-carrier efficacy against thickness. Frozen classes DONOR/ECB/PARTIAL and outcome rules (both 2 nm seeds DONOR; 0.7 nm decisive; bracket and reversal flags); controls: C1 paired substitution at 0.7 nm, C2 directional dilution, C3 widths, C4 Gaussian polish, C5 PAW->NC->HSE chain, C6 spin | User request after an external critique; Codex FREEZE-WITH-EDITS; D-28; before any slab electronic result |
| A28 | H-L: registered near cell In31WO47_near restarted from its best validated geometry with A19 settings; pre-declared fallback (local-TF, beta 0.1, maxstep 300, ndim 12) for this cell only if it fails again; UNRESOLVED if both fail or not converged by 17 Oct | User decision D-29, before any H-L energy difference |
| A29 | aIO_2p0_s1 only: NV_ACC_MEM_MANAGE=0 permitted (allocator; retained-memory cause ASSUMED); physics, A25 gates and force qualification unchanged; restart from geometry 0 | Second-SCF GPU out-of-memory after the passed A25 gate; Codex GO-WITH-CHANGES; user go (D-30) |
| A30 | Seven idle 1.5/2 nm chains (252-274 atoms): A25 split labels + A29 allocator on 1 x H100; physics unchanged; per-chain construction gate; OOM -> back to 2 GPUs; Al2O3 cells excluded | 2-GPU starvation (~22 h idle); S2 force check PASS (C035); A29 acceptance PASS; user go (D-31) |
| A31 | A15 audit: CPU FINAL route (64 cores, 200 GB, 250000 s), SCF path with frozen sibling-density fallback, original labels, width provisional without EA (amends A15 qualification), trap classes by predicates, common 0.001 Ry rule, named s2 backups | 2.0 nm FINALs exceed one H100; rc7 has no EA; Codex GO-WITH-CHANGES; user go (D-33) |
| A34 | Two 1-GPU split-label routes (A25 split + A29 allocator, 1 x H100 NVL non-MIG, QE_NK=1; physics unchanged). (i) 2.0 nm MACE force-check SCFs 12890593.0/.1: 28 CPUs / 86016 MB, JobPrio -10, no single-slot clause; crash/OOM -> hold 31; non-converged -> FAILED by the frozen comparator; fallback 14 Oct 12:00 UTC to the CPU route. (ii) aIWO_1p0_Al2O3_s2 (In/O split; Al, W, H kept): 28 CPUs / 84000 MB, extended hold (exit 1 < 1 h -> subcode 4); recovery-rule correction before the route starts (fatal GPU/CUDA errors checked before CONTINUE; FAILED [infra]; next retry holds, tested); OOM -> 12:39Z 2-GPU unsplit state; FAILED [scf] -> park, no rescue; exploratory regardless of completion time (non-convergence by 17 Oct 10:00 is an estimate and does not decide eligibility); no FINAL route. aIWO_2p0_Al2O3_s2: no route, stopped ~05:55Z (user decision); H-I expected UNRESOLVED | 2-GPU requests match 0 slots (idle since 10-11 Oct); live 2 nm chains on 1 H100 at 85.6-90.2 GB; internal reviews GO-WITH-CHANGES applied; Codex (i) GO, (ii) GO-WITH-CHANGES, three changes applied; user go (D-34) |
| A35 | aIWO_0p8_s2 only: Gaussian 0.005 Ry relaxation from relax_s2_bestvalid.in (s2 g1) with the A15 rescue settings, all else unchanged; one attempt (FAILED [scf] or not converged at 17 Oct 10:00 UTC -> 0.8 nm W class UNRESOLVED for H-N, NO CROSSOVER cannot be claimed, park); A15 force comparison UNRESOLVED by design for this cell (MV restart reproducibility about 5e-3 Ry/bohr); restart gate (1e-5 Ry, 1e-3 Ry/bohr) from s4 and a required fresh-start Gaussian qualification SCF at the final geometry (same tolerances), whatever the number of segments; gate evidence bound into the certificate; a failed or missing qualification or any earlier gate failure on the lineage -> relaxation=exploratory (excluded from primary scoring, certify.py:218), attached to descendants (new rule, modelled on section 3); mixed relaxation-smearing family in the W series disclosed; post-hoc disclosure of the 11 Oct 18:15Z MV release | Three MV SCF failures (s0 g14, s1 g11, s2 g2); restart non-reproducibility at production tolerance (finding E); Gaussian step pre-declared 2026-10-11T03:15Z; A15 pilot PASS on aIO_0p8_s1; Codex GO-WITH-CHANGES, all changes applied; user go (D-36) |
| A36 | aIWO_2p0_s2: Gaussian 0.005 + A15 aids from relax_s0_bestvalid.in (2223d6cf; staged 0df5ad47); aIWO_2p0_comp_s1: MV 0.01 + aids (8aacdf98; staged 09eab9f1); all else unchanged; one attempt each (FAILED [scf] or not converged at 17 Oct 10:00 UTC -> roles UNRESOLVED, park); conditional Gaussian-plus-aids rescue of aIWO_2p0_s1 on FAILED [scf] (loses its MV comparison: A15 2.0 nm check UNRESOLVED); C4 eligibility and reader unchanged, so the H-N 2.0 nm endpoint is UNRESOLVED for any seed without an MV-to-Gaussian C4 polish; A35 restart gate from s2, required qualification SCF (FINAL may run concurrently, primary scoring waits), certificate binding and exploratory rule; mixed smearing in the 2.0 nm W class disclosed | s2: SCF stall at 7-9x conv_thr (g3); comp: iteration-limit failure (1.7e-7 at 200); MV failure tally 3/14 SCFs at 2.0 nm W; Codex GO-WITH-CHANGES, all changes applied; user go (D-40) |
| A37 | H-N thick endpoint UNRESOLVED in every branch (aIWO_2p0_s2 has no MV-converged parent, A36; native-Gaussian eligibility declined). Formal reporting override: the registered H-N outcome is UNRESOLVED whatever rc7 hn_outcome returns. Both 2.0 nm seeds stay in the registered series. The raw rc7 output and both seed records are kept as diagnostics. 2.0 nm seed differences are reported as lineage-confounded cell discrepancies. C2 and C5 cut with their requirements kept (unmet). C1 and C6 at 0.7 nm kept. Footnote † for the partial unblinding. Logged before any H-N class exists | A36 C4 point; Codex 13:15Z, 14:54Z, 15:08Z; D-42 |
| A38 | Result-informed amendment (not an erratum): the stop action of ML_VALIDATION.md:32 (and the matching D-12 stop clause) is overridden for aIWO_2p0_s1, so no stop and no anneal. The trigger is kept: compare_val.py d0179e1 (4ae21f15) D8 on both aIWO_2p0_s1 frames. One SCORED frame > 0.30 eV/Å = TRIGGERED even if its partner is missing; NOT_TRIGGERED needs both SCORED ≤ 0.30. TRIGGERED attaches a fixed topology-representativeness limitation to every 2.0 nm result, and the superseded action is disclosed in every branch. Blind geometry-identity check of the 'final' frame against the s0 relax input, with a prior-exposure label. Ordinary FAIL continuation (ML_VALIDATION.md:28-31) unchanged | Remedy infeasible before the cutoff; C037 and s1 forces known; 'final' frame probably not blind; Codex 15:08Z; D-42 |
| A39 | Cutoff read-out rules. Converged chains (A19 verified <= cutoff) are read out at their actual final geometry; a pending qualification is due by 20 Oct 12:00Z only if no gate failed. G* is for exploratory chains only: the lowest-F validated evaluation of the last settings epoch with verified pre-cutoff timing (job-log termination, or a snapshot completed by 10:00:00Z with execution approval); overhang is excluded and listed. Ties measured from the set minimum (1e-5 Ry, then 1e-6 Ry/bohr, then the latest position). Allowlist-gated F9 cutoff_selection writer. Residual-force report. Route: registered CPU FINAL at G* only if admitted on 14 Oct (q + T + X <= 80 h, conservative T and X = 6 h; S - P slots); otherwise no read-out (no automatic fallback). Exploratory artifacts verified by 20 Oct 18:00Z; primary qualifications by 12:00Z. Read-outs submitted idle; held jobs released within 24 h; removed jobs are new submissions, allowed only before 18 Oct 22:00Z. Export P0-P4: AFS primary, verified, quota and sizes checked, A14 gaps preserved. The extension shifts only unpassed dates and never revives failures. One administrative rescue DAG per chain in total (<= 9 additional RELAX executions; never after a terminal failure) | Section 3 leaves the geometry, route and order undefined; Codex 04:19Z, 15:08Z and 15:56Z; D-42 |
| A40 | C3 width companions 0.002/0.005 Ry against the A26 0.001 Ry reference: one changed physical line (diff gate, derived from the inputs); fresh start. Density-seeded comparisons (A31(b) fallback) are reported, never counted (series C3, A31(e), F9); any applicable FAIL, fresh or density-seeded, blocks qualification. C3 applies only to the geometry it ran on: polished-geometry comparisons never qualify an MV geometry. Polished geometries for the C4 W cells. MV-geometry companions retained for the 0.7 nm H-H reference (aIWO_0p7_s1 MV, bare), otherwise H-H 0.7 nm UNRESOLVED. Native-Gaussian exceptions aIWO_2p0_s2 (A36) and aIWO_0p8_s2 (A35). Zero-step polish reuse only with an actual converged polish, exact geometry/settings/UPF identity, a fresh final-geometry qualification and newly bound evidence. 2.0 nm: audit comparisons reused as C3; non-duplicated C3 kept where primary qualification needs it; 2.0 nm C6 cut, spin robustness "untested". Cell-local C3 PASS with the class UNRESOLVED is legitimate | Density-seeding changes eligibility; Codex 15:08Z and 15:56Z; finding E; D-43 (release decision, renumbered from D-42) |
| A41 | Resolution-method sign-off: scorer c0f28bb9; signed-off constants RES_SUPPORT_MIN 3, RES_NEAR_DEC 1, RES_BIAS_COVERAGE 1.0, RATIO_RTOL 1e-3, OXIDE_LINES_UM (0.002, 0.017); an ASSUMED operational method; one decade = the tightest value both S1 pairs satisfy (disclosed); pair agreement = numerical stability under the tested intervention, not an absolute bound; scope = quantity, film, physical settings, bias range and numerical endpoint (hc_mesh: verified finer refinement); the pair under test is never its own evidence; the shared run_0067 baseline is recorded, not independent. Scope of A41: S2-11, S0-02-DOS2 and the refinement triggers for S2-04, S2-06, S2-08. S2-11 rerun once: same entry and label, first entry of campaign_C10_DIAGb with `--retry S2-11` (STARTED-row rule: --retry only while no newer c10_s2_11_2p0 row exists); the A41 pre-launch gate (environment, frozen files, deck/material hashes, no DeckBuild/ATLAS/TonyPlot or runner process, RUN_INDEX state, sealed inventory, budget; explicit equality) before every invocation, including a resume; committed runner 1375164 (state-only, viewers recorded); DIAGa held. The registered S2-11 run is the rerun, labelled "S1-informed operational method; S2 blinding cannot be demonstrated; possibly exposed; not viewed according to the user's statement"; run_0075 is kept, sealed (config/sealed_runs.json), invalid and never substituted; viewer-close method UNKNOWN. S0-02-DOS2 added (c10_s0_02_dos2_2p0 = run_0067 overrides with numa/numd 768/384 only; acceptor quadrature only, numerical): the I_G resolution pair with run_0067 for hc_mesh, R cited verbatim; reproducibility, not an absolute tunnelling error bound. Frozen hc_explains trigger (no resolution inputs; branch B an operational spending screen, the raw UNRESOLVED verdict kept) for matched oxide-mesh refinements of S2-04, S2-06 and S2-08 (labels registered; at most 6 launches; scorer REG/PIN extension only, first; OOM = UNRESOLVED; I_G mesh stability only, a non-PROVISIONAL hc_explains still needs I_D resolution evidence for mechanism and control); nominal and generation nulls stay PROVISIONAL/UNRESOLVED. Order kept: S2-11 first, then S0-02-DOS2, then the S2 mechanisms (expected run_0076, run_0077). Sealed-aware regression gate: committed wrapper regress_sealed_aware.py with the explicit inventory config/sealed_runs.json (A41 runs appended right after they start). C10 15 -> 17/200 (effective reserve 9); global 75 -> 77/260 | run_0075 timed out behind a TonyPlot viewer, so it is invalid under the frozen timeout rule; its output was displayed before the sign-off ("not viewed", user statement, D-42 (3); "possibly exposed", Codex D7). No I_G resolution pair existed for S2-11. Codex round 3 (adaptive amendment, 15:50Z), freeze GO 16:08Z and GO-WITH-CHANGES on A41 (2026-10-13T01:32Z, six changes applied in revision 3); user go ~00:05Z (work chat 00:15Z) subject to Codex review; D-44 |
| A42 | Result-informed A20(i) implementation for H-L (annex A20i_implementation_record.md v4, 7b9d0c5b): two starts (A = registered small seed on W + O first shell; B = cation-large, stage-4-informed), primary min(E_A, E_B, E_nspin1) (lowest tested stationary state), additive start-A trigger labelled "not robust to the registered spin-start branch; metastable start" when only A triggers, "second-start sensitivity unresolved" for a missing B, split-label gate, one mechanical fallback with one go, counting bound to the submitted cluster.proc with a disposition veto for both attempts, removal-reason evidence and the hold/release sequence enforced (comparator v4 87e2ae1c), deadline 17 Oct 10:00Z; reported sensitivity, does not replace the original registered score | Codex 03:26Z reply (GO-WITH-CHANGES, FIX_FIRST applied); result-informed, before any A20(i) output; user go 2026-10-13 ~04:15Z (work chat USER GO item 3, conditional on Codex review; met); D-45 |
| A43 | Result-informed administrative continuation after the 13 Oct GPU full stop (pause from 2026-10-13T03:13:17Z; logged after it, before any resumption; not backdated): same epoch, each chain's remaining RELAX executions, prior rescue use, terminal status and restart gates preserved; no additional A39 allowance (A39 stays once per chain under its own trigger); rescue-retry reset never inherited; DAG chains resume only through the registered A43 DAG form (RETRY = remaining - 1, DAGMAN_RESET_RETRIES_UPON_RESCUE = False, reviewed -no_submit .condor.sub submitted with condor_submit, DAGMan ad bound) after the corrected F9 checker and a real-file audit; A39's +9 registered as its own DAG form (genuine exhaustion, once per chain); never-started removed jobs are not attempts (C4 polishes and MACE frames resubmittable as byte-identical new clusters with the user's go); 7 DAG chains + C4 polishes 12904172/3 + MACE 12890593.0/.1; dates unchanged | Codex review of checker v9 (case 2), the full stop (03:18Z reply), the count-enforcement design (21:31Z) and A43 v4 (21:47Z): Codex 2026-10-14T08:59Z: GO to log A43/D-46 after the text corrections (applied in draft v6); user go 2026-10-14 ~08:50Z (work chat USER GO: log A43 and resubmit the two C4 polishes on their registered 1-GPU route); D-46 |
| A44 | Blind evidence-audit scope exception (procedural; not D-43): rc7 certify/validate-cert (provenance binding only) and frozen F9 on the 7 pinned thin/bulk A26 FINALs from the verified local archive, F11 venv, sealed outputs and an allowlist validator; no cell/compare/series | Codex v16 reply GO-WITH-CHANGES; user go; D-48 (row added 2026-10-14T10:35Z with A40) |

**A15 in detail (proposed):**
- **Pilot:** Gaussian 0.005 Ry on aIO_0p8_s1, with β = 0.1, local-TF, mixing_ndim 12, at most 300 iterations, and the SCF tolerance unchanged. A consistent rescue rule is applied to the other aIO slabs only after the pilot succeeds.
- **Retries:** exit codes CONVERGED 0, valid continuation 1, hard failure 2, with `RETRY RELAX 8 UNLESS-EXIT 2`.
- **Restarts:** a restart geometry is accepted only after a converged SCF and an accepted ionic step. The `steps_relax.sh` classification is repaired; the exit codes alone are not enough. The inputs, logs and geometry lineage are archived.
- **GPUs:** aIO_2p0_s1 runs on 2 GPUs with `QE_NK=1`.
- **Smearing audit for the final SCF:**
  - 0.005 → 0.002 → 0.001 Ry, at fixed geometry, on the 2.0 nm aIO, aIWO and compensated cells.
  - **Acceptance:** edges and EA within 0.05 eV, trap classes unchanged, donated charge within 5 percentage points.
  - **Selection:** the final smearing is the largest value whose observables agree with the 0.001 Ry result. If 0.001 Ry does not converge, or no value agrees, the affected quantities are *unresolved*.
- **Force check:** a single-point force comparison, MV 0.01 against Gaussian 0.005, on one 2.0 nm aIWO geometry. If max |ΔF| > 1e-3 Ry/bohr, the family difference in relaxation smearing is reported as a geometry uncertainty.
- **Fixed occupations:** used only after a global gap has been shown.

**A16 in detail:**
- **DFT accounting (section 1):**
  - projection normalisation and completeness;
  - the PR_n atom domain;
  - occupations and k-weights;
  - the N_v band split and the nominal N_ex denominator;
  - an operational host-edge rule.
- **A13 wording corrected:**
  - S3-01 − S1-05 keeps the mass-dependent NC change and is not independent of the 2.0 nm band;
  - +0.86 mV is a local surrogate, and 7–8 % is an inferred bias;
  - 18 % is a net counterfactual.
- **Sign corrected to ΔV_th = +Δ(ΔE_c) = −Δχ** in N1 and in NC_AUDIT.md. The audit's NC-equivalence statement now says that trap depths increase.
- **AFF scoring frozen** (H-E).
- **H-I:** the fixed 0.2 eV target is restored, with a frozen outcome rule. Revision 2 had added the seed spread to the bound without logging it.
- **Seen-results disclosure corrected** (section 0).
- **Diagnostic set recounted** to 26 entries and 26 launches. H-C costs 9 launches and H-B 5 + 3.
- **A14 export list completed:** per-state projections with maps and completeness, occupations, k-weights, inputs, logs and geometry lineage.
- **Confirmatory edits (FREEZE_OK_WITH_EDITS):**
  - S2-14 to S2-17 are no longer doubled (26 launches);
  - an empty interior gives an unresolved host edge;
  - the electron-accounting partition is worded as such, with an all-band gap-state search against a separate host valence edge; fractions are N/A when N_ex = 0.
