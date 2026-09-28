# Full LaTeX report: lean workflow plan and stage prompts

Target: an Overleaf-ready ZIP of the complete source-traceable report. It contains:
- the literature, with every item used and its exact page
- the inputs
- one section per parameter with its derivation
- the code
- all important runs, including the non-fitting ones
- the results, predictions and validation status

Budget cap: $50. Effort: high by default, extra-high only where marked.
Paths:
- `REPORT` = `IWO_PHYSICS_CONSTRAINED_MODEL_V1\report_latex_full`
- `PKG` = `IWO_PHYSICS_CONSTRAINED_MODEL_V1`

Already done (on disk):
- `REPORT/main.tex`, `preamble.tex`, `references.bib`, `bib/extra_*.bib`
- `CONVENTIONS.md` (hard rules, page map, label and figure registries)
- `figures/src/style.py`
- `tools/lint_latex.py`
- `PKG/analysis_2026-09-25/` (EVIDENCE_BRIEF, S1-S6, REVIEW, SYNTHESIS, PREDICTIONS_REGISTER)

## Handoff (start of the fresh session)
Paste this to start the new session:
> Continue the IWO full LaTeX report. Read `IWO_PHYSICS_CONSTRAINED_MODEL_V1\report_latex_full\WORKFLOW_PLAN.md` and `CONVENTIONS.md`, then execute the stages in order. Do not re-read the old conversation. Budget +3.5M tokens.

---

## Stage 0: Digest build (main session, Python scripts, no agents, ~$1) -- DONE 2026-09-25
Status: digest built; 23 figures generated and visually checked + 8 copied; code (13 scripts, 26 analysis scripts), 11 decks, configs and data copied; A_runs_table.tex (56 rows) and D_hashes_table.tex (44/44 hashes identical) generated.

Scripts to write and run:
- **`tools/build_digest.py`** writes `REPORT/digest/`. Contents:
  1. **`papers/<key>.md`:** each paper's pages, pre-split with the printed page number from the CONVENTIONS page map.
  2. **`used_items.csv`:** every literature item the model uses (key, quantity, value, printed page, model parameter). Sources:
     - `tables/PARAMETER_PROVENANCE.csv`, `THICKNESS_LAW_EVIDENCE.csv`, `docs/MATERIAL_PARAMETER_EXTRACTION.md`
     - a grep of S1-S6 and SYNTHESIS for citations
     - each page confirmed by string search in the page text
  3. **`atlas_manual_pages.md`:** the manual pages for every deck statement and parameter, extracted with pypdf from `atlas_users1.pdf`, with printed page numbers.
  4. **`runs.csv`:** all 52 runs (id, film, label, category, overrides, status, Vth_cc, Vth_lin, fixed-current SS, SS_cc, gm_max, mu_FE, Ion, RMSE, elapsed), built from RUN_INDEX and execution.json.
  5. **`numbers.md`:** the key numbers from SYNTHESIS, S1-S6 and PREDICTIONS_REGISTER, each with its source line.
- **`tools/make_figures.py`** builds all 29 registry figures with `style.py`, from real run and data files. The figure registry is in CONVENTIONS section 7. The existing PNGs are copied.
- **`tools/make_appendix_assets.py`:**
  - copies scripts, decks, configs and data into `REPORT/code` and `REPORT/data`, ASCII-sanitised
  - generates `appendices/A_runs_table.tex` (the longtable from `runs.csv`)
  - generates `appendices/D_hashes_table.tex` (hashes re-verified)
- **Check:** run all three, then view each figure PNG once to catch layout problems.

## Stage 1: Writers, batch 1 (3 agents in parallel)
Common header (prepend to every writer prompt):
> You are writer {TAG} of a publication-grade LaTeX report (UC Berkeley dissertation standard) on thickness-dependent ultrathin IWO TFTs and their ATLAS TCAD model.
>
> READ FIRST: `REPORT/CONVENTIONS.md`, `REPORT/preamble.tex`, `PKG/analysis_2026-09-25/SYNTHESIS.md` (conclusions and section K corrections), and `REPORT/digest/` (papers by printed page, used_items.csv, atlas_manual_pages.md, runs.csv, numbers.md).
>
> Use the digest instead of the raw sources. Open a raw file only to confirm a detail missing from the digest.
>
> YOU OWN: {FILES} (plus `bib/extra_{TAG}.bib` for new keys). Write only these.
>
> Rules:
> - ASCII only; use the macros.
> - Every literature statement is cited with the exact printed page, checked in `digest/papers`.
> - Every simulated number carries its run ID. Invent nothing.
> - No long quotations.
> - Use `\cref`, and only to labels you own or labels in the registries.
> - Include only the registry figures you own.
> - Do not launch ATLAS.
>
> Resilience:
> - Create the file skeleton first (all headings and labels).
> - Fill it section by section, saving after each section.
> - If the file already exists, continue it instead of starting over.
>
> Finally, re-read your file and fix LaTeX errors. Return the files, labels defined, and open issues.

- **W1 Literature, extra-high effort.** Files: `02a_literature_target.tex`, `02b_literature_in2o3.tex`, `02c_literature_methods.tex`, `02d_provenance.tex`.
  - Task: the L1 + L2 + L3 tasks of `workflows/scripts/iwo-full-latex-report-*.js` (verbatim scope). Every paper gets:
    - a summary
    - every item used (value, exact page, how it enters the model, `\cref` to the parameter section, caveat)
    - items not used, and why
    - contradictions
  - Also: the ATLAS manual section and the master provenance longtable, built from `used_items.csv`.
- **W2 Derivations I, extra-high effort.** File: `04_derivations_electrostatics.tex`. Task: the D1 task (every D1 parameter section with the fixed structure: definition; values; source and page; full derivation, or how it could be derived; ATLAS statement and manual page; sensitivity runs; status).
- **W3 Derivations II, extra-high effort.** File: `05_derivations_transport.tex`. Task: the D2 task.

## Stage 2: Writers, batch 2 (3 agents in parallel, high effort)
Same common header.
- **W4 Inputs and numerics.** Files: `00_nomenclature.tex`, `03_device_data.tex`, `06_numerics.tex`, `appendices/A_runs.tex` (which wraps the generated `A_runs_table.tex`, adds notes on non-standard runs, and summarises the V0/Astra history), `appendices/B_code.tex`, `appendices/C_decks.tex`, `appendices/E_reproducibility.tex`. Task: the C1 + C2 tasks, plus the R1 appendix part. Listings use the files copied in Stage 0.
- **W5 Results.** Files: `07_calibration.tex`, `08_six_nm.tex`, `09_mechanisms.tex`. Task: the R1 chapter part and the R2a task. It must cover every important run, including the non-fitting ones, the parameter-control matrix, the 6.3 nm hypothesis study with its pre-registered predictions and their outcomes, and the mechanism verdicts.
- **W6 Framing.** Files: `00_abstract.tex`, `01_introduction.tex` (with the TikZ workflow figure), `10_predictions.tex`, `11_validation.tex`, `12_conclusions.tex`, `appendices/D_register.tex` (which wraps `D_hashes_table.tex`). Task: the R2b + R3 tasks.

## Stage 3: Scripted verification (main session, ~$1)
- **`tools/check_citations.py`:** for every `\citep[p.~X]{key}`, take the sentence around it, extract its numbers and key terms, and search page X of the digest.
  - Output `tools/citation_report.csv`: status `OK`, `NOT_ON_PAGE` (with the page where it was found), or `NOT_FOUND`.
- **`tools/lint_latex.py`:** checks labels, refs, cite keys, figures, listings, ASCII, environments, braces and math mode.
- **Number check:** a script compares numbers in the `.tex` files that sit next to a run ID against `runs.csv`, within tolerance.
- **Fixes:** mechanical errors are fixed directly in the main session. Everything else is collected into `tools/verify_queue.md`.

## Stage 4: Adversarial verification (2 agents, extra-high effort)
Prompt:
> You are verifier {V} of the IWO LaTeX report.
>
> READ `REPORT/CONVENTIONS.md`, `tools/verify_queue.md`, `tools/citation_report.csv`. YOU OWN AND MAY EDIT ONLY: {FILES}.
>
> 1. Resolve every queued item in your files. For a citation flagged `NOT_ON_PAGE` or `NOT_FOUND`, open the digest page. Then either correct the page or rewrite or remove the claim.
> 2. Independently re-check at least 25 load-bearing numbers per file against `runs.csv`, `numbers.md` and the primary files.
> 3. Check that every claim agrees with the SYNTHESIS verdicts and the section K corrections:
>    - confinement is not identified;
>    - run_0027 is retracted;
>    - SS_min is not robust;
>    - the tmu caveat applies;
>    - the model is calibrated, not validated.
> 4. Check that every figure caption matches its PNG.
> 5. Check LaTeX hygiene.
>
> Log all changes to `tools/verify_{V}.md`. Do not launch ATLAS.

- **V1** owns chapters 02a-02d, 03, 04 and 05.
- **V2** owns chapters 06-12 and all appendices.

## Stage 5: Consistency pass (1 agent, high effort)
Prompt:
> Read the whole report in order: `main.tex`, then each chapter.
>
> Fix, in any file:
> - cross-chapter contradictions (the same quantity given different values or verdicts);
> - broken narrative flow (each chapter needs an opening, its body, and a closing key-result box);
> - duplicated passages (replace them with `\cref`);
> - wording that overclaims relative to SYNTHESIS.
>
> Keep every citation page and number unchanged unless it is demonstrably wrong. Log the changes to `tools/consistency.md`.

## Stage 6: Build (main session)
1. Run `lint_latex.py` until it reports 0 errors.
2. If TeX is available (MiKTeX, with the user's permission), compile with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` and fix errors until a clean PDF is produced.
3. Zip `REPORT` to `PKG/results/IWO_TCAD_full_report_latex_2026-09-25.zip`. Exclude `tools/*.md` logs? No: keep them, since they are the audit trail. The ZIP contains the report, figures, code, data, digest and logs; it does not contain the papers' full texts.
4. Send the ZIP, the compiled PDF if one was made, and a summary to the user.

## Budget guard
- Launch the stages sequentially. After each stage, check the spend. Stop and report if the remaining budget is below the next stage's estimate.
- Rough estimates:

| Stage | Estimate |
|---|---|
| 0 | $1 |
| 1 | $12-18 |
| 2 | $8-12 |
| 3 | $1 |
| 4 | $6-9 |
| 5 | $3-5 |
| 6 | $1 |
| **Total** | **$32-47** |

