# 06 Adversarial verification of numbers, calculations and citations in PLAN_C10_S2_S5_2026-10-14.md (2026-10-14)

Scope: every number in `PLAN_C10_S2_S5_2026-10-14.md` (900 lines) checked against its sources. Read-only. No ATLAS run, no CERN contact, no commit. Outputs of run_0075/0076/0077 were not opened. Only `RUN_INDEX.csv` rows and the allowed scored file `register_scores/hc_mesh_run_0076_run_0067.json` were read. Nothing under `sealed/` and no amorphous DFT quantity was read. All recomputation used `IWO_ATLAS_Model_claude/.venv/Scripts/python.exe`; the scripts are in the session scratchpad (`chk.py`, `s211.py`, `s211b.py`, `fn.py`). Citations were checked through Crossref metadata (api.crossref.org) plus web search.

Tags:
- **MUST-FIX**: a wrong number or claim that a headline conclusion depends on.
- **SHOULD-FIX**: a wrong or mis-scoped number, unit or citation detail; the conclusion survives.
- **REPORT**: imprecision or scope to disclose.

## A. Defects

### MUST-FIX

**M1. The SRH/TAT generation bound is quoted for the wrong parameter set.** Locations: §1.4 row "S2 generation", §3.3 NV300, §3.5 τ row, §3.9, R1.
- The plan says SRH and trap-assisted generation cannot produce the floor, "≤ 1.1e-27 A/µm … at least 12.6 decades below the 2.0 nm floor".
- Evidence: the figure is the GENERATOR_AUDIT §7.1 bound, 8.0e-29 A/µm (13.2 nm), multiplied by √(1.93e21/1e19) = 13.9. GENERATOR_AUDIT l.250 shows it uses σ = 1e-15 cm², v_th = 1.08e7 cm/s and no field enhancement. The bound G ≤ n_i·σ·v·N_t/2 is linear in σ and v.
- The S2-01/03 decks use σ = 1e-13 cm² (×100) with TRAP.TUNNEL/HURKX. CALCULATED with σ 1e-13, v_th(m*) = 2.32e7 / 2.54e7 cm/s and COMPUTED N_v:
  - 2.0 nm: ≤ 3.0e-28 A/µm;
  - 13.2 nm: ≤ 2.6e-25 A/µm.
- Against each film's own floor that is ≥ 13.2 dec (2.0 nm) and ≥ 13.4 dec (13.2 nm). Against the 2.0 nm floor, as the plan compares, the 13.2 nm value is only 10.2 dec below.
- The Hurkx enhancement factor Γ is not bounded by any calculation.
- Correction: quote the bound at the S2 extreme settings, per film. State "without field enhancement; the floor needs Γ ≳ 1e13".

**M2. The headline "plan path fits with one spare" rests on an undisclosed assumption.** Locations: §1.2 assumptions list, §4.3.
- Block I uses "plan" = 17 = S6 12 (the early exit) + S7 2 + repairs 3 (consistent with `01` §6: S6 12 → 1.60 h).
- The S6 early exit requires "S4 failed and S5 confirms it on ≥ 2 folds" (§2.9). Yet the listed assumptions say "S4b runs in full" and do not mention S6.
- With S6 in full (22), the totals are 180 (campaign) and 192 (grand), above the 183 available (CALCULATED).
- Correction: add "S4 fails and S5 confirms it (S6 early exit)" to the plan-path assumptions, or show 192 > 183 and the cut that applies.

### SHOULD-FIX

**S1. DIAG hours (§2.2 "DIAG total about 6.3 h", §1.2 B, §4.5).**
- The plan's own per-entry B1–B18 "h" column sums to **6.49 h** (CALCULATED). `01` uses 5.58 + 0.70 = 6.28 h.
- The campaign total is 32.9 h and the grand total is 32.9 + 2.5 = **35.4 h**, so "≈ 36" should read "≈ 35".

**S2. S5 fold hours are swapped (§2.8).**
- In the stated fold order: H6p3 = (4·(395.8 + 735.4) + 2·493.7)/3600 = **1.53 h**, H2p0 = **1.59 h**, H13p2 = 1.40 h.
- The plan prints 1.59 / 1.53 / 1.40.

**S3. Floor-window medians (§2.5 item 3).**
- The plan has "6.5 and 6.1 dec below the 2.0 nm floor". These are lower medians of the 16 window points.
- The conventional median (np.median, the convention the floors themselves use, generator l.317) gives **6.65 (×1) and 6.24 (×0.5) dec** (CALCULATED from the allowed JSON).

**S4. Single-subband margin (§3.3 E21).**
- 0.7191/0.158 = **4.55**, so "at least 4.6×" should read "≥ 4.5×".
- The 0.120 eV case gives 5.98×.

**S5. The S6 early-exit saving (§4.1).** It is ≤ **10**, not ≤ 12, because S6-13/15 are never cut (§4.4): 22 − 12 = 10.

**S6. Block F minimum (§1.2).**
- The minimum is **7**, not 9, when IGZO is inactive after the fallback: F1 + re-run + F5 + 4 tails.
- The campaign minimum becomes 136.

**S7. HfO2 χ range (§3.6, §3.11 item 2).**
- The plan says "LITERATURE 2.05–2.75 eV (R&W 2015; Monaghan 2009)". That range excludes Monaghan's own value, χ = 2.0 ± 0.25 eV (confirmed from the abstract).
- Correction: 2.0–2.75 eV (`03` C2), or 1.75–2.75 eV with Monaghan's σ.

**S8. "×2.0–3.2" from χ 2.5 → 2.55 eV (§3.6).**
- This is CALCULATED at E_HfO2 = 3–5 MV/cm (`02` F5). At V_G = −3 V the HfO2 field is only ≈ 1.6–1.8 MV/cm (V_ox ≈ 3.0–3.43 V over 15 + 2·19.57/9 nm). At that field the FN ratio is **×6.9–9.0** (CALCULATED).
- This is still immaterial against the 9-decade margin.

**S9. ATLAS capture-σ default (§3.5).**
- The plan says "default is 1e-16 cm²". Manual l.48761–48781: SIGTAE/SIGGAE/SIGTDH/SIGGDH = 1e-16, but SIGTAH/SIGGAH/SIGTDE/SIGGDE = **1e-14** cm².
- A software default is better labelled ASSUMED (default) than LITERATURE.

**S10. Author initials (Crossref).**
- "T. Prodhomme" should be **P.-Y. Prodhomme**. The article number 022101 is now verified, so its UNVERIFIED tag can be dropped.
- "C. Oh" should be **Y. J. Oh** (Oh, Lee, Noh, Chang).
- "J. Fung" should be **T.-C. Fung**.
- "D. R. Perevalov" should be **T. V. Perevalov**. The paper treats **α-Al2O3**, and its 0.22–0.42 m0 range is quoted from secondary sources.

**S11. Unit mismatch (§3.5).**
- "N_s 4e12 cm⁻² … in range of … 3.3e20 cm⁻³eV⁻¹" compares a sheet density with a volumetric DOS per eV. Compare NTA instead (5.0e20 cm⁻³eV⁻¹ at 2.0 nm). Wang 2022 is a mean subgap DOS from the conductance method, not a tail peak.
- The "about 6e11" for D_it needs units: cm⁻²eV⁻¹.

**S12. ε_IWO 9.30 ± 0.04 (§3.2).**
- This comes from the same unbundled SI as ε_HfO2. `02` F14 marks both UNVERIFIED here, but the plan flags only ε_HfO2.

### REPORT

- **R1.** m*(2 nm) multiplicative: with the law Δm at t = 2.0 nm it is **0.2686 m0 (+5.6 %)**. The plan's 0.270 (+5.7 %) uses the DFT point at t_HH = 1.962 nm against 0.2554. Against the plan's 0.25429, 0.270 is +6.2 %. The NC equivalent (1.4 meV) is unchanged.
- **R2.** HfO2 nominal 1/κ = 0.294 nm is the TiN side (2.2 eV) only. The IWO side (1.518 eV) gives 0.354 nm, and the worst range includes both sides.
- **R3.** run_0075: RUN_INDEX shows **elapsed 6,060 s** against timeout = 5,400 s. "Held until its 5,400 s timeout" understates the MEASURED wall time.
- **R4.** "n_i ≈ 1e-7 cm⁻³" (§2.1, R2) uses NV300 = 1e19 (ASSUMED). With the COMPUTED N_v it is 9.75e-7 cm⁻³ at 13.2 nm (CALCULATED).
- **R5.** S2-11 was not a uniform halving. The scorer record says "Al2O3 about ×1.5, HfO2 about ×2" (the y = 0 line is kept). Likewise T1a against S2-11: Al2O3 22 → 32 intervals (×1.44), HfO2 55 → 111 (×2) (CALCULATED by geometric grading). The node counts 182–184 × 117 and 3.75–3.79 GB reproduce.
- **R6.** T2a "121 × 71" holds only if the qty.mesh enclosure shrinks from 0.5 nm (run_0066: loc −0.0005 / 0.0175 µm) to 0.25 nm. That is a second change. Keeping run_0066's locations gives 121 × 73 = 8,833.
- **R7.** Inconsistent minimum convention:
  - D min = 3 assumes PA-4 approval;
  - E min = 0 assumes PA-5 refusal;
  - G min = 63 includes the 3-D NC branch (PA-11, unbudgeted).
- **R8.** "Flatness fails … by more than 11 decades" (§7.6) confuses the |I_G| span (11.6 / 12.2 dec, verified) with the registered slope criterion, which is in dec/V.
- **R9.** The branch's planned 3 / max 5 launches exceed the bounded proposal in Codex 03:36Z (one refinement plus one conditional, "two extra launches"). The QT-mesh series is the user's addition, and the plan should say so.
- **R10.** Not re-verified here: R&W 2015 Table 1 "ALD Al2O3 K 8, E_g 6.4 eV, CBO 1.6 eV". The full text was not accessible to this check (`03` C3 records it as verified from the accepted manuscript). Michaelson's Pd value of 5.12 eV is still UNVERIFIED. The other measured Pd values found, 4.97–4.99 eV (DuBridge & Roehr 1932), give a Schottky–Mott estimate of 0.67–0.69 eV.

## B. Verified correct (CALCULATED unless stated)

- **Launches:**
  - 17/200 used, 183 remain, 77/260 (RUN_INDEX: 77 unique ids; solver.yaml max_launches 260);
  - 11/185 matrix entries;
  - reserve 9/3 (register l.1861);
  - block sums 138/170/210 and 150/182/242; R_need 113/142/145;
  - S4a 6.32 h, 3-D NC 1.65 h, S4b 2.71 h, triple 0.451 h.
- **Runtime factors:** QTNLSC ×3.148 = 1246/395.8; ×2.43 = 1786.5/735.4; B1 0.35, B2 0.64, B7 0.45, B8 0.84 h; DIAG timeout sum 10.42 h. The DIAG/S3/S6 timeouts match the matrix.
- **S2-11 (from the allowed JSON):**
  - 73/75 points > 0.1 dec; maximum 2.858 dec; 0.315 dec at −3 V;
  - |I_G(−3 V)| 2.75e-12 / 5.67e-12 A/µm;
  - spans 11.62 / 12.23 dec;
  - offsets from the floor: −2.0 V +0.26 / +0.50, −1.8 V −0.81 / +0.70 dec;
  - V_G ≥ −0.45 V: −0.44 to −0.17 dec, median −0.351 (n = 54); floor window −0.49 to +2.86 dec;
  - 2.86/11.62 = 0.246; R = 2.20233e-31 A/µm.
- **Floors and margins:** floor ratio 1431.67, exponent 3.8507; margins 12.62 and 9.66 dec (arithmetic).
- **Constants:** kT 0.025852 eV; A* 120.173.
- **Electrostatics:** C_ox 8.95537e-7 F/cm²; ε_Al2O3 at 8/7/11 gives −2.73 / −6.03 / +4.26 %; ΔV_FB −0.24751 V; ±2.7948e12 cm⁻².
- **DFT laws:**
  - ΔE_c 0.28161/0.06216/0.02347 eV, AFFINITY 4.01839/4.23784/4.27653 eV;
  - ΔE_g and EG300 as stated; Δm 0.04629/0.01086/0.00426; m* 0.25429/0.21886/0.21226;
  - NC 2.38049e18 / 2.56928e18 / 2.45405e18; quasi-2D 1.37306e19; −37.51 meV; F½(4.7)/ln(1+e^4.7) = 1.723;
  - E21/kT 27.82; E_F − E1 0.1203/0.1578 eV.
- **Transport and traps:**
  - mass factors and 0.8347; μ_band 17.6897/63.2597 (anchors); MUN 12.977/40.2607/60.5388 and 15.865/42.362/61.7795; 24.1564; 2.38345e12;
  - N_t and NTA; T_t 464.18 K; merged Gaussian 1.16757e19 / 0.30155 / 0.123975 (ATLAS form exp[−((E−E0)/W)²]);
  - 50:50 NTA 3.29365e20 / 2.87879e20.
- **Oxide, strip and Schottky:**
  - v_th(0.2543) 2.316e7 cm/s, and the printed vn 1.08e7 is in run_0067 `deckbuild.out`;
  - FN A/r² 2.1734e-6 (0.11 % from 2.171e-6, as disclosed), B·r 8.629e7 V/cm, r 2.17444;
  - 1/κ Al2O3 0.198–0.229 nm, HfO2 0.504–0.682 nm; step ratios 1.47–3.40 / 0.73–1.70;
  - strip 1.02134;
  - work functions 4.2184/4.4378/4.4765 and 4.5184/4.7378/4.7765 eV; ARICHN 30.559/26.301/25.508; VSURFN 1.250e6 / 5.335e6 (×0.2344);
  - image-force lowering 0.0393/0.1244/0.2006/0.2155 eV; Schottky–Mott 0.82 eV.
- **IGZO and temperature:** γ 0.8947 and 0.2847/0.2176/0.1881; NC.F errors 1.744 / 2.734 meV.
- **P4:** dEc 0.7015 / 1.0245 eV; 0.199 / 0.220 V.
- **Memory and mesh:** 2.41, 3.75–3.79, 2.84 and 4.23 GB; grading 15 + 28 = 43 → 77.6 → 142.9 oxide intervals; node counts 9,594 = 117 × 82, 12,051 = 117 × 103, 13,689.
- **QT grid:** 4,477 = 121 × 37, as run_0066 device.in qtx/qty lines show.
- **Al2O3/HfO2 barriers:** 2.85/2.25, 2.168/1.568, 3.10/2.418 eV; 2.55 eV; 3σ.
- **n_i and N_v:** 5.0e-10 / 7.0e-8 cm⁻³; ×13.9.
- **run_0073:** 22 / 20 / 2 convergence warnings, verified in its `deckbuild.out`.
- **Register and manual:**
  - H-E −0.13 ± 0.03 (−0.23 ± 0.04), −0.272 ± 0.010, −0.062 ± 0.015, −0.023 ± 0.008, −281.6 / −62.2 ± 5 mV (register l.185–197);
  - H-J 0.25–0.65 (l.297);
  - design D5 84/69;
  - manual 5.28 lines 3826–3828 (NC.F 1.5), 8250–8262 (IGZO defaults), 13505–13507, 13660–13677, 14499–14505, 14730 (TAT.SLICEPTS 12), 34791–34792 (BQP 1.2/0.5), 34851–34857, 58524–58526, Table 3-132 QTUNN.CMASS 1.0; 2004 l.8700–8703.
- **Citations verified (Crossref metadata; values where checked):**
  - Januar et al., Small Struct. 7(2) e202500807 (2026);
  - Robertson & Wallace, MSE R 88, 1–41 (2015);
  - Robertson, JVST B 18, 1785 (2000);
  - Tiesinga, RMP 93, 025010;
  - Stokey, JAP 129, 225102 (ε_DC 10.55 ± 0.07, m* 0.208 ± 0.006, abstract);
  - Fan, Nanomaterials 11, 3070 (4 nm a-IWO on HfO2);
  - King, PRL 101, 116808 and PRB 79, 205211;
  - Hohmann, JPCM 23, 334203 (IP ≈ 7.0 eV for (111), ≈ 7.7 eV for (100));
  - Feneberg, PRB 93, 045203;
  - Wang, Front. Mater. 9, 850451 (3.3e20 cm⁻³eV⁻¹);
  - Si, Nano Lett. 21, 500; Lin, ACS Nano 16, 21536;
  - Monaghan, SSE 53, 438 (χ 2.0 ± 0.25 eV, m 0.11 ± 0.03 m0);
  - Cimino, MEE 95, 71–73 (2012; the 2011 DOI is correct);
  - Lenzlinger & Snow, JAP 40, 278;
  - Padovani & La Torraca, MEE 281, 112080 (on the SiOx/HfO2 first-to-fail figure of merit; the trap values stay UNVERIFIED);
  - Ielmini, TED 47, 1258 and 1266;
  - Hurkx, TED 39, 331;
  - Michaelson, JAP 48, 4729;
  - Iannaccone, Curatola, Fiori, SISPAD 2004, pp. 275–278;
  - Abe, TSF 559, 40–43;
  - von Wenckstern, APL Mater. 2, 046104;
  - Fung, JAP 106, 084511.

Sources: [Crossref API](https://api.crossref.org/works/), [Monaghan 2009 record (UCC)](https://research.ucc.ie/en/publications/determination-of-electron-effective-mass-and-electron-affinity-in/), [Hohmann 2011 (PubMed 21813943)](https://pubmed.ncbi.nlm.nih.gov/21813943), [DuBridge & Roehr, Pd work function (Caltech)](https://resolver.caltech.edu/CaltechAUTHORS:DUBpr32a).
