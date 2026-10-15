# Resume point (paused 2026-10-15 at the user's request)

State: all 15 sections drafted, double-reviewed and fixed; whole-deck review 1 done (`review/deck_review_1.json`,
31 findings); deck-level fixes applied (theme, citations, references, closing order, appendix, top alignment).
Last full build: 112 pages, 0 errors, 19 small frame overflows (top alignment).

Section fixes for deck review 1 (rules G1-G10 in AUTHORING_GUIDE.md section 8):
- done: 01, 02 (results in `review/deckfix_results.json`)
- interrupted mid-edit (re-check): 03, 04
- not started: 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 16
  Per-section task lists: the args of workflow `ntu-presentation-deck-fixes` (also summarised in deck_review_1.json).

To continue: for each remaining section, apply the findings of `review/deck_review_1.json` for its file plus G1-G10,
run `bash tools/build_section.sh NN`, check the PNG renders; then full build (`bash tools/build.sh`), a second
whole-deck review, commit, push, and send build/main.pdf.
