# S4: Defect and trap physics vs IWO thickness (2 to 13.2 nm)

Scope: tail states and their thickness law; interface vs bulk trapping; donors, oxygen vacancies and compensation; subthreshold-slope inversion; off-state floors; bias stress. No ATLAS run was launched. Scripts and outputs are in `analysis_2026-09-25/scratch/S4/`:
- `s4_traps.py` → `s4_traps_out.txt`. Parts A-F and the figure `s4_trap_spectroscopy.png`.
- `s4_part2.py` → `s4_part2_out.txt`. Measured/ATLAS spectra, the 6.3 nm charge excess, floor checks.
- `s4_part3_63shape.py` → `s4_part3_out.txt`. The 6.3 nm shape scan.

Metrics come from EVIDENCE_BRIEF §2/§4. Campaign numbers come from `results/campaigns/campaign_A_6p3_hypotheses.json`.

## 0. Main findings

1. **Trap-DOS inversion, validated before use.** I use an exact charge-sheet identity: n_s0(Vg) = (L/qμW)·Σ_k gm(Vg − k·Vd). It removes both the Vd = 0.7 V drain term and the free-carrier capacitance from the SS. The trap DOS then follows as D_trap(u) = (Cox/q)(dVg/du − 1) − dn_f/du, with u = EF − Ec at the source. V_FB cancels.
   - **Validation:** applied to ATLAS curves whose DOS is known, the inversion recovers the input thermal DOS within ×0.73-1.31 for u = −0.20…−0.05 eV at 2 and 6.3 nm (runs 0012, 0014, 0015, 0033). At 13.2 nm it is exact only near −0.10 eV (×0.52-3.4 elsewhere, because the film potential is non-uniform).
   - **How I use it:** measured and ATLAS curves go through the *same* inversion, and only their ratios are used.
2. **Near Ec, the V1 tail reproduces all three films.** For u = −0.125…−0.025 eV the measured/ATLAS ratio is 0.81-0.98 (2 nm), 0.90-1.46 (6.3 nm) and 0.87-1.17 (13.2 nm).
   - What the data do not follow is the V1 *form* deeper down. There are ×2.2-2.8 more states at Ec − 0.175…−0.20 eV (2 nm) and ×2.6 more at Ec − 0.15 eV (6.3 nm).
   - Near Ec the sheet DOS grows sub-linearly with t: D(Ec − 0.1 eV) = 1.05 / 1.67 / 2.16e13 cm⁻²eV⁻¹, i.e. ∝ t^0.38±0.15. This is a **surface + bulk** signature: Ds ≈ 8.5e12 cm⁻²eV⁻¹ plus g_b ≈ 1e19 cm⁻³eV⁻¹. It is not a pure-bulk power law.
3. **Neither SS_cc nor SS_min(t) is a trap-only metric.**
   - **SS_cc is confounded by mobility.** The free-carrier crossover (C_free = Cox) sits at 3.2e-10 / 4.0e-10 / 1.8e-9 A/µm for μ = 10.7 / 13.3 / 59 cm²/Vs, so the 1e-10…1e-8 window straddles it. A trap-free 2 nm film already gives SS_cc = 122 mV/dec at μ 13.3, against 75 at μ 59.
   - **The naive formula reverses the trend.** It ranks 13.2 nm lowest (9.4e12 vs 2.0e13), while the proper inversion ranks it highest.
   - **SS_min is confounded by the floor.** The extractor only looks above 5× the measured floor, which cuts off at 2.3e-14 / 7.6e-13 / 3.3e-11 A/µm.
4. **Donors.**
   - A thickness-independent donor density cannot produce the Vth pattern. Fitting the 6.3 → 13.2 nm drop needs Nd = 2.2e18 cm⁻³. That value then predicts −0.25 V from 2 → 6.3 nm; the measured shift is −0.02 V.
   - The low Nd_eff of V1 is credible. Kim2024 IWO gives 4.3-4.5e17 cm⁻³ from its linear Von(t). It is also **unidentifiable** at 2 nm (0.036 V per 1e18 cm⁻³).
   - Qf (1.73e12 cm⁻²) acts as a sheet, not a volume. It is electrostatically identical to ionized V_O donors within ~1 nm of the Al2O3.
5. **The 6.3 nm on-state shape** needs ≈2e12 cm⁻² of extra trapped charge between Vth_cc and Vth_lin.
   - Front Dit is rejected: A4/run_0033 leaves the gap unchanged (0.857 vs 0.862 V).
   - The back acceptor sheet is rejected: A3/run_0030 closes the gap (0.72 V).
   - Two readings remain; ATLAS can test them. One is states piled within ~1-2 kT of Ec plus ~30 % higher μ (my surrogate). The other is a scaled tail plus μ ≈ 19.6 (S2's B0, run pending).
6. **The off-state floors are not gate leakage** (at 6.3 and 13.2 nm).
   - They are flat to ±3 % over Vg −3…−0.5 V, where any tunnelling or ohmic Igd would change ≥×3. They also rise ×1432 (∝ t^3.85) across an identical gate stack.
   - They behave as a gate-independent parallel conductance: 1.3e-13 / 4.4e-12 / 1.9e-10 S/sq.
   - The 2 nm floor (1.3 pA total) is at instrument level.
   - IG/IS records would settle this directly.
7. **Bias stress.** Januar's PBS in the same family gives 0.72-1.2 V after 1200 s at 6 V. Extrapolating that to a −3…+3 V sweep gives 0.003-0.24 V, and Nt can change ×2 (2 nm, Januar). Hysteresis is therefore a live but **not determined** confounder of the 0.29 V offset at 6.3 nm.

## 1. Tail-state density law (task 1)

**(a) Thickness form.** V1 uses Nt = 2e19·(2/t)^0.75, giving sheets of 4.0 / 5.3 / 6.4e12 cm⁻².
- **Surface + bulk alternative.** Nt·t = Ns + Nb·t through the same anchors gives Ns = 3.57e12 cm⁻² and Nb = 2.15e18 cm⁻³. It predicts Nt(6.3) = 7.8e18, 8 % below the power law (8.5e18).
- **Beyond the fitted range the two forms diverge.** Surface + bulk tends to Nb for thick films, where the power law tends to 0. At 31.8 nm surface + bulk is 30 % higher (3.3e18 vs 2.5e18).

**(b) Magnitude and origin of the law.** The law is **not physically derived**:
- the 2 nm anchor is fitted;
- the exponent 0.735 = ln 4 / ln 6.6 comes from one ratio ("roughly a factor of four", Januar §2.8). That ratio is itself a derived quantity of Januar's compact model (their Eq. 3 needs θt, Tt, μc and Nc);
- the two forms differ at 6.3 nm by less than the ±20-30 % accuracy of any single-curve extraction. Both are interpolations.

**(c) Discriminating predictions.**
- Surface + bulk predicts sub-linear growth of the sheet DOS, with a finite bulk limit.
- A pure-volume trap predicts sheet ∝ t.
- A pure interface predicts sheet = constant.

**(d) Data and model comparison.**
- The subthreshold inversion (part2 ratios; figure, left and middle panels) gives the near-Ec sheet exponent 0.38 (V1 input: 0.25).
- The fitted 2/13.2 decomposition at Ec − 0.10 eV predicts 6.3 nm within +13 %. At Ec − 0.05 eV the miss is +40 %, and the 6.3 nm film is the one above the interpolation.
- S2's curve-shape partition gives Nt(6.3) = 2.66e19, ×3.1 the law (B0 pending). It is therefore contradicted by both smooth forms, unless μ is re-partitioned.

**(e) Supporting and contradicting evidence.**
- *For surface + bulk:* the inversion is independent of Januar, and Januar says the 2 nm device's tail is "denser" through interface disorder (§2.7).
- *Against using Januar's absolute numbers:* the PBS devices give Nt = 5.3e19 (2 nm) and 3.39e18 (10 nm). That is a ratio of 15.6 (exponent 1.71), and the sheet *decreases* with t (1.06e13 → 3.4e12). It forces Nb = −9e18, which is unphysical. These are not the Fig. 5a devices (S5 agrees).
- *Kim2024 is not tail evidence.*
  - Its 2.37/3.12/14.6e18 cm⁻³eV⁻¹ are **gate-oxide border traps** from the 1/f carrier-number-fluctuation model (λ = 0.1 nm in SiO2), not IWO tail states. `config/iwo_material_model.yaml` ("support") conflates the two.
  - Its SS-derived Nt (3.32/3.96/7.03e12 cm⁻²eV⁻¹ on 90 nm SiO2) uses the naive formula that I show is confounded (§2), and it accelerates with t.

**(f) Evidence class.** The law itself is **calibration**. The surface + bulk decomposition is **correlation**, obtained from a method validated on ATLAS.

## 2. Subthreshold inversion and the two SS regimes (task 2)

**Naive formula.** D_eff = (Cox/q)(SS/59.5 − 1) gives:
- SS_min: 2.35 / 5.18 / 6.69e12 cm⁻²eV⁻¹, i.e. 1.2e19 / 8.2e18 / 5.1e18 cm⁻³eV⁻¹;
- SS_cc: 1.98 / 2.22 / 0.94e13.

Both are biased:
1. **Free carriers and drain bias.** In a fully depleted film with an air back there is no body-capacitance term, so SS − 59.5 must come from traps plus the **free-carrier capacitance** q²n_s/kT.
   - The 0-D charge-sheet surrogate reproduces ATLAS SS_cc: 294/303/165 vs 289/289/193 mV/dec (part C).
   - Without traps it still gives 122 mV/dec (μ 13.3) and 75 (μ 59) at 2 nm.
   - So about 60 mV/dec of the thin films' SS_cc, versus about 15 at 13.2 nm, is mobility, not traps.
   - The low SS_cc at 13.2 nm (160) mainly reflects that its window sits ~kT ln 4.5 ≈ 39 meV deeper in energy. It does not reflect fewer traps: the inversion gives 2.2e13 at Ec − 0.1 eV, the highest of the three.
2. **Floor-dependent window.** SS_min is evaluated only for Id > 5× the measured floor (`scripts/extract_metrics.py` l.9-12). That window reaches u ≈ −0.21 eV at 2 nm, −0.17 at 6.3 nm and only −0.13 at 13.2 nm. The rise of SS_min from 84 to 131 mV/dec is partly an artifact of the floors rising ×1432.

**Physical picture of the two regimes.** Vth_cc (1e-9 A/µm) sits at u = −0.051 / −0.071 / −0.118 eV, and Vth_lin at +0.063 / +0.028 / −0.003 eV (part2).
- **SS_min regime.** SS_min is set at u ≈ −0.15…−0.25 eV. There the DOS is the low-energy end of the tail plus the Dit and deep states: 2-6e12 cm⁻²eV⁻¹.
- **SS_cc regime.** Within ~3 kT of Ec the exponential tail (1-3e13 cm⁻²eV⁻¹, ×2.26 thermal enhancement for WTA 40 meV) and the free-carrier term take over. Hence 160-300 mV/dec.
- **Where the V1 model falls short.** It underestimates the deeper states: measured/ATLAS ratio 2.84 at −0.20 eV and 2.20 at −0.175 eV (2 nm), and 2.60 at −0.15 eV (6.3 nm). This is why run_0012 gives SS_min 73 against 84.5 measured. It is consistent with brief §4: removing confinement moves SS_min toward the data, which is another way of shifting the tail-to-deep-state balance.

**Identifiability from SS.**
- *Identifiable, given μ and Nc:* D_trap(u) over u ≈ −0.2…0 eV at 2 and 6.3 nm, and near −0.1 eV at 13.2 nm.
- *Not identifiable:*
  - where a state sits in space (front, bulk or back);
  - the absolute energy axis, which shifts by kT·ln(μ ratio): ±10-15 meV between the V1 and S2 mobilities;
  - acceptor vs donor character;
  - anything below u ≈ −0.2 eV, which the floors hide.
- *What breaks the degeneracies:*
  - D = Ds + g_b·t across thicknesses separates interface from bulk;
  - temperature (subthreshold activation energy) fixes u without μ;
  - Vd = 0.05 V transfer curves remove the drain term;
  - QS C-V gives the free/trapped partition.

## 3. Donors, oxygen vacancies and compensation (task 3)

**(a) Electrostatic weight.** Uniform donors in a fully depleted film shift Vth by −qNd·t/Cox − qNd·t²/2ε_s. Per 1e18 cm⁻³ (ε_s = 9.3, part E) this is:

| t (nm) | 2 | 6.3 | 13.2 | 31.8 |
|---|---|---|---|---|
| ΔVth per 1e18 cm⁻³ (V) | −0.040 | −0.151 | −0.406 | −1.55 |

**(b) What campaign A shows.**
- *A2 (run_0032, Nd0 1e16):* +0.030 V (0.350 → 0.380 V), SS_min +6.5 mV/dec, Ion −1.8 %. This confirms the analytic bound: V1's donors are electrostatically irrelevant at 6.3 nm.
- *A4 (run_0033, front Dit ×5):* +0.051 V and SS_min +8.3 mV/dec, with the gap unchanged. Reaching +0.29 V needs Dit ≈ ×24, i.e. ≈1.6e12 cm⁻² of charged acceptors. Extrapolating A4's slope, SS_min would then be ≈155 mV/dec against 114.7 measured. **Rejected.**

**(c) Is Nd_eff ≈ 2.5-3e17 credible?** Yes.
- *Why it is credible:*
  - Kim2024's IWO (different sputter process, 90 nm SiO2) shows Von shifting −2 V per 10 nm and linearly in t. That implies Nd = 4.5e17 (10 → 20 nm) and 4.3e17 (20 → 30 nm), within a factor 2 of V1.
  - Januar attributes n > 1e19 cm⁻³ to undoped In2O3 and V_O suppression to W (l.81-89). Wang2022 measures ~1e20 cm⁻³ in ALD In2O3.
  - Compensation is intrinsic to this model. In an isolated film, neutrality with the V1 tail pins EF at Ec − 0.21 / −0.17 / −0.15 eV (2 / 6.3 / 13.2 nm). Any donor density well below Nt·t is absorbed by filled tail acceptors.
  - A back-surface adsorbate acceptor sheet of 1e12 cm⁻² compensates up to 5e18 / 1.6e18 / 7.6e17 cm⁻³, which is strongest in the thinnest film.
- *Why it is not identifiable:* the curves fix only Qf + Nd·t (+ centroid term) per film.

**(d) Does the fitted Qf represent donors?** Its magnitude does. 1.73e12 cm⁻² corresponds to 8.7e18 / 2.7e18 / 1.3e18 cm⁻³ if spread through the film. But a *volumetric* donor at 8.7e18 would add −2.0 V at 13.2 nm. The shared fit therefore requires the charge to be **sheet-like at the front**.
- An interfacial layer of ionized V_O (≈1.7e19 cm⁻³ over ~1 nm, e.g. oxygen scavenging by the first IWO layers) and fixed charge in Al2O3/HfO2 are **indistinguishable on ID-VG**.
- Discriminators:
  - V_O donors respond to NBS, illumination and temperature (Kim2024 NBS: negative shifts that grow with t, assigned to V_O ionization); fixed oxide charge does not;
  - C-V frequency dispersion (Wang2022 assigns it to donor-like subgap states);
  - XPS O 1s depth profiles.

**(e) Coupling to the 13.2 nm Vth drop and to 31.8 nm.**
- **Positive charge needed without confinement** (runs 0016 / 0034-A6 / 0017):

  | t (nm) | 2 | 6.3 | 13.2 |
  |---|---|---|---|
  | needed charge (cm⁻²) | +4.8e10 | −2.7e11 | +1.43e12 |

  My 13.2 nm value, from run_0017's Vth_cc of 0.030 V, differs from the brief's ~1.86e12; the brief's derivation is NOT DETERMINED.
- **Monotonic donors cannot fit these three points.** A single uniform Nd fitted to 6.3 → 13.2 nm (2.2e18) misses 2 → 6.3 nm by 0.23 V. With confinement, the miss grows to ~0.5 V.
- **The readings that remain:**
  - V1: confinement plus a front sheet;
  - a **donor step**, meaning the no-confinement fit plus Nd ≈ 2.5e17 for t ≤ 6.3 nm, rising by ≈7e17 at 13.2 nm (0.248 V) and to ≳2e18 cm⁻³ at 31.8 nm. The 31.8 nm always-on state at −3 V needs ΔVth > 3.3 V, i.e. Nd ≳ 2.1e18 or a back donor sheet ≳4e12 cm⁻² (0.80 V per 1e12 cm⁻² at 31.8 nm).
- **The donor step has three supports:**
  - it coincides with S2's mobility step;
  - Januar links crystallinity to higher carrier density on annealing (l.186-187);
  - Kim2024 shows donors rising with t.
- **It is degenerate with confinement on Vth(t).** It is S3's lane to break this with the optical gap vs t, and S1's lane with V_FB(t) from C-V.

**(f) Evidence class.** Nd_eff is calibration; Kim's Nd is correlation. The A2 and A4 results are predictions (pre-registered, one mechanism at a time).

## 4. What trap redistribution explains the 6.3 nm on-state? (task 4)

**Requirement.** The measured gap (Vth_lin − Vth_cc) is 1.176 V; run_0015 gives 0.820 V. That means ΔQ ≈ Cox·0.356/q = **1.99e12 cm⁻²** of extra charge filled between Vth_cc and Vth_lin, with gm_max ×1.30 and Ion unchanged.

**Energy location (inversion, measured minus run_0015).** The answer depends on the assumed mobility:

| mobility | u = −0.17…−0.10 eV | u = −0.10…0 eV | u > 0 | total |
|---|---|---|---|---|
| V1 μ (10.65) | +3.3e11 | +6.5e11 | −9.8e11 | ≈0 |
| S2 μ (17.9) | +5.5e11 | +1.9e12 | +1.6e12 | +4.1e12 |

- With the V1 μ, the 6.3 nm film has **more states in the last ~50 meV below Ec** (ratios 1.25/1.46/1.72 at −0.05/−0.025/0 eV) and fewer "apparent" states above Ec (ratio 0.25 at +0.05 eV).
- In other words, the traps fill by Vth_lin and then saturate. That gives a later but steeper turn-on, which is exactly the measured shape. The measured gm(3 V)/gm_max = 0.981 at 6.3 nm and 1.000 at 2 nm (S2) is consistent with saturation.

**Candidates (0-D surrogate scan, part 3).** Each variant is rigidly aligned to Vth_cc. The surrogate's own error on run_0015 is +0.22 V in the gap and +15 % in gm, so only the *differences* are used.
- **Front Dit at Ec − 0.3 eV** (×5; also run_0033): gap +0.02 V. **Rejected.**
- **Back fixed acceptor sheet** (run_0030): gap 0.724 V (it closes), SS_min 97.7. **Rejected as the sole cause.**
- **Exponential tail ×1-4 at the same WTA.** The 0-D model over-fills a 6.3 nm film at high Vg because it has no front-accumulation layer. So the gap/gm/Ion triplet cannot be satisfied here (tail ×3.14, μ 17.9: Ion −72 %). S2's 1-D surrogate predicts only −5 to −10 %, so **run B0 decides**.
- **Broader tail** (WTA 60 meV, Nt ×2, μ 17.9): gap and gm fit, Ion −15 %, but SS_cc +126 mV/dec. Disfavoured.
- **Narrow acceptor band.** Ns 2-3e12 cm⁻² at E0 = Ec − 0.03…−0.10 eV (σ 0.02-0.04), with μ ≈ 14 (band μ ≈ 15.4): gap +0.23…+0.28 V, gm +23-25 %, Ion ±3 %. SS_cc rises only +23 mV/dec when E0 = −0.03 eV, but +70…+150 mV/dec for deeper bands. **Only states within ~1-2 kT of Ec survive the SS_cc = 295 constraint.** Physically these are localized states just below the mobility edge, 2e12 cm⁻² ≈ 3e18 cm⁻³ in 6.3 nm.

**Interface or bulk?** At a single thickness this cannot be decided. The 6.3 nm excess sits +13…+40 % above the 2/13.2 surface + bulk interpolation, so it is film-specific, not a smooth law.

**Proposed ATLAS test** (for S6 / main session; a prediction, not run):
- *Deck change:* add an acceptor Gaussian to run_0015 with NGA = 2e12/(6.3e-7·0.02·√π) = 9.0e19 cm⁻³eV⁻¹, EGA = 0.03 eV, WGA = 0.02 eV; set μ_band 15.4 and refit Qf rigidly.
- *DOS 384/192 is required.* If the 96 acceptor levels are spread over the ~3.4 eV gap, they are ~35 meV apart and cannot resolve a 20 meV band. The actual level placement is NOT DETERMINED; check it in the manual.
- *Expected:* Vth_lin +0.2-0.3 V, gm_max +20-30 %, SS_cc +20-30 mV/dec, SS_min unchanged.
- *Falsified if:* gm does not rise, or SS_cc exceeds ~330 mV/dec.
- *Competing test:* B0, S2's scaled-tail hypothesis.

## 5. Off-state floors (task 5)

**Measured behaviour** (part D). Floors are medians over −2…−0.5 V; slopes are over −3…−0.5 V.

| t (nm) | floor (A/µm) | total current | Vg slope (dec/V) | parallel G (S/sq) |
|---|---|---|---|---|
| 2 | 4.6e-15 | 1.3 pA | +0.08 over −2…−0.5; +1.2 below −2 V, falling to 1e-16 | 1.3e-13 |
| 6.3 | 1.5e-13 | 44 pA | −0.011 | 4.4e-12 |
| 13.2 | 6.6e-12 | 1.9 nA | −0.002, ±3 % | 1.9e-10 |

- Thickness exponents: 3.05 (2 → 6.3 nm), 5.09 (6.3 → 13.2 nm), 3.85 overall (×1432).

**Gate leakage.**
- The stack is 15 nm HfO2 + 2 nm Al2O3. At |Vg| = 1/2/3 V the field is 0.52/1.03/1.55 MV/cm in HfO2 (×2.17 in Al2O3).
- A Fowler-Nordheim estimate (TiN/HfO2 barrier 1-2 eV, m* 0.2-0.4; not locally sourced) spans 3e-28 to 5e-2 A/cm² at 3 V, so the magnitude is **not determinable**.
- Two decisive arguments do not need a magnitude:
  1. **Vg dependence.** Over Vg −0.5 → −3 V, V_gd rises from 1.2 to 3.7 V. Tunnelling or Poole-Frenkel current would change by orders of magnitude, and even an ohmic leak by ×3.1. The measured 6.3 and 13.2 nm floors change by ≤×1.06.
  2. **Thickness.** The gate stack is identical for every film, yet the floor rises ×1432.

  Gate leakage is therefore **rejected** as the dominant floor at 6.3 and 13.2 nm. For scale only: with an assumed (not measured) 290 × 100 µm² leaking area, the floors would need J = 4.6e-9 / 1.5e-7 / 6.6e-6 A/cm².
- **Thermal SRH generation** is 13-17 decades too small (Astra `PRIORITY_THREE_OFF_CURRENT_AUDIT.md`).

**What remains.** A **gate-independent parallel drain-source path** whose conductance grows ∝ t^3.85. No gated channel can produce such a path under drift-diffusion: in a fully depleted film with no back electrode, n_back ∝ exp(qVg/kT).
- *An ungated IWO path fits the order of magnitude.* Examples are film outside the gate footprint or beyond W, or edges. An isolated V1-parameter film has q·n0·μ·t = 4.5e-10 / 3.4e-9 / 1.1e-7 S/sq. That is ×255 from 2 to 13.2 nm against ×1432 measured, and it implies a geometry factor of 3e-4…2e-3. This is **plausible, unverified**.
- *Physically,* the floors then track n0 ∝ exp[(EF0 − Ec)/kT]. The measured ratio, after the t and μ factors, needs EF0 − Ec to move up by kT·ln 48 ≈ 0.10 eV from 2 to 13.2 nm. That is less than the extrapolated dEc difference (0.33 eV, which would give ×3e5). If the path is confirmed, this bounds confinement and donor compensation *together* (coupling to S3). Januar's Ioff ∝ t·n_FB (Eq. 4) encodes the same idea but is circular: n_FB is extracted from Ioff.
- *At 2 nm,* 1.3 pA with a non-flat below-−2 V segment is at probe-station floor level: **not interpretable**.

**Implication for donors.** A floor rising steeply with t supports a larger free-carrier or donor population in thicker films. It is qualitatively the same direction as the donor-step / EF0 reading in §3e, and the 31.8 nm always-on state (7.9e-6 S/sq) is its extreme.

**Settling measurement.** Record IG and IS simultaneously with ID over −3…0 V:
- IS ≈ −ID with IG ≪ ID means a source-drain parallel path;
- IG ≈ ID means gate leakage;
- floor ∝ 1/L on an L-series, or its absence on a mesa-isolated channel, identifies an ungated path.

## 6. Hysteresis and bias stress (task 6)

**What the literature reports.**
- *Januar PBS* (6 V, 0-1200 s): ΔVth ≈ 0.72 V (10 nm IWO), up to 1.2 V (2 nm IWO, roughly linear in time), 0.93 V (10 nm In2O3). Nt at 2 nm rose 5.3e19 → 1.05e20.
- *Sign check:* Januar attributes the 2 nm positive shift to activated traps "contributing positive charge". A positive charge would shift Vth *negatively*, so electron trapping is the consistent reading. A reviewer will flag this.
- *Kim2024:* "negligible hysteresis" in dual sweeps, but on a different IWO process with 90 nm SiO2. The NBS values are only in figures, so their magnitude is NOT DETERMINED here.

**Scaling to one measured sweep.** Assume cumulative time at Vg ≥ 1 V of 10-60 s, ΔV ∝ t^β with β = 0.3-1, and field scaling (3/6)^1-2. The result is **0.003-0.24 V**.
- The upper end is comparable to the 0.29 V offset at 6.3 nm.
- Stress also changes Nt (×2 at 2 nm), so electrical history can alter the *shape* (gap and SS), not just the rigid offset.

**What is missing.** Sweep direction, dwell, prior stress and replicates are all unrecorded. Verdict: **not determined**. It is a credible confounder of a single-device 6.3 nm point.

## 7. Couplings and identifiability

| degenerate set on one ID-VG curve | what breaks it |
|---|---|
| Qf ↔ gate WF ↔ χ ↔ Nd·t (+t² centroid) ↔ back-surface charge (all rigid shifts in a fully depleted film) | C-V V_FB(t): a sheet is t⁰, a volume is t + t², the back surface is t/ε_s; passivation; XPS |
| NTA ↔ WTA ↔ near-Ec band ↔ μ_band (gap, gm, Ion; S2) | temperature series (activation vs u), QS C-V free/trapped partition, Hall on unpatterned films |
| Dit (front) ↔ back-surface states ↔ bulk deep states | thickness series D = Ds + g_b·t (started here), air vs passivated, conductance method |
| SS_cc ↔ μ (free-carrier and drain terms) | the charge-sheet inversion (needs μ) or Vd = 0.05 V curves |
| SS_min ↔ floor window | a common current window or subtraction of IG/IS-identified leakage |
| confinement dEc ↔ donor step ↔ EF0(t) (S3, S1) | optical gap vs t, V_FB(t), T-activation of the floor once its path is identified |

Cross-lane couplings:
- **S1:** the no-confinement donor-step reading has a smaller 6.3 nm miss at the Vth_cc level (A6: −0.057 V) than V1 (−0.29 V). But it needs donors to step between 6.3 and 13.2 nm, co-located with S2's mobility step.
- **S2:** B0 vs my near-Ec band hypothesis; both raise μ.
- **S5:** the inversion assumes negligible Rsd in subthreshold, which is safe (Rsd ≲ 4 % of R_on); the floor path needs IG/IS.
- **S6:** DOS level spacing for narrow bands; the SS_min extractor window.

## 8. Trap-specific measurements (in priority order)

1. IG/IS alongside ID, plus an L-series or a mesa device (floors).
2. Transfer curves at Vd = 0.05 V, plus dual sweeps with recorded dwell and sweep order (inversion without the drain term; hysteresis magnitude).
3. T-dependent transfer at 3-4 temperatures. The subthreshold activation energy gives Ec − EF(Vg) directly, which turns the inversion into a μ-free DOS measurement.
4. QS plus multi-frequency C-V and conductance per thickness: interface vs bulk DOS, and whether Qf is ionized V_O (dispersion).
5. Passivated vs air-exposed devices (back-surface acceptors or adsorbates).
6. GIXRD/TEM and Hall vs t (the donor and mobility step).
7. Short NBS/PBS on 6.3 nm replicates.

## Verdicts

| mechanism | verdict | evidence class | key number |
|---|---|---|---|
| Exponential acceptor tail near Ec controls threshold and SS_cc in all films | strongly supported | calibration (+ inversion validated on ATLAS) | measured/ATLAS D ratio 0.81-1.17 for u −0.125…−0.025 eV (2, 13.2 nm) |
| Nt ∝ t^-0.75 as a physical law | rejected as physics (keep as interpolation) | calibration | surface + bulk differs by only 8 % at 6.3 nm; exponent from one ratio |
| Surface + bulk trap DOS (Ds + g_b·t) | plausible, unverified (preferred form) | correlation | Ds ≈ 8.5e12 cm⁻²eV⁻¹, g_b ≈ 1e19 cm⁻³eV⁻¹ at Ec − 0.1 eV; sheet ∝ t^0.38 |
| Deep states (Ec − 0.15…−0.2 eV) underestimated in V1 | strongly supported | calibration (residual) | ×2.2-2.8 (2 nm), ×2.6 (6.3 nm) |
| SS_cc(t) read as a trap trend (naive SS formula, as in Januar/Kim) | rejected | calibration (surrogate check) | trap-free SS_cc 122 (μ 13) vs 75 (μ 59) mV/dec |
| Front interface acceptors as the 6.3 nm cause | rejected | prediction (A4, run_0033) | ×5 → +0.051 V, gap unchanged; ×24 needed → SS_min ≈ 155 |
| Back-surface acceptor/adsorbate sheet as sole 6.3 nm cause | rejected | prediction (A3, run_0030) | gap 0.72 vs 1.18 V; SS_min 97.7 vs 114.7 |
| Low effective donor density (Nd_eff ~ 2.5e17, compensated) | plausible, unverified | correlation (Kim2024) + calibration | Kim 4.3-4.5e17; 0.036 V per 1e18 at 2 nm (not identifiable) |
| Thickness-independent uniform donors explain 13.2 nm Vth drop | rejected | calibration | needs 2.2e18; misses 2 → 6.3 nm by 0.23 V |
| Donor step (≤6.3 nm ≈ 2.5e17 → 13.2 nm ≈ 1e18 → 31.8 nm ≳ 2e18) | plausible, unverified | correlation | +0.248 V at 13.2 nm without confinement; degenerate with dEc |
| Qf = ionized V_O layer at the front interface | plausible, unverified | none (electrostatically identical to oxide charge) | 1.73e12 cm⁻² ≈ 1.7e19 cm⁻³ over 1 nm |
| States within ~1-2 kT of Ec + higher μ produce the 6.3 nm shape | plausible, unverified | calibration (surrogate; ATLAS test proposed) | 2e12 cm⁻² at Ec − 0.03 eV: gap +0.28 V, gm +24 %, SS_cc +23 |
| Off-state floors = gate leakage | rejected (6.3, 13.2 nm) | correlation | flat ±3 % over 2.5 V; ×1432 with an identical stack |
| Floors = gate-independent parallel IWO path | plausible, unverified | correlation | G 1.3e-13 / 4.4e-12 / 1.9e-10 S/sq ∝ t^3.85 |
| Floors = thermal SRH generation | rejected | calculation (Astra audit) | 13-17 decades short |
| Sweep hysteresis/stress behind the 0.29 V offset at 6.3 nm | not determined | none | 0.003-0.24 V extrapolated from Januar PBS |
