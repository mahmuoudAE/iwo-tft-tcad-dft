# DFT campaign plan for the ultrathin IWO study (v1, 2026-10-03)

**Basis.**
- The user's proposal (three blocks: a 22-item table, a Pd/V_O mini-campaign and a thickness matrix).
- Four independent read-only reviews (evidence, feasibility, physics, TCAD), saved in `REVIEWS.md` and `review_*.json`.
- Everything learned in the project so far.

**Cost figures.** All costs are **estimates**, scaled from measured runs:
- 2 nm vc-relax: 33.7 min per BFGS step on one H100 NVL.
- 2 nm slab memory: 31 GB host for the vc-relax, 66 GB host for the final SCF, 86 GB GPU at 672 bands.
- 1 nm HSE06: 1,054 s of SCF plus 11,724 s of stress.

**Criteria.** Before any item runs, its acceptance and decision criteria are written into `PROTOCOL_CERN.md`.

## 1. Principles

1. **Every calculation answers a named question**, and its pre-registered result has a defined consequence.
2. **Ultrathin first.**
   - The 1–2 nm films carry the device physics; 2 nm is the device.
   - A 3 nm slab is the only bridge point.
   - 6.3 and 13.2 nm are handled by a quantum-well (Kane effective-mass) model calibrated on the 1/2/3 nm DFT points, not by slabs.
3. **Slabs give local and relative quantities**: band edges, level positions, segregation energies, binding energies.
   - One defect per 10.34 Å cell is about 1e14 cm⁻² (about 5e20 cm⁻³ at 2 nm), so a slab's E_F is not the device E_F.
   - No defect density from DFT is entered into TCAD as N_D or g_t(E).
4. **HSE06 only where it fits one GPU and is decisive**: bulk, the 1 nm film, and bulk W or V_O cells. The 2 nm film uses the measured 1 nm HSE/PBE ratio (1.06–1.11), as the protocol allows.
5. **Computed, not validated.** Validation needs the experimental falsifiers in section 6.

## 2. Corrections to the proposal

| Proposal statement | Verdict | Basis |
|---|---|---|
| TCAD uses ideal Ohmic Pd contacts | Confirmed | config and decks; evidence review |
| A confinement-raised Pd/IWO barrier at 2 nm is plausible and unverified | Confirmed | evidence review |
| Changing the contact potential brought the simulated off-current toward measurement | **Refuted** | No V1 run changes the S/D contact potential; the simulated off-state is a numerical zero (≤6.3e-18 A/µm); the older Astra Schottky runs gave 1e-34 to 1e-53 A/µm. |
| "DFT Φ_Bn → freeze in TCAD → predict I_off → compare" | **Cannot work in V1** | Ideal Ohmic is already the injection upper bound, so any barrier only lowers the current. The 20 µm off-state is set by the gated channel. The measured floors are gate-independent and scale as about t^3.8. |
| V_O near Pd explains the off-state floors | Not supported | gate-independent floors; ×33/×43 floor ratios incompatible with exp(−ΔΦ/kT) from confinement |
| Off-floors rise strongly with thickness; origin undetermined | Confirmed, with caveat | Gate leakage is rejected only at 6.3/13.2 nm. |
| μFE about 11 → 50 cm²/Vs between 6.3 and 13.2 nm | Confirmed | 12.15 / 10.95 / 50.17 cm²/Vs |
| Structural transition between 6.3 and 13.2 nm is the working hypothesis | Confirmed: plausible, unverified | evidence review |
| 6.3 nm about 500 atoms, 13 nm more than 1000 atoms | Confirmed (496 and 1056, computed) | about 379 GB and about 1.4 TB of memory: not feasible |
| Inventory: 11 built, 2 pending | Confirmed | |

Separately, `11_validation.tex:77` has stale text (a 52-launch budget, and TMUN/overlap "not done"). Runs 0054/0055 did both, and solver.yaml allows 57. This will be fixed in the report.

## 3. Phases and gates

### Phase 0 – workflow hardening (no GPU time; now)

| ID | Action | Status |
|---|---|---|
| P0.1 | Explicit nbnd for doped-slab relaxations (occupied + 12); the default of about 798 bands exceeds 94 GB at 2 nm | done |
| P0.2 | tstress off for hybrid runs (stress took 81 % of the 1 nm HSE06 run) | done |
| P0.3 | Memory requests from measured demand; no auto-release of memory-held jobs after more than 1 h | done |
| P0.4 | Laptop-side snapshot loop every 15 min; jobs' tickets expire after about 25 h and in-job EOS checkpoints then fail | done (running) |
| P0.5 | Segment long relaxations into pw.x runs of ≤20 h, with automatic continuation from the last geometry, so every segment returns its outputs while the job's ticket is valid | to do |
| P0.6 | Multi-GPU mode in driver.sh: `-nk 1` instead of `-nk $NGPU`, so two GPUs share the memory. Test once on the 2 nm slab. | to do |
| P0.7 | Dipole correction (`tefield/dipfield`) and `nspin = 2` options in make_jobs.py and dat2h5.py, with a GPU-build test on a 1 nm asymmetric slab | to do |
| P0.8 | PDOS of GPU runs needs a CPU SCF (projwfc cannot read the GPU wavefunctions). Plan these as separate 16–32-core CPU jobs, not FORCE_CPU on a GPU node, where the GPU would sit idle. | to do |
| P0.9 | Monitoring that does not depend on the laptop: investigate running `dft_flow.sh auto` on lxplus via CERN's authenticated cron | to investigate |
| P0.10 | **Approvals (user):** download Pd and Al PAW data sets (10-electron Pd preferred); Pd/Al SG15 only if a hybrid is needed | waiting for approval |

### Phase 1 – pristine ultrathin films and the ΔEc/ΔEv split (≈25–40 GPU-h)

| ID | Calculation | Question / output | Pre-registered criterion | TCAD use |
|---|---|---|---|---|
| 1.1 | Relaxed 2 nm slab (running; final SCF, pp.x via dat2h5 and bands in the same job) | ΔEg(2 nm), m*, EA, IP | Lin et al.: +0.33 eV at 1.98 nm. Recipe reproduced if within 0.1 eV. | dEc(t) refit |
| 1.2 | Thickness definition, fixed before the refit (H–H, O–O or cation span) | removes about ±0.05 eV of ambiguity at 2 nm | written before 1.1 is read | t in the law |
| 1.3 | ΔEc/ΔEv split. Between films: EA/IP differences of the relaxed 1 and 2 nm slabs (same termination). Relative to bulk: two-step alignment, i.e. bulk band edges against the macroscopic-average potential (40-atom bulk pp.x at the slab in-plane lattice), aligned to the slab-interior average. | ΔEc, ΔEv at 1 and 2 nm | ΔEc + ΔEv = ΔEg within 20 meV (internal check) | χ(t); tests the model's assumption ΔEg = ΔEc |
| 1.4 | Hybrid edge corrections from existing outputs: bulk VBM −1.015 / CBM +0.173 eV (HSE − PBE, computed, unconfirmed). Confirm with planar averages of the existing HSE runs. | HSE-corrected ΔEc | ΔEc ratio (HSE/PBE) within the 1.06–1.11 band | uncertainty of χ(t) |
| 1.5 | Sub-band ladder of the 2 nm slab, giving the subthreshold-equivalent shift (Nc kept at the bulk mass) | dEc as TCAD sees it | — | dEc(2 nm) input |
| 1.6 | ~3 nm slab: 256 atoms, 1×1×3 cells, Lin recipe, rebuilt (the legacy slab_3p0nm input fails electron closure). Needs 2 GPUs with `-nk 1`, or 15 Å vacuum (allowed: vacuum test changed EA/IP by ≤0.1 meV). About 40–120 GPU-h. | third point of the law, where V1 crosses the effective-mass bound (2.98 nm) | law and Kane model within 0.03 eV at 3 nm | t^-n vs t^-2 form |
| 1.7 | Kane effective-mass quantum-well model calibrated on 1/2/3 nm | ΔEc(6.3) and ΔEc(13.2) with uncertainty (expected ≤0.05 and about 0.01 eV) | — | replaces 6.3/13.2 slabs |

**Gate G1.** Phase 1 passes when 1.1 meets its criterion and 1.3 closes. Otherwise stop and diagnose before Phase 2.

### Phase 2 – W and V_O chemistry (≈100–200 GPU-h)

| ID | Calculation | Question | Criterion / note |
|---|---|---|---|
| 2.0 | **Resolved 2026-10-05 (read-out error).** The 1.1–1.65 eV shift was a band-count artefact: the IWO slab has one occupied band fewer below the gap (In 4d10 = 5 bands replaced by W 5s2 5p6 = 4 bands), so band 312 is the host CB bottom, not the VB top (projwfc). Corrected: EA 4.07, IP 5.79 eV (pure 3.93 / 5.72); W 5d level 1.22 eV above the CB bottom, E_F pinned there. | — | Doped-slab read-outs must use nvb = n_pure − (number of W). |
| 2.1 | W localization in bulk: 160-atom cell (1.6 % W) vs 80 (3.1 %); spin-polarized at 4×4×4; HSE06 (NC, no stress) on the 80-atom W24d cell, about 1–4 GPU-h | Is "W-5d states at E_F" real or a PBE/k-sampling artefact? | Pre-registered: the claim stands only if the W-5d share at E_F stays above 0.3 at both concentrations and with HSE. |
| 2.2 | 2 nm IWO, W at the centre (chained; nbnd fixed; final SCF and PDOS as a CPU job) | donor depth at 1 vs 2 nm; m* | only local quantities are read |
| 2.3 | W depth scan, same site type (24d) at centre, subsurface and surface: 1 nm pilot first, then one 2 nm configuration; dipole correction | segregation E_seg = E(W at depth) − E(W at centre), same cell and occupations | sign and size > 0.1 eV are decisive |
| 2.4 | Bulk V_O^q (q = 0, +1, +2): 80-atom PBE relax, HSE (NC) single points, FNV or Kumagai–Oba correction with the report's permittivities, over the full In-rich to O-rich range | transition levels | No concentration or N_D is derived. |
| 2.5 | W–V_O binding: bulk 160-atom first, then one adjacent 2 nm configuration. E_bind = E(W) + E(V_O) − E(W+V_O) − E(pristine), all four in identical cells, k and occupations. | Tests the trap passivation by W reported by Januar et al. (pp. 5, 8, DFT interface energetics). | "Separated" in a 10.3 Å cell is not a dilute reference; it is reported as such. |
| 2.6 | Neutral V_O at three depths in the 1 nm pilot, then 1–2 configurations at 2 nm | surface preference of V_O | relative energies only |

**Gate G2.** Phase 2 passes when 2.1 decides whether "W electrons are retained in W-5d states" may be stated in the paper. After the 2026-10-05 correction, PBE says no at device-like filling: the W level is resonant 1.2–1.8 eV above the CB bottom, and it is just empty in the 2 nm film with 1.8 % W. Only HSE or DFT+U could still lower it.

### Phase 3 – interfaces (≈60–150 GPU-h; needs P0.6, P0.7 and P0.10)

| ID | Calculation | Question | Trigger / criterion |
|---|---|---|---|
| 3.1 | Air-side surface: 1 nm slab with OH/H2O adsorbates on one side instead of H termination (dipole correction) | How much do the back-surface adsorbates move EA and the band edges? | cheap; always run |
| 3.2 | Pd stage A: Pd work function (slab) and bulk branch-point (CNL) estimate with HSE-corrected edges | predicted Φ_Bn window | Stage B runs only if Φ_Bn(A) ≥ 0.18 eV (see 4.3). |
| 3.3 | Pd stage B: Pd(001) √13×√13 R33.7° (13 Pd per layer, strain +2.3 to +4.2 %), 4–6 layers, on the 1 nm IWO pilot (~136 atoms + Pd), 3 terminations × 2 registries, dipole correction; k-mesh and layer-number tests; then 1–2 single points at 2 nm on 2 GPUs | Φ_Bn, Δρ(z), V(z) | decision window in 4.3 |
| 3.4 | Amorphous Al2O3 on the 1 nm IWO film, device-like Al2O3 \| IWO \| OH (~189 atoms; crystalline α/γ-Al2O3 do not match the 10.3 Å cell) | band offset to Al2O3; dEc with an asymmetric film | feeds the registered P8 Schrödinger–Poisson check |

**Dropped from Phase 3:** the relaxed full Pd/IWO/Al2O3 stack (about 309 atoms, about 165 GB) and the six-model Pd/V_O off-current mini-campaign, for the reasons in section 2. If the Pd work is triggered, it targets on-state and low-Vd behaviour.

### Phase 4 – disorder (deferred until GIXRD/TEM show the 2–6 nm microstructure)

| ID | Calculation | Question |
|---|---|---|
| 4.1 | Amorphous IWO bulk and 2 nm films by machine-learned-potential melt-quench, then DFT relaxation: 3 samples, about 40–100 GPU-h (ab initio MD would be about 150–570 GPU-h); acceptance tests pre-registered (density, coordination); software download needs approval | Do the localized tail states follow the confined CBM? This is the report's dominant model-form uncertainty at 2 nm (onset 0.26 vs 0.91 V). |
| 4.2 | V_O in the amorphous film: screen all sites with the potential, then DFT on 2–3 | V_O localization under disorder |

## 4. How results enter TCAD (a V2 model; V1 stays frozen)

1. First run the zero-launch S12 comparison of the registered V1 predictions (65/85 °C). Then fork V2 with its own timestamped register. Build V2 from `material_model_used.json` of runs 0038–0040 (and 0014), not from `config/` (the seed).
2. **Confinement:** the DFT dEc(t) (from 1.5, with the t^-2 asymptote from 1.7) enters through the exact identities (dEc ↔ Qf rigid shift), with no ATLAS launch. With one I–V curve per film it is falsifiable only by the optical gap or C–V (section 6).
3. **Pd barrier**, a model-conditional window computed by the TCAD review:
   - Φ_Bn < 0.18 eV: keep Ohmic.
   - 0.18–0.23 eV: testable only with low-Vd ID–VD.
   - Above 0.23 eV: inconsistent with the 2 nm θ bound unless tunnelling dominates.
   If inserted, use `WORKFUN = χ_ATLAS(t) + Φ_Bn,corr`, with the CBM-position correction (not the gap correction).
4. **ATLAS launches:** 1 + 1 contingency to certify the 2 nm m*/Nc change if |Δm*/m*| > 5 %; 0–2 conditional for the Pd barrier; 2 optional for P8. All sequential, with the user's approval (57/57 used).
5. **Never inserted:** slab V_O/W densities as N_D, slab defect DOS as g_t(E), or slab dipoles as Qf.

## 5. Dropped or deferred, with reasons

| Item | Decision | Reason |
|---|---|---|
| 6.3 and 13.2 nm slabs | dropped | about 379 GB and about 1.4 TB; confinement there is bounded at ≤0.05 and about 0.01 eV, below DFT noise and the HSE uncertainty; m* ratio 1.03 against the ×4.6 mobility step |
| HSE06 on 2 nm and on any interface | dropped | about 112 GB of exact-exchange arrays plus about 48 GB; the 1 nm ratio is transferred instead |
| Pd/V_O off-current mini-campaign (6 models at 2 nm) | dropped | its premise is refuted (section 2) |
| Full relaxed Pd/IWO/Al2O3 stack | dropped | about 165 GB; not identifiable from the existing data |
| 3 × AIMD amorphous | replaced by 4.1 | cost and restart fragility |
| Second W concentration in a slab | replaced by bulk 160 atoms (2.1) | a lower W fraction in a slab needs about 352 atoms |
| Bader charges | replaced by Löwdin (projwfc) | Bader code not installed; a download would need approval |

## 6. Experimental falsifiers (to request; these turn "computed" into "validated")

| DFT output | Measurement that tests it | Falsified if |
|---|---|---|
| ΔEg(2 nm) − ΔEg(13.2 nm) | optical gap vs thickness (ellipsometry/UV-vis) | measured shift < 0.1 eV |
| ΔEc split, Al2O3 offset | XPS valence-band offsets; V_FB(t) from multi-EOT C–V | sign or magnitude outside the DFT±HSE band |
| Pd barrier | low-Vd ID–VD at 2 nm (already a registered prediction) | linear low-Vd behaviour while Φ_Bn > 0.23 eV is predicted |
| Off-floor origin (not DFT) | I_G/I_S separation, channel-length series | — |
| W activation | gated Hall vs W content | — |
| Microstructure (Phase 4 trigger) | GIXRD/TEM at 2 and 6.3 nm | — |

Device replicates (3–5 per thickness) are needed for any 6.3 nm statement.

## 7. Budget and timeline (estimates)

| Phase | GPU-h | CPU core-h | Earliest window |
|---|---|---|---|
| 0 | 0 | small | now – 5 Oct |
| 1 | 25–40 (+40–120 for the 3 nm slab) | ~500 | 4 – 10 Oct |
| 2 | 100–200 | 1,000–4,000 | 6 – 20 Oct |
| 3 | 60–150 | 500–2,000 | after the approvals, about 15 – 31 Oct |
| 4 | 40–100 (+30–80 for V_O) | — | after GIXRD/TEM |
| **Core (0–3)** | **≈270–560 (340–840 with contingency)** | **2,000–8,000** | ~4 weeks |

A minimal decisive subset costs about 110–200 GPU-h: 1.1–1.5, 2.0–2.2, 2.4 and 3.2. For comparison, the project has used 85–90 GPU-h so far. The ticket must be renewed by the user before 8 October and then weekly.

## 8. Decisions needed from the user

1. Approve this plan, or change its priorities.
2. Approve the downloads: Pd and Al PAW data sets (Phase 3); later, the machine-learned-potential software (Phase 4).
3. Approve the ATLAS launches for V2 (up to 5, sequential).
4. Request the measurements in section 6 from the lab.
