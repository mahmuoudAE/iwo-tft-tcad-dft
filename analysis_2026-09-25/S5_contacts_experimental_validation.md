# S5: Contact effects, series resistance and experimental validation design

Scope: contact and series resistance, Pd/IWO injection, access through the film, and which missing measurements break which degeneracies. Scripts and outputs are in `analysis_2026-09-25/scratch/S5/`: `s5_yfunction.py` → `s5_results.json` and `s5_yfunction_stdout.txt`; `s5_checks.py` → `s5_checks_stdout.txt`; `s5_plot.py` → `s5_yfunction_hfunction.png`. Constants come from EVIDENCE_BRIEF §1: Cox 8.955e-7 F/cm², L 20 µm, Vd 0.7 V, and the Vth_lin values in the §2 table.

## 0. Bottom line
1. **Contact or series resistance cannot explain the thickness dependence.** To explain the Ion gap between 2 and 13.2 nm, 2 nm would need Rsd·W ≈ 1.15e6 Ω·µm. That requires ρc ≈ 0.26 Ω·cm² and L_T ≈ 45 µm (longer than L), and it would drop 0.58 V of the 0.7 V Vd across the contacts. The Rc it implies is about 5700× the TLM bound for metal/In2O3 (NatElec2022: < 0.1 Ω·mm). The measured 2 nm curve also shows the opposite of an Rsd signature: gm is still rising at +3 V and the net Y-function θ is negative.
2. **The Y-function cannot extract Rsd from these curves (2, 6.3 and 13.2 nm).** All three films are net supralinear: the threshold-free H-function exponent is α_H = 1.59, 2.14 and 1.29, and θ_net = -0.10, -0.12 and -0.046 V⁻¹. Ideal-contact ATLAS runs with constant μ_band reproduce a negative θ (-0.04 to -0.06 V⁻¹). When the tail exponent and θ are fitted together they are perfectly correlated (r = +1.00), so Rsd is **not identifiable from one ID-VG curve at one L**.
3. **Upper bounds on Rsd hold only within the model.** Using the calibrated trap model (runs 0012/0013), no positive Rsd is needed. Rsd·W ≲ 5e4 Ω·µm at 2 nm (≲ 4 % of R_on) and ≲ 1-2e4 Ω·µm at 13.2 nm (≲ 4-9 %). These are calibration-class bounds.
4. **The paper-vs-workbook mobility mismatch is resolved.** Applying the *saturation* formula μ = (2L/WCox)(d√Id/dVg)²_max to the workbook curves (at Vd = 0.7 V) gives **5.09 and 27.40 cm²/Vs**. The paper quotes 5.1 and 27.4. So the workbook curves are the paper's thickness-series devices, and the paper's μ is a saturation-formula peak taken near threshold, not a linear-regime μ_FE. The same method predicts **3.86 cm²/Vs** for 6.3 nm, which can be checked against Januar Fig. 5a.
5. **run_0027 (the "overlap 4 µm" run) is malformed.** ATLAS truncated the drain to a zero-width line. The run does not test overlap, and with ideal-Ohmic boundaries the model cannot represent ρc in any case.

## 1. Task 1: On-resistance and Y-function from `data/experimental_clean.csv`

On-resistance: R_on·W = Vd/Id(3 V) = **1.38e6** (2.0 nm), **1.74e6** (6.3), **2.28e5** (13.2) and **1.95e5 Ω·µm** (31.8), with Id from brief §2.

Method: gm is the central difference; the Savitzky-Golay derivative agrees within 2 %. Y = Id/√gm gives μ0 from the slope. θ comes from a direct fit, Id = A²(Vg−V*)/(1+θ(Vg−V*)). α_H comes from the Cerdeira H-function, H = ∫Id dVg/Id, whose slope is 1/(α+1) and needs no threshold. The main window is Vg ≥ Vth_lin + Vd, so the device is in the linear regime at Vd = 0.7 V. The ranges quoted span windows shifted by ±0.2 V and both gm methods.

| film | window (V), pts | μ0_Y (cm²/Vs) | θ_net (V⁻¹) | Y curvature | α_H (GCA baseline) | R_sh at source, 3 V (Ω/□) | Rsd·W bound, θ0 = 0 |
|---|---|---|---|---|---|---|---|
| 2.0 | 2.40-3.00, 13 | 8.8 (8.0-8.9) | −0.100 ± 0.007 (−0.10…−0.13) | +0.04…+0.15 | 1.59 (1.55-1.71) vs ≈1.1-1.2 | 8.2e4 | none: θ < 0 |
| 6.3 | 2.55-3.00, 10 | 7.9 (5.7-8.0) | −0.12…−0.20 | +0.30…+0.39 | 2.14 (2.14-2.23) vs ≈1.1-1.3 | 1.0e5 | none: θ < 0 |
| 13.2 | 1.75-3.00, 26 | 41.2 (39.2-41.9) | −0.046 ± 0.002 (−0.042…−0.061) | +0.04…+0.10 | 1.29 (1.27-1.35) vs ≈1.05-1.13 | 1.26e4 | none: θ < 0 |
| 31.8 | −0.20-3.00, 65 | Y invalid (154-217) | +0.17…+0.28 (Id fit, μ0 52-67) | +1.6…+2.0 | ≈1.0 | ~5e3 | ≤ 7.5e4-9.4e4 (38-48 % of R_on) |

Method check on ideal-contact ATLAS runs (Rsd = 0, constant μ_band), same windows:

| run | μ0_Y (cm²/Vs) | μ0_Y/μ_band | θ (V⁻¹) | α_H |
|---|---|---|---|---|
| run_0012 (2 nm) | 9.2-9.9 | 0.53 | −0.045…−0.070 | 1.35-1.46 |
| run_0015 (6.3 nm, tuned) | 6.6-7.1 | 0.58 | −0.054…−0.077 | 1.34-1.42 |
| run_0013 (13.2 nm) | 41.5-43.0 | 0.68 | −0.032…−0.047 | 1.23-1.28 |

With no contact resistance and no field-dependent mobility, trap filling alone produces negative θ and upward Y curvature. In these films the Y-function μ0 underestimates the band mobility by 1.5-1.9×, so μ0_Y is a free-fraction-weighted effective mobility, not an intrinsic one.

Measured θ minus ATLAS θ is −0.044 (2 nm), −0.053 (6.3 nm) and −0.010 V⁻¹ (13.2 nm). Every residual has the sign opposite to Rsd.

**Rsd is not significant at 2, 6.3 or 13.2 nm, but only within the model.** A forward check (gradual-channel model plus Rsd, `s5_checks.py`) shows what an Rsd would do. With Rsd·W = 9.2e4 Ω·µm, a 13.2-nm-like device loses 27 % of Ion, α_H falls by 0.25, and the IR drop is 0.19 V. A 2-nm-like device loses 5 % of Ion and α_H falls by 0.06. The measured 13.2 nm α_H is the model value plus 0.04 ± 0.04, which gives the bound Rsd·W ≲ 1-2e4 Ω·µm (≤ 4-9 % of R_on). The 2 nm bound from window scatter (Δθ ≈ 0.02 V⁻¹) is Δθ/β ≈ 5e4 Ω·µm (≤ 4 %).

**Where the Y-function is invalid:**
- **Near threshold.** For Vg < Vth_lin + Vd (2.36 / 2.52 / 1.74 V) the device is in saturation at Vd = 0.7 V. This leaves only 9-17 usable points at 2 and 6.3 nm.
- **Trap-limited films.** Throughout 2 and 6.3 nm, and weakly at 13.2 nm, the free fraction still rises at +3 V, so μ depends on Vg (α > 1 and θ < 0).
- **At 31.8 nm.** gm has two maxima (−0.3 V and ~+0.8 V; see figure), which indicates two parallel conduction paths, and the Y curvature is ≥ 1.6. The positive θ there cannot be assigned to contacts.
- **Tail exponent and θ are degenerate.** In a 4-parameter fit Id = K·Vov^α/(1+θVov), the correlation between α and θ is +1.00 in every window and every film. Examples: 2 nm α = 1.64 ± 0.86 with θ = +0.12 ± 0.47; 13.2 nm α = 1.44 ± 0.14 with θ = +0.10 ± 0.07, versus α = 1.14 ± 0.09 with θ = −0.005 ± 0.03 in the next window.

## 2. Task 2: Contact physics

**Pd/IWO injection.** In2O3 has its charge-neutrality level (CNL) about 0.4 eV above Ec (Si2021 l.248; NatElec2022 l.376-380; Wang2022 l.94). Metal/In2O3 contacts are therefore pinned Ohmic-like:
- NatElec2022 (Ni on ALD In2O3, TLM): Rc < 0.1 Ω·mm = 100 Ω·µm "even at the nanometre scale", and < 0.08 Ω·mm at Tch 2.5 nm. A Schottky signature in the output curves appears only for Tch < 1 nm (l.366-369, 540-548).
- Lin2022: Rc < 70 Ω·µm (l.196-197).

All of this is **related-material evidence: Ni on ALD In2O3, not Pd on sputtered IWO.** No local source measures Pd/IWO. The Pd work function (handbook ~5.1-5.6 eV; not in the local literature) matters only if the IWO interface is unpinned: NOT DETERMINED.

**Transfer length and contact fraction.** L_T = √(ρc/R_sh), with R_sh from the table above and overlap L_ov = 2 µm (not reported). The contact fraction is 2Rc/R_on, with Rc = √(ρc·R_sh)·coth(L_ov/L_T):

| ρc (Ω·cm²) | L_T at 2 / 6.3 / 13.2 nm (µm) | 2Rc/R_on at 2 / 6.3 / 13.2 nm |
|---|---|---|
| 1e-6 | 0.035 / 0.031 / 0.089 | 0.4 % / 0.4 % / 1.0 % |
| 1e-5 | 0.11 / 0.10 / 0.28 | 1.3 % / 1.2 % / 3.1 % |
| 1e-4 | 0.35 / 0.31 / 0.89 | 4.2 % / 3.7 % / 10 % |
| 1e-3 | 1.1 / 0.98 / 2.8 | 14 % / 12 % / 51 % |

For L_ov ≫ L_T the contact fraction is ≈ 2L_T/L ∝ R_sh^−1/2. At fixed ρc the *thick* film therefore pays about 2.5× more (√(8.2e4/1.26e4)). A thickness-independent contact would *compress* the 2 vs 13.2 nm difference, not create it.

**What would be needed.** To explain the gap, 2 nm would need Rc ≈ 5.7e5 Ω·µm per contact, i.e. ρc ≈ 0.26 Ω·cm² (L_T ≈ 45 µm). That is about 2600× larger than the ρc that would already cost 13.2 nm about 10 %. It is also 5700× the literature Rc.

**Access through the film (staggered top contact).** The vertical specific resistance is ρ·t:
- 2 nm, accumulated: 3.3e-9 Ω·cm² (n_avg 4.4e19 cm⁻³).
- 13.2 nm, accumulated average: 2.2e-8 Ω·cm².
- 13.2 nm, neutral top layer (Nd_eff 2.97e17 cm⁻³, μ 61.9; both FITTED): 4.5e-7 Ω·cm².

All of these are below 1 % of R_on, and the trend runs the wrong way (it grows with t). Access resistance would matter only if the film between the Pd and the channel were fully depleted. That cannot happen under a gated overlap. Whether the gate extends under the S/D is NOT DETERMINED.

**Current crowding at 2 nm.** For ρc ≤ 1e-4 Ω·cm², L_T ≤ 0.35 µm, so Rc does not depend on overlap. Crowding matters only above ~1e-3 Ω·cm².

**ATLAS run_0027 is not an overlap test.** Its deck extended the regions and electrodes to x = 28 µm but left `x.mesh` ending at 24 µm. From `deckbuild.out` l.166-204, ATLAS shortened the gate to 0-24 µm and the source to 0-3.905 µm, and collapsed the drain to a zero-width line at x = 24 µm (15 nodes) that touches the IWO only at a corner. So:
- The −2.15 % Ion (RUN_INDEX) reflects a slightly different L (20.1 µm) plus a point drain contact, not a 4 µm overlap.
- It does show that an ideal-Ohmic boundary carries **no** contact resistance, even through a single node.
- The model's μ_band(t) therefore lumps in any real Rsd (Id is exactly linear in μ_band; brief §4).

**The 31.8 nm series resistance (V0: 9.2e4 Ω·µm total; `..\IWO_ATLAS_Model_claude\docs\PARAMETERS_AND_PROVENANCE.md` l.72).** The Id-fit bound on the same curve (≤ 7.5-9.4e4 Ω·µm) is consistent with it. That is two readings of one curve, not validation. If a contact of that size were thickness-independent, 13.2 nm would show θ_sd ≈ +0.17 V⁻¹, −27 % Ion and α_H lower by 0.25. None of these is observed: θ_net is −0.046, and run_0013 reproduces α_H with Rsd = 0. Therefore the 31.8 nm gm roll-off is either specific to the thick film (two-channel conduction; S1) or is not a contact effect.

## 3. Mechanisms, points (a)-(f)

**M1: Thickness-independent Rsd causes the Ion/μ_FE(t) trend.** (a) Penalty ∝ R_sh^−1/2, hurting thick films more. (b) Needs ρc = 0.26 Ω·cm²; falls short by 5700× in Rc, or needs 83 % of Vd dropped at the contacts. (c) Predicts gm roll-off, θ > 0, Ion ∝ L⁰, μ_FE ∝ L. (d) Observed: 2 nm gm_max at 3.00 V and still rising; θ < 0 in all films. (e) For: 13.2 nm gm plateau (max 2.80 V, −2 % at 3 V); 31.8 nm roll-off. Against: (d) and §1. (f) Correlation plus model-conditional bounds.

**M2: Confinement-raised contact barrier (Ec rising toward the pinned CNL).** (a) Δφ_B ≈ dEc(t) − (E_CNL − Ec); ρc ∝ exp(qΔφ_B/kT). (b) A ρc ratio ≥ 2600 needs Δφ ≥ kT·ln 2600 = 0.20 eV. The model's dEc(2) − dEc(13.2) = 0.33 eV (DFT proxy ±50 %), so this is possible only if IWO's CNL margin is ≤ 0.15 eV (In2O3: 0.4 eV) or dEc(2 nm) ≥ 0.6 eV. (c) Predicts S-shaped ID-VD near Vd = 0, activated Rc (Ea ≈ φ_B), and an effect confined to 2 nm (dEc(6.3) = 0.07 eV). (d) **Contradicted by the pattern:** Ion(6.3) = 0.79·Ion(2) and μ_FE(6.3) < μ_FE(2). (e) For: supralinear 2 nm Id (a gate-modulated barrier also gives this). Against: (d); NatElec2022 sees Schottky behaviour only below 1 nm. (f) None.

**M3: Vertical access** (ρ·t ≤ 5e-7 Ω·cm², grows with t) and **M4: current crowding** (smallest L_T/L at 2 nm): both rejected as thickness mechanisms. **M5: θ attenuation (Rsd + Januar θr):** θ_net < 0 everywhere and no roll-off at 2 nm within +3 V; θr, Rsd and the tail exponent are degenerate on one curve (not determined; shared with S2).

## 4. Task 3: Identifiability matrix

Key: **B** = breaks the degeneracy; P = partial (needs another column); – = no leverage.

| ambiguity \ measurement | C-V per t (QS + multi-f) | T series (≥ 3-4 T) | ID-VD | dual-sweep hysteresis | vacuum/air/passivated | IG + IS | TLM / gated 4-probe | XPS/RBS W | XRR/ellipsometry t ± σ | optical gap vs t | replicates (N ≥ 3-5) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| charge location: front / back / bulk | **B** (V_FB(t): front is t⁰; back or bulk add t/εs and t² terms) | P | – | P (border traps) | **B** for back surface | – | – | P (donors) | P | – | P |
| confinement dEc vs t-dependent fixed charge | P (gives the sum Φ_MS(t) − Qf/Cox; shape in t helps) | P (Ea of Ioff → Ec − EF) | – | – | P | – | – | P (XPS EF − Ev) | P (dEc ∝ t^−1.38) | **B** | P |
| μ_band vs Nt / WTA | **B** (QS C-V: n_total(Vg); with Id → free fraction) | **B** (activated μ_FE(Vg,T) vs phonon-like) | P | P | P | – | P (removes Rc from μ) | P | – | – | P |
| contact vs channel R (and θr vs Rsd vs α) | P | P (barrier Ea) | **B** for barrier (low-Vd linearity) | – | – | P | **B** | – | – | – | P |
| sample-to-sample (N = 1) | P | – | – | P | – | – | P | P | P (wafer map) | – | **B** |
| film-thickness uncertainty | P | – | – | – | – | – | – | **B** (RBS areal density) | **B** | P | P |
| WF / χ / Qf absolute alignment | P (V_FB only; one EOT) | P | – | – | – | – | – | P (UPS/XPS cut-off) | – | P (Eg for χ) | – |

Falsifying outcomes that follow from the models:
- **C-V.** If V_FB(2) ≈ V_FB(6.3) ≈ V_FB(13.2) within 50 mV, both the back-charge hypothesis (A3) and a bulk-charge explanation of the 6.3 nm offset are falsified, and the 0.35 V confinement shift at 2 nm must also appear as a C-V shift. If QS C-V gives n_free/n_total at +3 V above about 0.8 at 2 nm, the trap-limited account of μ_FE(2 nm) is falsified (S4).
- **Optical gap.** A shift below 0.1 eV at 2 nm falsifies the 0.353 eV law (S3).
- **TLM.** 2Rc/R_on > 30 % at 2 nm overturns M1's rejection. Rc(2)/Rc(13.2) > 10 revives M2.
- **ID-VD.** Superlinear output below Vd ≈ 0.1 V at 2 nm but not at 6.3 nm supports M2. Linear output at all thicknesses rejects it. Campaign B's ideal-contact ID-VD predictions (runs 0037-0049) serve as the reference.
- **Vacuum vs air.** No Vth change at 6.3 nm falsifies adsorbate back charge.
- **Replicates.** A Vth spread of ≥ 0.3 V at 6.3 nm makes the "6.3 nm anomaly" process variation.
- **T series.** An activation energy of μ_FE(3 V) below ~5 meV at 2 nm falsifies trap-limited conduction as the μ_FE(t) driver. Campaign B 350 K predictions exist for comparison.

## 5. Task 4: Measurements in order of scientific dependency

Each step lists what it needs from earlier steps, followed by the limitation sentence the paper must carry if the step cannot be done.

0. **Retrieve data that already exist** (Januar SI, not in the package): C-V of MIM/MISM stacks (S1), 2 nm HRTEM (S2), ID-VD after anneal (S7b), NBS (S11), 65/85 °C transfer curves of the 2 nm device (S12), and PBS at 2/10 nm (Fig. 6).
1. **Measurement records and IG/IS.** Nothing is interpretable without them.
   > "Drain bias (0.7 V), current normalisation and geometry were taken from the device schematic; gate and source currents were not recorded, so off-state currents cannot be attributed to the channel."
2. **Replicates per thickness.** Every mechanism is judged against the spread.
   > "Each thickness is represented by a single device; device-to-device variation was not quantified, so the 6.3 nm threshold offset cannot be distinguished from process variation."
3. **Thickness metrology (XRR/ellipsometry, RBS, HRTEM).** All t-laws depend on it; ±0.3 nm at 2 nm moves dEc between 0.29 and 0.44 eV.
   > "Channel thicknesses are nominal, without measured uncertainty; all thickness laws are evaluated at nominal t."
4. **TLM or gated 4-probe, plus ID-VD, per thickness.** This separates channel from contacts, which every mobility extraction (Y-function, split C-V, T series) requires.
   > "Contacts were not characterised; extracted mobilities include any source/drain resistance, which is not identifiable from one transfer curve at one channel length (it is fully correlated with the tail-state exponent); bounds of ≲ 5e4 Ω·µm (2 nm) and ≲ 2e4 Ω·µm (13.2 nm) hold only within the calibrated trap model."
5. **Dual sweep and ambient/passivation.** These decide which curve counts as the quasi-static reference for static TCAD.
   > "Sweep direction, dwell and ambient were not recorded and the back channel is unpassivated; thresholds may include hysteresis and adsorbate charge, so the 6.3 nm offset is represented by an effective charge without attributing it to a location."
6. **C-V per thickness, quasi-static and multi-frequency.** Needs step 4, because Rc distorts multi-frequency C-V of thin films, and step 3, for t.
   > "Flat-band voltage and the free/trapped charge partition were not measured per thickness; work function, electron affinity and fixed charge enter as one fitted offset, and the confinement shift cannot be separated from a thickness-dependent fixed charge."
7. **Optical gap vs t, UPS/XPS alignment and W composition.** Interpreting these needs step 6.
   > "The confinement shift is a PBE proxy for pure In2O3 slabs of 0.95-1.98 nm, extrapolated to 6.3 and 13.2 nm and not measured on IWO; '~2 % W' is undefined (atomic, cation or WO3 fraction; target or film)."
8. **Temperature series (≥ 3-4 T) per thickness.** Needs steps 4 and 6 so that Rc(T) and n(T) are known.
   > "Only room-temperature data were used; band mobility and tail-state density form a calibrated pair and are not separately identified."

## 6. Task 5: Provenance issues a reviewer will catch

- **Units and Vd.** A/µm and Vd = 0.7 V come only from the schematic (`data/data_summary.json`, `_units_note`). The μ_sat reproduction (5.09/27.40) confirms the A/µm normalisation together with L/Cox, but not Vd, because the saturation formula does not contain Vd.
- **Mobility definition (resolved, §0 point 4).** The d√Id/dVg maximum lies at Vg = 1.75 V (2 nm), 2.55 V (6.3 nm) and 0.95 V (13.2 nm). At 6.3 nm that point is in the linear regime (Vov ≈ 1.1 V > Vd), where the saturation formula is invalid. At 2 and 13.2 nm it sits at the trap-filling onset.
- **Mobility ratio depends on the definition.** The 13.2/2 ratio is 4.1 (linear μ_FE), 4.7 (Y-function μ0) or 5.4 (paper). Any μ(t) power law inherits this choice (S2).
- **SS.** The paper claims "near-thermal-limit SS (60-70 mV dec⁻¹)" (l.209-210), but the workbook SS_min is 84.5 / 114.7 / 130.8 mV/dec. The pre-stress PBS devices are 62 mV/dec (2 nm) and ~119 mV/dec (10 nm) (l.668-671). Whether the PBS devices are the workbook devices is NOT DETERMINED.
- **Nt.** The PBS devices give Nt = 5.3e19 (2 nm) versus 3.39e18 cm⁻³ (10 nm), a ratio of 15.6, while §2.8 says "roughly a factor of four" between 13.2 and 2 nm. This again suggests different devices (S4). Likewise "10 nm" (PBS/AFM/SEM), "11-13 nm" (Fig. 1a) and 13.2 nm (workbook) cannot be matched; 31.8 nm is not in the paper.
- **Items the Januar text does not state:** device count or statistics (NatElec2022, by contrast, states ≥ 5 devices per point); sweep direction; Vd; measurement ambient; passivation; the method used to measure IWO thickness (HRTEM of 2 nm only; AFM gives roughness only); measurement temperature (RT is implied by S12).
- **Items the Januar text does state:** RTA at 150 °C for 600 s after the Pd step (l.181-182).
- **"Contact hole opening and metallization" (l.178-180)** implies some dielectric was opened, either over the devices or only over the gate. The passivation state is NOT DETERMINED, and this bears on the air-back-surface assumption.
- **Ioff units.** "Below 10⁻¹⁴ A in 2 nm-thick films" (l.210-211) disagrees with the workbook floor of 4.6e-15 A/µm × 290 µm = 1.3e-12 A, unless "A" means A/µm.
- **Januar's identifiability claim** (VIF < 5, l.376-382) comes from a model without Rsd. A VIF analysis cannot detect a degeneracy with a parameter the model omits. In addition, within one thickness the factor (1 − Δsr/t)² is a constant multiplying Γc, so the Δsr/Γc pair should be collinear. Their Δsr VIF of 2.28 needs explanation.

## 7. Couplings
S1: 31.8 nm double gm peak vs Rsd; passivation ambiguity behind A3. S2: μ_band(t) lumps Rsd; θr/Rsd/α degenerate; mobility definition changes the μ(t) exponent. S3: dEc sets the CNL-barrier margin (M2). S4: α_H > 1 is the tail-filling signature; IG/IS needed for floors. S6: run_0027 malformed; campaign B ID-VD is the contact reference.

## Verdicts

| mechanism | verdict | evidence class | key number |
|---|---|---|---|
| Thickness-independent Rsd causes the Ion/μ_FE(t) trend | rejected | correlation (+ literature, related material) | needs ρc ≈ 0.26 Ω·cm², Rc 5.7e5 Ω·µm per contact (5700× NatElec2022); θ_net < 0 in all films |
| Rsd as a minor contributor at 2-13.2 nm | not determined (bounded only within the model) | calibration | ≲ 5e4 Ω·µm (≤ 4 %) at 2 nm; ≲ 1-2e4 Ω·µm (≤ 4-9 %) at 13.2 nm |
| Confinement-raised Pd/IWO barrier at 2 nm | plausible-unverified; rejected as the cause of the 2/6.3 vs 13.2 step | none | needs Δφ ≥ 0.20 eV; dEc(6.3) = 0.07 eV cannot explain Ion(6.3) ≤ Ion(2) |
| Vertical access through the film | rejected | order-of-magnitude estimate | ρ·t ≤ 5e-7 Ω·cm² (< 1 % of R_on); grows with t |
| Current crowding / L_T in the 2 nm film | rejected | order-of-magnitude estimate | L_T ≤ 0.35 µm at ρc ≤ 1e-4 Ω·cm²; contact fraction ∝ R_sh^−1/2 |
| 31.8 nm series R (V0 9.2e4 Ω·µm) as a contact property carried over to 13.2 nm | rejected (within the model); 31.8 nm itself plausible-unverified | calibration | would give −27 % Ion and θ +0.17 V⁻¹ at 13.2 nm; observed θ −0.046 V⁻¹ |
| Y-function Rsd / intrinsic μ for these films | not determined (method invalid) | calibration (ATLAS method check) | α-θ correlation +1.00; μ0_Y/μ_band = 0.53-0.68 |
| Paper μ (5.1/27.4) = saturation formula applied to the workbook curves | demonstrated | validation (independent reproduction of published numbers) | 5.09 / 27.40 cm²/Vs; prediction for 6.3 nm: 3.86 |
| run_0027 as an overlap sensitivity test | rejected (malformed deck) | numerical audit | drain collapsed to x = 24 µm (15 nodes); ΔIon −2.15 % |
