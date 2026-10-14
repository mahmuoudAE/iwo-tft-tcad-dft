# Z3 duplicate proof: S3-04 and S3-07 vs S0-01 (2026-10-15, dry build, no launch)

Builder: scripts/run_campaign.current_deck_text / current_material_text (the runner's own code, as used by regress_sealed_aware.py l.104),
matrix analysis_2026-10-10_campaign/campaign_matrix.json, model file config/iwo_material_model_v3.yaml (run_0061 RUN_INDEX notes `model=...v3.yaml`).
Script: dry_builds/z3_dry.py; decks written to dry_builds/{S0-01,S3-04,S3-07}_device.in. Hash = sha256 of the deck text (RUN_INDEX convention).

| Entry | label | deck_sha256 (COMPUTED) | material sha256 (COMPUTED) | non-comment-lines sha256 (COMPUTED) |
|---|---|---|---|---|
| run_0061 (RUN_INDEX deck_sha256, MEASURED record) | c10_s0_01_2p0 | d2fd986f9f68b1758013e66b3c04804c6d13ca741a0f79defbfeba9360b20f7a | 974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204 | - |
| S0-01 rebuild | c10_s0_01_2p0 | d2fd986f9f68b1758013e66b3c04804c6d13ca741a0f79defbfeba9360b20f7a (= run_0061) | 974b23ea... (= run_0061) | 352f48b0773029dd4a70a01eaf9663d2bb1c60b5227c0f920ce002011f7b8f62 |
| S3-04 | c10_s3_04_2p0 | 7721525ff32600e5e8bf7db17e8e09e936aa622284c86544e3d1caa6ab2ca006 | 71463208640439495a93ff0d9bb8be71dede890cee22288905992f9ca0310942 | 352f48b0...7b8f62 (equal) |
| S3-07 | c10_s3_07_2p0 | 26135c1f1afea9157109dcaf0988a82dd44f17db39bef923b7f9c38aaa310fdc | 81a8887f09b9055d755bb6bb3d984888be81a298f1e71ad6bc3fb181defc0472 | 352f48b0...7b8f62 (equal) |

Result: full deck_sha256 NOT equal. The only differences are `#` comment lines (provenance text); every ATLAS statement is identical
(non-comment sha256 equal for all three). Reason: S3-04 sets Nt alpha=0 (Nt2*(2/t)^0 = Nt2 at t=2 nm); S3-07 splits Nt2 1e19 + bulk 1e19 = 2e19 cm^-3,
equal to S0-01 Nt2 2e19 with (2/2)^1 = 1 (CALCULATED). Matrix `duplicate_of` is None for both (PA-0 adds it later). Register l.2164 lists them as duplicates.

Diff vs S0-01 (unified, n=0):
```
S3-04: @@ -19 +19 @@
- # [D] Nt(t) = 2.0000e+19 cm^-3 | ... | Nt2*(2/t)^alpha, Nt2=2e+19, alpha=1.0
+ # [D] Nt(t) = 2.0000e+19 cm^-3 | ... | Nt2*(2/t)^alpha, Nt2=2e+19, alpha=0.0
S3-07: @@ -19 +19 @@
- # [D] Nt(t) = 2.0000e+19 cm^-3 | ... | Nt2*(2/t)^alpha, Nt2=2e+19, alpha=1.0
+ # [D] Nt(t) = 2.0000e+19 cm^-3 | ... | Nt2*(2/t)^alpha, Nt2=1e+19, alpha=1.0 + Nt_bulk 1e+19 (OPTION)
S3-07: @@ -32,0 +33 @@
+ # [D] OPTION Nt bulk term = 1.0000e+19 (Nt = 1.0000e+19 + 1.0000e+19) cm^-3 | FITTED branch (...) | physics_options.nt_bulk_cm3
```
Verdict: simulation-equivalent duplicates (statement content identical), not byte-identical decks; not launched.
The plan's Z3 criterion "deck_sha256 equal" is not met literally; the plan text (l.183, l.659) should say "non-comment deck content equal".
