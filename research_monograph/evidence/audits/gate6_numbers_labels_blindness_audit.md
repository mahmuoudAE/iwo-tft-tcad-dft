# Gate 6 review 2: numbers, labels and blindness audit of the monograph (M00–M15, MG, MH)

Reviewer: independent subagent, read-only, 2026-10-14. Report reproduced verbatim below; the disposition of each
finding (verified by the main session before any edit) is at the end. Line numbers refer to the draft before the
Gate 6 corrections (commit ab428e8).

---

AUDIT REPORT (read-only; nothing edited, created or committed; no blind path opened). Paths below are relative to research_monograph/ (chapters/ or appendices/). Severity descends within each group.

SUMMARY. No numeric mismatch of consequence: every ledger, FACT_REGISTRY, RESULTS_LOG and derived-JSON value I tested matches. The real problems are LABEL-UPGRADES in M15, with spill-over into M10, M11 and M01. There is no amorphous electronic-outcome leak. Two borderline blindness wording items and about ten minor inconsistencies are listed. All 17 page-numbered citations check out against the digests.

A. LABEL-UPGRADE

1. M15:180-182 (keyresult) and M15:48-50 | LABEL-UPGRADE | The keyresult says "the published mobilities are saturation-formula numbers". The ledger has C031 INFERRED ("leading candidate, no probability stated") and C024 UNRESOLVED. C024's history says "numerical reconciliation is sufficient, not a recipe identification". The "Strongly supported" item 3 (M15:48-50) also rests on C031. Under M15:9 ("listed under the weakest class that any of its parts falls into") it belongs under "Plausible". M07:110-113 and MG:146-149 word it correctly. | Fix: "reproduced numerically by the saturation-formula peak, the leading candidate for the paper's definition (INFERRED)". Move the item to "Plausible".

2. M15:55-56 (and M10:162-169, M10:177-179) | LABEL-UPGRADE | H-L is listed under "Strongly supported" ("W raises the energy of a neutral oxygen vacancy... 0.73 eV"), but C038/RESULTS_LOG say "H-L overall UNRESOLVED. Do not write 'H-L supported'". ΔE_dop is only "PASS under registered settings". A20(i) spin is UNASSESSED. ΔE_dop "mixes local chemistry, strain, band filling and image effects". M10:163 says "ΔE_dop is k-converged within 3.4 meV", but RESULTS_LOG says the k3→k4 shift "does not establish convergence of individual energies". M10:177-178 calls the result "consistent in direction with the paper's statement". M10:168-169 says "within or below the forecast ranges"; RESULTS_LOG says both lie inside them. | Fix: move to "Plausible" or "Computed, unresolved". Replace "k-converged" with "changes by 3.4 meV from k3 to k4". Replace "within or below" with "within".

3. M15:47 and M15:181 | LABEL-UPGRADE | "The off-state floor is not gate leakage" is placed under "Strongly supported" and repeated in the keyresult without a hedge. C005 is INFERRED, with no I_G recorded. The registered tests (H-C, S2) are sealed. M07:85-86 and M13:84 say "unlikely". | Fix: use "unlikely (INFERRED)" and move it to "Plausible".

4. M15:35-38 | LABEL-UPGRADE | "Demonstrated: Confinement does not account for the threshold step by itself." The 44 % is monograph arithmetic from a rigid transfer of the crystalline PBE ΔEc law (C020 caveat: films are amorphous). The 18 % is only a register forecast (A13, "not an identified physical contribution"). The same item concedes that "the threshold data cannot distinguish readings with and without confinement (C018)". The three shares (44 / ~50 / 18 %) are not reconciled. The 50 % is the V1 "realised term" (report_latex_full ch.12:142). The register's earlier figure was 36 %. | Fix: label it DERIVED/INFERRED with the conditions, and state which share is which.

5. M15:12-33 (section header) and M01:94-95 | LABEL-UPGRADE (moderate) | The "Demonstrated" class holds COMPUTED crystalline-PBE items (C020/C021/C022/C039) and the DERIVED Kane relation. M01:94 calls the Kane relation "the demonstration". Its labels are:
 - FACT-027 / M004: DERIVED. Errors −1.3 / +1.9 / +9.6 / +0.7 %.
 - "mass and dEc laws are not independent inputs".
 - confinement_analysis.json: the predicted in-plane α is 7–19 % below the computed α.
 M09:229-232 and M15:178-179 ("explained by bulk non-parabolicity") are similarly strong. M15:22-24 "reproduced against an independent published calculation" is supported only for ΔEg within 0.1 eV (0.04 and 0.005 eV, 13_dft.tex:786). Lin's masses are 6–10 % higher than ours (BANDS_MASSES.md:216). | Fix: rename the class "Computed/derived within stated scope", or use "consistent with" instead of "demonstration/explained".

6. M11:58-61 | LABEL-UPGRADE | "...so compensation must dominate in the devices whatever H-N shows." This is unlabelled. It is inferred from the fitted N_D,eff, which C016 says is "not identifiable". M12:46 says "compensation not computed". | Fix: "would have to dominate if the fitted N_D,eff were physical (INFERRED)".

7. M01:100, M15:53-54 and M15:182 | LABEL-UPGRADE (mild) | "A quantitative account of why every 6.3 nm prediction failed" and "failures follow from..." make a causal claim. M12:106-107 says "The arithmetic does not identify a cause". M13:153 prefers device spread. | Fix: "quantitative description of how every failure is related to...". Label it DERIVED, with no cause assigned.

B. BLINDNESS (no outcome stated; two wording risks)

8. M14:91-92 (also the comment at M08:5-6) | BLINDNESS (low) | "One public commit message names a scored criterion of a sealed-stage run." This implies that an S2+ run has been scored and that a commit message describes it. No value is given. M08:5-6 says "commit messages that mention S2 scores". | Fix: "A public commit message contains sealed-adjacent information; not used". Do not characterise its content.

9. M02:61 and M11:306-307 | BLINDNESS (very low) | "H-J sealed; forecast: fails" is the registered Claude forecast (H-J). It reads like an outcome without a qualifier. "H-H 2.0 nm part unresolved: bare control parked" is a process consequence (D-35 parks aIWO_2p0_s1_bare). I did not find "H-H unresolved" stated within the allowed register range. | Fix: "registered forecast (unscored): fails". Cite D-35 for the H-H status.
 Allowed and clean: M08:192-197 (17/200 used, D-58 plan), M11:416-423 (conditional reading guide), M11:381-383 and MG D1/D2 (exposure disclosures without values), C034-C037 force numbers. M11 lists structural facts and placeholders only.

C. MISMATCH / INCONSISTENCY (numbers, definitions)

10. M07:51-53, M07:56-58, M07:66-67 | MISMATCH (scope overstated) | The text says the independent re-implementation "reproduces every core number" in the table, and the caption says "independent recomputation against the ledger". tools/verify_device_facts.py recomputes only V_th,cc, floor, I_D(±3 V) and the saturation μ. It has no SS or μ_FE code. The SS rows (123.6 / 122.7 / 115.3) are copied from C008. I re-checked the μ_FE peaks against analysis_2026-10-06_extraction/mobility_vs_vg.csv: 12.15 @ 3.0 V, 10.95 @ 2.85 V, 50.17 @ 2.8 V, which match the table. | Fix: restrict the claim to the recomputed rows and mark the SS / μ_FE rows "from the registered extraction".

11. M07:139-140 | INCONSISTENCY | "The registered windows give 123.6, 122.7 and 115.3 mV/dec, up to 168 % higher". Against the paper's 61.8 / 87.4 / 119.3 these three values are +100 %, +40 % and −3 %. The +168 % in C032 belongs to the S1 window, which is not quoted. | Fix: quote the S1 value, or write "+100 % at 2 nm (A1); up to +168 % with S1".

12. M14:19-20 | INCONSISTENCY | "Supervisor: Mukul Kumar; principal investigator: Prof. Chao-Hsin Wu". main.tex:35-37 and README.md:3 give PI: Wu and Mentor: Kumar. | Fix: "Mentor".

13. M11:230-231 | INCONSISTENCY | "one-attempt Gaussian rescues of the 0.8 nm and two 2.0 nm W chains". D-40/A36: aIWO_2p0_s2 uses Gaussian 0.005 Ry. aIWO_2p0_comp_s1 is rescued with MV 0.01 Ry plus aids (the registered family kept). aIWO_2p0_s1 is only a conditional rescue. | Fix: "A35/A36: one-attempt rescues (Gaussian for 0.8 nm and 2.0 nm s2; MV for comp_s1)".

14. M10:24-26 | MISMATCH | "two to three orders of magnitude above the Mott density". FACT-080 gives 9.09e17 cm^-3. The donated densities (1.4–3.0e21) are 1.5e3 to 3.3e3 times larger, about 3 to 3.5 orders. With the PBE-mass Mott density (3.7e17) the ratio is 3.8e3 to 8e3. | Fix: "about three orders".

15. M09:49-50 and M09:200 | INCONSISTENCY (source conflict) | The deck-vs-band-edge difference is given as "−3.0 % (bulk) to +3.4 % (0.461 nm)" and "−3 % ... to +3 %". Ledger C039 and SESSION_STATE X6 say −3 % to +0.5 % (0.75 nm). BANDS_MASSES.md:117 does give +3.4 % for the 0.51 nm slab, which is outside the laws. | Fix: state that +3.4 % belongs to the In8(OH)24 film, or align the ledger. The deck-basis window is "|k| ≤ 0.05 Å^-1" at M09:42; BANDS_MASSES.md:34 gives 0.046 and RESULTS_LOG 0.045.

16. M09:101-102 | MISMATCH (minor) | "0.54 m0, two orders of magnitude below the computed value". The mass ratio is 16–22 / 0.54, about 30 to 40, which is 1.5 orders. The two-orders figure applies to N_V (about 200×, as in the keyresult M09:233). | Fix: wording.

17. M10:33-35 | MISMATCH (minor) | "N_24d/N_8b ... about 430 at 600 K". 3·exp(0.2577 / 0.051704) = 438 (440 with 0.2579). | Fix: "about 440".

18. M10:32 vs FACT-040 caveat | INCONSISTENCY (the registry is probably the error) | The monograph gives 0.2579 eV for 3×3×3, which matches f09_iwo_bulk.json E8b−E24d (relax k3 = 0.2579; scf k4 = 0.2577). The FACT_REGISTRY caveat says 0.2580. | Fix: the registry.

D. CITATION / PROVENANCE

19. M13:35-36 | CITATION | "SEM grains grow with thickness [Januar2026]" has no page. The digest text (p.2) says only that IWO has a smaller grain size than In2O3 at comparable thickness. A thickness dependence appears only in the SI Fig. S4b caption (2 and 10 nm), and no direction is given. M14:44 says the SI is "not in the project files". | Fix: soften, or cite as "SI Fig. S3-S4".

20. M01:57 and M14:75 | CITATION | "crystalline DFT at 5.3 % W [Januar2026]". The digest (DFT section, p.3) gives QE, PAW, PBE, 71 / 639 Ry and an 8×8×8 grid, but no W fraction. The only source of 5.3 % is research_record/01_CURRENT_STATE.md:48 (flagged stale). | Fix: add a page or SI reference, or drop the number.

21. M00:5-6, M07:20-21, M14:40, M14:86-87 | CITATION (minor) | The abstract says the 2.0 / 6.3 / 13.2 / 31.8 nm channels were "fabricated and published". Januar2026 reports channels "~2 to ~13 nm". The text names 2.0 and 13.2 nm; 6.3 nm appears only in the digitised Fig. 1b. I found no 31.8 nm device in the digest. | Fix: "the first three are described in the paper; 31.8 nm was supplied with the data".

E. MINOR

22. M01:42-43 | MINOR | "only a few hundred donors per square micrometre" is unsourced. The fitted N_D,eff at 2 nm gives 2.5e17 cm^-3 × 2 nm = 5e11 cm^-2 = 5×10^3 µm^-2. Full activation gives about 10^6.

23. M13:54-55 | MINOR | "6.3 nm film has the strongest gate dependence of mobility (γ = 1.13)". The ledger (C011/C012) gives γ only at 13.2 nm (0.27) and 6.3 nm (1.13). γ at 2.0 nm is not in the sources I checked.

24. M09:198 and M12:43 / M12:81 | MINOR | Kane N_c factors are 5.7 % / 1.057 and 2.5 %. confinement_analysis.json has 1.0562 and 1.0243. RESULTS_LOG and C039 say 5.7 / 2.5 %. | Fix: align the source.

25. M11:143 | MINOR | The aIWO_0p7_s1 composition (In49W1O83H14) is shown, but the aIO_0p7_s1 composition is missing from the table.

26. Items I could not verify from permitted sources: M11:82-122 (SLAB_PROTOCOL rules, "three structures were replaced") and M11:92 (cooling rate; the 23 ps and 9 ps quench times are consistent with ~1–3e14 K/s). SLAB_PROTOCOL.md lies under the blocked compute/amorph path.

VERIFIED (passed)

Numerics
- Device metrics: Vth,cc 0.6618 / 0.6440 / 0.0825; floors 4.606e-15 / 1.528e-13 / 6.597e-12; I_D(±3 V); the 31.8 nm values (3.0e-7, on/off 12.0, 3.590e-6 at +3 V); μ_sat 5.087 @ 1.75, 3.858 @ 2.55, 27.403 @ 0.95; Cox 8.955e-7 (device_facts.json, FACT-100..113).
- μ_sat/μ_FE ratios 0.47 / 0.23 / 0.68 vs 0.72 / 0.41 / 1.02, and overdrives 1.09 / 1.91 / 0.87 V (musat_ratio.json). Floor exponents 3.1 / 5.1 / 3.85. Threshold changes −0.018 and −0.561 V; on-current factors 0.79 and 7.6; −0.579 V total.
- C-ledger numbers: C002, C003, C008, C014 (−0.29 / −0.37 / −0.23), C025, C032, C033 (0.71 / 0.93 / 1.02), C034, C035, C036, C037 (Table M11 values and the 71–75 %, 0.063–0.066 and 0.107 figures), C038.
- Crystalline DFT: gaps 0.8887 / 0.8931; slab gaps and dEg (2.2514 / 1.3099 / 0.8998 / 0.3352); dEc 0.281 / 0.848 and the 0.84 / 0.94 shares; masses 0.443 / 0.337 / 0.279 / 0.203 and α 0.24–0.47; Δm = 0.1145 t^-1.2755; r 1.06–1.11; HSE-corrected 2.44–2.46 and 3.06 eV; the ± 0.17 eV 0.695 nm sensitivity.
- W cells: W-level table, E_F, W-5d counts 0.36 / 0.29 / 0.43 / 0.09, bond means, spin energies 19.5 / 22.7 meV, 1 nm and 2 nm ΔGap / ΔEA, OH share 0.72, band 312 holding 2.0 e, 1.79 / 1.93 e per band, Kane 2.04 / 2.17 vs parabolic 0.73 / 0.76. Hole numbers: 4.44 / 1.62 meV, 4.03 / 17.8 m0, N_V 1.6–2.7e21, m_DOS 16–22, 0.54 m0, n_i 5.0e-10 → 6.7e-9, SRH 3.4e-3, 5.9 / 3.3 m0, 29 meV.
- All six H-L table rows, BFGS step counts and the −25.7 / −41.3 / −3.4 meV changes.
- Table M09 (device-ready parameters) agrees with BANDS_MASSES.md rows. I recomputed the law values at 2 / 6.3 / 13.2 nm for ΔEg, ΔEc and Δm, and the deck-basis χ, Eg and m*.

Campaign and derived JSON
- M12: multiscale_budget.json for the ΔEc ranges, −0.2194 to −0.2233 V, d ΔEc/dt, the mV sensitivities, 142 mV, 44 %, 18 %.
- M08 vs register: H-A..H-F and H-J numbers, all forecasts, S1 table values, the +37.5 / +89.5 / slope 3.5 / 0.86 mV / 7–8 % audit figures, the 181-launch stage counts (design table), 14 + 3 = 17 of 200 (D-44 / D-58), the register freeze time, the scorer hash c0f28bb9.
- MH Table: atlas_usage.json; the pool snapshot (resources.json: 405 GPUs on 79 nodes, 144 / 96 / 72); the 85.6–90.2 / 95.8 GB figure (register A29-A34 line 1007); 8,300 core-hours / 85–90 GPU-hours (13_dft.tex:1517); ≈120 kWh.
- MG: X1–X13, E3–E5, R1, D1 / D2, T1–T5, P1 / P2 and the nine record inconsistencies agree with RESULTS_LOG errata 1-5, SYNTHESIS and the register. The 83 % series-resistance figure is in SYNTHESIS:142, 243; "six mechanisms" is in ch.08.

Labels, decisions, wording
- Superseded values (−0.056 eV, 0.19 eV, 5.5e21, −0.002 eV) appear only in correction contexts.
- Status labels agree with the ledger for C005, C006, C007, C014, C022 (INFERRED parts), C023, C024, C027, C028, C031, C032, C037, C038 outside the M15 / M10 items above. The M02 priors match 02_RESEARCH_QUESTIONS.md. D-05 / D-06 / D-11 / D-17 / D-35 / D-41 / D-42 / D-43 / D-44 / D-58 content and the A37 text are reproduced faithfully. Proposition prop:mono-hn follows A37.

Citation page checks (printed pages against report_latex_full/digest/papers; 17 page-numbered cites, all verified)
- Januar2026: p.1 (BEOL <400 °C; disorder-limited <~10 nm; CC BY), p.2 (HRTEM lacks long-range crystallinity), p.3 (60–70 mV/dec, 5.1–27.4), pp.3 and 7 (27.4 → 5.1), p.4 (passivates O vacancies and smoother delocalization; single model captures the crossover), p.10 (data on reasonable request).
- Si2022 p.164 (3 nm Si / 10 nm InGaAs), Si2021 p.500 (0.7 nm, TNL / quantum-confinement abstract), Lin2022 p.21536 (>10 A/mm), Stokey2021 p.225102-1 (0.208 ± 0.006 m_e).
- Also confirmed: "IWO ~2 % W", the bottom-gate structure and "eight fitted parameters" in the paper. The affiliations in M07 / M14 are right (NTU; Chang Gung for Liu). The 11 digested papers, the 3.5 MB ATLAS files and the workbook sha256 ce97eccd also check out.

---

## Disposition (main session, 2026-10-14)

Each finding was checked against the cited source before any edit. Correction IDs refer to appendix MG, section
"Corrections made in the monograph's own review (Gate 6)".

| # | Disposition | What was done |
|---|---|---|
| 1 | Accepted | M15 re-sorted: the numerical reproduction (C030, DERIVED) stays under "strongly supported"; the definition (C031) moved to the new "inferred, derived under stated conditions, or computed but unresolved" section; key result reworded. V9 |
| 2 | Accepted | H-L moved to "computed but unresolved" in M15; M10 "changes by only 3.4 meV from k3 to k4", "within the forecast ranges", and the paper-statement sentence reworded; manuscript MS-08 likewise. V9 |
| 3 | Accepted | M15: "unlikely to be gate leakage (INFERRED)", moved. V9 |
| 4 | Accepted | M15 item rewritten with the three shares named (44 % rigid transfer, ~50 % earlier calibrated model, 18 % register counterfactual) and labelled INFERRED. V9 |
| 5 | Accepted | M15 class renamed "Demonstrated, or computed within a stated scope"; Lin2022 agreement stated for the gap openings only; M01 "finding ... consistent"; M09 key result "consistent with". |
| 6 | Accepted | M11 conditional and labelled INFERRED with C016. |
| 7 | Accepted | M01 item (6) and M15 item reworded: description, no cause assigned. |
| 8 | Accepted | M14, M08 comment, DECISIONS.md N45 and SESSION_STATE now say only "contains sealed-adjacent information; not used". |
| 9 | Accepted (D-35 checked: "aIWO_2p0_s1_bare parked ... H-H at 2.0 nm UNRESOLVED") | M02 "registered forecast (unscored)"; M11 cites D-35. |
| 10 | Accepted | M07 text and caption restricted to the recomputed rows; SS and μ_FE marked as from the registered extraction. |
| 11 | Accepted (C032 checked) | M07 gives +100 % / +40 % / −3 % for A1 and "up to +168 %" for S1. |
| 12 | Accepted | M14 "Mentor". |
| 13 | Accepted (D-40 checked) | M11 rescue item rewritten per D-40. |
| 14 | Accepted | M10 "about three orders of magnitude (1500–3300 times)". |
| 15 | Accepted | M09: −3.0 % to +0.5 % for the films within the laws, +3.4 % for the In8(OH)24 layer; window "≲0.05 Å^-1 (0.045–0.046 in the logs)". |
| 16 | Accepted | M09 "30–40 times lighter ... a factor of about 200 in N_V". |
| 17 | Accepted (recomputed 438) | M10 "about 440". |
| 18 | Accepted (recomputed from f09_iwo_bulk.json: 0.25792 eV) | FACT_REGISTRY caveat now 0.2579 eV. |
| 19 | Accepted (digest p. 2 checked) | M13 row reworded and cited to p. 2; SI dependence noted as unavailable. |
| 20 | Accepted (no source in the digest) | "5.3 % W" removed from M01 and M14. |
| 21 | Accepted | M00 abstract and M14 say the 2–13 nm series is published and the 31.8 nm curve was supplied with the data. M07:20–21 already said "provided by the fabrication group"; unchanged. |
| 22 | Rejected (arithmetic error in the finding) | 2.5e17 cm^-3 × 2e-7 cm = 5e10 cm^-2 = 500 per µm^2, so "a few hundred" was right. The sentence now gives this source (C016). |
| 23 | Accepted | M13: "much stronger ... than the 13.2 nm film (γ = 1.13 against 0.27; C011, C012)". |
| 24 | No change | The two numbers are different quantities: 1.0562 is the first-order factor (M05 eq. mono-conf-nc3d), +5.7 % the logged full integral; M05 states both. |
| 25 | Deferred | The aIO_0p7_s1 composition is in a source under the blocked compute/amorph path; left for a session with permitted access. |
| 26 | Noted | Not verifiable from permitted sources; M11 statements left as written, sourced to the register. |
| Verified list, μ_sat ratio | Accepted | M07 0.23 → 0.22 (0.2249), as the theory review also noted. |
