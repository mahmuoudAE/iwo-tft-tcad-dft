# Decision points, checks and pending results of the npj manuscript framework

Numbering: N01-N40 keep the numbers of P01-P40 in
`research_record/claude/paper_draft_2026-10-13/TODO.md`, so the two lists can be read side by side; N41-N45 are new.
Status as of 2026-10-14, from the public record in this checkout (decision log up to D-58). The private record and
the sealed outputs are not in this checkout, so a status marked "not re-checked" may have moved.

Kinds: DECISION (a human must decide), CHECK (verifiable fact to settle), RESULT (waits for a computation or a release),
CITATION, TEXT (wording that waits for another item), DISCLOSURE.

| N | Kind | Item | Status 2026-10-14 | Waits for |
|---|---|---|---|---|
| N01 | DECISION | Permission to use and publish the fabrication group's four transfer curves (already in the public repo), data custody, authorship | OPEN (HUM-001 meeting not held). Blocks Figs. 5 and S-device, MS-09, MS-10, any device number in the paper | Fab group / research owner |
| N02 | CHECK | 0.695 nm point in the V3 laws not in RESULTS_LOG | RESOLVED: logged 2026-10-14 (C021); point excluded from the primary dEc fits (monograph correction X4) | - |
| N03 | CHECK | Fab's mobility/swing recipe | OPEN. Partly answered by the monograph (M07: the saturation formula reproduces the paper's numbers; the identity fails quantitatively, M008) | Fab confirmation |
| N04 | CITATION | Oxide band parameters, tunnelling masses, Lenzlinger-Snow, Ielmini TAT, IGZO.TOKYO, capture cross-sections | OPEN | Page-exact literature pinning |
| N05 | RESULT | H-B (S2-14..S2-17, STRIP-6p3) | SEALED / not launched (D-58 plan) | D-58 launches, then the release protocol |
| N06 | RESULT | H-C (S2-11 rerun, S2-01..S2-13) | SEALED. run_0075 kept sealed, invalid, never substituted; S2-11 rerun ordered (D-44/A41) | Release protocol |
| N07 | RESULT | H-D (S4, native triples) | PENDING (D-58) | S4 |
| N08 | RESULT | H-E (S3-01..S3-03, AFF-2p0, AFF-6p3) | PENDING / SEALED | DIAG launches (D-58) |
| N09 | RESULT | H-F (S3-10..S3-13, S3-27) | PENDING; H-F operational scoring freeze not re-checked | Freeze, then DIAG_HF |
| N10 | RESULT | H-J (S4a, S4c, S5) | PENDING | S4/S5 |
| N11 | DECISION | Sign-off of the S2 resolution method | RESOLVED: D-44 (A41, 2026-10-13T02:16Z), ASSUMED operational method | - |
| N12 | DECISION | Matched numerical refinement runs | PARTLY RESOLVED: frozen refinement trigger for S2-04/S2-06/S2-08, at most 6 launches (D-44) | User go per launch |
| N13 | CHECK | Runner revision 3 committed, Codex verdict | Not re-checked | Record |
| N14 | DECISION | run_0075 rulings | RESOLVED for use: sealed, invalid, never substituted (D-44) | - |
| N15 | RESULT | Final launch count and status of every launch | PENDING (17 of 200 C10 launches used by 14 Oct, D-58) | End of campaign |
| N16 | RESULT | H-L energies, k3/k4, A20 sensitivities | RESOLVED for energies and k3/k4 (C038, MS-08); A20(i) spin sensitivity staged, not run (D-45); H-L stays UNRESOLVED | A20(i) run after a separate go |
| N17 | CITATION / CHECK | MACE architecture and MACE-MPA-0 model; complete per-calculation settings table | Citation RESOLVED (Batatia2022, Batatia2023; DOI/arXiv verified). Settings table for the SI: OPEN (copy from monograph Ch. 13, M04b) | - |
| N18 | RESULT | Relaxation status of every amorphous cell at the 17 Oct cutoff | PENDING | Cutoff |
| N19 | RESULT | 2.0 nm MACE force-check frames; Hf force check | Not re-checked | DFT agent record |
| N20 | RESULT | A15 audit outcome, provisional width, A36 rescue need, C4 polishes | BLIND (D-43) | Release protocol |
| N21 | RESULT | Restart-gate and qualification outcomes | Not re-checked; partly blind | Record / release |
| N22 | CHECK | Frozen reader reproduced 3 % W-5d and dEc 0.281 eV | Not re-checked | DFT agent record |
| N23 | RESULT | H-N per-cell classes; H-G, H-H, H-K scores | SEALED. D-43 is a conditional release, blocked until F10, lineage audit, F9 CLAIMS_OK and logged clearance. Note: the registered H-N series outcome is UNRESOLVED in every branch (A37; MS-13) | D-43 release |
| N24 | RESULT | A23 hybrid checks (W cell, amorphous bulk) | PENDING / BLIND | A23 jobs; D-43 |
| N25 | RESULT | CPU/GPU hours after 4 Oct | PENDING (monograph App. MH gives totals to 4 Oct only) | End of CERN access |
| N26 | DECISION | Charter adoption (D-10) | OPEN (charter PROPOSED) | Research owner |
| N27 | CHECK | External timestamp of the register (DOI or public tag) | OPEN. Any push or DOI needs the owner's approval (charter section 9) | Research owner |
| N28 | DISCLOSURE | Pre-release sight events (A36 erratum; RESULTS_LOG 2026-10-11 13:36Z Fermi energy of aIO_1p0_s1) | OPEN. The framework does not reproduce either value | Register erratum or ruling |
| N29 | TEXT | Per-cell sight-history table | Waits for N23 | - |
| N30 | RESULT | Scorecard of every registered prediction | PENDING | All scoring and releases |
| N31 | TEXT | Safeguards wording in the limitations | Waits for N26, N27 | - |
| N32 | TITLE | Title | OPEN; working title in main.tex comment, not approved | After N30 |
| N33 | TEXT | Abstract | Candidate abstract written from supported claims only; one placeholder sentence for sealed results | Approval; N23, N05-N10 |
| N34 | DECISION | Authors, order, affiliations | OPEN | Agreement with the fab group |
| N35 | TEXT | Figure plan; final introduction paragraph | Figure plan drafted (FIGURE_PLAN.tsv); final hypothesis list waits for releases | Approval |
| N36 | DECISION | Target journal and its current rules | npj Computational Materials named by the owner as the target for this framework. Its current length, display-item, reference and statement rules were NOT checked in this session; check the guide for authors before drafting to length | Owner |
| N37 | TEXT | Data availability | Waits for N01 | - |
| N38 | TEXT | Code availability, archive with DOI | OPEN | Owner decision on repositories and DOI |
| N39 | TEXT | AI-use statement | Waits for N36 | - |
| N40 | TEXT | Acknowledgements, competing interests | OPEN | Owner |
| N41 | DECISION | Whether the W band-counting correction (X1) is told in the paper or only in the SI | OPEN | Owner |
| N42 | DECISION | Copyright: the public repo holds full texts of 11 papers (report_latex_full/digest/papers) and Silvaco manual extracts | OPEN (monograph finding P-2/P-3) | Owner |
| N43 | CHECK | Literature statement "no peer-reviewed DFT study of W in In2O3 located" | Re-run the search before submission | Literature search |
| N44 | DECISION | Whether the device-model sections (MS-09 to MS-11, sealed campaign) belong in this computational-materials paper or in a separate device paper | OPEN; the framework keeps them as a short section | Owner |
| N45 | CHECK | Public commit message 50f627f names an S2-11 score (sealed-adjacent); not used here | Owner to decide whether it counts as a sight event | Owner / Codex |
