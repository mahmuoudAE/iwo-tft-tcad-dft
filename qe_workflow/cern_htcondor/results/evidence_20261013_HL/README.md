# H-L evidence (2026-10-13)

Analysis files behind the RESULTS_LOG entry "2026-10-13 03:40Z: H-L crystalline oxygen-vacancy test scored" and claims-ledger entry C038 (private repo). Copied unchanged from the analysis session scratchpad on 2026-10-13 ~03:38Z. Crystalline cells only; no amorphous quantity is contained.

| File | What it is |
|---|---|
| `r23.sh` | Read-only grep of `~/iwo_amorph/vac/<cell>/` and `checks/gpumax_work/a20_g002/<cell>/` on lxplus (energies, -TS, convergence lines, input diffs) |
| `r23.out` | Raw output of `r23.sh` (2026-10-13 ~00:29Z) |
| `hl_a20ii.py` | Parser of `r23.out` into the differences (1 Ry = 13.605693122994 eV); field `minus_TS_Ry` (renamed from `minus_TS_mRy`, values in Ry, unchanged) |
| `hl_a20ii.json` | Output of `hl_a20ii.py` |
| `digest_hl_a20ii.md` | First scoring digest sent to Codex (00:31Z). Its BFGS counts 12/15/17/28 are the last 'number of bfgs steps' counter; QE's own 'bfgs converged' counts are 13/16/18/29 (In32O47, far, near, near72), as logged |
| `q1_prov.sh`, `q1_prov.out` | Read-only job, cell and file-hash map (HTCondor user-log times are CEST = UTC+2) |
| `g5_bind.sh`, `g5_bind.out`, `g5_bind.json` | Read-only geometry binding (canonical geometry sha256; prints no energies) |
| `geometry_binding.md` | Geometry-binding report: all six cells BOUND |

All files are byte-identical to the analysis copies (`.gitattributes` disables line-ending conversion here; `hl_a20ii.json` and `geometry_binding.md` have CRLF line endings). Checksums: `SHA256SUMS`.
