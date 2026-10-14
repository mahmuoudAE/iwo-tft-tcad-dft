# DRAFT v2 (not in the register): A27, H-N "extended-carrier efficacy of W against thickness", with its controls

- **v1** was drafted by Claude on 2026-10-11.
- **v2** applies every edit from Codex's review of 2026-10-11, whose verdict was FREEZE-WITH-EDITS (work chat).
- **Open user decisions** are marked [DECISION].
- **Sight history:** no slab FINAL has run, so no slab electronic metric has been seen by anyone. The only electronic outputs seen so far are relax-SCF energies and iteration counts, plus geomsel summaries with KS gaps for aIO_0p8_s1. The first slab FINAL (aIWO_1p0_s1, A26) was released on 2026-10-11. This amendment must be frozen before any of its electronic metrics is read.

## Why
H-G tests W only at 2.0 nm, so the thickness question is not registered. Three confounds would make a thickness trend ambiguous:
- **Topology:** each aIO cell is an independent melt-quench (seed + 10), not the W cell's parent network.
- **Relaxation smearing:** aIO slabs relax with Gaussian 0.005 Ry (A15), aIWO slabs with MV 0.01 Ry.
- **Functional:** PBE's delocalisation error biases the localised-versus-extended question.

W–W image interaction is only partly controlled: W is about 2 % of cations and W images are ≥ 12.5 Å apart.

## H-N [DECISION: EXPLORATORY with frozen read-out rules (recommended), or SCORED with Claude's forecast promoted to a prediction]

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

**Forecast (Claude):** DONOR at bulk, 2.0 and 1.0 nm; PARTIAL at 0.7 nm. It is scored only if [DECISION] = SCORED.

## Controls

| Control | Thick endpoint (2.0 nm) | Thin endpoint (0.7 nm) | 1.0 nm |
|---|---|---|---|
| C3 widths | required | required | reported |
| C4 Gaussian polish | required | required | required (geometry exists now) |
| C6 spin | required | required | reported |
| C1 paired substitution | not run (cost); scope stated | required | [DECISION] |
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

## Budget, cuts and deadline
**Cut first:**
- 1.5 nm;
- any duplicate thin-control bundle;
- C1 at 1.0 nm [DECISION].

**Order:**
1. Existing-series FINALs.
2. C4 polish and C6 spin at the endpoints.
3. C1 at 0.7 nm, once aIO_0p7_s1 has converged.
4. C2 and C5, only if 0.7 nm is ECB or PARTIAL.

**Deadlines:**
- Relaxations stay under the 17 Oct 10:00 UTC cutoff.
- Single-point controls must finish by 20 Oct 12:00 UTC; anything unfinished leaves its claim UNRESOLVED.
- The capacity estimate (about 0.8 of our GPU starts per hour) is an observation, not a guaranteed capacity.

## Not changed
- H-G and its scoring.
- The section-1 definitions.
- A15, A25 and A26.
