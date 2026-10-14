# Paper draft 2026-10-13: open items

Draft of the Methods and a manuscript skeleton for the computational IWO TFT paper (ATLAS 5.28 + Quantum ESPRESSO + the
hypothesis register). Written by Claude on 2026-10-13 for human review. **Nothing here is approved for a manuscript**
(charter section 9). Not committed.

## Files

| File | Content | Words (texcount: body + headers + captions) |
|---|---|---|
| `skeleton.tex` | main document: title/abstract placeholders, status note, section list with one intent paragraph each; `\input`s the files below | 1077 + 90 + 0 |
| `methods_tcad.tex` | device and data, simulation domain and solver, V3 model, model history, extraction protocol (incl. A1), campaign design, registered TCAD predictions, scoring/resolution method (ASSUMED operational method), execution controls and deviations, launch accounting | 2810 + 52 + 69 |
| `methods_dft.tex` | codes, crystalline references (incl. H-L settings), MACE melt-quench, slab construction (SLAB_PROTOCOL rev. 2), cell inventory, ML force validation (C037 FAIL), relaxation and D-24 rules, smearing families (A15/A26/A31/A35/A36), restart gate and qualification (C036), final SCF/export/certification, read-out definitions, gap anchoring (A23), CERN resources | 3434 + 61 + 28 |
| `methods_registration.tex` | governance, registration record and freeze tags, the register, amendment log A17-A36 (A1-A16 summarised; A32/A33 reserved), sight history and disclosures, reporting commitments | 1076 + 19 + 44 |
| `limitations.tex` | data, device model, first-principles, procedure | 901 + 7 + 0 |
| `paper_preamble.tex` | packages and the report's notation macros, plus `\pdPending`, `\pdCell`, `pdIntent` | - |
| `TODO.md` | this file | - |

texcount does not count table cells; with tables the prose is about 11,400 words in all (stripped estimate).
Total body text (texcount): about 9,300 words.

**Build.** `pdflatex skeleton; bibtex skeleton; pdflatex skeleton; pdflatex skeleton`. The bibliography is read from
`../../../IWO_PHYSICS_CONSTRAINED_MODEL_V1/report_latex_full/references.bib` and `.../bib/extra_DFT.bib` (relative
paths). A copy compiled in the session scratchpad with MiKTeX: 26 pages, no undefined citation or reference, no
overfull box; the only BibTeX warnings are the empty years of `AtlasManual` and `DeckBuildManual` (pre-existing).
No build output was written into this folder.

## Conventions used

- **Sources.** Every number carries a source comment `% <!-- KEY:line -->` (file:line). The requested "HTML comment"
  is placed inside a LaTeX comment, because a bare HTML comment would print. Each `.tex` file starts with its KEY
  legend (`PRIV/` = `iwo-tft-research-private/`, `PKG/` = `IWO_PHYSICS_CONSTRAINED_MODEL_V1/`). A script checked
  every commented number against the cited lines; the remaining mismatches are formatting artefacts (units such as
  NC300 = 300 K, 0.04 eV written as 40 meV, dates in file names, LaTeX-formatted numbers in the source).
- **Labels.** Ledger vocabulary through `\prov{...}` (COMPUTED, DERIVED, FITTED, ASSUMED, CALCULATED, LITERATURE,
  MEASURED, HYPOTHESIS, INFERRED, UNRESOLVED, FALSIFIED).
- **Style.** ASCII only, siunitx, booktabs, macros of `report_latex_full/preamble.tex`, plain environments.
- **Placeholders.** `\pdPending{Pnn}{KIND: text}` prints `[Pnn KIND: text]`; `grep -n "pdPending{P" *.tex` lists them.

## Sight and sealing compliance

- Not opened: any FINAL export, XML or projection output, relaxation output, the scratchpad quarantine folders,
  `PKG/results/runs/run_0075_*`, `PKG/results/sealed/`.
- Read, besides the listed sources: the module docstrings of `compute/amorph/mace_amorph.py`, `make_specs.py` and
  `dft/make_dft.py`, and the melt-quench schedule constants of `mace_amorph.py` (structure-generation inputs, no
  outputs), plus `certify.py` lines 210-222 (code of the relaxation check cited by the register as `certify.py:218`).
- No amorphous-slab electronic value (class, PR_n, gap, edge, Fermi level, projection, band energy) appears in the
  draft. Sight events are described by what was seen and when, never by value.
- RESULTS_LOG.md (2026-10-11 13:36Z entry) records a Fermi energy of `aIO_1p0_s1` at a non-final geometry. It was
  read while reading the log; it is not reproduced in the draft and is raised as P28.

## Placeholders

| ID | Kind | Where | What is missing | Waits for |
|---|---|---|---|---|
| P01 | DECISION | methods_tcad.tex:72 | Permission to use and publish the fab's raw curves (already in the public repo), data custody, authorship | Fab meeting / human decision (charter section 8; 01_CURRENT_STATE H.6; HUM items) |
| P02 | CHECK | methods_tcad.tex:136 | The 0.695 nm (nominal 0.75 nm) crystalline slab point in the V3 fit3 laws is "preliminary, not in RESULTS_LOG" (C021) | DFT agent: log the slabL2 result in RESULTS_LOG and update C021, or refit the laws without it (then re-check the decks) |
| P03 | CHECK | methods_tcad.tex:227 | The fab's mobility/SS recipe (formula, C_ox, W/L, current normalisation, sweep provenance) | Fab confirmation (C031 falsified_if; C024, C025 stay UNRESOLVED until then) |
| P04 | CITATION | methods_tcad.tex:273 | Oxide band parameters (Robertson 2000 as cited in CAMPAIGN_DESIGN), tunnelling masses, Lenzlinger-Snow, Ielmini TAT, IGZO.TOKYO (Abe 2014); also capture cross-sections ("to be cited before publication", CAMPAIGN_DESIGN:193) | Literature pinning with page-exact citations (report CONVENTIONS) |
| P05 | RESULT | skeleton:99; methods_tcad:298 | H-B: S2-14..S2-17, STRIP-6p3 | DIAG launches after P11 and P14 |
| P06 | RESULT | skeleton:99; methods_tcad:299 | H-C: S2-11 (sealed run_0075), S2-01..S2-13 | Unsealing after P11/P14; DIAG launches |
| P07 | RESULT | skeleton:117; methods_tcad:300 | H-D: S4 profiling, native triples | S4 |
| P08 | RESULT | skeleton:108; methods_tcad:301 | H-E: S3-01..S3-03, AFF-2p0, AFF-6p3 | DIAG launches |
| P09 | RESULT | skeleton:108; methods_tcad:302 | H-F: S3-10..S3-13, S3-27 | H-F operational scoring written and frozen (S2_PREP 6), then DIAG_HF released |
| P10 | RESULT | skeleton:117; methods_tcad:303 | H-J: S4a, S4c, S5 | S4/S5 |
| P11 | DECISION | methods_tcad.tex:333 | User sign-off of the resolution method as a logged amendment | User (S2_SCORER_FIXES:129; S2_RUNNER_GATES:248); before S2-11 is unsealed |
| P12 | DECISION | methods_tcad.tex:335 | Whether to add matched numerical refinement runs so primary S2 verdicts can become demonstrated | User; logged plan change (S2_SCORER_FIXES 9.7) |
| P13 | CHECK | methods_tcad.tex:352 | Runner revision 3 (stop gates, sealing, clean-up) uncommitted, DIAG not launched (S2_RUNNER_GATES:3) | Commit hash + Codex verdict recorded |
| P14 | DECISION | methods_tcad.tex:367 | run_0075 rulings: timeout eligibility and the "possibly exposed" label; unsealing of S2-11 | User/Codex rulings (S2_RUNNER_GATES:249) |
| P15 | RESULT | methods_tcad.tex:391 | Final launch count and status of every launch (also reconcile 181+19 vs 184/16, see issue 8) | End of campaign |
| P16 | RESULT | skeleton:128; methods_dft:97 | H-L energies, k3/k4 check, A20 sensitivities | H-L jobs (D-19, D-29/A28); entry in RESULTS_LOG and the ledger |
| P17 | CITATION | methods_dft.tex:104 | MACE architecture and the MACE-MPA-0 model | Literature pinning |
| P18 | RESULT | methods_dft.tex:180 | Relaxation status of every cell at the 17 Oct 10:00 UTC cutoff, with segments, lineage and smearing family | Cutoff 17 Oct 10:00 UTC |
| P19 | RESULT | methods_dft.tex:200 | Two 2.0 nm MACE force-check frames (12890593.0/.1 or the CPU fallback); Hf force check (A21) | A34 route or fallback (14 Oct 12:00 UTC trigger); Hf check jobs |
| P20 | RESULT | methods_dft.tex:271 | A15 audit outcome and provisional width (A31); whether aIWO_2p0_s1 needed the A36 rescue; C4 polishes at 1.0 and 0.7 nm | A31 audit runs; C4 jobs (D-40); unblinding decision D-42 for any electronic read-out |
| P21 | RESULT | methods_dft.tex:296 | Restart-gate and qualification-SCF outcomes (aIWO_0p8_s2, aIWO_2p0_s2, aIWO_2p0_comp_s1) | A35/A36 segments; qualification submits need the user's go (REG:1022) |
| P22 | CHECK | methods_dft.tex:320 | Record that the frozen reader reproduced 3 % W-5d and dEc 0.281 eV (register section 3) | DFT agent record |
| P23 | RESULT | skeleton:138; methods_dft:351 | H-N per-cell classes and series outcome; H-G, H-H, H-K scores | Certificates + Codex audit + **release decision D-42 (not yet in 05_DECISION_LOG.md)** |
| P24 | RESULT | skeleton:148; methods_dft:364 | A23 (ii) W-cell and (iii) amorphous-bulk hybrid checks; amorphous bulk references | A23 jobs (D-25); D-42 for amorphous electronic quantities |
| P25 | RESULT | methods_dft.tex:379 | Total CPU/GPU hours of the amorphous, vacancy and validation campaign | End of CERN access (21 Oct) |
| P26 | DECISION | methods_registration.tex:33 | Charter still PROPOSED; adoption (D-10) pending | User (HUM-002) |
| P27 | CHECK | methods_registration.tex:64 | External timestamp of the register and read-out freezes (charter section 7 step 5: DOI, or tags pushed to GitHub); the record's remote is private | User decision (pushing to a new remote or a DOI needs approval, charter section 9) |
| P28 | DISCLOSURE | methods_registration.tex:163 | RESULTS_LOG 2026-10-11 13:36Z logs a Fermi energy of aIO_1p0_s1 (non-final geometry), after A27, not in the register's sight history | User/Codex: register erratum or a ruling that it is immaterial |
| P29 | TEXT | methods_registration.tex:188 | Final per-cell sight-history table | After P23 (D-42) |
| P30 | RESULT | skeleton:156; methods_registration:198 | Scorecard of every registered prediction (H-A..H-M) and the H-N exploratory read-out | All scoring done |
| P31 | TEXT | limitations.tex:96 | Final wording of the safeguards bullet | P26, P27 |
| P32 | TITLE | skeleton.tex:22 | Title (a non-approved working title is in a comment) | After P30 |
| P33 | TEXT | skeleton.tex:30 | Abstract (intent paragraph gives the required content) | Written last |
| P34 | DECISION | skeleton:23; skeleton:189 | Authors, order, affiliations | Agreement with the fab group (memory: settle data ownership and co-authorship before submission) |
| P35 | TEXT | skeleton.tex:80 | Figure plan for main text and Extended Data | figure-maker agent, consistent with PAPER_FIGURES.md |
| P36 | DECISION | skeleton.tex:50 | Target journal (Nature target is an ambition; the device data are already published; the paper is computational) | User |
| P37 | TEXT | skeleton.tex:182 | Data availability statement | P01 |
| P38 | TEXT | skeleton.tex:185 | Code availability (deck generator, scorer, read-out package with freeze tags, generators; archive DOI) | User decision on public/private repos and a DOI |
| P39 | TEXT | skeleton.tex:197 | AI-use statement in the journal's required wording | P36 |
| P40 | TEXT | skeleton.tex:200 | Acknowledgements (CERN computing, funding), competing interests | User |

## Inconsistencies found in the sources (fix in the record before submission)

1. `HYPOTHESIS_REGISTER.md:4` lists the post-freeze amendments as "A17 to A31, A34 and A35"; A36 exists (line 984).
2. A36 time: `HYPOTHESIS_REGISTER.md:984` says 2026-10-12T13:21Z (commit b164faa); `05_DECISION_LOG.md:51` (D-40)
   says 13:25Z. The draft uses 13:21Z (register).
3. `HYPOTHESIS_REGISTER.md:1115` still reads "Proposed, needs the user's go" for A15, which D-16 and D-26 approved.
4. Time zones: decision-log dates are local (UTC+8). Example: D-17 is dated 2026-10-11 for a freeze at
   2026-10-10T18:33:13Z; the tag's creator date is 2026-10-11 02:33:15 +0800. The section-5 heading of the register
   also says 2026-10-11. The draft states UTC times and notes the convention in Table m-reg-record.
5. `CAMPAIGN_DESIGN.md:31` says the SRH term is "≥ 1e14 below the currents"; `CAMPAIGN_DESIGN.md:232` gives
   1e-28 against ≥ 1e-15 A/µm (a factor 1e13). The draft quotes the line-232 numbers.
6. `HYPOTHESIS_REGISTER.md:546` says the bulk references have "125 atoms each"; by the slab rules aIWO_bulk_s1
   (In49 W1 O76) has 126 atoms. Check `specs/spec_aIWO_bulk_s1.json`. The draft says "50 cations".
7. `COMPLETE_PLAN_2026-10.md:42` names MACE-MP-0; `ML_VALIDATION.md:3`, the register and the ledger use MACE-MPA-0.
   The draft follows ML_VALIDATION.md.
8. Stage counts: `CAMPAIGN_DESIGN.md:39` (181 + 19 reserve) against the regenerated matrix (184 entries, 16 reserve;
   `S2_PREP.md:33`). The draft quotes the design table; reconcile in P15.
9. `01_CURRENT_STATE.md` is dated 2026-10-07 and is stale for the campaign (for example section F says amorphous
   structures are not done, section J gives 60 of 71 launches). The draft cites it only for device/data facts and the
   pre-campaign budget.
10. `score_register.py` c0f28bb9: `S2_SCORER_FIXES_2026-10-12.md:349` records it as superseding 6651044e without an
    explicit freeze statement; `S2_RUNNER_GATES_2026-10-13.md:243` calls it frozen. Record the freeze (commit or tag).
11. The 0.695 nm crystalline point used by the V3 laws is not in RESULTS_LOG (P02); the 0.51 nm result (C021) is
    also absent from the log.

## Not done here (by instruction)

No other repository file was edited; nothing was committed or pushed; no job, launch or read-out was run.
