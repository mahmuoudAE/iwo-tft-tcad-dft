# Public exclusions (2026-10-15; updated 2026-10-23)

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

### Added 2026-10-22 (ATLAS campaign C10 after run_0074; REG-001)

Published on 2026-10-22: run directories run_0157..0159 (S4c) and run_0161..0163 (S4d), the S4c campaign record
`results/campaigns/campaign_C10_S4c.json`, and the RUN_INDEX rows of run_0078, run_0157..0159 and run_0161..0163.
Everything below stays local and untracked. The explicit patterns are in `.gitignore` (blind-guard extension of
2026-10-22, and its section "pending user OK 2026-10-22"), so `git add -A` cannot stage them. Nothing was deleted.

| Date | Path or pattern | Reason |
|---|---|---|
| 2026-10-22 | `results/runs/run_0079_*` .. `run_0096_*`, `run_0102_*` .. `run_0156_*` | sealed (state-only plans DIAG, S3a, S3b, S3c, S4a; `config/sealed_runs.json`) |
| 2026-10-22 | `results/runs/run_0097_*` .. `run_0101_*` | restricted (Dmesh and FNORD runs; reading limited by the register, A45 / A47) |
| 2026-10-22 | `results/runs/run_0164_*` .. `run_0181_*` | restricted (S5 leave-one-film-out folds; A53 (g)) |
| 2026-10-22 | `results/runs/run_0182_*` .. `run_0200_*`, `run_0202_*` .. `run_0204_*`, `run_0206_*` .. `run_0210_*` | unread (S6, S7 and F13-F15 outputs before their registered read-out; A59 (d), A62 (d)) |
| 2026-10-22 | `results/runs/run_0160_*`, `run_0201_*`, `run_0205_*` | unread (interrupted launches, kept and never opened) |
| 2026-10-22 | `results/runs/run_0211_*` .. `run_0213_*` | REG-001: P1 runs; the registered predicted values are public as a hash only (D-102) |
| 2026-10-22 | `results/campaigns/campaign_C10_DIAG.json`, `campaign_C10_DIAG.gates.jsonl`, `campaign_C10_{S3a_act,S3b_igzo,S3c_tails,S4a_b1,S4a_b2,S4a_b3}.json` | sealed (state-only campaign records) |
| 2026-10-22 | `results/campaigns/campaign_C10_{Dmesh,Dmesh_T2b,Efnord,S4d,S5_*}.json` | restricted (they carry metrics of restricted runs; S4d holds the unread run_0160) |
| 2026-10-22 | `results/campaigns/campaign_C10_{S6_b1..b8,S6_b7r,S7__S7-01,S7__S7-02,F13_F15__S3-24,F13_F15__S3-25,F13_F15__S3-26}.json` | unread |
| 2026-10-22 | `results/campaigns/campaign_C10_P1_{2p0,6p3,13p2}.json` | REG-001 (hash-only, D-102) |
| 2026-10-22 | `analysis_2026-10-10_campaign/profile/p1_floor_record_REG-001.json`, `p1_a55_manifest_REG-001.json` | REG-001 (hash-only, D-102). These two files were also removed from the unpushed local commits before the 2026-10-22 push, so they never reached the public history. The commit that added them stays in the history as an empty commit with a neutral message (no seal hash, no outcome) |
| 2026-10-22 | `analysis_2026-10-10_campaign/profile/s5_A53/**` (21 files), `config/campaign_C10_S5_{h6p3_t1,h6p3_t2,h6p3_t3,h6p3_t4,h6p3_pred,h2p0_t1,h2p0_t2,h13p2_t1,h13p2_t2}.json`, `analysis_2026-10-10_campaign/branch_d/branch_d_T*.json` (4), `analysis_2026-10-10_campaign/fp_plans.py`, `analysis_2026-10-10_campaign/profile/fp_record_A60.json` | pending user confirmation: S5 LOO and branch-D records (the S5 leave-one-film-out records and the route plans resolved from them; the branch-D read-outs of run_0097..run_0099; the A60 generator and record, which state an S5 fold status). They were removed from the unpushed local commits before the push, and the S5 / branch-D result values in those commit messages are replaced by "[withheld pending user OK]". Section "pending user OK 2026-10-22" of `.gitignore` |
| 2026-10-22 | `results/RUN_INDEX.csv`: the rows of every run listed above | as the run (sealed, restricted, unread or REG-001) |

### Published by user decision 2026-10-22 ("Publish"; recorded 2026-10-23)

The frozen-code fit / score records of the sealed S3 and S4a runs are published. They are registered read-outs made by
frozen code under the logged frozen-code routes A49 (d), A50, A51 (d) and A52 (sealed curves are read only through
`profile_s4s5.py`, `config/sealed_runs.json`). The rule "no output content of runs 0079-0156" is amended for these
records only. The sealed raw run directories `results/runs/run_0102_*` .. `run_0156_*` stay excluded (row above).

| Date | Path or pattern | Status |
|---|---|---|
| 2026-10-22 | `analysis_2026-10-10_campaign/register_scores/hf_v4_A49.json` | published (A49 (d), A50: H-F v4 score, S3-10 shape fit, IGZO triple profile, S3-27 check) |
| 2026-10-22 | `analysis_2026-10-10_campaign/profile/s3_adoption_A49.json` | published (A49 (d), A50: S3 adoption record) |
| 2026-10-22 | `analysis_2026-10-10_campaign/profile/s4s5_confirm_S3-27_run_0103_vs_run_0102.json` | published (A49 (d): S3-27 confirmation record; the file name carries sealed run ids) |
| 2026-10-22 | `analysis_2026-10-10_campaign/profile/s4s5_profile_n_S4A-01.json` .. `s4s5_profile_n_S4A-15.json` (15) | published (A49 (d): S4a profiles; S4A-01 reuses public runs, S4A-02..15 read runs 0114-0156) |
| 2026-10-22 | `analysis_2026-10-10_campaign/profile/s4a_archive_A51.json`, `s4s5_surrogate_s4a_archive_A51.json` | published (A51 (d): S4a archive, surrogate and abort verdict) |
| 2026-10-22 | `analysis_2026-10-10_campaign/profile/s4c_record_A52.json`, `s4c_confirm_A52.json` | published (A52: S4c record from the S4A-04 profile of runs 0120-0122, and its confirmation) |
| 2026-10-22 | Messages of commits 9b43d30, 275e3ee, 338f812, a6ff6cb, a8dca98, 5af9019 (metrics of these records) | published |

How `results/RUN_INDEX.csv` is handled (2026-10-22): the committed version is a filtered copy. It holds the rows that
were already public, unchanged, plus the rows of run_0078, run_0157..0159 and run_0161..0163, in the original order.
The local working copy keeps the full index. It is marked with `git update-index --skip-worktree results/RUN_INDEX.csv`,
so git does not see the local rows and `git add -A` does not stage them. To commit a later public change to this file,
run `git update-index --no-skip-worktree results/RUN_INDEX.csv`, stage a filtered copy built by the same rule, and then
set the flag again. Never stage the full local file.

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
