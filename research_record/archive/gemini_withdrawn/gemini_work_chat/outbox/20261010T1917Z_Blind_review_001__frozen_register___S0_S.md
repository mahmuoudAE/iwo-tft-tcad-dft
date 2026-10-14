You are the independent theoretical critic for a research project on ultrathin tungsten-doped indium oxide (IWO, W:In2O3) thin-film transistors. The project combines:
- measured transfer curves from the user's own fab (films of 2.0, 6.3 and 13.2 nm; published as Januar et al., Small Structures 2026);
- Silvaco ATLAS device simulations;
- Quantum ESPRESSO DFT of crystalline and amorphous slabs (PBE, PAW), including slabs below 1 nm.

The target is a Nature-level paper. No new measurements are possible. Compute ends on 21 Oct 2026.

**Your role:**
- You are *blind*. You see raw data, definitions and pre-registered predictions. You do not see the other reviewers' verdicts (another AI reviewer exists; its conclusions are withheld from you on purpose).
- Find what is wrong, what is unjustified, and what alternative physics would explain the same observations.
- Derive limiting cases and order-of-magnitude checks yourself.
- Say which existing or planned calculation would discriminate between the explanations.
- Be concrete: cite equations, numbers and the file or section you are criticising.
- Prefer primary literature. Give a DOI or URL for every literature claim, and never invent a reference. If you are unsure, say "unknown".
- You cannot run anything. Do not propose new measurements as the solution; you may say what a measurement *would* decide.

**Reply format:**
1. **Verdict:** AGREE, CONCERN or DISAGREE, with one sentence why.
2. **Strongest objections,** ranked. For each: the location, the problem, and why it matters for the claim.
3. **Alternative mechanisms,** and the existing or planned calculation that would distinguish each from the favoured one.
4. **Errors** in definitions, arithmetic, units, signs or logic, with their location.
5. **Literature,** with a DOI or URL for each entry.
6. **What evidence would change your verdict.**


---

# Blind review 001: frozen register + S0/S1 results

**Task: blind review of the frozen hypothesis register and the first simulation results.**

Attached:
- the frozen hypothesis register (revision 2, frozen 2026-10-10T18:33Z, plus post-freeze amendments A17 and A18);
- the campaign design for the ATLAS runs;
- the DFT-to-TCAD input mapping;
- the raw results of the first ATLAS stages (S0 smoke tests, S1 baselines) as JSON;
- the measured transfer-curve data (clean CSV and data summary).

Please answer, in the reply format of your role:
1. Which registered predictions are **weak**? That is, predictions that are trivially satisfied, unfalsifiable in practice, or whose pass band is wider than the effect they claim to test. Give the hypothesis ID and the line.
2. Which **alternative mechanisms** for the three central observations are missing, and which existing or planned run would discriminate each from the favoured one? The three observations are:
   - the off-current floor at 2.0 nm (about 4.6e-15 A/µm) and how it scales with thickness;
   - the threshold-voltage shift with thickness;
   - the mobility drop with thinning.
3. Are there **errors**? Check the definitions (host edge, localisation PR_n, excess-electron accounting, the censoring rule), the arithmetic (bands, launch counts), the units and the signs (e.g. ΔV_th = +Δ(ΔE_c) = −Δχ).
4. In S1, the 3-D density-of-states run (S1-05) shifted V_th,cc by +142 mV against a registered +40 to +70 mV. The register attributes this to trapped charge in the acceptor tail amplifying a 37.5 meV statistics shift. **From the numbers alone**, is that plausible? What else could produce it?
5. The DFT part uses neutral, spin-unpolarised PBE slabs (0.7–2.0 nm, amorphous, ML-generated structures, OH-terminated, about 2 % W). Which DFT conclusions in the register **cannot** be supported by such cells, whatever the outcome?

Constraints: no new measurements; CERN compute until 21 Oct; 186 ATLAS launches left.


=== FILE: HYPOTHESIS_REGISTER.md (sha256 71f8f8ca6f7b) ===
# Hypothesis register: IWO TFT TCAD + DFT, revision 2

**Status: FROZEN, 2026-10-10T18:33:13Z** (user approval, decision log D-17; git tag `register-rev2-frozen-20261010T1833Z`). From now on, every change is a logged amendment, and the frozen predictions stay scored.
- Revision 1 is kept unchanged in `HYPOTHESIS_REGISTER_rev1.md`. Every change from revision 1 is listed in section 5 as an amendment (A1 to A16; A17 and A18 added after the freeze).
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


=== FILE: CAMPAIGN_DESIGN.md (sha256 710e56edc3fd) ===
# ATLAS campaign design, 2026-10-10 (at most 200 sequential launches)

**What this is.** One merged campaign design built from three independent inputs:
- `DFT_TO_TCAD.md` / `dft_inputs.json` (DFT → TCAD inputs);
- `GENERATOR_AUDIT.md` (what the generator and ATLAS 5.28 can do);
- `codex_design.md` (Codex's independent design).

Where they disagree, §2 states the disagreement and the choice. The run list is in `campaign_matrix.json`, generated by `make_campaign_matrix.py`. That script only does arithmetic and launches nothing.

Codex then reviewed this merged design, read-only (`codex_review_2026-10-10.md`; prompt `codex_review_prompt_2026-10-10.md`). Its arithmetic check reproduced every start value, constant and count. §2.1 lists which review points were adopted and which were not.

**Nothing was launched to write this.** No `deckbuild.exe`, no `run_atlas.py` and no `run_campaign.py` were run. The only code run was:
- `make_campaign_matrix.py`;
- one deck-*text* check through `build_deck()` (no `subprocess`/`deckbuild` in that module). It confirmed that every existing-key override in the matrix reaches the deck, for example `tmun=0`, `carriers=2`, the MODELS strings and the fit3 χ/E_g/m* values.

No file in `data/`, `results/`, `config/` or any registered file was changed.

**Labels.** COMPUTED (our DFT, file cited), MEASURED (target devices), LITERATURE (cited), FITTED (to named data), ASSUMED. CALCULATED and MODEL are used as in `DFT_TO_TCAD.md`. **Calibration is never called validation.** The only out-of-sample evidence this campaign can give is the retrospective leave-one-film-out (LOO) in S5. It is labelled *retrospective*, because all four curves have already been seen.

---

## 1. Bottom line

1. **One shared model for the 2.0/6.3/13.2 nm films.**
   - Five FITTED shared parameters: the alignment offset ΔV₀ (written as one Q_f), μ∞, the scattering length ℓ, the integrated tail N_s and the tail width W_T.
   - One conditional sixth parameter: GAMMA0, only if the IGZO.TOKYO branch is adopted.
   - No per-film Q_f or mobility. Every DFT quantity enters as COMPUTED, or as a law FITTED to COMPUTED DFT points (no device data): ΔE_c(t), ΔE_g(t), Δm*(t), quasi-2D NC300 at 2 nm, and the DFT mass factor in the mobility law.
2. **Three of the five fitted parameters cost no launches.**
   - A uniform front Q_f shifts the transfer curve rigidly.
   - With a constant or IGZO mobility, I_D is proportional to MUN.
   - Both hold exactly in the continuum equations, apart from the SRH term, which is ≥ 1e14 below the currents (§5.2). Both were already used in this project (V2 T0, the campaign B recalibration). But V2 T2 missed its transformation-based RMSE prediction at 2 nm by 0.006 dec.
   - So two native checks come first: S1-07 (constant μ) and S3-27 (IGZO). Then ΔV₀, μ∞ and ℓ are profiled offline from each launched film triple, and every optimum is confirmed natively.
   - Launches go to N_s, W_T (and GAMMA0) and to model form.
3. **The off-state floor gets quantitative tests, not assumptions.**
   - Gate leakage: 11 launches with self-consistent tunnelling (QTNLSC.EL, FNORD) and defect-assisted oxide TAT (ITAT.SC.EL), at nominal LITERATURE and deliberately leakage-maximising oxide parameters, at all three films. It is scored as I_G and I_D versus the measured floor, plus flatness in V_G.
   - SRH/TAT generation: 3 two-carrier bounds with extreme lifetimes and capture cross-sections.
   - The ungated strip: 7 separate-deck runs (2 of them Q_f-off controls) plus 1 in-solver run.
   - All verdicts are fixed before the runs (§7).
4. **Budget.** 181 planned launches + 19 reserve = 200.
   - Typical wall time about 43 h for the 181 (timeout-sum upper bound about 112 h); add about 4 h if the reserve is used.
   - Smoke stage of 2 runs first. 10-run minimum set in §9.
5. **Expected outcome, stated now.** The shared model will probably not fit 6.3 nm. Both a monotonic mobility law and a monotonic DFT shift fail on a film whose on-current is *below* that of 2.0 nm (I_on ×0.79 from 2.0 → 6.3 nm). The design keeps that failure visible: no per-film rescue parameters, and the shift/shape decomposition is reported (§5.4).

---

## 2. Where the inputs disagree, and the choice

| # | Issue | Codex | Audit / DFT | Choice and reason |
|---|---|---|---|---|
| D1 | Where Q_f sits | IWO/Air (run_0040 `device.in` l.98) | IWO/Al2O3 at y = 0 | **Audit.** The generator line 249 writes `interface qf=… y.min=-1e-7 y.max=1e-7`, which encloses only y = 0 (the IWO/Al2O3 boundary). The state file's "QF works on IWO/Air" is a tool fact, not the placement. The back-surface Q_b exists separately. |
| D2 | ΔE_c above 2 nm | (2/t)² continuation (ASSUMED): 0.028 / 0.0065 eV at 6.3 / 13.2 nm | 3-point law fit3 through the 0.695/0.930/1.962 nm DFT points: 0.062 / 0.023 eV; spread 0.046–0.062 / 0.013–0.024 | **DFT fit3 as primary.** It uses all three DFT points; Codex saw only the 2 nm point. The low end (box MODEL, below Codex's t⁻²) and the HSE high end (×1.107) are run in S6. The whole spread is ≤ 34 meV at 6.3 nm, far below the 0.23–0.37 V miss. |
| D3 | Bulk mass | 0.159 m0 (PBE, COMPUTED) + Δm | 0.208 m0 (LITERATURE, Stokey 2021) + Δm (V2) | **0.208 + Δm(t), DFT increment.** PBE underestimates the band mass because its gap is too small (Kane α 0.63/eV), while Stokey is an optical-Hall measurement on In2O3. The 0.159 choice is one S6 profile (3 runs). |
| D4 | Codex Q4 run 10: 13.2 nm Schottky 0.7 eV as a floor test | proposed | Schottky is on-state only | **Dropped as a floor test.** In a single-channel deck the depleted channel offers no collection path that makes a contact *create* a V_G-flat floor. Thermionic reverse leakage needs a conducting path to the other contact, which Codex itself states. The contact can still change the off-state current, so the S3 Schottky runs also report the floor metrics. Schottky stays as a branch at the low barriers favoured by In2O3 pinning (0.2/0.5 eV, 7 runs). |
| D5 | Calibration launches | 84 = 18×3 + 10×3, all 5 parameters by launch | not covered | **69 launches** over (N_s, W_T[, GAMMA0]). ΔV₀, μ∞ and ℓ are profiled exactly (§5.2). 4c confirms natively and 4d re-checks the runner-up branch. The saved launches go to the leakage tests and model branches. |
| D6 | LOO | 36: 5 candidates × 2 training films + 2 predictions per fold | — | **30.** The S4a design was fixed before any data, so its archive is shared legitimately by all folds. Per fold: 4 adaptive candidates on the training films only, plus 2 frozen held-out predictions. S4b is excluded from LOO because it saw all films. |
| D7 | Deep Gaussian and D_it sheet | ASSUMED 0 in the primary | V2 keeps 5e16 cm⁻³eV⁻¹ at E_c−0.6 eV and 3e11 cm⁻²eV⁻¹ at E_c−0.3 eV (both ASSUMED) | **Keep the V2 values** (realistic, literature-motivated magnitudes, continuity with V1/V2). Run the zero alternative in S6 (3 runs). |
| D8 | Mobility shape model | "test conditionally" | IGZO.TOKYO recommended (high relevance) | **Test in S3** (6 runs). Adopt by the rule in §6. NCRIT is fixed (ASSUMED 1e20 cm⁻³) because μ0·NCRIT^(−γ/2) is one number; only GAMMA0 can be fitted. |
| D9 | SRH | keep, ASSUMED background; one two-carrier and one SRH-off run | already ON; CALCULATED bound ≤ 8e-29 A/µm (audit §7.1) | **Keep SRH ON** (τ = 1e-6 s, σ = 1e-15 cm², ASSUMED). Add **extreme bounds** (τ = 1e-9 s, σ = 1e-13 cm², plus TRAP.TUNNEL/HURKX) with two carriers at 2.0 and 13.2 nm, and one SRH-suppressed reference. |
| D10 | Gate leakage | "measure before exclusion"; PF magnitude possible | null test via QTNLSC/FNORD | **Test it in the solver, quantitatively** (the user requirement), with a leakage-maximising bound, and include the defect-assisted oxide path (Ielmini TAT) that Codex could not exclude. |
| D11 | MASS.TUNNEL / tunnelling mass in IWO | 0.2 (illustrative) | 0.206 (PBE 2 nm) | **m*(t) of the TCAD convention** (0.254/0.219/0.212), so that NC300, ARICHN and the tunnelling masses use the same number. |
| D12 | Donor law | retire (1+(t/20)⁴), hold N_D shared | DFT: W is a fully ionised donor; active fraction unknown | **Agree with Codex.** N_D = 2.5e17 cm⁻³, constant in t (`tc_nm=1e9`). The value is the **FITTED V1 donor amplitude, kept fixed** (N_D0 of the V1 law, fitted to the V0 per-film values; 01_CURRENT_STATE §E); the **constant thickness dependence is ASSUMED**. ×0.1 and ×10 are run in S6. (Label corrected 2026-10-10 after review; it was called ASSUMED / not fitted.) |
| D13 | N_t parameterisation | integrated N_s (cm⁻²) | V1 law Nt2·(2/t)^0.75 | **Integrated N_s, spread uniformly** (Nt = N_s/t, i.e. `alpha=1`, `Nt2 = N_s/2 nm`). Bulk-only and 50:50 are run in S3. N_t (cm⁻³) ≠ NTA (cm⁻³eV⁻¹); NTA = Nt/W_T. |
| D14 | Quasi-2D NC300 (new DFT input) | not considered | candidate, ×4.27 at 2 nm | **Primary at 2.0 nm only**, by a pre-registered physics rule. DFT E21 = 0.72 eV is > 10 kT and > E_F − E1 (≤ 0.12 eV at V_G = 3 V), which gives a single subband. At 6.3 nm E21 exists only from a 2-parameter MODEL (0.137 eV ≈ 5 kT), so 3-D stays primary there and ×1.467 is run in S6. This is a DOS substitution inside the 3-D Fermi–Dirac form, not true 2-D statistics: the on-state n is overstated by up to 1.7×. S1-05 (3-D NC at 2 nm) is the model sensitivity that brackets this. |
| D15 | Boltzmann ablation | yes, all films | — | **2.0 nm only** (1 run). That is where degeneracy matters most: n ≈ 5.6e19 cm⁻³ at 2 V overdrive. |

### 2.1 Codex review of this merged design (`codex_review_2026-10-10.md`)

**Adopted:**
- **Native checks of the offline profiling before S3/S4.** S1-07 (2.0 nm, Q_f +1e12 cm⁻², MUN ×0.6) and S3-27 (the same for IGZO at 6.3 nm). The S4c tolerance is 0.01 dec, not 0.005, because V2 T2 missed its transformation-based prediction at 2 nm by 0.006 dec.
- **No extrapolation when shifting curves** (§5.2).
- **Schottky adoption.** It makes the scaling approximate, so a Schottky branch is adopted into S4 only if a reserve launch passes the same native check.
- **S4a candidate 1 equals the existing baselines** when no branch is adopted. It is then reused, not re-launched, and its 3 launches return to the reserve.
- **Q_f-off strip controls** (S2-16/17). V2 variant D had no Q_f; variant Q had it and scaled differently.
- **Leakage scoring** (§7):
  - the slope criterion is 2 × |measured slope| plus 2σ;
  - a minimum fraction of valid points is required, and sign reversals are reported;
  - the mechanism-induced ΔI_D is scored against a matched control, not only the total;
  - drain_share is pointwise and suppressed when I_G is unresolved;
  - the "floor-scale current means audit" rule applies only to nominal/SRH runs, not to the worst-case set;
  - an underprediction at 2 nm does not falsify a mechanism, because the 2 nm floor may be instrument-limited;
  - FNORD evaluates the field at the semiconductor-interface segment (Al2O3/IWO). The HfO2-barrier constants are therefore transferred to that field (F.AE = A/r², F.BE = r·B, r = ε_HfO2/ε_Al2O3 = 2.174; review fix 2026-10-10; without it FNORD over-estimated I_G by about 5.5–6 decades at V_G = −3 V). It stays a single-barrier (HfO2-limited) estimate of the bilayer.
- **The worst-case oxide set is an optimistic scenario,** not a rigorous upper bound: pinholes, thinning and defects are not covered.
- **Labels.** Quasi-2D NC300 and the mobility mass factor are CALCULATED from LITERATURE + DFT-law inputs. The leakage/SRH numbers are CALCULATED conditional bounds. Data-selected branch choices are reported as such.
- **S5 branch selection.** Branches are re-selected inside each fold, from the training films' S3 results.
- **BQP increment** is read against S3-01 (no confinement, no BQP) as well as S0-01.
- **Extraction** is guarded against missing crossings and failed fits. S6 μ_FE is reported with the registered C_ox and with the perturbed one.
- **Minimum set.** S3-02 is replaced by S1-07.

**Not adopted:**
- **"The Q_f shift is not exact in this 2-D deck."** If the semiconductor solution is unchanged, its contact boundary conditions are unchanged. The required oxide perturbation is a field uniform in x: Q_f and the gate both span x = 0–24 µm, and the side boundaries are Neumann. It is supplied exactly by the Q_f sheet. The remaining error is numerical, and S1-07 measures it.
- **"Replace S2-08 by S1-05 in the minimum set."** The gate-leakage test is a user requirement. The second film at the largest floor shows that the oxide current is thickness-independent while the floor is not. S1-05 stays in S1.

### 2.2 Agreements that need no choice
- ΔE_g ≠ ΔE_c (0.335 vs 0.281 eV at 2 nm; V2 already separates them).
- Exclude FLDMOB, CONMOB/ANALYTIC/ARORA/KLA, CVT and BBT.
- A density-gradient or BQP correction only as a pair, with the DFT shift switched off.
- `tmun` declared; MAXTRAPS ≤ 10; XANDRNORM and strict CR.TOLER in depletion; MOBILITY never between SOLVEs (EMPIRICAL, run_0008); sequential launches.
- 31.8 nm is a stress check, never fitted.
- Spend fewer launches if shared physics fails early (§6, stop rules).

---

## 3. Model set (ON/OFF, with reasons)

"Primary" is the model calibrated in S4. "Branch" is tested in S3 and adopted only by the rule in §6. "Test" means a diagnostic launch that never enters the fit.

| Model | Status | Reason |
|---|---|---|
| Fermi–Dirac statistics (`fermi`) | **ON, primary** | Degenerate accumulation: n ≈ 5.6e19 cm⁻³ at 2 nm and 2 V overdrive. Boltzmann is checked once (S3-26). |
| DFT confinement: ΔE_c(t) in AFFINITY, ΔE_g(t) in EG300, Δm*(t) in NC300 | **ON, primary** | COMPUTED points; laws FITTED to the DFT points (fit3). EG300 enters only n_i (no visible effect, but kept consistent). OFF in S3-01..03; low/high ends in S6. |
| Quasi-2D NC300 at 2.0 nm (1.373e19 cm⁻³) | **ON, primary** | CALCULATED (N2D/t) from the LITERATURE bulk mass + the DFT Δm law. Single-subband criterion from COMPUTED E21 = 0.719 eV. Equivalent to −37.5 meV. It is a DOS substitution in the 3-D FD form, which overstates the on-state n by up to 1.7× (DFT_TO_TCAD §3). 3-D at 2 nm in S1-05; ×1.467 at 6.3 nm in S6. |
| Exponential acceptor tail (`defects` NTA, WTA), Nt = N_s/t | **ON, primary** | Multiple trapping and release; collapse of SS vs I_D/I_on in data and TCAD. N_s and W_T FITTED. Placement branches: bulk / 50:50 / none. |
| Deep acceptor Gaussian 5e16 at E_c−0.6 eV | ON (ASSUMED) | V2 continuity; weak effect; zero in S6. |
| Interface acceptor sheet 3e11 cm⁻²eV⁻¹ at E_c−0.3 eV (0.25 nm layer) | ON (ASSUMED) | LITERATURE-scale D_it (HfO2/In2O3 proxy); zero in S6. |
| Uniform donors N_D = 2.5e17 cm⁻³ | ON (shared; FITTED V1 donor amplitude, kept fixed; constant thickness dependence ASSUMED) | DFT: W is a fully ionised resonant donor, but compensation is not computed. The fitted (1+(t/20)⁴) thickness term is retired; its fitted amplitude is kept. |
| Front fixed charge Q_f (y = 0) | **ON, FITTED shared** | Carries ΔV₀. Degenerate with the gate work function and χ_bulk, which are therefore held fixed. |
| Constant mobility per film from the shared law μ_band(t) = μ∞·(0.208/m*(t))/(1+ℓ/t), times the existing roughness (1−0.287/t)² | **ON, primary** | Matthiessen form: bulk + interface scattering ∝ 1/t. The mass factor 0.208/m*(t) (CALCULATED from LITERATURE + the DFT Δm law) explains only 0.83 of the 2→13.2 nm drop, so ℓ carries the rest (FITTED, an empirical law). `tmun=0`. |
| IGZO.TOKYO μ(n) = MUN·(n/NCRIT)^(γ/2) | **Branch** (S3, 6 runs) | Amorphous-oxide percolation mobility; targets the measured γ (1.13 at 6.3 nm vs TCAD 0.57) and the rising μ_FE. Use with `user.material` is UNVERIFIED: the first launch must show it in the REGIONAL MOBILITY MODEL SUMMARY. |
| Schottky Pd S/D (thermionic + E.TUNNEL + image-force BARRIER, `^ins.ohmic`) | **Branch** (S3, 7 runs) | On-state shape; off-state metrics also reported. Shared barrier from an ASSUMED grid {0.2, 0.5} eV, never per film. ARICHN = 120.17·m*(t) (CALCULATED). Not a V_G-flat floor mechanism by itself (D4). |
| Bohm quantum potential (BQP) | **Test** (2 runs, 2 nm) | Only as (DFT shift OFF + BQP). It is read against S0-01 (DFT shift ON) and against S3-01 (no confinement, no BQP), which isolates the BQP increment. Quantum mass from DFT (m_z 0.139 MODEL, or 0.254). Never both ON (double counting). |
| SRH background (τ 1e-6 s, σ 1e-15 cm²) | **ON** (ASSUMED) | User requirement; physically present. CALCULATED bound (audit §7.1) ≥ 1e16 below the floors. Bounded in S2-01..03. |
| SRH extreme + TRAP.TUNNEL + TRAP.HURKX, two carriers | **Test** (2 runs) + SRH-suppressed reference (1) | Quantitative null test of generation (D9). |
| Gate tunnelling QTNLSC.EL (self-consistent) with LITERATURE oxide band parameters | **Test** (8 runs incl. smoke and mesh check) | User requirement. Self-consistent, so KCL holds. Post-processing QTUNN.EL/FNPP are not used: they inflate i."gate" without debiting the channel and trip the KCL check. |
| Fowler–Nordheim FNORD (self-consistent; F.AE/F.BE CALCULATED from φ, m) | **Test** (2 runs) | Second, independent leakage formulation. |
| Oxide trap-assisted tunnelling (ITAT.SC.EL, DOPING TAT.TRAP in HfO2) | **Test** (2 runs) | Defect-assisted (Poole–Frenkel-like) leakage, which Codex could not exclude without I_G. UNVERIFIED for a bilayer. |
| Ungated strip, separate deck (audit 7.11 A) | **Test** (7 runs, 2 of them Q_f-off controls) | The only candidate that gives a V_G-flat floor of the right size. Predicts I(0.7 V)/I(0.1 V) = 7. (W/L)_par FITTED, geometry ASSUMED. |
| Ungated strip in-solver (7.11 B) | **Test** (1 run) | Checks that the same-name split electrodes work and agree with deck A. |
| Two-carrier solve | **Test** (S1-06, S2-01..03) | The electron-only assumption. |
| Field-dependent mobility FLDMOB | **OFF** | Lateral field 350 V/cm gives v ≤ 2.1e4 cm/s ≪ v_sat (CALCULATED). Silicon v_sat would be inherited. |
| CONMOB / ANALYTIC / ARORA / KLA | **OFF** | They overwrite MATERIAL MUN (manual p.896) and are doping-, not carrier-dependent (silicon parameters). |
| CVT / WATT / YAMAGUCHI / SHIRAHATA / TASCH | **OFF** | Silicon inversion-layer laws; CVT overrides every other model (p.196). |
| PRPMOB (vertical-field degradation) | **OFF**; reserve only | The measured μ_FE *rises* up to 3 V, so a degradation-only law cannot improve the fit. It is a reserve diagnostic of the θ_r contradiction, run only after trap filling is settled. |
| BBT (std/KL/nonlocal) | **OFF** | E_g ≥ 3.05 eV, 350 V/cm, no ambipolar branch. With `carriers=1` it creates untransported holes; the manual calls BBT.NONLOCAL unsuitable for unipolar high-field regions (p.280). |
| TRAP.COULOMBIC (Poole–Frenkel in the channel) | **OFF** | Physically meaningful only for donor-like (Coulombic) wells. The DOS here is acceptor-only, and ATLAS would apply it to SIGTAE anyway. |
| Lumped / distributed contact resistance | **OFF** | Requires `newton carriers=2` (p.85). A single R_sd cannot create the thickness trend (SYNTHESIS). The 31.8 nm S7 runs set R = 0. |
| Back-surface Q_b / donor sheet | **OFF** | A gated back layer cannot give a V_G-flat floor at L_D ≈ 7.3 nm (thin films). Already exercised (runs 0030, 0035). |
| Density gradient (`quantum`) | **OFF** | BQP covers the paired test with fewer extra solves (no QFACTOR ramp). |

---

## 4. Parameter table

Values at 2.0 / 6.3 / 13.2 nm. "Profiled" means fitted offline by an exact transformation, with no launch.

### 4.1 DFT and band inputs

| Parameter | Value | Label and source |
|---|---|---|
| E_g,bulk | 3.05 eV | LITERATURE (Fan 2021) |
| χ_bulk | 4.3 eV | LITERATURE (Fan 2021). The DFT bulk-equivalent EA of 4.776 eV (PBE, H-(001)) is reported, not used (termination-specific). |
| ΔE_c(t) | 0.2816 / 0.0622 / 0.0235 eV (law 0.70147·t^−1.31669) | Law FITTED to COMPUTED DFT points (0.695/0.930/1.962 nm, `dft_inputs.json` laws.dEc_eV.fit3). 6.3/13.2 nm are extrapolations; spread 0.046–0.062 / 0.013–0.024 eV. Device t ≡ H–H thickness is ASSUMED. |
| AFFINITY = χ_bulk − ΔE_c | 4.0184 / 4.2378 / 4.2765 eV | CALCULATED |
| ΔE_g(t) | 0.3273 / 0.0724 / 0.0274 eV (0.81431·t^−1.31518) | Law FITTED to COMPUTED DFT points (residuals ≤ 0.4 %) |
| HSE factor | 1.0 primary; ×1.107 in S6 | COMPUTED at 1 nm (1.060–1.107); transfer to other t ASSUMED |
| m*(t) = 0.208 + Δm(t) | 0.2543 / 0.2189 / 0.2123 m0 (Δm = 0.11116·t^−1.26387) | 0.208 LITERATURE (Stokey 2021) + Δm law FITTED to COMPUTED DFT points |
| NC300 | 1.373e19 (quasi-2D) / 2.569e18 / 2.454e18 cm⁻³ | 2 nm: CALCULATED N2D/t from m*(t) (LITERATURE bulk + DFT Δm law); single-subband criterion from COMPUTED E21 = 0.719 eV. 6.3/13.2 nm: 3-D formula (CALCULATED). |
| NV300 | 1e19 cm⁻³ | ASSUMED (holes not solved) |
| ε_IWO | 9.3 | MEASURED (Januar 2026 SI Fig. S1; the fab's measurement) |
| W donor character | fully ionised, level +1.2 to +1.8 eV above E_c | COMPUTED (all four W cells; 3 % W-5d weight at 2 nm). Supports a constant shared N_D, not its value. |
| Subband box (δ, m_z) | 1.396 nm, 0.139 m0 | MODEL (2 parameters through 2 DFT spacings; exact, untested). Used only for S6 and the BQP mass. |

### 4.2 Device and stack

| Parameter | Value | Label |
|---|---|---|
| L, W, V_D | 20 µm, 290 µm, 0.7 V | MEASURED (fab schematic and data) |
| HfO2 15 nm, ε 19.57 | — | thickness from the fab schematic; ε MEASURED (SI Fig. S1) |
| Al2O3 2 nm, ε 9.0 | 7 / 11 in S6 | ASSUMED (position touching the channel is also ASSUMED, open item H.3) |
| Gate work function | 4.7 eV | ASSUMED (TiN 4.5–4.9); fixed, degenerate with Q_f |
| Contact overlap | 2 µm | ASSUMED |
| T | 300 K | ASSUMED |

### 4.3 Fitted shared parameters (S4)

| Parameter | Start | Range | How fitted | Label |
|---|---|---|---|---|
| ΔV₀ via Q_f | Q_f = 1.383e12 cm⁻² | Q_f −1.4e12 … +4.2e12 (ΔV₀ ±0.5 V ↔ ±2.80e12) | profiled, rigid shift (exact) | FITTED (shared, all 3 films) |
| μ∞ | 100.0 cm²/Vs | 10–300 | profiled, I ∝ MUN (exact) | FITTED (shared); start passes through the V2 FITTED anchors |
| ℓ | 7.25 nm | 0–50 nm | profiled jointly with μ∞ over the 3 per-film scales (1 dof left) | FITTED (empirical law) |
| N_s | 4e12 cm⁻² (Nt 2e19 / 6.35e18 / 3.03e18 cm⁻³) | 1e12–1e13, log | launches (S4a/b) | FITTED |
| W_T | 0.040 eV | 0.025–0.060 | launches | FITTED |
| GAMMA0 (only if IGZO adopted) | −0.31 | −0.6 … +0.6 | launches | FITTED; TGAMMA 178.4 K LITERATURE default (no T data); NCRIT 1e20 ASSUMED (degenerate with MUN) |
| φ_B (only if Schottky adopted) | — | {0.2, 0.5} eV, shared | chosen in S3, not refined | ASSUMED grid; selected, so FITTED in effect |

With these starts the per-film MUN is 12.98 / 40.26 / 60.54 cm²/Vs. At 6.3 nm that is about 4× the V1 per-film value (10.4), so the start already predicts the known 6.3 nm on-current miss.

### 4.4 Fixed ASSUMED physics

| Parameter | Value | Label |
|---|---|---|
| N_D | 2.5e17 cm⁻³, constant | FITTED V1 donor amplitude, kept fixed (not re-fitted here); constant thickness dependence ASSUMED; ×0.1/×10 in S6 |
| τ_n0 = τ_p0 | 1e-6 s (extreme 1e-9) | ASSUMED |
| Capture σ (all DEFECTS) | 1e-15 cm² (extreme 1e-13; suppressed 1e-20) | ASSUMED; typical oxide-TFT order, to be cited before publication |
| μ_p | 0.01 cm²/Vs | ASSUMED |
| DOS quadrature | 384/192 (768/384 in S1-04) | NUMERICAL |
| MASS.TUNNEL (channel TAT) | m*(t) | COMPUTED + LITERATURE (D11) |

### 4.5 Oxide and tunnelling parameters (S0-02, S2)

| Set | HfO2 χ / E_g / me.tunnel | Al2O3 χ / E_g / me.tunnel | TiN→HfO2 barrier | Label |
|---|---|---|---|---|
| nominal | 2.5 eV / 5.8 eV / 0.20 | 1.25 eV / 8.8 eV / 0.35 | 2.2 eV | χ, E_g LITERATURE (Robertson 2000, JVST B 18, 1785: HfO2 CBO 1.5 eV to Si, Al2O3 CBO 2.8 eV, E_g 8.8 eV). Masses ASSUMED inside the LITERATURE ranges (HfO2 0.1–0.4, Al2O3 0.3–0.5 m0); source to be pinned before publication. |
| worst | 3.2 eV / 5.8 eV / 0.10 | 1.6 eV / 8.8 eV / 0.30 | 1.5 eV | ASSUMED leakage-maximising bound, below the LITERATURE barrier range, chosen so that I_G is resolvable for the V_G-slope test |
| FNORD nominal | φ 2.2 eV, m_r 0.20 → HfO2-barrier A 3.50e-6 A/V², B 9.97e7 V/cm → written F.AE 7.40e-7 A/V², F.BE 2.17e8 V/cm (field at the Al2O3/IWO segment: A/r², r·B, r = 2.174) | | | CALCULATED (Lenzlinger–Snow form + field transfer) |
| FNORD worst | φ 1.5 eV, m_r 0.10 → A 1.03e-5 A/V², B 3.97e7 V/cm → written F.AE 2.17e-6 A/V², F.BE 8.63e7 V/cm | | | CALCULATED |
| Oxide TAT | HfO2 traps 1e19 cm⁻³, 1.0 eV below the HfO2 band edge; trap charge kept out of Poisson (`^tat.poisson`, PDF p.323) so that S2-12/13 isolate the TAT current | | | ASSUMED high-defect bound |
| Gate `qtunn.cmass` | 1.0 | | | ASSUMED |

These parameters override the ATLAS defaults that are active today without being visible: HfO2 χ = 0 eV and E_g 5.7 eV; Al2O3 χ 0.9 eV and E_g 9 eV.

---

## 5. Fitting procedure (S4) and scoring

### 5.1 Objective (fixed before any launch)

Codex's equal-film objective, using the registered extraction code (§8):

J = (1/3) Σ_t (RMSE²_sub,t + RMSE²_on,t)/2, where
- RMSE_sub is the log10 residual where the *measured* I_D lies between 10 × floor_t and 1e-9 A/µm;
- RMSE_on is the log10 residual over V_G = 1…3 V.

No film is weighted by its current or its number of points. √J is reported in decades.

### 5.2 Offline profiling (no launches), checked natively

For every film triple at given (N_s, W_T[, GAMMA0], branch):
- **Shift:** I(V_G; Q_f) = I(V_G + q(Q_f − Q_f0)/C_ox; Q_f0).
  - Exact in the continuum equations: the QF sheet at y = 0 and the gate both span x = 0–24 µm. An unchanged semiconductor solution then needs only a field change in the oxide that is uniform in x, and the sheet supplies exactly that (§2.1).
- **Scale:** I(V_G; MUN) = (MUN/MUN₀)·I(V_G; MUN₀).
  - Exact in electron-only drift-diffusion when every electron mobility is multiplied by one constant. This includes IGZO.TOKYO, μ = MUN·f(n).
  - Broken only by the generation–recombination term. That term is ≤ 1e-28 A/µm against currents ≥ 1e-15 A/µm (CALCULATED bound).
  - Broken by any gate or contact injection, so it is not used for the Schottky branch or for any tunnelling run.
- **Native checks.**
  - S1-07 and S3-27 must agree with the transformed curves within 0.01 dec on every J-window point. If not, the profiling is labelled approximate and every S4b candidate carries the profiled Q_f and MUN natively.
  - A Schottky branch gets one reserve launch of the same check before it may enter S4.
- **No extrapolation.** A shifted curve is evaluated only inside the solved V_G range (−3 … 3 V).
  - J uses only covered window points, and their number is reported.
  - If the coverage of either window falls below 95 %, the optimum is flagged and confirmed natively.
  - |ΔV₀| ≤ 0.5 V by the range.
- **Minimise J** over (ΔV₀, μ∞, ℓ), with PCHIP interpolation of log I onto the measured grid. That is 3 parameters for 3 shifts + 3 scales, leaving 3 dof as the honest test of sharing.
- **4c re-runs the best natively.** Profiled and native must agree within 0.01 dec. Otherwise the native run is the reported result and the profiling error is reported.
- **Reuse.** If S3 adopts no branch, S4a candidate 1 is identical to S0-01/S1-01/S1-02; those curves are reused and its 3 launches return to the reserve.
- **Diagnostic only, never a model:** per-film free shift and scale give the shape-only residual. This is Codex's alignment/shape decomposition of the 6.3 nm anomaly.

### 5.3 Acceptance thresholds (ASSUMED engineering limits, Codex; not measurement confidence intervals)

Per film:
- active log-RMSE ≤ 0.15 dec;
- |ΔV_th,cc| ≤ 0.10 V;
- I_D(3 V) within ±30 %;
- SS (A1 normalised window) within ±20 %;
- μ_FE at 1.5, 2 and 3 V within ±20 % (g_m shape).

A film that fails any of these is reported as failed. Calibration success on all three films is still called *calibration*.

### 5.4 Identifiability

- From the S4a+S4b archive: the scaled residual Jacobian in (log N_s, W_T[, GAMMA0], ΔV₀, log μ∞, ℓ), its singular values and the parameter correlations.
- A condition number above 100 or |corr| > 0.95 (ASSUMED thresholds) means a parameter *combination* is reported, not individual values.
- S6 profiles: each ASSUMED/COMPUTED input is perturbed, (ΔV₀, μ∞, ℓ) are re-profiled exactly, and the movement of each fitted value is reported. Example: confinement high vs low shows how much of ΔV₀ is really DFT alignment.

---

## 6. Staged run matrix

`campaign_matrix.json` lists all 181 entries. Each entry has `{id, stage, film_nm, model_flags, params, purpose}` plus a ready `campaign_entry` block for `config/campaign_*.json`.

| Stage | Launches | Running total | Content |
|---|---:|---:|---|
| **S0 smoke** | **2** | 2 | S0-01 2.0 nm primary baseline (new laws, quasi-2D NC, surface tail, shared μ law). S0-02 the same + QTNLSC worst-case gate tunnelling (oxide parameters, j.tun, 0.25 nm oxide mesh). |
| **S1 baselines and numerics** | **7** | 9 | 6.3 and 13.2 nm primary baselines; 13.2 nm mesh ×0.7; 2.0 nm DOS 768/384; 2.0 nm 3-D NC (quasi-2D check); 13.2 nm two carriers; S1-07 native profiling check (2.0 nm, Q_f +1e12, MUN ×0.6). |
| **S2 off-floor mechanisms** | **17** | 26 | SRH/TAT bounds, two carriers: 13.2 extreme, 13.2 suppressed, 2.0 extreme (3). Gate leakage (10): QTNLSC nominal ×3 films; QTNLSC worst 6.3 and 13.2 (2.0 is S0-02); FNORD worst 2.0 and 13.2; oxide-mesh ×0.5 check at 2.0; oxide TAT 2.0 and 13.2. Strip deck 13.2 and 2.0 (2), plus Q_f-off controls at 13.2 and 2.0 (2). |
| **S3 model-form branches** (shared start parameters) | **27** | 53 | No confinement ×3; bulk-only tail ×3; 50:50 tail ×3; no tail at 6.3 (1); IGZO.TOKYO GAMMA0 −0.31 and +0.30 ×3 (6); S3-27 native IGZO profiling check at 6.3 (1); Schottky 0.2 and 0.5 eV with lowering ×3 (6) + 0.5 eV without lowering at 6.3 (1); BQP pair at 2.0 (2); Boltzmann at 2.0 (1). |
| **S4a calibration, space-filling** | **45** | 98 | 15 candidates × 3 films. Candidate 1 is the start point (reused if no branch is adopted); 14 come from a pre-registered Latin hypercube (seed 20261010 for 2-D, 20261011 for 3-D with GAMMA0, both listed in the matrix). |
| **S4b calibration, adaptive** | **18** | 116 | 6 candidates × 3 films from a quadratic surrogate of J (trust region half the S4a spacing). |
| **S4c native confirmation** | **3** | 119 | Best model with profiled Q_f and MUN written into the decks. |
| **S4d runner-up branch** | **3** | 122 | Runner-up S3 branch at the calibrated parameters. |
| **S5 leave-one-film-out** | **30** | 152 | 3 folds × (4 adaptive training candidates × 2 training films + 2 frozen held-out predictions: best and runner-up). Branches are re-selected inside each fold. |
| **S6 sensitivity and frozen predictions** | **27** | 179 | Confinement low ×3 and HSE-high ×3; bulk mass 0.159 ×3; N_D ×0.1 and ×10 ×3; ε_Al2O3 7 and 11 at 2.0 and 13.2 (4); deep Gaussian + D_it off ×3; 6.3 nm quasi-2D box ×1.467 (1); frozen strip decks ×3; in-solver strip 13.2 (1). |
| **S7 31.8 nm stress** | **2** | 181 | Frozen model; frozen model with N_D ×10. R_sd = 0, never fitted. |
| **Reserve** | **≤ 19** | ≤ 200 | In this order: (1) repairs of failed launches; (2) a refined-numerics re-run if S1 trips a numerics rule; (3) one PRPMOB diagnostic; (4) one 2-parameter Schottky × IGZO combination if both branches pass separately. Unused reserve stays unused. |

### Stop and decision rules

**Global rules**
- Every launch counts, including failures.
- Hard cap 200, enforced in code (review fix 2026-10-10): `config/solver.yaml` `max_launches` 260 = 60 used + 200, and `run_campaign.py` counts C10 launches (labels `c10_*` in RUN_INDEX, failures included) up to 200, refuses `--workers` ≠ 1 for C10 plans and never re-launches an entry that already has a RUN_INDEX row (from any C10 plan) unless `--retry ID` is given.
- Sequential only (`--workers 1`).
- After any code change, `regress_all_decks.py` must print `unexpected differences 0` before the next launch.

**S0 (smoke)**
- If either run fails on syntax, an option is not active (OPTION_NOT_ACTIVE from the deckbuild.out activation parser) or KCL fails, stop and fix the code.
- At most 3 reserve launches are spent on S0 repairs. If S0-02 still fails, gate tunnelling is reported as not implementable in this installation, and the leakage test falls back to the CALCULATED bounds plus the oxide TAT runs.
- S0-01 must reproduce its own deck parameters in the deck header: χ 4.0184 eV, NC300 1.373e19, MUN 12.977, Q_f 1.383e12.

**S1 (baselines and numerics)**
- If mesh ×0.7 or DOS ×2 changes active RMSE by > 0.01 dec, V_th,cc by > 5 mV or SS by > 3 mV/dec, adopt the refined setting for every later run (reserve) and repeat the affected baselines.
- If S1-05 (3-D NC) shifts V_th,cc outside +40…+70 mV relative to S0-01, the NC override is audited before S3.
- If S1-06 (two carriers) changes I_D by > 1e-3 relative above 1e-14 A/µm, the electron-only assumption is dropped: all later runs use two carriers, with timeout ×1.5.
- If S1-07 differs from the transformed S0-01 by > 0.01 dec, offline profiling becomes approximate: every S4b candidate is run natively at the current profiled Q_f and MUN, and the S4 report says so.

**S2 (off-floor mechanisms; pre-registered verdicts in §7)**
- A *nominal* or SRH null test that produces floor-scale current contradicts the CALCULATED bounds. Stop and audit KCL, CR.TOLER and the deck; do not fit.
- Floor-scale current from the worst-case set is an allowed result. It is checked by S2-11 (oxide mesh) before it is interpreted.
- The strip decks must give I(0.7)/I(0.1) = 7.0 ± 0.5. Otherwise the strip is not ohmic in ATLAS, and that is the result.

**S3 (branch adoption; decided on the shared-profiled √J at the start parameters)**
- A branch is adopted if all of these hold:
  - it lowers √J by ≥ 0.03 dec;
  - no film's RMSE_sub or RMSE_on worsens by > 0.03 dec;
  - it converges at all three films;
  - its activation is confirmed in deckbuild.out.
- Choices within a group:
  - tail placement: the lowest √J of {surface, bulk, 50:50};
  - IGZO: the better GAMMA0 seeds S4, and GAMMA0 is then FITTED;
  - Schottky: the better barrier is fixed for S4.
- At most two branches are adopted. If both IGZO and Schottky pass, the one with the larger gain is adopted and the combination goes to the reserve.
- A branch whose only effect is a rigid shift or a uniform scale is rejected: those directions are already profiled.
- Branch choices are data-selected model choices and are reported as such.
- The IGZO branch needs S3-27 to pass (≤ 0.01 dec) for exact profiling. Otherwise it is profiled natively, as in the S1-07 rule.
- The Schottky branch needs one reserve launch of the same check.

**S4 (calibration)**
- After S4a: if the best √J > 0.30 dec (twice the acceptance) and the residuals are systematic (same-sign on-state error at 6.3 nm for ≥ 80 % of candidates), skip S4b. Run S4c on the best candidate, go to S5, and report the shared model as failed. No per-film rescue parameters, ever.
- S4b stops early when 3 successive candidates improve √J by < 0.01 dec; the unused launches return to the reserve.
- If S4c shows profiled vs native > 0.01 dec, the native result is reported and the profiling is audited before S5.

**S5 (leave-one-film-out)**
- The S3 adoption rule is re-applied inside each fold, using the two training films' S3 results only (no launches). If a fold picks a different branch than the full data, its 8 training launches use that branch, and its candidates come from around the S3 start instead of the S4a archive.
- The held-out film is never tuned. The best-training candidate is the primary prediction; the runner-up only measures optimiser uncertainty.
- Any held-out film that fails §5.3 falsifies transferability of this model form. That is reported, not repaired.

**S6 and S7**
- No stop rule; every result is reported.
- S7 failure (31.8 nm never turning off is not reproduced) is documented, not fitted.

**Early exit for the whole campaign.** If S4 reports the shared model as failed and S5 confirms it on ≥ 2 folds, S6 is cut to the DFT-input profiles (confinement low/high, NC 6.3 nm, frozen strip decks: 10 launches). The rest is not spent (Codex: spend less when shared physics fails early).

---

## 7. Off-floor and gate-leakage tests (pre-registered)

**Floors (MEASURED/DERIVED):** 4.61e-15 / 1.53e-13 / 6.60e-12 A/µm, the median over V_G ∈ [−2, −0.5] V, flat in V_G.

### 7.1 Metrics for every S2 run and for every run with gate tunnelling

| Metric | Definition |
|---|---|
| floor_ratio | median over [−2, −0.5] V of log10(I_D,sim/I_floor,meas) |
| valid points | fraction of points in the window with I_D,sim > 0 and above the KCL limit; sign reversals listed |
| d_floor_ratio | the same median for the mechanism-induced ΔI_D = I_D(mechanism) − I_D(matched control without it): S0-01 / S1-01 / S1-02, or S1-06 for two-carrier runs |
| floor_slope | least-squares slope of log10 I_D,sim over [−2, −0.5] V in dec/V. The measured slope and its σ come from the same code on the data. |
| ig_ratio | median log10(\|I_G\|/I_floor) over the same window, and \|I_G(−3 V)\| |
| drain_share(V_G) | pointwise ΔI_D/\|I_G\|, reported only where \|I_G\| exceeds the KCL limit |
| KCL | \|I_D + I_S + I_G\| ≤ max(1e-17 A, 0.1 × floor) + 1 % Σ\|I\| (existing runner rule) |

### 7.2 Verdict rule (fixed now)

A mechanism *explains* the floor of film t only if all of these hold:
- valid points ≥ 80 %;
- |d_floor_ratio| ≤ 0.5 dec (the mechanism's own contribution, not the total);
- |floor_slope| ≤ 2 × |measured slope| + 2σ_slope;
- the KCL check passes.

It explains the *thickness scaling* only if the three films' d_floor_ratios agree within 0.5 dec, i.e. it reproduces t^3.85 without film-specific parameters.

**The 2.0 nm floor may be instrument-limited** (1.3 pA total; Codex Q1). There:
- an *underprediction* does not falsify a mechanism;
- an overprediction does.

### 7.3 Expectations

These follow from the CALCULATED conditional bounds (GENERATOR_AUDIT §7, `leakage_bounds.py`, Codex Q1). The runs test them. They are not used as results.

**What the worst-case oxide set is.** An optimistic scenario, not a rigorous upper bound: pinholes, local thinning and percolation paths are not modelled.

**FNORD caveat.** FNORD evaluates the field at the semiconductor–insulator segment (PDF p.288, manual text l.13034–13038), i.e. in the Al2O3, where E_Al = 2.174·E_Hf. The HfO2 gate-barrier constants are transferred to that field (F.AE = A/r², F.BE = r·B), so J equals the HfO2-barrier FN current at the HfO2 field. Without the transfer the estimate was inflated by about 6 decades at V_G = −3 V (review fix 2026-10-10). It remains a single-barrier estimate: the higher Al2O3 barrier is not in FNORD, so this is an upper estimate for injection through the bilayer.

**Gate injection is UNVERIFIED.** Injection from the Conductor-region gate is supported by the manual (electrode/contact injection for QTNLSC; electrode–insulator coupling for FNORD) but not verified in this deck. S0-02 must show a non-zero signed I_G with KCL closing.

- **SRH/TAT, extreme values:** ΔI_D(off) ≤ 1e-20 A/µm; floor ratio ≤ 1e-5.
- **QTNLSC nominal:** I_G(−3 V) ≤ 1e-24 A/µm, at least 9 decades below every floor.
- **QTNLSC/FNORD worst:** I_G(−3 V) ~ 1e-15 to 1e-11 A/µm, so the magnitude can reach the 2.0 nm floor. But I_G(−0.5 V)/I_G(−3 V) ≤ 1e-3, i.e. not flat, and the oxide current is the same for all films (no t^3.85).
- **Oxide TAT:** strongly V_G-dependent (J(3.7 V)/J(1.2 V) ≈ 6e3, Codex PF estimate). S2-12/13 run with the trap charge out of Poisson (`^tat.poisson`): 1e19 cm⁻³ acceptors in 15 nm HfO2 are up to 1.5e13 cm⁻² of charge, far above the fitted Q_f, and with the default TAT.POISSON the change in I_D would mix that electrostatic shift with collected leakage. The ITAT current is identified against the matched QTNLSC-only deck (S2-04 / S2-06). The electrostatics of a charged oxide are not tested by these runs.
- **Strip:** I(0.7)/I(0.1) = 7.
- **Q_f-on vs Q_f-off strips:** different G_strip(13.2)/G_strip(2.0). The measured floor ratio is 1432.

**Fitting the strip.**
- I_floor,pred(t) = I_strip(t) × L_p × (W/L)_par, with L_p = 20 µm (ASSUMED).
- (W/L)_par is FITTED on one film and predicted for the other two, in all three LOO folds, offline.
- The thickness scaling of G_strip(t) then comes from ATLAS (N_s/t traps, N_D, Q_f), not from a fitted law. That is the test.
- The V2 value (1e-4 /µm, FITTED on 13.2 nm, predicting 0.46 / 0.64 of the floor) is the reference.

**What this cannot settle.** No gate current and no second V_D were measured. These runs bound and rank the mechanisms *in the model*. The discriminating measurement is still I_D, I_S and I_G vs V_D at off-state V_G (strip ×7 vs diffusion form ×1.02).

---

## 8. Outputs per run

**Runner outputs (existing, unchanged):**
- `transfer.log`, `idvg.dat`, `igvg.dat`, `isvg.dat`, `terminal_currents.csv`, `comparison.csv`;
- `chan_mobility_vg.dat`, `chan_electrons_vg.dat`, `avg_electrons_vg.dat`;
- band, QFL and n cuts at equilibrium, near V_th and in the on-state;
- `execution.json` with fit_metrics: active, sub and on RMSE, Id(3 V) error, KCL, non-positive count.

**New runner outputs (code item C11):**
- the floor metrics of §7.1;
- the parsed `REGIONAL MODEL FLAGS`, `REGIONAL MOBILITY MODEL SUMMARY` and Contacts table, with OPTION_NOT_ACTIVE on mismatch;
- `j.tun` columns and `ifnvg.dat` when tunnelling is on;
- `solver_used.json`, `geometry_used.json`, `opts=<sha8>`;
- the strip mode output: I(V_D) at 0.1 and 0.7 V.

**Extraction (registered code, unchanged).** A new wrapper `analysis_2026-10-10_campaign/campaign_extract.py` (code item C12) imports `analysis_2026-10-06_extraction/extraction.py` and calls `run_extraction.analyse()` on each run's native `terminal_currents.csv`, exactly as for runs 0038–0040. Per run it reports:
- V_th,cc at 1e-9 and 5e-10 A/µm (`crossing`), with uncertainty;
- SS in the fixed window 5e-11–5e-10 A/µm and in the A1 normalised window [2.15e-5, 2.15e-4]·I_on,meas (`ss_window`). The normalisation uses the *measured* I_on and is never recomputed from the simulation;
- μ_FE at 1.0/1.5/2.0/2.5/3.0 V (`gm`, `MU_FACTOR`);
- V_th,ELR with validity flags (`vth_elr`);
- the power-law fit V_T, μ0, γ over [1, 3] V with the alternative windows (`pl_fit`), and μ_ch;
- off_floor (`off_floor`);
- the campaign metrics: RMSE_sub, RMSE_on, √J contribution, signed errors in V_th,cc, I_D(3 V) and μ_FE(1.5/2/3 V).

The registered `PROTOCOL.md`, `extraction.py` and `run_extraction.py` are not edited. The wrapper adds three things:
- **Guards:** a missing crossing, a failed power-law fit or an all-off curve gives an explicit `invalid` flag instead of an exception.
- **Labels:** it does *not* inherit the `STATUS` labels of `run_extraction.py` (written for the per-film V1 calibration). Every quantity is relabelled for this campaign: fitted, constrained by the whole-curve fit, or held out.
- **C_ox in S6:** for the ε_Al2O3 runs, μ_FE is reported with the registered C_ox (comparable with the data) and with the perturbed-stack C_ox.

**Campaign-level outputs:**
- a profiling table per S4/S5 candidate: ΔV₀, μ∞, ℓ, √J, per-film acceptance;
- the Jacobian / identifiability report;
- the LOO table, calibration and held-out shown separately;
- the S2 verdict table;
- a list of every failed branch and run.

---

## 9. The 10-run minimum set (launch order)

If only 10 launches are allowed:

| # | Run | Decides |
|---:|---|---|
| 1 | S0-01: 2.0 nm primary baseline | The new DFT-input model runs; the starting misfit at the anchor film. |
| 2 | S0-02: 2.0 nm + QTNLSC worst case | Gate leakage at the smallest floor: can the most leakage-friendly oxide reach 4.6e-15 A/µm, and is it flat? |
| 3 | S1-01: 6.3 nm primary baseline | Shared physics at the problem film (expected failure pattern stated in §1). |
| 4 | S1-02: 13.2 nm primary baseline | Shared physics at the thick anchor. 1–4 give the first shared ΔV₀, μ∞, ℓ by exact profiling. |
| 5 | S2-01: 13.2 nm two carriers, extreme SRH + TAT | Generation bound inside the solver (user requirement: SRH). |
| 6 | S2-08: 13.2 nm QTNLSC worst case | Gate leakage against the largest floor (1.9 nA total) and thickness independence of the oxide current. |
| 7 | S2-14: strip deck 13.2 nm | Fixes (W/L)_par; the ohmic V_D ratio. |
| 8 | S2-15: strip deck 2.0 nm | Frozen strip prediction of the 2.0 nm floor: does ATLAS give the t-scaling? |
| 9 | S1-07: 2.0 nm, Q_f +1e12 cm⁻² and MUN ×0.6 | Native check that the offline profiling of runs 1, 3 and 4 is valid (Codex review). Replaces "6.3 nm no confinement", whose shift and scale effects would be profiled away anyway. |
| 10 | S3-12: 6.3 nm, IGZO.TOKYO with GAMMA0 −0.31 | Activation of the carrier-density mobility for `user.material`, and whether μ(n) changes the 6.3 nm shape (γ 1.13 vs 0.57). |

**Left out of the 10, and why.**
- Mesh/DOS checks: mesh ×0.7 is already established for this physics (runs 0028/0036: ≤ 0.0004 dec).
- Schottky: on-state only.
- BQP: a pair test of a double-counting issue.
- No-confinement runs: their dominant effect is a shift and scale, which profiling absorbs.

**Defensible output after 10 runs.** Mechanism and model-form diagnosis plus a profiled shared baseline, not an optimised model.

---

## 10. Code needed before the first launch

Each item defaults to OFF and emits no deck line when OFF. Gate: `regress_all_decks.py` → `unexpected differences 0`.

| Id | Item | Notes |
|---|---|---|
| C1 | `config/physics_options.yaml` (all disabled) + emission hooks in `build_deck()` | Audit §8. Overrides via the existing `solver.physics_options.*` prefix; booleans parsed explicitly. |
| C2 | `nc300_override_cm3: {t: value}` | Replaces NC300 at listed thicknesses; header comment labels it CALCULATED (quasi-2D). |
| C3 | `nt_bulk_cm3` (default 0) | Adds a constant bulk term to Nt(t); header line printed only when non-zero. |
| C4 | `gate_tunnelling {enabled, model: qtnlsc\|fnord, set: nominal\|worst, f_ae, f_be, oxide_mesh_nm}` | Emits MATERIAL region=3/4 affinity/eg300/me.tunnel, `contact name=gate qtunn.cmass`, MODELS `qtnlsc.el qtnl.derivs` or `fnord`, `j.tun` on LOG, the `ifnvg.dat` extract, and oxide y.mesh refinement. |
| C5 | `schottky_sd {enabled, barrier_eV, lowering, e_tunnel}` | `contact name=source/drain workfun=χ(t)+φ_B surf.rec [barrier] [e.tunnel me.tunnel=m*(t)] ^ins.ohmic`, `material arichn=120.17·m*(t)`, top mesh 0.1 nm at y = −t. |
| C6 | `mobility {model: igzo_tokyo, gamma0, tgamma, ncrit}` | One `mobility material=IWO igzo.tokyo mun=… tmun=0 …` line before `solve init`. |
| C7 | `quantum {model: bqp, mass}` | `models bqp.n bqp.ngamma bqp.nalpha bqp.qdir=2`, quantum mass, `method bqp.newton` if needed. |
| C8 | Strip: `mode: strip` (separate two-terminal deck, V_D 0→0.1→0.7 V) and `strip.mode=in_solver` | Audit 7.11 A/B; `run_campaign.py` passes `mode`. |
| C9 | `oxide_tat {enabled, conc_cm3, e_level_eV}` | `doping region=4 uniform tat.trap conc= e.level=` + `models itat.sc.el`. |
| C11 | Runner | Thickness timeouts (2.0 1200 s, 6.3 1500 s, 13.2 2400 s, 31.8 3000 s; ×1.3–2.0 per entry as listed in the matrix); activation parser; floor/I_G metrics; provenance files. |
| C12 | `campaign_extract.py` | Wrapper around the registered extraction (§8). **Written 2026-10-10 after review** (it was missing); `compare` evaluates the S1 rules. |
| C13 | `profile_shared.py` | Exact shift/scale profiling, surrogate for S4b, LOO selection, Jacobian. **Partly written 2026-10-10 after review:** `check` (S1-07 / S3-27 / S4c native checks), `profile` (shared √J, S3/S4a) and `adopt` (S3 rule) exist; the S4b surrogate, S5 LOO selection and the Jacobian do not yet (needed only from S4b on). |

---

## 11. Integrity notes

**Shared parameters.**
- Q_f, μ∞, ℓ, N_s, W_T (and GAMMA0 or φ_B if adopted) are single values for all three films.
- Film dependence enters only through t in physical laws: DFT laws, N_s/t, the 1/t scattering term, and the mass factor.

**Named fitted quantities.**
- The five above (FITTED to the three thin-film transfer curves);
- (W/L)_par (FITTED to one film's floor);
- GAMMA0 / φ_B if adopted;
- the DFT *laws*, which are FITTED to COMPUTED DFT points, not to device data.

**Data-selected choices.** The tail placement, the mobility branch and the contact branch are chosen on the device data in S3. They are reported as model selection, and S5 repeats the selection inside each fold.

**Not fitted in this campaign:** gate work function, χ_bulk, E_g,bulk, ε, σ, τ, oxide parameters, NCRIT, TGAMMA, BQP γ/α. **N_D is not re-fitted here, but its value is the FITTED V1 donor amplitude** (kept fixed; constant form ASSUMED), so it is a fitted quantity carried over, not a free assumption.

**Retrospective status.** All comparisons are retrospective. The registered V2 6.3 nm prediction already failed (0.270 / 0.417 V vs 0.644 V). Nothing here re-opens that registration. The LOO is retrospective transferability within four already-seen devices, not an independent prediction.

**Prospective predictions after the campaign:**
- I_off vs V_D;
- low-V_D output curves;
- temperature dependence (TGAMMA);
- replicate devices.

These are frozen before any new measurement.

**Reporting.** Every failed branch, failed launch and failed acceptance is reported, with calibration and LOO residuals in separate tables.

---

## 12. Files

- `analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md`: this document.
- `analysis_2026-10-10_campaign/campaign_matrix.json`: 181 entries, stage counts, start values, derived per-film parameters.
- `analysis_2026-10-10_campaign/make_campaign_matrix.py`: generator (arithmetic only).
- `analysis_2026-10-10_campaign/codex_review_2026-10-10.md` and `codex_review_prompt_2026-10-10.md`: Codex's read-only review of this design (§2.1).
- Inputs: `DFT_TO_TCAD.md`, `dft_inputs.json`, `GENERATOR_AUDIT.md`, `codex_design.md`, `iwo-tft-research-private/01_CURRENT_STATE.md` (§D–H, K).


=== FILE: DFT_TO_TCAD.md (sha256 cb1c19869360) ===
# From our DFT to TCAD inputs (campaign 2026-10-10)

**Purpose.** List every TCAD-relevant quantity in the DFT we already have, and turn each into an ATLAS input. For each one, say whether V2 already uses it.

**Scope.** No new DFT and no ATLAS run were made. Every number was re-read from the Quantum ESPRESSO output files by `dft_to_tcad_extract.py`, which is in this folder. Codex checked the numbers independently (§2).

**Labels** (charter §3):
- COMPUTED: from our DFT output files.
- MEASURED: measured on the target devices.
- LITERATURE: from a cited publication.
- FITTED: fitted to named data.
- ASSUMED: chosen without data.
- CALCULATED: a closed-form formula applied to labelled inputs.
- MODEL: a simple physical model whose parameters were fitted to COMPUTED points.

A law fitted only to DFT points is labelled "FITTED to COMPUTED DFT points". It contains no device data, and nothing here is validation against the devices.

## 1. Bottom line

1. **Conduction-band shift.** The confinement shift of the conduction band, ΔE_c(t), is the main DFT input to the TCAD. V2 already uses it at 1 and 2 nm.
   - New point at 0.695 nm: ΔE_c = +1.059 eV.
   - The 2 nm value was re-computed: +0.281 eV.
   - The HSE06 check raises ΔE_c by a factor of 1.06–1.11, i.e. +17 to +31 meV at 2 nm. This assumes the ratio measured at 1 nm transfers to other thicknesses.
2. **Thick films are extrapolated.** No slab is thicker than 2 nm, so the values at 6.3 and 13.2 nm come from fitted laws. Depending on the law, ΔE_c is 0.046–0.062 eV at 6.3 nm and 0.013–0.024 eV at 13.2 nm (PBE).
3. **New candidate: a quasi-2D density of states.**
   - DFT puts the second subband 0.72 eV above the first at 2 nm (1.50 eV at 1 nm), far above kT. So at 2 nm and below, the film carries a single subband.
   - The matching effective density of states is N2D/t = 1.38e19 cm⁻³ at 2 nm. That is 4.3 times the 3-D value V2 uses (3.24e18 cm⁻³).
   - This equals a band shift of −37.5 meV, or about −55 mV in V_G at the 2 nm subthreshold slope. This is an estimate, not an ATLAS result.
   - At 6.3 nm the effect is ×1.5 (MODEL), and at 13.2 nm it is about ×0.9.
4. **The DFT band inputs cannot explain the 6.3 nm failure.** Their combined uncertainty at 6.3 nm is about 0.03 eV:
   - ΔE_c spread: 16 meV;
   - HSE scaling: about 7 meV;
   - change in the density of states: about 10 meV.

   The 6.3 nm threshold misses by 0.29 V (rigid part, V1) and by 0.23–0.37 V (V2 T3) [INFERRED].
5. **The mass cannot explain the mobility trend.** DFT gives m*(2 nm)/m*(13.2 nm) = 1.20. At constant scattering time this lowers the 2 nm mobility to 0.83 of the 13.2 nm value. The fitted μ_band ratio is 0.28 [INFERRED].
6. **W is a fully ionized, resonant donor.** In all four W cells (PBE), the W-5d-rich level lies 1.2–1.8 eV *above* the host conduction-band bottom.
   - In the 2 nm W slab (1.8 % of the cations are W, the composition closest to the devices), 97 % of the three donated electrons are in the host conduction band. Only 3 % project onto W 5d orbitals.
   - So W adds no gap state and no electron trap. The effective donor density must stay FITTED, because compensation was not computed.
7. **Surface states.**
   - The conduction-band edge is an interior state at every thickness from 0.695 nm up.
   - The valence-band edge becomes an OH surface state at 1 nm and below, and in the 2 nm slab once W is added.
   - In an electron-only TCAD this does not matter. DFT gives no support for acceptor-like surface states near E_c on an OH-terminated surface. The interface trap sheet and Q_f stay ASSUMED/FITTED.

## 2. Sources, method and cross-check

### Output folders
Under `qe_workflow/cern_htcondor/results/`.

| Film | Folders |
|---|---|
| 0.5 nm | `slabL1_relax_v2` |
| 0.75 nm | `slabL2_relax_v2` |
| 1 nm | `slab1r_final_cpu`; W slab `iwo_slab1_final_cpu` |
| 2 nm | `slab2_relax_c2`, `slab2r_pdos_cpu`; W slab `iwo_slab2_final_cpu` |
| W in bulk | `iwo_W24d`, `iwo_W8b` |
| HSE check | `nc_pbe_*`, `nc_hse_*` |
| Bulk | `qe_workflow/bulk_In2O3_protocol/bands_path.out`, `bands_gamma.out` |

### Method
All numbers are PAW-PBE unless marked HSE.

- **Gap.** From the last HOMO/LUMO line of `scf.out`. ΔE_g = gap − 0.8887 eV (bulk fundamental gap).
- **EA and IP.** From the vacuum plateau of `*_avg.dat` (as in `analyze_slabs.py`). The vacuum-referenced CBM is −EA.
- **ΔE_c at 2 nm.** Two-step alignment, a/2 window. The slab side was re-computed here and gives +0.2813 eV (log: +0.281). The bulk constants E_v − ⟨V⟩ = 3.9098 eV and E_c − ⟨V⟩ = 4.7985 eV are taken from `RESULTS_LOG.md`, because `bulk_v11.cube` was deleted on 2026-10-06.
- **ΔE_c below 2 nm.** ΔE_c(t) = ΔE_c(2 nm) + EA(2 nm) − EA(t), the same-termination EA route used by V2 at 1 nm. Then ΔE_v = ΔE_c − ΔE_g.
- **Mass.** Parabolic fit, |k| ≤ 0.05 Å⁻¹, along in-plane [100] (`collect_results.slab_mass`).
- **Non-parabolicity.** Kane fit E(1 + αE) = ħ²k²/2m* over the 10 points nearest Γ.
- **W cells.**
  - Band characters come from `projwfc.x`. The VB top is band n_pure − 1, because of the In 4d / W 5s5p band-count pitfall; this was confirmed for every cell.
  - Occupations come from the eigenvalues with the Marzari–Vanderbilt smearing of `scf.in` (0.01 Ry). They reproduce the electron counts to 2e-4.
- **Surface-state measure.** Same as `surface_state_check.py`: the share of projected weight on H atoms plus O atoms within 1.15 Å of an H.

### Cross-check by Codex
Codex re-derived the main numbers with its own scripts, read-only and without seeing ours. Its answer is in `codex_xcheck_2026-10-10.md` (prompt: `codex_xcheck_prompt_2026-10-10.md`).
- The gaps, EA, IP, thicknesses, E2 − E1, surface shares and all 2 nm W-slab numbers agree to the printed digits.
- The masses agree within 0.001 m0.

## 3. Results per thickness (pure In2O3 slabs)

All rows are COMPUTED except those marked CALCULATED or LITERATURE.

| Quantity | bulk | 2 nm | 1 nm | 0.75 nm | 0.51 nm |
|---|---|---|---|---|---|
| H-to-H thickness, relaxed (nm) | — | 1.962 | 0.930 | 0.695 | 0.461 |
| In-plane cell (Å) | 10.306 | 10.318 × 10.309 | 10.336 × 10.335 | 10.428 × 10.293 | 10.696 × 10.019 |
| PBE gap (eV) | 0.8887 | 1.2239 | 1.7885 | 2.1986 | 3.1401 |
| ΔE_g, PBE (eV) | 0 | +0.335 | +0.900 | +1.310 | +2.251 |
| ΔE_g, HSE-corrected (eV) [CALCULATED, ratio 1.060–1.107] | 0 | 0.355–0.371 | 0.954–0.996 | 1.388–1.450 | 2.386–2.492 |
| ΔE_c, PBE (eV) | 0 | **+0.281** (two-step; double average +0.287) | **+0.848** (EA route; two-step +0.819, no interior) | **+1.059** (EA route) | +1.585 (EA route) |
| ΔE_v, PBE (eV) | 0 | −0.054 | −0.052 | −0.251 | −0.667 |
| CB share ΔE_c/ΔE_g | — | 0.84 | 0.94 | 0.81 | 0.70 |
| ΔE_c, HSE-scaled (eV) [CALCULATED; same CB share ASSUMED] | 0 | 0.298–0.311 | 0.899–0.939 | 1.122–1.172 | 1.680–1.754 |
| EA (eV); vacuum-referenced CBM = −EA | 4.776 (bulk-equivalent) | 4.495 | 3.9285 | 3.718 | 3.192 |
| IP (eV) | 5.665 (bulk-equivalent) | 5.719 | 5.717 | 5.916 | 6.332 |
| Vacuum asymmetry, left − right (meV) | — | 0.0 | 0.0 | −27 | 0.0 |
| m*, in-plane, PBE (m0) | 0.159 | 0.2064 | 0.2811 | 0.3348 | 0.4282 |
| Δm* (m0) | 0 | +0.047 | +0.122 | +0.176 | +0.269 |
| E2 − E1 at Γ (eV) | — | 0.719 | 1.499 | 1.815 | 1.887 |
| Kane α, PBE (1/eV) | 0.63 | 0.50 | 0.38 | 0.33 | 0.25 |
| m* for TCAD, V2 convention 0.208 + Δm* [CALCULATED] | 0.208 (LITERATURE, Stokey 2021) | 0.255 | 0.330 | 0.384 | 0.477 |
| NC300, 3-D, V2 form (cm⁻³) [CALCULATED] | 2.38e18 | 3.24e18 | 4.76e18 | 5.97e18 | 8.27e18 |
| NC300, quasi-2D N2D/t (cm⁻³) [CALCULATED] | — | 1.38e19 | 3.56e19 | 5.53e19 | 1.01e20 |
| Ratio quasi-2D / 3-D (equivalent E_c shift) | — | 4.26 (−37.5 meV) | 7.49 (−52 meV) | 9.26 (−58 meV) | 12.2 (−65 meV) |
| VBM weight on OH (OH share of atoms) | — | 0.2 % (27 %): interior | 73 % (50 %): surface, proxy | 76 % (63 %): surface, one side | 98 % (86 %): all OH |
| CBM weight on OH | — | 1.4 %: interior | 23 %: interior, proxy | 36 %: interior-weighted | 56 % |
| Validity | reference | bulk-like interior | no bulk-like interior | VB edge is a surface state | **outside the recipe**: relaxes into an In(OH)₃-like layer; excluded from all laws |

### Notes on the table

**Bulk-equivalent EA and IP.**
- They are the 2 nm EA plus ΔE_c(2 nm), and the 2 nm IP plus ΔE_v(2 nm).
- They hold only for the H/OH-terminated (001) surface, in PBE.
- They are reported but not proposed for AFFINITY:
  - the termination dipole is not that of the device surfaces;
  - an HSE correction of the absolute edges does not exist;
  - χ is degenerate with the gate work function and Q_f (`analysis_2026-09-25/SYNTHESIS.md`).

**The 1 nm surface check is a proxy.** The pure 1 nm slab has no projwfc run, so its W twin was used (`iwo_slab1_final_cpu`, VB top = band 311).
- In the pure 2 nm slab, the valence states with the most OH weight (20–27 %) lie 50–70 meV below the VBM.
- In the 2 nm W slab, four OH-surface bands (71–75 % OH weight) form the VB top. They sit 67 meV above the highest interior-like valence state.

**Quasi-2D NC300.** It is defined as N2D/t, with N2D = m* kT/(πħ²), the label thickness t and the V2-convention mass. The second subband is included with its Boltzmann weight, which is at most 8e-13.
- It is the Boltzmann-equivalent density of states, valid in subthreshold.
- In the degenerate on-state, the 3-D Fermi–Dirac form in ATLAS overstates n at a given Fermi level: by a factor of 1.7 at E_F − E_1 = 4.7 kT, the level that n_s ≈ 1.3e13 cm⁻² at V_G = 3 V implies. Here F_1/2 = 8.10 against ln(1 + e^η) = 4.70.

**Kane α.** It is overestimated, because the PBE gap is too small. It is reported, not mapped: ATLAS drift-diffusion uses a parabolic NC300 for a user material.

## 4. Tungsten (PBE, crystalline cells, one W per cell)

| Quantity | bulk, W on 24d | bulk, W on 8b | 1 nm slab | 2 nm slab |
|---|---|---|---|---|
| W share of the cations | 3.1 % | 3.1 % | 4.2 % | 1.8 % |
| Donated electrons (3 per W), cm⁻³ [CALCULATED] | 2.7e21 | 2.7e21 | 3.0e21 (2.8e14 cm⁻²) | 1.4e21 (2.8e14 cm⁻²) |
| VB top band; host CB bottom band (projwfc) | 351; 352 | 351; 352 | 311; 312 | 663; 664 |
| E_F − host CB bottom at Γ (eV) | 1.763 | 1.713 | 1.228 | 1.238 |
| W-5d-rich level − host CB bottom at Γ (eV), W 5d weight | **+1.764** (0.54) | **+1.803** (0.50) | **+1.223** (0.56) | **+1.341** (0.52) |
| Electrons in the host CB bottom band (of 3) | 1.79 | 1.93 | 2.00 | 2.04 (+0.86 in the 2nd host subband) |
| W-5d-projected electrons (of 3) | 0.29 (10 %) | 0.36 (12 %) | 0.43 (14 %) | **0.09 (3 %)** |
| Gap, VB top to host CB at Γ (eV); change vs pure | 0.862; −0.031 | 0.894; +0.001 | 1.719; −0.069 | 1.076; −0.148 (VB top is an OH surface state; interior ≈ −0.08) |
| EA; IP; work function (eV) | — | — | 4.069; 5.789; 2.84 | 4.746; 5.823; 3.51 |
| Change vs the pure twin: EA, IP (eV) | — | — | +0.141, +0.072 | +0.251, +0.104 |

### Other W results [COMPUTED, `results/summary.json`, `RESULTS_LOG.md`]
- **Site.** W prefers 24d by 0.258 eV.
- **Charge state.** The mean W–O bond is 1.98 Å, which matches W⁶⁺ (Shannon 1976 [LITERATURE]: W⁶⁺ 1.98 Å, W⁴⁺ 2.04 Å).
- **Magnetism.** Weak moments of 0.6–0.7 μB per cell appear at 3×3×3 k-points. This is preliminary.

### How to read the W table [INFERRED]
- Each cell holds 1.4–5.5e21 cm⁻³ donated electrons, so E_F lies 1.2–1.8 eV inside the conduction band. The W-5d-rich level holds some electrons only because the band is filled up to it.
- The thinner and more W-rich 1 nm cell puts more of the charge on W (14 %). The 2 nm cell is the closest to the devices, at 1.8 % W, and puts only 3 % there.
- At device densities (below 1e19 cm⁻³, E_F below E_c) the level is empty.
- **For ATLAS:**
  - W is a fully ionized donor with a negative ionization energy, i.e. no DEFECTS or trap entry for W.
  - A fully active "~2 % W" would give about 1e21 cm⁻³, which is incompatible with films that switch off. Most of the W donors must therefore be compensated or inactive, and the DFT cannot say by what.
  - The changes in gap and EA with W are dominated by this extreme filling. They do not transfer to device densities.
- **Limitation.** This is PBE only. A hybrid functional can lower localized d levels, and no HSE calculation of a W cell exists.

## 5. Mapping to ATLAS parameters

| ATLAS parameter | Law | DFT input (label) | Other inputs (label) | V2 | New here |
|---|---|---|---|---|---|
| **EG300** | E_g,bulk + ΔE_g(t) | ΔE_g points COMPUTED. Law ΔE_g = 0.8143·t^−1.3152 (t = H–H, nm) is FITTED to the 0.695/0.930/1.962 nm DFT points; residuals ≤ 0.4 %. Optional HSE factor ×1.06–1.11 (ASSUMED transfer). | E_g,bulk = 3.05 eV, LITERATURE (Fan 2021) | Used: 2-point PBE law 0.83997·t^−1.34569 (Lin labels) | 0.695 nm point; 3-point law; HSE option. EG300 enters only n_i (holes are not solved), so its effect on I_D is negligible [INFERRED]. |
| **AFFINITY** | χ_bulk − ΔE_c(t) | ΔE_c COMPUTED: two-step at 2 nm, EA route below. Laws, all FITTED to DFT points, at 2.0 / 6.3 / 13.2 nm: (a) V2 0.78504·t^−1.504: 0.277 / 0.049 / 0.016; (b) 3-point H–H 0.7015·t^−1.3167 (residuals +7/−9/+3 %): 0.282 / 0.062 / 0.024; (c) 1–2 nm H–H 0.7616·t^−1.4778: 0.273 / 0.050 / 0.017; (d) MODEL box E1 = E21/3: 0.234 / 0.046 / 0.013. Optional HSE factor ×1.06–1.11. | χ_bulk = 4.3 eV, LITERATURE (Fan 2021). The DFT bulk-equivalent EA of 4.78 eV (PBE, H-(001)) is not proposed. | Used: 0.281 @ 1.98 nm, 0.848 @ 0.95 nm | 0.695 nm point (1.059 eV); extrapolation spread at 6.3/13.2 nm; HSE option (+17 to +31 meV at 2 nm, +3 to +7 meV at 6.3 nm). For T4, tabulated points `{"0.695": dEc 1.0586, dEg 1.3099, dm 0.1758}` (`dft_inputs.json`, same format as `t4_prepare.py`; T4 is on hold, D-07). |
| **NC300** | V2: 2(2πm*kT/h²)^1.5 with m* = 0.208 + Δm*(t). Candidate at t ≤ 2 nm: N2D/t. | Δm* COMPUTED. Law Δm* = 0.1112·t^−1.2639 (FITTED to DFT points; V2 had 0.11416·t^−1.29453). E2 − E1 COMPUTED. Crossover box (δ = 1.40 nm, m_z = 0.139 m0) is a MODEL from the 1 and 2 nm E21. | m*_bulk = 0.208, LITERATURE (Stokey 2021) | Used: 3-D form | Quasi-2D: 1.38e19 at 2 nm (×4.3, −37.5 meV). MODEL: ×1.47 (−10 meV) at 6.3 nm, ×0.88 (+3 meV) at 13.2 nm. Needs one ATLAS test before any use. If adopted, Q_f must be refitted. |
| **Quantum-confinement model** (if one is ever switched on) | the solver computes the confinement itself | in-plane m* COMPUTED; m_z only from the MODEL (0.139) | — | not used | **Then the ΔE_c/ΔE_g laws must be switched off** (double counting). Check the mass keywords in the installed manual first. |
| **ARICHN** (Schottky S/D only) | 120.17 A cm⁻² K⁻² × m*(t) | m*(t) as above | — | not used (ideal ohmic S/D) | Relevant only if the Pd contacts are made Schottky. The Mott–Schottky barrier would then be WF_Pd − AFFINITY(t), which ΔE_c raises by 0.28 eV at 2 nm. WF_Pd is a LITERATURE input that must be cited. Pinning is not computed. |
| **ME.TUNNEL** (gate tunnelling) | oxide tunnelling mass | none: this DFT has no HfO2/Al2O3 | LITERATURE needed | — | Not derivable here. |
| **DOPING / N_d,eff(t)** | unchanged: FITTED 2.5e17·[1 + (t/20)^4] | W is a resonant, fully ionized donor with 3 e per W; 3 % W-5d-projected at 2 nm (COMPUTED) | — | Qualitative only | Supports keeping N_d,eff FITTED. DFT cannot give the compensated (active) fraction. |
| **DEFECTS / INTDEFECTS / INTERFACE QF** | unchanged: tail FITTED; deep Gaussian ASSUMED; D_it sheet ASSUMED; Q_f FITTED | No W gap state. The CB edge is interior at every t ≥ 0.695 nm. OH states appear only at the VB edge, are donor-like near E_v and stay neutral in n-type operation. | — | Not DFT-based | No DFT basis for acceptor-like surface states near E_c of an OH surface. The real Al2O3/IWO interface and the air surface are not computed. |
| **MUN** (μ_band) | unchanged: FITTED | m*(2)/m*(13.2) = 1.20 (COMPUTED + LITERATURE bulk) | — | not used | At constant scattering time the mass gives a mobility ratio of 0.83; the fitted ratio is 0.28. Most of the mobility drop is not band-structural [INFERRED]. |
| **PERMITTIVITY** | unchanged: 9.3, MEASURED (Januar 2026 SI) | none (no DFPT) | — | — | — |

### ATLAS constraints that apply when these are implemented
These are from `01_CURRENT_STATE.md` §K.
- NC300, EG300 and AFFINITY are MATERIAL parameters, set once per deck. Thickness laws therefore enter through the deck generator, as in V2.
- Nothing here needs more than the existing traps (MAXTRAPS ≤ 10).
- A change of NC300 at 2 nm must be followed by a Q_f refit. Q_f is shared and acts as one number with χ and ΔE_c (SYNTHESIS).

## 6. What V2 already used and what is new

### Already in V2 (`config/iwo_material_model_v2.yaml`, `analysis_2026-10-06_V2/make_v2_model.py`)
- ΔE_g at 0.95 and 1.98 nm: 0.900 and 0.335 eV.
- ΔE_c at 0.95 and 1.98 nm: 0.848 and 0.281 eV.
- Δm* at 0.95 and 1.98 nm: 0.122 and 0.047 m0, added to the 0.208 m0 literature bulk mass.
- NC300 from the 3-D formula.
- HSE: only as a check (ratio 1.06). It was not applied.
- W: only qualitatively (N_d,eff stays fitted).
- 2 nm band edges bulk-like: only qualitatively.
- The `points` slots for thin films are empty: `t4_prepare.py` was never run, and `thin_dft.json` does not exist.

### New in this extraction
- **Thin films.** Full read-out of the 0.695 and 0.461 nm films: gap, ΔE_c, Δm*, EA/IP, E21, surface character and validity flag.
- **2 nm alignment.** The two-step ΔE_c(2 nm) was re-computed on the slab side and gives +0.2813 eV.
- **Laws.** 3-point laws, and the spread of the extrapolation at 6.3 and 13.2 nm.
- **HSE option.** HSE-scaled ΔE_g and ΔE_c.
- **Subbands and density of states.** Subband spacings, and the quasi-2D NC300 candidate with its MODEL crossover.
- **Non-parabolicity.** Kane α (PBE).
- **Surface character.** At 0.695, 0.461 and 1 nm (proxy), and in the 2 nm W slab.
- **2 nm W slab analysis.** This was pending in `01_CURRENT_STATE.md` §F. It gives the filling, the W level and the W effect.
- **All W cells.** One consistent electron-filling and W-5d-projection analysis of all four cells.
- **Absolute alignment.** Bulk-equivalent EA/IP (PBE, H-(001)).

## 7. Gaps: what this DFT cannot give

1. **Absolute E_g and χ of amorphous IWO.**
   - PBE gives 0.89 eV and HSE06 2.07–2.11 eV, both at the PBE lattice and both below the literature bulk value.
   - The EA depends on the termination.
   - The bulk anchors of EG300 and AFFINITY therefore stay LITERATURE.
2. **HSE band-edge partition.** No HSE planar average exists, and the HSE ratio exists only at 1 nm. Keeping the PBE CB share is ASSUMED.
3. **HSE for W cells.** The position of the W 5d level beyond PBE is unknown.
4. **Mass of the W slabs.** The 1 nm bands run aborted, and the 2 nm job ran without bands.
5. **Films thicker than 2 nm.** No slab exists, so every value at 6.3 and 13.2 nm is an extrapolation (spread in §5).
6. **Compensation and the effective donor density.** No V_O, H, O_i or W-complex calculations exist yet (COMPLETE_PLAN 2B, item 3). N_d,eff stays FITTED.
7. **Interfaces.** The Al2O3/IWO interface and the air-exposed surface are not computed (2B, item 4). D_it and Q_f stay ASSUMED/FITTED.
8. **Band tails and localization.** Crystalline cells have no tails (amorphous series, plan 2A). N_t and W_TA stay FITTED.
9. **Dielectric constant.** There is no DFPT calculation. ε_r stays MEASURED (9.3).
10. **Mobility.** Scattering is not computed. μ_band stays FITTED; DFT gives only m*.
11. **Other.** The temperature coefficients (EGALPHA/EGBETA), the gate-field (Stark) shift of the subbands, the Pd/IWO barrier with pinning, and second structural samples are not computed.

## 8. Reproduce

```
"<venv>\Scripts\python.exe" analysis_2026-10-10_campaign\dft_to_tcad_extract.py
```

- **Runtime.** About 1 minute.
- **What it reads.** Only QE output files.
- **What it writes.** `dft_inputs_raw.json` (full machine output) and `dft_inputs.json` (curated, labelled, with sources), both in this folder.
- **What it does not do.** It changes no other file and launches no simulator.


=== FILE: campaign_C10_S0a_smoke.json (sha256 62ea9329daf7) ===
{
 "campaign": "campaign_C10_S0a_smoke",
 "purpose": "2026-10-10 DFT-informed campaign, S0-01. Generated by analysis_2026-10-10_campaign/make_campaign_configs.py from campaign_matrix.json (entries verbatim, matrix order). Design: analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md.",
 "plan_file": "config\\campaign_C10_S0a_smoke.json",
 "placeholders": {},
 "runs": [
  {
   "id": "S0-01",
   "thickness": 2.0,
   "label": "c10_s0_01_2p0",
   "purpose": "Smoke 1 / primary shared baseline at 2.0 nm: new DFT laws (fit3 dEc/dEg/dm), quasi-2D NC300, surface tail Nt=Ns/t, constant Nd, shared Qf, mu from the shared law, tmun=0. Checks the new option code path (nc300_override) and that every override reaches the deck.",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0",
    "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19"
   ],
   "run_dir": "results/runs/run_0061_2p0_c10_s0_01_2p0",
   "run_id": "run_0061",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 395.8,
   "active_rmse_dec": 0.3670315891870657,
   "sub_rmse_dec": 0.6296206673938449,
   "on_rmse_dec": 0.22249557601846148,
   "Id3V_err_pct": 16.710546480511468,
   "sim": {
    "Vth_cc_1e-9_V": 0.5305987532639841,
    "Vth_lin_V": 1.3424477495326073,
    "SS_mV_dec": 75.05091965987425,
    "SS_min_window_mV_dec": 75.05091965987425,
    "SS_cc_1e-10_1e-8_mV_dec": 227.8527920759141,
    "gm_max_A_V_um": 3.5837000000000026e-07,
    "mu_FE_cm2Vs": 11.433523203867935,
    "Ion_A_per_um": 5.94017e-07,
    "Ioff_A_per_um": 3.3799999999999822e-21,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 46,
    "Ion_over_Ioff": 175744674556213.94,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.6618205007741922,
    "Vth_lin_V": 1.6630785395324494,
    "SS_mV_dec": 84.45385574424456,
    "SS_min_window_mV_dec": 84.45385574424456,
    "SS_cc_1e-10_1e-8_mV_dec": 269.89862041948567,
    "gm_max_A_V_um": 3.8070000000000266e-07,
    "mu_FE_cm2Vs": 12.145944927623823,
    "Ion_A_per_um": 5.08966e-07,
    "Ioff_A_per_um": 1.07931e-16,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 4715660931.521065,
    "off_band_median_A_per_um": 4.60552e-15
   },
   "max_kcl_A": 1.0000000000118097e-17,
   "wall_s": 399.5
  }
 ]
}

=== FILE: campaign_C10_S0b_smoke.json (sha256 3415483d9cea) ===
{
 "campaign": "campaign_C10_S0b_smoke",
 "purpose": "2026-10-10 DFT-informed campaign, S0-02. Generated by analysis_2026-10-10_campaign/make_campaign_configs.py from campaign_matrix.json (entries verbatim, matrix order). Design: analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md.",
 "plan_file": "config\\campaign_C10_S0b_smoke.json",
 "placeholders": {},
 "runs": [
  {
   "id": "S0-02",
   "thickness": 2.0,
   "label": "c10_s0_02_2p0",
   "purpose": "Smoke 2 / gate-leakage code path and first quantitative leakage result: S0-01 + self-consistent direct/FN-regime tunnelling QTNLSC.EL (qtnl.derivs) through Al2O3/HfO2 with the leakage-maximising oxide set, j.tun logged, oxide mesh 0.25 nm. Must show non-zero I_G and KCL pass; compares I_D(off) and I_G with the 2 nm floor (the smallest).",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0",
    "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19",
    "solver.physics_options.gate_tunnelling.enabled=1",
    "solver.physics_options.gate_tunnelling.model=qtnlsc",
    "solver.physics_options.gate_tunnelling.set=worst"
   ],
   "run_dir": "results/runs/run_0067_2p0_c10_s0_02_2p0",
   "run_id": "run_0067",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 1246.0,
   "active_rmse_dec": 0.3664675933301878,
   "sub_rmse_dec": 0.6296206673938449,
   "on_rmse_dec": 0.22125980411634513,
   "Id3V_err_pct": 3.3617176785875724,
   "sim": {
    "Vth_cc_1e-9_V": 0.5305987532639841,
    "Vth_lin_V": 1.2606982216794251,
    "SS_mV_dec": 75.05073949409878,
    "SS_min_window_mV_dec": 75.05073949409878,
    "SS_cc_1e-10_1e-8_mV_dec": 227.8527920759141,
    "gm_max_A_V_um": 3.357099999999999e-07,
    "mu_FE_cm2Vs": 10.710573080253647,
    "Ion_A_per_um": 5.26076e-07,
    "Ioff_A_per_um": 1.21447e-20,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 8,
    "Ion_over_Ioff": 43317331840226.6,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.6618205007741922,
    "Vth_lin_V": 1.6630785395324494,
    "SS_mV_dec": 84.45385574424456,
    "SS_min_window_mV_dec": 84.45385574424456,
    "SS_cc_1e-10_1e-8_mV_dec": 269.89862041948567,
    "gm_max_A_V_um": 3.8070000000000266e-07,
    "mu_FE_cm2Vs": 12.145944927623823,
    "Ion_A_per_um": 5.08966e-07,
    "Ioff_A_per_um": 1.07931e-16,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 4715660931.521065,
    "off_band_median_A_per_um": 4.60552e-15
   },
   "max_kcl_A": 1.0399999999995911e-10,
   "wall_s": 1247.9,
   "earlier_records": [
    {
     "id": "S0-02",
     "thickness": 2.0,
     "label": "c10_s0_02_2p0",
     "purpose": "Smoke 2 / gate-leakage code path and first quantitative leakage result: S0-01 + self-consistent direct/FN-regime tunnelling QTNLSC.EL (qtnl.derivs) through Al2O3/HfO2 with the leakage-maximising oxide set, j.tun logged, oxide mesh 0.25 nm. Must show non-zero I_G and KCL pass; compares I_D(off) and I_G with the 2 nm floor (the smallest).",
     "mode": "transfer",
     "overrides": [
      "thickness_laws.dEc_eV.a=0.70147",
      "thickness_laws.dEc_eV.p=1.31669",
      "thickness_laws.dEg_QC_eV.a=0.81431",
      "thickness_laws.dEg_QC_eV.p=1.31518",
      "thickness_laws.mstar_m0.b=0.11116",
      "thickness_laws.mstar_m0.q=1.26387",
      "thickness_laws.Nt_cm3.Nt2=2e+19",
      "thickness_laws.Nt_cm3.alpha=1",
      "thickness_laws.WTA_eV.value=0.04",
      "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
      "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
      "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
      "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
      "solver.dos_levels.numa=384",
      "solver.dos_levels.numd=192",
      "solver.tmun=0",
      "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19",
      "solver.physics_options.gate_tunnelling.enabled=1",
      "solver.physics_options.gate_tunnelling.model=qtnlsc",
      "solver.physics_options.gate_tunnelling.set=worst"
     ],
     "error": "RuntimeError: run_0066: SIGN_REVERSAL; inspect C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\results\\runs\\run_0066_2p0_c10_s0_02_2p0/terminal_currents.csv",
     "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_campaign.py\", line 58, in run_entry\n    dest = execute(float(e['thickness']), e['label'], ov, timeout=e.get('timeout'))\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_atlas.py\", line 197, in execute\n    if verdict != 'OK': finish(verdict, 'yes', f'{verdict}: max KCL {v[\"max_kcl_abs_A\"]:.2g} A'); raise RuntimeError(f'{rid}: {verdict}; inspect {dest}/terminal_currents.csv')\n                                                                                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nRuntimeError: run_0066: SIGN_REVERSAL; inspect C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\results\\runs\\run_0066_2p0_c10_s0_02_2p0/terminal_currents.csv\n",
     "wall_s": 588.7,
     "earlier_records": [
      {
       "id": "S0-02",
       "thickness": 2.0,
       "label": "c10_s0_02_2p0",
       "purpose": "Smoke 2 / gate-leakage code path and first quantitative leakage result: S0-01 + self-consistent direct/FN-regime tunnelling QTNLSC.EL (qtnl.derivs) through Al2O3/HfO2 with the leakage-maximising oxide set, j.tun logged, oxide mesh 0.25 nm. Must show non-zero I_G and KCL pass; compares I_D(off) and I_G with the 2 nm floor (the smallest).",
       "mode": "transfer",
       "overrides": [
        "thickness_laws.dEc_eV.a=0.70147",
        "thickness_laws.dEc_eV.p=1.31669",
        "thickness_laws.dEg_QC_eV.a=0.81431",
        "thickness_laws.dEg_QC_eV.p=1.31518",
        "thickness_laws.mstar_m0.b=0.11116",
        "thickness_laws.mstar_m0.q=1.26387",
        "thickness_laws.Nt_cm3.Nt2=2e+19",
        "thickness_laws.Nt_cm3.alpha=1",
        "thickness_laws.WTA_eV.value=0.04",
        "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
        "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
        "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
        "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
        "solver.dos_levels.numa=384",
        "solver.dos_levels.numd=192",
        "solver.tmun=0",
        "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19",
        "solver.physics_options.gate_tunnelling.enabled=1",
        "solver.physics_options.gate_tunnelling.model=qtnlsc",
        "solver.physics_options.gate_tunnelling.set=worst"
       ],
       "run_dir": "results/runs/run_0065_2p0_c10_s0_02_2p0",
       "run_id": "run_0065",
       "status": "REAL_ATLAS_SCORED",
       "elapsed_s": 388.7,
       "active_rmse_dec": 0.367031626861457,
       "sub_rmse_dec": 0.6296207568103158,
       "on_rmse_dec": 0.22249557601846148,
       "Id3V_err_pct": 16.710546480511468,
       "sim": {
        "Vth_cc_1e-9_V": 0.5305987532639841,
        "Vth_lin_V": 1.3424477495326073,
        "SS_mV_dec": 75.05046924208132,
        "SS_min_window_mV_dec": 75.05046924208132,
        "SS_cc_1e-10_1e-8_mV_dec": 227.8527920759141,
        "gm_max_A_V_um": 3.5837000000000026e-07,
        "mu_FE_cm2Vs": 11.433523203867935,
        "Ion_A_per_um": 5.94017e-07,
        "Ioff_A_per_um": 8.45097e-20,
        "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
        "native_zero_count": 18,
        "Ion_over_Ioff": 7028980105242.356,
        "off_band_median_A_per_um": null
       },
       "exp": {
        "Vth_cc_1e-9_V": 0.6618205007741922,
        "Vth_lin_V": 1.6630785395324494,
        "SS_mV_dec": 84.45385574424456,
        "SS_min_window_mV_dec": 84.45385574424456,
        "SS_cc_1e-10_1e-8_mV_dec": 269.89862041948567,
        "gm_max_A_V_um": 3.8070000000000266e-07,
        "mu_FE_cm2Vs": 12.145944927623823,
        "Ion_A_per_um": 5.08966e-07,
        "Ioff_A_per_um": 1.07931e-16,
        "Ioff_definition": "min Id over sweep",
        "native_zero_count": 0,
        "Ion_over_Ioff": 4715660931.521065,
        "off_band_median_A_per_um": 4.60552e-15
       },
       "max_kcl_A": 1.0000000000118097e-17,
       "wall_s": 399.5,
       "earlier_records": [
        {
         "id": "S0-02",
         "thickness": 2.0,
         "label": "c10_s0_02_2p0",
         "purpose": "Smoke 2 / gate-leakage code path and first quantitative leakage result: S0-01 + self-consistent direct/FN-regime tunnelling QTNLSC.EL (qtnl.derivs) through Al2O3/HfO2 with the leakage-maximising oxide set, j.tun logged, oxide mesh 0.25 nm. Must show non-zero I_G and KCL pass; compares I_D(off) and I_G with the 2 nm floor (the smallest).",
         "mode": "transfer",
         "overrides": [
          "thickness_laws.dEc_eV.a=0.70147",
          "thickness_laws.dEc_eV.p=1.31669",
          "thickness_laws.dEg_QC_eV.a=0.81431",
          "thickness_laws.dEg_QC_eV.p=1.31518",
          "thickness_laws.mstar_m0.b=0.11116",
          "thickness_laws.mstar_m0.q=1.26387",
          "thickness_laws.Nt_cm3.Nt2=2e+19",
          "thickness_laws.Nt_cm3.alpha=1",
          "thickness_laws.WTA_eV.value=0.04",
          "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
          "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
          "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
          "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
          "solver.dos_levels.numa=384",
          "solver.dos_levels.numd=192",
          "solver.tmun=0",
          "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19",
          "solver.physics_options.gate_tunnelling.enabled=1",
          "solver.physics_options.gate_tunnelling.model=qtnlsc",
          "solver.physics_options.gate_tunnelling.set=worst"
         ],
         "error": "RuntimeError: run_0064: Error: Memory allocation failure.  Try killing processes",
         "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_campaign.py\", line 58, in run_entry\n    dest = execute(float(e['thickness']), e['label'], ov, timeout=e.get('timeout'))\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_atlas.py\", line 192, in execute\n    if sc['errors']: finish('SIMULATOR_ERROR', 'no', sc['errors'][0][:120]); raise RuntimeError(f'{rid}: {sc[\"errors\"][0]}')\n                                                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nRuntimeError: run_0064: Error: Memory allocation failure.  Try killing processes\n",
         "wall_s": 24.8,
         "earlier_records": [
          {
           "id": "S0-02",
           "thickness": 2.0,
           "label": "c10_s0_02_2p0",
           "purpose": "Smoke 2 / gate-leakage code path and first quantitative leakage result: S0-01 + self-consistent direct/FN-regime tunnelling QTNLSC.EL (qtnl.derivs) through Al2O3/HfO2 with the leakage-maximising oxide set, j.tun logged, oxide mesh 0.25 nm. Must show non-zero I_G and KCL pass; compares I_D(off) and I_G with the 2 nm floor (the smallest).",
           "mode": "transfer",
           "overrides": [
            "thickness_laws.dEc_eV.a=0.70147",
            "thickness_laws.dEc_eV.p=1.31669",
            "thickness_laws.dEg_QC_eV.a=0.81431",
            "thickness_laws.dEg_QC_eV.p=1.31518",
            "thickness_laws.mstar_m0.b=0.11116",
            "thickness_laws.mstar_m0.q=1.26387",
            "thickness_laws.Nt_cm3.Nt2=2e+19",
            "thickness_laws.Nt_cm3.alpha=1",
            "thickness_laws.WTA_eV.value=0.04",
            "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
            "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
            "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
            "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
            "solver.dos_levels.numa=384",
            "solver.dos_levels.numd=192",
            "solver.tmun=0",
            "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19",
            "solver.physics_options.gate_tunnelling.enabled=1",
            "solver.physics_options.gate_tunnelling.model=qtnlsc",
            "solver.physics_options.gate_tunnelling.set=worst"
           ],
           "error": "RuntimeError: run_0063: Error: Memory allocation failure.  Try killing processes",
           "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_campaign.py\", line 58, in run_entry\n    dest = execute(float(e['thickness']), e['label'], ov, timeout=e.get('timeout'))\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_atlas.py\", line 192, in execute\n    if sc['errors']: finish('SIMULATOR_ERROR', 'no', sc['errors'][0][:120]); raise RuntimeError(f'{rid}: {sc[\"errors\"][0]}')\n                                                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nRuntimeError: run_0063: Error: Memory allocation failure.  Try killing processes\n",
           "wall_s": 15.6,
           "earlier_records": [
            {
             "id": "S0-02",
             "thickness": 2.0,
             "label": "c10_s0_02_2p0",
             "purpose": "Smoke 2 / gate-leakage code path and first quantitative leakage result: S0-01 + self-consistent direct/FN-regime tunnelling QTNLSC.EL (qtnl.derivs) through Al2O3/HfO2 with the leakage-maximising oxide set, j.tun logged, oxide mesh 0.25 nm. Must show non-zero I_G and KCL pass; compares I_D(off) and I_G with the 2 nm floor (the smallest).",
             "mode": "transfer",
             "overrides": [
              "thickness_laws.dEc_eV.a=0.70147",
              "thickness_laws.dEc_eV.p=1.31669",
              "thickness_laws.dEg_QC_eV.a=0.81431",
              "thickness_laws.dEg_QC_eV.p=1.31518",
              "thickness_laws.mstar_m0.b=0.11116",
              "thickness_laws.mstar_m0.q=1.26387",
              "thickness_laws.Nt_cm3.Nt2=2e+19",
              "thickness_laws.Nt_cm3.alpha=1",
              "thickness_laws.WTA_eV.value=0.04",
              "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
              "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
              "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
              "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
              "solver.dos_levels.numa=384",
              "solver.dos_levels.numd=192",
              "solver.tmun=0",
              "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19",
              "solver.physics_options.gate_tunnelling.enabled=1",
              "solver.physics_options.gate_tunnelling.model=qtnlsc",
              "solver.physics_options.gate_tunnelling.set=worst"
             ],
             "error": "RuntimeError: run_0062: Error: Memory allocation failure.  Try killing processes",
             "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_campaign.py\", line 58, in run_entry\n    dest = execute(float(e['thickness']), e['label'], ov, timeout=e.get('timeout'))\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_atlas.py\", line 192, in execute\n    if sc['errors']: finish('SIMULATOR_ERROR', 'no', sc['errors'][0][:120]); raise RuntimeError(f'{rid}: {sc[\"errors\"][0]}')\n                                                                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nRuntimeError: run_0062: Error: Memory allocation failure.  Try killing processes\n",
             "wall_s": 14.2
            }
           ]
          }
         ]
        }
       ]
      }
     ]
    }
   ]
  }
 ]
}

=== FILE: campaign_C10_S1_baselines.json (sha256 2ab4bf54860f) ===
{
 "campaign": "campaign_C10_S1_baselines",
 "purpose": "2026-10-10 DFT-informed campaign, S1_baseline_numerics. Generated by analysis_2026-10-10_campaign/make_campaign_configs.py from campaign_matrix.json (entries verbatim, matrix order). Design: analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md.",
 "plan_file": "config\\campaign_C10_S1_baselines.json",
 "placeholders": {},
 "runs": [
  {
   "id": "S1-01",
   "thickness": 6.3,
   "label": "c10_s1_01_6p3",
   "purpose": "Primary shared baseline at 6.3 nm (same shared parameters as S0-01; nothing tuned to this film).",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[6.3]=44.1956",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0"
   ],
   "run_dir": "results/runs/run_0068_6p3_c10_s1_01_6p3",
   "run_id": "run_0068",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 493.7,
   "active_rmse_dec": 1.1810147145730199,
   "sub_rmse_dec": 1.8148307702061381,
   "on_rmse_dec": 0.9364492128669714,
   "Id3V_err_pct": 386.6971703912277,
   "sim": {
    "Vth_cc_1e-9_V": 0.24361873146849677,
    "Vth_lin_V": 1.1341980235651854,
    "SS_mV_dec": 85.88741524048547,
    "SS_min_window_mV_dec": 85.88741524048547,
    "SS_cc_1e-10_1e-8_mV_dec": 190.25762227707452,
    "gm_max_A_V_um": 1.0524000000000007e-06,
    "mu_FE_cm2Vs": 33.576024275889765,
    "Ion_A_per_um": 1.96357e-06,
    "Ioff_A_per_um": 2.12952e-21,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 26,
    "Ion_over_Ioff": 922071640557496.6,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.6440037102307175,
    "Vth_lin_V": 1.8199688146658495,
    "SS_mV_dec": 114.6732332017215,
    "SS_min_window_mV_dec": 114.6732332017215,
    "SS_cc_1e-10_1e-8_mV_dec": 295.3670282761616,
    "gm_max_A_V_um": 3.431099999999996e-07,
    "mu_FE_cm2Vs": 10.946664471019112,
    "Ion_A_per_um": 4.03448e-07,
    "Ioff_A_per_um": 5.86207e-15,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 68823470.2076229,
    "off_band_median_A_per_um": 1.52759e-13
   },
   "max_kcl_A": 8.8734841e-17,
   "wall_s": 494.5
  },
  {
   "id": "S1-02",
   "thickness": 13.2,
   "label": "c10_s1_02_13p2",
   "purpose": "Primary shared baseline at 13.2 nm (same shared parameters as S0-01; nothing tuned to this film).",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[13.2]=63.2597",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0"
   ],
   "run_dir": "results/runs/run_0069_13p2_c10_s1_02_13p2",
   "run_id": "run_0069",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 735.4,
   "active_rmse_dec": 0.05597008235350779,
   "sub_rmse_dec": 0.0766641746505101,
   "on_rmse_dec": 0.05103738271871534,
   "Id3V_err_pct": 9.139639624970286,
   "sim": {
    "Vth_cc_1e-9_V": 0.09281557405281662,
    "Vth_lin_V": 0.9129779549134365,
    "SS_mV_dec": 126.20160427188124,
    "SS_min_window_mV_dec": 126.20160427188124,
    "SS_cc_1e-10_1e-8_mV_dec": 161.1651588411554,
    "gm_max_A_V_um": 1.605799999999998e-06,
    "mu_FE_cm2Vs": 51.231831796107635,
    "Ion_A_per_um": 3.35134e-06,
    "Ioff_A_per_um": 7.97535e-21,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 26,
    "Ion_over_Ioff": 420212279084930.44,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.08252222827718106,
    "Vth_lin_V": 1.0440663953192557,
    "SS_mV_dec": 130.77458466120197,
    "SS_min_window_mV_dec": 130.77458466120197,
    "SS_cc_1e-10_1e-8_mV_dec": 160.0202452147923,
    "gm_max_A_V_um": 1.5723999999999987e-06,
    "mu_FE_cm2Vs": 50.16623011346349,
    "Ion_A_per_um": 3.07069e-06,
    "Ioff_A_per_um": 6.42069e-12,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 478249.22243559494,
    "off_band_median_A_per_um": 6.59655e-12
   },
   "max_kcl_A": 2.00779917e-16,
   "wall_s": 736.1
  },
  {
   "id": "S1-03",
   "thickness": 13.2,
   "label": "c10_s1_03_13p2",
   "purpose": "Numerics: 13.2 nm baseline with all mesh spacings x0.7 (x0.5 exceeds 32-bit memory).",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[13.2]=63.2597",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0",
    "geometry.mesh.spacing_factor=0.7"
   ],
   "run_dir": "results/runs/run_0070_13p2_c10_s1_03_13p2",
   "run_id": "run_0070",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 1786.5,
   "active_rmse_dec": 0.05550517748569361,
   "sub_rmse_dec": 0.07456452170527797,
   "on_rmse_dec": 0.051030242569248346,
   "Id3V_err_pct": 9.12433361882834,
   "sim": {
    "Vth_cc_1e-9_V": 0.09248645893973723,
    "Vth_lin_V": 0.9128807225163547,
    "SS_mV_dec": 126.33171843812573,
    "SS_min_window_mV_dec": 126.33171843812573,
    "SS_cc_1e-10_1e-8_mV_dec": 161.1690487413426,
    "gm_max_A_V_um": 1.6055000000000035e-06,
    "mu_FE_cm2Vs": 51.22226052350921,
    "Ion_A_per_um": 3.35087e-06,
    "Ioff_A_per_um": 4.39592e-21,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 14,
    "Ion_over_Ioff": 762268194143660.5,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.08252222827718106,
    "Vth_lin_V": 1.0440663953192557,
    "SS_mV_dec": 130.77458466120197,
    "SS_min_window_mV_dec": 130.77458466120197,
    "SS_cc_1e-10_1e-8_mV_dec": 160.0202452147923,
    "gm_max_A_V_um": 1.5723999999999987e-06,
    "mu_FE_cm2Vs": 50.16623011346349,
    "Ion_A_per_um": 3.07069e-06,
    "Ioff_A_per_um": 6.42069e-12,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 478249.22243559494,
    "off_band_median_A_per_um": 6.59655e-12
   },
   "max_kcl_A": 2.961878e-17,
   "wall_s": 1786.9
  },
  {
   "id": "S1-04",
   "thickness": 2.0,
   "label": "c10_s1_04_2p0",
   "purpose": "Numerics: 2.0 nm baseline with DOS quadrature doubled (768/384) - finds the practical memory limit if it fails.",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
    "solver.tmun=0",
    "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19",
    "solver.dos_levels.numa=768",
    "solver.dos_levels.numd=384"
   ],
   "run_dir": "results/runs/run_0071_2p0_c10_s1_04_2p0",
   "run_id": "run_0071",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 476.8,
   "active_rmse_dec": 0.36701572049614006,
   "sub_rmse_dec": 0.6295423511427469,
   "on_rmse_dec": 0.22253302455995255,
   "Id3V_err_pct": 16.76379168746045,
   "sim": {
    "Vth_cc_1e-9_V": 0.5306202842131837,
    "Vth_lin_V": 1.342292887029287,
    "SS_mV_dec": 75.05162864633394,
    "SS_min_window_mV_dec": 75.05162864633394,
    "SS_cc_1e-10_1e-8_mV_dec": 227.8846370148787,
    "gm_max_A_V_um": 3.584999999999996e-07,
    "mu_FE_cm2Vs": 11.437670755327307,
    "Ion_A_per_um": 5.94288e-07,
    "Ioff_A_per_um": 3.650820000000054e-20,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 35,
    "Ion_over_Ioff": 16278205992078.25,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.6618205007741922,
    "Vth_lin_V": 1.6630785395324494,
    "SS_mV_dec": 84.45385574424456,
    "SS_min_window_mV_dec": 84.45385574424456,
    "SS_cc_1e-10_1e-8_mV_dec": 269.89862041948567,
    "gm_max_A_V_um": 3.8070000000000266e-07,
    "mu_FE_cm2Vs": 12.145944927623823,
    "Ion_A_per_um": 5.08966e-07,
    "Ioff_A_per_um": 1.07931e-16,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 4715660931.521065,
    "off_band_median_A_per_um": 4.60552e-15
   },
   "max_kcl_A": 5.900000000001141e-18,
   "wall_s": 477.6
  },
  {
   "id": "S1-05",
   "thickness": 2.0,
   "label": "c10_s1_05_2p0",
   "purpose": "DFT input check: 2.0 nm with the V2 3-D NC300 instead of the DFT quasi-2D value (x4.27). Quantifies the quasi-2D choice inside ATLAS.",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=17.6897",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0"
   ],
   "run_dir": "results/runs/run_0072_2p0_c10_s1_05_2p0",
   "run_id": "run_0072",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 295.7,
   "active_rmse_dec": 0.05332864674077384,
   "sub_rmse_dec": 0.09124809473621,
   "on_rmse_dec": 0.03254257783441713,
   "Id3V_err_pct": 0.48293992133070507,
   "sim": {
    "Vth_cc_1e-9_V": 0.6727490154240484,
    "Vth_lin_V": 1.5292919997699408,
    "SS_mV_dec": 74.79120562671143,
    "SS_min_window_mV_dec": 74.79120562671143,
    "SS_cc_1e-10_1e-8_mV_dec": 291.95852180792264,
    "gm_max_A_V_um": 3.477399999999995e-07,
    "mu_FE_cm2Vs": 11.094381111457507,
    "Ion_A_per_um": 5.11424e-07,
    "Ioff_A_per_um": 1.7170000000000002e-20,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 24,
    "Ion_over_Ioff": 29785905649388.465,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.6618205007741922,
    "Vth_lin_V": 1.6630785395324494,
    "SS_mV_dec": 84.45385574424456,
    "SS_min_window_mV_dec": 84.45385574424456,
    "SS_cc_1e-10_1e-8_mV_dec": 269.89862041948567,
    "gm_max_A_V_um": 3.8070000000000266e-07,
    "mu_FE_cm2Vs": 12.145944927623823,
    "Ion_A_per_um": 5.08966e-07,
    "Ioff_A_per_um": 1.07931e-16,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 4715660931.521065,
    "off_band_median_A_per_um": 4.60552e-15
   },
   "max_kcl_A": 1.865806e-17,
   "wall_s": 296.7
  },
  {
   "id": "S1-06",
   "thickness": 13.2,
   "label": "c10_s1_06_13p2",
   "purpose": "Electron-only assumption: 13.2 nm baseline solved with two carriers (holes transported, background SRH generation active).",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=1.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[13.2]=63.2597",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0",
    "solver.carriers=carriers=2"
   ],
   "error": "RuntimeError: run_0073: no export (timeout=True); inspect C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\results\\runs\\run_0073_13p2_c10_s1_06_13p2",
   "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_campaign.py\", line 58, in run_entry\n    dest = execute(float(e['thickness']), e['label'], ov, timeout=e.get('timeout'))\n  File \"C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\scripts\\run_atlas.py\", line 193, in execute\n    if not (dest / 'idvg.dat').exists(): finish('TIMEOUT' if timed_out else 'NO_EXPORT', 'no', 'no idvg.dat'); raise RuntimeError(f'{rid}: no export (timeout={timed_out}); inspect {dest}')\n                                                                                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nRuntimeError: run_0073: no export (timeout=True); inspect C:\\Users\\moham\\Downloads\\IWO_Local_Codex_Handoff (1)\\IWO_PHYSICS_CONSTRAINED_MODEL_V1\\results\\runs\\run_0073_13p2_c10_s1_06_13p2\n",
   "wall_s": 3600.7
  },
  {
   "id": "S1-07",
   "thickness": 2.0,
   "label": "c10_s1_07_2p0",
   "purpose": "Native check of the offline profiling (Codex review 2026-10-10): S0-01 with Qf +1.0e+12 cm-2 (dV = -q dQf/Cox = -0.1789 V) and MUN x0.6. The shifted+scaled S0-01 curve must reproduce this run before profiling is used in S3/S4.",
   "mode": "transfer",
   "overrides": [
    "thickness_laws.dEc_eV.a=0.70147",
    "thickness_laws.dEc_eV.p=1.31669",
    "thickness_laws.dEg_QC_eV.a=0.81431",
    "thickness_laws.dEg_QC_eV.p=1.31518",
    "thickness_laws.mstar_m0.b=0.11116",
    "thickness_laws.mstar_m0.q=1.26387",
    "thickness_laws.Nt_cm3.Nt2=2e+19",
    "thickness_laws.Nt_cm3.alpha=1",
    "thickness_laws.WTA_eV.value=0.04",
    "thickness_laws.Nd_eff_cm3.Nd0=2.5e+17",
    "thickness_laws.Nd_eff_cm3.tc_nm=1e9",
    "traps.fixed_interface_charge_Qf_cm2.value=2.38345e+12",
    "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=10.6138",
    "solver.dos_levels.numa=384",
    "solver.dos_levels.numd=192",
    "solver.tmun=0",
    "solver.physics_options.nc300_override_cm3[2.0]=1.373e+19"
   ],
   "run_dir": "results/runs/run_0074_2p0_c10_s1_07_2p0",
   "run_id": "run_0074",
   "status": "REAL_ATLAS_SCORED",
   "elapsed_s": 310.3,
   "active_rmse_dec": 0.7404337567541011,
   "sub_rmse_dec": 1.4489183168844522,
   "on_rmse_dec": 0.20790776118888352,
   "Id3V_err_pct": -22.35984329012155,
   "sim": {
    "Vth_cc_1e-9_V": 0.4011433124828451,
    "Vth_lin_V": 1.1791447792830123,
    "SS_mV_dec": 71.7508410094531,
    "SS_min_window_mV_dec": 71.7508410094531,
    "SS_cc_1e-10_1e-8_mV_dec": 263.3044360229671,
    "gm_max_A_V_um": 2.1701999999999962e-07,
    "mu_FE_cm2Vs": 6.923858597827421,
    "Ion_A_per_um": 3.95162e-07,
    "Ioff_A_per_um": 6.591674999999892e-21,
    "Ioff_definition": "min Id over sweep (min POSITIVE; native zeros counted)",
    "native_zero_count": 28,
    "Ion_over_Ioff": 59948647346843.78,
    "off_band_median_A_per_um": null
   },
   "exp": {
    "Vth_cc_1e-9_V": 0.6618205007741922,
    "Vth_lin_V": 1.6630785395324494,
    "SS_mV_dec": 84.45385574424456,
    "SS_min_window_mV_dec": 84.45385574424456,
    "SS_cc_1e-10_1e-8_mV_dec": 269.89862041948567,
    "gm_max_A_V_um": 3.8070000000000266e-07,
    "mu_FE_cm2Vs": 12.145944927623823,
    "Ion_A_per_um": 5.08966e-07,
    "Ioff_A_per_um": 1.07931e-16,
    "Ioff_definition": "min Id over sweep",
    "native_zero_count": 0,
    "Ion_over_Ioff": 4715660931.521065,
    "off_band_median_A_per_um": 4.60552e-15
   },
   "max_kcl_A": 2.685999999999981e-18,
   "wall_s": 310.7
  }
 ]
}

=== FILE: data_summary.json (sha256 027f14cfebb7) ===
{
  "6p3": {
    "n": 121,
    "vg_min": -3.0,
    "vg_max": 3.0,
    "steps": [
      0.05
    ],
    "id_min": 5.86207e-15,
    "id_max": 4.03448e-07,
    "all_positive": true,
    "monotonic_vg": true,
    "source_columns": "A2:B122"
  },
  "13p2": {
    "n": 121,
    "vg_min": -3.0,
    "vg_max": 3.0,
    "steps": [
      0.05
    ],
    "id_min": 6.42069e-12,
    "id_max": 3.07069e-06,
    "all_positive": true,
    "monotonic_vg": true,
    "source_columns": "C2:D122"
  },
  "31p8": {
    "n": 121,
    "vg_min": -3.0,
    "vg_max": 3.0,
    "steps": [
      0.05
    ],
    "id_min": 2.64862e-07,
    "id_max": 3.59034e-06,
    "all_positive": true,
    "monotonic_vg": true,
    "source_columns": "E2:F122"
  },
  "2p0": {
    "n": 121,
    "vg_min": -3.0,
    "vg_max": 3.0,
    "steps": [
      0.05
    ],
    "id_min": 1.07931e-16,
    "id_max": 5.08966e-07,
    "all_positive": true,
    "monotonic_vg": true,
    "source_columns": "G2:H122"
  },
  "_workbook_sha256": "ce97eccd975207650c5404eff69fa651954cee51d738a60b9811541847d47d12",
  "_units_note": "Workbook headers carry no units; A/um and VDS=0.7 V come from the device/transfer screenshot (inputs/device_and_transfer_curves.png) and the PPTX slide; sweep direction and instrument floor not recorded in the workbook."
}

=== FILE: experimental_clean.csv (sha256 e27a53e8c721) ===
thickness_nm,source_row,vg_V,id_A_per_um
6.3,2,-3.0,1.86207e-13
6.3,3,-2.95,1.80345e-13
6.3,4,-2.9,1.86207e-13
6.3,5,-2.85,1.50345e-13
6.3,6,-2.8,1.38621e-13
6.3,7,-2.75,1.53448e-13
6.3,8,-2.7,1.31034e-13
6.3,9,-2.65,2.00345e-13
6.3,10,-2.6,8.62069e-14
6.3,11,-2.55,6.10345e-14
6.3,12,-2.5,1.0931e-13
6.3,13,-2.45,1.83793e-13
6.3,14,-2.4,1.73793e-13
6.3,15,-2.35,1.58621e-13
6.3,16,-2.3,1.13448e-13
6.3,17,-2.25,1.82414e-13
6.3,18,-2.2,1.96207e-13
6.3,19,-2.15,1.27241e-13
6.3,20,-2.1,1.37931e-13
6.3,21,-2.05,1.47931e-13
6.3,22,-2.0,1.74483e-13
6.3,23,-1.95,1e-13
6.3,24,-1.9,1.88966e-13
6.3,25,-1.85,1.3931e-13
6.3,26,-1.8,1.39655e-13
6.3,27,-1.75,2.12759e-13
6.3,28,-1.7,1.38276e-13
6.3,29,-1.65,1.90345e-13
6.3,30,-1.6,1.45172e-13
6.3,31,-1.55,8.44828e-14
6.3,32,-1.5,1.42759e-13
6.3,33,-1.45,1.64138e-13
6.3,34,-1.4,8.2069e-14
6.3,35,-1.35,7.10345e-14
6.3,36,-1.3,1.48621e-13
6.3,37,-1.25,1.57241e-13
6.3,38,-1.2,1.57241e-13
6.3,39,-1.15,2.01034e-13
6.3,40,-1.1,1.8069e-13
6.3,41,-1.05,1.52759e-13
6.3,42,-1.0,1.24138e-13
6.3,43,-0.95,1.64483e-13
6.3,44,-0.9,1.19655e-13
6.3,45,-0.85,1.28276e-13
6.3,46,-0.8,1.65517e-13
6.3,47,-0.75,1.79655e-13
6.3,48,-0.7,2.05172e-13
6.3,49,-0.65,1.5931e-13
6.3,50,-0.6,9.58621e-14
6.3,51,-0.55,7.89655e-14
6.3,52,-0.5,1.7069e-13
6.3,53,-0.45,1.80345e-13
6.3,54,-0.4,1.34483e-13
6.3,55,-0.35,1.72069e-13
6.3,56,-0.3,1.64138e-13
6.3,57,-0.25,1.59655e-13
6.3,58,-0.2,2.20345e-13
6.3,59,-0.15,8.82759e-14
6.3,60,-0.1,1.83448e-13
6.3,61,-0.05,5.86207e-15
6.3,62,0.0,1.83793e-13
6.3,63,0.05,1.38621e-13
6.3,64,0.1,1.12759e-13
6.3,65,0.15,4.10345e-14
6.3,66,0.2,6.45172e-13
6.3,67,0.25,2.28379e-12
6.3,68,0.3,8.4e-12
6.3,69,0.35,2.09586e-11
6.3,70,0.4,6.04138e-11
6.3,71,0.45,1.2669e-10
6.3,72,0.5,2.42966e-10
6.3,73,0.55,4.15172e-10
6.3,74,0.6,6.82414e-10
6.3,75,0.65,1.05345e-09
6.3,76,0.7,1.57e-09
6.3,77,0.75,2.2631e-09
6.3,78,0.8,3.10414e-09
6.3,79,0.85,4.08276e-09
6.3,80,0.9,5.43103e-09
6.3,81,0.95,7.07586e-09
6.3,82,1.0,9.02414e-09
6.3,83,1.05,1.11034e-08
6.3,84,1.1,1.37517e-08
6.3,85,1.15,1.67517e-08
6.3,86,1.2,2.01276e-08
6.3,87,1.25,2.39e-08
6.3,88,1.3,2.78655e-08
6.3,89,1.35,3.22621e-08
6.3,90,1.4,3.71207e-08
6.3,91,1.45,4.2e-08
6.3,92,1.5,4.76897e-08
6.3,93,1.55,5.3689699999999997e-08
6.3,94,1.6,6.00345e-08
6.3,95,1.65,6.68276e-08
6.3,96,1.7,7.32759e-08
6.3,97,1.75,8.07931e-08
6.3,98,1.8,8.88621e-08
6.3,99,1.85,9.69655e-08
6.3,100,1.9,1.05552e-07
6.3,101,1.95,1.14621e-07
6.3,102,2.0,1.24345e-07
6.3,103,2.05,1.33966e-07
6.3,104,2.1,1.44448e-07
6.3,105,2.15,1.55241e-07
6.3,106,2.2,1.66759e-07
6.3,107,2.25,1.78345e-07
6.3,108,2.3,1.90552e-07
6.3,109,2.35,2.0331e-07
6.3,110,2.4,2.16483e-07
6.3,111,2.45,2.29103e-07
6.3,112,2.5,2.42793e-07
6.3,113,2.55,2.57414e-07
6.3,114,2.6,2.72621e-07
6.3,115,2.65,2.87586e-07
6.3,116,2.7,3.03552e-07
6.3,117,2.75,3.1969e-07
6.3,118,2.8,3.36517e-07
6.3,119,2.85,3.53414e-07
6.3,120,2.9,3.70828e-07
6.3,121,2.95,3.86621e-07
6.3,122,3.0,4.03448e-07
13.2,2,-3.0,6.77931e-12
13.2,3,-2.95,6.4931e-12
13.2,4,-2.9,6.8e-12
13.2,5,-2.85,6.53448e-12
13.2,6,-2.8,6.57586e-12
13.2,7,-2.75,6.8e-12
13.2,8,-2.7,6.49655e-12
13.2,9,-2.65,6.82759e-12
13.2,10,-2.6,6.55172e-12
13.2,11,-2.55,6.53793e-12
13.2,12,-2.5,6.84138e-12
13.2,13,-2.45,6.55862e-12
13.2,14,-2.4,6.52069e-12
13.2,15,-2.35,6.7931e-12
13.2,16,-2.3,6.52759e-12
13.2,17,-2.25,6.51724e-12
13.2,18,-2.2,6.8e-12
13.2,19,-2.15,6.75517e-12
13.2,20,-2.1,6.46207e-12
13.2,21,-2.05,6.78276e-12
13.2,22,-2.0,6.51379e-12
13.2,23,-1.95,6.50345e-12
13.2,24,-1.9,6.77241e-12
13.2,25,-1.85,6.50345e-12
13.2,26,-1.8,6.5e-12
13.2,27,-1.75,6.80345e-12
13.2,28,-1.7,6.71379e-12
13.2,29,-1.65,6.44138e-12
13.2,30,-1.6,6.75172e-12
13.2,31,-1.55,6.74138e-12
13.2,32,-1.5,6.46207e-12
13.2,33,-1.45,6.76207e-12
13.2,34,-1.4,6.73103e-12
13.2,35,-1.35,6.45862e-12
13.2,36,-1.3,6.74138e-12
13.2,37,-1.25,6.72759e-12
13.2,38,-1.2,6.43103e-12
13.2,39,-1.15,6.50345e-12
13.2,40,-1.1,6.74828e-12
13.2,41,-1.05,6.46897e-12
13.2,42,-1.0,6.68966e-12
13.2,43,-0.95,6.59655e-12
13.2,44,-0.9,6.45172e-12
13.2,45,-0.85,6.75862e-12
13.2,46,-0.8,6.49655e-12
13.2,47,-0.75,6.43448e-12
13.2,48,-0.7,6.76207e-12
13.2,49,-0.65,6.71379e-12
13.2,50,-0.6,6.48276e-12
13.2,51,-0.55,6.76552e-12
13.2,52,-0.5,6.42069e-12
13.2,53,-0.45,6.65517e-12
13.2,54,-0.4,6.76552e-12
13.2,55,-0.35,6.46897e-12
13.2,56,-0.3,6.8931e-12
13.2,57,-0.25,6.94828e-12
13.2,58,-0.2,8.04483e-12
13.2,59,-0.15,1.24759e-11
13.2,60,-0.1,2.58828e-11
13.2,61,-0.05,7.87931e-11
13.2,62,0.0,2.34172e-10
13.2,63,0.05,5.84828e-10
13.2,64,0.1,1.33414e-09
13.2,65,0.15,2.66586e-09
13.2,66,0.2,4.55172e-09
13.2,67,0.25,7.58966e-09
13.2,68,0.3,1.18448e-08
13.2,69,0.35,1.76793e-08
13.2,70,0.4,2.51138e-08
13.2,71,0.45,3.49e-08
13.2,72,0.5,4.62069e-08
13.2,73,0.55,6.05172e-08
13.2,74,0.6,7.7931e-08
13.2,75,0.65,9.83103e-08
13.2,76,0.7,1.22e-07
13.2,77,0.75,1.49172e-07
13.2,78,0.8,1.79517e-07
13.2,79,0.85,2.13241e-07
13.2,80,0.9,2.47276e-07
13.2,81,0.95,2.87828e-07
13.2,82,1.0,3.3131e-07
13.2,83,1.05,3.77724e-07
13.2,84,1.1,4.23103e-07
13.2,85,1.15,4.73793e-07
13.2,86,1.2,5.27931e-07
13.2,87,1.25,5.84138e-07
13.2,88,1.3,6.42414e-07
13.2,89,1.35,7.01379e-07
13.2,90,1.4,7.63448e-07
13.2,91,1.45,8.25172e-07
13.2,92,1.5,8.88966e-07
13.2,93,1.55,9.53448e-07
13.2,94,1.6,1.01931e-06
13.2,95,1.65,1.08621e-06
13.2,96,1.7,1.14759e-06
13.2,97,1.75,1.2169e-06
13.2,98,1.8,1.28621e-06
13.2,99,1.85,1.35517e-06
13.2,100,1.9,1.42621e-06
13.2,101,1.95,1.49724e-06
13.2,102,2.0,1.5669e-06
13.2,103,2.05,1.63828e-06
13.2,104,2.1,1.70897e-06
13.2,105,2.15,1.7869e-06
13.2,106,2.2,1.85621e-06
13.2,107,2.25,1.93138e-06
13.2,108,2.3,2.00483e-06
13.2,109,2.35,2.08034e-06
13.2,110,2.4,2.15345e-06
13.2,111,2.45,2.22793e-06
13.2,112,2.5,2.3031e-06
13.2,113,2.55,2.37724e-06
13.2,114,2.6,2.45034e-06
13.2,115,2.65,2.53207e-06
13.2,116,2.7,2.60483e-06
13.2,117,2.75,2.68069e-06
13.2,118,2.8,2.76103e-06
13.2,119,2.85,2.83793e-06
13.2,120,2.9,2.91655e-06
13.2,121,2.95,2.99379e-06
13.2,122,3.0,3.07069e-06
31.8,2,-3.0,2.99793e-07
31.8,3,-2.95,2.98103e-07
31.8,4,-2.9,2.97103e-07
31.8,5,-2.85,2.95793e-07
31.8,6,-2.8,2.94828e-07
31.8,7,-2.75,2.93483e-07
31.8,8,-2.7,2.92138e-07
31.8,9,-2.65,2.90655e-07
31.8,10,-2.6,2.89379e-07
31.8,11,-2.55,2.88069e-07
31.8,12,-2.5,2.86517e-07
31.8,13,-2.45,2.85172e-07
31.8,14,-2.4,2.83828e-07
31.8,15,-2.35,2.82379e-07
31.8,16,-2.3,2.81138e-07
31.8,17,-2.25,2.7969e-07
31.8,18,-2.2,2.78414e-07
31.8,19,-2.15,2.77e-07
31.8,20,-2.1,2.75517e-07
31.8,21,-2.05,2.74034e-07
31.8,22,-2.0,2.72897e-07
31.8,23,-1.95,2.71379e-07
31.8,24,-1.9,2.70276e-07
31.8,25,-1.85,2.69069e-07
31.8,26,-1.8,2.67966e-07
31.8,27,-1.75,2.67069e-07
31.8,28,-1.7,2.66138e-07
31.8,29,-1.65,2.6531e-07
31.8,30,-1.6,2.65241e-07
31.8,31,-1.55,2.64862e-07
31.8,32,-1.5,2.65103e-07
31.8,33,-1.45,2.64966e-07
31.8,34,-1.4,2.66517e-07
31.8,35,-1.35,2.68414e-07
31.8,36,-1.3,2.71345e-07
31.8,37,-1.25,2.74931e-07
31.8,38,-1.2,2.79966e-07
31.8,39,-1.15,2.85483e-07
31.8,40,-1.1,2.93655e-07
31.8,41,-1.05,3.03759e-07
31.8,42,-1.0,3.16069e-07
31.8,43,-0.95,3.25655e-07
31.8,44,-0.9,3.42241e-07
31.8,45,-0.85,3.65621e-07
31.8,46,-0.8,3.93517e-07
31.8,47,-0.75,4.15862e-07
31.8,48,-0.7,4.54828e-07
31.8,49,-0.65,4.98621e-07
31.8,50,-0.6,5.47931e-07
31.8,51,-0.55,5.93103e-07
31.8,52,-0.5,6.5069e-07
31.8,53,-0.45,7.16897e-07
31.8,54,-0.4,7.87931e-07
31.8,55,-0.35,8.61724e-07
31.8,56,-0.3,9.38276e-07
31.8,57,-0.25,1.01586e-06
31.8,58,-0.2,1.09207e-06
31.8,59,-0.15,1.16724e-06
31.8,60,-0.1,1.24034e-06
31.8,61,-0.05,1.30966e-06
31.8,62,0.0,1.37172e-06
31.8,63,0.05,1.42517e-06
31.8,64,0.1,1.47138e-06
31.8,65,0.15,1.50655e-06
31.8,66,0.2,1.52655e-06
31.8,67,0.25,1.54103e-06
31.8,68,0.3,1.55172e-06
31.8,69,0.35,1.55655e-06
31.8,70,0.4,1.57552e-06
31.8,71,0.45,1.60138e-06
31.8,72,0.5,1.63862e-06
31.8,73,0.55,1.68103e-06
31.8,74,0.6,1.73586e-06
31.8,75,0.65,1.79759e-06
31.8,76,0.7,1.86517e-06
31.8,77,0.75,1.93621e-06
31.8,78,0.8,2.00966e-06
31.8,79,0.85,2.08414e-06
31.8,80,0.9,2.15862e-06
31.8,81,0.95,2.23207e-06
31.8,82,1.0,2.30414e-06
31.8,83,1.05,2.37448e-06
31.8,84,1.1,2.4431e-06
31.8,85,1.15,2.50862e-06
31.8,86,1.2,2.57828e-06
31.8,87,1.25,2.63828e-06
31.8,88,1.3,2.69586e-06
31.8,89,1.35,2.75138e-06
31.8,90,1.4,2.80414e-06
31.8,91,1.45,2.85414e-06
31.8,92,1.5,2.90207e-06
31.8,93,1.55,2.94793e-06
31.8,94,1.6,2.99138e-06
31.8,95,1.65,3.0331e-06
31.8,96,1.7,3.0731e-06
31.8,97,1.75,3.11793e-06
31.8,98,1.8,3.15586e-06
31.8,99,1.85,3.18931e-06
31.8,100,1.9,3.22172e-06
31.8,101,1.95,3.25172e-06
31.8,102,2.0,3.28069e-06
31.8,103,2.05,3.30793e-06
31.8,104,2.1,3.33414e-06
31.8,105,2.15,3.35828e-06
31.8,106,2.2,3.38172e-06
31.8,107,2.25,3.40414e-06
31.8,108,2.3,3.42448e-06
31.8,109,2.35,3.44414e-06
31.8,110,2.4,3.46138e-06
31.8,111,2.45,3.47793e-06
31.8,112,2.5,3.49448e-06
31.8,113,2.55,3.50862e-06
31.8,114,2.6,3.52207e-06
31.8,115,2.65,3.53483e-06
31.8,116,2.7,3.54621e-06
31.8,117,2.75,3.55586e-06
31.8,118,2.8,3.56517e-06
31.8,119,2.85,3.57379e-06
31.8,120,2.9,3.58069e-06
31.8,121,2.95,3.58517e-06
31.8,122,3.0,3.59034e-06
2.0,2,-3.0,1.86897e-16
2.0,3,-2.95,1.07931e-16
2.0,4,-2.9,4.11724e-16
2.0,5,-2.85,4.40345e-16
2.0,6,-2.8,1.00897e-15
2.0,7,-2.75,1.62931e-15
2.0,8,-2.7,1.66621e-15
2.0,9,-2.65,1.94379e-15
2.0,10,-2.6,2.04069e-15
2.0,11,-2.55,2.15172e-15
2.0,12,-2.5,2.39276e-15
2.0,13,-2.45,2.56276e-15
2.0,14,-2.4,2.59828e-15
2.0,15,-2.35,2.87724e-15
2.0,16,-2.3,3.19138e-15
2.0,17,-2.25,3.15552e-15
2.0,18,-2.2,3.41034e-15
2.0,19,-2.15,3.36448e-15
2.0,20,-2.1,3.36552e-15
2.0,21,-2.05,3.54207e-15
2.0,22,-2.0,3.63517e-15
2.0,23,-1.95,3.80379e-15
2.0,24,-1.9,3.74103e-15
2.0,25,-1.85,3.76655e-15
2.0,26,-1.8,3.91483e-15
2.0,27,-1.75,4.13931e-15
2.0,28,-1.7,4.06276e-15
2.0,29,-1.65,4.26966e-15
2.0,30,-1.6,4.22793e-15
2.0,31,-1.55,4.33483e-15
2.0,32,-1.5,4.33207e-15
2.0,33,-1.45,4.18345e-15
2.0,34,-1.4,4.13483e-15
2.0,35,-1.35,4.73793e-15
2.0,36,-1.3,4.74931e-15
2.0,37,-1.25,4.75655e-15
2.0,38,-1.2,4.65069e-15
2.0,39,-1.15,4.38448e-15
2.0,40,-1.1,4.72207e-15
2.0,41,-1.05,4.71103e-15
2.0,42,-1.0,4.60552e-15
2.0,43,-0.95,4.95862e-15
2.0,44,-0.9,4.77966e-15
2.0,45,-0.85,2.41379e-15
2.0,46,-0.8,5.51414e-15
2.0,47,-0.75,5.08517e-15
2.0,48,-0.7,5.06931e-15
2.0,49,-0.65,5.15483e-15
2.0,50,-0.6,5.18e-15
2.0,51,-0.55,4.75e-15
2.0,52,-0.5,5.02793e-15
2.0,53,-0.45,5.09172e-15
2.0,54,-0.4,5.11276e-15
2.0,55,-0.35,5.17e-15
2.0,56,-0.3,5.16379e-15
2.0,57,-0.25,5.17621e-15
2.0,58,-0.2,5.28552e-15
2.0,59,-0.15,5.18069e-15
2.0,60,-0.1,5.42793e-15
2.0,61,-0.05,5.23e-15
2.0,62,0.0,5.36552e-15
2.0,63,0.05,5.27759e-15
2.0,64,0.1,4.54483e-15
2.0,65,0.15,1.92169e-14
2.0,66,0.2,1.36897e-13
2.0,67,0.25,7.18586e-13
2.0,68,0.3,3.10103e-12
2.0,69,0.35,1.11255e-11
2.0,70,0.4,3.19559e-11
2.0,71,0.45,7.71552e-11
2.0,72,0.5,1.65197e-10
2.0,73,0.55,3.15345e-10
2.0,74,0.6,5.53034e-10
2.0,75,0.65,9.01207e-10
2.0,76,0.7,1.39931e-09
2.0,77,0.75,2.08328e-09
2.0,78,0.8,3.00317e-09
2.0,79,0.85,4.14655e-09
2.0,80,0.9,5.59276e-09
2.0,81,0.95,7.43448e-09
2.0,82,1.0,9.67207e-09
2.0,83,1.05,1.23459e-08
2.0,84,1.1,1.5501e-08
2.0,85,1.15,1.89248e-08
2.0,86,1.2,2.31034e-08
2.0,87,1.25,2.78614e-08
2.0,88,1.3,3.30679e-08
2.0,89,1.35,3.89934e-08
2.0,90,1.4,4.51207e-08
2.0,91,1.45,5.23069e-08
2.0,92,1.5,6.00793e-08
2.0,93,1.55,6.85103e-08
2.0,94,1.6,7.75138e-08
2.0,95,1.65,8.71862e-08
2.0,96,1.7,9.74069e-08
2.0,97,1.75,1.08228e-07
2.0,98,1.8,1.1961e-07
2.0,99,1.85,1.30845e-07
2.0,100,1.9,1.43272e-07
2.0,101,1.95,1.563e-07
2.0,102,2.0,1.69772e-07
2.0,103,2.05,1.83776e-07
2.0,104,2.1,1.982e-07
2.0,105,2.15,2.13045e-07
2.0,106,2.2,2.28297e-07
2.0,107,2.25,2.43897e-07
2.0,108,2.3,2.59966e-07
2.0,109,2.35,2.76097e-07
2.0,110,2.4,2.91893e-07
2.0,111,2.45,3.09021e-07
2.0,112,2.5,3.26279e-07
2.0,113,2.55,3.43986e-07
2.0,114,2.6,3.61334e-07
2.0,115,2.65,3.79462e-07
2.0,116,2.7,3.96379e-07
2.0,117,2.75,4.14379e-07
2.0,118,2.8,4.3331e-07
2.0,119,2.85,4.51931e-07
2.0,120,2.9,4.71241e-07
2.0,121,2.95,4.89931e-07
2.0,122,3.0,5.08966e-07
