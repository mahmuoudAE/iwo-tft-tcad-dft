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
| 5 Chapters written | pending | |
| 6 Critical review | pending | |
| 7 LaTeX validated | pending | |
| 8 npj manuscript scaffold | pending | |

## 8. Compilation notes

- Baseline `report_latex_full` needs `newtx`, TeX Gyre fonts, `binhex.tex` (plain-generic). Installed.

## 9. Exact next action

Gate 5: write the new chapters in this order (priority): MG_corrections (appendix) -> M11_amorphous_protocol ->
M04_dft_theory -> M05_confinement_theory -> M06_defect_theory -> M09_masses_parameters -> M10_w_and_vacancies ->
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
| 13_dft_rev, 03/09/11/14 _rev | DONE (patched) |
| all M* chapters and MF/MG/MH | STUB |

## 10. Verification results of Gate 2 (do not redo)

- Raw-pointer facts: all verified (a = 2 x 5.153045099 A; H-H 1.9623 / 0.9303 nm from scf.in; bulk CBM/VBM in
  bands_path.out blocks; HSE 9.9936 - 7.8856 = 2.1080 eV; NC-PBE 9.8209 - 8.9005 = 0.9204 eV).
- Device: V_th,cc 0.6618 / 0.6440 / 0.0825 V; floors 4.606e-15 / 1.528e-13 / 6.597e-12 A/um; I_D(+3 V)
  5.090e-7 / 4.034e-7 / 3.071e-6 / 3.590e-6; mu_sat peaks 5.087 (1.75 V) / 3.858 (2.55 V) / 27.403 (0.95 V);
  C_ox 8.955e-7 F/cm2 reproduced from the stack. All agree with the ledger within rounding.
- Note for M002: computed -dEv is ~0.05 eV at both 1 and 2 nm (no power law), unlike EMA hole confinement.
