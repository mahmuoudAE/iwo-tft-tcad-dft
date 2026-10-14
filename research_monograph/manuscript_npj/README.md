# npj Computational Materials manuscript framework

**Status: framework for human review, 14 October 2026. Not a submission draft. Nothing here is approved.**
Under charter section 9 (`research_record/00_PROJECT_CHARTER.md`), no AI agent may put a claim in a manuscript without
the research owner's explicit approval. Every result sentence in `main.tex` is a *candidate*, tagged with its evidence and
listed in `CLAIMS_USED.tsv` as AWAITING APPROVAL.

## Files

| File | Content |
|---|---|
| `main.tex` | Article: candidate abstract, introduction, results (6 subsections), discussion points, methods, statements. Sealed results are `\sealed{...}` blocks; open items are `\pending{Nnn}{...}`. |
| `ms_preamble.tex` | Packages and macros. `\ev{...}` prints evidence tags (hide them with `\evfalse`). |
| `CLAIMS_USED.tsv` | The 15 candidate manuscript claims MS-01..MS-15: statement, charter label, evidence (facts, ledger and monograph claims), monograph location, conditions, approval status. |
| `DECISIONS.md` | N01-N45: decisions, checks, pending and sealed results. N01-N40 keep the numbers of P01-P40 of `research_record/claude/paper_draft_2026-10-13/TODO.md`, with status updated to the decision log up to D-58. |
| `FIGURE_PLAN.tsv` | Main and SI display items with sources, generators and conditions (sealed, permission). |
| `check_manuscript.py` | Checks that every evidence tag resolves to the registers, every MS claim is used, every placeholder is listed in `DECISIONS.md`, no superseded or overclaiming phrase appears, and no amorphous cell name is followed by a value. |
| `build.sh` | Runs the checks, then pdflatex/bibtex into `build/` (git-ignored). |

Build: `bash research_monograph/manuscript_npj/build.sh` produces `build/main.pdf` (10 pages on 14 Oct; 0 errors, 0
undefined references; the only BibTeX warning is the empty year of `AtlasManual`).

## What the framework claims, and what it does not

Supported (computed, derived or recorded; crystalline PBE unless stated):
- confinement of crystalline In2O3 films (gap opening, band partition, exponents, HSE/PBE ratio);
- the no-fit Kane relation between the confinement shift and the in-plane mass (the two laws are one input);
- W as a resonant donor in crystalline cells at their filling (device-density behaviour INFERRED);
- the registered oxygen-vacancy test H-L, overall UNRESOLVED (never "supported");
- the rigid transfer of the computed shift to the device threshold (needs the fabrication group's permission, N01);
- two properties of the registered amorphous read-out that follow from its frozen rules alone (size-dependent PR
  thresholds; H-N cannot return CROSSOVER or NO CROSSOVER).

Not claimed, placeholders only:
- every result of the ATLAS C10 campaign from stage S2 on (runs 0075-0077, C10_DIAGb);
- every electronic quantity of the amorphous aIO_*/aIWO_* cells (H-G, H-H, H-K, H-N per-cell classes);
- the scorecard, the title, the final abstract sentence on the sealed work, authorship and all statements.

## Rules for whoever continues this

1. Do not fill a `\sealed{}` block except from released results under the D-43 protocol; never by inference from
   figures, logs, file names, sizes or timestamps.
2. Every new result sentence gets an `\ev{}` tag and a row in `CLAIMS_USED.tsv`; run `check_manuscript.py`.
3. Numbers come from `research_monograph/evidence/FACT_REGISTRY.tsv` or the ledger, never from older summaries; the
   corrections X1-X13 in the monograph appendix MG must not be undone (for example: W is resonant, not below the
   conduction band; the donated density of the bulk W cells is 2.7e21 cm^-3, not 5.5e21).
4. The journal's current guide for authors (length, display items, references, statements) has not been checked
   (N36). Check it before cutting to length.
5. The device data are collaborator-owned; no figure or number from them goes into a submission without written
   permission (N01).
