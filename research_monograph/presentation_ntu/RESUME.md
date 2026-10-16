# Status (2026-10-15): presentation complete

Final build (`bash tools/build.sh` -> `build/main.pdf`): 114 pages, 0 errors, 0 undefined citations or references,
0 frame overflows. The footer numbers the talk 1/82 (title to "Thank you") and the appendix 1/15 (10 backup frames and
5 reference pages).

Two whole-deck reviews have been run. All blocker and major findings are resolved. Review 1 is in
`review/deck_review_1.json`; the review 2 major item (X versus V correction naming) was fixed by hand.

Open minor items (optional):
- The convergence figure on p. 36 is small.
- The band labels on p. 55 overlap the curves.
- The tables on pp. 20 and 86 are dense.
- The reference list mixes journal-name styles, and some DOIs print with spaces.
- 9 overfull hboxes, each under 5 pt.

Length: 82 talk frames, about 2 h. For a shorter slot, move Part 13 (computational cost) and selected method slides
of Part 5 to the backup.

# PowerPoint conversion (paused 2026-10-16 at the user's request)

Local conversion only (no online converter: the deck holds unpublished, collaborator-owned data). Tools in `tools/pptx/`:
- `make_all.sh`: marked build, conversion, LibreOffice rendering, review images and width check (about 10 min).
  It writes `build/IWO_NTU_presentation_exact.pptx` (each slide one 2560 px picture of the PDF page, pixel-identical;
  done, sent) and `build/IWO_NTU_presentation_editable.pptx` (editable text boxes over a background picture).
- `charcheck.py`: last result 111513/111528 text characters found in the rendering, nearly all within 1 pt.

Editable version, state: all text placed from the PDF with kerned Arial widths. Sub-/superscripts and text after
thin spaces are separate boxes, because LibreOffice ignores negative spacing on spaces. Figures, display equations
and special glyphs are pictures.
To do:
1. Title placeholder: holds only the first word group of titles split at wide spaces (title slide shows
   "Thickness-Dependent"). Join the title-row segments, or use a hidden full-title placeholder as in the exact file.
2. Look at the 15 missing characters and the offsets of 2-4 pt (p2, p107, p8, p69, p96) in
   `build_pptx/check/charcheck.txt`.
3. Rerun the visual review workflow (script `pptx-visual-review`, 10 reviewers over `build_pptx/check/img`). It was
   stopped at the pause, before any reviewer had reported.
4. Send `build/IWO_NTU_presentation_editable.pptx`.
