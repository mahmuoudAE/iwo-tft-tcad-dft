# Codex manual research for the review fixes (2026-10-10)

- **What this is.** The final answer of a read-only Codex run (codex-cli 0.162.0 in WSL "Ubuntu", `codex exec --sandbox read-only`). Prompt: `codex_fixes_research_prompt_2026-10-10.md`; full log: `codex_fixes_research.log`. Codex ran no simulator and changed no file.
- **Used for:** fix 5 (`^tat.poisson` syntax and default, Q2) and fix 6 (FNORD field location and the r-transfer algebra, Q1); fix 3 (no documented activation string for QTNLSC / FNORD / ITAT / BQP / IGZO.TOKYO, Q3, so the parser reports UNVERIFIED unless it finds positive evidence).

---

All manual citations below refer to `report_latex_full/tools/atlas_manual_pages.txt`; page numbers are the preceding **PDF PAGE markers**.

1. **Q1 — FNORD field and collection.** E is the oxide-field magnitude; current is calculated for each insulator–semiconductor segment, then assigned to an electrode–insulator segment (p.288, lines 13021–13038). This places evaluation at Al2O3/IWO, rather than TiN/HfO2. F.AE/F.BE are MODELS parameters. However, MODELS supports MATERIAL and REGION selectors: an exclusively global pair is **UNVERIFIED**, as is FN-specific behavior under those selectors (p.1482, lines 59404–59406; p.1483, line 59443).

   For charge-free, one-dimensional normal fields, your algebra is correct: \(r=2.174444\), \(A'=A/r^2=0.2114966A\), \(B'=rB\). This is a mathematical substitution into the documented equation, not documented multilayer calibration; no contradiction found (p.288, lines 13046–13048).

   FNORD is self-consistent and sums current into the gate terminal (p.288, lines 13027–13033; p.289, lines 13055–13065). Metal-origin injection is mentioned (p.288, lines 13014–13015), but explicit negative-VG implementation coverage is **UNVERIFIED**.

2. **Q2 — TAT.POISSON.** Use `MODELS ITAT.SC.EL ^TAT.POISSON`. The manual explicitly disables Poisson trap charge by clearing this MODELS flag; default is **True** (p.323, lines 14541–14548). Its example uses `MODELS RTAT.SC TAT.SLICEPTS=21 ^TAT.POISSON` (p.327, line 14745).

   Clearing the flag removes charge coupling, while ITAT.SC.EL selects current-continuity coupling; thus the documented controls retain self-consistent tunnelling current (p.322, lines 14505–14510; p.325, lines 14671–14676). It cannot be disabled during transient simulation (p.323, lines 14560–14564).

   `OUTPUT TRAPS.FT` saves each trap’s occupation fraction; trap density and ionized density are automatically saved (p.325, lines 14660–14665). `SOLVE ITAT.FILE=<stem>` additionally produces slice logs containing trap occupation probability, density, energy and component current densities (p.325, lines 14691–14696).

3. **Q3 — Positive stdout identification.**

   - QTNLSC.EL: **UNVERIFIED**
   - FNORD: **UNVERIFIED**
   - ITAT.SC.EL: **UNVERIFIED**
   - BQP.N: **UNVERIFIED**
   - IGZO.TOKYO: **UNVERIFIED**

   No verified model-specific, non-echoed activation string was found in the searched installed `.out`/`.log` text or manual. The manual says `PRINT` prints model status and `PRT.FLAGS` prints regional model flags, but supplies no exact identifying row/title for these five models (p.1483, lines 59432–59441). ITAT results are described as visible in runtime output without a specified string (p.325, line 14658).

   The supplied run contains `"REGIONAL MODEL FLAGS:"` and `"REGIONAL MOBILITY MODEL SUMMARY:"`, but these generic headings cannot identify the requested inactive models: `results/runs/run_0040_13p2_recal_dos384_13p2/deckbuild.out`, lines 237–433.

4. **Q4 — LOG j.tun.** `LOG ... J.TUN` writes tunnelling currents; ITAT documentation explicitly says the current associated with **each contact** is logged (p.1307, line 53194; p.325, lines 14658–14660). FN documentation likewise directs `J.TUN` for gate tunnelling current (p.289, lines 13063–13065).

   Exact column names such as `Itnl`/`Jtnl`, electrode-label conventions, and readability from DeckBuild-format plain text are **UNVERIFIED**. The LOG reference describes MASTER as the default standard structure format and OLD/PISCES as the original PISCES-II format, without documenting tunnelling-column text encoding (p.1307, lines 53195–53201).

5. **Q5 — Combination and solver restrictions.** No prohibition against combining FNORD, QTNLSC.EL and ITAT.SC.EL was found in their reviewed sections. This does **not** verify combined operation. No mandatory ITAT METHOD or CARRIERS setting was found; compatibility of the exact supplied METHOD line remains **UNVERIFIED**. The manual recommends TAT.NLCURRS, TAT.NLDERIVS and reduced METHOD DVMAX for convergence (p.325, lines 14653–14657 and 14671–14679).

   Installed example `/mnt/c/sedatools/examples/deckbuild/4.2.5.R/quantum/quantumex20/quantumex20.in` enables ITAT.SC.EL and performs DC solves without an explicit METHOD/carriers statement beforehand.

   An explicit FNORD exclusion exists for **ZAIDMAN**, outside these three models (p.372, lines 16871–16873). `OUTPUT QTUNN.EL` describes FN output “instead of direct quantum tunneling,” but does not state a model-combination prohibition (p.1518, lines 60633–60636).

**Facts for the author**

- FN current is calculated at insulator–semiconductor segments and collected at gate segments (p.288, lines 13034–13038; p.289, lines 13063–13065).
- A strictly global F.AE/F.BE pair is not established: MODELS has material/region selectors (p.1482, lines 59404–59406; p.1483, line 59443).
- `^TAT.POISSON` disables default-enabled trap charge; transient disabling is forbidden (p.323, lines 14546–14548, 14563–14564).
- `OUTPUT TRAPS.FT` and automatically saved ionized trap densities provide charge diagnostics (p.325, lines 14663–14665).
- `J.TUN` logs contact tunnelling currents; exact column names remain UNVERIFIED (p.325, lines 14658–14660).
