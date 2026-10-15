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
