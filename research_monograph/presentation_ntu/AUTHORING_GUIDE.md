# Authoring guide: NTU presentation (research_monograph/presentation_ntu/)

A talk to be given at National Taiwan University by the research owner, Mahmoud Elrasheedy (advisor Prof. Chao-Hsin
Wu, mentor Mukul Kumar). Audience: device physicists and materials scientists, including the fabrication group that
owns the device data (Prof. Min-Hung Lee's group, NTU). Style target: a talk at IEDM / VLSI / MRS / APS level,
written by a scientist: plain, dense with evidence, every number sourced, every literature statement cited.

## 1. What you may edit

- Only your own section file `sections/NN_name.tex`.
- Optionally new figure files `figures/NN_*.pdf`, produced by a script `tools/fig_NN_*.py` that you also write
  (matplotlib, plain style: white background, black axes, no titles or text boxes inside panels, labels on axes,
  serif or sans fonts at readable size; use the data files of the repository, never invented numbers).
- Do NOT edit `ntutalk.sty`, `main.tex`, other sections, or anything outside `presentation_ntu/`.
  If you need a macro, define it in your section file with `\providecommand`, with a name prefixed by your section
  number (e.g. `\sixDeltaE`).

## 2. Build and check (mandatory before you finish)

```
cd research_monograph/presentation_ntu
bash tools/build_section.sh NN        # NN = your two-digit section number
```
It prints errors, undefined citations, frame overflows (`Overfull \vbox`: content runs off the slide), overfull
hboxes > 5 pt and missing characters, and renders every slide to `build/sec_NN/png/p-XX.png`. Open the PNG files
with the Read tool and look at every slide. A slide is finished only when: 0 errors, 0 undefined citations,
no frame overflow, no overfull hbox > 5 pt, no missing characters, and the rendered slide looks clean (nothing
overlaps, nothing is clipped, text is not cramped, figures are legible, footnotes do not collide with content).

## 3. Theme macros (defined in ntutalk.sty)

| Macro | Use |
|---|---|
| `\partslide{Part n}{Title}` | first thing in your file: the part divider (not numbered) |
| `\begin{frame}{Title}` ... `\end{frame}` | one slide; optional `\framesubtitle{...}` |
| `\sref{key}`, `\sref[p.~4]{key}` | literature citation: inline mark `[n]`, full short reference at the slide foot |
| `\srefs{key1,key2}` | several works in one footnote |
| `\lab{computed}` | evidence label after a result (measured, derived, fitted, computed, inferred, unresolved, falsified, assumed, observed, hypothesis, theory) |
| `\src{...}` | small grey source line under a figure or table (e.g. `\src{This work, PAW-PBE; data: ...}`) |
| `\takeaway{...}` | one-sentence conclusion at the bottom of a slide (use on most result slides) |
| `\sealed{...}` | placeholder for a sealed or blind result |
| `\ntuemblem{h}` | NTU emblem (already in every frame title; do not add more logos) |
| `\InO`, `\IWO`, `\HfO`, `\AlO`, `\Vth`, `\Vthcc`, `\Vg`, `\Vd`, `\Id`, `\Ec`, `\EF`, `\Eg`, `\dEc`, `\dEv`, `\dEg`, `\tHH`, `\PRn`, `\kT`, `\cmcu`, `\cmsq`, `\cmVs`, `\cell{name}` | notation |

Packages available: graphicx, booktabs, array, tabularx, multirow, xcolor (colours `ntumaroon`, `inkgrey`,
`rulegrey`), tikz (arrows.meta, positioning, calc, fit, shapes.geometric), amsmath, siunitx (`\num`, `\SI`),
adjustbox. 16:9 slides, text width about 14.2 cm.

Figures: `\includegraphics[width=...]{name}` with the file name only (no directory, no extension). The search path
covers: `presentation_ntu/figures/`, `research_monograph/figures/`, `report_latex_full/figures/`,
`qe_workflow/analysis_2026-10-13_full/figures/`, `qe_workflow/analysis_2026-10-13_full/bands_masses/figures/`,
`analysis_2026-10-06_extraction/figures/{final,paper,.}`. Check `research_monograph/evidence/FIGURE_INDEX.tsv`
before using a figure: for first-principles results use ONLY the re-derived figures (`fig01`-`fig13`,
`BM1`-`BM9`, `mono_*`); the `report_latex_full/figures/dft_*` files are marked "check-DFT-currency" and may show
superseded values (e.g. the pre-correction W picture): do not use them. Device and TCAD figures marked "reuse"
are fine. Read a figure's caption in the monograph or the report before using it, and say on the slide what it shows.

## 4. Visual style (plain academic; must not look machine-made)

- White background, black text. The only colour accent is `ntumaroon`, and only sparingly (e.g. one emphasised
  number or one arrow in a TikZ diagram). No coloured boxes, no shaded blocks, no icons, no emoji, no clip art, no
  gradients, no rounded "cards". Tables: booktabs, no vertical rules.
- Assertion-style frame titles: the title states the slide's message ("The mass increase follows the bulk
  non-parabolicity at 2 nm"), not a topic word ("Masses"). Keep titles to one line (about 70 characters).
- Body text `\small` by default; never smaller than `\scriptsize` for content (footnotes and `\src` are smaller
  by design). At most 6 bullets per slide and 2 bullet levels. Prefer one figure plus 2-4 bullets, or one table
  plus 2-3 bullets. Use `columns` for figure + text.
- Equations: display the key ones properly (amsmath); define every symbol on the slide or in a short "where" line.
- No filler. Words to avoid: delve, leverage, harness, unlock, seamless, cutting-edge, game-changer, robust (unless
  in the technical sense defined in the register), comprehensive, "In conclusion", "It is worth noting".
- Write in plain technical English, short sentences, units always given (SI with `\,`), thicknesses in nm.

## 5. Accuracy and evidence rules (binding)

1. Every number must come from these sources, in this order of precedence, and must match them exactly (rounding
   only): `research_monograph/evidence/FACT_REGISTRY.tsv`, `research_monograph/evidence/CLAIM_SOURCE_MAP.tsv`,
   the monograph chapters `research_monograph/chapters/M*.tex` and `*_rev.tex` (current after the Gate 6
   review), `research_monograph/evidence/derived/*.json`, `research_record/03_CLAIMS_LEDGER.yaml`,
   `qe_workflow/cern_htcondor/results/RESULTS_LOG.md` (newest entries supersede older ones). Do not take numbers
   from `report_latex_full/chapters/*.tex` unless the same statement is in a `*_rev.tex` copy or a monograph
   chapter (the baseline contains corrected errors).
2. Never undo a correction: see `research_monograph/appendices/MG_corrections.tex` (X1-X13, R1, V1-V11). In
   particular: W is a resonant donor 1.2-1.8 eV above the host conduction-band minimum (never "below the conduction
   band", never "deep donor"); the donated density of the bulk W cells is 2.7e21 cm^-3; the 1 nm valence shift is
   -0.052 eV; the Kane mass relation holds within 1 % at 1.962 nm and 10 % at 0.930 nm (the two thinner films do not
   test it); the SCF force noise is about 6e-5 Ry/bohr per component; H-L is UNRESOLVED overall (never write "H-L
   supported"); every 6.3 nm out-of-sample threshold prediction FAILED; the published mobilities are reproduced
   numerically by the saturation-formula peak, which is the leading candidate (INFERRED) for the paper's definition.
   Marzari-Vanderbilt (cold) smearing as implemented in Quantum ESPRESSO (correction V12, 2026-10-15): the weight is
   0.40 at the Fermi level, never negative, and EXCEEDS ONE below the Fermi level (maximum 1.083 at x = -sqrt2); the
   printed occupations of the 8b W cell reach 1.074. Any statement of "negative MV weights", "0.60 at mu" or
   "minimum -0.083" is wrong.
3. Attach the evidence label (`\lab{...}`) to every result: measured, derived, fitted, computed, inferred,
   unresolved, falsified, assumed. Never present a fitted or calibrated agreement as a prediction or validation.
   Say what was fitted and what was tested.
4. Literature: cite only keys that exist in `report_latex_full/references.bib`, `report_latex_full/bib/extra_DFT.bib`
   or `research_monograph/bib/monograph.bib` (list: `research_monograph/evidence/REFERENCE_INDEX.tsv`). Cite a paper
   only for what the monograph already cites it for (grep the key in `research_monograph/chapters/` and
   `report_latex_full/chapters/` to see the supported statement). Page numbers (`\sref[p.~N]{key}`) only where the
   monograph uses that page. Never invent a reference, a page or a quotation.
5. Device data (the four transfer curves) belong to the fabrication group; every slide that shows them carries
   `\src{Data: Prof.\ M.-H.\ Lee's group, NTU; device study \cite...}` or similar plus `\sref{Januar2026}`.

## 6. Blind-analysis rules (binding; violations cannot be undone)

- Do not open, list or search: `research_record/compute/amorph/` (except inputs/specs/protocols already summarised
  in the monograph), any `results/sealed/`, `run_0075*`, `run_0076*`, `run_0077*`, `campaign_C10_DIAGb`, files named
  `A44_*` or `archive_identity_*`, `research_record/codex/work_chat/CODEX_WORK_CHAT.md`.
- Never state, estimate or hint at any electronic quantity of the amorphous `aIO_*` / `aIWO_*` cells (classes,
  PR_n values, gaps, edges, Fermi levels, projections). Only protocol facts and force-only checks (C034-C037) may
  appear. Per-cell outcomes are `\sealed{...}`.
- Never state or hint at any ATLAS campaign result from stage S2 onward. Stage S0/S1 results that the register marks
  as "seen before revision 2" may appear (as in monograph chapter M08). Everything else is `\sealed{...}`.
- Do not mention the content of public commit messages about sealed runs.
- H-N: by the frozen rules (amendment A37) its registered outcome is UNRESOLVED in every branch; neither a
  crossover nor its absence can be claimed (monograph Proposition prop:mono-hn).

## 7. What to return

When finished, reply with: the number of slides; the list of figures used; the citation keys used; and a list of
every number on your slides with its source (file and line or registry ID), so that an independent reviewer can
check them.
