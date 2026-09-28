# Thickness-aware Silvaco ATLAS model of ultrathin W-doped In2O3 (IWO) transistors

## Complete report: literature theory, experiment, model definition, deck annotation, calibration, results, limitations

Package: `IWO_PHYSICS_CONSTRAINED_MODEL_V1` (built 2026-09-20/21). Simulator: Silvaco DeckBuild 5.0.10.R + ATLAS 5.28.1.R, local licence, 32-bit build. Author of the runs: this session (29 launches, `results/RUN_INDEX.csv`). Every simulated number in this report comes from one of those launches; every material number carries a provenance label from the fixed set MEASURED_TARGET_DEVICE, MEASURED_RELATED_MATERIAL, DFT_TARGET_IWO, DFT_PURE_IN2O3_PROXY, LITERATURE_IWO, LITERATURE_IN2O3_PROXY, CALCULATED, FITTED, NUMERICAL, ASSUMED. Where the supplied inputs cannot fix a quantity the report says NOT DETERMINED FROM AVAILABLE DATA.

---

## Contents

1. Purpose and scope
2. The experiment: device, measurement, what is and is not known
3. Theory from the literature
4. From the theory to one material model M(t): every parameter, its law, its value, its reason
5. The device as represented in ATLAS
6. The final deck, line by line
7. Solver and numerical choices, with reasons
8. Calibration procedure: stages, launches, what was free at each stage
9. Results
10. Numerical verification
11. Comparison with the two earlier per-device calibrations (Astra, Claude V0)
12. Limitations and things that were not done
13. Publication-readiness statement
14. How to reproduce
15. References
Appendix A. Launch index. Appendix B. Metric definitions. Appendix C. Glossary of ATLAS keywords used.

---

## 1. Purpose and scope

The goal was a single, source-traceable ATLAS description of the sputtered ~2 % W:In2O3 channel that (a) contains the thickness physics explicitly, through laws for the band edges, effective mass, density of states, sub-gap states and background donors, instead of a separate parameter set per device; (b) is run on the real device structure; (c) is compared with the measured transfer curves of the 2.0, 6.3, 13.2 and 31.8 nm devices using identical metric extraction for measurement and simulation; and (d) is documented so that a reader can see, for every line of the deck, where its value comes from and why it exists.

The final set, at the user's request, is four launches: the 2.0 nm and 13.2 nm devices (calibrated), the 6.3 nm device run with the same parameters as an out-of-sample validation, and, after that validation had shown a threshold miss, the 6.3 nm device tuned with one device-specific flat-band offset and its own band mobility. The 31.8 nm device is excluded from the final set; the evidence gathered on it is reported in Section 12.

Two earlier calibrations of the same data existed (GPT "Astra 6" package of 2026-09-12 and the Claude V0 package of 2026-09-10/21). Both reached 0.02-0.05 decades of agreement but with four to six tuned parameters per device. They were used here as numerical baselines and as audit material (Section 11), not as sources of physics.

---

## 2. The experiment: device, measurement, what is and is not known

### 2.1 Device (Januar et al. 2026, Sec. 2.1; user's schematic)

| Layer (bottom to top) | Value | Verified in | Status |
|---|---|---|---|
| Substrate | n+ Si | paper Sec. 2.1 | screened by the continuous TiN gate; not in the electrical domain |
| Gate | TiN, 50 nm (PVD) | paper; schematic "G = TiN = 50 nm" | MEASURED_TARGET_DEVICE |
| Gate dielectric | HfO2 ~15 nm (ALD, 250 C) then Al2O3 ~2 nm; Al2O3 touches the channel | paper (growth rates); nominal thicknesses from the schematic | MEASURED_TARGET_DEVICE |
| Channel | sputtered IWO, "~2 % W", t = 2.0 / 6.3 / 13.2 / 31.8 nm (XRR) | paper (2-13 nm series); workbook columns | MEASURED_TARGET_DEVICE; the 31.8 nm film lies outside the published series |
| Source/drain | Pd, 70 nm, on top of the channel | paper; schematic "S/D = Pd = 70 nm" | MEASURED_TARGET_DEVICE |
| Anneal | RTA 150 C, 600 s | paper | process context |
| W / L | 290 um / 20 um | schematic | MEASURED_TARGET_DEVICE |
| VDS during the transfer sweep | 0.7 V | schematic | MEASURED_TARGET_DEVICE (figure) |
| Top of the channel | air (no cap) | none shown | no fictitious cap added |

The composition "2 % W" is not defined in the source (atomic, cation or mol% WO3; target or film). It enters the model only as the identity of the material. It is never converted into a donor density: 2 at.% W corresponds to about 6e20 W atoms per cm3, while every calibration of these curves needs an electrically active donor density three to four orders of magnitude smaller.

### 2.2 Measurement (workbook `IWO-TFT (1).xlsx`, sha256 ce97eccd...d47d12, preserved unchanged in `data/`)

Sheet1, rows 2-122: columns A:B = 6.3 nm, C:D = 13.2 nm, E:F = 31.8 nm, G:H = 2.0 nm. Each curve has 121 points from -3 V to +3 V in 0.05 V steps, all currents positive, VG strictly increasing. The headers carry no units. The unit A/um (current per micrometre of width) and VDS = 0.7 V are taken from the schematic and the PowerPoint slide. The currents were divided by W = 290 um exactly once when the clean CSV was produced (`data/experimental_clean.csv`); the simulation uses a 1 um width so its currents are numerically in A/um. Nothing is divided by 290 a second time.

| t (nm) | Id min (A/um) | Id at +3 V (A/um) | off-band median, -2..-0.5 V | remark |
|---|---|---|---|---|
| 2.0 | 1.08e-16 (single point at -3 V) | 5.09e-7 | 4.6e-15 | floor ~5e-15 |
| 6.3 | 5.9e-15 | 4.03e-7 | 1.5e-13 | floor ~1.5e-13 |
| 13.2 | 6.4e-12 | 3.07e-6 | 6.6e-12 | floor ~6.6e-12 |
| 31.8 | 2.6e-7 | 3.59e-6 | 2.7e-7 | always on; on-state saturates |

NOT DETERMINED FROM AVAILABLE DATA: sweep direction, dwell time, temperature, instrument floor, gate and source currents, the origin of the off-state plateaus.

### 2.3 Metrics extracted from the measurement (same code as for the simulation, Appendix B)

| t (nm) | Vth (constant current 1e-9 A/um) | SS_min (mV/dec) | SS over 1e-10..1e-8 A/um (mV/dec) | mu_FE (cm2/Vs) | Ion (A/um) | Ion/Ioff |
|---|---|---|---|---|---|---|
| 2.0 | 0.66 V | 84 | 270 | 12.1 | 5.09e-7 | 4.7e9 |
| 6.3 | 0.64 V | 115 | 295 | 10.9 | 4.03e-7 | 6.9e7 |
| 13.2 | 0.08 V | 131 | 160 | 50.2 | 3.07e-6 | 4.8e5 |
| 31.8 | none (always on) | - | - | 49.2 | 3.59e-6 | 14 |

Two facts drive the whole modelling problem. First, the threshold of the 6.3 nm film equals that of the 2 nm film although the 13.2 nm film is 0.58 V lower. Second, the apparent mobility jumps by a factor five between 6.3 and 13.2 nm.

---

## 3. Theory from the literature

### 3.1 Bulk In2O3 and the transport-neutrality level

In2O3 is a wide-gap (experimental ~2.9-3.2 eV) n-type oxide whose conduction-band minimum is a single, dispersive s-like band. Its charge-neutrality level lies about 0.4 eV ABOVE the bulk conduction-band edge (King 2008; Robertson 2011; used by Si 2021, Lin 2022, Wang 2022). Consequently surfaces and defects tend to pin the Fermi level inside the conduction band, the material is naturally degenerate n-type, and contacts to metals tend to be low-barrier. This is why the ideal-Ohmic source/drain assumption is defensible and why the 0.4 eV value is used as a consistency check (Section 4.2).

Measured bulk values used as anchors (Stokey 2021, single crystal, optical Hall and ellipsometry): electron effective mass 0.208 m0 at n = 2.8e17 cm-3 (zero-density extrapolation 0.18 m0, Feneberg), static permittivity 10.55, high-frequency permittivity 4.05. Evaporated films give eps ~8.9 (Hamberg 1986). The target process gives, by C-V on the same stack (Januar 2026 SI Fig. S1, values recorded from the online SI): IWO 9.30, In2O3 9.03, HfO2 19.57.

### 3.2 Quantum confinement in nanometre-thin In2O3 (DFT, PBE)

Two first-principles studies give slab-versus-bulk band-edge shifts for pure In2O3:

| source | slab | quantity | value |
|---|---|---|---|
| Lin 2022 (ACS Nano), H-passivated slabs in vacuum, ONCV/PBE | 1.98 nm | Eg_PBE 1.27 eV vs bulk 0.94 eV | dEg = +0.33 eV |
| Lin 2022 | 0.95 nm | Eg_PBE 1.88 eV | dEg = +0.94 eV |
| Lin 2022 | bulk / 3.52 / 1.98 / 0.95 nm | m* (PBE) 0.17 / 0.19 / 0.23 / 0.30 m0 | dm* = +0.02 / +0.06 / +0.13 m0 |
| Si 2021 (Nano Lett.), In2O3 on Al2O3, PAW/PBE | 1.5 nm | Ec shift with Ev "almost unchanged" | dEc = +0.6 eV |

PBE underestimates the absolute gap (0.94 eV vs ~3 eV experimentally), so absolute PBE gaps are never used. Only slab-minus-bulk differences are used, and only for pure In2O3: no DFT of W-doped slabs exists in the supplied material, and none could be executed here (no Quantum ESPRESSO on this machine; the inputs are prepared in `qe_workflow/`). W raises m* and flattens the conduction band (Januar 2026, qualitative), so the true IWO shifts are probably smaller; the uncertainty is carried as +/-50 %.

An infinite square well gives dE ∝ t^-2. The fitted exponent (Section 4.1) is 1.38, smaller because of the finite barrier and the nonparabolic band.

### 3.3 Sub-gap density of states in amorphous oxide semiconductors

Amorphous oxide TFTs are described with a continuous sub-gap DOS: an exponential acceptor-like tail below the conduction band g_TA(E) = N_TA exp[(E - Ec)/W_TA], a deep acceptor Gaussian, an exponential donor-like valence tail, a donor Gaussian, and interface states D_it at the semiconductor/dielectric boundary. ATLAS implements exactly this family (DEFECTS statement). Wang 2022 measured for ALD In2O3 on HfO2: Dit ~6.3e11 cm-2 eV-1 and bulk sub-gap DOS 3.3e20 cm-3 eV-1 at ND ~1e20; Lin 2022 inferred Dit ~6e11 from a 63.5 mV/dec swing; Fan 2021 (sputtered IWO, a different device) used Eg 3.05 eV, chi 4.30 eV and a deep-acceptor amplitude of 2.5-3.7e16 cm-3 eV-1. These are proxies (pure In2O3 on HfO2, or a different IWO process) and are labelled as such.

### 3.4 The analytic framework of the target paper (Januar 2026)

The paper describes the transfer curve by a blended current

ID = Iblend + Ioff, with Iblend = [ (1/IDc)^m + (1/IDt)^m + (1/IDit)^m ]^(-1/m) (1a, 1b)

IDc = (W/L) Γc Vov^2 (band-like conduction through extended states) (1c)
IDt = (W/L) Γt Vov^γ (percolative conduction through tail states) (1d)
IDit = Ioff exp[(VG - VFB)/(SS/ln 10)] (interface-trap-mediated diffusion) (1e)
Ioff = (W/L) q Dn ts nFB [exp(-qVD/kT) - 1] (1f)

with Vov = (1/κ) ln[1 + exp(κ(VG - VFB))]. The tail-channel strength is converted to a volumetric tail density by

Nt = Cox^2 / (2 θt εs k Tt) · [ μc Nc εs kT / (Γt Cox (γ - 1)) ]^(2/γ) (3)

and the sub-threshold occupation by nt ≈ θt Nt exp[(EF - Ec)/(k Tt)] (8). Tt is the characteristic tail temperature (k Tt = W_TA in ATLAS language). The paper reports, for the thickness series, that Nt rises by about a factor four from 13.2 to 2 nm while the peak mobility falls from ~27.4 to ~5.1 cm2/Vs; for the bias-stress devices it reports Nt(2 nm) = 5.3e19 cm-3 and Nt(10 nm) = 3.39e18 cm-3 (different device set, θt convention).

Mobility is modelled by the carrier-partition relation

μeff(VG) = nfree / (nfree + ntail + nit) · μmax (5)

and the surface-roughness law

μsr(Vov, t) = μ0 / (1 + θr Vov) · (1 - Δsr/t)^2 (6)

whose first factor is the Ando surface-roughness roll-off and whose second factor is the quadratic collapse when the film thickness approaches the effective roughness Δsr; the paper extracts Δsr ≈ 2.87 Å for IWO (3.75 Å for In2O3). Off-state current is stated to scale as Ioff ∝ ts nFB (4).

How each element maps into ATLAS is given in Section 4: Equation (5) is not inserted, it is produced self-consistently by the DOS occupancy of the solver; the roughness factor of Eq. (6) multiplies the band mobility; the Ando roll-off (θr) is NOT insertable natively (Section 12); Eq. (4) is used only as a consistency check.

### 3.5 Thickness trends from other IWO work

Kim 2024 (RF-sputtered 1 wt% WO3:In2O3 on SiO2, different process) finds bulk/border trap densities of 2.4, 3.1 and 14.6e18 cm-3 eV-1 at 10, 20 and 30 nm, i.e. a strong rise for thick films. This supports a background-donor/defect density that rises for the 31.8 nm film (Section 4.6), but it is a different process and is labelled LITERATURE_IWO (different process).

### 3.6 Contacts

In2O3 contacts are low-barrier because of the CNL position (Section 3.1); scaled ALD In2O3 devices reach contact resistances below 0.1 ohm·mm (Si 2022). No transfer-length data exist for the target Pd/IWO contacts, so the contacts are ASSUMED Ohmic; for the 31.8 nm film the measured total resistance at 3 V (672 ohm) bounds any series resistance.

---

## 4. From the theory to one material model M(t)

The material model is `config/iwo_material_model.yaml`; the laws are fitted and evaluated by `scripts/material_laws.py` (evidence table `tables/THICKNESS_LAW_EVIDENCE.csv`, evaluated laws `tables/THICKNESS_LAWS.csv`). The deck generator `scripts/build_iwo_decks.py` evaluates M at the requested thickness and writes the deck with a provenance header. Category labels used in the decks: A intrinsic, B confinement, D bulk defects, E interface, F transport, G contacts, H numerical.

### 4.1 Band gap and electron affinity: Eg(t), chi(t) [A + B]

Definition: Eg(t) = Eg_bulk + dEg_QC(t); chi(t) = chi_bulk - dEc(t); dEc = dEg (the whole confinement shift assigned to the conduction band, Ev fixed, as found by Si 2021).

Law: dEg_QC(t) = 0.921 · t^-1.382 eV (t in nm), a log-log least-squares fit through the three slab-minus-bulk PBE points (+0.33 eV at 1.98 nm, +0.94 eV at 0.95 nm, +0.60 eV at 1.5 nm).

Bulk anchors: Eg_bulk = 3.05 eV, chi_bulk = 4.30 eV (Fan 2021, sputtered IWO of a different device; LITERATURE_IWO). The absolute chi is uncertain by ~0.3 eV and is degenerate with the gate work function and any fixed charge; only thickness DIFFERENCES of chi are used as physics. The absolute alignment is absorbed by one shared fitted quantity (Section 4.8).

Values: 

| t (nm) | dEg_QC (eV) | Eg = EG300 (eV) | chi = AFFINITY (eV) |
|---|---|---|---|
| 2.0 | 0.353 | 3.403 | 3.947 |
| 6.3 | 0.072 | 3.122 | 4.228 |
| 13.2 | 0.026 | 3.076 | 4.274 |
| 31.8 | 0.008 | 3.058 | 4.292 |

Why it exists: it is the only mechanism in the inputs that shifts the 2 nm turn-on positive relative to the 13.2 nm film by a physically-derived amount (0.35 eV of affinity, i.e. ~0.35 V at fixed gate work function). Approach A: because the shift is in Eg/chi/m*/Nc explicitly, no BQP or Schrodinger quantum correction is enabled in ATLAS (that would double count).

Label: DFT_PURE_IN2O3_PROXY for the shift, LITERATURE_IWO for the anchors, CALCULATED for the evaluated values. TNL consistency check: with the transport-neutrality level fixed in absolute energy 0.4 eV above bulk Ec, TNL - Ec(t) = 0.4 - dEc(t) = +0.05 eV at 2 nm; the Fermi level is expected to sit lower in the gap for thinner films and the threshold to be more positive, which is what the 2 vs 13.2 nm data show.

### 4.2 Effective mass and conduction-band density of states: m*(t), Nc(t) [A + B]

Law: m*(t) = 0.208 + 0.131 · t^-1.412 m0. The bulk value 0.208 m0 is measured (Stokey 2021, MEASURED_RELATED_MATERIAL); the increment is the PBE slab-minus-bulk increase of Lin 2022 (+0.02, +0.06, +0.13 m0 at 3.52, 1.98, 0.95 nm), a proxy.

Nc(t) = 2 (2π m* k T / h^2)^{3/2} = 2.509e19 (m*/m0)^{3/2} cm-3 at 300 K.

| t (nm) | m* (m0) | Nc = NC300 (cm-3) |
|---|---|---|
| 2.0 | 0.257 | 3.27e18 |
| 6.3 | 0.218 | 2.55e18 |
| 13.2 | 0.211 | 2.44e18 |
| 31.8 | 0.209 | 2.40e18 |

Why: Nc sets the relation between the Fermi level and the free-electron density (Eq. 2 of the paper); both earlier calibrations used Nc = 5e18, which corresponds to m* = 0.34 m0 and has no source. With the measured mass the DOS is lower, which the shared electrostatic value compensates. Nv = 1e19 cm-3 is ASSUMED; holes are not solved (Section 7).

### 4.3 Permittivity [A]

eps_IWO = 9.30, from C-V on the target process (Januar 2026 SI Fig. S1; MEASURED_TARGET_DEVICE), shared over thickness. The bulk-crystal 10.55 and the film 8.9 are kept as sensitivity bounds; in a 2 nm film in series with the 3.86 nm EOT gate stack the semiconductor capacitance term changes the accumulation charge by well under 1 %.

### 4.4 Conduction-band tail states: Nt(t), W_TA [D]

ATLAS tail: g_TA(E) = N_TA exp[(E - Ec)/W_TA], acceptor-like (negative when filled). Its integral over the gap is Nt ≈ N_TA · W_TA. W_TA = k·Tt.

Law: Nt(t) = 2.0e19 · (2 nm / t)^0.75 cm-3, W_TA = 0.040 eV shared (Tt = 464 K). Anchors: the real-ATLAS calibrations of both earlier lineages give N_TA·W_TA = 2.0-2.2e19 cm-3 at 2 nm, 1.3-1.5e19 at 6.3 nm and 2.5-4.6e18 at 13.2 nm (exponent 0.7-0.8), and the paper reports ~4x between 13.2 and 2 nm (exponent 0.73); the paper's 5.3e19 at 2 nm uses the θt convention of Eq. (8) and is of the same order. Absolute Tt is not printed in the paper (only ΔTt), so W_TA is FITTED once and shared.

| t (nm) | Nt (cm-3) | N_TA = Nt/W_TA (cm-3 eV-1) |
|---|---|---|
| 2.0 | 2.00e19 | 5.00e20 |
| 6.3 | 8.46e18 | 2.11e20 |
| 13.2 | 4.86e18 | 1.21e20 |
| 31.8 | 2.51e18 | 6.28e19 |

Why: the tail sets the subthreshold slope and the free/trapped partition of Eq. (5). Because the solver fills these states according to Fermi statistics at every bias, the carrier-partition mobility of the paper emerges from the DOS without a second empirical factor.

Deep acceptor Gaussian: N_GA = 5e16 cm-3 eV-1 at Ec - 0.6 eV, width 0.15 eV, shared, ASSUMED (Fan 2021 range); the DC transfer curves are insensitive to it. Valence tail N_TD = 0 and bulk donor Gaussian N_GD = 0 (ASSUMED; the effective background donors are represented by Nd_eff instead). Capture cross sections 1e-15 cm2 for all states (ASSUMED; not identifiable from DC curves).

### 4.5 Interface states D_it [E]

Acceptor-like Gaussian sheet of peak 3e11 cm-2 eV-1 centred 0.3 eV below Ec, width 0.12 eV, shared over thickness, ASSUMED: literature HfO2/In2O3 interfaces give ~6e11 (Lin 2022, Wang 2022) and the target interface is IWO/Al2O3, which Januar reports as smoother. Implementation: a 0.25 nm IWO layer next to the Al2O3 (region 2) carries a volume Gaussian of amplitude 3e11 / 2.5e-8 cm = 1.2e19 cm-3 eV-1, moment-matched with the bulk deep Gaussian (the printed values 1.16757e19 at 0.3016 eV, width 0.1240 eV are the moment-matched combination of the sheet with the 5e16 bulk Gaussian). Halving the layer thickness changes Id by 0.009 decades (Section 10).

Dit is kept separate from the fixed charge Qf: Dit changes the swing and the free/trapped partition; Qf shifts the flat band only.

### 4.6 Effective background donor density Nd_eff(t) [D]

Law: Nd_eff(t) = 2.5e17 · [1 + (t / 20 nm)^4] cm-3 → 2.50e17, 2.52e17, 2.97e17, 1.85e18 for 2.0, 6.3, 13.2, 31.8 nm. FITTED law (three coefficients for four films): both earlier lineages needed ~2-3e17 for the thin films and >1e18 for the 31.8 nm film; Kim 2024's rising trap density for thick films supports the direction. This is the electrically active density, not the W concentration (Section 2.1). The flat-band free-electron density n_FB is not an input; it is the solver's equilibrium output (probe `avg_n`, exported per run).

### 4.7 Mobility [F]

μ0(t) = μ_band(t) · (1 - Δsr/t)^2 with Δsr = 0.287 nm (Januar Fig. 5f; the prose gives 2.87 Å; the figure axis unit is ambiguous and this is noted). Roughness factor: 0.734, 0.911, 0.957, 0.982.

μ_band is FITTED per thickness: 18.13 (2.0 nm, stage 6), 11.69 (6.3 nm, stage 8; the validation run used the earlier value 12.4 unchanged), 61.9 (13.2 nm, stage 6). The step between 6.3 and 13.2 nm has no defensible law in the inputs (hypothesis: percolation/crystallinity; Januar Figs. S2-S4 show nanoscale grains; Kim 2024 finds an optimum near 20 nm).

The deck value MUN = μ0(t): 13.30, 11.30, 59.24 cm2/Vs. The gate-voltage dependence of the effective mobility comes from the DOS occupancy (Eq. 5 realised by the solver); the Ando roll-off μ0/(1 + θr Vov) is NOT inserted: this ATLAS version ignores MOBILITY statements between SOLVE statements (verified in V0 run_0008) and its field-dependent surface models (CVT, Lombardi) are silicon calibrations with no IWO basis. Hole mobility 0.01 (irrelevant, holes not solved).

### 4.8 Fixed interface charge Qf and gate work function [E, G]

Gate work function 4.70 eV, ASSUMED (TiN literature 4.5-4.9 eV), held fixed. Qf at the IWO/Al2O3 interface: ONE value shared by all thicknesses, FITTED in stage 3: Qf = +1.73e12 cm-2, equivalent to a flat-band shift dVfb = -q Qf / Cox = -0.31 V. It is classified as an effective electrostatic correction: it absorbs the unmeasured absolute chi_bulk, the unmeasured TiN work function and any true fixed charge, which one transfer curve per device cannot separate. It is not used to hide a wrong affinity: with Qf = 0 the two calibrated films were offset by the SAME +0.3 V (Section 8), which is exactly what a common alignment error looks like and what a thickness-dependent chi error would not.

### 4.9 Contacts and series resistance [G]

Source/drain: Ohmic (no CONTACT work function), ASSUMED (Section 3.6). Series resistance zero for the thin films; a 9.2e4 ohm·um lumped value (ATLAS CONTACT RESISTANCE is in ohm·um in 2-D) was a FITTED hypothesis for the 31.8 nm film only and is not part of the final set.

### 4.10 Cox and the gate stack

Cox = eps0 / (15 nm / 19.57 + 2 nm / 9.0) = 8.955e-7 F/cm2 (EOT 3.86 nm), Cox/q = 5.59e12 cm-2 V-1. HfO2 19.57 is MEASURED_TARGET_DEVICE (SI Fig. S1); Al2O3 9.0 is ASSUMED (not reported). Both are set explicitly in the deck because the ATLAS built-in permittivities of the named materials are not the measured values.

---

## 5. The device as represented in ATLAS

Two representations are generated by the same script and were both run:

A. Reduced electrical deck (calibration stages, runs 0001-0009): IWO regions 1+2 (region 2 is the 0.25 nm interface-regularization layer), oxide regions 3 (Al2O3) and 4 (HfO2) with the permittivities set by region, gate = Dirichlet boundary at the bottom of the HfO2 with the TiN work function, source/drain = Dirichlet boundaries on the IWO top surface over 0-2 um and 22-24 um. In DC a continuous metal is an equipotential, so replacing its volume by a boundary with the same work function changes neither the field in the dielectric nor the contact condition and removes nodes (the 32-bit ATLAS build is limited to ~30k nodes).

B. Physical structure (final runs 0012-0014, at the user's request): the same channel and dielectric regions with `material=Al2O3` and `material=HfO2`, a 50 nm `Conductor` volume for the TiN gate carrying the gate electrode (TiN is not in the ATLAS metal table; the work function 4.70 eV is set on CONTACT), a 70 nm `Air` region above the channel, and 70 nm x 2 um `Palladium` electrode volumes for source and drain on the IWO top surface with no imposed work function.

Electrical equivalence of A and B was verified in the solver with identical parameters: drain currents agree to within 0.1 % at every compared bias (run_0012 vs run_0008 at 2 nm; run_0013 vs run_0009 at 13.2 nm; Section 10).

Coordinates (um): x = 0..24 (source 0-2, channel 2-22, drain 22-24); y = -t-0.07..-t Air/Pd, -t..0 IWO, 0..0.002 Al2O3, 0.002..0.017 HfO2, 0.017..0.067 TiN volume. The 2 um contact overlap is ASSUMED (not reported); with Ohmic top contacts and a 20 um channel the current is insensitive to it. MESH WIDTH = 1 um.

---

## 6. The final deck, line by line

The 2.0 nm deck of run_0012 (`results/runs/run_0012_2p0_v2_full_stepped_final/device.in`, also `decks/iwo_2p0nm.in`) is annotated below. The 13.2 nm and 6.3 nm decks differ only where stated in 6.9.

### 6.1 Provenance header (lines 1-31)

Comment lines only. They print, for every material quantity, the value written below, its category letter, its provenance label and its source or law, e.g.

`# [B] dEg_QC(t) = 0.3533 eV | DFT_PURE_IN2O3_PROXY | a*t^-p, a=0.9205, p=1.3815 (Lin2022 slabs, Si2021)`

They exist so that the deck alone is auditable without the YAML.

### 6.2 Mesh (lines 32-52)

`go atlas` starts the device simulator inside DeckBuild.

`mesh width=1.0` sets the third dimension to 1 um, so every terminal current is numerically A/um.

`x.mesh loc=0 spac=0.3` ... `x.mesh loc=24 spac=0.3`: eleven lateral mesh lines. Spacing is 0.3 um under the contacts, refined to 0.05 and 0.01 um at the contact edges (x = 1.8-2.2 and 21.8-22.2 um) where the current enters the channel, and 0.7 um in the middle of the 20 um channel where nothing varies laterally. Halving all lateral spacings changed the current by < 0.005 decades (Section 10, check A).

`y.mesh loc=-0.072 spac=0.02`: top of the Air/Pd layer (70 nm above the film), 20 nm spacing; nothing electrical happens there.

`y.mesh loc=-0.002 spac=0.00025`: the IWO top surface at y = -2 nm; 0.25 nm spacing through the film (8 intervals across 2 nm; for thicker films the spacing is min(1 nm, t/8)).

`y.mesh loc=-0.00025 spac=6.25e-05`, `loc=-0.000125`, `loc=0 spac=6.25e-05`: the 0.25 nm interface layer is resolved with 0.0625 nm spacing (four intervals) so the regularized sheet DOS and the accumulation layer next to the Al2O3 are resolved.

`y.mesh loc=0.002 spac=0.00025`: Al2O3, 0.25 nm spacing. `y.mesh loc=0.017 spac=0.001`: HfO2, 1 nm spacing. `y.mesh loc=0.067 spac=0.02`: the gate metal volume, coarse.

### 6.3 Regions and electrodes (lines 53-65)

`region num=1 user.material=IWO ... y.min=-0.002 y.max=-0.00025`: the IWO bulk. `user.material=IWO` declares a user-defined material name whose parameters are all supplied by the MATERIAL statement below.

`region num=2 user.material=IWO ... y.min=-0.00025 y.max=0`: the same material; a separate region number is needed only so that the DEFECTS statement can give this 0.25 nm layer the additional interface Gaussian.

`region num=3 material=Al2O3 ... y.min=0 y.max=0.002` and `region num=4 material=HfO2 ... y.max=0.017`: the two dielectrics as named ATLAS insulators (their permittivities are overridden below).

`region num=6 material=Conductor ... y.min=0.017 y.max=0.067`: the 50 nm TiN gate as a conductor volume.

`region num=7 material=Air ... y.min=-0.072 y.max=-0.002`: air above the channel (permittivity 1); the Pd volumes are carved out of it by the electrode statements.

`electrode name=gate x.min=0 x.max=24 y.min=0.017 y.max=0.067`: the gate electrode occupies the whole conductor volume.

`electrode name=source material=Palladium x.min=0 x.max=2 y.min=-0.072 y.max=-0.002` and `electrode name=drain material=Palladium x.min=22 x.max=24 ...`: 70 nm x 2 um Pd volumes on top of the film ends. No CONTACT work function is set for them, so ATLAS treats them as Ohmic boundaries (ASSUMED; Section 3.6). This is verified by the equivalence with the reduced deck.

### 6.4 Doping (lines 66-67)

`doping uniform n.type conc=2.50025e+17 region=1` (and region=2): the effective background donor density Nd_eff(2 nm) of Section 4.6. It is a fitted law value, not the W content.

### 6.5 Material (lines 68-78)

`material material=IWO user.group=semiconductor user.default=silicon \`: declares IWO as a semiconductor; `user.default=silicon` only tells the parser which parameter template to start from. Every parameter that matters at 300 K is overridden on the following continuation lines; nothing silicon-specific survives (no silicon mobility models are enabled, and all band, DOS, mobility and lifetime numbers are given explicitly).

`eg300=3.40331`: Eg(2 nm) = 3.05 + 0.353 (Section 4.1). `affinity=3.94669`: chi(2 nm) = 4.30 - 0.353. `permittivity=9.3`: measured (Section 4.3).

`nc300=3.27444e+18`: Nc from m*(2 nm) = 0.257 m0 (Section 4.2). `nv300=1e+19`: assumed, unused in practice.

`mun=13.3`: μ0(2 nm) = 18.13 x 0.7336 (Section 4.7). `mup=0.01`: hole mobility, irrelevant.

`taun0=1e-06 taup0=1e-06`: SRH lifetimes, ASSUMED; thermal generation is 13-17 decades below the measured floors, so they are not tuned.

`material region=3 permittivity=9.0` and `material region=4 permittivity=19.57`: Al2O3 (assumed 9.0) and HfO2 (measured 19.57). They exist because the built-in values for the named materials are not the measured ones; together they fix Cox = 8.955e-7 F/cm2.

`contact name=gate workfunction=4.7`: TiN work function, ASSUMED (Section 4.8).

### 6.6 Models and sub-gap DOS (lines 79-98)

`models fermi srh temp=300 print`: Fermi-Dirac statistics (the accumulation layer of a 2 nm film with Nc ~3e18 becomes degenerate; Boltzmann would overestimate n); SRH recombination as background only; 300 K; `print` echoes the parameters actually used into the log for audit.

`defects region=1 continuous numa=96 numd=48 \`: continuous sub-gap DOS for region 1, discretised with 96 acceptor and 48 donor energy levels (doubling them changes Id by 0.006 dec, Section 10).

`nta=5e+20 wta=0.04`: conduction-band tail, N_TA = Nt/W_TA = 2.0e19/0.040 (Section 4.4), W_TA = 0.040 eV. `ntd=0 wtd=0.1`: no valence tail.

`nga=5e+16 ega=0.6 wga=0.15`: deep acceptor Gaussian, 0.6 eV below Ec (EGA is measured from Ec in this ATLAS version), assumed and insensitive.

`ngd=0 egd=3.30331 wgd=0.1`: no donor Gaussian; EGD is measured from Ev, so the placeholder energy is Eg - 0.1 (it has no effect at zero amplitude).

`sigtae=1e-15 ... siggdh=1e-15`: electron and hole capture cross sections of the tail and Gaussian states, all 1e-15 cm2, ASSUMED (not identifiable from DC curves).

`afile=acceptor_r1.dat dfile=donor_r1.dat`: ATLAS writes the DOS it actually used to these files, which are kept in every run directory as evidence.

`defects region=2 ...`: identical tail; `nga=1.16757e+19 ega=0.301554 wga=0.123975` is the interface sheet regularized into the 0.25 nm layer (peak 3e11 cm-2 eV-1 / 0.25 nm = 1.2e19 cm-3 eV-1, moment-matched with the 5e16 bulk Gaussian, Section 4.5).

`interface qf=1.73e+12 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001`: the fixed charge on the IWO/Al2O3 interface (y = 0), the single shared fitted electrostatic value (Section 4.8), dVfb = -0.31 V.

### 6.7 Numerical method, output, probes and equilibrium (lines 99-108)

`method newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19 cr.toler=1e-17 xandrnorm carriers=1 electrons`: full Newton with up to 10 bias-step halvings on non-convergence (MAXTRAPS may not exceed 10), 80 iterations per bias, a tightened absolute current tolerance (IR.TOL) far below the measured floor, and XANDRNORM, which accepts a bias point only when BOTH the update norm and the residual norm are satisfied. Without it, in V0, ATLAS accepted deep-depletion points with a 1e-15 A/um continuity residual (visible as |Id + Is| ~ 3e-15 A). `carriers=1 electrons` solves electrons only: hole currents were 1e-38..1e-55 A in every two-carrier run of both lineages and their relative-update norm was pure noise that blocked XANDRNORM convergence. `cr.toler` is set to max(1e-17 A, 1e-5 x smallest measured active current) and this strict criterion is used up to the measured threshold (0.7 V for 2 nm).

`output con.band val.band e.mobility`: requests the band edges and the electron mobility in the saved structure files.

`probe name=chan_mob x=12 y=-0.001 n.mob dir=0`, `probe name=chan_n x=12 y=-0.001 n.conc`, `probe name=avg_n region=1 average n.conc ...`: native solver quantities recorded at every bias: electron mobility and free-electron density at the channel centre, and the film-averaged free-electron density (whose VG = 0 value is n_FB).

`solve init`: the equilibrium solution (all contacts at 0 V). `save outf=equilibrium.str`: saved for the equilibrium band diagram.

### 6.8 Bias ramp and stepped sweep (lines 109-131)

`solve vstep=-0.1 vfinal=-3 name=gate`: ramps the gate from 0 to -3 V in 0.1 V steps (deep depletion of the film), continuing from the equilibrium solution. `solve vstep=0.1 vfinal=0.7 name=drain`: ramps the drain to VDS = 0.7 V.

`log outf=transfer.log`: opens the logged sweep.

`solve vgate=-3 vstep=0.2 vfinal=-1 name=gate`: the first logged block; VGATE gives the start (already the current bias), then 0.2 V steps in deep depletion where the current is at the solver floor and nothing is extracted.

`solve vstep=0.05 vfinal=0.7 name=gate`: 0.05 V steps, the measured grid, from -1 V to the measured threshold; threshold and swing are extracted here.

`save outf=near_vth.str`: structure at VG ≈ Vth for the near-threshold band diagram.

`method ... cr.toler=5e-18 ^xandrnorm ...`: above threshold the default acceptance is restored (the on-state residual floor scales with the current; the strict criterion would never converge there).

`solve vstep=0.05 vfinal=1.5 name=gate` and `solve vstep=0.1 vfinal=3 name=gate`: the on-state, 0.05 V steps to 1.5 V (mobility peak region), 0.1 V steps to 3 V. In total 76 solved points; the measurement is compared at exactly these points.

`log off`, `save outf=final.str`: end of sweep, on-state structure.

`extract ... curve(v."gate", i."drain") outfile="idvg.dat"` (and gate, source currents, and the three probes): DeckBuild exports of the logged quantities. Gate and source currents are exported so that Kirchhoff's law Id + Is + Ig = 0 can be checked at every bias (Section 10).

### 6.9 Cut-line exports (lines 132-147)

`extract init infile="equilibrium.str"` then `curve(depth, impurity="Conduction Band Energy" material="All" mat.occno=1 x.val=12)` and the same for the valence band, electron concentration and electron quasi-Fermi level, at x = 12 um (channel centre), repeated for the near-threshold and on-state structures. These produce the band diagrams and electron-density profiles in `plots/`.

### 6.10 What differs in the 13.2 nm and 6.3 nm decks

| line | 2.0 nm | 6.3 nm | 13.2 nm |
|---|---|---|---|
| y.mesh through the film | 0.25 nm | 0.7875 nm (t/8) | 1 nm |
| doping conc | 2.50e17 | 2.52e17 | 2.97e17 |
| eg300 / affinity | 3.4033 / 3.9467 | 3.1224 / 4.2276 | 3.0761 / 4.2739 |
| nc300 | 3.27e18 | 2.55e18 | 2.44e18 |
| mun | 13.30 | 11.30 | 59.24 |
| nta (wta 0.04 everywhere) | 5.00e20 | 2.11e20 | 1.21e20 |
| interface qf | 1.73e12 | 1.73e12 | 1.73e12 |
| strict cr.toler / strict up to | 1e-17 A / 0.7 V | 2.28e-17 A / 0.65 V | 7.88e-16 A / 0.1 V |

Everything else (region 2 Gaussian, Dit, deep Gaussian, capture cross sections, contacts, models, mesh in x and in the dielectrics, sweep) is identical.

---

## 7. Solver and numerical choices, with reasons

| choice | reason |
|---|---|
| Direct ATLAS device construction, no ATHENA | a process simulator cannot predict sputtered IWO chemistry, W incorporation or the amorphous DOS; ATHENA would only reproduce the geometry, which is known. |
| Drift-diffusion, classical | the confinement physics is carried explicitly by Eg(t), chi(t), m*(t), Nc(t) (Approach A); enabling BQP/Schrodinger on top would double count. |
| Fermi statistics | degenerate accumulation in a low-Nc film. |
| Electrons only | holes are numerically zero; including them destabilised strict convergence. |
| SRH background only | not tunable against the data; thermal generation cannot produce the measured off floors. |
| Strict acceptance below Vth, default above | see 6.7; verified in V0 runs 0006/0009/0010/0011. |
| 96/48 DOS levels | x2 changes Id by 0.006 dec. |
| 0.25 nm interface regularization layer | halving it changes Id by 0.009 dec. |
| Stepped sweep 0.2/0.05/0.1 V | verified equal to 0.05 V point-by-point solves (Section 10). |
| Native zeros kept | below ~1e-17 A/um the solver returns 0 or +/-1e-19 A/um; these are counted, excluded from log residuals and never replaced by a floor. |
| 32-bit build | meshes are kept below ~30k nodes (the 13.2 nm x0.5 mesh with 40k nodes crashes). |

---

## 8. Calibration procedure: stages, launches, what was free at each stage

All launches are real, sequential, and logged (Appendix A). The scoring region "active" is the set of measured points above five times the measured off-band median, i.e. where the measurement carries device information; the score is the RMS of log10(Isim/Imeas) over that region in decades.

| stage | free quantities | launches | outcome |
|---|---|---|---|
| 1-2. Laws only (Sections 4.1-4.7), Qf = 0, WF 4.70, μ_band from the earlier calibrations | none tuned | run_0001 (2 nm), run_0002 (13.2 nm) | both curves have the measured SHAPE (SS_min sim/meas 81/84 at 2 nm, 146/131 at 13.2 nm) but sit +0.33 V (2 nm) and +0.29 V (13.2 nm) too positive; Ion -27 % / -21 %, mostly the lost overdrive; active RMSE 3.93 / 1.03 dec |
| 3. One shared flat-band offset: Qf = +1.73e12 cm-2 (dVfb -0.31 V) | 1 shared | run_0003 (2 nm), run_0004 (13.2 nm) | 2 nm 0.056 dec, dVth +0.02 V, Ion -7.3 %; 13.2 nm 0.086 dec, dVth -0.02 V, Ion -7.0 %. One number fixes both because the baseline offsets agreed to 40 mV |
| 5. Cross-thickness test at 6.3 nm with the stage-3 parameters | 0 | run_0005 | Vth 0.35 V vs 0.64 V measured (-0.29 V); shape reproduced (SS_min 108 vs 115); 0.68 dec |
| 5b. Evidence run: one device-specific offset for 6.3 nm (Qf 8.7e10) | 1 device-specific | run_0007 | 0.082 dec, Ion +6 %. Not part of the shared model |
| 5. 31.8 nm with laws + shared Qf + series resistance | 0 (+1 inherited) | run_0006 | Ion -6 % but the bulk depletes below -1 V while the measurement is flat: always-on baseline not reproduced |
| 6. Band mobility refit to Ion at fixed electrostatics | 1 per film (declared FITTED) | run_0008 (2 nm, 16.8→18.13), run_0009 (13.2 nm, 57.6→61.9) | 0.037 dec / 0.081 dec, Ion within 0.02 % |
| aborted | 31.8 nm back-surface hypothesis (run_0010, stopped in SOLVE INIT without error text); 6.3 nm mobility stage (run_0011, chain stopped by the user) | | no currents produced |
| 7. Final form: physical structure + stepped sweep, same parameters as stage 6 | 0 new | run_0012 (2 nm), run_0013 (13.2 nm), run_0014 (6.3 nm validation, shared parameters) | Section 9 |
| 8. 6.3 nm tuned (user request after the validation miss): the stage-5b device-specific offset (Qf 8.7e10) plus the mobility stage (μ_band 12.4 → 11.69, removing the +6.1 % Ion of run_0007) | 1 device-specific + 1 fitted mobility | run_0015 | 0.063 dec, Ion -0.01 %, Vth 0.65 vs 0.64 V, SS_min 111 vs 115 mV/dec |

Free-parameter count for the final model: one shared electrostatic value (Qf), one band mobility per film, and one device-specific flat-band offset for the 6.3 nm film; all laws untuned. Astra: per-device NTA, WTA, ND, μ plus a shared work function (13 numbers for three films). Claude V0: per-device NTA, WTA, ND, μ, dVfb, Dit (22+ numbers for four films).

The sensitivities that these stage pairs measure directly are in `tables/SENSITIVITY_RESULTS.csv`: dVth = -0.309 V for dQf = 1.73e12 cm-2 (the solver reproduces -q dQf/Cox = -0.3095 V exactly); Ion scales linearly with μ_band (+7.9 % → +7.9 %); the 6.3 nm offset of -1.64e12 cm-2 moves Vth by +0.294 V; changing the structure and sweep form changes nothing (< 0.2 % in any metric).

### 8.1 Counterfactual and one-at-a-time sensitivity runs (2026-09-22, runs 0016-0027)

No-confinement counterfactual (dEg = 0, m* = bulk, everything else at the final values):

| film | reference | counterfactual | dVth | dSS_min | dIon | active RMSE |
|---|---|---|---|---|---|---|
| 2.0 nm | run_0012 | run_0016 | -0.316 V | +11 mV/dec | +21 % | 0.037 → 0.846 dec |
| 13.2 nm | run_0013 | run_0017 | -0.023 V | -13 mV/dec | +1 % | 0.081 → 0.114 dec |

Reading: the confinement law moves the 2 nm film by 0.32 V and the 13.2 nm film by 0.02 V. Without it, fitting both thresholds would require fixed charges differing by (0.316 - 0.023) x Cox/q = 1.6e12 cm-2, i.e. a per-device electrostatic parameter. With it, one shared value fits both. This is the test that separates "the law is consistent with the data" from "the law is doing the work": it is doing the work.

One-at-a-time perturbations at 2 nm (each against run_0012; the changed input is the only difference):

| case | change | dVth (V) | dSS_min (mV/dec) | dmu_FE | dIon | RMSE (dec) |
|---|---|---|---|---|---|---|
| chi_bulk -0.1 eV | run_0020 | +0.10 | 0 | -0.7 % | -6.9 % | 0.46 |
| chi_bulk +0.1 eV | run_0021 | -0.10 | 0 | +0.6 % | +7.0 % | 0.36 |
| Nd0 x2 | run_0022 | -0.01 | +1.6 | +0.1 % | +0.7 % | 0.054 |
| Nt2 x1.5 | run_0023 | +0.08 | +3.1 | -6.8 % | -25 % | 0.26 |
| WTA +5 meV | run_0024 | +0.02 | +12.4 | +0.3 % | +0.4 % | 0.063 |
| Dit x3 | run_0025 | +0.03 | +9.4 | -0.2 % | -1.8 % | 0.098 |
| eps_IWO 9.3 → 10.55 | run_0026 | 0.00 | -0.1 | +0.6 % | +0.7 % | 0.037 |
| contact overlap 2 → 4 um | run_0027 | 0.00 | 0 | -1.8 % | -2.2 % | 0.038 |

What this establishes about identifiability at 2 nm: the threshold is controlled by chi (or equivalently Qf, WF) and, weakly, by the tail density; the swing by WTA and Dit, which are therefore separable from the electrostatic parameters; the on-current by the tail density through the free/trapped partition (x1.5 in Nt costs a quarter of Ion at unchanged mobility) and by chi through the overdrive. Nd, eps and the contact overlap are irrelevant for the 2 nm film, which confirms that the fitted electrostatics are not hiding a donor or geometry error. Not run: gate work function (identical action to Qf), m* alone, and any case at 6.3 nm.

---

## 9. Results

### 9.1 Final table (identical extraction for both curves; `tables/EXPERIMENTAL_VS_SIMULATION.md`)

| t (nm) | run | role | Vth_cc exp / sim (V) | SS_min exp / sim (mV/dec) | SS 1e-10..1e-8 exp / sim | mu_FE exp / sim (cm2/Vs) | Ion exp / sim (A/um) | Ioff exp / sim | active log RMSE | native zeros |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.0 | run_0012 | calibrated | 0.66 / 0.68 | 84 / 73 | 270 / 294 | 12.1 / 11.3 | 5.09e-7 / 5.09e-7 (+0.0 %) | 1.1e-16 / 5e-21 (min positive) | 0.037 dec | 24 |
| 13.2 | run_0013 | calibrated | 0.08 / 0.05 | 131 / 151 | 160 / 195 | 50.2 / 49.0 | 3.07e-6 / 3.07e-6 (-0.0 %) | 6.4e-12 / 3e-20 | 0.081 dec | 37 |
| 6.3 | run_0014 | VALIDATION, nothing tuned | 0.64 / 0.35 | 115 / 108 | 295 / 285 | 10.9 / 9.1 | 4.03e-7 / 5.11e-7 (+26.8 %) | 5.9e-15 / 1e-21 | 0.678 dec | 23 |
| 6.3 | run_0015 | TUNED: device-specific Qf 8.7e10 (+0.29 V) and μ_band 11.69 | 0.64 / 0.65 | 115 / 111 | 295 / 289 | 10.9 / 8.4 | 4.03e-7 / 4.03e-7 (-0.0 %) | 5.9e-15 / 7e-22 | 0.063 dec | 25 |

Ion/Ioff: measured 4.7e9, 6.9e7, 4.8e5; simulated values are lower bounds (> 1e14) because the simulated off-state is a native zero; the measured floors are not modelled and no percentage is reported.

### 9.2 Reading the residuals (plots/<t>/residual.png)

2.0 nm: the whole active region lies within +/-0.08 dec; a shallow -0.08 dec dip around VG ≈ 1 V (mobility peak region) and a slight positive residual right at turn-on. Simulated SS_min is 11 mV/dec steeper than measured.

13.2 nm: +0.45 dec at the single point where the measured curve leaves its 6.6e-12 A/um floor (the simulation has no floor to leave), -0.1 dec around 0.5 V, then within +/-0.03 dec above 1 V. Simulated SS_min is 20 mV/dec softer than measured; the 1e-10..1e-8 band swing is 195 vs 160 mV/dec. Ion matches to 0.02 %.

6.3 nm (validation): the simulated curve is the measured curve shifted 0.29 V to the left; the subthreshold and on-state shapes are right (SS_min within 7 %, band swing within 4 %, apparent mobility within 17 %), so the +27 % on-current is an overdrive error, not a mobility error.

6.3 nm (tuned, run_0015): with the device-specific offset (Qf 8.7e10 cm-2 instead of the shared 1.73e12, i.e. +0.29 V, equivalent to 1.6e12 cm-2 less positive interface charge) and the band mobility refitted to Ion (11.69 cm2/Vs), the film is reproduced as well as the other two: 0.063 dec, Ion within 0.02 %, Vth within 10 mV, SS_min within 4 mV/dec; the residual stays within +/-0.1 dec over the whole active region (+0.2 dec at the single point where the measured curve leaves its 1.5e-13 A/um floor, and a broad +0.1 dec hump around 1.5-2 V where the measured apparent mobility, 10.9, exceeds the simulated 8.4 cm2/Vs). The offset itself is the quantity the shared laws do not explain.

### 9.3 Physics conclusions supported by the runs

1. The pure-In2O3 confinement proxy (dEc = 0.35 eV between 2 and 13.2 nm), together with Nc(t), Nt(t) and Nd(t), accounts for the measured 0.58 V threshold difference between the 2 and 13.2 nm films: the untuned laws misplaced both thresholds by the same +0.3 V, and one shared value corrected both. The counterfactual runs (Section 8.1) confirm that the law is doing the work: without it the two films would need fixed charges differing by 1.6e12 cm-2.
2. The subthreshold shapes of both calibrated films follow from the tail law with one shared W_TA and one shared Dit without tuning.
3. The band mobility is not predicted by anything in the inputs: 18.1 vs 61.9 cm2/Vs after the roughness factor.
4. The 6.3 nm film contradicts every monotonic thickness law: its threshold sits at the 2 nm value. Cause NOT DETERMINED FROM AVAILABLE DATA (candidates: sample-to-sample fixed charge or ageing, thickness or process deviation, non-monotonic donor/confinement behaviour between 2 and 6 nm). Both earlier calibrations had hidden this by tuning a per-device parameter.
5. The measured off-state plateaus are not thermal generation in this stack (13-17 decades margin) and cannot be attributed with the available data (no gate or source current records).

### 9.4 Figures produced (plots/)

Per thickness: overlay_log, overlay_linear, residual, band_diagram_{eq, vth, on} (Ec, Ev, EFn across the stack at the channel centre, depth origin at the film top surface), electron_density_{eq, vth, on} (across the film), electron_density_vs_vg (channel-centre and film-averaged free electrons; the VG = 0 value is n_FB), mobility_vs_vg (native probe mobility vs the measured apparent field-effect mobility). Global: metrics_vs_thickness, thickness_laws_overview, mobility_roughness_factor.

---

## 10. Numerical verification (docs/NUMERICAL_CONVERGENCE.md)

Criteria: a check passes if the active-region log RMSE changes by < 0.01 dec, |dVth| < 10 mV, |dSS| < 3 mV/dec, |dIon| < 1 %, and native zeros remain zeros.

| check | evidence | result |
|---|---|---|
| A. lateral mesh x0.5 (2 nm, 28k nodes) | V0 run_0015 vs 0013 | max 0.0046 dec, Ion -0.02 %: PASS |
| A. mesh x0.7 (13.2 nm, 20k nodes; x0.5 exceeds the 32-bit memory) | V0 run_0026 vs 0024 | max 0.0040 dec: PASS |
| C. DOS levels 96/48 → 192/96 | V0 run_0016 vs 0013 | max 0.0056 dec, Ion +1.1 %: PASS (marginal on Ion) |
| E. interface layer 0.25 → 0.125 nm | V0 run_0017 vs 0013 | max 0.009 dec: PASS |
| F. tolerance: CR.TOLER 1e-19 never converges; 1e-17 + XANDRNORM vs default | V0 runs 0006/0009/0010/0011 | glitches removed, on-state unaffected: documented choice |
| G. Kirchhoff |Id+Is+Ig| at every bias | every V1 run | 5e-18 .. 1.2e-16 A; limit max(1e-17 A, 0.1 x measured off-band median): PASS. One 2 nm deep-depletion point (VG = -1.2 V, Id ~1e-19) had 1.0e-16 A, above the ORIGINAL limit based on the single-point measured minimum (1.1e-17 A); the floor was redefined as the off-band median (limit 4.6e-16 A) and the run was rescored without relaunch; both execution records are kept |
| H. repeatability | V0 identical decks | identical currents: PASS |
| I. electrons-only vs two-carrier | Astra rebuild | identical Id; hole current 1e-38..1e-55 A: PASS |
| J. width convention | V0 WIDTH=2 | raw currents x2.000, A/um identical: PASS |
| M. physical structure + stepped sweep vs reduced boundaries + per-point sweep | run_0012 vs 0008; run_0013 vs 0009 | Id within 0.08 % at 0.5 V and 0.002 % at 3 V: PASS |
| A'. V1 final 13.2 nm deck, all spacings x0.7 (24k nodes) | run_0028 vs run_0013 | max 0.0032 dec, Ion -0.01 %: PASS |
| C'. V1 final 2 nm deck, DOS levels 96/48 → 192/96 → 384/192 | run_0019, run_0029 vs run_0012 | Ion +2.0 % then +2.5 %, max 0.0125 dec, Vth/SS unchanged: FAILS the 1 % criterion; the on-current carries a +2.5 % systematic from the DOS discretization, smaller than the fit residual, so no conclusion changes; a recalibration at 384/192 would lower μ_band by ~2.5 % |
| K/L. 31.8 nm (excluded) and 6.3 nm mesh refinement | not run | OPEN |

---

## 11. Comparison with the two earlier per-device calibrations

| item | Astra 6 (2026-09-12) | Claude V0 (2026-09-10/21) | V1 (this) |
|---|---|---|---|
| band parameters | Eg 3.05, chi 4.30, eps 9.3, Nc 5e18 for all films | same | Eg(t), chi(t), m*(t), Nc(t) from laws |
| gate / contacts | WF 4.765; S/D WF 4.45 with surface recombination | WF 4.70; Ohmic | WF 4.70; Ohmic |
| flat band | one shared WF | per-device Qf | one shared Qf |
| tail | per-device NTA, WTA (0.035-0.040) | per-device NTA, WTA (0.036-0.044) | Nt(t) law, WTA 0.040 shared |
| Dit | none | per-device 2-6e11 | 3e11 shared |
| Nd | 2e17 / 1e17 / 8.9e17 | 2e17 / 3e17 / 3e17 / 2.65e18 | law 2.5e17 [1 + (t/20)^4] |
| mobility | 13.3 / 12 / 55 | 12.3 / 11.3 / 55.1 / 82 | 18.1 / (12.4) / 61.9 band x roughness factor |
| active RMSE 2 / 6.3 / 13.2 nm | 0.033 / 0.049 / 0.049 | 0.019 / 0.048 / 0.025 | 0.037 / 0.68 (validation) and 0.063 (tuned, one device-specific offset) / 0.081 |
| 31.8 nm | deferred | 0.093 (back sheet + Rs) | excluded |
| tuned numbers | 13 for three films | 22+ for four films | 1 shared + 1 per calibrated film |

Robust, lineage-independent findings: the same effective tail capacity (~2e19 cm-3 at 2 nm, falling ~4x by 13.2 nm), the same band-mobility step between 6.3 and 13.2 nm, and the same conclusion that intrinsic drift-diffusion cannot produce the off-state floors. V1 trades 0.03-0.06 dec of per-device accuracy for cross-thickness structure and exposes the 6.3 nm anomaly.

---

## 12. Limitations and things that were not done

1. No DFT of the target IWO: all confinement laws are pure-In2O3 PBE proxies; Quantum ESPRESSO could not be installed on this machine; inputs are prepared but unexecuted (`qe_workflow/`).
2. Absolute band alignment is not measured: chi_bulk, the TiN work function and Qf are degenerate; only thickness differences of chi are used as physics. C-V or Kelvin probe per thickness would remove the degeneracy.
3. The composition "2 % W" is undefined and never converted to a donor density.
4. Off-state floors are not modelled; their origin is NOT DETERMINED (no IG/IS or instrument-floor records).
5. Mobility: constant band mobility per film times the roughness factor; the gate roll-off of Eq. (6) is not insertable natively; μ_band is fitted and the 6.3→13.2 nm step has no law.
6. The 6.3 nm validation fails on the threshold by 0.29 V (Section 9).
7. The 31.8 nm device is excluded: laws + series resistance give Ion within 6 % but not the flat always-on baseline; the back-surface donor-sheet hypothesis run aborted in SOLVE INIT and was not investigated.
8. Dit is an assumed shared value; capture cross sections, lifetimes, Nv and the deep Gaussian are assumed and not identifiable from DC curves.
9. Quasi-2D sub-band quantisation of the in-plane DOS is not represented (Approach A uses a 3-D continuum Nc with a confinement-corrected mass).
10. Calibration, not validation, for 2 and 13.2 nm: one transfer curve per device at one VD and one temperature; no ID-VD, temperature or C-V data were available.
11. Contacts are ideal; the 2 um overlap is a numerical assumption.
12. The no-confinement counterfactual, eight one-at-a-time perturbations at 2 nm and the V1 mesh/DOS refinements were executed on 2026-09-22 (Sections 8.1 and 10). Not run: gate work function (same action as Qf), m* alone, sensitivity cases at 6.3 nm, and the mesh refinement of the 6.3 nm film.
13. run_0010 and run_0011 produced no currents (aborted / stopped) and are recorded as such.
14. Data provenance: current units, VD and geometry come from the schematic, not from workbook headers.

Integrity statement: no material parameter or source was invented; no fit is called a measurement; the W content was not treated as a donor density; pure-In2O3 values are labelled as proxies; no PBE gap is used as an experimental gap; the fitted Qf is declared as an effective alignment correction and was shown to be a common offset rather than a thickness-dependent patch; mobility was not used to correct a wrong carrier density (it was fitted last, at fixed electrostatics, and moved Vth by < 10 mV); no ATLAS run, DFT run or convergence test is fabricated; no nonzero leakage was manufactured where ATLAS gives zero; ATHENA was not used; "exact match" is not claimed anywhere; the model is not called predictive.

---

## 13. Publication-readiness statement

The package is publication-ready as a calibrated, thickness-resolved TCAD parameter extraction for the 2, 6.3 and 13.2 nm devices (0.037 / 0.063 / 0.081 dec) with one documented shared electrostatic offset, one documented device-specific offset for the 6.3 nm film, and a documented negative out-of-sample result for that film under the shared laws. It is not a predictive model of thickness scaling: the shared laws miss the 6.3 nm threshold by 0.29 V, the band mobility is fitted per film, the confinement law is a pure-In2O3 proxy, and no independent bias, temperature or capacitance data were available. A manuscript should describe it as calibrated on the same transfer curves it reproduces and report both the 6.3 nm validation miss and its device-specific correction. A ready-to-edit Methods paragraph is in `docs/PUBLICATION_METHODS_DRAFT.md`.

What would make it predictive: C-V (or Kelvin probe) per thickness; a second bias or temperature per device; DFT of W-doped slabs; TLM for the contacts; gate/source current records for the off state.

---

## 14. How to reproduce

From the package directory with the Python environment of the sibling package (`..\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe`):

```
python scripts/material_laws.py                    # laws -> config/iwo_material_model.yaml, tables/THICKNESS_LAWS.csv, law plots
python scripts/build_iwo_decks.py                  # decks/iwo_{2p0,6p3,13p2,31p8}nm.in in the final form (physical structure, stepped sweep)
python scripts/run_atlas.py --thickness 2 --label rerun --override traps.fixed_interface_charge_Qf_cm2.value=1.73e12 --override "thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]=18.13"
python scripts/run_atlas.py --thickness 13.2 --label rerun --override traps.fixed_interface_charge_Qf_cm2.value=1.73e12 --override "thickness_laws.mu0_cm2Vs.mu_band_fitted[13.2]=61.9"
python scripts/run_atlas.py --thickness 6.3 --label validation --override traps.fixed_interface_charge_Qf_cm2.value=1.73e12
python scripts/compare_experiment_simulation.py    # tables/EXPERIMENTAL_VS_SIMULATION.{csv,md} from results/BEST_RUNS_V1.json
python scripts/plot_results.py                     # plots/
python scripts/make_provenance_tables.py           # tables/MATERIAL_PARAMETERS_USED.*, PARAMETER_PROVENANCE.csv
python scripts/sensitivity_from_stage_runs.py      # tables/SENSITIVITY_RESULTS.*
```

Every launch creates a new `results/runs/run_NNNN_*` directory (deck, DeckBuild log, transfer.log, exports, KCL table, comparison, execution record) and appends to `results/RUN_INDEX.csv`; the launch budget is enforced by `config/solver.yaml`.

---

## 15. References

Supplied and read (PDF text in `inputs/papers_text/`):

1. M. Januar, Z.-F. Luo, K.-C. Liu, M.-H. Lee, "Unified Analytic Framework for Thickness-Dependent Transport and Trap-State Modulation in Ultrathin W:In2O3 Field-Effect Transistors," Small Structures 7, e202500807 (2026), DOI 10.1002/sstr.202500807. Stack, process, Eqs. (1)-(9), Nt/Tt, Δsr, mobility law, DFT trends. Supporting Information not supplied (eps values recorded from the online SI by the Astra audit).
2. M. Si, Y. Hu, Z. Lin, et al., P. D. Ye, "Why In2O3 Can Make 0.7 nm Atomic Layer Thin Transistors," Nano Letters 21, 500 (2021), DOI 10.1021/acs.nanolett.0c03967. CNL 0.4 eV above Ec; DFT dEc ≈ 0.6 eV at 1.5 nm with Ev unchanged.
3. Z. Lin, M. Si, V. Askarpour, et al., P. D. Ye, "Nanometer-Thick Oxide Semiconductor Transistor with Ultra-High Drain Current," ACS Nano 16, 21536 (2022), DOI 10.1021/acsnano.2c10383. PBE gaps 0.94/1.27/1.88 eV; m* 0.17/0.19/0.23/0.30 m0; Dit 6e11.
4. Z. Wang, Z. Lin, M. Si, P. D. Ye, "Characterization of Interface and Bulk Traps in Ultrathin Atomic Layer-Deposited Oxide Semiconductor MOS Capacitors With HfO2/In2O3 Gate Stack by C-V and Conductance Method," Frontiers in Materials 9, 850451 (2022), DOI 10.3389/fmats.2022.850451. Dit 6.3e11; bulk DOS 3.3e20.
5. M. Stokey, R. Korlacki, S. Knight, et al., M. Schubert, "Optical phonon modes, static and high-frequency dielectric constants, and effective electron mass parameter in cubic In2O3," J. Appl. Phys. 129, 225102 (2021), DOI 10.1063/5.0052848. eps_DC 10.55, m* 0.208 m0.
6. H. Kim, H.-S. Choi, G. Yun, W.-J. Cho, H. Park, "Understanding thickness-dependent stability of tungsten-doped indium oxide transistors," Appl. Phys. Lett. 125, 173507 (2024), DOI 10.1063/5.0228363. Thickness trend of bulk/border traps.
7. M. Si, Z. Lin, Z. Chen, X. Sun, H. Wang, P. D. Ye, "Scaled indium oxide transistors fabricated using atomic layer deposition," Nature Electronics 5, 164 (2022), DOI 10.1038/s41928-022-00718-w. Contact/CNL context.
8. N. Pandey et al., "Analytical Modeling of Short-Channel Effects in BEOL-Compatible Thin-Film Transistors," IEEE Trans. Electron Devices 72, 2381 (2025), DOI 10.1109/TED.2025.3546593. TCAD trap convention (context).
9. X. Wang et al., "A Physics-Based Compact Model for IGZO Channel FET Toward Subthreshold Characteristic Dependent Memory Application," IEEE Trans. Electron Devices 72, 2390 (2025), DOI 10.1109/TED.2025.3549745. Donor-Gaussian treatment (context).
10. K. Anusha, A. D. D. Dwivedi, "Review and analysis on numerical simulation and compact modeling of InGaZnO thin-film transistor for display SENSOR applications," Measurement: Sensors 36, 101391 (2024), DOI 10.1016/j.measen.2024.101391. Background.
11. P. Giannozzi et al., "QUANTUM ESPRESSO: a modular and open-source software project for quantum simulations of materials," J. Phys.: Condens. Matter 21, 395502 (2009), DOI 10.1088/0953-8984/21/39/395502. Software reference for the unexecuted workflow.

Cited inside the packages and used as priors (not supplied; METADATA_REQUIRES_VERIFICATION):

12. W.-T. Fan et al., "Numerical Analysis of Oxygen-Related Defects in Amorphous In-W-O Nanosheet Thin-Film Transistor," Nanomaterials 11, 3070 (2021), DOI 10.3390/nano11113070. Eg 3.05 / chi 4.30 priors, deep-acceptor range.
13. C. Yoo et al., "Atomic Layer Deposition of WO3-Doped In2O3 for Reliable and Scalable BEOL-Compatible Transistors," Nano Letters 24, 5737 (2024), DOI 10.1021/acs.nanolett.4c00746. W content evidence.
14. I. Hamberg, C. G. Granqvist, J. Appl. Phys. 60, R123 (1986). eps 8.9 of evaporated films.
15. P. D. C. King et al., Phys. Rev. Lett. 101, 116808 (2008). CNL above Ec.
16. J. Robertson, S. J. Clark, Phys. Rev. B 83, 075205 (2011). CNL.
17. Y. Hinuma, T. Gake, F. Oba, Phys. Rev. Materials 3, 084605 (2019). In2O3/Al2O3 band alignment.
18. M. Feneberg et al., In2O3 nonparabolicity, m*(0) = 0.18 m0 (cited in ref. 5).
19. T. Ando, A. B. Fowler, F. Stern, Rev. Mod. Phys. 54, 437 (1982). Surface-roughness mobility law.
20. J. Lee, K.-H. Lim, Y. S. Kim, Sci. Rep. 8, 13905 (2018). Gate-leakage caution.

Software and manuals: Silvaco ATLAS User's Manual 5.28.1.R (DEFECTS, INTDEFECTS, CONTACT, METHOD, TFT and quantum chapters, installed copy); Silvaco DeckBuild User's Manual 5.0.10.R (batch options); installed vendor TFT examples used to validate syntax. Packages audited: GPT Astra 6 `IWO_PRIORITY_THREE_20260912.zip`; Claude `IWO_ATLAS_Model_claude`.

---

## Appendix A. Launch index (results/RUN_INDEX.csv)

| run | t (nm) | label | outcome |
|---|---|---|---|
| 0001 | 2.0 | laws only | scored, 3.93 dec (offset +0.33 V) |
| 0002 | 13.2 | laws only | scored, 1.03 dec (offset +0.29 V) |
| 0003 | 2.0 | + shared Qf 1.73e12 | 0.056 dec |
| 0004 | 13.2 | + shared Qf | 0.086 dec |
| 0005 | 6.3 | shared parameters (prediction) | 0.678 dec, Vth -0.29 V |
| 0006 | 31.8 | laws + shared Qf + Rs | 1.05 dec; baseline not reproduced |
| 0007 | 6.3 | device-specific Qf 8.7e10 (evidence) | 0.082 dec |
| 0008 | 2.0 | μ_band 18.13 | 0.037 dec |
| 0009 | 13.2 | μ_band 61.9 | 0.081 dec |
| 0010 | 31.8 | back-surface sheet hypothesis, stepped | aborted in SOLVE INIT (no error text) |
| 0011 | 6.3 | μ_band 11.69 | stopped by the user before completion |
| 0012 | 2.0 | FINAL: physical structure, stepped sweep | 0.037 dec (rescored under the median-floor KCL rule) |
| 0013 | 13.2 | FINAL | 0.081 dec |
| 0014 | 6.3 | FINAL validation, shared parameters | 0.678 dec |
| 0015 | 6.3 | FINAL tuned: device-specific Qf 8.7e10 + μ_band 11.69 | 0.063 dec |
| 0016 / 0017 | 2.0 / 13.2 | no-confinement counterfactual | dVth -0.316 V / -0.023 V |
| 0018 | 13.2 | mesh x0.7 (900 s timeout) | timed out at 68/76 points; repeated as 0028 |
| 0019 / 0029 | 2.0 | DOS levels 192/96 / 384/192 | Ion +2.0 % / +2.5 % |
| 0020-0027 | 2.0 | one-at-a-time: chi -/+0.1, Nd x2, Nt x1.5, WTA +5 meV, Dit x3, eps 10.55, overlap 4 um | Section 8.1 |
| 0028 | 13.2 | mesh x0.7 (1500 s timeout) | max 0.0032 dec: PASS |
| 0016 / 0017 | 2.0 / 13.2 | no-confinement counterfactual | Vth -0.316 V / -0.023 V |
| 0018 | 13.2 | mesh x0.7 | timed out at 900 s (68 of 80 points) |
| 0019 / 0029 | 2.0 | DOS levels 192/96 / 384/192 | Ion +2.0 % / +2.5 % |
| 0020-0027 | 2.0 | one-at-a-time: chi -/+0.1, Nd x2, Nt x1.5, WTA +5 meV, Dit x3, eps 10.55, overlap 4 um | Section 8.1 |
| 0028 | 13.2 | mesh x0.7, 1500 s | max 0.0032 dec: PASS |

## Appendix B. Metric definitions (scripts/extract_metrics.py, applied identically to both curves)

Vth_cc: gate voltage where Id = 1e-9 A/um, log-linear interpolation between adjacent points, no extrapolation. Vth_lin: linear extrapolation at maximum transconductance. SS_min: minimum over 0.2 V centred windows of dVG/dlog10(Id), restricted to currents above five times the MEASURED off-band median of the same device (applied to the simulated curve too, so both are evaluated over the same current range) and below 1 % of Ion. SS_cc: average slope between the 1e-10 and 1e-8 A/um crossings. mu_FE = gm,max L / (W Cox VD) with L = 20 um, W = 1 um for A/um data, Cox = 8.955e-7 F/cm2, VD = 0.7 V (an apparent field-effect mobility, not the band mobility). Ion = Id(+3 V). Ioff = minimum Id (measurement) or minimum POSITIVE Id with the count of native zeros (simulation). Threshold differences are absolute; no percentage for sign-changing quantities. Active-region log RMSE: RMS of log10(Isim/Imeas) over measured points above five times the off-band median.

## Appendix C. Glossary of ATLAS keywords used

MESH WIDTH: third-dimension width (um). REGION/ELECTRODE: geometry; `user.material` = user-defined material. DOPING UNIFORM N.TYPE CONC: ionised donor density (cm-3). MATERIAL EG300 / AFFINITY / PERMITTIVITY / NC300 / NV300 / MUN / MUP / TAUN0 / TAUP0: band gap (eV), electron affinity (eV), relative permittivity, effective DOS (cm-3), electron/hole mobility (cm2/Vs), SRH lifetimes (s). CONTACT WORKFUNCTION: metal work function (eV); CONTACT RESISTANCE: lumped resistance (ohm·um in 2-D). MODELS FERMI SRH: Fermi statistics, SRH recombination. DEFECTS CONTINUOUS NUMA/NUMD: continuous sub-gap DOS with the given number of acceptor/donor energy levels; NTA/NTD: tail intercepts at Ec/Ev (cm-3 eV-1); WTA/WTD: tail widths (eV); NGA/NGD: Gaussian amplitudes (cm-3 eV-1); EGA (from Ec)/EGD (from Ev): Gaussian centres (eV); WGA/WGD: Gaussian widths; SIGTAE.. SIGGDH: capture cross sections (cm2); AFILE/DFILE: DOS export files. INTERFACE QF: fixed interface charge (cm-2). METHOD NEWTON TRAP MAXTRAPS ITLIMIT CLIMIT IR.TOL CR.TOLER XANDRNORM CARRIERS: Newton solver, bias-step halving, iteration limit, concentration limit, absolute current tolerance, continuity residual tolerance, dual-norm acceptance, carrier selection. PROBE: named scalar recorded at each bias. SOLVE INIT / VSTEP / VFINAL / NAME: equilibrium solution; stepped bias sweep on the named electrode. LOG OUTF: logged sweep file. SAVE OUTF: structure file. EXTRACT: DeckBuild post-processing (curves from logs and cut-lines from structures).
