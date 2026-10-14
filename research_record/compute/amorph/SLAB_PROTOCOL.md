# Slab protocol, revision 2 (registered 2026-10-10, before any ML or DFT result)

Decision D-14 (`05_DECISION_LOG.md`). The rules are applied in the code: `make_specs.py`, `mace_amorph.py` (QC) and `dft/make_dft.py`.

The first wave (cluster 12883756) was removed while it was still idle; none of its jobs had started. Revision 2 runs as cluster 12883773, with 18 jobs.

## 1. Dopant concentration

- **Ratio.** W/(In+W) is exactly 2.0 % in every IWO cell: 50 cations for each W.
- **Compensation.** Each W gets one extra O, which leaves one extra electron per W:
  - IWO cell: In(49n) W(n) O(76n);
  - In2O3 twin: In(50n) O(75n), with the same cell.
- **Change from wave 1.** At 2 nm, wave 1 used 1 W in 66 cations (1.5 %). The bulk cells used 1 W in 32 cations (3.1 %). Both are replaced.
- **W placement.**
  - W atoms start at least 6 Å apart.
  - The QC file reports the following. These are reported only; they do not make a structure fail.
    - **W depth:** the depth of each W below the nearer film boundary.
    - **Closest W-W distance:** the closest W-W distance, including periodic images.

## 2. Lateral supercell size

- **Choice of n_W.** n_W is the smallest number that makes the in-plane edge at least 12.5 Å, at 7.0 g/cm³.
- **Consequence.** The W volume density is the same at every thickness.
- **QC rule.** A slab FAILS QC if its in-plane edge is below 12.5 Å.

| t (nm) | n_W | Cell, IWO / IO | L (Å) |
|---|---|---|---|
| 2.0 | 2 | In98W2O152 / In100O150 | 12.91 |
| 1.5 | 2 | In98W2O152 / In100O150 | 14.91 |
| 1.0 | 1 | In49W1O76 / In50O75 | 12.91 |
| 0.8 | 1 | In49W1O76 / In50O75 | 14.43 |
| 0.7 | 1 | In49W1O76 / In50O75 | 15.43 |

- **k-points.** The density is fixed at n_k = ceil(2π / (a · 0.25 Å⁻¹)). That gives 2×2×1 for every cell, in both the relax and the final SCF.
- **Bulk force-check cells.** These are 50 cations with L = 11.9 Å. They are used only to validate the ML potential, so the lateral rule does not apply to them.

## 3. Thickness definition

Four thicknesses are reported. Only t_eq is used for labels, plots and TCAD.

| Name | Definition | Use |
|---|---|---|
| **t_eq** (primary) | Film mass / (7.0 g/cm³ × area). This is the mass-equivalent thickness, which XRR/ellipsometry and the ALD cycle count measure. It equals the box height before the cleave. | labels, TCAD |
| t_span | Outermost non-H film atoms | roughness / expansion check |
| t_cat | Outermost film cations | cation-layer count |
| t_ρ | Distance between the two points where the DFT planar-averaged electron density falls to 50 % of its interior mean (from `ppavg`) | electronic thickness; quantum-confinement plots, with t_eq on the axis and t_ρ given |

## 4. Termination

**Default.** Dissociated water, added in OH + H pairs so the electron count is unchanged. The sites are under-coordinated surface atoms, meaning at least about 2 below the amorphous bulk value:

| Site | Threshold |
|---|---|
| In | CN ≤ 4 |
| W | CN ≤ 5 |
| Al | CN ≤ 3 |
| O bonded to In/W | ≤ 2 cation neighbours |
| O on Al2O3 | ≤ 1 cation neighbour |

**Reported in QC.** H per nm² on each face, and the number of unpaired sites.

**Controls.** Bare surfaces at 2.0 nm (`aIWO_2p0_s1_bare`) and at 0.7 nm (`aIWO_0p7_s1_bare`). 0.7 nm is where surface atoms dominate.

**Test.** A termination counts as acceptable for TCAD if the passivated slab shows no gap states that the bare control lacks. The DFT PDOS of the surface atoms is used to check this.

## 5. Interface realism

- **Device stack.**
  - n+Si / TiN / HfO2 15 nm / Al2O3 2 nm / channel / Pd.
  - Al2O3 is listed after HfO2, so Al2O3 touches the channel. This order is still an open question for the fab (`01_CURRENT_STATE.md` item 3).
- **Model, mode `interface`.**
  1. a-Al2O3, about 1 nm at 3.0 g/cm³, is melt-quenched first.
  2. The film is melted and quenched on top of it while the oxide is held fixed. This mimics ALD growth on an existing oxide.
  3. The stack is cleaved below the oxide.
  4. It is annealed at 800 K with all atoms free.
  5. Both outer faces are passivated:
     - the film top is the OH-terminated back channel;
     - the Al2O3 bottom is OH-terminated.
- **Runs.** `aIWO_2p0_Al2O3_s1` (the measured thinnest film) and `aIWO_1p0_Al2O3_s1`. Each uses the same lateral cell as its vacuum slab, so the two can be compared directly.
- **Intermixing.** QC reports the film cations inside the oxide and the Al inside the film.
- **Not modelled.**
  - **Pd contact.** It affects contact injection, not the channel bands; its effect is carried by the TCAD Schottky contact.
  - **HfO2 interface.** Not modelled unless the fab says HfO2 touches the channel.
- **Al PAW** (pslibrary 1.0.0, `Al.pbe-n-kjpaw_psl.1.0.0.UPF`): installed 2026-10-10 from pseudopotentials.quantum-espresso.org into `~/iwo_amorph/common/pseudo/`.
  - Size and checksum: 1,678,298 bytes, sha256 `450c947c…e3ab4a`.
  - Header checked: PAW, PBE, Z_val = 3. Its suggested cutoffs are 29.5 / 143 Ry, below the 60/480 and 71/568 Ry used here.

## 6. Other settings

**Vacuum.**
- 2 × 10 Å before relaxation.
- QC requires at least 15 Å afterwards.
- Dipole correction along z.
- **Amendment (2026-10-10, after the first two ML results).** Every DFT slab cell gets exactly 18 Å of vacuum: c = film span + 18 Å, with the slab re-centred. This is a numerical setting, and it leaves the structure unchanged.
  - The trigger: aIWO_2p0_s1 and aIWO_2p0_s2 passed every check except vacuum (14.7 Å). The film roughened by about 4 Å after the cleave.
  - A QC failure whose only reason is the vacuum is therefore fixed in `make_dft.py`; it does not reject the structure. Every other QC rule is unchanged.

**The final CPU SCF.** It includes pp.x and projwfc. Cells above 200 atoms go to the 3-day queue.

**ML.** The pass limits in `ML_VALIDATION.md` are unchanged.

## 7. QC rejections and replacements

- **Rule.** A structure that fails QC for any reason other than the vacuum is rejected. It is replaced by the same recipe with the next seed. The thresholds are never changed after a result is seen.
- **Rejections on 2026-10-10:**

| Rejected structure | Reason | Replacement (seed) |
|---|---|---|
| `aIWO_0p8_s1` | O–O 1.51 Å (peroxide) and 1 water molecule | `aIWO_0p8_s2` (82) |
| `aIWO_2p0_Al2O3_s1` | Al–Al 2.479 Å, below the 2.5 Å limit | `aIWO_2p0_Al2O3_s2` (702) |
| `aIWO_1p0_Al2O3_s1` | 1 water molecule | `aIWO_1p0_Al2O3_s2` (602), made with the amended recipe below |

- **Recipe amendment (2026-10-10).** Two of the first three rejections contained an H2O molecule. In both, an OH and an H from the dissociated-water passivation recombined during the final relaxation. In a real film this water would desorb during the anneal or in vacuum.
  - **New step.** After the final relaxation, `remove_water()` deletes any O that is bound to no cation but to exactly two H, together with those two H. The structure is then re-relaxed.
  - **Why it is safe.** One OH and one H leave together, so the structure stays neutral and the passivation stays paired.
  - **Reporting.** The number removed is written to the QC file (`water_removed`).
  - **Unchanged.** The QC rules themselves. Peroxide and short contacts still cause rejection.
  - **Coverage.** The amendment applies to every ML job that starts after this time; that includes the queued replacements. Structures that had already passed contain no water, so they are unaffected.

- **Reporting.** Every rejection is reported with the results, together with the QC pass rate.

## 8. Fully compensated 2.0 nm variant (added 2026-10-10, D-15)

**Structure.** `aIWO_2p0_comp_s1`, In98 W2 O153.
- W6+ on an In3+ site carries +3. With 1.5 extra O per W, the cell has **0 excess electrons**.
- The production cells, In(49n) W(n) O(76n), carry 1 e per W, about 6e20 cm^-3. That is far above the device's carrier density (Codex work chat, open question 6).

**Pairing with `aIWO_2p0_s1`.** Same t (2.0 nm), same L (12.91 A), same seed (201), same recipe and QC rules.
- The O count differs by one, so the two melt-quench structures are not identical. Seed spread is set by the two 2.0 nm samples (s1, s2).

**What it is for.** To show the W level and band edges when the conduction band is empty. This separates the band filling and screening seen in the 1 e/W cells from the effect of W itself.

**Labels.** Its electronic results are COMPUTED. Its role is a sensitivity control on the doping regime; it is not a fit target.

## 9. HfO2 interface control (A18, D-20)

Registered as hypothesis H-M (amendment A18, 2026-10-10T18:52Z) before the Hf pseudopotential was installed or any structure was built. It is a **control** for the unresolved stack order (`01_CURRENT_STATE.md` item 3); it becomes the primary interface only if the fab confirms that HfO2 touches the channel.

**Cell.** `aIWO_2p0_HfO2_s1`, round 4 (`ml_jobs_r4.txt`), ML seed 902.
- Film identical to `aIWO_2p0_Al2O3_s2`: In98W2O152, t = 2.0 nm, L = 12.91 Å, 2.0 % W.
- Substrate: a-HfO2, Hf46O92, 10.05 Å mass-equivalent thickness at **9.6 g/cm³** (ASSUMED; ALD a-HfO2 is about 9.1–9.7). `make_specs.py`: `RHO_HFO2 = 9.6`, `hfo2(L, t_nm=1.0)` (analogue of `al2o3`). 390 atoms before passivation.
- Recipe: §5 unchanged (oxide melt-quench; film melt-quench with the oxide fixed; cleave below the oxide; 800 K anneal, all atoms free; OH passivation of both faces; `remove_water()` as in §7).
- DFT settings identical to `aIWO_2p0_Al2O3_s2` (relax MV 0.01 Ry; final SCF Gaussian, A15 gate). `make_dft.py` only gains Hf in `VAL` (12), `MASS` (178.49), `PP` and the ATOMIC_SPECIES order (In, W, Al, Hf, O, H).

**Hf PAW** (pslibrary 1.0.0, `Hf.pbe-spn-kjpaw_psl.1.0.0.UPF`): installed 2026-10-10T18:56Z from `https://pseudopotentials.quantum-espresso.org/upf_files/` (the Al source) into `~/iwo_amorph/common/pseudo/`. That directory is what every relax, final and force-check job transfers (`transfer_input_files ... {common}/pseudo`, `pseudo_dir = './pseudo'`).
- Size and checksum: 2,143,956 bytes, sha256 `095c2e6c7997f8b78dedd2132f6cf12c60e93e1a30c77a85b2d552a0527b87bd`.
- Header checked (UPF 2.0.1, ADC `atomic` 6.2.2, 3 May 2018; XML parses, ends with `</UPF>`): `pseudo_type` PAW, scalar-relativistic, functional SLA PW PBX PBC (PBE), `z_valence` 12 (5s2 5p6 5d2 6s2; **4f14 frozen in the core**), nonlinear core correction. Suggested cutoffs 46 / 264 Ry, below the 60/480 and 71/568 Ry used here.

**New Hf thresholds in `mace_amorph.py`** (In/W/Al/O/H values unchanged):

| Quantity | Value | Justification |
|---|---|---|
| Hf–O coordination cutoff | 2.65 Å | a-HfO2 first shell 2.0–2.3 Å (m-HfO2 bonds 2.03–2.25 Å); next Hf–O shell ≥ ~3.4 Å, so the cutoff sits in the empty gap, 0.4 Å beyond the longest first-shell bond |
| QC min Hf–O | 1.85 Å | ~0.87 × the a-HfO2 mean bond (2.10 Å), the same margin as In–O, W–O, Al–O; below the shortest m-HfO2 bond (2.03 Å) |
| QC min Hf–Hf | 2.80 Å | ~0.8 × the first a-HfO2 Hf–Hf peak (3.3–3.5 Å) and ~0.9 × the hcp Hf metal bond (3.13 Å); same relative margin as In–In 2.70 and Al–Al 2.50 |
| QC min Hf–In / Hf–W | 2.75 / 2.70 Å | means of the like-cation limits, as Al–In / Al–W |
| QC min Hf–H | 1.80 Å | below Hf–H hydride bonds (1.85–2.1 Å), as In–H / Al–H |
| Random-start packing | generic 2.9 / 1.9 / 2.4 Å | 2.9 Å < Hf–Hf 3.3–3.5 Å and 1.9 Å < Hf–O 2.0–2.2 Å; 46 Hf at 2.9 Å already fill a hard-sphere fraction 0.35 of the box (random-sequential-addition limit ~0.38), so a larger Hf–Hf start distance would only force the scale-back |
| Under-coordinated Hf | CN ≤ 5 | a-HfO2 mean Hf CN ~6–7, the §4 rule |
| OH placed on Hf at | 1.95 Å | terminal Hf–OH bond, shorter than the bulk Hf–O as for In and Al |
| Under-coordinated O | ≤ 1 cation neighbour if most of its cations are substrate cations (Al **or Hf**), else ≤ 2 | the §4 Al2O3 rule generalised to the substrate-cation set; a-HfO2 O CN ~3.3 |

- **Intermixing and oxide QC (reported only, as for Al):** `n_film_cations_in_oxide`, `n_Hf_in_film`, `Hf_CN_mean`, `Hf_CN_hist`, `Hf_O_bond_mean_A`. The film/oxide boundary z_if is the midpoint between the 95th-percentile Hf and the 5th-percentile film cation, as for Al.
  - **Correction (2026-10-10, independent verification).** These two counts are **not** a measure of intermixing. They add film material left on the *outer* oxide face (see the smoke test) to the few cations within ~0.3 Å of z_if that the percentile midpoint places on the wrong side by construction. The same holds for the Al2O3 cells (§5).
- **Added reported-only QC keys (verification fixes, 2026-10-10; HfO2 cell only).** They change no PASS/FAIL rule and no output of any other cell (proof below).
  - `iface_partition()`:
    - `outer_face_film_cations`: film cations within 3 Å of the lowest Hf, i.e. on the outer oxide face, with their density per nm²;
    - `outer_face_film_O`: film-origin O there. The origin labels (substrate / film / passivation) are carried through passivation and `remove_water()`;
    - `buried_film_cations_in_oxide`, `buried_Hf_in_film`: more than 1 Å past z_if, outer face excluded;
    - the counts within 1 Å of z_if;
    - `OO_contacts_below_limit`: every O–O pair below 2.15 Å, with its region (outer oxide face, interface, oxide or film interior, film top), the origin of each O and the H attached.
  - `hf_diag()`:
    - `Hf_O_bond_hist_0p05A` (1.80–2.65 Å) and `Hf_O_bond_stats_A` (n, min, p5, p50, p95, max, mean, std): the Hf–O bond-length distribution that A21 requires;
    - `Hf_Hf_hist_0p1A` (2.8–5.0 Å), `Hf_Hf_first_peak_A`, `Hf_Hf_min_A`;
    - `Hf_O_Hf_angle_hist_10deg`, `Hf_O_Hf_angle_mean_deg`;
    - `oxide_interior_density_gcc`: all atoms between 2 Å above the lowest Hf and 2 Å below z_if.
  - `oxide_3000K_hold_MSD_A2`: Hf and O mean-square displacement over the 3000 K hold of the oxide-only melt.
  - `slab_annealed_diag`: the same partition and diagnostics, plus `Hf_CN_hist`, for the state right after the 800 K anneal, before the relaxation and passivation. A peroxide formed in the cleave or anneal therefore shows up as such.
  - `iface_audit.py` (new, read-only) applies `iface_partition()` after the fact to any interface cell, the Al2O3 cells included. Their QC files are not changed.
- **MACE-MPA-0** (`mace-mpa-0-medium.model` on EOS, sha256 `75428afe…04fb638`): 89 elements, Hf included (read from `model.atomic_numbers`).
- **Caveat (corrected 2026-10-10 after the verification).** The oxide "melt" holds 3000 K for 4 ps, then quenches over 6 ps, at a fixed 9.6 g/cm³.
  - **Temperature.** 3000 K is just below the measured HfO2 melting point, about 3073 K (Gallington et al., *Materials* 10, 1290 (2017)).
  - **Density.** The box is about 18 % denser than liquid HfO2 (8.16 g/cm³ at 2900 °C, same paper).
  - **Usual practice.** Melt-quench a-HfO2 models normally start from a superheated melt. Wang et al., *PRB* 85, 224110 (2012) used classical MD (not ab initio) at 4000 K, "well above the experimental melting point of around 3000 K", and 7.97 g/cm³. In that work, boxes denser than about 8.4 g/cm³ recrystallised to the cubic form.
  - **The risk.** In production the risk is partial crystallisation during the hold and the quench, not a failure to melt. The verification cites a glass transition near 1500 K (arXiv:2502.03114; not re-checked here).
  - **What can and cannot detect it.** `Hf_CN_hist` and the mean Hf–O bond cannot detect ordering: m-HfO2 is 7-fold, and 7-fold is already 48 % of the smoke layer. The new MSD, Hf–Hf, Hf–O–Hf and interior-density keys are the check.
  - **The density itself.** 9.6 g/cm³ is inside the registered ASSUMED range 9.1–9.7 and is about 95 % of m-HfO2 (10.11 g/cm³). It is not in question.
- **Crystallinity flags (PROPOSED, need the user's or Codex's approval before the production QC is read; reported only).**
  - **No-diffusion flag:** Hf MSD over the 4 ps hold below 1.0 Å². This is an estimate-based threshold. Vibration of a solid at 3000 K gives a few tenths of Å². A melt with D ≈ 1e-5 cm²/s moves about 2.4 Å² in 4 ps.
  - **Ordering flag:** still to be fixed. The candidates are sharp Hf–Hf shells or a bimodal Hf–O–Hf angle distribution, compared with a-HfO2 (Hf–Hf 3.38 / 3.89 Å; Hf–O 2.13 Å; Hf CN 6.8; Gallington 2017).
  - **If a flag is raised.** A register amendment is raised before H-M is used, for example a 4000 K oxide melt. No threshold is changed after the result.

**Additivity proofs (2026-10-10).**
- `make_specs.py`: all 22 existing spec JSONs and `ml_jobs.txt`, `ml_jobs_r1–r3.txt` are regenerated byte-identically; only `spec_aIWO_2p0_HfO2_s1.json` and `ml_jobs_r4.txt` are new.
- `make_dft.py`: for all 17 existing run directories, the new and old code write byte-identical `relax.in`, `final.tmpl`, `relax.sub`, `final.sub`, `steps_*.sh` and `.dag`. For `aIWO_2p0_Al2O3_s2` they also equal the live files, except a hand-edited A15 comment line in `final.sub`.
- `mace_amorph.py`: with an LJ stand-in for MACE and seeded RNGs, old and new code give byte-identical outputs (xyz, qe, qc, md, snapshots) for `aIWO_2p0_Al2O3_s2`, `aIWO_0p7_s1`, `aIWO_0p7_s1_bare` and `aIWO_bulk_s1`. `ut_water.py` still passes. A Hf unit test keeps H2O adsorbed on Hf and removes free H2O.

**Smoke test (2026-10-10, lxplus913 CPU, real MACE-MPA-0, `--quick`: 1.65 ps of MD, relaxations capped at 40 steps; not a production structure, nothing submitted).**
- Every stage ran: the a-HfO2 layer, the film melt with the oxide fixed, the cleave, the anneal, passivation, `remove_water()` and `qc()`. Exit code 2 (QC FAIL), with 423 atoms (Hf46 In98 W2 O255 H22).
- **Passivation.** 22 groups (11 OH + 11 H), with OH on Hf, In and W sites. Per face: 7 OH + 6 H on the film top and 4 OH + 5 H on the oxide face. *(Corrected: 13 and 9 are the group counts per face, not OH counts.)* No sites were left unpaired and no water was removed.
- **a-HfO2.** Hf CN mean 6.43 (CN 5: 2, CN 6: 22, CN 7: 22). Mean Hf–O 2.149 Å.
- **Closest contacts:** Hf–O 1.899, Hf–Hf 3.143, Hf–In 3.05, Hf–H 2.34 Å. All are above the new limits.
- **Film.** In CN 5.55, mean In–O 2.226 Å, W CN 6/6.
- **"Intermixing" (corrected 2026-10-10; the first wording said "one In on the outer face" and called the Al2O3_s2 count comparable intermixing, which was wrong).** The QC counted 5 film cations in the oxide and 2 Hf in the film. Taken apart:
  - **4 In on the outer HfO2 face** (atoms 159, 180, 191, 206). They sit −0.7 to +0.6 Å from the lowest Hf, which puts them 9.2–10.4 Å below z_if = 20.68 Å.
  - **6 film-origin O beside them** (atoms 262, 311, 322, 323, 375, 382). Together with the 4 In this is an In4O6 fragment, 2.4 In/nm², on the back of the 1 nm HfO2. In 191 carries one of the 4 OH on the oxide face.
  - **How it got there.** The periodic film melt lets the film top touch the oxide bottom across the z boundary, and the cleave 1 Å below the oxide keeps that material.
  - **The other counted atoms are at z_if by definition.** The fifth In (153) is 0.05 Å below z_if. The 2 "Hf in film" are 0.09 and 0.27 Å above it.
  - **Buried-interface exchange** (more than 1 Å past z_if): none.
- **The same artefact in the Al2O3 cells** (`iface_audit.py`, 2026-10-10, read-only on `~/iwo_amorph/results`):

  | Cell | Outer-face film material | Buried exchange |
  |---|---|---|
  | `aIWO_2p0_Al2O3_s2` (QC PASS, now in DFT) | all 5 counted cations are In on the outer Al2O3 face, within ±0.6 Å of the lowest Al; 9 film-origin O; 3.0 In/nm². Its "Al in film" is within 1 Å of z_if | none |
  | `aIWO_2p0_Al2O3_s1` | 4 of 4 In, 6 O | none |
  | `aIWO_1p0_Al2O3_s2` | 2 of 2 In, at 10.3 and 7.8 Å below z_if; 10 O | none |
  | `aIWO_1p0_Al2O3_s1` | 2 of 2 In, 6 O | none |

  - **Consequence.** Any oxide-side or z_if-based "interface weight" (the H-I and H-M interface-state test) would count this outer-face material as interface atoms.
- **Failure reasons (corrected 2026-10-10).**
  1. **One O–O contact of 1.446 Å.** This is a peroxide on the outer oxide face, and it formed during the cleave and the 800 K anneal, before the capped relaxation and before passivation.
     - In `slab_annealed` (right after the anneal), O 74 and O 262 are already 1.409 Å apart. O 74 is a substrate O, on Hf 41 at 2.24 Å. O 262 is a film-origin O carried to the outer face, on Hf 7 at 2.40 Å.
     - In `quenched_300K` (before the cleave), the shortest O–O is 2.301 Å.
     - Passivation then put an H on O 74 (H 413, 0.98 Å), which gives an HO–O species. No added-OH oxygen is part of the pair.
     - *Corrected:* the first wording, "an added OH on that In ... with the relaxation stopped by the 40-step cap", was wrong. The cap is not the cause.
  2. **Vacuum 14.6 Å.** That alone is fixed in `make_dft.py` (§6).
- **What this does and does not show.**
  - The quick schedule held 3000 K for only 0.2 ps, so it says nothing about the production 4 ps hold.
  - The peroxide is not a schedule artefact. Outer-face film material is a peroxide source, and the same QC failure (O–O 1.51 Å) rejected the full-schedule `aIWO_0p8_s1`. **The production QC can therefore fail for real**, and §7 then applies, with the replacement seed fixed below.
  - The production QC reports where any O–O contact sits (`OO_contacts_below_limit` in the final structure and in `slab_annealed_diag`), so a recurrence at recipe level is visible.

**Replacement seed (fixed 2026-10-10, before the production result).** This follows the §7 "next seed" rule and changes no rule.
- If `aIWO_2p0_HfO2_s1` (seed 902) fails QC, its replacement is `aIWO_2p0_HfO2_s2`, seed 903.
- A second rejection gives s3, seed 904.
- This is also recorded in the H-M section of the register.

**Hf force check (A21): `dft/make_val.py --list` (added 2026-10-10).**
- **Command:** `python3 make_val.py --list hfo2 aIWO_2p0_HfO2_s1:quenched_300K,slab_annealed,final` (A21 asks for two to three snapshots).
- **Before the fix,** `make_val.py` treated mode `interface` as bulk. The vacuum frames would have got k 2×2×2 with no dipole correction, and a run would have overwritten `val/val_jobs.txt` and `val/val.sub`.
- **Now:**
  - **Vacuum frames** (after the cleave: `slab_annealed`, `final`) get the relax settings: 60/480 Ry, MV 0.01, k 2×2×1 and the dipole correction.
  - **Periodic frames** (`melt_3000K`, `quenched_300K`) get no dipole correction and the KSPACING density on all three axes, which is 2×2×1 for the 12.91 × 12.91 × 30 Å box.
  - **Output.** Jobs go to `val/val_jobs_<list>.txt` and `val/val_<list>.sub`. The default path refuses interface cells, and without `--list` every output is unchanged.
  - **Resources:** those of the relax of the same cell, from the `make_dft.py` rule. Above 350 atoms that is 4 H100/H200, 32 CPUs, 128 GB and `QE_NK=1`, and the job runs on QE 7.3.1 GPU, the same as the relax. A 400-atom CPU SCF would not fit in the 100 GB of `val.sub`.
  - **No wavefunction save.** `disk_io = 'nowf'`, because the save would be about 60 GB. It does not change the forces.
- **Checked on the A18 smoke snapshots** (inputs only, in `/tmp`):

  | Frame | Atoms | Box c | k | Dipole |
  |---|---|---|---|---|
  | `melt_3000K`, `quenched_300K` | 390 | 30.05 Å | 2×2×1 | no |
  | `slab_annealed` | 390 | 50.05 Å | 2×2×1 | yes |
  | `final` | 423 | 50.05 Å | 2×2×1 | yes |

**Final-SCF memory (OPEN; must be settled before any FINAL release).**
- **The request.** `final.sub` asks for 100 GB for every cell. It has not been tested at this size: no amorphous final has run yet (A15 hold).
- **The HfO2 cell** (from the smoke structure): 423 atoms, 3406 electrons, nbnd 2214. For comparison, `aIWO_2p0_Al2O3_s2` has 2966 electrons and nbnd 1928.
- **Estimate** at 71 Ry, 4 k-points and c ≈ 51 Å: about 5.9e5 plane waves per k. The wavefunctions alone are then about 21 GB per k-point, or about 83 GB for the 4 k-points, and QE's Davidson work arrays come on top. The total is expected well above 100 GB.
- **Measured anchors and pools (added 2026-10-11).**
  - QE's own estimate in the RELAX checkpoints of the running cells (60 Ry, default nbnd, one process, 4 k; `dft/TODO_D24_make_dft.md` §3) is 82–86 GB at 149–155 atoms and 130–173 GB at 252–274 atoms. The final runs at 71 Ry with nbnd = 1.3 × occupied, which is larger still.
  - The final SCF uses the default Davidson solver, and `steps_final.sh` runs 4 pools on 32 CPUs (`-nk 4`). All 4 k-points are therefore diagonalised at once, each pool with its own Davidson work space (ψ, Hψ, Sψ over 2 × nbnd vectors by default, about 6 × the wavefunctions of one k-point).
  - For the 423-atom HfO2 cell this gives an order of magnitude of 0.5 TB with `-nk 4` and about 200 GB with `-nk 1` (estimates; QE's figure settles it).
  - Conclusion: 100 GB is too small for this cell and for `aIWO_2p0_Al2O3_s2` (414 atoms, nbnd 1928). The D-24 note reaches the same conclusion for every cell.
- **How to settle it.** Read the relax output's "Estimated total dynamical RAM" (scaled to 71 Ry and nbnd), then make a per-cell change: `condor_qedit` of the held FINAL, or a per-cell value in `make_dft.py`. Either way the 17 existing run directories stay byte-identical.
- The D-24 note (`dft/TODO_D24_make_dft.md`) flags the same issue for disk.

**OPEN DECISION for the user or Codex (finding: outer-face artefact).** The recipe is frozen, so either option needs a register amendment. It should be decided before the production go.
- **(a) Change the recipe.** Add a barrier above the film top during the film melt (a vacuum gap or a fixed wall), so the film cannot wet the oxide's bottom face. H-M would then differ in recipe from the Al2O3 cells it is compared with.
- **(b) Keep the recipe.** Define the H-I and H-M "interface weight" to exclude the outer oxide face (z below the lowest substrate cation + 3 Å, `iface_partition()`), fixed before any DFT result is read.

**Additivity proofs, verification fixes (2026-10-10, lxplus913 `/tmp/melrashe-a18/fix`).** Nothing under `~/iwo_amorph/runs`, `results`, `val` or `vac` was written.
- **`mace_amorph.py`** (LJ stand-in for MACE, seeded RNGs):
  - pre-A18 code against the fixed code gives byte-identical outputs (xyz, qe, qc, md, snapshots) for `aIWO_2p0_Al2O3_s2`, `aIWO_0p7_s1`, `aIWO_0p7_s1_bare` and `aIWO_bulk_s1`;
  - for `aIWO_2p0_HfO2_s1`, A18 code against the fixed code: xyz, qe, md and snapshots are byte-identical, and the qc.json keeps every A18 key with its value and order and only adds the new keys;
  - `ut_water.py` passes, and the Hf unit test gives the same result as before.
- **`make_val.py`:** regenerating the 8 existing validation inputs (26 files) gives files identical to the old code's output and to the live `val/`, once the scratch root is substituted in `val.sub`.
- **`make_dft.py`, `make_specs.py`:** not changed.

**Fresh regression, smoke re-run and CERN install (2026-10-11).** Code under test (sha256): `mace_amorph.py` `3049c3b3…5211`, `dft/make_val.py` `a61f769f…7bfe`, `iface_audit.py` `dbc715ea…ed12`. Run on lxplus913 in `/tmp/melrashe-a18/fix2`; nothing under `~/iwo_amorph/runs`, `results`, `val` or `vac` was written.
- **LJ regression, every spec** (LJ stand-in for MACE, seeded RNGs, `--quick`):
  - pre-A18 code against the fixed code: byte-identical xyz, qe, qc, md and snapshots, and the same exit code, for **all 22 existing specs** (110 files);
  - `aIWO_2p0_HfO2_s1`, A18 code against the fixed code: xyz, qe, md and snapshots identical; the qc.json keeps every A18 key with its value and order and only adds the new keys.
- **`make_val.py`:**
  - the 8 existing validation inputs (26 files) equal the old code's output and the live `val/` (after the scratch root is substituted in `val.sub`);
  - the default path refuses the interface cell and writes nothing;
  - `--list hfo2` on the re-run smoke snapshots writes 4 inputs (390, 390, 390, 411 atoms). All have k 2×2×1 and `disk_io = 'nowf'`; only `slab_annealed` and `final` get the dipole correction. `val_hfo2.sub` asks for 4 GPUs, 32 CPUs, 128 GB and `QE_NK=1`. `val_jobs.txt` and `val.sub` are not written.
- **Unit tests:**
  - `ut_water.py` passes;
  - the Hf unit test gives the same result with the A18 code and the fixed code;
  - a new test of `remove_water(atoms, deleted)` checks that the origin labels stay aligned after a deletion. The smoke removed no water, so it did not exercise that path.
- **Smoke test re-run with the fixed code** (2026-10-10T21:24–22:53Z, lxplus913 CPU, real MACE-MPA-0, `--quick`; not a production structure, nothing submitted). Every stage ran and every new key was written.
  - **Result.** Exit 2. The only QC failure is the vacuum (14.45 Å; §6). 411 atoms (Hf46 In98 W2 O251 H14).
  - **Passivation.** 14 groups (7 OH + 7 H). 9 under-coordinated cations stayed unpaired because no further O qualified. No water was removed. The first smoke had 22 groups and none unpaired.
  - **The two smoke runs are different trajectories.** The seed fixes the random packing and the initial velocities. The Langevin noise, however, comes from numpy's unseeded global generator (an unchanged property of the recipe), so a second run of the same spec gives a different structure.
  - **Outer-face artefact, again.** 4 In (153, 160, 192, 226) sit between −0.9 and +0.7 Å from the lowest Hf, with 6 film-origin O beside them (2.4 In/nm²). They are already there in `slab_annealed`. The QC count `n_film_cations_in_oxide` = 4 is exactly these four. There is no buried exchange, and nothing within 1 Å of z_if.
  - **No O–O contact below 2.15 Å** (shortest 2.36 Å in the final structure, 2.21 Å after the anneal). The first smoke's peroxide did not recur in this run. With one run each, no rate follows.
  - **a-HfO2, final structure.**
    - Hf CN 6.17 (CN 5: 8, 6: 25, 7: 10, 8: 3).
    - Hf–O bonds: n 284; p5, p50 and p95 1.986, 2.115 and 2.355 Å; max 2.555 Å; std 0.114 Å.
    - Hf–Hf: first peak 3.35 Å, shortest 3.00 Å.
    - Hf–O–Hf: mean 112°, mostly 90–110°, with a tail to 160–170°.
    - Interior density 8.69 g/cm³ (window 12.7–18.9 Å).
  - **Limits of these numbers.**
    - The interior density is noisy: its window holds about 75 atoms, and the same function gives 9.53 g/cm³ on the first smoke's final frame.
    - The quick 0.2 ps hold (Hf MSD 0.18 Å², O 0.34 Å²) says nothing about the production 4 ps hold.
- **CERN install (2026-10-11T00:09:57Z).**
  - `~/iwo_amorph/mace_amorph.py`, `~/iwo_amorph/common/make_val.py` and the new `~/iwo_amorph/iface_audit.py` now equal the local files: same sha256 as above, LF line endings.
  - The previous versions are kept as `mace_amorph.py.pre_A18fix` and `common/make_val.py.pre_A18fix`.
  - The ML jobs transfer `~/iwo_amorph/mace_amorph.py`, so the production HfO2 build will write the new keys.
  - No queued or running job reads either file at run time. The 8 queued validation jobs use their prepared inputs.

**Status.** The spec, `ml_jobs_r4.txt` and the fixed code are in place on lxplus, and nothing has been submitted. The production ML job (an `ml_r4.sub` analogue of `ml_r3.sub`) waits for the user's go. That go should come after the OPEN DECISION above and the approval of the proposed crystallinity flags. The final-SCF memory must be settled before any FINAL release.

**Production ML submission (2026-10-11T00:27:03Z, cluster 12888137).**
- **How.** `~/iwo_amorph/ml_r4.sub` was made from `ml_r3.sub` by changing only the job list (`ml_jobs_r3.txt` to `ml_jobs_r4.txt`, comment and `queue` line; sha256 `c341d9d2…e8e4`, identical to `ml.sub` with the list renamed). A local copy is `compute/amorph/ml_r4.sub`. It was submitted from `~/iwo_amorph` with `condor_submit ml_r4.sub`, as r1–r3 were. `condor_submit -dry-run` was checked first.
- **Inputs, checked before the submit.** Local and CERN copies are identical (sha256, LF): `mace_amorph.py` `3049c3b3…5211`, `ml_driver.sh`, `ml_jobs_r4.txt`, `spec_aIWO_2p0_HfO2_s1.json` (seed 902, Hf46O92 under In98W2O152, L 12.91 Å), `collect.sh`, `common/make_dft.py` `2312362d…63f1`, `common/make_val.py`, `iface_audit.py`. The Hf PAW in `common/pseudo/` has the sha256 above. The MACE env and model are on EOS.
- **Job.** 1 process, `IWOJob = aIWO_2p0_HfO2_s1`, 1 GPU (A100, H100 or H200), workday flavour. The schedd changed the request to 6 CPUs and 18000 MB, as it did for the r3 job 12884291. Logs: `logs/aIWO_2p0_HfO2_s1.12888137.{out,err}`, `logs/ml.12888137.log`. Output: `~/iwo_amorph/aIWO_2p0_HfO2_s1_ml.tar.gz`.
- **Queue check.** The queue was compared before (00:26:44Z) and after the submit. Exactly one new job, 12888137.0, was added, and it is idle. Every other job kept its status: 32 jobs in total, 24 idle, 6 running and 2 held (the 2 held were held before). No job was held, released or removed.
- **What `collect.sh` will do later.** It is run by hand; lxplus has no crontab for it. The first run after the tarball arrives unpacks it to `results/aIWO_2p0_HfO2_s1/`. If the QC is PASS, or a FAIL for vacuum only, it then calls `python3 common/make_dft.py aIWO_2p0_HfO2_s1` and `condor_submit_dag -batch-name aIWO_2p0_HfO2_s1` in `runs/aIWO_2p0_HfO2_s1/`. Any run of `collect.sh` does this, so it should not be run until the open items below are settled.
  - **Expected size.** 390 atoms before passivation; the two smoke builds had 411 and 423. The relax therefore gets `ngpu = 4` (more than 350 atoms): H100/H200 only, 32 CPUs, 128 GB, `QE_NK=1`, flavour tomorrow, 72000 s segments, `RETRY RELAX 8`.
  - **FINAL.** On the CPU (32 cores, 100 GB, testmatch, 250000 s), submitted **on hold**: `final.sub` carries `hold = True` with the A15 comment line. The A15 gate is therefore in place.
  - **Not in place.** `make_dft.py` has not had the D-24 edits (`dft/TODO_D24_make_dft.md`, `dft/TODO_D24_BD_make_dft.md`). This chain would get the pre-D-24 relax continuation, a DAG without `UNLESS-EXIT 2`, a `final.tmpl` with verbosity 'low' and the 100 GB / 60 GB final request (final-SCF memory, OPEN above).
- **Still open at submission. These were not recorded as decided in the register, the decision log or the work chat.**
  - The outer-face decision, (a) or (b).
  - The approval of the proposed crystallinity flags. They must be fixed before the production QC is read.
  - The final-SCF memory.

**DECIDED 2026-10-11T03:13Z (D-26, register A24).** The open outer-face decision is option (b): the recipe is kept, and the outer oxide face (z < lowest substrate cation + 3 Å) is excluded from the H-I/H-M interface weight and from z_if for all interface cells. The crystallinity flags are approved; the ordering flag is fixed as a Steinhardt q6 test (see A24). Still open before `collect.sh` may be run: the final-SCF memory request and the D-24 changes in `make_dft.py`.
