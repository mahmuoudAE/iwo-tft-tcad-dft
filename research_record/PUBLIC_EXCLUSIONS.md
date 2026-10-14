# Public exclusions (2026-10-15)

`research_record/` is a copy of the tracked files of the private research repo
(`iwo-tft-research-private`, commit 21895d2) made with `git archive`. Some files were left out of
the public repo. This page lists them by path or pattern, with the reason. File contents are not
reproduced here. Excluded files stay local and nothing was deleted.

Reasons:
- **sealed**: ATLAS runs sealed under the state-only rule (`config/sealed_runs.json`: run_0075,
  run_0076, run_0077; campaign_C10_DIAGb), and AFF-6p3 / STRIP-6p3 outputs (none present).
- **amorph**: blind on the electronic data of the amorphous films (all `aIO_*` / `aIWO_*` cells;
  the 7 films are aIO_bulk_s1, aIWO_bulk_s1, aIO_1p0_s1, aIWO_1p0_s1, aIO_0p8_s1, aIO_0p7_s1,
  aIWO_0p7_s1). Every QE output, filtered output, archive identity, SHA256 manifest, log and derived
  result is excluded. Inputs (`*.in`, specs, geometries), scripts and docs are kept. Anything
  unclear was excluded.
- **copyright**: published literature, or text and images extracted from it.
- **secret-like**: session identifiers.
- **log**: `*.log` is ignored by the public `.gitignore`.

## Public repo (outside research_record/)

| Path or pattern | Reason |
|---|---|
| `results/sealed/**` | sealed |
| `results/runs/run_0075_*/**`, `results/runs/run_0076_*/**`, `results/runs/run_0077_*/**` | sealed |
| `results/campaigns/campaign_C10_DIAGb.json` | sealed (state-only campaign) |
| `results/RUN_INDEX.csv`: uncommitted rows for run_0075..0077 (left unstaged) | sealed |
| `report_latex_full/tools/atlas_user_manual_740p.txt` | copyright (Silvaco manual text) |

## qe_workflow/analysis_2026-10-13_full/

| Path or pattern | Reason |
|---|---|
| `raw_cern/amorph_forces_allowlist/**`, except `*.in` and `*.sh` (scf.allow.txt, compare_*, mace_ref.json, label_map.tsv, val_jobs.txt, FILTERED_SHA256.txt, SHA256_REMOTE.txt; 23 files) | amorph |
| `out/f14_amorph_force_checks.json`, `figures/fig14_amorph_force_checks.{pdf,png}` | amorph (derived from amorphous outputs) |
| `DFT_FULL_STUDY.md`, `digest_codex_ext.md` | amorph (these reports include the amorphous force-check section) |

## research_record/ (from the private repo)

| Path or pattern | Reason |
|---|---|
| `sources/Januar2026_SmallStructures.pdf` | copyright |
| `codex/independent_reviews/RQ-001_pdf_image_72.jpg`, `RQ-001_pdf_text_streams.txt` | copyright (extracted from the paper PDF) |
| `codex/work_chat/session_id.txt` | secret-like |
| `codex/work_chat/autodigest.log` | log |
| `codex/work_chat/annex/A44_add1_mapping_records/archive_identity_a{IO,IWO}_*.txt` (7) | amorph |
| `codex/work_chat/annex/A44_F13_SHA256MANIFEST.txt`, `A44_add1_lineage_inventory.txt`, `A44_add1_offset_evidence_lxplus.txt` | amorph (A44 sealed outputs) |
| `compute/amorph/bulkref/runs/a{IO,IWO}_bulk_s1/PROVENANCE` | amorph (unclear) |
| `compute/amorph/**/*.log` (22) and `compute/amorph/dft/D24_BD/install_20261011T003919Z/` | amorph (job and test logs) |
| `claude/atlas_campaign_plan_2026-10-14/prelaunch/dry_builds/*run0076form*` (4) | sealed (named after run_0076) |
| `claude/atlas_campaign_plan_2026-10-14/prelaunch/z9_wrapper_output.txt` | sealed (blind-leakage wrapper output) |

Also not published: regenerable scratch, files larger than 50 MB and copyrighted PDFs, all
covered by the existing `.gitignore`.
