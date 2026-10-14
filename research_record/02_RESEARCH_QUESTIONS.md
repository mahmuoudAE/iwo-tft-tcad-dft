# Research questions and hypotheses (2026-10-07)

**How to read this file.**
- **Status against the published paper** (Januar et al. 2026) is one of: `ALREADY SHOWN` · `PARTIALLY SHOWN` · `NEW` · `CONTRADICTED` · `NOT TESTABLE NOW`.
- **Who wrote what.** The assessments are Claude's first pass; Codex/Astra review them in task RQ-004. H1–H5 come from the external review proposal of 2026-10-07; H6–H8 are Claude's.
- **Priors** are subjective: low, medium or high.

## Prerequisites (answer before testing any hypothesis)

- **Q0.1 Definitions.** Do we and the paper define mobility, SS, C_ox and V_D the same way? If not, which values are right for these devices? → RQ-001
- **Q0.2 Device spread.** How large is the spread between devices at one thickness? This needs ≥ 10 devices per thickness. Until then, no single-device feature (the 6.3 nm anomaly, the kink at 6.3–13.2 nm) can be called physics.
- **Q0.3 Thickness and provenance.**
  - What are the true thicknesses (XRR/TEM)?
  - Were the four devices made in one run?
  - What was their sweep history?

---

## H1. A critical thickness t_c separates two transport regimes, and W content shifts it

**Status vs paper: PARTIALLY SHOWN.**
- Already in the paper:
  - Sec. 2.5 speaks of a "crossover from near-band transport in thicker channels to disorder- and interface-limited transport in ultrathin films".
  - Fig. 1a contrasts 2 nm IWO (enhancement mode) with 3 nm In2O3 (depletion-like).
- New would be:
  - t_c actually measured, not asserted;
  - t_c as a function of W content;
  - its microscopic origin;
  - a registered prospective prediction.

**Our evidence [OBSERVED, one device per film]:**
- From 2.0 to 6.3 nm almost nothing changes:
  - V_th,cc moves by −0.018 V;
  - μ_FE peak ×0.9;
  - I_on ×0.79.
- From 6.3 to 13.2 nm everything changes:
  - V_th,cc moves by −0.561 V;
  - μ_FE peak ×4.6;
  - I_on ×7.6.
- At 31.8 nm the device no longer turns off (I_D(−3 V) = 3.0e-7 A/µm).
- The local exponent of the off-state floor rises from 3.1 to 5.1.

**Competing explanations:**
- (a) **Back-surface depletion.**
  - An acceptor-like back-surface charge N_s (adsorbates) depletes a layer of width W_dep = N_s/N_D, so films thinner than W_dep are fully depleted.
  - Then t_c ≈ W_dep. This is a classical mechanism and does not need W physics.
  - It shifts with capping or with the ambient.
- (b) **Donor density that grows with thickness** (sputter growth, O-vacancy gradient). The V1 law N_D,eff ∝ 1 + (t/20)^4 is a fit of exactly this.
- (c) **Structural change.** Crystallinity or grain growth sets in with thickness; the paper's SEM grain size grows with thickness.
- (d) **No real crossover.** A smooth law plus device-to-device spread.
- (e) **The proposed W-dependent localization/defect crossover.**

**Quantitative predictions to register:**
- The kink position for 2 % W.
- The direction in which t_c moves with W.
- Under (a), capping or measuring in vacuum moves t_c by a computable amount.

**Discriminating test:**
- A dense thickness series, 3–15 nm in about 1 nm steps, for W = 0 / 2 / 4 at.%, with ≥ 5 devices each.
- XRR, GIXRD and TEM on the same films.
- Capped vs uncapped; air vs vacuum.
- Compare a piecewise (kink) fit against a smooth one on the device means, using an information criterion.

**Minimum computation:**
- TCAD electrostatics of (a) and (b), giving their predicted t_c (cheap, using the existing V1/V2 machinery).
- DFT is not needed to tell (a)–(d) apart.

**Cost:** one fab run. The same run also serves H3, H5, H6 and H7.

**Prior:**
- high that the thickness dependence is non-uniform;
- medium that a sharp t_c exists;
- mechanism unknown.

---

## H2. W acts by keeping conduction-edge states delocalized, not by reducing the number of defects

**Status vs paper: PARTIALLY SHOWN, qualitatively.** The paper says W "promotes smoother charge delocalization" (Sec. 2.3) and shows interface charge maps (Fig. 3h), all from crystalline DFT.

**New would be:**
- A quantitative inverse participation ratio (IPR) of the conduction-edge states in amorphous IWO vs In2O3:
  - for several W contents;
  - with at least 5 structures each.
- Linked to measured band-like vs hopping transport, through gated-Hall vs field-effect mobility and the temperature dependence.

**Competing explanations:**
- W reduces the number of O vacancies (the paper's view).
- W adds Coulomb scattering.
- W changes m*: in crystals the W 5d level is resonant 1.2–1.8 eV above the CBM.

**Prediction:** if H2 holds,
- the conduction-edge IPR (or the mobility-edge position) changes strongly with W, while the integrated tail-state count changes little;
- the Hall mobility follows the IPR, not the V_O count.

**Tests:**
- amorphous DFT (melt-quench by ab initio MD, or with an ML potential);
- gated Hall bars;
- μ(T).

**Cost:** weeks of CERN compute, plus new test structures. **Prior:** low to medium.

---

## H3. The intermediate-thickness (6.3 nm) anomaly is real, non-monotonic electrostatics

**Status vs paper: NEW** (not discussed there).

**Evidence:**
- V1 needs Q_f = 8.7e10 cm⁻² at 6.3 nm, against 1.73e12 cm⁻² at 2.0 and 13.2 nm.
- Three out-of-sample V_th tests failed: −0.29 / −0.37 / −0.23 V.
- The miss decomposes into a rigid 0.294 V shift plus a 0.16–0.19 V shape part.
- Of the three thin films (2.0–13.2 nm), 6.3 nm has the lowest peak mobility in both analyses, and the strongest V_G dependence (γ = 1.13).

**Competing explanations (a priori more likely):**
- device-to-device spread;
- an error in the thickness;
- a different fab batch;
- sweep history.

**Test:** ≥ 10 devices at 2, 4, 6.3, 9 and 13 nm, all from one run. These come free with H1's run. H3 is falsified if the 6.3 nm devices lie on a smooth trend, within the spread.

**Computation:** none until the statistics exist. **Prior:** low.

---

## H4. The way W suppresses oxygen vacancies depends on thickness

**Status vs paper: NEW.** The paper states, citing the literature, that W raises the V_O formation energy. It says nothing about thickness.

**Prediction:** ΔE_f(V_O, near W − far from W) changes with film thickness and with depth (surface vs interior).

**Tests:**
- DFT on 1, 2 and 4 nm slabs, with V_O at several depths, with and without W nearby; then a check in amorphous bulk.
- Experiment: XPS of the O 1s vacancy component against thickness and W content.

**Cost:** moderate compute. Charged defects in slabs need care (corrections, slab size).

**Prior:** medium that some dependence exists; its relevance to the device is unknown.

---

## H5. At 1–2 nm the contacts become part of the channel

**Status vs paper: NEW** (the paper does not analyse contacts).

**Our evidence: PARTIALLY CONTRADICTED** for a thickness-independent contact resistance:
- θ_net < 0 in all films.
- An R_sd large enough to create the trend would take 83 % of V_D at 2 nm (SYNTHESIS, S5).
- A thickness-dependent barrier is not excluded: confinement raises the Pd/IWO barrier at 2 nm (S5 M2).

**Tests:** TLM at each thickness (in H1's run), and a DFT Pd/IWO interface (metal-induced gap states).

**Prior:** low to medium.

---

## H6. The off-state floor is an ohmic parallel path (ungated strip), not diffusion

**Status vs paper: would CONTRADICT the paper's Eq. 1f.**

**Predictions:**

| Mechanism | Floor vs V_D | With mesa isolation | Floor from 0.1 to 0.7 V |
|---|---|---|---|
| Strip | ∝ V_D | gone | ×7 |
| Eq. 1f | saturates above ~0.1 V | survives | ×1.02 |

**Tests:**
- Floor against V_D on the existing chips (days).
- Mesa devices in the next run.
- Register both predictions before the measurement.

**Prior:** medium to high for an ohmic parallel path.

---

## H7. Subthreshold behaviour is universal against I_D/I_on

**Status vs paper: NEW.**

**Evidence:** collapse in 3 devices, both measured and TCAD.

**Possible reason:** the areal tail-state density near E_c depends only weakly on thickness (surface-dominated tails).

**Test:** many devices; In2O3 against IWO; literature data. H7 is falsified if the collapse fails within one composition.

**Prior:** medium.

---

## H8 (model side). Too many near-edge tail states at 13.2 nm (and near threshold at 2.0 nm)

**Evidence:**
- At 13.2 nm the simulated SS is 16–25 mV/dec too high.
- At 2.0 nm it is 7–20 mV/dec too high above about 3e-11 A/µm.

**Test:** V3 with an energy-dependent tail constrained by temperature-dependent data and DFT.

---

## Claude's first ranking (to be reviewed)

1. **Q0.1 and H6.** Days of work and decisive; they come before everything else.
2. **H1, through one dense thickness × W fab run.** It gives the most information per fab run, because it tests H1, H3, H5, H6 and H7 at once.
3. **H4.** Bounded DFT and genuinely new.
4. **H2.** Expensive, and it needs new test structures. Worth it only if H1's run shows a W-dependent effect.
5. **H3 and H5** come free with H1's run; no dedicated effort until then.
