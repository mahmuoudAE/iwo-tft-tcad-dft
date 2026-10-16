# Research monograph: session state

Read this file first after any compaction or restart. Then read `evidence/SOURCE_MAP.tsv` and
`evidence/FACT_REGISTRY.tsv`. Do not repeat the repository audit unless a source listed below has changed
(check with `git log -1 --format=%h -- <path>`).

## 1. Objective

A thesis-style LaTeX research monograph covering the whole evidence-controlled IWO (W:In2O3) TFT project
(TCAD, crystalline DFT, amorphous-DFT protocol, experimental provenance, multiscale integration), plus a separate
npj Computational Materials manuscript scaffold. Assignment text: user prompt of 2026-10-14 ("ADDENDUM -
REPOSITORY-AWARE SCIENTIFIC WRITING AND ADAPTIVE TOKEN OPTIMIZATION").

## 2. Workspace facts (Gate 1)

| Item | Value |
|---|---|
| Checkout | `/home/user/iwo-tft-tcad-dft` (cloud container; fresh clone of the PUBLIC repo github.com/mahmuoudAE/iwo-tft-tcad-dft) |
| Branch / HEAD at start | `claude/zealous-carson-5fjmi8` / `3fe6627` (2026-10-15 +0800, "Publish research record and full crystalline DFT analysis; blind guard in .gitignore"); working tree clean at start |
| Authoritative? | **No, not fully.** It is the public branch. The user's authoritative local trees are on Windows: the private record `iwo-tft-research-private` (commit 21895d2 was archived into `research_record/`), and `IWO_PHYSICS_CONSTRAINED_MODEL_V1`. Absent here: sealed ATLAS runs (run_0075..0077, campaign_C10_DIAGb), all amorphous-DFT outputs, `inputs/papers_text/`, the Januar 2026 PDF, `data_private/raw/`, the 740-page ATLAS manual text, any result newer than 3fe6627. |
| Remote sync | None performed. Per the user's instruction: no pull, reset, merge, push or release. |
| Tooling installed this session | TeX Live (Debian packages: latex-base/recommended/extra, science, fonts-recommended/extra, bibtex-extra, plain-generic, pictures, publishers, tex-gyre, latexmk); Python 3.13 with numpy, scipy, matplotlib, pandas, pyyaml, openpyxl. |
| Baseline report build | Test build of `report_latex_full` in the session scratchpad (not in the repo): see section 8. |

## 3. Source-of-truth decisions (topic-specific; details in evidence/SOURCE_MAP.tsv)

1. **Governance and blindness:** `research_record/00_PROJECT_CHARTER.md` (PROPOSED, adoption D-10 pending),
   `research_record/05_DECISION_LOG.md` (human decisions only), `research_record/codex/work_chat/HYPOTHESIS_REGISTER.md`
   (rev. 2 frozen 2026-10-10T18:33:13Z, amendments A17-A44), `research_record/PUBLIC_EXCLUSIONS.md`.
2. **Claim status:** `research_record/03_CLAIMS_LEDGER.yaml` (C001-C040) is the authoritative claim register.
   FACT_REGISTRY entries point to ledger IDs; they never upgrade a ledger label.
3. **Crystalline DFT numbers:** `qe_workflow/cern_htcondor/results/RESULTS_LOG.md` (newest entries first; the
   2026-10-14 errata and C022 filling caveat supersede earlier lines) and
   `qe_workflow/analysis_2026-10-13_full/` (re-derivation from raw outputs; `out/*.json`, `bands_masses/out/*.json`).
4. **Device data and extraction:** `data/experimental_clean.csv` (MEASURED; collaborator-owned, permission pending),
   `analysis_2026-10-06_extraction/` (registered protocol 7a61687 + A1 7ce7116).
5. **TCAD V1/V2:** `analysis_2026-09-25/SYNTHESIS.md`, `analysis_2026-10-06_V2/`, runs 0001-0060.
   **C10 campaign:** `analysis_2026-10-10_campaign/` (runs 0061-0074 public; S1 results "seen before rev. 2";
   everything from S2 on is blind or sealed).
6. **Current state file is stale:** `research_record/01_CURRENT_STATE.md` is dated 2026-10-07. Use it only for
   device/data facts and the pre-campaign state (same judgement as paper_draft TODO item 9).
7. **Historical, not current:** `FINAL_STATUS.md`, `00_README.md` (V1, Sept 2026; overclaims corrected in
   report_latex_full ch. 11-12), `latex_report/` (V1 report).

## 4. Corrections that must not be undone

| ID | Superseded statement | Current statement | Source |
|---|---|---|---|
| X1 | (2026-09-30) W forms a 5d state ~0.19 eV BELOW the host CB, E_F pinned in it; W is a localized/deep donor in the 1 nm film; unexplained 1.1-1.65 eV vacuum-scale shift | Band-count error (In PAW has 4d10 = 5 bands/In, W PAW has 5s2 5p6 = 4 bands, so IWO cells have one fewer occupied band below the gap). W-5d-rich level is resonant 1.22 (1 nm), 1.34 (2 nm), 1.76 (bulk 24d), 1.80 eV (bulk 8b) above the host CB bottom at Gamma at the DFT filling (3 donated e/cell, 1.4e21-3e21 cm^-3); E_F lies 1.2-1.8 eV inside the host CB. "Pinning" is an interpretation; "stays above E_C at device density" is INFERRED | RESULTS_LOG 2026-10-05 CORRECTION; 2026-10-14 C022 caveat; ledger C022 |
| X2 | 1 nm dEv = -0.056 eV (EA/IP route) | -0.052 eV (-0.0521); dEc - dEv = 0.8998 eV = dEg(1 nm) | RESULTS_LOG 2026-10-14 errata item 1 |
| X3 | 2 nm IWO final SCF/projwfc from cluster 12835131 | cluster 12835211 (12835131 failed in mp_start_pools after 60 s) | errata item 2 |
| X4 | "0.75 nm and 0.51 nm slabs preliminary, not in RESULTS_LOG" | Logged 2026-10-14 (C021); 0.51 nm relaxes to In8(OH)24 (outside every law); 0.695 nm polar, no dipole correction, excluded from new primary dEc fits | RESULTS_LOG 2026-10-14; C021 |
| X5 | V1 "publication-ready", "validation", "confinement accounts for the 0.58 V step" | Calibrated, non-unique; every 6.3 nm out-of-sample test failed (C014 FALSIFIED); confinement not identifiable from I_D-V_G (C018, C020 caveat) | report_latex_full ch. 11-12; SYNTHESIS sec. K; ledger |
| X6 | 2 nm in-plane mass 0.206 m0 (4-point fit) quoted as "the" mass | Basis-dependent: band-edge (10-point Kane) 0.203 m0 at H-H 1.962 nm; 4-point deck basis differs by -3 % to +0.5 % | C039; RESULTS_LOG 2026-10-14 |
| X7 | W 0.6-0.7 muB moments as physics | Preliminary, likely spurious Stoner moments from coarse sampling of a degenerate gas; not claimed | RESULTS_LOG 2026-09-29 |
| X8 | MACE-MPA-0 amorphous structures as validated amorphous models | Registered force check OVERALL FAIL (W first shell); ML structures are DFT-relaxed starting points only | C037 |

## 5. Blind-analysis restrictions (binding for every session and every subagent)

- **Sealed ATLAS:** run_0075, run_0076, run_0077, campaign_C10_DIAGb (`config/sealed_runs.json` in the private tree).
  Not present here; do not seek them. S2-S7 outcomes are unknown and must appear only as placeholders.
- **Amorphous DFT electronic data:** every quantity of aIO_* / aIWO_* cells (classes, PR_n, gaps, edges, E_F,
  projections, eigenvalues). Release blocked by D-43 (conditional; requires F10, lineage audit, F9 CLAIMS_OK, logged
  clearance). Do not read `research_record/codex/work_chat/CODEX_WORK_CHAT.md` (877 kB, mixed content) except by
  narrow, non-numeric grep; do not read annex files named A44_*, archive_identity_*, or anything under
  `research_record/compute/amorph/` other than inputs, specs, scripts and protocols.
- **Known prior exposure (disclosed in the record, not by us):** A36 erratum (2.0 nm relaxation-SCF Fermi energies
  of aIWO_2p0_s2 and aIWO_2p0_comp_s1 parsed ~2026-10-12T12:49Z); paper_draft P28 (a Fermi energy of aIO_1p0_s1 at a
  non-final geometry in RESULTS_LOG 2026-10-11 13:36Z entry). The monograph does not reproduce these values.
- **H-N consequence (A37):** the registered H-N outcome is UNRESOLVED in every branch (2.0 nm thick endpoint cannot
  be scored). Neither CROSSOVER nor NO CROSSOVER can ever be claimed from this campaign. Per-cell classes may be
  reported only after D-43 release.
- Amorphous force-only results already logged (C034-C037) are permitted (forces/energies, no electronic quantity).

## 6. Publication and data-protection findings (to be expanded in the audit chapter)

- P-1 Measured transfer curves (4 devices) belong to the NTU fab group (Prof. Min-Hung Lee; Dr. M. Januar,
  Z.-F. Luo); the paper (Small Structures 7, e202500807, 2026; CC BY) releases data "upon reasonable request".
  Raw curves are already in the public repo (`data/`, and a copy under `inputs/astra_.../audit/sources/`).
  Permission is pending (charter sec. 8; HUM-001). The monograph may use them internally; the npj manuscript cannot
  publish them without the fab's permission.
- P-2 `report_latex_full/digest/papers/*.md` contains the full text of 11 papers (several not open access) and is
  committed to the public repo, although the .gitignore excludes `inputs/papers_text/`. Flag to the user; do not
  reproduce long passages. Used locally only to verify printed page numbers.
- P-3 `report_latex_full/digest/atlas_manual_pages.md` holds Silvaco manual page extracts (copyright; check scope).
- P-4 Authorship, data custody, AI-tool consent: undecided (HUM-001 fab meeting not held). Charter sec. 9: AI agents
  may not put claims in a manuscript without explicit human approval; the npj file is a scaffold for human review.

## 7. Progress by gate

| Gate | Status | Deliverables |
|---|---|---|
| 1 Repository mapped | DONE (this file, evidence/SOURCE_MAP.tsv) | |
| 2 Evidence indexed | DONE 2026-10-14 | evidence/SOURCE_MAP.tsv (40), FACT_REGISTRY.tsv (69; 13 raw-pointer facts verified against raw QE output, device facts independently recomputed from the CSV), CLAIM_SOURCE_MAP.tsv (40 ledger + 3 monograph proposals), REFERENCE_INDEX.tsv (70 keys; 62 journal entries verified against Crossref), FIGURE_INDEX.tsv (93). Builders in tools/. |
| 3 Synthesis approved internally | DONE (corrections X1-X8; audits in evidence/audits/) | |
| 4 Existing LaTeX assessed | DONE | main.tex skeleton builds (433 pp, 0 errors). Revised copies via tools/patch_13dft.py (46 patches) and tools/patch_reused.py (03, 09, 11, 14). Reused-by-reference files pinned in baseline_manifest.tsv (19). |
| 5 Chapters written | DONE 2026-10-14 | 523 pp, 0 errors, 0 undefined refs |
| 6 Critical review | DONE 2026-10-14 | Two independent reviews (theory referee; numbers/labels/blindness audit). Every finding verified before use; corrections V1-V11 in appendix MG (sec:mono-corr-review). Rejected: audit item 22 (donor count: 2.5e17 cm^-3 x 2 nm = 500 per um^2, the text was right). Not actionable without blocked sources: aIO_0p7_s1 composition (M11 table), SLAB_PROTOCOL details. Varley2012 checked (abstract covers In2O3). |
| 7 LaTeX validated | DONE 2026-10-14 | 530 pp, 0 errors, 0 undefined refs/cites, 0 multiply defined; bibtex: 2 empty-year warnings of baseline manuals only. \file redefined as breakable \nolinkurl (monograph_preamble.tex); overfull >15pt: 92 in all, 12 in monograph-owned files, of which 11 in *_rev copies of baseline text and 1 of 21pt in M07 (tools/overfull.py). |
| 8 npj manuscript scaffold | DONE 2026-10-14 | manuscript_npj/: main.tex (10 pp, builds clean), CLAIMS_USED.tsv (MS-01..15, all AWAITING APPROVAL), DECISIONS.md (N01-N45), FIGURE_PLAN.tsv, check_manuscript.py (passes), build.sh, README.md. Journal rules not checked (N36). |

## 8. Compilation notes

- Baseline `report_latex_full` needs `newtx`, TeX Gyre fonts, `binhex.tex` (plain-generic). Installed.

## 9. Exact next action

All gates done (2026-10-14). Remaining work needs the research owner: approvals (charter section 9), the fab
permission (N01), and the release decision (D-43). Old plan text below kept for history.

Gate 6: adversarial review (theory chapters; numbers/blindness consistency), then Gate 7 polish (overfull boxes via tools/overfull.py), then Gate 8 npj scaffold in research_monograph/manuscript_npj/ -> M10_w_and_vacancies ->
M07_provenance -> M08_c10_campaign -> M12_multiscale -> M13_alternatives_uncertainty -> M14_audit -> M02_questions ->
M01_introduction -> M03_literature_materials -> M15_conclusions -> M00 front matter -> MF, MH appendices.
After each chapter: tools/build.sh, fix errors, update section 11 below.

## 11. Architecture (fixed 2026-10-14)

- research_monograph/main.tex inputs: new chapters chapters/M*.tex; revised copies chapters/*_rev.tex (generated by
  tools/patch_13dft.py and tools/patch_reused.py from the baseline; never edit the *_rev.tex files by hand, edit the
  patch lists and re-run); unchanged baseline chapters by ../report_latex_full/... (pinned by tools/check_baseline.py).
- Preamble: monograph_preamble.tex = baseline preamble + \input@path + \graphicspath + macros \fact{NNN}, \claim{C0NN},
  \corr{Xn}, \dlog{D-nn}, \amend{Ann}, \sealedph{}, \pendingph{}, \vr \vk \vG \vR \Hop \Exc \vxc \vext \Ecut \PRn
  \mzero \Evac \dEv \dEgPBE \tHH \aIO \aIWO.
- Bibliography: ../report_latex_full/references.bib + bib/extra_DFT.bib + bib/monograph.bib (new keys; all DOI-verified).
  New citations are article-level (DOI-verified); page-exact citations only for papers in report_latex_full/digest/papers.
- Build: research_monograph/tools/build.sh -> build/main.pdf (build/ is git-ignored).
- Chapter status table: section 12.

## 12. Chapter status

| File | Status |
|---|---|
| 13_dft_rev, 03/09/11/14 _rev | DONE (patched; tools/patch_13dft.py 46, tools/patch_reused.py) |
| MG_corrections (appendix) | DONE (X1-X13, R1, D1-D2, T1-T5, P1-P2, record inconsistencies) |
| M11_amorphous_protocol | DONE (protocol only; Proposition prop:mono-hn = A37 consequence; reading guide written blind) |
| M04_dft_theory + M04b_dft_numerics | DONE (derivations; plane-wave counts and force-error scaling checked vs raw outputs) |
| M05_confinement_theory | DONE (Kane tests FACT-027..029a; figure figures/mono_confinement_models.pdf) |
| M06_defect_theory | DONE (hydrogenic/dielectric estimates FACT-080; PR-threshold property FACT-081; tab:mono-defect-pr) |
| M09_masses_parameters | DONE (C039/C040; BM1, BM6, BM7, BM9 figures; laws table; deck params; runs needed) |
| M10_w_and_vacancies | DONE (C022 table; X1 history; H-L scored table; fig09-fig11) |
| M07_provenance | DONE (RQ-001; mu_sat identity tested: obs/pred ratios 1.5-1.8, evidence/derived/musat_ratio.json) |
| M08_c10_campaign | DONE (design, H-A..H-F/H-J, S0/S1 seen only; S2+ sealed; A13 NC audit) |
| M12_multiscale | DONE (chain figure, budget table from evidence/derived/multiscale_budget.json) |
| M13, M14, M02, M01, M03, M15, M00 front matter | DONE |
| MF (generated by tools/make_registers_tex.py), MH resources | DONE |

## 13. Findings to report to the user (not yet reported)

1. H-N cannot return CROSSOVER or NO CROSSOVER (A37), independent of sealed data.
2. Frozen PR thresholds are not size-consistent across the registered cells (FACT-081): a W+6 O support of 7 atoms
   is 'localised' at 0.7/0.8/2.0 nm but 'intermediate' in bulk and at 1.0 nm. Reading aid only; rule unchanged.
3. Kane relation m_b(1+2 alpha dEc) reproduces the computed slab mass within 1 % at 2 nm and 10 % at 1 nm (no fit);
   to ~10 % the mass law and dEc law are one input (FACT-027, M004 as revised in Gate 6).
4. report_latex_full/digest/papers holds full text of 11 papers in the public repo (copyright concern P-2).
5. Baseline 13_dft errors corrected: donated density 5.5e21 -> 2.7e21; mixed dEv sign conventions; stale statuses.
6. Measured device curves are collaborator-owned and already public; permission pending (P-1).
7. DFT dEc(2.0)-dEc(6.3) implies a -0.21..-0.22 V threshold change vs measured -0.018 V: same sign/size as all
   failed 6.3 nm predictions (M12). Largest model-side input sensitivity: Nc convention (142 mV, S1-05/A13).
8. mu_sat identity mu V_D/(2V_ov - V_D) fails quantitatively on the curves (obs/pred 1.5-1.8): saturation peaks are
   numerical correspondences, not mobilities (M07).
9. Baseline citations corrected: W passivation claim is Januar2026 p. 4; HRTEM no long-range order p. 2.
10. A public commit message (50f627f) contains sealed-adjacent information; NOT used, not characterised further.
11. Gate 6 review corrections V1-V11 (appendix MG): SCF force noise is per-component ~6e-5 Ry/bohr, not 1e-3;
    vc-relax used BFGS, not Wentzcovitch dynamics; 2 nm valence-shift excess (38 meV) is resolved and unexplained;
    finite-barrier envelope model brings E1(2 nm) to 0.25 eV (not refuted, not predictive); dielectric enhancement
    small for the HfO2-backed stack; full W activation 6e20-1.8e21 cm^-3; M15 conclusions re-sorted (H-L, floor,
    mobility definition, confinement share no longer 'strongly supported'/'demonstrated').
12. New monograph claims M007 (rigid dEc transfer vs 6.3 nm) and M008 (mu_sat identity fails by 1.5-1.8).

## 14. NTU presentation (presentation_ntu/) -- DONE 2026-10-15

Beamer deck, 114 pages: 82 talk frames, plus 10 backup frames and 5 reference pages in the appendix. Clean build.
Two whole-deck reviews were run; their blockers and majors are resolved. Status and open minor items:
presentation_ntu/RESUME.md.
