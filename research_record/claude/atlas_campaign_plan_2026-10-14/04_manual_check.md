# 04 ATLAS 5.28 manual + generator check of every statement form in the remaining S2/S3 campaign (2026-10-14)

Read-only check. Nothing launched, nothing edited outside this folder. No output of run_0075/0076/0077 was opened; the S2-11 numbers below come only from the allowed scored file `register_scores/hc_mesh_run_0076_run_0067.json`. No amorphous-DFT quantity was used.

**Sources.**
- `M` = ATLAS 5.28 manual text, `IWO_PHYSICS_CONSTRAINED_MODEL_V1/report_latex_full/tools/atlas_manual_pages.txt` (Silvaco Atlas User's Manual, 25 Jun 2019; authority). Cited as `M l.<line>, p.<PDF page>`.
- `M04` = 2004 manual text, `.../atlas_user_manual_740p.txt` (second reference), cited `M04 l.<line>`.
- Deck text: `analysis_2026-10-10_campaign/s2_prep_decks/*.in`, `deck_diffs.txt`, `sample_decks/*.in`, `sample_decks/extra/*.in`, `sample_decks/NEW_STATEMENTS.md`. Generator: `scripts/build_iwo_decks.py` (cited `G:<line>`). Activation parser: `analysis_2026-10-10_campaign/post_run_checks.py` (`P:<line>`).
- Solver printouts used as EMPIRICAL evidence of what this build prints: `results/runs/run_0067_2p0_c10_s0_02_2p0/deckbuild.out`, `run_0073_.../deckbuild.out`, `run_0074_.../deckbuild.out` (not in the forbidden set).

**Labels.** Manual defaults/units = LITERATURE (vendor manual, no DOI; line cited). Deck values keep the design's labels. My arithmetic = CALCULATED (formula + inputs shown). ATLAS outputs = COMPUTED (our ATLAS run, file cited). Printout facts = EMPIRICAL (file cited). Physical constants: CODATA 2018 (LITERATURE: Tiesinga et al., Rev. Mod. Phys. 93, 025010 (2021), DOI 10.1103/RevModPhys.93.025010).

**Verdict codes.** VERIFIED = manual text gives syntax, units, default. READING = supported by a reading of the text, not stated explicitly. UNVERIFIED = must be confirmed by the first launch (deckbuild.out or behaviour). ISSUE = manual statement that contradicts or qualifies the design.

---

## 0. Bottom line

| # | Finding | Branch / runs | Code |
|---|---|---|---|
| 1 | QTNLSC with an Atlas-built mesh has **no documented slice or point-count control**; the only knobs are the device mesh, `SHAPEOX` and `QTX.MESH/QTY.MESH`. Baseline oxide steps are 1–3.4 × the tunnelling decay length; S2-11 halving gives a *systematic* −0.17…−0.44 dec shift at V_G ≥ −0.45 V and erratic changes up to +2.86 dec inside the floor window. | S2-04/06/08, S2-11 follow-up, tunnelling-mesh branch | ISSUE + design input (§4) |
| 2 | `TRAP.HURKX` is **not an extra generation mechanism**: it restricts the TRAP.TUNNEL enhancement of CONTINUOUS DEFECTS/INTDEFECTS to the R/G term. This build prints no flag row for it. | S2-01, S2-03 | ISSUE (wording) + UNVERIFIED (activation) |
| 3 | ITAT: `TAT.SLICEPTS` (default 12) must be convergence-checked by the manual's own rule; ITAT tunnels into band states only unless `TAT.LOCAL` (amorphous channel tails) is set; bilayer auto-detection and the ITAT mass are not documented. | S2-12, S2-13 | ISSUE + UNVERIFIED |
| 4 | BQP: with any BQP model `METHOD NEWTON` is ignored and BLOCK is used unless `METHOD BQP.NEWTON` (then `FREEZEBQPNI` on later SOLVEs); the generator emits neither, nor `NOCURRENT`. BQP γ/α defaults are silicon-calibrated. | S3-24, S3-25 | ISSUE |
| 5 | Schottky: every statement exists with the design's units. Two consistency flags: default `VSURFN = ARICHN·T²/(q·NC)` is 4.27× too low at 2.0 nm because of the quasi-2D NC300; image-force lowering reaches 0.2 eV at an interface field of 2.6 MV/cm and no cap is documented. | S3-17…S3-23 | ISSUE (consistency) + UNVERIFIED |
| 6 | IGZO.TOKYO formula, units and defaults VERIFIED; MUN/TMUN interplay is as designed. `MOBILITY MATERIAL=` is documented for Table B-1 materials only, so `material=IWO` (user material) is UNVERIFIED; the documented fallback is `REGION=1`/`REGION=2`. The parser checks region 1 only. | S3-11…S3-16, S3-27 | UNVERIFIED |
| 7 | FNORD: syntax/units VERIFIED; F.AE/F.BE reproduced within 0.1 %. The audit claim (field at the semiconductor–insulator segment) is a correct READING, not explicit text. The existing `interface qf … y.min=-1e-7 y.max=1e-7` line also **localises FN** to the IWO/Al2O3 interface (manual, default S.I.). | S2-09, S2-10 | READING + UNVERIFIED detail |
| 8 | The semiconductor-side lateral mass in the QTNLSC prefactor (direct gap: DOS mass) is undefined for `user.default=silicon`. EMPIRICAL: the IWO thermal velocity printed in run_0067 is the silicon formula value, so silicon mass defaults are inherited despite NC300. Span of the prefactor: up to 0.91 dec. | all QTNLSC | UNVERIFIED |
| 9 | Boltzmann, tail placement, strip deck, SRH/DEFECTS σ, TAUN0/TAUP0, MASS.TUNNEL: syntax/units/defaults VERIFIED. Tail "placement" is a thickness law, not a spatial placement; at 2.0 nm all three placements are the same deck (S3-04, S3-07 duplicate S0-01, already in register l.2164). | S3-04…S3-10, S3-26, S2-14…17, S2-01…03 | VERIFIED + note |
| 10 | Two-carrier risk: run_0073 (S1-06, 13.2 nm, carriers=2) timed out at 3600 s with 22 Newton non-convergence warnings (EMPIRICAL). S2-01 is the same film with carriers=2 plus extreme SRH/TAT and the same 3600 s timeout. | S2-01 | launch risk |

---

## 1. S2 generation bound: SRH, DEFECTS σ, TRAP.TUNNEL, MASS.TUNNEL, TRAP.HURKX, carriers=2 (S2-01/02/03)

**Deck text** (S2-03, `s2_prep_decks/S2-03_c10_s2_03_2p0.in`; S2-01 same at 13.2 nm with `mass.tunnel=0.2123`):
`material … taun0=1e-09 taup0=1e-09 tmun=0`; `models fermi srh temp=300 print trap.tunnel trap.hurkx mass.tunnel=0.2543`; DEFECTS `sigtae/sigtah/sigtde/sigtdh/sigg*=1e-13`; `method newton trap … carriers=2` (both METHOD lines). S2-02: `models fermi temp=300 print`, σ = 1e-20, τ 1e-6, carriers=2.

| Statement | Manual | Verdict |
|---|---|---|
| `SRH` on MODELS, `TAUN0/TAUP0` on MATERIAL (s) | M l.10141–10175, p.228–229: SRH enabled by MODELS SRH; TAUN0/TAUP0 user-definable on MATERIAL; one level at ETRAP = 0 | VERIFIED. EMPIRICAL: run_0067 printout lists `taun0/taup0` per region (deckbuild.out l.291–292). |
| DEFECTS `SIGTAE/SIGTAH/SIGTDE/SIGTDH`, `SIGGAE…` (cm²) | M l.48761–48781, p.1173–1174: Real, cm², defaults 1e-16 / 1e-14 / 1e-14 / 1e-16 | VERIFIED |
| DEFECTS R/G | M l.37086–37090, p.883: steady-state SRH-type R/G of the defect states (Eq. 15-16) | READING: the text does not tie DEFECTS R/G to MODELS SRH. S2-02 removes both (no `srh`, σ 1e-20), so the control is correct either way. |
| `TRAP.TUNNEL` | M l.37203–37220, p.884: for TFT DEFECTS the field enhancement Γ multiplies the capture cross-sections SIGTAE, SIGGAE, SIGTDE, SIGGDE (electrons) and SIGTAH… (holes). M l.10460–10465, p.235: for SRH it modifies the lifetimes (Eq. 3-380). | VERIFIED. Printout flag `tat(local)` exists (EMPIRICAL, run_0074 deckbuild.out l.374); parser checks it (P:146). |
| `MASS.TUNNEL` (relative mass) | M l.37278–37280, p.885 (TFT TAT) and l.5038–5040, p.132; MODELS default 0.25 (l.58007, p.1445) | VERIFIED. Deck value = m*(t) (LITERATURE 0.208 + DFT Δm law, FITTED to COMPUTED points). EMPIRICAL: this build prints `mass.tunnel` under "Band-to-band tunneling Parameters" (run_0067 deckbuild.out l.331, value 0.25 there). **First launch must show 0.2123 / 0.2543.** |
| `TRAP.HURKX` | M l.58524–58526, p.1460: "the trap-assisted tunneling enhancement factor used in the CONTINUOUS DEFECTS and INTDEFECTS models applied only to the recombination/generation model". Not in M04 (5.28-only). | **ISSUE (wording).** It is a *scope modifier* of TRAP.TUNNEL, not an additive mechanism: with it, trap occupancy (charge) keeps the unenhanced σ and only R/G is enhanced. That is the cleaner choice for a generation bound (no electrostatic shift mixed into ΔI_D), but the design text "SRH extreme + TRAP.TUNNEL + TRAP.HURKX" should say "TRAP.TUNNEL applied to R/G only (TRAP.HURKX)". **UNVERIFIED activation:** the REGIONAL MODEL FLAGS table of this build has no row for it (EMPIRICAL, run_0074 deckbuild.out l.341–379; only `bbthurkx`, which is BBT.HURKX). Hand check: `bbthurkx` must stay F. |
| `carriers=2` on METHOD | M p.301 (QTUNN works with CARRIERS 0/1/2, l.13629); METHOD CARRIERS is generic | VERIFIED syntax. Echoed in deckbuild.out (EMPIRICAL, run_0073 l.224); parser does not check it. |

**Thermal velocity (affects the size of the "extreme" bound).** M l.4974–4980, p.131: v_n = (3kT/(M.VTHN·m0))^½; if M.VTHN is not set, the DOS mass is extracted from NC, except for silicon, which uses its own formula (Eq. 3-104). EMPIRICAL: run_0067 (2.0 nm, NC300 = 1.373e19) prints `vn = 1.08e+007 cm/s` (deckbuild.out l.336). CALCULATED: the silicon formula M.VTHN = 1.045 + 4.5e-4·300 = 1.18 gives (3·kT/(1.18 m0))^½ = 1.08e7 cm/s, whereas the NC-derived mass (0.669 m0, below) would give 1.43e7 cm/s. So `user.default=silicon` inherits silicon's mass formula. For m* = 0.2543 m0 (deck value), (3kT/m*)^½ = 2.32e7 cm/s (CALCULATED, CODATA constants). R/G scales with σ·v_n, so the S2-01/03 bound is σ·v_n = 1e-13 cm² × 1.08e7 cm/s, i.e. ×0.47 (CALCULATED) of what "σ = 1e-13 with the IWO thermal velocity" would mean. Steady-state electron-only occupancy does not depend on v_n (detailed balance), so the baselines are unaffected. Report the bound as σ·v_n, or set `M.VTHN` (amendment).

**Launch risk.** run_0073 (S1-06: 13.2 nm, carriers=2, timeout 3600 s) ended `timeout`, `converged = no`, 3600.5 s, 22 "Newton algorithm did not converge in 80 iterations" warnings (EMPIRICAL, RUN_INDEX.csv and run_0073 deckbuild.out). S2-01 has the same film, carriers=2, extreme SRH and TRAP.TUNNEL, and timeout 3600 s (campaign_matrix.json). The work chat already holds "one targeted continuation repair" for S1-06 (CODEX_WORK_CHAT l.368, l.386); S2-01 should not be launched before that repair is understood.

---

## 2. FNORD with F.AE/F.BE (S2-09 2.0 nm, S2-10 13.2 nm; sample `sample_decks/extra/S2-10_c10_s2_10_13p2.in`)

Deck text: `models fermi srh temp=300 print fnord f.ae=2.171e-06 f.be=8.628e+07`; oxide `material region=3/4 affinity eg300 me.tunnel` (worst set); HfO2 y.mesh at 0.017 µm refined to 0.25 nm; `log … j.tun`; `extract … curve(v."gate",ifn."gate") outfile="ifnvg.dat"`. No `exclude_near`, no `qtunn.cmass` (correct: those belong to the QT model).

| Item | Manual | Verdict |
|---|---|---|
| FNORD self-consistent; FNPP post-processing; FN.CUR = FNORD+FNHOLES | M l.13024–13033, p.288 | VERIFIED |
| J = F.AE·E²·exp(−F.BE/E); E = magnitude of the oxide field; F.AE/F.BE on MODELS; defaults 1.82e-7 / 1.90e8 | M l.13017–13023, Table 3-126 l.13040–13046, p.288; MODELS list l.57764–57765, p.1438: F.AE units C·V⁻²·s⁻¹ (= A/V²), F.BE V/cm | VERIFIED |
| Current computed per insulator–semiconductor segment, added to an electrode–insulator segment found along the field vector at the semiconductor–insulator interface (default) or by NEARFLG | M l.13034–13038, p.288; l.13053–13061, p.289; same text M04 l.8214–8220 | VERIFIED |
| Localisation: "By default … applied to all relevant interfaces. To localize the model, use one or more INTERFACE statements with … X.MIN, X.MAX, Y.MIN, Y.MAX … S.I. … enabled by default" | M l.13066–13071, p.289 | **Consequence:** the deck's existing `interface qf=1.38345e+12 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001` (Q_f line) also restricts FN to the IWO/Al2O3 interface. That is the intended interface, and it excludes the IWO/Air surface (where FN would be negligible anyway). The dual role should be stated in the run notes. |
| `ifn."gate"` extract | DeckBuild manual only (audit §4) | UNVERIFIED in ATLAS text; parser records presence of `ifnvg.dat` (P:205). |

**Audit/design claim "FNORD evaluates the field at the semiconductor–insulator segment (Al2O3/IWO)".** READING, correct: the current is computed per insulator–semiconductor segment (l.13034–13036) from "the electric field in the oxide" (l.13019), and the receiving segment follows "the electric field vector at the semiconductor–insulator interface" (l.13055–13056). The manual does not say whether E is the element field of the first Al2O3 element or a nodal value, nor that it is the insulator-side value explicitly (UNVERIFIED detail). The transfer is exact under D-continuity with no charge at the Al2O3/HfO2 interface (true in S2-09/10: no INTERFACE line at y = 0.002 µm, no oxide traps):
- CALCULATED: r = ε_HfO2/ε_Al2O3 = 19.57/9.0 = 2.1744 (ε_HfO2 MEASURED; ε_Al2O3 ASSUMED).
- CALCULATED (Lenzlinger–Snow form as used in IMPLEMENTATION.md §11.6; A = q²/(8πh φ)·(m0/m_ox), B = 8π(2m_ox m0)^½(qφ)^{3/2}/(3qh)): worst φ = 1.5 eV, m = 0.10 (ASSUMED set) → A = 1.028e-5 A/V², B = 3.968e7 V/cm → F.AE = A/r² = 2.173e-6, F.BE = r·B = 8.629e7; nominal φ = 2.2 eV, m = 0.20 → A = 3.503e-6, B = 9.968e7 → 7.409e-7, 2.168e8. Deck/config: 2.171e-6 / 8.628e7 and 7.402e-7 / 2.167e8: agreement within 0.1 %.
- Cross-check: M l.16881–16883 quotes F.AE = 1.5414e-6 and F.BE = 6.8308e7 as constants of another model; these equal q²/(8πh) (A·eV/V²) and 8π(2m0)^½q^{3/2}/(3qh) (V/cm·eV^{-3/2}) (CALCULATED), the same prefactors used above.
- Still a single-barrier, HfO2-limited estimate (design §7.3).

**Mesh.** In the planar, charge-free oxide the potential is linear in y in each layer (Laplace; READING of the 1-D geometry away from x = 0, 2, 22, 24 µm), so the interface field is represented exactly by any oxide mesh; FNORD is therefore expected to be insensitive to the oxide mesh (CALCULATED argument), which makes it the mesh-robust magnitude cross-check of the QTNLSC worst set in the FN regime.

**First-launch checks.** I_G non-zero and same sign as QTNLSC at −3 V (run_0067 I_G < 0 at −3 V, COMPUTED, hc_mesh JSON ref column); `ifnvg.dat` present; FN-plot check: ln(|I_G|/(L_g·E_Al²)) against 1/E_Al must have slope −F.BE with E_Al from the oxide voltage of a saved structure (L_g = 24 µm, deck geometry).

---

## 3. QTNLSC.EL / QTNL.DERIVS and companions (S2-04, S2-06, S2-08, S2-11 family)

Deck text (S2-04, `s2_prep_decks/S2-04_c10_s2_04_2p0.in`): `material region=3 affinity=1.25 eg300=8.8 me.tunnel=0.35`, `material region=4 affinity=2.5 eg300=5.8 me.tunnel=0.2`, `contact name=gate workfunction=4.7 qtunn.cmass=1`, `contact name=source exclude_near`, `contact name=drain exclude_near`, `models fermi srh temp=300 print qtnlsc.el qtnl.derivs`, `log … j.tun`.

| Item | Manual | Verdict |
|---|---|---|
| QTNLSC.EL (self-consistent, electrons), QTNL.DERIVS (extra Jacobian terms, better convergence, slower) | M l.13633–13653, p.301, Table 3-129; MODELS list l.58736–58744, p.1466. Not in M04 (5.28 feature). | VERIFIED |
| NEARFLG automatic for quantum tunnelling; `EXCLUDE_NEAR` on CONTACT removes an electrode from the search | M l.13699–13705, p.303; Table 3-132 l.13734, default False; M04 l.8783 | VERIFIED |
| `QTUNN.CMASS` (contact mass, default 1.0) | M l.13706–13709, p.303, Table 3-132 | VERIFIED; the deck value 1 equals the default (ASSUMED). |
| Oxide mass via `MC` or `ME.TUNNEL` on MATERIAL | M l.13711–13715, p.303 | VERIFIED |
| Lateral masses m_y, m_z in the prefactor (Eq. 3-560) = semiconductor lateral masses; for a direct gap, the DOS mass; for an indirect gap, sum over valleys (silicon 6 valleys) | M l.13476–13483, p.297; l.13495–13499, p.298 | **UNVERIFIED for IWO** (see below) |
| Tunnelling current per interface node can be written to structure files: `OUTPUT QTUNN.EL` (PP and SC) | M l.13720–13723, p.303 | Not used now; useful diagnostic (§4). |

**Lateral mass for a `user.default=silicon` material.** Nothing in the IWO MATERIAL line sets MC/ME/ML/MT. Candidate values (CALCULATED): m* = 0.2543 m0 (deck, DFT-law value); the NC-derived DOS mass (NC300/2.509e19)^{2/3} = 0.669 m0 at NC300 = 1.373e19 cm⁻³ (2.0 nm, quasi-2D override); silicon six-valley sum 2·m_t + 4·(m_t m_l)^½ = 2.055 with the inherited silicon m_l = 0.916, m_t = 0.191 (LITERATURE defaults, M l.54006–54014, p.1333). The EMPIRICAL thermal-velocity evidence (§1) shows silicon mass formulas are inherited. The prefactor could therefore differ from the m*-based value by up to log10(2.055/0.2543) = 0.91 dec (CALCULATED). This is smaller than the S2-11 mesh effect but is a systematic on every QTNLSC I_G magnitude; no printout identifies it. Resolving it needs an amendment (e.g. set MC on IWO, which may alter other inherited quantities) or a manual/vendor answer.

---

## 4. Tunnelling meshes, slices and QT-mesh controls (S2-11 non-convergence; tunnelling-mesh branch)

### 4.1 What the manuals say

1. **Step approximation.** "The tunneling probability T(E) is calculated by using a transfer matrix method … uses a stepwise approximation of the potential. Consequently, it is recommended to use a fine mesh in the tunnelling direction" (M l.13505–13507, p.298). M04 l.8700–8703: the potential is approximated as piecewise constant; best results when the oxide contains "at least several mesh points in the tunnelling direction".
2. **Atlas-built mesh: slicing is automatic.** "Everything including the direction of tunneling is determined automatically"; default slices are "locally perpendicular to each semiconductor-oxide segment on the interface"; `SHAPEOX` instead builds, from each interface node, the slice of shortest distance to the contact (M l.13660–13677, p.302). M04 l.8766–8770: SHAPEOX "will generally give a higher value" for non-planar oxides.
3. **QT mesh.** `QTX.MESH`/`QTY.MESH` create a rectangular mesh "on which all quantum tunneling is calculated. Interpolation is used to couple between this supplementary mesh and the device mesh"; tunnelling along y by default (`QTUNN.DIR` 0); "Place the QT mesh to enclose the insulator and to not overextend into the conductor or semiconductor" (M l.13665–13670, p.302). This is presented as the option for Athena/DevEdit meshes. Statement: parameters NODE, LOCATION, X, RATIO, SPACING (Table 3-130, l.13684–13691; statement l.61739–61765, p.1550: "required in some situations for the direct quantum tunneling model for gate insulators"). M04 l.8728–8757: unnecessary for a semi-classical run on a general mesh; for a non-planar oxide do not use it.
4. **How a QT mesh is read (from the BBT.NONLOCAL text, same statements):** QTX lines = parallel slices (e.g. 0.25 µm apart), QTY spacing = points along each slice (0.02/0.0005 + 1 = 41 points); "It is recommended to have as fine mesh as possible in the tunneling direction, both for the physical mesh and this tunneling mesh, so that values can be accurately interpolated between the two meshes" (M l.12724–12744, p.280–281).
5. **No point-count parameter for QTNLSC.** The manual documents `TAT.SLICEPTS` (ITAT, l.14501) and `MIMSLICEPTS` (MIM, l.14387) but no equivalent for QTNLSC (grep of the full text). `QTREGION` replaces the device mesh for non-local BBT/TAT (l.61637–61641, p.1549), not for QTNLSC. **Hence for automatic slicing the only accuracy controls are the device y-mesh in the oxide (step size along each slice, READING of item 1) and the x-mesh along y = 0 (number of slices, READING of item 2).** The manual gives no convergence criterion; the 0.1 dec rule is the register's (ASSUMED).

### 4.2 Project facts (EMPIRICAL, from the user's request file and records)
run_0062: automatic slicing OOM at the old 2 GB limit; run_0063/0064 OOM; LAA patch to 4 GB; run_0065: QT mesh flush with the oxide faces ignored ("must enclose oxide", consistent with item 3); run_0066: QT mesh 0.5 nm past both faces: slices under the pads booked to S/D and drift-diffusion currents bit-identical to the no-tunnelling run (no continuity coupling), KCL failed; run_0067: automatic slicing + `exclude_near`, KCL passed, 1.69 GB peak, 9,594 nodes (117 × 82). A QT-mesh deck *with* `exclude_near` has never been run.

### 4.3 S2-11 result pattern (COMPUTED, our ATLAS runs; file `register_scores/hc_mesh_run_0076_run_0067.json`, 75 resolved points)
- V_G ∈ [−0.45, 3] V (54 points): refined minus baseline log10|I_G| = −0.44 … −0.17 dec, median −0.35, all the same sign: a smooth systematic discretisation shift.
- V_G ∈ [−2, −0.5] V (registered floor window, 16 points): −0.49 … +2.86 dec, mixed sign; max at −0.7 V where |I_G| = 1.3e-22 (baseline) and 9.4e-20 A/µm (refined), 7.5 and 4.7 decades below the 2.0 nm floor 4.61e-15 A/µm (MEASURED/DERIVED floor, CAMPAIGN_DESIGN §7; decades CALCULATED). I_G(V_G) is non-monotonic there in both runs (e.g. baseline −2.3e-14 at −2.2 V but −7.1e-16 at −1.8 V).
- V_G ∈ [−3, −2.05] V: −0.43 … +0.33 dec; at −3 V +0.32 dec (−5.67e-12 vs −2.75e-12).

### 4.4 Why the baseline mesh cannot be expected to be converged (CALCULATED)
Decay length 1/κ = ħ/(2 m_ox m0 ΔE)^½ (CODATA constants):
- Al2O3, worst (m 0.30, ΔE = χ_IWO(2 nm) − χ_Al = 4.018 − 1.6 = 2.418 eV): 0.229 nm; nominal (0.35, 2.768 eV): 0.198 nm.
- HfO2, worst (m 0.10): 0.504 nm at the 1.5 eV TiN-side barrier, 0.682 nm at the 0.818 eV IWO-side offset; nominal (0.20, 2.2 eV): 0.294 nm.
- Oxide intervals (EMPIRICAL from run_0067 equilibrium.str, S2_PREP §6): Al2O3 0.06–0.25 nm (15 intervals), HfO2 0.24–0.99 nm (28). Largest step / (1/κ): Al2O3 1.1–1.3; HfO2 1.5–3.4 (baseline), 0.7–1.7 after ×0.5 (S2-11).
- So neither mesh puts several points per decay length in HfO2, which the step approximation needs (items 1, 4). A same-sign −0.35 dec median shift for one halving is what a first-order step error would give; under that ASSUMED error order a further halving would still move I_G by about 0.2 dec, under a second-order model by about 0.1 dec (CALCULATED: halving ratio 2 or 4).
- In a charge-free planar oxide the potential is linear in each layer (QTNLSC runs have no oxide traps), so a coarse device mesh already holds the exact potential; interpolation onto a fine QT mesh is then exact, and a QT-mesh series isolates the T(E) step error (READING + CALCULATED argument). The non-monotonic floor-window behaviour may also reflect transmission resonances in the HfO2 triangular well in front of the higher Al2O3 barrier, which a step potential resolves poorly (hypothesis, ASSUMED; not testable from the manual).

### 4.5 Inputs for the tunnelling-mesh convergence branch (manual-conformant forms only; launches need a result-informed amendment, Codex + manual check, user go)
- **(i) Automatic-slice series.** The generator's `oxide_mesh_factor` scales only the 0.002 and 0.017 µm line spacings (G:188–227, G:311); the y = 0 line stays 0.0625 nm. Factor 0.25 → Al2O3 uniform 0.0625 nm (32 intervals), HfO2 0.0625→0.25 nm (≈111 intervals; geometric grading L·ln(s2/s1)/(s2−s1)) → ≈182 y-lines × 117 = 21.3k nodes (CALCULATED). Memory at linear scaling from run_0067 (1.69 GB / 9,594 nodes, EMPIRICAL; linearity ASSUMED) ≈ 3.75 GB against the 4 GB LAA limit: high OOM risk. Factor 0.125 ≈ 35.7k nodes: beyond the ≈30k limit stated in the audit (ASSUMED). At most one more automatic-slice halving is affordable; an OOM is UNRESOLVED under A41(d) rules.
- **(ii) QT-mesh series as I_G magnitude cross-check.** Existing generator form `gate_tunnelling.qt_mesh=1` (G:206, G:419–427) emits `qtx.mesh loc=0/xox spac=<slice>` and `qty.mesh loc=-dyq … tox+dyq spac=dyq` (encloses the insulator by one point, consistent with item 3). Series: QTY 0.5 → 0.25 nm (→ 0.125 nm), QTX 0.2 → 0.1 µm, device mesh fixed. Per run_0066 the QT-mesh current did not couple into continuity in this build, so these are post-processing-like I_G values: KCL will fail by |I_G| and the frozen scorer cannot use them without an amendment. With `exclude_near` the pads issue is gone but coupling is still UNVERIFIED.
- **(iii) SHAPEOX** at the run_0067 mesh: for a planar stack the slices coincide with the default except at the x ends, so a large change would implicate the slicing, not the physics (one launch, run_0067 cost ≈ 1,250 s, EMPIRICAL).
- **(iv) Diagnostics without new physics:** `OUTPUT QTUNN.EL` (current density per interface node, l.13720–13723) to see slice-to-slice smoothness; record node and slice counts from deckbuild.out ("Total grid points", EMPIRICAL run_0067 l.206).
- **(v) FNORD (S2-09/10)** as the mesh-robust FN-regime magnitude check (§2), already in the matrix.
- What each outcome can claim: a converged QT-mesh series bounds the T(E) step error of the worst-set I_G only (not self-consistent, not KCL-closed); an automatic-slice pass at factor 0.25 certifies only run_0067's settings (A41 scope rule); FNORD agreement within its single-barrier limit supports the magnitude in the FN regime only.

---

## 5. ITAT.SC.EL with DOPING TAT.TRAP, ^TAT.POISSON, TAT.SLICEPTS (S2-12 2.0 nm, S2-13 13.2 nm)

Deck text (S2-12): `doping region=4 uniform tat.trap conc=1e+19 acceptor sign=1e-13 sigp=1e-13 e.level=1`; `models fermi srh temp=300 print qtnlsc.el qtnl.derivs itat.sc.el ^tat.poisson`; QTNLSC nominal-set lines as S2-04. No `tat.slicepts`.

| Item | Manual | Verdict |
|---|---|---|
| ITAT.SC.EL self-consistent (current injected into the semiconductor continuity equations); ITAT.PP.* post-processing | M l.14505–14512, p.322–323; Table 3-139 l.14714–14732, p.326 | VERIFIED |
| `DOPING … TAT.TRAP` with ACCEPTOR, SIGN, SIGP, E.LEVEL | Example `DOPING REGION=2 UNIFORM TAT.TRAP CONC=1E16 ACCEPTOR SIGN=1E-14 SIGP=1E-14 E.LEVEL=4.2` (l.14711–14712, p.326); TAT.TRAP "must be located in an insulator or wide bandgap semiconductor quantum barrier" (l.49688–49689, p.1202); E.LEVEL for acceptors relative to Ec (l.49683–49684); SIGN/SIGP cm² (l.49268–49269) | VERIFIED: e.level=1 = 1.0 eV below the HfO2 Ec as the design says. |
| `^TAT.POISSON` (default TAT.POISSON = True) | M l.14545–14549, p.323; l.14729; example `MODELS RTAT.SC TAT.SLICEPTS=21 ^TAT.POISSON` (l.14745, p.327); not allowed in transients (l.14562–14564) | VERIFIED (DC only here) |
| `TAT.SLICEPTS` (default 12) | "control the number of interpolated mesh points on each slice through the oxide … This number should be chosen so that the calculated currents are largely unchanged if one uses a slightly higher or lower value" (M l.14499–14505, p.322); default 12 (l.14730) | **ISSUE:** the manual itself requires this check. With 12 points over 17 nm ≈ 1.4 nm per point (CALCULATED), i.e. 1–2 points in the 2 nm Al2O3. A41(d) already records ITAT convergence as UNRESOLVED without its own amendment; the form of that amendment is a TAT.SLICEPTS pair (e.g. 12 vs 24) on S2-12 or S2-13. |
| Geometry: "requires an electrode on one side of the oxide and a semiconducting channel on the other. It automatically detects the gate oxide and sets up a QTREGION automatically" | M l.14497–14500, p.322 | **UNVERIFIED for a bilayer** (traps only in region 4, Al2O3 between channel and traps). If only the semiconductor-adjacent insulator is treated, ITAT current would be zero; the parser's matched-control test (P:211–234) then gives NOT_ACTIVE, which is the right outcome. |
| Mass in the capture rate b_L (Eq. 3-590): "m* is the effective mass" | M l.14422–14425, p.321 | UNVERIFIED which parameter (probably the insulator ME.TUNNEL). |
| `TAT.LOCAL`: "The tunneling model assumes by default that tunneling is into a crystalline semiconductor. If the semiconductor has localized energy states in the mobility gap, as is the case with amorphous semiconductors, you can enable the TAT.LOCAL flag … to include tunneling to localized energy states as defined on the DEFECTS statement" | M l.14600–14603, p.324 | **ISSUE (model form):** S2-12/13 omit TAT.LOCAL, so trap-to-tail-state transitions in the amorphous IWO are excluded. The null result is conditional on that; state it, or register a TAT.LOCAL variant (amendment). |
| Convergence aids: TAT.NLDERIVS, TAT.NLCURRS, smaller METHOD DVMAX | M l.14652–14657, l.14672–14679, p.325 | Not emitted; fallback only by amendment. |
| Per-slice logs: `SOLVE … ITAT.FILE=<stem>` (one log per slice; last bias of a ramp) | M l.14691–14706, p.325–326 | Optional diagnostic: gives the ITAT slice count. |

---

## 6. IGZO.TOKYO on a user material (S3-11…S3-16, S3-27)

Deck text (S3-12): `mobility material=IWO igzo.tokyo mun=40.2606 mup=0.01 tmun=0 tmup=0 igzo.gamma0=-0.31 igzo.tgamma=178.4 igzo.ncrit=1e+20`, before `solve init` (G:251–255, G:441). S3-27: MATERIAL and MOBILITY mun both 24.1564, Q_f 2.38345e12.

| Item | Manual | Verdict |
|---|---|---|
| μ_n(T,N) = μ_n0(T)·(N/IGZO.NCRIT)^{γ/2}, γ = IGZO.TGAMMA/T + IGZO.GAMMA0, μ_n0 = MUN·(T/300)^{−TMUN}; N = electron concentration; electrons only; holes μ_p = MUP·(T/300)^{−TMUP}; enabled on MOBILITY | M l.8200–8218, p.195 (Eqs. 3-263…3-266) | VERIFIED |
| Defaults: GAMMA0 −0.31, TGAMMA 178.4 K, NCRIT 1.0e20 cm⁻³; **MOBILITY MUN 15.0, TMUN 1.5**, MUP 0.1 | Table 3-61, l.8250–8262, p.196; MOBILITY list l.56850–56857, p.1411 | VERIFIED. Not in M04. |
| MUN/TMUN interplay as the design assumes | — | VERIFIED by construction: the generator restates mun/tmun on the MOBILITY line (avoids the MOBILITY default 15/1.5); at T = 300 K, (T/300)^{−TMUN} = 1 for any TMUN (CALCULATED), so TMUN only matters for temperature predictions; I ∝ MUN holds because μ = MUN·f(n) (design §5.2), and S3-27 scales both MUN statements together. |
| `MOBILITY MATERIAL=` scope | "Specifies which material from Table B-1 should be applied" (l.57136–57138, p.1420); `REGION=` "number of the region" (l.57152, p.1421) | **UNVERIFIED** for the user material name IWO. Documented fallback: `mobility region=1 …` and `mobility region=2 …`. |
| Numbers | γ = 0.5947 − 0.31 = 0.2847 and 0.5947 + 0.30 = 0.8947 (CALCULATED). Mobility factor (n/1e20)^{γ/2} at n = 1e19 / 1e16 / 1e12 cm⁻³: 0.721 / 0.270 / 0.0727 (γ 0.285) and 0.357 / 0.0162 / 2.6e-4 (γ 0.895) (CALCULATED). | The γ 0.895 case drives μ to ~1e-4·MUN in depletion: possible convergence stress (ASSUMED risk). |

**First launch (S3-12 or the first IGZO run):** REGIONAL MOBILITY MODEL SUMMARY must name the IGZO model for electrons in **regions 1 and 2** with mu = MUN and tmu = 0 (format: EMPIRICAL run_0074 deckbuild.out l.383–391 shows "Concentration Independent Mobility / mu / tmu"). The parser reads region 1 only (P:150–159): region 2 by hand.

---

## 7. Schottky Pd source/drain (S3-17…S3-23)

Deck text (S3-17, 2.0 nm, 0.2 eV): MATERIAL `arichn=30.558`; `contact name=source workfun=4.21839 surf.rec barrier e.tunnel me.tunnel=0.25429 ^ins.ohmic` (drain same); top y.mesh 0.1 nm at y = −t. S3-23: no `barrier`.

| Item | Manual | Verdict |
|---|---|---|
| `WORKFUN` (absolute work function, V/eV; default 0); φ_bn = WORKFUN − AFFINITY | CONTACT l.48044, l.48097–48099, p.1152/1156; Eqs. 3-176…3-180 l.6400–6470, p.158–159 | VERIFIED. CALCULATED workfun = χ(t) + φ_B: 4.2184 / 4.4378 / 4.4765 eV (0.2 eV) and 4.5184 / 4.7378 / 4.7765 eV (0.5 eV) for 2.0/6.3/13.2 nm (χ CALCULATED from LITERATURE χ_bulk 4.3 eV and the FITTED DFT ΔE_c law). |
| Thermionic BC enabled by SURF.REC, E.TUNNEL, VSURFN, VSURFP or BARRIER; J_sn = q·VSURFN·(n_s − n_eq) | M l.6404–6415, p.158; l.6427–6440, p.159 | VERIFIED |
| Default VSURFN = ARICHN·T_L²/(q·NC) | M l.6436–6447, p.159; CONTACT l.48205–48219, p.1159 (Eq. 22-1) | **ISSUE (consistency, 2.0 nm only).** CALCULATED with ARICHN 30.56 A cm⁻²K⁻², T 300 K: NC 1.373e19 (quasi-2D override) → 1.25e6 cm/s; NC 3.218e18 (3-D formula, m* 0.2543) → 5.335e6 cm/s = (kT/2πm*)^½ (CALCULATED). The quasi-2D NC lowers the contact recombination velocity ×0.234 at 2.0 nm only. Either state it, or set `VSURFN` explicitly (amendment). |
| `ARICHN` on MATERIAL, A/cm²/K² (defaults 110 / 30 for silicon) | Table 3-32 l.6449–6455, p.159; MATERIAL l.53398, p.1314 | VERIFIED. CALCULATED 120.17·m*(t) = 30.56 / 26.31 / 25.51 (120.17 ≈ 4πq m0 k²/h³, CODATA). |
| `BARRIER`: Δφ_b = BETA·(qE/(4πε))^½ + ALPHA·E^GAMMA; defaults ALPHA 0 cm, BETA 1, GAMMA 1; E = field magnitude at the interface; default form changes the current via exp(Δφ_b/kT) but not the contact potential (ALT.BARRIER does) | M l.6470–6492, p.160, Table 3-33; CONTACT l.47936–47967, l.48100–48112 | VERIFIED (ε symbol garbled in the text extraction; READING: semiconductor permittivity). **ISSUE:** CALCULATED with ε = 9.3 (MEASURED): Δφ = 0.039 / 0.124 / 0.201 / 0.216 eV at E = 0.1 / 1 / 2.6 / 3 MV/cm. A 0.2 eV barrier is fully cancelled at ≥ 2.6 MV/cm; the gate-induced field in a 2 nm film under the pads can be of this order at +3 V (oxide field ≈ 3.4 MV/cm at 3 V across the stack, audit §7.5, ASSUMED full drop). No cap Δφ_b ≤ φ_b is documented: UNVERIFIED. |
| `E.TUNNEL` (also enables SURF.REC), `ME.TUNNEL` (CONTACT, relative mass, default 1.0); Tsu–Esaki with WKB for a triangular barrier using the interface field | CONTACT l.47950, l.47993, l.48116–48118, l.48155–48156, p.1152–1158; M l.6493–6530, p.160–161; example `CONTACT NAME=GATE SURF.REC E.TUNNEL BARRIER` (p.161) | VERIFIED. Note: a triangular-barrier WKB at the contact is an approximation for a 2 nm film (ASSUMED limitation). |
| `INS.OHMIC` exists: Logical, default True; "contacts which connect to both semiconductor and insulator regions will be treated as ohmic" | CONTACT l.47988, p.1152; l.48153–48154, p.1158. Absent from M04 (5.28-only). | VERIFIED: `^ins.ohmic` is required because the Pd volumes touch Air (deck geometry). |
| Printout | EMPIRICAL: the Contacts table prints only name, work function and lumped elements (run_0067 deckbuild.out l.437–442) | SURF.REC/BARRIER/E.TUNNEL/INS.OHMIC activation is not printed: the parser can confirm only the work function (P:163–174). Behavioural check needed (I_on change against the ohmic baseline; S3-23 vs S3-21 isolates BARRIER). |

---

## 8. BQP (S3-24 m 0.139, S3-25 m 0.2543; both 2.0 nm, DFT shifts off)

Deck text (`sample_decks/extra/S3-24_c10_s3_24_2p0.in`): MATERIAL `ml=0.139 mt1=0.139 mt2=0.139`; `models fermi srh temp=300 print bqp.n bqp.ngamma=1.2 bqp.nalpha=0.5 bqp.qdir=2`; METHOD unchanged (`method newton trap …`); no `bqp.newton`, `freezebqpni`, `nocurrent` (G:257–263).

| Item | Manual | Verdict |
|---|---|---|
| BQP.N; BQP.NGAMMA default 1.2, BQP.NALPHA 0.5, BQP.QDIR 2 (y); QDIR has no effect for spherical bands | M l.34754–34793, p.839–840, Table 14-3; also on MATERIAL (Table 14-7, l.34925–34934, p.844) | VERIFIED. With ml = mt1 = mt2 the bands are spherical, so QDIR is irrelevant (consistent). |
| Mass: Q contains "the inverse effective mass tensor" | M l.34728–34731, p.839; the tensor from MT1, MT2, ML is defined for the Schrödinger solver (l.34436–34438, p.833); silicon defaults ML 0.916, MT1/MT2 0.191 (l.54006–54014) | UNVERIFIED that BQP reads ML/MT1/MT2 (design already says so). |
| Iteration: "The iteration scheme uses a modified version of BLOCK … (although NEWTON and GUMMEL are ignored, BLOCK is always used if the BQP model is set)" | M l.34845–34848, p.842 | **ISSUE:** the decks' `method newton trap … xandrnorm cr.toler` are not the scheme that runs. Alternative documented form: `METHOD BQP.NEWTON` (allowed with BQP.N alone), then `FREEZEBQPNI` on subsequent SOLVEs because BQP.NEWTON modifies n_i (l.34747–34753, p.839); `NOCURRENT` on the first SOLVE after INIT to speed convergence (l.34858–34860, p.842). Choose one and register it (amendment). |
| FD + BQP convergence "can be poor for very high carrier densities"; BQP.NOFERMI needs recalibration | M l.34851–34857, p.842 | Risk at 2 nm accumulation (n ≈ 5.6e19 cm⁻³ at 2 V overdrive, design D15, CALCULATED there). |
| BQP automatically computed in insulators; applied globally, not per region | M l.34897–34906, p.843 | Note only (IWO is the only semiconductor). |
| γ/α calibration: compare with Schrödinger–Poisson at CARRIERS=0 | M l.34800–34830, p.841 | The 1.2/0.5 values are the generic defaults (LITERATURE, silicon-oriented); for IWO they are ASSUMED, so the BQP test is conditional on them. |

Printout: no documented BQP activation string; the parser returns UNVERIFIED by design (P:176–181). Hand-read deckbuild.out for a BQP/Bohm line, the iteration scheme used, and the printed ml/mt values.

---

## 9. Boltzmann (S3-26: `models srh temp=300 print`)

M l.3757–3766, p.109: Boltzmann statistics "are the default in Atlas"; FERMIDIRAC (alias `fermi`) on MODELS switches to Fermi–Dirac. VERIFIED. The flags table prints `Boltzmann` and `Fermi-Dirac` rows (EMPIRICAL, run_0074 deckbuild.out l.378–379), so the parser check (P:144, P:147) is valid. DEFECTS occupancy uses its own trap statistics (TFT chapter) whatever the carrier statistics (READING).

## 10. DEFECTS placement: bulk / 50:50 / none (S3-04…S3-10)

- DEFECTS applies per region (`NUMBER or REGION`, M l.48709–48720, p.1173); NTA in cm⁻³eV⁻¹, WTA in eV (l.48753, l.48789); CONTINUOUS (l.48803). VERIFIED.
- All variants write the **same NTA into region 1 (bulk) and region 2 (0.25 nm interface layer)**; "surface", "bulk" and "50:50" are thickness laws for a spatially uniform tail, not spatial placements (deck_diffs S3-10; G:182–185). A spatial surface placement would be a different DEFECTS layout (supported by REGION; not registered).
- CALCULATED NTA (N_s 4e12 cm⁻² FITTED start, W_T 0.04 eV): surface N_s/(t·W_T) = 5.0e20 / 1.587e20 / 7.58e19; bulk 2e19/0.04 = 5.0e20 at all films; 50:50 ((N_s/2)/t + 1e19)/0.04 = 5.0e20 / 3.29e20 / 2.88e20 cm⁻³eV⁻¹ (2.0/6.3/13.2 nm). At 2.0 nm the three are identical: S3-04 and S3-07 are solver-identical to S0-01 (S3-07: only comment lines differ, diff of `sample_decks/extra/S3-07…in` against `S0-01…in`). Already registered as duplicates (HYPOTHESIS_REGISTER l.2164): 2 launches to save.
- None (S3-10, 6.3 nm): `nta=0` in both regions; NTA is Real with no stated lower bound (VERIFIED syntax); the deep Gaussian and the region-2 D_it Gaussian remain.

## 11. Ungated strip deck (S2-14…S2-17; `s2_prep_decks/S2-14_c10_s2_14_13p2_strip.in`)

- Only existing statements (MESH, REGION, ELECTRODE, DOPING, MATERIAL, MODELS, DEFECTS, INTERFACE, METHOD, PROBE, SOLVE, LOG, SAVE, EXTRACT). No gate region/electrode/contact. VERIFIED by deck_diffs [10]–[13].
- Outer non-contact edges are homogeneous (reflecting) Neumann boundaries (M l.6988–6990, p.170): the "domain ends at the HfO2 bottom" comment is correct. Consequence (READING): without a gate the Q_f sheet at y = 0 must be compensated inside the film or by the distant Pd contacts, which is why Q_f-on and Q_f-off strips (S2-16/17 `interface qf=0`) differ.
- `solve vstep=0.05 vfinal=0.1 name=drain` then `vstep=0.1 vfinal=0.7` from 0 V; both 0.1 and 0.7 V are logged (generator enforces them, G:146–154). VERIFIED form.
- Nothing in the manual contradicts the design. The in-solver strip (S6-27) relies on `material region=<n> mun=` for a user-material region and on same-name electrodes; region MATERIAL is VERIFIED for built-in materials (audit 7.11 B), user-material case UNVERIFIED (already flagged).

---

## 12. Required wording/design changes found by this check (no file changed)

1. CAMPAIGN_DESIGN §3/§1 and matrix purposes: "TRAP.TUNNEL + TRAP.HURKX" → "TRAP.TUNNEL, enhancement applied to R/G only (TRAP.HURKX)"; report the generation bound as σ·v_n with v_n = 1.08e7 cm/s (EMPIRICAL silicon value), or register `M.VTHN`.
2. S2-12/13: state "no TAT.LOCAL: tunnelling into IWO band states only"; ITAT stays UNRESOLVED until a TAT.SLICEPTS pair is registered (manual l.14501–14505).
3. S3-24/25: register the BQP iteration form (BLOCK as now, or BQP.NEWTON + FREEZEBQPNI + NOCURRENT) before launch; label BQP γ/α as ASSUMED defaults.
4. Schottky 2.0 nm: state or fix the quasi-2D NC effect on the default VSURFN (×0.234); report whether Δφ_b ≥ φ_B at the contact field.
5. IGZO: keep `material=IWO`, but pre-register the fallback `region=1`/`region=2` if the summary shows "Concentration Independent Mobility".
6. Tunnelling mesh: the branch needs an amendment that names the QT-mesh I_G as non-self-consistent (KCL waiver in scoring) and caps automatic-slice refinement at factor 0.25 with OOM → UNRESOLVED.
7. S3-04 and S3-07 (2.0 nm) are duplicates of S0-01: reuse S0-01 (already in the register).

## 13. First-launch confirmation list (deckbuild.out, by hand where the parser is blind)

| Run | Must show | Parser covers? |
|---|---|---|
| S2-01 / S2-03 | flags SRH T, tat(local) T, bbthurkx F; `mass.tunnel` 0.2123 / 0.2543; taun0/taup0 1e-9; METHOD echo `carriers=2`; any TRAP.HURKX message | tat(local), SRH only |
| S2-02 | SRH F; σ 1e-20 echoed; carriers=2 | SRH only |
| S2-04/06/08 | as run_0067: no warnings; Itnl(S/D) = 0; In_S + In_D = −Itnl(gate); node count | I_G non-zero only |
| S2-09/10 | I_G non-zero, sign as QTNLSC; `ifnvg.dat`; FN-plot slope −F.BE | I_G, ifnvg presence |
| S2-12/13 | ^tat.poisson echoed; I_G differs from the matched control; TAT.SLICEPTS = 12 (default) recorded | yes, with --gate-control |
| S2-14…17 | no gate in Contacts; I(0.7)/I(0.1) | strip metrics |
| S3 IGZO | IGZO model named for electrons in regions 1 **and 2**; mu = MUN; tmu = 0 | region 1 only |
| S3 Schottky | Contacts work fn = values in §7; material arichn; on-current change vs ohmic; S3-23 vs S3-21 for BARRIER | work function only |
| S3 BQP | BQP/Bohm line; scheme (BLOCK/BQP.NEWTON); ml/mt printed; convergence at the strict window | UNVERIFIED by design |
| S3-26 | Boltzmann T, Fermi-Dirac F | yes |
