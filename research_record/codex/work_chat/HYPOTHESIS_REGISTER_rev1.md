# Hypothesis register, REVISION 1 (superseded by HYPOTHESIS_REGISTER.md rev 2; kept unchanged for the record)

**Status: draft, merged 2026-10-10. Not frozen.**
- **Next:** Codex reviews the merge, then the user approves the freeze. After that, a git tag records the frozen state.

**Sources.** This register merges two drafts made independently:
- **Codex:** work chat, "Co-design" entry, items H01 to H10.
- **Claude agent:** blind draft, items H1 to H8. It did not read the work chat.

Claude merged them. Where the two drafts disagree, both positions are kept in the table in section 3.

## 0. Rules and disclosures
- **Registered prediction:** a test with a pass/fail criterion, frozen before the result is seen.
- **Forecast:** a drafter's best guess. It is recorded but it is not the test.
- **Thresholds:** every numeric threshold below is an ASSUMED decision threshold. None is a literature confidence interval.
- **What was seen before this register was written:**
  - S0-01 and S0-02 (run_0061, run_0067).
  - S1-01 and S1-02, seen by the Claude drafter.
  - S1-03, seen by the merger. Results:

    | Run | Film | Objective (dec) | I_D at 3 V |
    |---|---|---|---|
    | S1-01 | 6.3 nm | 1.18 | ×4.87 |
    | S1-02 | 13.2 nm | 0.056 | — |
    | S1-03 | 13.2 nm, mesh ×0.7 | 0.0555 | — |

  Predictions are blind only to S1-04 onward, all of S2 to S7, and all amorphous DFT.
- **Against the measured device data:** every comparison is retrospective. One device per thickness.
- **Protocol deviation, disclosed:**
  - S0-02 needed 6 launches (run_0062 to run_0067), against the cap of 3 repairs in CAMPAIGN_DESIGN.md:294.
  - The launch counter stands at 70 of 260; 190 C10 launches remain.
- **Resolution limit of the DFT:** one state per DFT cell is about 6e13 cm^-2.
  - The fitted Q_f is about 0.023 e per cell; the fitted tail N_s is about 0.07 states per cell.
  - So DFT cannot test those fitted values. It can test band edges, W levels and trap states that are much denser than they are.
- **Floor reference:** the measured 2.0 nm off-current floor is 4.6e-15 A/um.

## 1. Hypotheses

| ID | Hypothesis | Codex | Claude | Priority |
|---|---|---|---|---|
| H-A | The 2.0 nm floor is extrinsic or instrument-limited | H01 | part of H2 | 1 |
| H-B | One shared ungated strip explains how the floor scales with thickness | H02 | H2 | 1 |
| H-C | Gate leakage and channel generation do not set the floor | H03 | H1 | 1 |
| H-D | Mass alone is not enough; mass plus a shared 1/t scattering term explains mobility | H04 | H3 | 1 |
| H-E | Confinement explains part of V_th(t); the rest cannot be told apart from Q_f or donors | H05 | H4 | 1 |
| H-F | The 6.3 nm discrepancy is device-specific shape physics | H06 | H5 | 1 |
| H-G | W donates into extended host states; it does not pin E_F | H07 | H6 | 1 |
| H-H | OH termination moves dipoles, not the interior conduction edge | H08 | H7a/b | 1 |
| H-I | Al2O3 changes the alignment but adds no channel-edge traps | H09 | H7c | 2 |
| H-J | One shared model transfers across 2.0, 6.3 and 13.2 nm | H10 | H8 | 1 |
| H-K | Amorphous confinement agrees with the crystalline DFT laws | part of H05 | H7d | 2 |

### H-A: the 2.0 nm floor is extrinsic or instrument-limited
- **Mechanism.** Measurement background dominates the intrinsic channel leakage.
- **Registered prediction.** Every intrinsic mechanism that is converged and independently constrained (H-C) stays at least 1 decade below 4.6e-15 A/um at 2.0 nm.
- **Falsified if** an independently constrained mechanism reproduces the floor's magnitude, flatness and thickness dependence.
- **Unresolved if** the instrument records stay unavailable.
- **Open anomaly** (Claude): at 2.0 nm, I_D falls ×19 between −2 and −3 V (3.6e-15 to 1.9e-16 A/um). Neither a strip nor a constant offset reproduces this. It is reported, not explained.
- **Cost:** 0 launches. Decided by H-C plus the instrument records (RQ-010).

### H-B: one ungated strip explains the floor scaling
- **Tests.** S2-14 to S2-17 (each with and without Q_f), a new **STRIP-6p3** run (Codex), then frozen S6-24 to S6-26.
- **Registered prediction, part 1.** The strip current ratio I(0.7 V)/I(0.1 V) = 7.0 ± 0.5.
  - Claude forecast: ±0.2.
  - The ±0.5 band allows for numerics.
- **Registered prediction, part 2.** One (W/L)_par puts the 6.3 and 13.2 nm floors within 0.5 dec. The geometry is chosen on one film only and is never selected using the held-out film.
- **Claude forecast with Q_f.** The strip conductance ratio G(13.2)/G(2.0) is at most 10^2, while the measured ratio is 10^3.16. A strip fitted at 13.2 nm therefore over-predicts the 2.0 nm floor by at least 10×.
- **Interpretation rule, frozen now.** If the strip fails with Q_f and passes without it, then ΔV0 must be a gate work function, not an interface charge.
- **Truly decisive test:** a measurement. Varying V_D from 0.1 to 0.7 V should raise the floor ×7 for a strip but only ×1.02 for diffusion. Strip decks add V_D steps at no extra launch (REG-001).
- **Cost:** 5 + 1 + 3 launches.

### H-C: gate leakage and generation do not set the floor
- **Tests.**

  | Run | Tests |
  |---|---|
  | S2-11, run first | Leakage convergence, redefined as oxide y-mesh ×0.5 |
  | S2-04, S2-06 | Nominal oxide |
  | S2-08 | Worst-case oxide |
  | S2-12, S2-13 | Oxide TAT with ^tat.poisson |
  | S2-03 | Extreme generation |

- **Registered predictions.** Each result is set against the floor of the same film:

  | Case | Registered prediction |
  |---|---|
  | Nominal-oxide leakage at −3 V | ≤ 1e-2 × floor |
  | Extreme SRH/TAT generation | ≤ 1e-20 A/um |
  | Worst-case leakage (S2-08) | Fails the registered flatness test (slope > 2× measured + 2σ) or the thickness-scaling test |
  | Converged leakage under refinement (S2-11) | Changes by ≤ 0.1 dec |

- **Forecasts on nominal leakage:** Codex ≤ 1e-24 A/um; Claude ≤ 1e-22 A/um, unresolved below 1e-17 A at ≥ 90 % of the points.
- **Claude forecast on S2-08:** I_G(−3 V) = 2.7e-12 A/um within ×3, independent of thickness, with slope > 0.2 dec/V.
- **Falsified if** a converged tested mechanism passes all the registered floor criteria (CAMPAIGN_DESIGN §7.2).
- **Scope.** This excludes neither pinholes nor arbitrary trap distributions.
- **Cost:** 8 launches.

### H-D: mobility needs a 1/t scattering term, not just the DFT mass
- **Law.** mu(t) = mu_inf · [m_bulk / m(t)] / (1 + ℓ/t). The observable is the fitted band-mobility ratio and the native g_m, not mu_FE.
- **Tests.** S4 profiling, with a **nested ℓ = 0 comparison** (Codex), then native best triples.
- **DFT addition.** Dispersion and localisation on aIO and aIWO at 2.0 nm (s1 and s2) and at 1.0 nm (s1). This needs a dispersion workflow that does not exist yet.
- **Registered predictions.**
  - The mass-only ratio is 0.75 to 0.95; the scattering branch is needed to reach the fitted 0.28.
  - The shared ℓ comes out at 4 to 12 nm.
- **Forecasts.** Claude's numbers sit inside both registered ranges:
  - mass-only ratio 0.835;
  - the mass explains 14 % of the drop in log-mobility, or 18 % with the PBE bulk mass;
  - ℓ = 8 ± 3 nm.
- **Falsified if** the shared branch fails native mobility acceptance or needs film-specific scattering.
- **Caveat** (Claude): the two-film fit has no degrees of freedom left. ℓ is a fit, not a test.

### H-E: threshold shift from confinement versus Q_f and donors
- **Tests.** S3-01 to S3-03 (confinement off), compared with S0-01, S1-01 and S1-02; S6-01 to S6-06 and S6-10 to S6-15; the amorphous thickness series.
- **Registered prediction, ATLAS** (Claude). With confinement off, V_th,cc moves by:

  | 2.0 nm | 6.3 nm | 13.2 nm |
  |---|---|---|
  | −0.23 ± 0.04 V | −0.062 ± 0.015 V | −0.023 ± 0.008 V |

  That is 36 ± 7 % of the measured 0.579 V shift from 2.0 to 13.2 nm.
- **Registered prediction, shared fit.** In the shared fit of the two films, max |ΔV_th,cc| ≤ 0.10 V with confinement and ≥ 0.15 V without it.
- **Registered prediction** (Codex). The crystalline-input uncertainty changes the 6.3 nm threshold by < 0.10 V.
- **Claude forecast.** N_D ×10 shifts V_th,cc by −0.08 to −0.10 V at 2.0 nm and by −0.5 to −0.95 V at 13.2 nm. A donor change of about 1e18 cm^-3 could mimic the whole DFT term (ledger claim C018).
- **Falsified if** the ATLAS predictions miss by more than twice their band, or the shared fit passes without confinement.
- **Scope.** Transfer curves cannot separately identify Q_f, affinity and gate work function.

### H-F: the 6.3 nm anomaly
- **Tests.** S3-10 to S3-13 and S3-27; conditional runs S3-14 to S3-16, plus contacts (Codex keeps contacts as a competing explanation); the S5 fold that leaves out 6.3 nm.
- **Registered prediction** (Claude). Relative to the two-film model, 6.3 nm needs a rigid shift of +0.28 ± 0.08 V and a current scale of 0.15 to 0.35 (V1 needed 0.294 V).
- **Registered prediction** (Codex). The baseline shape RMSE is > 0.15 dec. The density-dependent mobility branch (IGZO.TOKYO) improves 6.3 nm by ≥ 0.05 dec and moves γ toward 0.9 to 1.3.
- **Registered prediction** (Claude). The same branch gives γ ≥ 0.5 at 13.2 nm, where the measured γ is 0.27. So it is **not adopted** under the rule that no film may get worse.
  - The two drafters' predictions are compatible: the branch helps 6.3 nm and breaks 13.2 nm.
- **Falsified if** the baseline passes, or any branch passes CAMPAIGN_DESIGN §5.3 for all three films.
- **Scope.** Success would not establish a thickness anomaly at the population level.

### H-G: W donates into the host conduction band and does not pin E_F
- **Tests.** aIWO_2p0_s1 and s2, aIO_2p0_s1 and s2, and the compensated aIWO_2p0_comp_s1 (In98W2O153, D-15).
- **Registered predictions.**
  - The lowest strongly W-rich state, with ≥ 30 % W-5d weight, lies more than 0.3 eV above the host edge (LUMO or CB edge).
  - In the 1 e/W cells, at least 80 % of the nominal excess charge is in host-like states.
  - The compensated cell has no occupied W-localised gap state.
  - Claude adds:
    - no state with ≥ 20 % W-5d weight between VBM + 0.1 eV and the LUMO;
    - the LUMO has ≤ 10 % W-5d weight;
    - |E_g(comp) − E_g(a-In2O3)| ≤ max(0.15 eV, sample spread).
- **Forecasts** (Claude):
  - the first W-rich state lies ≥ 0.5 eV above the LUMO (crystalline: +1.22 to +1.80 eV);
  - ≤ 15 % of the excess electrons sit on W-5d;
  - E_F is 0.4 to 1.0 eV above the CB edge.
- **Falsified if** there is a reproducible occupied W-associated gap state, or more than 20 % of the excess charge is trapped in localised states. A W trap would then go into the TCAD (N2 below).
- **Caveats.**
  - The calculation is spin-unpolarised PBE without +U, which favours delocalisation. A "shallow" result is weak evidence; a "deep" result is strong (Claude).
  - The 0.01 Ry smearing must be audited before shallow levels are interpreted (Codex).
  - One compensated structure cannot prove full ionisation. Why only about 4e-4 of the W is active stays open.

### H-H: OH termination
- **Tests.** aIWO_2p0_s1 and aIWO_0p7_s1, each against its bare control.
- **Registered predictions.**
  - The interior-aligned host-edge shift is ≤ 0.15 eV at 2.0 nm.
  - No new occupied electron trap appears within 0.3 eV below the host edge.
  - No state with ≥ 30 % surface weight appears within 0.3 eV below the CB edge in the OH slabs.
- **Forecasts.** |ΔEA| ≥ 0.2 eV (Codex). The bare 0.7 nm slab does have a surface state near the edge (Claude, medium prior).
- **Unresolved if** the interior alignment is insufficient.

### H-I: the Al2O3 interface
- **Tests.** aIWO_2p0_Al2O3_s2 and aIWO_1p0_Al2O3_s2, against the vacuum slabs.
- **Registered predictions.**
  - The host-edge shift is ≤ 0.2 eV at 2.0 nm.
  - No interface-localised state lies within 0.3 eV below the edge.
- **Claude forecasts:**
  - shift ≤ 0.10 eV at 2.0 nm and ≤ 0.20 eV at 1.0 nm;
  - no state within 0.5 eV below the edge;
  - PBE conduction-band offset 2.0 to 3.5 eV.
- **Caveat.** The interface slabs use different seeds from the vacuum slabs, which confounds the attribution. The seed spread from the 2.0 nm s1/s2 pair is reported alongside.

### H-J: transfer of one shared model
- **Tests.** S4a and S4c, then S5 (leave one film out), all frozen and native.
- **Registered acceptance criteria.**
  - RMSE ≤ 0.15 dec;
  - threshold within ±0.10 V;
  - I_on within ±30 %;
  - SS and mu_FE within ±20 %, for every film.
  - Any failure falsifies transferability.
- **Forecasts. The two drafters disagree:**
  - **Codex** states H-J as the hypothesis under test and gives no forecast.
  - **Claude** forecasts failure:
    - the best S4a √J is 0.25 to 0.65 dec, so S4b is skipped under the stop rule;
    - S4c fails at 2 or more films;
    - leaving out 6.3 nm, the prediction misses by −0.33 ± 0.10 V and ×3 to 6 in I_on;
    - leaving out 2.0 nm drives ℓ to the 50 nm bound;
    - leaving out 13.2 nm gives I_on ×0.15 to 0.4.
- **Reporting rule, frozen now.** The two-film fit (2.0 and 13.2 nm) is reported first, so the 6.3 nm failure is not spread across all films.

### H-K: amorphous against crystalline confinement
- **Registered prediction** (Claude). E_g(0.7 nm) − E_g(2.0 nm) is 0.6 to 1.3 eV (crystalline: 0.97 eV). The sample spread is 0.03 to 0.20 eV.
- **Registered prediction** (Codex). The aligned host edge rises by 0.2 to 1.0 eV from 2.0 to 1.0 nm.
- **Falsified if** the confinement trend is reproducibly reversed, or E_g lies outside its range.
- **Trigger for N1.** If the amorphous ΔE_c law differs from the crystalline law by more than 0.05 eV, run N1: 3 launches. The prediction is a rigid V_th shift equal to that difference ± 10 mV.

## 2. Experiment plan

**Not in the plan** (both drafters agree unless marked):
- S3-04 and S3-07 duplicate S0-01.
- The old S2-11 is inert; it is replaced by the redefinition above.
- Deferred: BQP and Boltzmann (S3-24 to S3-26), the FNORD duplicates, S2-05 and S2-07 (oxide current does not depend on thickness), and S6-16 to S6-19 and S6-27.
- Claude would drop S2-01 and S2-02, because S2-03 is 217× more sensitive. Codex keeps them. **Merged:** run S2-03 first, then S2-01 and S2-02 only if S2-03 is not decisive.
- Schottky contacts (S3-17 to S3-23): Claude would drop them; Codex keeps them as an alternative for H-F. **Merged:** conditional, run only if H-F is not settled by S3-10 to S3-13.
- S7 (31.8 nm): Claude says it has no prediction; Codex keeps 2 stress runs. **Merged:** keep the 2 runs as stress checks, labelled as having no registered prediction.

**Minimal decisive set: 26 launches.** This is the union of both drafts:
- S1-07;
- S2-11 (redefined), S2-03, S2-04, S2-06, S2-08, S2-12, S2-13;
- S2-14 to S2-17 and STRIP-6p3;
- S3-01 to S3-03, S3-10 to S3-13 and S3-27;
- S6-13 and S6-15.

**Launch order:**
1. Finish S1, including S1-05 to S1-07.
2. S2 in this order: S2-11 (redefined), then the nominal-oxide runs, then S2-03, then S2-08, then TAT, then strips.
3. S3: confinement, then IGZO (S3-12 first), then S3-10, then the tail runs.
4. S4a with 8 candidates, then S4c, released in batches.
5. S5, starting with the fold that leaves out 6.3 nm.
6. Targeted runs from S6.
7. The 2 S7 runs.
8. The conditional runs: N1 (H-K), N2 (a W trap, up to 3 launches, if H-G fails), Schottky (H-F) and the S2-01/S2-02 pair.

The plan comes to about 105 to 136 launches, leaving at least 54 of the 190 uncommitted.

**CERN analysis plan** (access ends 21 Oct):
- **By 12 Oct:** freeze the analysis code. It must first reproduce the crystalline results: 3 % W-5d weight and ΔE_c = 0.281 eV.
- **Additions:** a dispersion (mass) workflow, a real-space localisation measure (IPR), and a smearing audit.
- **Final-SCF priority:**
  1. compensated, IWO and IO at 2.0 nm;
  2. the second 2.0 nm sample (s2);
  3. the bare and OH pairs;
  4. the interfaces;
  5. the remaining thicknesses.
- **Cut-offs:**
  - A relaxation not converged by 17 Oct 12:00 goes to its final SCF anyway if its maximum force is ≤ 0.10 eV/A.
  - The last job submission is 18 Oct.
  - An SCF still missing on 20 Oct is replaced by the eigenvalues from the relaxation, labelled as such.
- **Reserved:** 19 to 21 Oct for analysis and export.

## 3. Disagreements and how the merge resolved them

| Point | Codex | Claude | Merged | Reason |
|---|---|---|---|---|
| Nominal leakage bound | ≤ 1e-24 A/um | ≤ 1e-22 A/um | Registered: ≤ 1e-2 × floor; both values kept as forecasts | The decision only needs leakage to be negligible against the floor |
| Leakage convergence tolerance | 0.1 dec | 0.3 dec | 0.1 dec | Already registered in the matrix |
| Strip ratio band | ±0.5 | ±0.2 | ±0.5 | Allows for numerics |
| W-state gap above the edge | > 0.3 eV | ≥ 0.5 eV | Registered 0.3 eV; 0.5 eV kept as a forecast | The looser bound guards against a false failure |
| Interface edge shift / trap window | 0.2 eV / 0.3 eV | 0.10 eV / 0.5 eV | Registered 0.2 / 0.3 eV; Claude's values kept as forecasts | Same reason |
| H-J outcome | No forecast (the hypothesis itself) | Forecast: fails | Criteria registered; Claude's forecast recorded | A forecast is not a test |
| S2-01 and S2-02 | Keep | Drop | Run only if S2-03 is not decisive | Saves launches |
| Schottky contacts | Keep as an alternative for H-F | Drop | Conditional | Saves launches; still tests the alternative |
| S7 | 2 stress runs | No prediction | 2 runs, explicitly without a prediction | — |
| STRIP-6p3 | New run | — | Added | It tests the held-out-film rule |
| Nested ℓ = 0 test | Add | — | Added, as part of S4 profiling | Isolates the mass-only case |

## 4. Freeze list: commit and tag before S1-05 completes, before any S2 run and before any DFT final SCF

1. Every registered prediction in H-A to H-K, the Q_f interpretation rule (H-B) and the reporting rule (H-J).
2. Analysis definitions:
   - **surface weight:** H atoms, plus O within 1.15 A of an H, plus under-coordinated cations;
   - **W-5d weight:** Löwdin projection;
   - **CB edge:** the lowest state whose IPR is at most 3× the median IPR of the states in the 0.5 eV above it;
   - **interior alignment:** a planar average over the middle third of the slab;
   - **sample spread:** as defined in ML_VALIDATION.md:36;
   - **convergence:** the edge stable within 0.05 eV; leakage within 0.1 dec.
3. Branch-selection rules, scoring windows, stop rules, seed exclusions and amendment history, all as in CAMPAIGN_DESIGN.md and SLAB_PROTOCOL.md.
4. The CERN cut-offs, the N1 and N2 triggers, and the disclosures in section 0.
